"""Simple Bearer token authentication for VanceSender API."""

from __future__ import annotations

import hmac
import threading

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import load_config

_bearer = HTTPBearer(auto_error=False)

# ── Token cache ───────────────────────────────────────────────────────────
# Avoids reading config.yaml on every single API request.

_token_cache_lock = threading.Lock()
_cached_token: str | None = None  # None = not yet loaded
_cache_initialized = False


def _load_token_into_cache() -> str:
    """Read token from config and cache it. Returns the token string."""
    global _cached_token, _cache_initialized
    try:
        cfg = load_config()
        token = cfg.get("server", {}).get("token", "")
    except Exception:
        token = ""
    _cached_token = token
    _cache_initialized = True
    return token


def _get_cached_token() -> str:
    """Return cached token, initializing on first access."""
    global _cache_initialized
    if _cache_initialized and _cached_token is not None:
        return _cached_token
    with _token_cache_lock:
        if _cache_initialized and _cached_token is not None:
            return _cached_token
        return _load_token_into_cache()


def invalidate_token_cache() -> None:
    """Clear the cached token so the next request re-reads from config.

    Should be called whenever server.token is modified via settings API.
    """
    global _cached_token, _cache_initialized
    with _token_cache_lock:
        _cached_token = None
        _cache_initialized = False


# ── Dependency ────────────────────────────────────────────────────────────


async def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    """FastAPI dependency — skip auth when no token is configured.

    When ``server.token`` is set in config, every API request must include
    ``Authorization: Bearer <token>``.  If the header is missing or the
    token does not match, a 401 is returned.

    Uses ``hmac.compare_digest`` for timing-safe comparison.
    """
    token = _get_cached_token()

    # No token configured → auth disabled
    if not token:
        return

    if credentials is None or not hmac.compare_digest(
        credentials.credentials.encode("utf-8"),
        token.encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未授权访问，请提供有效的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
