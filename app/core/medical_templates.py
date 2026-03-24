"""Medical scenario templates for quick AI generation."""

from __future__ import annotations

from typing import Any


MEDICAL_TEMPLATES: dict[str, list[dict[str, str]]] = {
    "急救现场": [
        {
            "id": "trauma_car_accident",
            "name": "🚗 车祸创伤急救",
            "scenario": "你作为急救人员到达一起严重车祸现场，一名伤者被困在变形的车内，面部有多处割伤，右腿呈不自然角度弯曲，意识模糊",
        },
        {
            "id": "gunshot_wound",
            "name": "🔫 枪伤急救",
            "scenario": "你作为EMS到达一起枪击案现场，伤者腹部中弹，大量出血，意识逐渐模糊，旁边有群众围观",
        },
        {
            "id": "cardiac_arrest",
            "name": "💔 心脏骤停抢救",
            "scenario": "你作为急救人员赶到现场，一名中年男性倒在地上，已无呼吸和脉搏，旁边有人正在进行简单的心肺复苏",
        },
        {
            "id": "overdose",
            "name": "💊 药物过量",
            "scenario": "你作为EMS到达一间公寓，一名年轻人躺在沙发上，呼吸极浅，瞳孔缩小如针尖，旁边散落着注射器和锡纸",
        },
        {
            "id": "stabbing",
            "name": "🔪 刺伤急救",
            "scenario": "你作为急救人员到达案发现场，一名男子胸部被刺伤，伤口约3cm，持续渗血，呼吸困难，面色苍白",
        },
        {
            "id": "fall_injury",
            "name": "🏗️ 高处坠落",
            "scenario": "你作为EMS到达建筑工地，一名工人从约5米高处坠落，仰卧在地，腰部剧痛无法动弹，双下肢感觉减弱",
        },
        {
            "id": "burn_injury",
            "name": "🔥 烧伤急救",
            "scenario": "你作为急救人员到达火灾现场附近，一名伤者双臂和面部有大面积烧伤，皮肤发红起泡，疼痛剧烈不停呻吟",
        },
        {
            "id": "drowning",
            "name": "🌊 溺水急救",
            "scenario": "你作为急救人员赶到海滩，一名溺水者刚被救上岸，无意识，口鼻有泡沫状液体，腹部膨隆",
        },
        {
            "id": "motorcycle_accident",
            "name": "🏍️ 摩托车事故",
            "scenario": "你作为EMS到达事故现场，一名摩托车骑手被甩出数米远，头盔破裂，左臂明显骨折外露，路面有血迹",
        },
    ],
    "医院急诊": [
        {
            "id": "er_triage",
            "name": "🏥 急诊分诊",
            "scenario": "你作为急诊值班医生，一名患者被送到急诊室，主诉胸痛、呼吸困难，出冷汗，需要快速分诊和初步处理",
        },
        {
            "id": "er_stabilize",
            "name": "🩺 急诊稳定伤情",
            "scenario": "你作为急诊室医生，接到一名多发伤患者，右侧肋骨骨折、气胸征象，血压偏低，需要紧急稳定生命体征",
        },
        {
            "id": "er_surgery_prep",
            "name": "🔬 术前准备",
            "scenario": "你作为急诊医生，一名阑尾炎患者需要紧急手术，你需要完成术前评估、建立静脉通路、签署知情同意书",
        },
        {
            "id": "er_seizure",
            "name": "⚡ 癫痫发作处理",
            "scenario": "你作为急诊值班医生，一名患者在候诊区突发癫痫大发作，全身强直阵挛，口唇发绀，旁人惊慌失措",
        },
        {
            "id": "er_allergic_reaction",
            "name": "🫁 严重过敏反应",
            "scenario": "你作为急诊医生，一名患者因食物过敏出现严重过敏反应，嘴唇和喉部肿胀，呼吸日益困难，全身起荨麻疹",
        },
    ],
    "日常医疗": [
        {
            "id": "routine_checkup",
            "name": "📋 日常体检",
            "scenario": "你作为值班医生，对一名来访者进行常规体格检查，包括血压、心率、呼吸、瞳孔反应等基本生命体征检查",
        },
        {
            "id": "wound_dressing",
            "name": "🩹 伤口换药",
            "scenario": "你作为护理人员，为一名手臂有缝合伤口的患者进行换药，检查伤口愈合情况，更换敷料",
        },
        {
            "id": "mental_health",
            "name": "🧠 心理评估",
            "scenario": "你作为急诊值班医生，对一名情绪极度低落、有自伤倾向的患者进行安全评估和心理安抚",
        },
        {
            "id": "iv_medication",
            "name": "💉 静脉输液",
            "scenario": "你作为护理人员，为一名脱水患者建立静脉通路并进行输液治疗，同时监测生命体征变化",
        },
        {
            "id": "bone_splint",
            "name": "🦴 骨折固定",
            "scenario": "你作为急救人员，对一名前臂闭合性骨折的患者进行临时夹板固定，减轻疼痛并防止二次损伤",
        },
        {
            "id": "blood_draw",
            "name": "🩸 抽血检验",
            "scenario": "你作为护理人员，需要为一名患者进行静脉采血，用于血常规和生化检验，患者对针头有些紧张",
        },
    ],
    "特殊情况": [
        {
            "id": "doa_declaration",
            "name": "⚫ 宣告死亡",
            "scenario": "你作为急救医生，经过长时间抢救，患者始终无法恢复心跳和呼吸，需要宣告死亡并通知家属",
        },
        {
            "id": "patient_transport",
            "name": "🚑 患者转运",
            "scenario": "你作为急救人员，将一名伤情稳定的患者搬上担架、固定好送上救护车，准备转运至医院急诊",
        },
        {
            "id": "mass_casualty",
            "name": "🚨 大规模伤亡事件",
            "scenario": "你作为现场急救指挥人员到达一起爆炸案现场，多名伤者散落各处，需要快速进行检伤分类(START)并协调急救资源",
        },
        {
            "id": "patient_handoff",
            "name": "📝 患者交接",
            "scenario": "你作为EMS急救人员到达医院，需要用SBAR格式向急诊医生交接患者信息，包括现场情况、体征变化和已实施的处置",
        },
        {
            "id": "psychiatric_emergency",
            "name": "🆘 精神科急症",
            "scenario": "你作为急救人员到达现场，一名患者出现急性精神病性症状，行为激动、言语混乱，对周围人有潜在威胁",
        },
        {
            "id": "child_emergency",
            "name": "👶 儿科急救",
            "scenario": "你作为急救人员到达一户家中，一名3岁儿童高热惊厥，家长极度恐慌，需要快速评估和处理",
        },
    ],
}


def get_medical_templates() -> dict[str, list[dict[str, str]]]:
    """Return the categorized medical scenario templates."""
    return MEDICAL_TEMPLATES


def get_template_by_id(template_id: str) -> dict[str, str] | None:
    """Find a specific template by its ID."""
    for templates in MEDICAL_TEMPLATES.values():
        for tmpl in templates:
            if tmpl["id"] == template_id:
                return tmpl
    return None
