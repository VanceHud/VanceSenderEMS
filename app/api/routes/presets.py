"""Preset CRUD routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    MessageResponse,
    PresetCreate,
    PresetResponse,
    PresetUpdate,
)
from app.core.presets import (
    PresetError,
    PresetNotFoundError,
    delete_preset_file,
    list_all_presets,
    now_iso,
    read_preset,
    write_preset,
)

router = APIRouter()


def _handle_preset_error(exc: PresetError) -> HTTPException:
    """Convert domain preset errors into HTTP exceptions."""
    return HTTPException(status_code=exc.status_code, detail=str(exc))


@router.get("", response_model=list[PresetResponse])
async def list_presets():
    """列出所有预设。"""
    return list_all_presets()


@router.post("", response_model=PresetResponse, status_code=201)
async def create_preset(body: PresetCreate):
    """创建新预设。"""
    now = now_iso()
    preset_id = uuid.uuid4().hex[:8]
    data = {
        "id": preset_id,
        "name": body.name,
        "texts": [t.model_dump() for t in body.texts],
        "created_at": now,
        "updated_at": now,
    }
    try:
        write_preset(preset_id, data)
    except PresetError as exc:
        raise _handle_preset_error(exc)
    return data


@router.get("/{preset_id}", response_model=PresetResponse)
async def get_preset(preset_id: str):
    """获取单个预设。"""
    try:
        return read_preset(preset_id)
    except PresetError as exc:
        raise _handle_preset_error(exc)


@router.put("/{preset_id}", response_model=PresetResponse)
async def update_preset(preset_id: str, body: PresetUpdate):
    """更新预设。"""
    try:
        data = read_preset(preset_id)
    except PresetError as exc:
        raise _handle_preset_error(exc)

    if body.name is not None:
        data["name"] = body.name
    if body.texts is not None:
        data["texts"] = [t.model_dump() for t in body.texts]
    data["updated_at"] = now_iso()

    try:
        write_preset(preset_id, data)
    except PresetError as exc:
        raise _handle_preset_error(exc)
    return data


@router.delete("/{preset_id}", response_model=MessageResponse)
async def delete_preset(preset_id: str):
    """删除预设。"""
    try:
        delete_preset_file(preset_id)
    except PresetError as exc:
        raise _handle_preset_error(exc)
    return MessageResponse(message=f"预设 '{preset_id}' 已删除")
