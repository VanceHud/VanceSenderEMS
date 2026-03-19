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
    client = _get_gemini_client(api_key)
    try:
        response = await client.aio.models.generate_content(
            model=model,
            contents="Hi",
            config=types.GenerateContentConfig(max_output_tokens=10),
        )
        return {"success": True, "response": response.text or ""}
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "error_type": type(exc).__name__,
        }
