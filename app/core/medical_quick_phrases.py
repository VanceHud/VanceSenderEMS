"""Medical quick action phrases for one-click sending during RP."""

from __future__ import annotations

from typing import Any


# Each phrase has: id, name (label for button), texts (list of /me and /do items)
MEDICAL_QUICK_PHRASES: list[dict[str, Any]] = [
    # ── Assessment ───────────────────────────────────────────────────
    {
        "id": "check_pulse",
        "name": "🩺 检查脉搏",
        "category": "评估",
        "texts": [
            {"type": "me", "content": "伸出两指按住对方颈动脉处，静默数秒感受脉搏跳动"},
            {"type": "do", "content": "指尖下可以感受到脉搏的跳动节律"},
        ],
    },
    {
        "id": "check_pupil",
        "name": "👁️ 查看瞳孔",
        "category": "评估",
        "texts": [
            {"type": "me", "content": "从腰间取出手电筒，轻轻翻开对方眼皮，用光照射瞳孔观察反应"},
            {"type": "do", "content": "光束照入后，瞳孔出现收缩反应"},
        ],
    },
    {
        "id": "check_breathing",
        "name": "🫁 听诊呼吸",
        "category": "评估",
        "texts": [
            {"type": "me", "content": "将听诊器置于对方胸壁，仔细听诊双侧呼吸音"},
            {"type": "do", "content": "听诊器中传来呼吸音，双侧对称"},
        ],
    },
    {
        "id": "check_consciousness",
        "name": "🔦 检查意识",
        "category": "评估",
        "texts": [
            {"type": "me", "content": "凑近对方耳边大声呼唤，同时以指节按压其胸骨处观察反应"},
            {"type": "do", "content": "对方对呼唤和疼痛刺激有/无明显反应"},
        ],
    },
    {
        "id": "check_bp",
        "name": "💉 测量血压",
        "category": "评估",
        "texts": [
            {"type": "me", "content": "取出血压计，将袖带缠绕在对方上臂加压，听诊肱动脉搏动"},
            {"type": "do", "content": "血压计指针显示测量结果"},
        ],
    },
    {
        "id": "attach_monitor",
        "name": "📊 连接监护仪",
        "category": "评估",
        "texts": [
            {"type": "me", "content": "迅速在对方胸部贴上心电监护电极片，将血氧探头夹在手指上"},
            {"type": "do", "content": "监护仪屏幕亮起，开始显示心电波形和数值"},
        ],
    },
    # ── Treatment ────────────────────────────────────────────────────
    {
        "id": "pressure_stop_bleeding",
        "name": "🩹 按压止血",
        "category": "治疗",
        "texts": [
            {"type": "me", "content": "迅速戴上手套，取出无菌纱布紧紧按压在伤口处进行直接加压止血"},
            {"type": "do", "content": "纱布逐渐被血液浸透，但出血速度有所减缓"},
        ],
    },
    {
        "id": "apply_tourniquet",
        "name": "🔧 止血带",
        "category": "治疗",
        "texts": [
            {"type": "me", "content": "从急救包中取出止血带，在伤口近心端2-3指处缠紧，旋转绞棒至出血停止"},
            {"type": "do", "content": "止血带收紧后远端出血明显减少，记录上带时间"},
        ],
    },
    {
        "id": "open_airway",
        "name": "💨 开放气道",
        "category": "治疗",
        "texts": [
            {"type": "me", "content": "一手按住对方前额，另一手托起下颌，施行仰头抬颏法开放气道"},
            {"type": "do", "content": "气道开放后，可以听到空气进出的声音"},
        ],
    },
    {
        "id": "bag_mask_ventilation",
        "name": "🎛️ 球囊面罩通气",
        "category": "治疗",
        "texts": [
            {"type": "me", "content": "将面罩紧密扣住口鼻，一手C-E手法固定面罩，另一手挤压球囊进行辅助通气"},
            {"type": "do", "content": "每次挤压球囊后可以看到胸廓随之起伏"},
        ],
    },
    {
        "id": "establish_iv",
        "name": "💉 建立IV通路",
        "category": "治疗",
        "texts": [
            {"type": "me", "content": "扎上止血带选择合适静脉，消毒后以18G留置针穿刺，见回血后松止血带，固定导管连接输液管路"},
            {"type": "do", "content": "留置针穿刺成功，生理盐水开始滴注，滴速通畅"},
        ],
    },
    {
        "id": "administer_epi",
        "name": "💊 注射肾上腺素",
        "category": "治疗",
        "texts": [
            {"type": "me", "content": "从药箱取出肾上腺素1mg，抽入注射器通过IV通路缓慢推注"},
            {"type": "do", "content": "肾上腺素注射完毕，继续监测心律变化"},
        ],
    },
    {
        "id": "apply_splint",
        "name": "🦴 夹板固定",
        "category": "治疗",
        "texts": [
            {"type": "me", "content": "取出夹板，分别固定骨折部位的上下关节，用绷带牢牢缠绕固定，检查末梢循环"},
            {"type": "do", "content": "夹板固定到位，远端指端仍可触及脉搏，感觉存在"},
        ],
    },
    {
        "id": "apply_cervical_collar",
        "name": "🔒 颈托固定",
        "category": "治疗",
        "texts": [
            {"type": "me", "content": "一手维持颈椎中立位，另一手将颈托从侧面滑入，扣紧固定带进行颈椎制动"},
            {"type": "do", "content": "颈托固定完毕，头颈部活动受限，脊柱制动到位"},
        ],
    },
    # ── Communication ────────────────────────────────────────────────
    {
        "id": "comfort_patient",
        "name": "🤝 安抚患者",
        "category": "沟通",
        "texts": [
            {"type": "me", "content": "蹲下身来平视对方的眼睛，用平稳的语气说道：\"你现在安全了，我是急救人员，我会照顾你的\""},
        ],
    },
    {
        "id": "radio_dispatch",
        "name": "📻 呼叫指挥中心",
        "category": "沟通",
        "texts": [
            {"type": "me", "content": "按下肩麦通话键：\"指挥中心，这里是EMS，到达现场，报告情况\""},
        ],
    },
    {
        "id": "radio_backup",
        "name": "🚨 请求增援",
        "category": "沟通",
        "texts": [
            {"type": "me", "content": "按下肩麦通话键：\"指挥中心，现场情况严重，请求增派一组急救力量支援\""},
        ],
    },
    {
        "id": "record_vitals",
        "name": "📋 记录体征",
        "category": "沟通",
        "texts": [
            {"type": "me", "content": "取出急救记录板，将当前生命体征数值逐项记录在患者护理报告上"},
        ],
    },
    # ── Equipment ────────────────────────────────────────────────────
    {
        "id": "prepare_stretcher",
        "name": "🛏️ 准备担架",
        "category": "设备",
        "texts": [
            {"type": "me", "content": "从救护车后方拉出自动担架，展开并调整高度，锁定支撑腿，推至患者身旁"},
            {"type": "do", "content": "银色自动担架展开到位，四点固定带已准备就绪"},
        ],
    },
    {
        "id": "power_on_aed",
        "name": "⚡ 启动AED",
        "category": "设备",
        "texts": [
            {"type": "me", "content": "打开AED电源，撕开电极贴片包装，将两片电极分别贴在右锁骨下方和左腋下"},
            {"type": "do", "content": "AED语音提示：\"正在分析心律，请勿接触患者\""},
        ],
    },
    {
        "id": "use_suction",
        "name": "🔧 吸引器清理",
        "category": "设备",
        "texts": [
            {"type": "me", "content": "打开便携式吸引器，将吸引管伸入口腔，清除气道内的分泌物和异物"},
            {"type": "do", "content": "吸引器发出工作声响，管内可见被吸出的液体"},
        ],
    },
]


def get_quick_phrases() -> list[dict[str, Any]]:
    """Return all quick phrases."""
    return MEDICAL_QUICK_PHRASES


def get_phrases_by_category() -> dict[str, list[dict[str, Any]]]:
    """Return phrases grouped by category."""
    result: dict[str, list[dict[str, Any]]] = {}
    for phrase in MEDICAL_QUICK_PHRASES:
        cat = phrase.get("category", "其他")
        result.setdefault(cat, []).append(phrase)
    return result
