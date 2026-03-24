"""Preset storage management for VanceSender.

Handles preset file CRUD: read, write (atomic), list, delete.
All preset files are stored as individual JSON files under ``PRESETS_DIR``.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import PRESETS_DIR


_SAFE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


class PresetError(Exception):
    """Domain error for preset operations."""

    def __init__(self, message: str, *, status_code: int = 400) -> None:
        super().__init__(message)
        self.status_code = status_code


class PresetNotFoundError(PresetError):
    """Raised when a preset does not exist."""

    def __init__(self, preset_id: str) -> None:
        super().__init__(f"预设 '{preset_id}' 不存在", status_code=404)


def validate_preset_id(preset_id: str) -> str:
    """Validate preset_id to prevent path-traversal attacks.

    Returns the sanitized id string.
    Raises ``PresetError`` if invalid.
    """
    safe_id = str(preset_id).strip()
    if not safe_id or not _SAFE_ID_RE.fullmatch(safe_id):
        raise PresetError(f"预设 ID '{preset_id}' 包含非法字符")
    return safe_id


def preset_path(preset_id: str) -> Path:
    """Return filesystem path for a given preset id."""
    safe_id = validate_preset_id(preset_id)
    return PRESETS_DIR / f"{safe_id}.json"


def _normalize_preset_data(raw: Any, *, fallback_id: str) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None

    name = str(raw.get("name", "")).strip()
    texts_raw = raw.get("texts")
    if not name or not isinstance(texts_raw, list):
        return None

    texts: list[dict[str, str]] = []
    for item in texts_raw:
        if not isinstance(item, dict):
            continue
        content = str(item.get("content", "")).strip()
        if not content:
            continue
        line_type = str(item.get("type", "me")).strip()
        if line_type not in ("me", "do", "b", "e"):
            line_type = "me"
        texts.append({"type": line_type, "content": content})

    tags_raw = raw.get("tags", [])
    tags = []
    if isinstance(tags_raw, list):
        tags = [str(tag).strip() for tag in tags_raw if str(tag).strip()]

    sort_order_raw = raw.get("sort_order", 0)
    sort_order = int(sort_order_raw) if isinstance(sort_order_raw, (int, float)) else 0
    created_at = str(raw.get("created_at", "")).strip() or now_iso()
    updated_at = str(raw.get("updated_at", "")).strip() or created_at
    preset_id = str(raw.get("id", "")).strip() or fallback_id

    return {
        "id": validate_preset_id(preset_id),
        "name": name,
        "texts": texts,
        "tags": tags,
        "sort_order": sort_order,
        "created_at": created_at,
        "updated_at": updated_at,
    }


def read_preset(preset_id: str) -> dict[str, Any]:
    """Read a single preset from disk.

    Raises ``PresetNotFoundError`` if the file does not exist.
    Raises ``PresetError`` on read/parse failure.
    """
    path = preset_path(preset_id)
    if not path.exists():
        raise PresetNotFoundError(preset_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        data = _normalize_preset_data(raw, fallback_id=path.stem)
        if data is None:
            raise PresetError("预设文件内容无效", status_code=500)
        return data
    except (json.JSONDecodeError, OSError) as exc:
        raise PresetError(f"预设文件读取失败: {exc}", status_code=500) from exc


def write_preset(preset_id: str, data: dict[str, Any]) -> None:
    """Write preset data atomically via temp-file + rename.

    Raises ``PresetError`` on write failure.
    """
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    target = preset_path(preset_id)
    try:
        fd, tmp_path = tempfile.mkstemp(
            suffix=".tmp", prefix="preset_", dir=str(PRESETS_DIR)
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, str(target))
        except BaseException:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
    except OSError as exc:
        raise PresetError(f"预设文件写入失败: {exc}", status_code=500) from exc


def list_all_presets(*, tag_filter: str | None = None) -> list[dict[str, Any]]:
    """List all presets sorted by sort_order then name.

    If *tag_filter* is given, only presets containing that tag are returned.
    """
    PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    presets: list[dict[str, Any]] = []
    for fp in sorted(PRESETS_DIR.glob("*.json")):
        try:
            with open(fp, "r", encoding="utf-8") as f:
                raw = json.load(f)
            data = _normalize_preset_data(raw, fallback_id=fp.stem)
        except (json.JSONDecodeError, OSError, PresetError):
            continue

        if data is None:
            continue
        if tag_filter and tag_filter not in data.get("tags", []):
            continue

        presets.append(data)

    # Sort by sort_order (ascending), then by name
    presets.sort(key=lambda p: (p.get("sort_order", 0), p.get("name", "")))
    return presets


def delete_preset_file(preset_id: str) -> None:
    """Delete a preset file from disk.

    Raises ``PresetNotFoundError`` if the file does not exist.
    Raises ``PresetError`` on delete failure.
    """
    path = preset_path(preset_id)
    if not path.exists():
        raise PresetNotFoundError(preset_id)
    try:
        path.unlink()
    except OSError as exc:
        raise PresetError(f"预设删除失败: {exc}", status_code=500) from exc


def now_iso() -> str:
    """Return current UTC time as ISO 8601 string."""
    return datetime.now(timezone.utc).isoformat()
