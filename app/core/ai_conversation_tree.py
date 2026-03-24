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
    "你是 FiveM 医疗角色扮演对话策划助手。用户扮演 EMS / 医生 / 急救人员。"
    "用户会描述一个医疗场景，"
    "你需要生成：\n"
    "1. 我方「节点」：恰好 1 条 /me + 2 条 /do。\n"
    "2. 2~3 条「预测路径」（患者/旁人可能的反应）。\n"
    "3. 当前「生命体征」摘要。\n\n"
    "节点规则：\n"
    "- /me（1条）：只描述自己角色的医疗操作（检查、包扎、注射、CPR等），"
    "第一人称，不带主语。\n"
    "- 第一条 /do：描述患者当前体征、伤情状态、医疗设备读数等客观信息。"
    "**绝对不能**替患者或他人做决定。\n"
    "- 第二条 /do：向患者或旁人提出互动引导"
    "（例如：'你能听到我说话吗？'、'旁边的人紧张地看着急救过程'）。\n"
    "- 如果用户提供了「剧情风格」，你生成的所有文本必须**严格遵循该风格的笔触和氛围**。\n"
    "- 适当使用医学术语（GCS、SpO2、BP等），但保持可读性。\n"
    "- 预测路径应覆盖不同可能性（患者配合、恐慌、失去意识、旁人干预等）。\n"
    "- 每条文本不超过80个字符。\n\n"
    "输出格式（必须严格遵守，只输出JSON，不要其他文字）：\n"
    '{"node":[{"type":"me","content":"..."},{"type":"do","content":"体征/状态..."},{"type":"do","content":"互动引导..."}],'
    '"paths":[{"id":1,"label":"简短描述","content":"患者/旁人的反应"},'
    '{"id":2,"label":"简短描述","content":"患者/旁人的反应"}],'
    '"vitals":{"heart_rate":"--","blood_pressure":"--","spo2":"--","gcs":"--","consciousness":"待评估","summary":"初步接触，体征待评估"}}'
)

_TREE_NEXT_SYSTEM = (
    "你是 FiveM 医疗角色扮演对话策划助手。根据之前的对话历史和患者/旁人最新的反应，"
    "生成下一轮我方「节点」、新的「预测路径」和更新后的「生命体征」。\n\n"
    "节点规则（恰好 1 条 /me + 2 条 /do）：\n"
    "- /me（1条）：只描述自己角色的下一步医疗操作（第一人称，不带主语）。\n"
    "- 第一条 /do：描述患者当前体征变化、伤情进展、设备读数等客观信息。"
    "**绝对不能**替患者做决定。\n"
    "- 第二条 /do：向患者或旁人的互动引导。\n"
    "- 严禁替他人写主观心理。\n"
    "- 节点文本应自然衔接患者的反应，推进医疗处置进程。\n"
    "- 如果用户提供了「剧情倾向」，你生成的节点和路径应**自然地朝该方向引导**，"
    "但不要生硬突兀，要保持医疗RP的真实感。\n"
    "- 如果用户提供了「剧情风格」，你生成的所有文本必须**严格遵循该风格的笔触和氛围**。\n"
    "- 适当使用医学术语（GCS、SpO2、BP等），但保持可读性。\n"
    "- 预测路径应覆盖不同可能性（患者配合、恶化、意外转折等）。\n"
    "- 每条文本不超过80个字符。\n\n"
    "- 生命体征应根据对话进展合理变化（如失血→心率升高/血压下降，CPR→可能恢复等）。\n\n"
    "输出格式（必须严格遵守，只输出JSON）：\n"
    '{"node":[{"type":"me","content":"..."},{"type":"do","content":"体征/状态..."},{"type":"do","content":"互动引导..."}],'
    '"paths":[{"id":1,"label":"简短描述","content":"患者/旁人的反应"},'
    '{"id":2,"label":"简短描述","content":"患者/旁人的反应"}],'
    '"vitals":{"heart_rate":"数值","blood_pressure":"数值","spo2":"数值","gcs":"数值","consciousness":"状态","summary":"一句话总结"}}'
)

_TREE_WRAPUP_SYSTEM = (
    "你是 FiveM 医疗角色扮演对话策划助手。根据之前的对话历史，"
    "生成能够**恰当收尾当前医疗场景**的节点（恰好 1 条 /me + 1 条 /do）。\n\n"
    "规则：\n"
    "- /me（1条）：描述自己角色的医疗收尾动作（交接班、宣布伤情稳定、"
    "安排转运、宣告死亡等，视情况而定）。\n"
    "- /do（1条）：描述最终患者状态、环境变化，给场景画上自然句号。\n"
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
    """Parse AI response into structured node/paths/vitals data.

    Expected format: {"node": [...], "paths": [...], "vitals": {...}}
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

    # Parse vitals (optional)
    vitals: dict[str, str] | None = None
    raw_vitals = payload.get("vitals")
    if isinstance(raw_vitals, dict):
        vitals = {}
        for vk in ("heart_rate", "blood_pressure", "spo2", "gcs", "consciousness", "summary"):
            val = raw_vitals.get(vk)
            if val is not None:
                vitals[vk] = str(val).strip()[:60]

    result: dict[str, Any] = {"node": validated_node, "paths": validated_paths}
    if vitals:
        result["vitals"] = vitals
    return result


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
