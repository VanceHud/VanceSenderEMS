"""AI generation history persistence for VanceSender.

Stores AI generation results as individual JSON files under ``data/ai_history/``.
Supports listing, starring, deleting, and auto-cleanup of old entries.
"""

from __future__ import annotations

import json
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import DATA_DIR

AI_HISTORY_DIR = DATA_DIR / "ai_history"
_MAX_UNSTARRED = 100


def _ensure_dir() -> None:
    AI_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, data: dict[str, Any]) -> None:
    """Atomic JSON write via temp-file + rename."""
    _ensure_dir()
    fd, tmp = tempfile.mkstemp(suffix=".tmp", prefix="aih_", dir=str(AI_HISTORY_DIR))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, str(path))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def save_generation(
    scenario: str,
    style: str,
    text_type: str,
    provider_id: str,
    texts: list[dict[str, str]],
) -> dict[str, Any]:
    """Save a new AI generation result. Returns the saved entry."""
    _ensure_dir()
    gen_id = f"gen_{uuid.uuid4().hex[:8]}"
    entry = {
        "id": gen_id,
        "scenario": scenario,
        "style": style,
        "text_type": text_type,
        "provider_id": provider_id,
        "texts": texts,
        "starred": False,
        "timestamp": _now_iso(),
    }
    _write_json(AI_HISTORY_DIR / f"{gen_id}.json", entry)
    _auto_cleanup()
    return entry


def list_history(limit: int = 20, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
    """List AI history entries sorted by timestamp descending.

    Returns (items, total_count).
    """
    _ensure_dir()
    entries: list[dict[str, Any]] = []
    for fp in AI_HISTORY_DIR.glob("gen_*.json"):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                entries.append(json.load(f))
        except (json.JSONDecodeError, OSError):
            continue

    entries.sort(key=lambda e: e.get("timestamp", ""), reverse=True)
    total = len(entries)
    return entries[offset : offset + limit], total


def toggle_star(gen_id: str) -> dict[str, Any] | None:
    """Toggle the starred status of an entry. Returns updated entry or None."""
    path = AI_HISTORY_DIR / f"{gen_id}.json"
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["starred"] = not data.get("starred", False)
        _write_json(path, data)
        return data
    except (json.JSONDecodeError, OSError):
        return None


def delete_entry(gen_id: str) -> bool:
    """Delete a single history entry."""
    path = AI_HISTORY_DIR / f"{gen_id}.json"
    if path.exists():
        path.unlink()
        return True
    return False


def clear_unstarred() -> int:
    """Delete all non-starred entries. Returns count deleted."""
    _ensure_dir()
    count = 0
    for fp in AI_HISTORY_DIR.glob("gen_*.json"):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data.get("starred", False):
                fp.unlink()
                count += 1
        except (json.JSONDecodeError, OSError):
            continue
    return count


def _auto_cleanup() -> None:
    """Keep at most _MAX_UNSTARRED non-starred entries (delete oldest)."""
    _ensure_dir()
    unstarred: list[tuple[str, Path]] = []
    for fp in AI_HISTORY_DIR.glob("gen_*.json"):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                data = json.load(f)
            if not data.get("starred", False):
                unstarred.append((data.get("timestamp", ""), fp))
        except (json.JSONDecodeError, OSError):
            continue

    if len(unstarred) <= _MAX_UNSTARRED:
        return

    # Sort oldest first, delete excess
    unstarred.sort(key=lambda x: x[0])
    to_delete = len(unstarred) - _MAX_UNSTARRED
    for _, fp in unstarred[:to_delete]:
        try:
            fp.unlink()
        except OSError:
            pass
