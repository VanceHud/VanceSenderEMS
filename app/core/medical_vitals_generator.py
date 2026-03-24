"""Random medical vitals generator — produces realistic, self-consistent vital signs."""

from __future__ import annotations

import random
from typing import Any


# ── Severity-based vital sign ranges ──────────────────────────────────────
# Each key maps to (min, max) for that severity level.
# Values are medically plausible and internally consistent.

_VITALS_RANGES: dict[str, dict[str, tuple[float, float]]] = {
    "mild": {
        "heart_rate": (70, 95),
        "systolic_bp": (110, 135),
        "diastolic_bp": (65, 85),
        "spo2": (96, 99),
        "respiratory_rate": (14, 20),
        "temperature": (36.4, 37.5),
        "gcs_e": (4, 4),
        "gcs_v": (5, 5),
        "gcs_m": (6, 6),
    },
    "moderate": {
        "heart_rate": (95, 120),
        "systolic_bp": (90, 115),
        "diastolic_bp": (55, 75),
        "spo2": (92, 96),
        "respiratory_rate": (20, 28),
        "temperature": (36.0, 38.5),
        "gcs_e": (3, 4),
        "gcs_v": (3, 5),
        "gcs_m": (5, 6),
    },
    "severe": {
        "heart_rate": (115, 145),
        "systolic_bp": (70, 95),
        "diastolic_bp": (40, 60),
        "spo2": (85, 93),
        "respiratory_rate": (26, 36),
        "temperature": (35.5, 39.2),
        "gcs_e": (2, 3),
        "gcs_v": (2, 4),
        "gcs_m": (3, 5),
    },
    "critical": {
        "heart_rate": (130, 180),
        "systolic_bp": (50, 80),
        "diastolic_bp": (25, 50),
        "spo2": (60, 88),
        "respiratory_rate": (6, 40),
        "temperature": (34.5, 40.0),
        "gcs_e": (1, 2),
        "gcs_v": (1, 3),
        "gcs_m": (1, 4),
    },
}

_CONSCIOUSNESS_MAP = {
    (15, 15): "清醒，定向力完整",
    (13, 14): "轻度意识模糊，可被唤醒",
    (9, 12): "嗜睡，对疼痛有反应",
    (6, 8): "浅昏迷，仅对强刺激有反应",
    (3, 5): "深昏迷，无自主反应",
}

_PUPIL_OPTIONS = {
    "mild": ["双侧瞳孔等大等圆约3mm，对光反射灵敏", "双侧瞳孔3mm，光反射正常"],
    "moderate": ["双侧瞳孔约3.5mm，对光反射略迟钝", "瞳孔等大约4mm，光反射减弱"],
    "severe": ["双侧瞳孔约4mm，对光反射迟钝", "右侧瞳孔4.5mm、左侧3.5mm，光反射迟钝"],
    "critical": ["双侧瞳孔散大约5mm，对光反射消失", "瞳孔散大固定约6mm，无对光反射"],
}

_SKIN_OPTIONS = {
    "mild": ["肤色正常，四肢温暖，CRT<2秒", "皮肤干燥温暖，毛细血管充盈正常"],
    "moderate": ["面色略苍白，皮肤微湿冷", "四肢末梢略凉，CRT约3秒"],
    "severe": ["面色苍白，皮肤湿冷，出冷汗", "全身大汗淋漓，四肢冰凉，CRT>4秒"],
    "critical": ["面色灰白/发绀，皮肤花斑样改变", "口唇紫绀，全身湿冷，末梢循环极差"],
}

_SEVERITY_LABELS = {
    "mild": "轻伤",
    "moderate": "中等",
    "severe": "重伤",
    "critical": "危重",
}


def _rand_int(lo: float, hi: float) -> int:
    return random.randint(int(lo), int(hi))


def _rand_float(lo: float, hi: float, decimals: int = 1) -> float:
    return round(random.uniform(lo, hi), decimals)


def generate_random_vitals(severity: str = "moderate") -> dict[str, Any]:
    """Generate a medically consistent set of vital signs.

    Args:
        severity: One of 'mild', 'moderate', 'severe', 'critical'.

    Returns:
        Dictionary with vital signs, GCS breakdown, descriptions, and /do texts.
    """
    if severity not in _VITALS_RANGES:
        severity = "moderate"

    r = _VITALS_RANGES[severity]

    hr = _rand_int(*r["heart_rate"])
    sys_bp = _rand_int(*r["systolic_bp"])
    dia_bp = _rand_int(*r["diastolic_bp"])
    spo2 = _rand_int(*r["spo2"])
    rr = _rand_int(*r["respiratory_rate"])
    temp = _rand_float(*r["temperature"])

    gcs_e = _rand_int(*r["gcs_e"])
    gcs_v = _rand_int(*r["gcs_v"])
    gcs_m = _rand_int(*r["gcs_m"])
    gcs_total = gcs_e + gcs_v + gcs_m

    # Determine consciousness description
    consciousness = "意识状态不明"
    for (lo, hi), desc in _CONSCIOUSNESS_MAP.items():
        if lo <= gcs_total <= hi:
            consciousness = desc
            break

    pupil = random.choice(_PUPIL_OPTIONS[severity])
    skin = random.choice(_SKIN_OPTIONS[severity])

    # HR description
    if hr < 60:
        hr_desc = "心动过缓"
    elif hr <= 100:
        hr_desc = "正常范围"
    elif hr <= 120:
        hr_desc = "轻度心动过速"
    else:
        hr_desc = "心动过速"

    # BP description
    if sys_bp < 90:
        bp_desc = "低血压（休克征象）"
    elif sys_bp <= 140:
        bp_desc = "正常范围"
    else:
        bp_desc = "高血压"

    # SpO2 description
    if spo2 >= 95:
        spo2_desc = "正常"
    elif spo2 >= 90:
        spo2_desc = "偏低"
    else:
        spo2_desc = "严重低氧"

    # Build vitals object
    vitals = {
        "severity": severity,
        "severity_label": _SEVERITY_LABELS[severity],
        "heart_rate": f"{hr} bpm（{hr_desc}）",
        "blood_pressure": f"{sys_bp}/{dia_bp} mmHg（{bp_desc}）",
        "spo2": f"{spo2}%（{spo2_desc}）",
        "respiratory_rate": f"{rr} 次/分",
        "temperature": f"{temp}°C",
        "gcs": f"E{gcs_e}V{gcs_v}M{gcs_m} = {gcs_total} 分",
        "consciousness": consciousness,
        "pupil": pupil,
        "skin": skin,
    }

    # Generate /do texts
    do_texts = [
        {
            "type": "do",
            "content": f"心电监护仪显示：心率 {hr}bpm，血压 {sys_bp}/{dia_bp}mmHg",
        },
        {
            "type": "do",
            "content": f"血氧探头读数 SpO2 {spo2}%，呼吸频率 {rr}次/分",
        },
        {
            "type": "do",
            "content": f"GCS评分 E{gcs_e}V{gcs_v}M{gcs_m}={gcs_total}分，{consciousness}",
        },
        {
            "type": "do",
            "content": pupil,
        },
        {
            "type": "do",
            "content": skin,
        },
    ]

    # Severity-based summary
    if severity == "mild":
        summary = "生命体征基本稳定，暂无生命危险"
    elif severity == "moderate":
        summary = "生命体征不稳定，需要积极干预和持续监测"
    elif severity == "severe":
        summary = "生命体征严重异常，需要紧急处置"
    else:
        summary = "生命体征极度不稳定，随时可能心脏骤停"

    vitals["summary"] = summary
    vitals["do_texts"] = do_texts

    return vitals
