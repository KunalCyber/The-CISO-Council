"""LLM provider abstraction for The CISO Council.

Supports:
- Google Gemini via google-genai SDK
- Anthropic Claude via anthropic SDK
- OpenAI-compatible APIs: OpenAI, Groq, Mistral, OpenRouter, DeepSeek, Cerebras, xAI

All providers expose a single interface:
    get_completion(provider, model, messages, api_key, timeout) -> str

API keys are never logged, printed, or included in exception messages.
All error messages are sanitised before surfacing.
"""

from __future__ import annotations

import asyncio
import re
from typing import Any

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

# ─── Error sanitisation ───────────────────────────────────────────────────────

# Patterns that look like API keys. Matched and redacted from all error output.
_KEY_PATTERN = re.compile(
    r"\b("
    r"sk-ant-[A-Za-z0-9_\-]{20,}"      # Anthropic
    r"|sk-[A-Za-z0-9_\-]{20,}"          # OpenAI / generic sk-
    r"|gsk_[A-Za-z0-9_\-]{20,}"         # Groq
    r"|xai-[A-Za-z0-9_\-]{20,}"         # xAI
    r"|AIza[A-Za-z0-9_\-]{20,}"         # Google
    r"|nvapi-[A-Za-z0-9_\-]{20,}"       # NVIDIA
    r")\b",
    re.IGNORECASE,
)


def sanitise_error(message: str) -> str:
    """Redact any API key patterns from an error string before logging or raising.

    Args:
        message: Raw error message that may contain credentials.

    Returns:
        The message with all recognised key patterns replaced by [REDACTED].
    """
    return _KEY_PATTERN.sub("[REDACTED]", str(message))


# ─── Provider registry ────────────────────────────────────────────────────────

# Base URLs for OpenAI-compatible providers. None means use the SDK default.
_OPENAI_BASE_URLS: dict[str, str | None] = {
    "groq":       "https://api.groq.com/openai/v1",
    "mistral":    "https://api.mistral.ai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "deepseek":   "https://api.deepseek.com/v1",
    "cerebras":   "https://api.cerebras.ai/v1",
    "xai":        "https://api.x.ai/v1",
    "openai":     None,
}

SUPPORTED_PROVIDERS = {"google", "anthropic"} | set(_OPENAI_BASE_URLS.keys())

# Extra headers required by OpenRouter
_OPENROUTER_HEADERS: dict[str, str] = {
    "HTTP-Referer": "https://github.com/kunal-rk/the-ciso-council",
    "X-Title": "The CISO Council",
}


# ─── Public interface ─────────────────────────────────────────────────────────

async def get_completion(
    provider: str,
    model: str,
    messages: list[dict[str, str]],
    api_key: str,
    timeout: int = 120,
    temperature: float = 0.7,
    json_mode: bool = False,
) -> str:
    """Get a completion from any supported LLM provider.

    Args:
        provider: Provider name (google, anthropic, openai, groq, mistral,
            openrouter, deepseek, cerebras, xai).
        model: Model identifier as the provider expects it.
        messages: List of message dicts with 'role' and 'content' keys.
        api_key: API key for the provider. Never logged or included in errors.
        timeout: Request timeout in seconds.
        temperature: Sampling temperature. Use 0 for deterministic output.
        json_mode: If True, instruct the model to return valid JSON only.

    Returns:
        The model's response as a plain string.

    Raises:
        ValueError: If the provider is not supported.
        RuntimeError: If the API call fails after all retries.
    """
    provider = provider.strip().lower()
    if provider == "google":
        return await _google_completion(model, messages, api_key, timeout, temperature, json_mode)
    if provider == "anthropic":
        return await _anthropic_completion(model, messages, api_key, timeout, temperature)
    if provider in _OPENAI_BASE_URLS:
        return await _openai_compatible_completion(
            provider, model, messages, api_key, timeout, temperature, json_mode
        )
    raise ValueError(
        f"Unsupported provider '{provider}'. "
        f"Supported: {', '.join(sorted(SUPPORTED_PROVIDERS))}"
    )


# ─── Google Gemini ────────────────────────────────────────────────────────────

async def _google_completion(
    model: str,
    messages: list[dict[str, str]],
    api_key: str,
    timeout: int,
    temperature: float = 0.7,
    json_mode: bool = False,
) -> str:
    """Get a completion from Google Gemini via the google-genai SDK."""
    from google import genai
    from google.genai import types

    system_instruction = next(
        (m["content"] for m in messages if m["role"] == "system"), None
    )
    user_content = "\n\n".join(
        m["content"] for m in messages if m["role"] != "system"
    )

    config_kwargs: dict[str, Any] = {"temperature": temperature}
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction
    if json_mode:
        config_kwargs["response_mime_type"] = "application/json"

    gen_config = types.GenerateContentConfig(**config_kwargs)
    client = genai.Client(api_key=api_key)

    try:
        return await _call_google(client, model, user_content, gen_config)
    except AttributeError:
        # Older SDK versions may not expose client.aio; run sync in executor.
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: client.models.generate_content(
                model=model,
                contents=user_content,
                config=gen_config,
            ).text,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Google Gemini call failed (model='{model}'): "
            f"{type(exc).__name__}: {sanitise_error(str(exc))}"
        ) from exc


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    reraise=True,
)
async def _call_google(client: Any, model: str, user_content: str, gen_config: Any) -> str:
    """Inner retry wrapper for the Google async API call."""
    response = await client.aio.models.generate_content(
        model=model,
        contents=user_content,
        config=gen_config,
    )
    return response.text


# ─── Anthropic Claude ─────────────────────────────────────────────────────────

async def _anthropic_completion(
    model: str,
    messages: list[dict[str, str]],
    api_key: str,
    timeout: int,
    temperature: float = 0.7,
) -> str:
    """Get a completion from Anthropic Claude via the anthropic SDK."""
    import anthropic

    system_text = next(
        (m["content"] for m in messages if m["role"] == "system"), None
    )
    user_messages = [m for m in messages if m["role"] != "system"]

    client = anthropic.AsyncAnthropic(api_key=api_key)

    try:
        return await _call_anthropic(client, model, user_messages, system_text, temperature, timeout)
    except Exception as exc:
        raise RuntimeError(
            f"Anthropic call failed (model='{model}'): "
            f"{type(exc).__name__}: {sanitise_error(str(exc))}"
        ) from exc


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    reraise=True,
)
async def _call_anthropic(
    client: Any,
    model: str,
    messages: list[dict[str, str]],
    system: str | None,
    temperature: float,
    timeout: int,
) -> str:
    """Inner retry wrapper for the Anthropic async API call."""
    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": 2048,
        "messages": messages,
        "temperature": temperature,
        "timeout": float(timeout),
    }
    if system:
        kwargs["system"] = system

    response = await client.messages.create(**kwargs)
    return response.content[0].text


# ─── OpenAI-Compatible Providers ─────────────────────────────────────────────

async def _openai_compatible_completion(
    provider: str,
    model: str,
    messages: list[dict[str, str]],
    api_key: str,
    timeout: int,
    temperature: float = 0.7,
    json_mode: bool = False,
) -> str:
    """Get a completion from an OpenAI-compatible API endpoint."""
    from openai import AsyncOpenAI

    base_url = _OPENAI_BASE_URLS[provider]
    extra_headers = _OPENROUTER_HEADERS if provider == "openrouter" else {}

    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=float(timeout),
        default_headers=extra_headers,
    )

    try:
        return await _call_openai(client, model, messages, temperature, json_mode)
    except Exception as exc:
        raise RuntimeError(
            f"Provider '{provider}' call failed (model='{model}'): "
            f"{type(exc).__name__}: {sanitise_error(str(exc))}"
        ) from exc


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    reraise=True,
)
async def _call_openai(
    client: Any,
    model: str,
    messages: list[dict[str, str]],
    temperature: float = 0.7,
    json_mode: bool = False,
) -> str:
    """Inner retry wrapper for the OpenAI-compatible API call."""
    kwargs: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1500,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    response = await client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
