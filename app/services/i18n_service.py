from __future__ import annotations

MESSAGES = {
    "ar": {
        "login": "تسجيل الدخول", "register": "إنشاء حساب", "logout": "تسجيل الخروج", "email": "البريد الإلكتروني", "password": "كلمة المرور", "home": "الرئيسية", "complaints": "بلاغاتي", "create_complaint": "إنشاء بلاغ", "dashboard": "لوحة التحكم", "map": "الخريطة", "submit": "إرسال", "save": "حفظ", "search": "بحث", "filter": "تطبيق", "reset": "إعادة تعيين", "details": "عرض التفاصيل", "category": "نوع البلاغ", "priority": "الأولوية", "status": "الحالة", "department": "الجهة المختصة", "governorate": "المحافظة", "area": "المنطقة", "comments": "التعليقات", "timeline": "سجل المتابعة", "routing": "توجيه البلاغ", "change_entity": "تغيير الجهة", "routing_reason": "سبب التوجيه", "admin_note": "ملاحظة إدارية", "new": "جديد", "assigned": "تم الإسناد", "in_progress": "قيد المعالجة", "resolved": "تم الحل", "closed": "مغلق", "low": "منخفض", "medium": "متوسط", "high": "مرتفع", "urgent": "عاجل",
    },
    "en": {
        "login": "Login", "register": "Create Account", "logout": "Logout", "email": "Email", "password": "Password", "home": "Home", "complaints": "My Complaints", "create_complaint": "Create Complaint", "dashboard": "Dashboard", "map": "Map", "submit": "Submit", "save": "Save", "search": "Search", "filter": "Apply", "reset": "Reset", "details": "View Details", "category": "Complaint Type", "priority": "Priority", "status": "Status", "department": "Responsible Entity", "governorate": "Governorate", "area": "Area", "comments": "Comments", "timeline": "Timeline", "routing": "Complaint Routing", "change_entity": "Change Entity", "routing_reason": "Routing Reason", "admin_note": "Administrative Note", "new": "New", "assigned": "Assigned", "in_progress": "In Progress", "resolved": "Resolved", "closed": "Closed", "low": "Low", "medium": "Medium", "high": "High", "urgent": "Urgent",
    },
}

DEPARTMENTS = {
    "مديرية الخدمات المحلية": "Local Services Directorate", "مديريات المجالس المحلية والإدارة المحلية": "Local Councils and Local Administration Directorates", "مديرية التخطيط والتنمية المحلية": "Local Planning and Development Directorate", "مديرية التنظيم والتخطيط العمراني": "Urban Organization and Planning Directorate", "مديرية الشؤون الفنية": "Technical Affairs Directorate", "مديرية الشؤون المالية": "Financial Affairs Directorate", "مديرية الرقابة والتفتيش": "Inspection and Oversight Directorate", "المحافظات": "Governorates", "مجالس المدن والبلديات والوحدات الإدارية": "City Councils, Municipalities and Administrative Units",
}
GOVERNORATES = {"دمشق": "Damascus", "ريف دمشق": "Rural Damascus", "حلب": "Aleppo", "حمص": "Homs", "حماة": "Hama", "اللاذقية": "Latakia", "طرطوس": "Tartous", "إدلب": "Idlib", "درعا": "Daraa", "السويداء": "As-Suwayda", "القنيطرة": "Quneitra", "دير الزور": "Deir ez-Zor", "الرقة": "Raqqa", "الحسكة": "Al-Hasakah"}


def language(request) -> str:
    return request.session.get("language", "ar") if request else "ar"


def translate(key: str, request=None) -> str:
    return MESSAGES[language(request)].get(key, key)


def status_label(value: str, request=None) -> str:
    return translate(value, request)


def priority_label(value: str, request=None) -> str:
    return translate(value, request)


def department_label(value: str | None, request=None) -> str:
    if not value:
        return "Awaiting routing" if language(request) == "en" else "بانتظار التوجيه"
    return DEPARTMENTS.get(value, value) if language(request) == "en" else value


def governorate_label(value: str | None, request=None) -> str:
    return GOVERNORATES.get(value, value) if language(request) == "en" else (value or "")
