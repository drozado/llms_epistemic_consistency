import pandas as pd
import os
import re
import asyncio
from typing import List, Dict, Any, Optional, Union
from any_llm import AnyLLM
from requests.exceptions import HTTPError
from vpei.models import MODELS, PROVIDER_CONCURRENCY_LIMITS, common_client_parameters
from tenacity import (
    retry,
    AsyncRetrying, 
    RetryError,
    retry_if_exception,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff
from vpei.utils.llm_utils import *

suppress_pydantic_serialization_warnings()



# Global semaphore for controlling concurrent LLM requests
_llm_semaphore = None
_default_max_concurrent_requests = 20
_provider_semaphores = {}
_provider_limits = dict(PROVIDER_CONCURRENCY_LIMITS)
_any_llm_instances: dict[tuple, AnyLLM] = {}


def _get_any_llm_instance(provider: str, api_key, api_base) -> AnyLLM:
    key = (provider, api_base, api_key)
    if key not in _any_llm_instances:
        _any_llm_instances[key] = AnyLLM.create(provider, api_key=api_key, api_base=api_base)
    return _any_llm_instances[key]


def _split_provider_model(model_str: str) -> tuple:
    if ':' in model_str:
        provider, model_name = model_str.split(':', 1)
        return provider, model_name
    return None, model_str


def _call_with_instance(request_params: dict):
    params = dict(request_params)
    model_str = params.pop('model')
    api_key = params.pop('api_key', None)
    api_base = params.pop('api_base', None)
    provider, model_name = _split_provider_model(model_str)
    instance = _get_any_llm_instance(provider, api_key, api_base)
    return instance.completion(model=model_name, **params)


async def _acall_with_instance(request_params: dict):
    params = dict(request_params)
    model_str = params.pop('model')
    api_key = params.pop('api_key', None)
    api_base = params.pop('api_base', None)
    provider, model_name = _split_provider_model(model_str)
    instance = _get_any_llm_instance(provider, api_key, api_base)
    return await instance.acompletion(model=model_name, **params)


def set_max_concurrent_llm_requests(limits: Union[int, Dict[str, int]]):
    """
    Set concurrency limits.

    Args:
        limits (int | dict): If int, apply to all providers; if dict, use per-provider limits.
    """
    global _llm_semaphore, _provider_semaphores, _provider_limits
    _provider_semaphores = {}

    if isinstance(limits, int):
        _provider_limits = {provider: limits for provider in PROVIDER_CONCURRENCY_LIMITS.keys()}
        _llm_semaphore = asyncio.Semaphore(limits)
        print(f"Setting max concurrent LLM requests to {limits} for all providers")
        return

    if isinstance(limits, dict):
        _provider_limits = dict(limits)
        fallback = max(_provider_limits.values()) if _provider_limits else _default_max_concurrent_requests
        _llm_semaphore = asyncio.Semaphore(fallback)
        print(f"Setting per-provider concurrency limits: {_provider_limits}")
        print(f"Setting global fallback concurrency limit to {fallback}")
        return

    raise ValueError("limits must be an int or a dict of provider limits")


def get_llm_semaphore():
    """
    Get the global LLM semaphore, creating it with default value if it doesn't exist.
    
    Returns:
        asyncio.Semaphore: The semaphore for controlling concurrent requests
    """
    global _llm_semaphore
    if _llm_semaphore is None:
        _llm_semaphore = asyncio.Semaphore(_default_max_concurrent_requests)
    return _llm_semaphore





def get_llm_semaphore_for_model(model_name: str) -> asyncio.Semaphore:
    provider = get_provider_for_model_name(model_name)
    if provider and provider in _provider_limits:
        if provider not in _provider_semaphores:
            _provider_semaphores[provider] = asyncio.Semaphore(_provider_limits[provider])
        return _provider_semaphores[provider]
    return get_llm_semaphore()



def get_model_name(model_name: str) -> str:
    """Convert internal model name to any-llm format (provider:model)."""
    # Try to determine provider from MODELS config
    if model_name in MODELS:
        client = MODELS[model_name]['client']
        client_type = type(client).__name__

        # Determine provider by client type
        if client_type in ['Anthropic', 'AsyncAnthropic']:
            return f"anthropic:{model_name}"

        # For OpenAI-like clients, check base_url if available
        if hasattr(client, 'base_url'):
            base_url = str(client.base_url).lower()

            if 'openai.com' in base_url:
                return f"openai:{model_name}"
            elif 'together.xyz' in base_url:
                return f"openai:{model_name}"
            elif 'googleapis.com' in base_url:
                # Use openai: prefix to route through the OpenAI-compatible endpoint
                return f"openai:{model_name}"
            elif 'x.ai' in base_url:
                # xAI exposes an OpenAI-compatible REST API; use openai: provider
                # with api_base override rather than any-llm's native xai: provider,
                # which uses the xai_sdk (Protocol Buffers) and is incompatible.
                return f"openai:{model_name}"

    # Default: return as is and let any-llm handle it
    return model_name


def _adapt_model_kwargs_for_model_legacy(model_name: str, custom_model_kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Adapt model_kwargs to match the expected parameters for specific models.
    """

    if model_name in MODELS:
        default_params = MODELS[model_name].get("model_parameters", {})
        custom_model_kwargs = custom_model_kwargs or {}
        model_kwargs = {**default_params, **custom_model_kwargs}
    else:
        raise ValueError(f"Model {model_name} not found in MODELS configuration.")

    if not model_kwargs:
        model_kwargs = {}

    provider = get_provider_for_model_name(model_name)

    # flex mode by default on for gpt-5 models to reduce costs unless user explicitly overrides it.
    if 'gpt-5' in model_name and 'service_tier' not in model_kwargs:
        model_kwargs["service_tier"] = "flex"

    # GPT-5 series: temperature is only supported when reasoning is fully off.
    # Older non-dot gpt-5 models (gpt-5, gpt-5-mini, gpt-5-nano) don't support
    # reasoning_effort='none' — 'none' maps to 'minimal' below, so always drop temperature.
    # Newer dot-release models (gpt-5.4+) support 'none', so only drop when reasoning is active.
    _older_gpt5 = model_name == 'gpt-5' or model_name.startswith('gpt-5-')
    if _older_gpt5 or (model_name.startswith('gpt-5') and model_kwargs.get('reasoning_effort', 'none').lower() != 'none'):
        model_kwargs.pop('temperature', None)

    # Anthropic: when extended thinking is enabled (reasoning_effort != 'none'), temperature
    # must be exactly 1 — remove it so the API uses its default rather than rejecting 0.0.
    if provider == 'anthropic' and model_kwargs.get('reasoning_effort', 'none').lower() != 'none':
        model_kwargs.pop('temperature', None)

    if not MODELS[model_name].get('supports_reasoning_effort', False):
        # Model doesn't support reasoning_effort at all — drop it to avoid API errors.
        model_kwargs.pop('reasoning_effort', None)
    else:
        if provider in ('anthropic', 'xai'):
            # For Anthropic: any-llm translates reasoning_effort to provider-specific
            # thinking parameters; omit 'none' so the model runs without extended thinking.
            # For xAI: routed via openai: provider with api_base; pass reasoning_effort
            # through directly to xAI's OpenAI-compatible API, but drop 'none'.
            if model_kwargs.get('reasoning_effort', '').lower() == 'none':
                model_kwargs.pop('reasoning_effort', None)
        elif provider == 'gemini':
            pass  # Pass 'none' through to the OpenAI-compatible endpoint; see adapt_model_kwargs_for_model.
        elif model_name == 'gpt-5' or model_name.startswith(('gpt-5-', 'gpt-5-mini', 'gpt-5-nano')):
            # Older GPT-5 models don't accept 'none' — use 'minimal' instead.
            if model_kwargs.get('reasoning_effort', '').lower() == 'none':
                model_kwargs['reasoning_effort'] = "minimal"

    return model_kwargs


def adapt_model_kwargs_for_model(model_name: str, custom_model_kwargs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Adapt model_kwargs to match the expected parameters for specific models.
    """

    if model_name in MODELS:
        default_params = MODELS[model_name].get("model_parameters", {})
        custom_model_kwargs = custom_model_kwargs or {}
        model_kwargs = {**default_params, **custom_model_kwargs}
    else:
        raise ValueError(f"Model {model_name} not found in MODELS configuration.")

    if not model_kwargs:
        model_kwargs = {}

    provider = get_provider_for_model_name(model_name)
    _effective_name = MODELS[model_name].get('api_model_name', model_name)

    # Translate max_tokens to the provider-specific parameter name.
    # OpenAI reasoning models (gpt-5+) require max_completion_tokens; Anthropic uses max_tokens.
    if 'max_tokens' in model_kwargs and provider == 'openai' and MODELS[model_name].get('supports_reasoning_effort', False):
        model_kwargs['max_completion_tokens'] = model_kwargs.pop('max_tokens')

    # flex mode by default on for gpt-5 models to reduce costs unless user explicitly overrides it.
    if 'gpt-5' in model_name and 'service_tier' not in model_kwargs:
        model_kwargs["service_tier"] = "flex"

    # GPT-5 series: temperature is only supported when reasoning is fully off.
    # Older non-dot gpt-5 models (gpt-5, gpt-5-mini, gpt-5-nano) don't support
    # reasoning_effort='none' — 'none' maps to 'minimal' below, so always drop temperature.
    # Newer dot-release models (gpt-5.4+) support 'none', so only drop when reasoning is active.
    _older_gpt5 = _effective_name == 'gpt-5' or _effective_name.startswith('gpt-5-')
    if _older_gpt5 or (model_name.startswith('gpt-5') and model_kwargs.get('reasoning_effort', 'none').lower() != 'none'):
        model_kwargs.pop('temperature', None)

    # Anthropic: when extended thinking is enabled (reasoning_effort != 'none'), temperature
    # must be exactly 1 — remove it so the API uses its default rather than rejecting 0.0.
    if provider == 'anthropic' and model_kwargs.get('reasoning_effort', 'none').lower() != 'none':
        model_kwargs.pop('temperature', None)

    if MODELS[model_name].get('supports_reasoning_toggle', False):
        explicit_reasoning = custom_model_kwargs.get('reasoning')
        explicit_reasoning_effort = custom_model_kwargs.get('reasoning_effort')

        if explicit_reasoning is not None:
            if isinstance(explicit_reasoning, bool):
                model_kwargs['reasoning'] = {"enabled": explicit_reasoning}
        elif explicit_reasoning_effort is not None:
            model_kwargs['reasoning'] = {"enabled": str(explicit_reasoning_effort).lower() != 'none'}
        elif 'reasoning' not in model_kwargs and model_kwargs.get('reasoning_effort') is not None:
            model_kwargs['reasoning'] = {"enabled": str(model_kwargs['reasoning_effort']).lower() != 'none'}

        # Together toggle models accept `reasoning`, not `reasoning_effort`.
        model_kwargs.pop('reasoning_effort', None)
    else:
        model_kwargs.pop('reasoning', None)

    if not MODELS[model_name].get('supports_reasoning_effort', False):
        # If the caller explicitly requested a non-'none' reasoning_effort, fail loudly.
        explicit_effort = (custom_model_kwargs or {}).get('reasoning_effort')
        if explicit_effort is not None and str(explicit_effort).lower() != 'none':
            raise ValueError(
                f"Model '{model_name}' does not support reasoning_effort, "
                f"but reasoning_effort='{explicit_effort}' was requested."
            )
        model_kwargs.pop('reasoning_effort', None)
    else:
        if provider in ('anthropic', 'xai', 'together_ai'):
            # For Anthropic: any-llm translates reasoning_effort to provider-specific
            # thinking parameters; omit 'none' so the model runs without extended thinking.
            # For xAI/TogetherAI OpenAI-compatible endpoints, pass reasoning_effort
            # through directly when present, but drop 'none'.
            if model_kwargs.get('reasoning_effort', '').lower() == 'none':
                model_kwargs.pop('reasoning_effort', None)
        elif provider == 'gemini':
            # Gemini is routed via the OpenAI-compatible endpoint (openai:model with custom
            # api_base), so any-llm does NOT translate reasoning_effort to Gemini thinking
            # parameters — pass it through as-is.
            # The OAI-compatible endpoint accepts "none" and minimises thinking:
            #   - Gemini 2.5 Flash/Flash-Lite: "none" → thinking_budget=0 (fully disabled)
            #   - Gemini 3 Flash/Flash-Lite:   "none" → thinking_level=minimal (cannot fully disable)
            #   - Gemini 3.1 Pro:              "none" → thinking_level=low  (minimal not supported on Pro)
            # Omitting reasoning_effort entirely causes the API to default to dynamic/high
            # thinking, which is extremely slow on long-context tasks (e.g. math proofs).
            pass
        elif _effective_name == 'gpt-5' or _effective_name.startswith(('gpt-5-', 'gpt-5-mini', 'gpt-5-nano')):
            # Older GPT-5 models don't accept 'none' - use 'minimal' instead.
            if model_kwargs.get('reasoning_effort', '').lower() == 'none':
                model_kwargs['reasoning_effort'] = "minimal"

    return model_kwargs


def prepare_request_params(model_name: str, messages: List[Dict], structured_output_schema=None, **model_kwargs) -> Dict[str, Any]:
    """
    Prepare request parameters for any-llm completion.
    any-llm handles provider-specific adjustments automatically.
    """
   
    # For suffixed model variants, use the base model name for the API call
    api_model_name = MODELS.get(model_name, {}).get('api_model_name', model_name)
    provider_model = get_model_name(api_model_name)
    
    # Prepend system_prompt_prefix for suffixed model variants
    system_prompt_prefix = MODELS.get(model_name, {}).get('system_prompt_prefix')
    if system_prompt_prefix:
        messages = [
            {**msg, 'content': system_prompt_prefix + '\n' + msg['content']} if msg.get('role') == 'system' else msg
            for msg in messages
        ]

    # Filter out empty system messages (some providers like Anthropic reject them)
    filtered_messages = [
        msg for msg in messages
        if not (msg.get('role') == 'system' and not msg.get('content', '').strip())
    ]
    
    # Build the request parameters
    # Ensure a timeout is always set so requests don't hang indefinitely.
    # any-llm creates its own HTTP client, so client-level timeouts from
    # models.py (common_client_parameters) do NOT apply here — we read the
    # value from common_client_parameters to keep a single source of truth.
    if 'timeout' not in model_kwargs and 'timeout' in common_client_parameters:
        model_kwargs['timeout'] = common_client_parameters['timeout']

    provider = get_provider_for_model_name(api_model_name)

    # Together's reasoning toggle is not part of the typed OpenAI Chat Completions
    # method signature in the installed SDK, so pass it via extra_body.
    if provider == 'together_ai' and 'reasoning' in model_kwargs:
        extra_body = dict(model_kwargs.get('extra_body') or {})
        extra_body['reasoning'] = model_kwargs.pop('reasoning')
        model_kwargs['extra_body'] = extra_body

    # For OpenAI-compatible third-party endpoints (Google, xAI, TogetherAI),
    # pass api_base and api_key so any-llm routes to the correct endpoint.
    if api_model_name in MODELS:
        client = MODELS[api_model_name]['client']
        if hasattr(client, 'base_url') and hasattr(client, 'api_key'):
            base_url = str(client.base_url).lower()
            if 'openai.com' not in base_url:
                model_kwargs.setdefault('api_base', str(client.base_url))
                if client.api_key is not None:
                    model_kwargs.setdefault('api_key', client.api_key)

    params = {
        'model': provider_model,
        'messages': filtered_messages,
        **model_kwargs
    }
    
    # Pass per-model API key if configured (e.g. fine-tuned models on different accounts)
    if model_name in MODELS and 'api_key' in MODELS[model_name]:
        params['api_key'] = MODELS[model_name]['api_key']

    # Handle structured output if provided
    if structured_output_schema:
        print(f"Adding structured output schema for model {model_name}.")
        params['response_format'] = structured_output_schema

    return params

def extract_content_from_model_response(response, structured_output_schema=None):
    """
    Extract content from any-llm response (OpenAI-compatible format).
    """
    # Handle structured output
    if structured_output_schema:
        message = response.choices[0].message
        # Parsed content is in choices[0].message.parsed
        if hasattr(message, 'parsed') and message.parsed is not None:
            return message.parsed
        # Fallback: parse JSON string content into the schema
        content = message.content
        if isinstance(content, str):
            return structured_output_schema.model_validate_json(content)
        return content
    
    # Regular text responses
    return response.choices[0].message.content




@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(3), retry=retry_if_exception(is_retryable_exception), reraise=True)    
def make_http_request_to_llm_provider(**request_params):
    """
    Make a request to the LLM provider using any-llm completion.
    This function is used to handle retries for HTTP requests.
    """
    try:
        response = _call_with_instance(request_params)
        return response
    except Exception as e:
        print(f"LLM API error occurred: {e}")
        raise e

async def _make_http_request_async(**request_params):
    """
    Async version of make_http_request_to_llm_provider using any-llm's acompletion.
    Avoids creating a nested event loop (which causes httpx cleanup errors in Jupyter).
    """
    async for attempt in AsyncRetrying(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(3),
        retry=retry_if_exception(is_retryable_exception),
        reraise=True
    ):
        with attempt:
            try:
                response = await _acall_with_instance(request_params)
                return response
            except Exception as e:
                print(f"LLM API error occurred: {e}")
                raise e


async def make_llm_request_async(model_name, input, structured_output_schema=None, **kwargs):
    """
    Make an async request to the specified LLM model with the given messages.
    Uses a global semaphore to limit concurrent requests.
    """
    semaphore = get_llm_semaphore_for_model(model_name)

    async with semaphore:
        required_text_response_regex = kwargs.pop('required_text_response_regex', None)
        structured_output_field_for_required_text = kwargs.pop('structured_output_field_for_required_text', None)

        model_kwargs = adapt_model_kwargs_for_model(model_name, custom_model_kwargs=kwargs)

        try:
            request_params = prepare_request_params(model_name, input, structured_output_schema, **model_kwargs)
            response = await _make_http_request_async(**request_params)
            response_content = extract_content_from_model_response(response, structured_output_schema)
            if response_content is None or (isinstance(response_content, str) and not response_content.strip()):
                finish_reason = response.choices[0].finish_reason if hasattr(response, 'choices') and response.choices else 'unknown'
                return f"ERROR: Model returned empty/None content (finish_reason={finish_reason}, model={model_name})"

            if required_text_response_regex:
                verify_response_content(
                    response_content,
                    required_text_response_regex=required_text_response_regex,
                    structured_output_schema=structured_output_schema,
                    structured_output_field_for_required_text=structured_output_field_for_required_text
                )
            return response_content
        except Exception as e:
            if is_retryable_exception(e):
                error_msg = f"ERROR: {type(e).__name__}: {e}"
                print(f"WARNING: Transient server error for model {model_name} after all retries exhausted: {e}. Returning error string.")
                return error_msg
            print(f"Error making async LLM request for model {model_name}: {e}")
            raise e
    

def verify_response_content(response_content, required_text_response_regex, structured_output_schema=None, structured_output_field_for_required_text=None):
    if not structured_output_schema:
        if not re.search(required_text_response_regex, response_content):
            print(f"Response does not match the required pattern: {required_text_response_regex}. Retrying...")
            raise RegexNotInTextResponseError(required_text_response_regex, response_content) 
    else: #structured output
        # Assuming response_content is a dict when structured_output_schema is provided
        attribute_text = getattr(response_content, structured_output_field_for_required_text)
        if not re.search(required_text_response_regex, attribute_text):
            print(f"Structured response attribute {attribute_text} does not match the required pattern: {required_text_response_regex}. Retrying...")
            raise RegexNotInTextResponseError(required_text_response_regex, attribute_text)  
    return True


@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(2), retry=retry_if_exception(is_retryable_exception), reraise=True)    
def make_llm_request(model_name: str, messages: List, structured_output_schema=None, required_text_response_regex=None, structured_output_field_for_required_text=None, **model_kwargs):
    """
    Make a request to the specified LLM model using any-llm's unified interface.
    """
    # Apply model defaults and model-specific adaptations. Custom kwargs override defaults.
    model_kwargs = adapt_model_kwargs_for_model(model_name, custom_model_kwargs=model_kwargs)

    try:
        request_params = prepare_request_params(model_name, messages, structured_output_schema, **model_kwargs)
        response = make_http_request_to_llm_provider(**request_params)

        # Extract content from the response
        response_content = extract_content_from_model_response(response, structured_output_schema)
        
        # Verify response content if regex pattern is provided
        if required_text_response_regex:
            verify_response_content(
                response_content, 
                required_text_response_regex=required_text_response_regex,
                structured_output_schema=structured_output_schema,  
                structured_output_field_for_required_text=structured_output_field_for_required_text
            )

        return response_content

    except Exception as e:
        if is_retryable_exception(e):
            print(f"WARNING: Transient server error for model {model_name} after all retries exhausted: {e}. Returning None.")
            return None
        print(f"Error making LLM request for model {model_name}: {e}")
        raise e

