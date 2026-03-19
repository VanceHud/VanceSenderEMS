"""Advanced AI Conversation Tree — Node/Path planning system."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.ai_client import (
    _call_provider,
    _resolve_provider,
    _get_fallback_providers,
    _try_parse_json_array,
)

log = logging.getLogger(__name__)

# ── System Prompts ─────────────────────────────────────────────────────────

_TREE_INIT_SYSTEM = (
    "你是 FiveM 角色扮演对话策划助手。用户会描述一个场景，"
    "你需要生成：\n"
    "1. 我方「节点」：恰好 1 条 /me + 2 条 /do。\n"
    "2. 2~3 条「预测路径」（对方可能的回复）。\n\n"
    "节点规则：\n"
    "- /me（1条）：只描述自己角色的动作、表情、语气（第一人称，不带主语）。\n"
    "- 第一条 /do：描述当前环境氛围、可观察状态、声音等客观信息。"
    "**绝对不能**替对方角色做出任何动作、表情或决定。\n"
    "- 第二条 /do：向对方角色提出一个开放性的互动问题或情境引导，"
    "方便对方自然回复和互动（例如：'你似乎有话要说？'、'面前的人正等待你的回应'）。\n"
    "- 如果用户提供了「剧情风格」，你生成的所有文本必须**严格遵循该风格的笔触和氛围**，"
    "包括用词、节奏、情绪基调。\n"
    "- 预测路径应是对方角色可能发出的 /me 或 /do，覆盖不同可能性（如配合、抗拒、中立）。\n"
    "- 每条文本不超过80个字符。\n\n"
    "输出格式（必须严格遵守，只输出JSON，不要其他文字）：\n"
    '{"node":[{"type":"me","content":"..."},{"type":"do","content":"环境描述..."},{"type":"do","content":"互动问题..."}],'
    '"paths":[{"id":1,"label":"简短描述","content":"对方的完整回复"},'
    '{"id":2,"label":"简短描述","content":"对方的完整回复"}]}'
)

_TREE_NEXT_SYSTEM = (
    "你是 FiveM 角色扮演对话策划助手。根据之前的对话历史和对方最新的回复，"
    "生成下一轮我方「节点」和新的「预测路径」。\n\n"
    "节点规则（恰好 1 条 /me + 2 条 /do）：\n"
    "- /me（1条）：只描述自己角色的动作、表情、语气（第一人称，不带主语）。\n"
    "- 第一条 /do：描述当前环境氛围、可观察状态、声音等客观信息。"
    "**绝对不能**替对方角色做出任何动作、表情或决定。\n"
    "- 第二条 /do：向对方角色提出一个开放性的互动问题或情境引导，"
    "方便对方自然回复和互动。\n"
    "- 严禁替他人写动作、心理、决定。\n"
    "- 节点文本应自然衔接对方的回复，推进情节发展。\n"
    "- 如果用户提供了「剧情倾向」，你生成的节点和路径应**自然地朝该方向引导**，"
    "但不要生硬突兀，要保持角色扮演的真实感。\n"
    "- 如果用户提供了「剧情风格」，你生成的所有文本必须**严格遵循该风格的笔触和氛围**，"
    "包括用词、节奏、情绪基调。\n"
    "- 预测路径应覆盖不同可能性（如配合、抗拒、意外转折）。\n"
    "- 每条文本不超过80个字符。\n\n"
    "输出格式（必须严格遵守，只输出JSON）：\n"
    '{"node":[{"type":"me","content":"..."},{"type":"do","content":"环境描述..."},{"type":"do","content":"互动问题..."}],'
    '"paths":[{"id":1,"label":"简短描述","content":"对方的完整回复"},'
    '{"id":2,"label":"简短描述","content":"对方的完整回复"}]}'
)

_TREE_WRAPUP_SYSTEM = (
    "你是 FiveM 角色扮演对话策划助手。根据之前的对话历史，"
    "生成能够**优雅地收尾并结束当前场景**的节点（恰好 1 条 /me + 1 条 /do）。\n\n"
    "规则：\n"
    "- /me（1条）：描述自己角色的收尾动作（告别、离开等）。\n"
    "- /do（1条）：描述环境变化和客观状态，给场景画上自然句号。\n"
    "- 严禁替他人行动。\n"
    "- 每条文本不超过80个字符。\n\n"
    "输出格式（只输出JSON数组）：\n"
    '[{"type":"me","content":"..."},{"type":"do","content":"..."}]'
)


# ── History formatting ────────────────────────────────────────────────────


def _format_history_for_prompt(
    scenario: str,
    history: list[dict[str, Any]],
    chosen_reply: str | None = None,
    plot_tendency: str | None = None,
    plot_style: str | None = None,
) -> str:
    """Build a user prompt from scenario, conversation history, and optional new reply."""
    parts: list[str] = [f"原始场景：{scenario}"]

    if plot_style and plot_style.strip():
        parts.append(f"剧情风格：{plot_style.strip()}")

    parts.extend(["", "对话历史："])

    for entry in history:
        role = entry.get("role", "")
        content = entry.get("content", "")
        if role == "node":
            parts.append(f"[我方发言] {content}")
        elif role == "path":
            parts.append(f"[对方回复] {content}")

    if chosen_reply:
        parts.append(f"\n对方最新回复：{chosen_reply}")
        if plot_tendency and plot_tendency.strip():
            parts.append(f"\n剧情倾向：{plot_tendency.strip()}")
        parts.append("\n请根据以上对话历史和对方最新回复，生成下一轮我方节点和预测路径。")
    else:
        parts.append("\n请根据以上对话历史，生成收尾节点。")

    return "\n".join(parts)


# ── Response parsing ──────────────────────────────────────────────────────


def _parse_tree_response(raw: str) -> dict[str, Any]:
    """Parse AI response into structured node/paths data.

    Expected format: {"node": [...], "paths": [...]}
    """
    text = raw.strip()

    # Try to find the JSON object
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < 0 or end <= start:
        raise RuntimeError("AI返回格式异常，缺少JSON对象。")

    try:
        payload = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        raise RuntimeError("AI返回格式异常，JSON解析失败。") from exc

    if not isinstance(payload, dict):
        raise RuntimeError("AI返回格式异常，结果不是对象。")

    # Validate node
    node = payload.get("node", [])
    if not isinstance(node, list) or not node:
        raise RuntimeError("AI返回格式异常，缺少有效节点。")

    validated_node: list[dict[str, str]] = []
    for item in node:
        if not isinstance(item, dict):
            continue
        t = item.get("type", "")
        c = item.get("content", "")
        if t in ("me", "do", "/me", "/do") and isinstance(c, str) and c.strip():
            validated_node.append({
                "type": t.lstrip("/"),
                "content": c.strip()[:80],
            })

    if not validated_node:
        raise RuntimeError("AI返回格式异常，节点内容为空。")

    # Validate paths
    paths = payload.get("paths", [])
    validated_paths: list[dict[str, Any]] = []
    if isinstance(paths, list):
        for idx, p in enumerate(paths):
            if not isinstance(p, dict):
                continue
            pid = p.get("id", idx + 1)
            label = str(p.get("label", f"路径{idx + 1}")).strip()
            content = str(p.get("content", "")).strip()
            if content:
                validated_paths.append({
                    "id": pid,
                    "label": label[:30],
                    "content": content[:200],
                })

    return {"node": validated_node, "paths": validated_paths}


def _parse_wrapup_response(raw: str) -> list[dict[str, str]]:
    """Parse wrapup AI response — expects a JSON array."""
    result = _try_parse_json_array(raw)
    if result:
        return [
            {"type": item["type"], "content": item["content"][:80]}
            for item in result
            if item.get("type") in ("me", "do") and item.get("content", "").strip()
        ]
    raise RuntimeError("AI收尾返回格式异常，无法解析JSON数组。")


# ── Public API ────────────────────────────────────────────────────────────


async def generate_initial_tree(
    scenario: str,
    provider_id: str | None = None,
    temperature: float | None = None,
    plot_style: str | None = None,
) -> tuple[dict[str, Any], str]:
    """Generate the initial node + predicted paths for a scenario.

    Returns:
        Tuple of (tree_data, resolved_provider_id).
        tree_data = {"node": [...], "paths": [...]}
    """
    cfg, provider = _resolve_provider(provider_id)
    resolved_pid = provider.get("id", "")

    user_parts = [f"场景描述：{scenario}"]
    if plot_style and plot_style.strip():
        user_parts.append(f"剧情风格：{plot_style.strip()}")
    user_parts.append("\n请生成初始节点和预测路径。")

    messages = [
        {"role": "system", "content": _TREE_INIT_SYSTEM},
        {"role": "user", "content": "\n".join(user_parts)},
    ]

    temp = temperature if temperature is not None else 0.8

    # Try primary provider, then fallbacks
    providers_to_try = [(provider, resolved_pid)]
    for fb in _get_fallback_providers(cfg, exclude_id=resolved_pid):
        providers_to_try.append((fb, fb.get("id", "")))

    last_error: Exception | None = None
    for prov, pid in providers_to_try:
        try:
            raw = await _call_provider(prov, cfg, messages, temp, 2048)
            tree_data = _parse_tree_response(raw)
            if pid != resolved_pid:
                log.info("Conversation tree init: fallback to '%s' succeeded", pid)
            return tree_data, pid
        except Exception as exc:
            log.warning("Conversation tree init: provider '%s' failed: %s", pid, exc)
            last_error = exc
            continue

    raise last_error  # type: ignore[misc]


async def generate_next_node(
    scenario: str,
    conversation_history: list[dict[str, Any]],
    chosen_reply: str,
    provider_id: str | None = None,
    temperature: float | None = None,
    plot_tendency: str | None = None,
    plot_style: str | None = None,
) -> tuple[dict[str, Any], str]:
    """Generate the next node + paths based on conversation history and the other party's reply.

    Returns:
        Tuple of (tree_data, resolved_provider_id).
    """
    cfg, provider = _resolve_provider(provider_id)
    resolved_pid = provider.get("id", "")

    user_prompt = _format_history_for_prompt(scenario, conversation_history, chosen_reply, plot_tendency, plot_style)
    messages = [
        {"role": "system", "content": _TREE_NEXT_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    temp = temperature if temperature is not None else 0.8

    providers_to_try = [(provider, resolved_pid)]
    for fb in _get_fallback_providers(cfg, exclude_id=resolved_pid):
        providers_to_try.append((fb, fb.get("id", "")))

    last_error: Exception | None = None
    for prov, pid in providers_to_try:
        try:
            raw = await _call_provider(prov, cfg, messages, temp, 2048)
            tree_data = _parse_tree_response(raw)
            if pid != resolved_pid:
                log.info("Conversation tree next: fallback to '%s' succeeded", pid)
            return tree_data, pid
        except Exception as exc:
            log.warning("Conversation tree next: provider '%s' failed: %s", pid, exc)
            last_error = exc
            continue

    raise last_error  # type: ignore[misc]


async def generate_wrapup(
    scenario: str,
    conversation_history: list[dict[str, Any]],
    provider_id: str | None = None,
    temperature: float | None = None,
) -> tuple[list[dict[str, str]], str]:
    """Generate wrap-up node to gracefully end the conversation.

    Returns:
        Tuple of (node_texts, resolved_provider_id).
    """
    cfg, provider = _resolve_provider(provider_id)
    resolved_pid = provider.get("id", "")

    user_prompt = _format_history_for_prompt(scenario, conversation_history)
    messages = [
        {"role": "system", "content": _TREE_WRAPUP_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    temp = temperature if temperature is not None else 0.7

    providers_to_try = [(provider, resolved_pid)]
    for fb in _get_fallback_providers(cfg, exclude_id=resolved_pid):
        providers_to_try.append((fb, fb.get("id", "")))

    last_error: Exception | None = None
    for prov, pid in providers_to_try:
        try:
            raw = await _call_provider(prov, cfg, messages, temp, 1024)
            node_texts = _parse_wrapup_response(raw)
            if not node_texts:
                raise RuntimeError("AI收尾返回内容为空。")
            if pid != resolved_pid:
                log.info("Conversation tree wrapup: fallback to '%s' succeeded", pid)
            return node_texts, pid
        except Exception as exc:
            log.warning("Conversation tree wrapup: provider '%s' failed: %s", pid, exc)
            last_error = exc
            continue

    raise last_error  # type: ignore[misc]
