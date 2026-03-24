"""Medical preset combo chains — sequential preset groups for complete workflows."""

from __future__ import annotations

from typing import Any


MEDICAL_COMBOS: list[dict[str, Any]] = [
    {
        "id": "full_trauma_response",
        "name": "🚨 创伤急救全流程",
        "description": "初步检查 → 创伤包扎 → 静脉输液 → 患者转运",
        "presets": [
            "medical_initial_check",
            "medical_wound_dressing",
            "medical_iv_line",
            "medical_transport",
        ],
    },
    {
        "id": "cpr_success_flow",
        "name": "💓 CPR 成功流程",
        "description": "初步检查 → CPR 心肺复苏 → 静脉输液 → 急诊交接",
        "presets": [
            "medical_initial_check",
            "medical_cpr",
            "medical_iv_line",
            "medical_er_handoff",
        ],
    },
    {
        "id": "cpr_fail_flow",
        "name": "⚫ CPR 失败流程",
        "description": "初步检查 → CPR 心肺复苏 → 宣告死亡",
        "presets": [
            "medical_initial_check",
            "medical_cpr",
            "medical_death_declaration",
        ],
    },
    {
        "id": "routine_er_flow",
        "name": "🏥 常规急诊流程",
        "description": "初步检查 → 静脉输液 → 急诊交接",
        "presets": [
            "medical_initial_check",
            "medical_iv_line",
            "medical_er_handoff",
        ],
    },
    {
        "id": "comfort_and_transport",
        "name": "🤝 安抚转运流程",
        "description": "心理安抚 → 初步检查 → 患者转运",
        "presets": [
            "medical_comfort",
            "medical_initial_check",
            "medical_transport",
        ],
    },
    {
        "id": "wound_to_er",
        "name": "🩹 创伤到院流程",
        "description": "创伤包扎 → 静脉输液 → 患者转运 → 急诊交接",
        "presets": [
            "medical_wound_dressing",
            "medical_iv_line",
            "medical_transport",
            "medical_er_handoff",
        ],
    },
]


def get_combos() -> list[dict[str, Any]]:
    """Return all medical combos."""
    return MEDICAL_COMBOS


def get_combo_by_id(combo_id: str) -> dict[str, Any] | None:
    """Find a specific combo by ID."""
    for combo in MEDICAL_COMBOS:
        if combo["id"] == combo_id:
            return combo
    return None
