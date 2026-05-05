from typing import Any, Dict, Optional
import asyncio
import os
import re
import warnings
import pandas as pd
from tqdm.asyncio import tqdm_asyncio
from vpei.models import MODELS


from requests.exceptions import HTTPError


def get_provider_for_model_name(model_name: str) -> Optional[str]:
    if model_name in MODELS:
        client = MODELS[model_name]["client"]
        client_type = type(client).__name__

        if client_type in ["Anthropic", "AsyncAnthropic"]:
            return "anthropic"

        if hasattr(client, "base_url"):
            base_url = str(client.base_url).lower()
            if "openai.com" in base_url:
                return "openai"
            if "together.xyz" in base_url:
                return "together_ai"
            if "googleapis.com" in base_url:
                return "gemini"
            if "x.ai" in base_url:
                return "xai"
    return None

def _get_output_csv_path(folder_path: str, model_name: str, model_kwargs: dict = {}) -> str:
    """Build the CSV output path for a model (mirrors the logic in save_model_experimental_results_to_csv)."""
    safe_model_name = model_name.replace('/', '_').replace(':', '_')
    path = os.path.join(folder_path, f"{safe_model_name}.csv")
    if model_kwargs.get("reasoning_effort", None) not in [None, "none", "minimal"]:
        reasoning_effort = model_kwargs["reasoning_effort"]
        path = os.path.join(folder_path, f"{safe_model_name}_reasoning_effort_{reasoning_effort}.csv")
    return path


def compute_effective_seed(base_seed: int, path_to_save: str, model_name: str, model_kwargs: dict, append_if_exists: bool) -> int:
    """
    When appending to an existing CSV, offset the random seed by the number of already-saved rows.
    This ensures each append run draws a fresh, non-overlapping sample rather than repeating the
    same stimuli and (with temperature=0) identical model responses.
    """
    _append = append_if_exists or os.environ.get('APPEND_EXPERIMENT_RESULTS', '').lower() in ('1', 'true')
    if not _append:
        return base_seed
    csv_path = _get_output_csv_path(path_to_save, model_name, model_kwargs)
    if os.path.exists(csv_path):
        try:
            existing_rows = len(pd.read_csv(csv_path, usecols=[0]))
            return base_seed + existing_rows
        except Exception:
            pass
    return base_seed


def save_model_experimental_results_to_csv(df, folder_path: str, model_name: str, model_kwargs: dict = {}, append_if_exists: bool = False) -> None:
    """
    Save the results of model experiments to a CSV file.
    Each payload in the list should contain the necessary fields.
    """

    if not isinstance(df, pd.DataFrame):
        df = pd.DataFrame(df[model_name])

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    output_csv_path = _get_output_csv_path(folder_path, model_name, model_kwargs)
    _append = append_if_exists or os.environ.get('APPEND_EXPERIMENT_RESULTS', '').lower() in ('1', 'true')
    if _append and os.path.exists(output_csv_path):
        df.to_csv(output_csv_path, mode='a', header=False, index=False)
        print(f"Appended experiment results to {output_csv_path}")
    else:
        df.to_csv(output_csv_path, index=False)
        print(f"Saved experiment results to {output_csv_path}")



def suppress_pydantic_serialization_warnings() -> None:
    """
    Suppress noisy Pydantic serialization warnings about unexpected values.
    """
    try:
        from pydantic.warnings import PydanticWarning
    except Exception:
        PydanticWarning = UserWarning

    warnings.filterwarnings(
        "ignore",
        message=r".*PydanticSerializationUnexpectedValue.*",
        category=PydanticWarning,
        module=r"pydantic.*",
    )
    warnings.filterwarnings(
        "ignore",
        message=r"^Pydantic serializer warnings:.*",
        category=PydanticWarning,
        module=r"pydantic.*",
    )


# Define your custom exception
class RegexNotInTextResponseError(Exception):
    """Custom exception raised when a regex is not in a text response."""
    def __init__(self, regex, response_text):
        super().__init__(f"The required pattern: {regex} was not found in the response text: {response_text}")


# Custom retry condition: Retry for server-side errors (e.g., 5xx HTTP errors) and rate limit errors (429)
def is_retryable_exception(exception):
    if isinstance(exception, HTTPError):
        # Retry for 5xx server errors
        if 500 <= exception.response.status_code < 600:
            return True
        # Retry for rate limit errors (429)
        if exception.response.status_code == 429:
            return True
    # Retry for LLM API exceptions with retryable status codes (5xx, 429)
    if hasattr(exception, 'status_code') and isinstance(exception.status_code, int):
        if 500 <= exception.status_code < 600 or exception.status_code == 429:
            return True
    # Retry for timeout errors (covers asyncio.TimeoutError, httpx.TimeoutException, openai.APITimeoutError, etc.)
    if 'timeout' in type(exception).__name__.lower():
        return True
    # Add other retryable exceptions here if needed
    if isinstance(exception, RegexNotInTextResponseError):
        return True
    return False
