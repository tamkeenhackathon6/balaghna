from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

from app.services.ollama_service import OllamaUnavailable, analyze_with_ollama

OFFICIAL_DEPARTMENTS = {
    "مديرية الخدمات المحلية": 1,
    "مديريات المجالس المحلية والإدارة المحلية": 2,
    "مديرية التخطيط والتنمية المحلية": 3,
    "مديرية التنظيم والتخطيط العمراني": 4,
    "مديرية الشؤون الفنية": 5,
    "مديرية الشؤون المالية": 6,
    "مديرية الرقابة والتفتيش": 7,
    "المحافظات": 8,
    "مجالس المدن والبلديات والوحدات الإدارية": 9,
}

CATEGORY_IDS = {
    "نفايات ونظافة": 1,
    "حدائق": 2,
    "أرصفة": 3,
    "إنارة": 4,
    "حفر وطرق محلية": 5,
    "خدمات يومية": 6,
    "شكوى على وحدة إدارية": 7,
    "احتياجات منطقة": 9,
    "تنظيم عمراني": 11,
    "مخالفة بناء": 12,
    "مشروع خدمي": 15,
    "بنية تحتية": 16,
    "موازنة محلية": 18,
    "مخالفة إدارية": 21,
    "مشكلة على مستوى المحافظة": 24,
    "مشكلة بلدية محلية": 25,
    "أخرى": 26,
}

RULES = [
    ("المحافظات", "مشكلة على مستوى المحافظة", ("عدة بلديات", "اكثر من بلدية", "على مستوى المحافظة", "عدة مناطق", "تنسيق بين الجهات", "مشكلة عامة بالمحافظة"), "تم اختيار المحافظات لأن البلاغ يتطلب تنسيقاً بين أكثر من جهة أو على مستوى المحافظة."),
    ("مديرية الشؤون المالية", "موازنة محلية", ("موازنة", "ميزانية", "ايرادات", "نفقات", "رسوم", "رسم محلي", "موارد", "صرف مالي", "تمويل", "تكلفة", "جباية"), "تم اختيار مديرية الشؤون المالية لأن البلاغ متعلق بموضوع مالي محلي."),
    ("مديرية التنظيم والتخطيط العمراني", "مخالفة بناء", ("مخالفة بناء", "بناء مخالف", "ترخيص بناء", "تنظيم", "مخطط تنظيمي", "استعمال ارض", "استعمالات الاراضي", "تغيير صفة", "تعدي بناء", "اشغال عقار", "تقسيم ارض"), "تم اختيار مديرية التنظيم والتخطيط العمراني لأن البلاغ متعلق بالبناء أو التنظيم أو استعمالات الأراضي."),
    ("مديرية الرقابة والتفتيش", "مخالفة إدارية", ("مخالفة ادارية", "فساد اداري", "تقصير موظف", "تقصير", "مخالفة", "موظف", "اهمال", "تجاوزات", "شكوى على موظف", "شكوى رقابية", "عدم تنفيذ", "مخالفة جهة", "استغلال", "محاباة"), "تم اختيار مديرية الرقابة والتفتيش لأن البلاغ يركز على مخالفة أو تقصير إداري."),
    ("مديريات المجالس المحلية والإدارة المحلية", "شكوى على وحدة إدارية", ("وحدة ادارية", "بلدية لا تستجيب", "مجلس محلي", "تاخر البلدية", "تقصير الوحدة الادارية", "شكوى على البلدية", "اداء البلدية", "اداء المجلس", "ادارة محلية", "ما عم ترد"), "تم اختيار مديريات المجالس المحلية والإدارة المحلية لأن البلاغ يتعلق بأداء أو متابعة الجهة الإدارية المحلية."),
    ("مديرية التخطيط والتنمية المحلية", "احتياجات منطقة", ("احتياجات المنطقة", "المنطقة بحاجة", "مشروع جديد", "اولوية المشروع", "ترتيب الاولويات", "تنمية المنطقة", "خطة تنمية", "احتياج خدمي", "نقص الخدمات", "توسعة الخدمات"), "تم اختيار مديرية التخطيط والتنمية المحلية لأن البلاغ يصف احتياجاً تنموياً أو أولوية مشروع."),
    ("مديرية الشؤون الفنية", "بنية تحتية", ("بنية تحتية", "البنية التحتية", "مشروع خدمي", "مشروع صيانة", "صيانة فنية", "متابعة فنية", "تنفيذ مشروع", "شبكة خدمية", "جسر", "منشاة خدمية", "اعمال فنية", "تاهيل طريق كبير", "مجارير", "شبكة الصرف"), "تم اختيار مديرية الشؤون الفنية لأن البلاغ يتعلق ببنية تحتية أو متابعة فنية لمشروع."),
    ("مديرية الخدمات المحلية", "نفايات ونظافة", ("نفايات", "قمامة", "زبالة", "حاوية", "نظافة", "وسخ"), "تم اختيار مديرية الخدمات المحلية لأن البلاغ متعلق بخدمة محلية يومية."),
    ("مديرية الخدمات المحلية", "حدائق", ("حديقة", "حدائق", "اشجار", "مساحات خضراء"), "تم اختيار مديرية الخدمات المحلية لأن البلاغ متعلق بخدمة محلية يومية."),
    ("مديرية الخدمات المحلية", "أرصفة", ("رصيف", "ارصفة"), "تم اختيار مديرية الخدمات المحلية لأن البلاغ متعلق بخدمة محلية يومية."),
    ("مديرية الخدمات المحلية", "إنارة", ("انارة", "عمود", "مصباح", "ضو", "ضوء", "عتمة"), "تم اختيار مديرية الخدمات المحلية لأن البلاغ متعلق بخدمة محلية يومية."),
    ("مديرية الخدمات المحلية", "حفر وطرق محلية", ("حفرة", "حفر", "طريق محلي", "شارع"), "تم اختيار مديرية الخدمات المحلية لأن البلاغ متعلق بخدمة محلية يومية."),
    ("مجالس المدن والبلديات والوحدات الإدارية", "مشكلة بلدية محلية", ("مجلس المدينة", "تنفيذ محلي", "الخدمة المحلية المباشرة", "البلدية", "الحي", "حارة"), "تم اختيار مجالس المدن والبلديات والوحدات الإدارية لأن البلاغ يحتاج تنفيذاً محلياً مباشراً."),
]


def normalize_arabic(text: str) -> str:
    text = text.lower().strip()
    text = re.sub("[إأآا]", "ا", text)
    text = re.sub("[ى]", "ي", text)
    text = re.sub("ة", "ه", text)
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text)


def _matches(text: str, keywords: Iterable[str]) -> list[str]:
    return [keyword for keyword in keywords if normalize_arabic(keyword) in text]


def analyze_complaint(text: str, category: str | None = None, area: str | None = None, governorate: str | None = None) -> dict:
    try:
        ai_result = _validate_ai_result(analyze_with_ollama(text, area, governorate))
        if ai_result:
            return ai_result
    except OllamaUnavailable:
        pass
    return analyze_with_rules(text, category, area, governorate)


def analyze_with_rules(text: str, category: str | None = None, area: str | None = None, governorate: str | None = None) -> dict:
    normalized = normalize_arabic(" ".join(part for part in (text, area or "", governorate or "") if part))
    scored = []
    for precedence, (department, category_name, keywords, reason) in enumerate(RULES):
        matched = _matches(normalized, keywords)
        if matched:
            scored.append((len(matched), -precedence, department, category_name, matched, reason))

    if scored:
        _, _, department, category_name, matched_keywords, reason = max(scored)
        confidence = min(0.95, round(0.62 + len(matched_keywords) * 0.09, 2))
    else:
        department = "مجالس المدن والبلديات والوحدات الإدارية"
        category_name = "أخرى"
        matched_keywords = []
        reason = "تم اختيار مجالس المدن والبلديات والوحدات الإدارية كجهة تنفيذ محلية للبلاغ غير المصنف."
        confidence = 0.4

    return {
        "category": category_name,
        "category_id": CATEGORY_IDS[category_name],
        "department": department,
        "department_id": OFFICIAL_DEPARTMENTS[department],
        "priority": _priority(normalized),
        "confidence": confidence,
        "matched_keywords": matched_keywords,
        "routing_reason": reason,
        "source": "rule_based",
    }


def _validate_ai_result(result: dict[str, Any]) -> dict[str, Any] | None:
    category = str(result.get("category", "")).strip()
    department = str(result.get("department", "")).strip()
    priority = str(result.get("priority", "")).strip().lower()
    reason = str(result.get("routing_reason", "")).strip()
    try:
        confidence = float(result.get("confidence"))
    except (TypeError, ValueError):
        return None
    if category not in CATEGORY_IDS or department not in OFFICIAL_DEPARTMENTS or priority not in {"low", "medium", "high", "urgent"} or not reason:
        return None
    return {
        "category": category,
        "category_id": CATEGORY_IDS[category],
        "department": department,
        "department_id": OFFICIAL_DEPARTMENTS[department],
        "priority": priority,
        "confidence": max(0.0, min(1.0, confidence)),
        "matched_keywords": [],
        "routing_reason": reason,
        "source": "ai",
    }


def _priority(text: str) -> str:
    if _matches(text, ("خطر", "خطير", "حادث", "اصابة", "طوارئ", "اطفال", "يهدد الحياة", "انهيار", "حريق")):
        return "urgent"
    if _matches(text, ("كبير", "كتير", "متكرر", "منذ ايام", "منذ اسبوع", "يمنع المرور", "يعطل الخدمة", "عدد كبير من المواطنين")):
        return "high"
    return "medium"
