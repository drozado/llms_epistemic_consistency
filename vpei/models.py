import os
from openai import OpenAI
from anthropic import Anthropic, AsyncAnthropic
from together import Together
from dotenv import load_dotenv
from vpei.epistemic_consistency.prompts import CENTRIST_LLM_SYSTEM_PROMPT, EPISTEMICALLY_RIGOROUS_LLM_SYSTEM_PROMPT
load_dotenv()

PROVIDER_CONCURRENCY_LIMITS = {
    "openai": 35,
    "anthropic": 15,
    # "together_ai": 20,
    "together_ai": 10, #for endpoint models
    "gemini": 15,
    "xai": 7,
}

common_client_parameters = {'timeout': 600} # 600-second timeout; also used by llm_requests_v3.py as the default timeout for any-llm requests.
common_model_parameters = {
    "temperature": 0.0,
    "reasoning_effort": "none",
    }

MODELS = {
    #OpenAI models
    "gpt-5.4": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-5.4", "snapshot_date": "2026-03-05", "model_size": "large", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": True,},
    "gpt-5.4-mini": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-5.4-mini", "snapshot_date": "2026-03-17", "model_size": "mini", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": True,},
    "gpt-5.4-nano": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-5.4-nano", "snapshot_date": "2026-03-17", "model_size": "nano", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": True,},
    "gpt-5": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-5", "snapshot_date": "2025-08-07", "model_size": "large", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": True,},
    "gpt-5-mini": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-5-mini", "snapshot_date": "2025-08-07", "model_size": "mini", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": True,},
    "gpt-5-nano": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-5-nano", "snapshot_date": "2025-08-07", "model_size": "nano", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": True,},
    "gpt-4.1": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-4.1", "snapshot_date": "2025-04-14", "model_size": "large", "model_parameters": common_model_parameters, "supports_image_input": True,},
    "gpt-4.1-mini": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-4.1-mini", "snapshot_date": "2025-04-14", "model_size": "mini", "model_parameters": common_model_parameters, "supports_image_input": True,},
    "gpt-4.1-nano": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-4o-nano", "snapshot_date": "2025-04-14", "model_size": "nano", "model_parameters": common_model_parameters, "supports_image_input": True,},
    "gpt-4o": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-4o", "snapshot_date": "2024-08-06", "model_size": "large", "model_parameters": common_model_parameters, "supports_image_input": True,},
    "gpt-4o-mini": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-4o-mini", "snapshot_date": "2024-07-18", "model_size": "mini", "model_parameters": common_model_parameters, "supports_image_input": True,},
    "gpt-3.5-turbo": {"client": OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.openai.com/v1",**common_client_parameters),"long_name": "OpenAI GPT-3.5", "snapshot_date": "2024-01-25", "model_size": "large", "model_parameters": common_model_parameters, "supports_image_input": False,},

    #xAI models
    "grok-4.20-non-reasoning": {"client": OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1"),"long_name": "xAI grok-4.20-non-reasoning", "snapshot_date": "2026-03-09", "model_parameters": common_model_parameters, "supports_image_input": True,}, #snapshot date estimated from google search
    "grok-4.20-reasoning": {"client": OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1"),"long_name": "xAI grok-4.20-reasoning", "snapshot_date": "2026-03-09", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": True,}, #snapshot date estimated from google search
    "grok-4-1-fast-non-reasoning": {"client": OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1"),"long_name": "xAI grok-4-1-fast-non-reasoning", "snapshot_date": "2025-11-19", "model_parameters": common_model_parameters, "supports_image_input": True,}, #snapshot date estimated from google search
    "grok-4-1-fast-reasoning": {"client": OpenAI(api_key=os.getenv("XAI_API_KEY"), base_url="https://api.x.ai/v1"),"long_name": "xAI grok-4-1-fast-reasoning", "snapshot_date": "2025-11-19", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": True,}, #snapshot date estimated from google search

    #Anthropic models
    "claude-sonnet-4-6": {"client": Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")), "long_name": "Anthropic claude-sonnet-4-6", "snapshot_date": "2026-02-17", "model_size": "large", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": True,},
    "claude-haiku-4-5-20251001": {"client": Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")), "long_name": "Anthropic claude-haiku-4-5", "snapshot_date": "2025-10-01", "model_size": "mini", "model_parameters": common_model_parameters, "supports_image_input": True,},  # does not support extended thinking

    #Google models
    "gemini-3-flash-preview": {"client": OpenAI(api_key=os.getenv("GOOGLE_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"),"long_name": "Google gemini-3.1-flash", "snapshot_date": "2026-02-19", "model_size": "large", "model_parameters": {**common_model_parameters, "reasoning_effort": "minimal"}, "supports_reasoning_effort": True, "supports_image_input": True,},
    "gemini-3.1-flash-lite-preview": {"client": OpenAI(api_key=os.getenv("GOOGLE_API_KEY"), base_url="https://generativelanguage.googleapis.com/v1beta/openai/"),"long_name": "Google gemini-3.1-flash-lite", "snapshot_date": "2026-03-03", "model_size": "mini", "model_parameters": {**common_model_parameters, "reasoning_effort": "minimal"}, "supports_reasoning_effort": True, "supports_image_input": True,},

    # TogetherAI open-source models
    "Qwen/Qwen3.5-397B-A17B": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Alibaba Qwen3.5-397B-A17B", "snapshot_date": "2026-02-16", "model_parameters": {**common_model_parameters, "reasoning": {"enabled": False}}, "supports_reasoning_toggle": True, "supports_image_input": True,},  # Together exposes reasoning for this Qwen model as a boolean on/off toggle, not adjustable low/medium/high levels.
    "moonshotai/Kimi-K2.5": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Moonshotai Kimi-K2.5", "snapshot_date": "2026-01-26", "model_parameters": {**common_model_parameters, "reasoning": {"enabled": False}}, "supports_reasoning_toggle": True, "supports_image_input": True,},  # Together exposes Kimi reasoning as a boolean on/off toggle, not adjustable low/medium/high levels. max_tokens needed: model burns default token budget on internal reasoning, leaving no room for visible output.
    "deepseek-ai/DeepSeek-V3.1": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "DeepSeek DeepSeek V3.1", "snapshot_date": "2025-09-5", "model_parameters": {**common_model_parameters, "reasoning": {"enabled": False}}, "supports_reasoning_toggle": True, "supports_image_input": False,},  # Together exposes reasoning for DeepSeek-V3.1 as a boolean on/off toggle, not adjustable low/medium/high levels.
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Meta Llama-3.3-70B", "snapshot_date": "2024-12-06", "model_parameters": common_model_parameters, "supports_image_input": False,},
    "openai/gpt-oss-120b": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "OpenAI gpt-oss-120b", "snapshot_date": "2025-08-05", "model_parameters": common_model_parameters, "supports_reasoning_effort": True, "supports_image_input": False,},
    "zai-org/GLM-5.1": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Zai-org GLM-5.1", "snapshot_date": "2026-04-07", "model_parameters": {**common_model_parameters, "reasoning": {"enabled": False}}, "supports_reasoning_toggle": True, "supports_image_input": False,},  # Together exposes GLM-5 reasoning as a boolean on/off toggle, not adjustable low/medium/high levels.

    # Private Together AI deployment endpoints (prefixed with the account name used to deploy them)
    "drozado/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8-4e57e3dc": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Meta Llama-4-Maverick-17B-128E", "snapshot_date": "2025-04-07", "model_parameters": common_model_parameters, "supports_image_input": True,},
    "drozado/mistralai/Mixtral-8x7B-Instruct-v0.1-11d06fa6": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Mistral AI Mixtral-8x7B-Instruct-v0.1-11d06fa6", "snapshot_date": "2023-12-11", "model_parameters": common_model_parameters, "supports_image_input": False,},
    "drozado/meta-llama/Meta-Llama-3-70B-Instruct-Turbo-0019830d": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Meta Llama-3-70B-Instruct-Turbo", "snapshot_date": "2024-04-18", "model_parameters": common_model_parameters, "supports_image_input": False,},
    "drozado/google/gemma-2-9b-it-c190a2df": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Google gemma-2-9b-it", "snapshot_date": "2024-06-27", "model_parameters": common_model_parameters, "supports_image_input": False,},
    "drozado/meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-1030ae43": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Meta Llama-3.1-8B-Instruct-Turbo", "snapshot_date": "2024-08-22", "model_parameters": common_model_parameters, "supports_image_input": False,},
    "drozado/mistralai/Mixtral-8x22B-Instruct-v0.1-99187f2a": {"client": OpenAI(api_key=os.getenv("TOGETHER_AI_API_KEY"), base_url="https://api.together.xyz/v1"),"long_name": "Mistral AI Mixtral-8x22B-Instruct-v0.1-99187f2a", "snapshot_date": "2024-04-17", "model_parameters": common_model_parameters, "supports_image_input": False,},
}

MODELS_WITH_REASON_OFF = list(MODELS.keys())
MODELS_WITH_REASON_OFF.remove("grok-4.20-reasoning")
MODELS_WITH_REASON_OFF.remove("grok-4-1-fast-reasoning")

MODELS_WITH_CUSTOM_SYSTEM_PROMPTS = list(MODELS.keys())
for target_model in MODELS_WITH_CUSTOM_SYSTEM_PROMPTS:
    MODELS[f"{target_model}_centrist"] = {
        **MODELS[target_model],
        "api_model_name": target_model,
        "system_prompt_prefix": CENTRIST_LLM_SYSTEM_PROMPT,
    }
    MODELS[f"{target_model}_epistemically_rigorous"] = {
        **MODELS[target_model],
        "api_model_name": target_model,
        "system_prompt_prefix": EPISTEMICALLY_RIGOROUS_LLM_SYSTEM_PROMPT,
    }
