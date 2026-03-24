"""Medical-specific API routes — templates, glossary, vitals, quick phrases, combos, SBAR."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.core.medical_templates import get_medical_templates, get_template_by_id
from app.core.medical_glossary import get_glossary, get_glossary_categories
from app.core.medical_vitals_generator import generate_random_vitals
from app.core.medical_quick_phrases import get_quick_phrases, get_phrases_by_category
from app.core.medical_combos import get_combos, get_combo_by_id

router = APIRouter()


# ── Templates ──────────────────────────────────────────────────────────────

@router.get("/templates")
async def list_medical_templates():
    """返回分类的医疗场景模板列表。"""
    return {"templates": get_medical_templates()}


@router.get("/templates/{template_id}")
async def get_medical_template(template_id: str):
    """根据ID获取单个医疗场景模板。"""
    tmpl = get_template_by_id(template_id)
    if tmpl is None:
        raise HTTPException(status_code=404, detail="模板不存在")
    return tmpl


# ── Glossary ───────────────────────────────────────────────────────────────

@router.get("/glossary")
async def list_glossary(q: str | None = None, category: str | None = None):
    """医疗术语速查，支持搜索和分类过滤。"""
    items = get_glossary(query=q, category=category)
    return {"items": items, "total": len(items)}


@router.get("/glossary/categories")
async def list_glossary_categories():
    """返回术语表所有分类。"""
    return {"categories": get_glossary_categories()}


# ── Random Vitals Generator ───────────────────────────────────────────────

@router.get("/random-vitals")
async def random_vitals(severity: str = Query("moderate", regex="^(mild|moderate|severe|critical)$")):
    """根据伤情程度随机生成一组医学上合理的生命体征和/do文本。"""
    return generate_random_vitals(severity)


# ── Quick Phrases ──────────────────────────────────────────────────────────

@router.get("/quick-phrases")
async def list_quick_phrases():
    """返回所有医疗快捷短语，按分类分组。"""
    return {"phrases": get_phrases_by_category()}


# ── Preset Combos ──────────────────────────────────────────────────────────

@router.get("/combos")
async def list_combos():
    """返回所有医疗预设连招组合。"""
    return {"combos": get_combos()}


@router.get("/combos/{combo_id}")
async def get_combo(combo_id: str):
    """根据ID获取单个连招组合。"""
    combo = get_combo_by_id(combo_id)
    if combo is None:
        raise HTTPException(status_code=404, detail="连招不存在")
    return combo


# ── SBAR Report Generator ─────────────────────────────────────────────────

class SBARRequest(BaseModel):
    """SBAR report generation request."""
    situation: str        # 患者情况: 性别/年龄/主诉
    background: str       # 背景: 现场/既往史
    assessment: str       # 评估: 当前体征/伤情
    recommendation: str   # 建议: 已处置/建议下一步


@router.post("/sbar")
async def generate_sbar(req: SBARRequest):
    """根据SBAR四要素生成交接报告/me+/do文本。"""
    texts = [
        {"type": "me", "content": f"手持患者护理报告板，面向急诊医生简明报告：\"S-情况：{req.situation}\""},
        {"type": "me", "content": f"\"B-背景：{req.background}\""},
        {"type": "do", "content": f"急救人员提供的评估信息：A-评估：{req.assessment}"},
        {"type": "me", "content": f"\"R-建议：{req.recommendation}\""},
        {"type": "me", "content": "将患者护理报告递交给急诊医生，完成正式交接"},
        {"type": "do", "content": "患者护理权正式移交给院内医疗团队"},
    ]
    return {
        "texts": texts,
        "sbar_summary": {
            "S": req.situation,
            "B": req.background,
            "A": req.assessment,
            "R": req.recommendation,
        },
    }
