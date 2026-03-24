"""Medical terminology glossary for EMS/medical RP quick reference."""

from __future__ import annotations


MEDICAL_GLOSSARY: list[dict[str, str]] = [
    # ── 体征与评估 ──
    {"term": "GCS", "full": "Glasgow Coma Scale", "cn": "格拉斯哥昏迷量表", "desc": "E(睁眼)1-4 + V(语言)1-5 + M(运动)1-6 = 3~15，≤8分为重度昏迷", "category": "评估"},
    {"term": "SpO2", "full": "Blood Oxygen Saturation", "cn": "血氧饱和度", "desc": "正常95-100%，<90%为严重低氧", "category": "体征"},
    {"term": "BP", "full": "Blood Pressure", "cn": "血压", "desc": "正常约120/80mmHg，收缩压<90为休克征象", "category": "体征"},
    {"term": "HR", "full": "Heart Rate", "cn": "心率", "desc": "正常60-100bpm，>100为心动过速，<60为心动过缓", "category": "体征"},
    {"term": "RR", "full": "Respiratory Rate", "cn": "呼吸频率", "desc": "正常12-20次/分，>24为呼吸急促", "category": "体征"},
    {"term": "BT", "full": "Body Temperature", "cn": "体温", "desc": "正常36.1-37.2°C，>38°C为发热", "category": "体征"},
    {"term": "AVPU", "full": "Alert, Voice, Pain, Unresponsive", "cn": "意识水平快速评估", "desc": "A=清醒 V=对声音有反应 P=对疼痛有反应 U=无反应", "category": "评估"},
    {"term": "SAMPLE", "full": "Signs/Allergies/Medications/Past/Last meal/Events", "cn": "病史采集口诀", "desc": "症状/过敏/用药/既往史/末次进食/事件经过", "category": "评估"},
    {"term": "OPQRST", "full": "Onset/Provoke/Quality/Radiate/Severity/Time", "cn": "疼痛评估口诀", "desc": "发作/诱因/性质/放射/严重度/时间", "category": "评估"},
    {"term": "ABCDE", "full": "Airway/Breathing/Circulation/Disability/Exposure", "cn": "初步评估法", "desc": "气道/呼吸/循环/神经功能/暴露全身检查", "category": "评估"},

    # ── 急救操作 ──
    {"term": "CPR", "full": "Cardiopulmonary Resuscitation", "cn": "心肺复苏", "desc": "30次胸外按压:2次人工通气，按压深度5-6cm，速率100-120次/分", "category": "急救"},
    {"term": "AED", "full": "Automated External Defibrillator", "cn": "自动体外除颤器", "desc": "分析心律并自动建议是否电击，用于室颤/无脉室速", "category": "急救"},
    {"term": "BLS", "full": "Basic Life Support", "cn": "基础生命支持", "desc": "包括CPR、AED使用、气道管理等基本急救技能", "category": "急救"},
    {"term": "ALS", "full": "Advanced Life Support", "cn": "高级生命支持", "desc": "包括药物治疗、高级气道管理、心电监护等进阶急救", "category": "急救"},
    {"term": "止血带", "full": "Tourniquet (CAT/SOF-T)", "cn": "止血带", "desc": "用于四肢严重出血的紧急止血，记录绑扎时间", "category": "急救"},
    {"term": "海姆立克", "full": "Heimlich Maneuver", "cn": "腹部冲击法", "desc": "站在患者背后，双手环抱腹部向上猛推，解除气道异物梗阻", "category": "急救"},
    {"term": "START", "full": "Simple Triage And Rapid Treatment", "cn": "简易检伤分类", "desc": "大规模伤亡事件中的快速分类：红(即刻)、黄(延迟)、绿(轻伤)、黑(死亡)", "category": "急救"},

    # ── 治疗与药物 ──
    {"term": "IV", "full": "Intravenous", "cn": "静脉注射/输液", "desc": "通过外周或中心静脉给药/补液", "category": "治疗"},
    {"term": "IM", "full": "Intramuscular", "cn": "肌肉注射", "desc": "将药物注入肌肉组织，常用部位：三角肌、臀大肌", "category": "治疗"},
    {"term": "IO", "full": "Intraosseous", "cn": "骨髓腔注射", "desc": "在静脉通路困难时通过骨髓腔给药/输液，常用部位：胫骨近端", "category": "治疗"},
    {"term": "NS", "full": "Normal Saline (0.9% NaCl)", "cn": "生理盐水", "desc": "最常用的静脉输液，用于补液和维持血容量", "category": "治疗"},
    {"term": "RL", "full": "Ringer's Lactate", "cn": "乳酸林格液", "desc": "含电解质的晶体液，用于失血性休克的液体复苏", "category": "治疗"},
    {"term": "肾上腺素", "full": "Epinephrine/Adrenaline", "cn": "肾上腺素", "desc": "心脏骤停首选药物，1mg IV/IO q3-5min；严重过敏0.3-0.5mg IM", "category": "治疗"},
    {"term": "纳洛酮", "full": "Naloxone/Narcan", "cn": "纳洛酮", "desc": "阿片类药物过量的特效拮抗剂，0.4-2mg IV/IM/IN", "category": "治疗"},
    {"term": "阿托品", "full": "Atropine", "cn": "阿托品", "desc": "治疗有症状的心动过缓，0.5mg IV q3-5min，最大3mg", "category": "治疗"},
    {"term": "胺碘酮", "full": "Amiodarone", "cn": "胺碘酮", "desc": "治疗难治性室颤/无脉室速，首剂300mg IV推注", "category": "治疗"},
    {"term": "地西泮", "full": "Diazepam/Valium", "cn": "地西泮(安定)", "desc": "抗惊厥/镇静，癫痫持续状态5-10mg IV缓推", "category": "治疗"},
    {"term": "吗啡", "full": "Morphine", "cn": "吗啡", "desc": "强效镇痛剂，2-4mg IV缓推，注意呼吸抑制", "category": "治疗"},

    # ── 设备与工具 ──
    {"term": "ET管", "full": "Endotracheal Tube", "cn": "气管插管", "desc": "经口/鼻插入气管确保气道通畅，成人内径7.0-8.0mm", "category": "设备"},
    {"term": "喉镜", "full": "Laryngoscope", "cn": "喉镜", "desc": "用于气管插管时暴露声门的器械，有弯叶(Mac)和直叶(Miller)", "category": "设备"},
    {"term": "BVM", "full": "Bag-Valve-Mask", "cn": "球囊面罩(简易呼吸器)", "desc": "手动正压通气设备，连接氧气可提供高浓度氧", "category": "设备"},
    {"term": "NPA", "full": "Nasopharyngeal Airway", "cn": "鼻咽通气管", "desc": "经鼻插入的软管维持气道，适用于有咬合反射的患者", "category": "设备"},
    {"term": "OPA", "full": "Oropharyngeal Airway", "cn": "口咽通气管", "desc": "防止舌后坠阻塞气道，仅用于无咬合反射的患者", "category": "设备"},
    {"term": "监护仪", "full": "Cardiac Monitor", "cn": "心电监护仪", "desc": "持续监测心电图、心率、血压、血氧等生命体征", "category": "设备"},
    {"term": "除颤仪", "full": "Manual Defibrillator", "cn": "手动除颤仪", "desc": "医疗级除颤设备，可手动分析心律和选择能量电击", "category": "设备"},
    {"term": "颈托", "full": "Cervical Collar (C-collar)", "cn": "颈椎固定器", "desc": "固定颈椎防止二次损伤，外伤患者常规使用", "category": "设备"},
    {"term": "脊柱板", "full": "Spine Board/Backboard", "cn": "脊柱固定板", "desc": "疑似脊柱损伤时全脊柱固定和搬运用硬板", "category": "设备"},
    {"term": "夹板", "full": "Splint", "cn": "骨折固定夹板", "desc": "临时固定骨折肢体防止移位，有充气式和硬质两种", "category": "设备"},
    {"term": "鼻导管", "full": "Nasal Cannula", "cn": "鼻导管", "desc": "低流量给氧装置,1-6L/min可提供24-44%浓度氧", "category": "设备"},
    {"term": "面罩", "full": "Non-Rebreather Mask", "cn": "非重复呼吸面罩", "desc": "高流量给氧装置,10-15L/min可提供60-90%浓度氧", "category": "设备"},

    # ── 诊断与状态 ──
    {"term": "室颤", "full": "Ventricular Fibrillation (VF/Vfib)", "cn": "心室颤动", "desc": "心室肌肉不协调颤动，需立即除颤的致命心律", "category": "诊断"},
    {"term": "无脉室速", "full": "Pulseless VT", "cn": "无脉搏室性心动过速", "desc": "虽有心电活动但无有效心输出，需除颤", "category": "诊断"},
    {"term": "PEA", "full": "Pulseless Electrical Activity", "cn": "无脉搏电活动", "desc": "有心电图活动但无脉搏,不可除颤,需找可逆原因(5H5T)", "category": "诊断"},
    {"term": "心搏停止", "full": "Asystole", "cn": "心搏停止", "desc": "心电图呈直线,无任何心电活动,不可除颤", "category": "诊断"},
    {"term": "气胸", "full": "Pneumothorax", "cn": "气胸", "desc": "空气进入胸膜腔导致肺塌陷，张力性气胸需紧急穿刺减压", "category": "诊断"},
    {"term": "休克", "full": "Shock", "cn": "休克", "desc": "组织灌注不足的危急状态,分低血容量/心源性/分布性等", "category": "诊断"},
    {"term": "DOA", "full": "Dead on Arrival", "cn": "到达时已死亡", "desc": "急救人员到达时患者已无生命体征", "category": "诊断"},
    {"term": "ROSC", "full": "Return of Spontaneous Circulation", "cn": "自主循环恢复", "desc": "心脏骤停患者恢复可触及的脉搏和血压", "category": "诊断"},

    # ── 沟通与流程 ──
    {"term": "SBAR", "full": "Situation/Background/Assessment/Recommendation", "cn": "标准交接格式", "desc": "S-现况 B-背景 A-评估 R-建议，用于患者交接", "category": "沟通"},
    {"term": "Code Blue", "full": "Code Blue", "cn": "紧急抢救代码", "desc": "医院内心脏骤停/呼吸停止的紧急呼叫代码", "category": "沟通"},
    {"term": "ETA", "full": "Estimated Time of Arrival", "cn": "预计到达时间", "desc": "急救车到达目的地的预估时间", "category": "沟通"},
    {"term": "MCI", "full": "Mass Casualty Incident", "cn": "大规模伤亡事件", "desc": "伤亡人数超出当地急救资源处置能力的事件", "category": "沟通"},
    {"term": "PCR", "full": "Patient Care Report", "cn": "患者护理报告", "desc": "记录急救过程中所有评估、处置和患者状态的正式文档", "category": "沟通"},
    {"term": "DNR", "full": "Do Not Resuscitate", "cn": "不予复苏", "desc": "患者或家属签署的放弃心肺复苏的医疗文书", "category": "沟通"},

    # ── 解剖位置 ──
    {"term": "颈动脉", "full": "Carotid Artery", "cn": "颈动脉", "desc": "颈部大动脉，成人心脏骤停时首选脉搏检查点", "category": "解剖"},
    {"term": "桡动脉", "full": "Radial Artery", "cn": "桡动脉", "desc": "手腕拇指侧动脉，日常脉搏检查最常用位置", "category": "解剖"},
    {"term": "肘正中静脉", "full": "Median Cubital Vein", "cn": "肘正中静脉", "desc": "肘窝处大静脉,静脉穿刺/抽血最常用部位", "category": "解剖"},
    {"term": "胸骨", "full": "Sternum", "cn": "胸骨", "desc": "胸前正中骨骼，CPR按压点在胸骨下半段", "category": "解剖"},
    {"term": "环甲膜", "full": "Cricothyroid Membrane", "cn": "环甲膜", "desc": "喉部前方薄膜，紧急气道时环甲膜切开术的位置", "category": "解剖"},

    # ── 无线电代码 ──
    {"term": "10-4", "full": "Acknowledgement", "cn": "收到/明白", "desc": "确认收到信息 → /me 按下对讲机: \"10-4，收到\"", "category": "无线电"},
    {"term": "10-7", "full": "Out of Service", "cn": "退出服务", "desc": "暂时离开岗位 → /me 按下对讲机: \"10-7，暂时退出\"", "category": "无线电"},
    {"term": "10-8", "full": "In Service", "cn": "恢复服务", "desc": "回到可出勤状态 → /me 按下对讲机: \"10-8，恢复服务\"", "category": "无线电"},
    {"term": "10-17", "full": "En Route", "cn": "途中赶往", "desc": "正在前往目的地 → /me 按下对讲机: \"10-17，正在途中\"", "category": "无线电"},
    {"term": "10-20", "full": "Location", "cn": "当前位置", "desc": "报告或询问位置 → /me 按下对讲机: \"我的10-20在...\"", "category": "无线电"},
    {"term": "10-23", "full": "Stand By", "cn": "待命/稍候", "desc": "原地等候进一步指示 → /me 按下对讲机: \"10-23，原地待命\"", "category": "无线电"},
    {"term": "10-76", "full": "En Route to Scene", "cn": "出发前往现场", "desc": "出动前往事故现场 → /me 按下对讲机: \"10-76，出发前往现场\"", "category": "无线电"},
    {"term": "10-97", "full": "Arrived on Scene", "cn": "到达现场", "desc": "已到达事故地点 → /me 按下对讲机: \"10-97，已到达现场\"", "category": "无线电"},
    {"term": "10-98", "full": "Available/Assignment Complete", "cn": "任务完成/可用", "desc": "当前任务完成 → /me 按下对讲机: \"10-98，任务完成，可供调遣\"", "category": "无线电"},
    {"term": "Code 1", "full": "Non-Emergency Response", "cn": "非紧急出车", "desc": "不开警灯警笛，正常行驶 → /me 正常驾驶出发前往目的地", "category": "无线电"},
    {"term": "Code 3", "full": "Emergency Response", "cn": "紧急出车(鸣笛)", "desc": "开启警灯警笛紧急出动 → /me 启动警灯和警笛, 紧急出车前往现场", "category": "无线电"},
    {"term": "Code 4", "full": "No Further Assistance Needed", "cn": "无需增援", "desc": "现场已控制 → /me 按下对讲机: \"Code 4，现场无需增援\"", "category": "无线电"},
    {"term": "Code Blue", "full": "Cardiac Arrest", "cn": "心脏骤停代码", "desc": "院内紧急代码 → /me 大声呼叫: \"Code Blue! Code Blue!\"", "category": "无线电"},
    {"term": "Signal 7", "full": "Deceased Person", "cn": "死亡代码", "desc": "现场有死亡人员 → /me 按下对讲机: \"报告Signal 7\"", "category": "无线电"},
    {"term": "EMS-1", "full": "Emergency Medical Unit", "cn": "急救单位编号", "desc": "呼号示例 → /me 按下对讲机: \"EMS-1 收到，出发\"", "category": "无线电"},
]


def get_glossary(query: str | None = None, category: str | None = None) -> list[dict[str, str]]:
    """Return glossary items, optionally filtered by search query and/or category."""
    results = MEDICAL_GLOSSARY

    if category:
        cat_lower = category.strip().lower()
        results = [g for g in results if g["category"].lower() == cat_lower]

    if query:
        q_lower = query.strip().lower()
        results = [
            g for g in results
            if q_lower in g["term"].lower()
            or q_lower in g["full"].lower()
            or q_lower in g["cn"].lower()
            or q_lower in g["desc"].lower()
        ]

    return results


def get_glossary_categories() -> list[str]:
    """Return all unique categories in the glossary."""
    seen: set[str] = set()
    cats: list[str] = []
    for g in MEDICAL_GLOSSARY:
        c = g["category"]
        if c not in seen:
            seen.add(c)
            cats.append(c)
    return cats
