"""Native Google Gemini client using the google-genai SDK."""

from __future__ import annotations

import logging
import threading
from typing import Any, AsyncIterator

from google import genai
from google.genai import types

log = logging.getLogger(__name__)

# ── Client cache (keyed by api_key) ──────────────────────────────────────

_gemini_cache_lock = threading.Lock()
_gemini_cache: dict[str, genai.Client] = {}


def _get_gemini_client(api_key: str) -> genai.Client:
    """Return a cached Gemini client for the given API key."""
    with _gemini_cache_lock:
        cached = _gemini_cache.get(api_key)
        if cached is not None:
            return cached

    client = genai.Client(api_key=api_key)

    with _gemini_cache_lock:
        _gemini_cache[api_key] = client

    return client


def invalidate_gemini_cache() -> None:
    """Clear all cached Gemini clients."""
    with _gemini_cache_lock:
        _gemini_cache.clear()


# ── Model name helpers ────────────────────────────────────────────────────


def _sanitize_model_name(model: str) -> str:
    """Normalise user-supplied model name.

    The google-genai SDK expects bare names like 'gemini-2.0-flash'.
    Users sometimes paste 'models/gemini-2.0-flash' from the docs,
    which causes a 404.  Strip the prefix transparently.
    """
    name = model.strip()
    if name.startswith("models/"):
        name = name[len("models/"):]
    return name


# ── Message conversion ───────────────────────────────────────────────────


def _openai_messages_to_contents(
    messages: list[dict[str, str]],
) -> tuple[str | None, list[types.Content]]:
    """Convert OpenAI-style messages to Gemini contents.

    Extracts the system message (if any) and converts user/assistant
    messages to Gemini Content objects.

    Returns:
        Tuple of (system_instruction, contents_list).
    """
    system_instruction: str | None = None
    contents: list[types.Content] = []

    for msg in messages:
        role = msg.get("role", "user")
        text = msg.get("content", "")

        if role == "system":
            system_instruction = text
            continue

        # Gemini uses "model" instead of "assistant"
        gemini_role = "model" if role == "assistant" else "user"
        contents.append(
            types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=text)],
            )
        )

    return system_instruction, contents


# ── Public API ───────────────────────────────────────────────────────────


async def gemini_generate(
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float = 0.8,
    max_tokens: int = 2048,
) -> str:
    """Generate text using the native Gemini SDK.

    Args:
        api_key: Gemini API key.
        model: Model name (e.g. 'gemini-2.0-flash').
        messages: OpenAI-style messages list [{role, content}].
        temperature: Generation temperature.
        max_tokens: Maximum output tokens.

    Returns:
        Raw text response from Gemini.
    """
    client = _get_gemini_client(api_key)
    model = _sanitize_model_name(model)
    system_instruction, contents = _openai_messages_to_contents(messages)

    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    if system_instruction:
        config.system_instruction = system_instruction

    response = await client.aio.models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )

    return response.text or ""


async def gemini_generate_stream(
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float = 0.8,
    max_tokens: int = 2048,
) -> AsyncIterator[str]:
    """Stream text generation using the native Gemini SDK.

    Yields raw text chunks as they arrive.
    """
    client = _get_gemini_client(api_key)
    model = _sanitize_model_name(model)
    system_instruction, contents = _openai_messages_to_contents(messages)

    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_tokens,
    )
    if system_instruction:
        config.system_instruction = system_instruction

    async for chunk in client.aio.models.generate_content_stream(
        model=model,
        contents=contents,
        config=config,
    ):
        if chunk.text:
            yield chunk.text


async def gemini_test(api_key: str, model: str) -> dict[str, Any]:
    """Send a tiny request to verify Gemini connectivity.

    Returns:
        Dict with 'success' key and either 'response' or error details.
    """
    model = _sanitize_model_name(model)
    client = _get_gemini_client(api_key)
    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents="Hi",
            config=types.GenerateContentConfig(max_output_tokens=10),
        )
        return {"success": True, "response": response.text or ""}
    except Exception as exc:
        error_msg = str(exc)
        status_code = getattr(exc, "code", None) or getattr(exc, "status_code", None)

        # Provide actionable hints for common errors
        hint = ""
        if status_code == 404 or "404" in error_msg:
            hint = (
                f"模型 '{model}' 未找到。请确认："
                "1) 模型名称正确（如 gemini-2.0-flash）；"
                "2) API Key 有权访问该模型；"
                "3) 你所在区域支持该模型。"
            )
        elif status_code == 403 or "403" in error_msg:
            hint = "API Key 无权访问，请检查 Google AI Studio 中的项目权限。"
        elif status_code == 400 or "400" in error_msg:
            hint = "请求参数有误，请检查 API Key 格式是否正确。"

        result: dict[str, Any] = {
            "success": False,
            "error": error_msg,
            "error_type": type(exc).__name__,
        }
        if status_code is not None:
            result["status_code"] = status_code
        if hint:
            result["hint"] = hint
        return result
