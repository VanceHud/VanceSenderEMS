"""Send statistics API routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import MessageResponse
from app.core.stats import get_stats, reset_stats

router = APIRouter()


@router.get("")
async def get_send_stats():
    """获取发送统计数据。"""
    return get_stats()


@router.delete("", response_model=MessageResponse)
async def clear_send_stats():
    """重置发送统计。"""
    reset_stats()
    return MessageResponse(message="统计数据已重置")
