from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.config import BASE_DIR, get_settings
from app.database import get_db
from app.models.category import Category
from app.models.comment import Comment
from app.models.complaint import Complaint
from app.models.complaint_update import ComplaintUpdate
from app.models.department import Department
from app.models.user import User
from app.services.analyzer_service import analyze_complaint
from app.services.auth_service import authenticate_user, create_user

router = APIRouter(prefix="", tags=["auth"])
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
settings = get_settings()
ALLOWED_PRIORITIES = {"low", "medium", "high", "urgent"}
ALLOWED_STATUSES = {"new", "assigned", "in_progress", "resolved", "closed"}
STATUS_LABELS = {
    "new": "جديد",
    "assigned": "تم الإسناد",
    "in_progress": "قيد المعالجة",
    "resolved": "تم الحل",
    "closed": "مغلق",
}


class ComplaintAnalysisRequest(BaseModel):
    text: str = Field(min_length=3)
    area: str | None = None
    governorate: str | None = None


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.get(User, user_id)


def require_auth(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return user


def require_role(role: str):
    def dependency(request: Request, db: Session = Depends(get_db)) -> User:
        user = require_auth(request, db)
        if user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        return user

    return dependency


async def upload_complaint_image(file: UploadFile | None) -> str | None:
    if file is None or file.filename in (None, ""):
        return None

    allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
    suffix = Path(file.filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise ValueError("تنسيق الصورة غير مسموح. استخدم JPG، JPEG، PNG أو WEBP.")

    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise ValueError("حجم الصورة يجب أن يكون أقل من 5 MB.")

    uploads_dir = BASE_DIR / "app" / "static" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid4().hex}{suffix}"
    target_path = uploads_dir / filename
    target_path.write_bytes(file_content)
    return f"/uploads/{filename}"


async def render_citizen_page(request: Request, user: User, db: Session, title: str):
    complaints_stmt = (
        select(Complaint)
        .options(selectinload(Complaint.category), selectinload(Complaint.updates))
        .where(Complaint.user_id == user.id)
        .order_by(Complaint.created_at.desc())
    )
    complaints = db.scalars(complaints_stmt).all()

    for complaint in complaints:
        complaint.updates = sorted(complaint.updates, key=lambda item: item.created_at, reverse=True)

    new_count = sum(1 for complaint in complaints if complaint.status == "new")
    in_progress_count = sum(1 for complaint in complaints if complaint.status in {"assigned", "in_progress"})
    resolved_count = sum(1 for complaint in complaints if complaint.status in {"resolved", "closed"})

    return templates.TemplateResponse(
        request,
        "dashboard_citizen.html",
        {
            "title": title,
            "user": user,
            "slogan": settings.project_slogan,
            "complaints": complaints,
            "total_complaints": len(complaints),
            "new_count": new_count,
            "in_progress_count": in_progress_count,
            "resolved_count": resolved_count,
        },
    )


def add_complaint_history(db: Session, complaint: Complaint, user: User, note: str, old_status: str | None = None) -> None:
    db.add(
        ComplaintUpdate(
            complaint_id=complaint.id,
            user_id=user.id,
            old_status=old_status,
            new_status=complaint.status,
            note=note,
        )
    )


def complaint_detail_options():
    return (
        selectinload(Complaint.category),
        selectinload(Complaint.department),
        selectinload(Complaint.updates),
        selectinload(Complaint.comments).selectinload(Comment.user),
    )


@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "auth_login.html",
        {"title": "تسجيل الدخول", "slogan": settings.project_slogan},
    )


@router.post("/login")
async def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = authenticate_user(email, password)
    if not user:
        return templates.TemplateResponse(
            request,
            "auth_login.html",
            {
                "title": "تسجيل الدخول",
                "slogan": settings.project_slogan,
                "error": "البريد الإلكتروني أو كلمة المرور غير صحيحة.",
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session["user_id"] = user.id
    request.session["user_role"] = user.role
    request.session["user_name"] = user.name

    redirect_path = "/admin" if user.role == "admin" else "/citizen"
    return RedirectResponse(url=redirect_path, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "auth_register.html",
        {"title": "إنشاء حساب", "slogan": settings.project_slogan},
    )


@router.post("/register")
async def register_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    if not name.strip() or not email.strip() or not password:
        return templates.TemplateResponse(
            request,
            "auth_register.html",
            {
                "title": "إنشاء حساب",
                "slogan": settings.project_slogan,
                "error": "يرجى تعبئة جميع الحقول المطلوبة.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if password != password_confirm:
        return templates.TemplateResponse(
            request,
            "auth_register.html",
            {
                "title": "إنشاء حساب",
                "slogan": settings.project_slogan,
                "error": "كلمتا المرور غير متطابقتين.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = create_user(name=name, email=email, password=password, role="citizen")
    except ValueError as exc:
        return templates.TemplateResponse(
            request,
            "auth_register.html",
            {
                "title": "إنشاء حساب",
                "slogan": settings.project_slogan,
                "error": str(exc),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    request.session["user_id"] = user.id
    request.session["user_role"] = user.role
    request.session["user_name"] = user.name
    return RedirectResponse(url="/citizen", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/citizen")
async def citizen_dashboard(request: Request, user: User = Depends(require_role("citizen")), db: Session = Depends(get_db)):
    return await render_citizen_page(request, user, db, "لوحة المواطن")


@router.get("/citizen/complaints")
async def citizen_complaints(request: Request, user: User = Depends(require_role("citizen")), db: Session = Depends(get_db)):
    return await render_citizen_page(request, user, db, "بلاغاتي")


@router.get("/citizen/complaints/new")
async def complaint_form_page(request: Request, user: User = Depends(require_role("citizen")), db: Session = Depends(get_db)):
    categories = db.scalars(select(Category).order_by(Category.name.asc())).all()
    return templates.TemplateResponse(
        request,
        "complaint_form.html",
        {"title": "إنشاء بلاغ جديد", "slogan": settings.project_slogan, "user": user, "categories": categories},
    )


@router.post("/api/complaints/analyze")
async def analyze_complaint_api(
    payload: ComplaintAnalysisRequest,
    user: User = Depends(require_role("citizen")),
):
    return analyze_complaint(payload.text, area=payload.area, governorate=payload.governorate)


@router.post("/citizen/complaints/new")
async def complaint_form_submit(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category_id: int = Form(...),
    address: str | None = Form(None),
    area: str | None = Form(None),
    governorate: str | None = Form(None),
    latitude: str | None = Form(None),
    longitude: str | None = Form(None),
    image: UploadFile | None = File(None),
    accept_analysis: bool = Form(False),
    user: User = Depends(require_role("citizen")),
    db: Session = Depends(get_db),
):
    category = db.get(Category, category_id)
    if not title.strip() or not description.strip() or category is None:
        categories = db.scalars(select(Category).order_by(Category.name.asc())).all()
        return templates.TemplateResponse(
            request,
            "complaint_form.html",
            {
                "title": "إنشاء بلاغ جديد",
                "slogan": settings.project_slogan,
                "user": user,
                "categories": categories,
                "error": "يرجى تعبئة عنوان البلاغ، الوصف، واختيار نوع المشكلة.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        image_path = await upload_complaint_image(image)
    except ValueError as exc:
        categories = db.scalars(select(Category).order_by(Category.name.asc())).all()
        return templates.TemplateResponse(
            request,
            "complaint_form.html",
            {
                "title": "إنشاء بلاغ جديد",
                "slogan": settings.project_slogan,
                "user": user,
                "categories": categories,
                "error": str(exc),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        latitude_value = float(latitude) if latitude not in (None, "") else None
        longitude_value = float(longitude) if longitude not in (None, "") else None
        if latitude_value is not None and not -90 <= latitude_value <= 90:
            raise ValueError("خط العرض يجب أن يكون بين -90 و 90.")
        if longitude_value is not None and not -180 <= longitude_value <= 180:
            raise ValueError("خط الطول يجب أن يكون بين -180 و 180.")
    except ValueError as exc:
        categories = db.scalars(select(Category).order_by(Category.name.asc())).all()
        return templates.TemplateResponse(
            request,
            "complaint_form.html",
            {
                "title": "إنشاء بلاغ جديد",
                "slogan": settings.project_slogan,
                "user": user,
                "categories": categories,
                "error": str(exc),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    analysis = analyze_complaint(f"{title} {description}", area=area, governorate=governorate) if accept_analysis else None
    if analysis:
        category = db.get(Category, analysis["category_id"])
        department = db.get(Department, analysis["department_id"])
        if category is None or department is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Analyzer recommendation is invalid")

    complaint = Complaint(
        user_id=user.id,
        category_id=analysis["category_id"] if analysis else category.id,
        department_id=analysis["department_id"] if analysis else None,
        title=title.strip(),
        description=description.strip(),
        address=address.strip() if address else None,
        area=area.strip() if area else None,
        governorate=governorate.strip() if governorate else None,
        latitude=latitude_value,
        longitude=longitude_value,
        image_path=image_path,
        priority=analysis["priority"] if analysis else "medium",
        status="assigned" if analysis else "new",
        routing_reason=analysis["routing_reason"] if analysis else None,
        routing_confidence=analysis["confidence"] if analysis else None,
        assigned_at=datetime.now(timezone.utc) if analysis else None,
    )
    db.add(complaint)
    db.flush()

    db.add(
        ComplaintUpdate(
            complaint_id=complaint.id,
            user_id=user.id,
            old_status=None,
            new_status="new",
            note="تم إنشاء البلاغ",
        )
    )
    db.add(
        ComplaintUpdate(
            complaint_id=complaint.id,
            user_id=user.id,
            old_status="new",
            new_status="new",
            note="تم تصنيف البلاغ",
        )
    )
    if analysis:
        db.add(
            ComplaintUpdate(
                complaint_id=complaint.id,
                user_id=user.id,
                old_status="new",
                new_status="assigned",
                note=f"تم توجيه البلاغ تلقائياً إلى {analysis['department']}",
            )
        )
    db.commit()
    db.refresh(complaint)
    return RedirectResponse(url=f"/citizen/complaints/{complaint.id}", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/citizen/complaints/{complaint_id}")
async def complaint_detail(
    request: Request,
    complaint_id: int,
    user: User = Depends(require_role("citizen")),
    db: Session = Depends(get_db),
):
    complaint = db.scalar(
        select(Complaint)
        .options(*complaint_detail_options())
        .where(Complaint.id == complaint_id, Complaint.user_id == user.id)
    )
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    complaint.updates = sorted(complaint.updates, key=lambda item: item.created_at, reverse=True)
    complaint.comments = sorted(complaint.comments, key=lambda item: item.created_at)

    return templates.TemplateResponse(
        request,
        "complaint_details.html",
        {
            "title": "تفاصيل البلاغ",
            "slogan": settings.project_slogan,
            "user": user,
            "complaint": complaint,
            "status_labels": STATUS_LABELS,
        },
    )


@router.post("/complaints/{complaint_id}/comments")
async def add_complaint_comment(
    request: Request,
    complaint_id: int,
    body: str = Form(...),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    if user.role == "citizen" and complaint.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")
    if user.role not in {"citizen", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    comment_body = body.strip()
    if not comment_body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment cannot be empty")

    db.add(Comment(complaint_id=complaint.id, user_id=user.id, body=comment_body))
    db.commit()
    destination = f"/admin/complaints/{complaint.id}" if user.role == "admin" else f"/citizen/complaints/{complaint.id}"
    return RedirectResponse(url=destination, status_code=status.HTTP_303_SEE_OTHER)


@router.get("/admin")
async def admin_dashboard(
    request: Request,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    complaints = db.scalars(
        select(Complaint)
        .options(selectinload(Complaint.user), selectinload(Complaint.category), selectinload(Complaint.department))
        .order_by(Complaint.created_at.desc())
    ).all()

    total_complaints = len(complaints)
    new_count = sum(1 for complaint in complaints if complaint.status == "new")
    urgent_count = sum(1 for complaint in complaints if complaint.priority == "urgent")
    in_progress_count = sum(1 for complaint in complaints if complaint.status in {"assigned", "in_progress"})
    resolved_count = sum(1 for complaint in complaints if complaint.status in {"resolved", "closed"})
    pending_routing_count = sum(1 for complaint in complaints if complaint.department_id is None)

    recent_complaints = complaints[:5]
    departments = db.scalars(select(Department).order_by(Department.name.asc())).all()
    routed_complaints = [complaint for complaint in complaints if complaint.department]
    open_complaints = [complaint for complaint in complaints if complaint.status not in {"resolved", "closed"}]
    top_department = max(routed_complaints, key=lambda item: sum(other.department_id == item.department_id for other in routed_complaints)).department if routed_complaints else None
    categorized_complaints = [complaint for complaint in complaints if complaint.category]
    top_category = max(categorized_complaints, key=lambda item: sum(other.category_id == item.category_id for other in categorized_complaints)).category if categorized_complaints else None
    governorates = [complaint.governorate for complaint in open_complaints if complaint.governorate]
    top_governorate = max(set(governorates), key=governorates.count) if governorates else None

    return templates.TemplateResponse(
        request,
        "dashboard_admin.html",
        {
            "title": "لوحة الإدارة",
            "user": user,
            "slogan": settings.project_slogan,
            "total_complaints": total_complaints,
            "new_count": new_count,
            "urgent_count": urgent_count,
            "in_progress_count": in_progress_count,
            "resolved_count": resolved_count,
            "pending_routing_count": pending_routing_count,
            "recent_complaints": recent_complaints,
            "departments": departments,
            "top_department": top_department,
            "top_category": top_category,
            "top_governorate": top_governorate,
        },
    )


@router.get("/admin/complaints")
async def admin_complaints_list(
    request: Request,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    category: str | None = Query(default=None),
    department: str | None = Query(default=None),
    governorate: str | None = Query(default=None),
    search: str | None = Query(default=None),
):
    stmt = (
        select(Complaint)
        .options(selectinload(Complaint.user), selectinload(Complaint.category), selectinload(Complaint.department))
        .order_by(Complaint.created_at.desc())
    )

    if status:
        stmt = stmt.where(Complaint.status == status)
    if priority:
        stmt = stmt.where(Complaint.priority == priority)
    if category:
        stmt = stmt.where(Complaint.category_id == int(category))
    if department:
        stmt = stmt.where(Complaint.department_id == int(department))
    if governorate:
        stmt = stmt.where(Complaint.governorate == governorate)
    if search:
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Complaint.title.ilike(term),
                Complaint.description.ilike(term),
                Complaint.address.ilike(term),
                Complaint.area.ilike(term),
                Complaint.governorate.ilike(term),
            )
        )

    complaints = db.scalars(stmt).all()
    categories = db.scalars(select(Category).order_by(Category.name.asc())).all()
    departments = db.scalars(select(Department).order_by(Department.name.asc())).all()
    governorates = db.scalars(
        select(Complaint.governorate)
        .where(Complaint.governorate.isnot(None))
        .distinct()
        .order_by(Complaint.governorate.asc())
    ).all()

    return templates.TemplateResponse(
        request,
        "admin_complaints.html",
        {
            "title": "إدارة البلاغات",
            "user": user,
            "slogan": settings.project_slogan,
            "complaints": complaints,
            "categories": categories,
            "departments": departments,
            "governorates": governorates,
            "status_filter": status,
            "priority_filter": priority,
            "category_filter": category,
            "department_filter": department,
            "governorate_filter": governorate,
            "search": search,
        },
    )


@router.get("/admin/map")
async def admin_complaint_map(
    request: Request,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    categories = db.scalars(select(Category).order_by(Category.name.asc())).all()
    departments = db.scalars(select(Department).order_by(Department.name.asc())).all()
    governorates = db.scalars(
        select(Complaint.governorate)
        .where(Complaint.governorate.isnot(None))
        .distinct()
        .order_by(Complaint.governorate.asc())
    ).all()
    return templates.TemplateResponse(
        request,
        "admin_map.html",
        {
            "title": "الخريطة التفاعلية للبلاغات",
            "user": user,
            "slogan": settings.project_slogan,
            "categories": categories,
            "departments": departments,
            "governorates": governorates,
        },
    )


@router.get("/api/map/complaints")
async def map_complaints_api(
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
    status: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    category: int | None = Query(default=None),
    department: int | None = Query(default=None),
    governorate: str | None = Query(default=None),
):
    stmt = (
        select(Complaint)
        .options(selectinload(Complaint.category), selectinload(Complaint.department))
        .where(Complaint.latitude.isnot(None), Complaint.longitude.isnot(None))
        .order_by(Complaint.created_at.desc())
    )

    if status:
        stmt = stmt.where(Complaint.status == status)
    if priority:
        stmt = stmt.where(Complaint.priority == priority)
    if category is not None:
        stmt = stmt.where(Complaint.category_id == category)
    if department is not None:
        stmt = stmt.where(Complaint.department_id == department)
    if governorate:
        stmt = stmt.where(Complaint.governorate == governorate)

    complaints = db.scalars(stmt).all()
    return [
        {
            "id": complaint.id,
            "title": complaint.title,
            "latitude": complaint.latitude,
            "longitude": complaint.longitude,
            "address": complaint.address,
            "area": complaint.area,
            "governorate": complaint.governorate,
            "category": complaint.category.name if complaint.category else None,
            "priority": complaint.priority,
            "status": complaint.status,
            "department": complaint.department.name if complaint.department else None,
        }
        for complaint in complaints
    ]


@router.get("/admin/complaints/{complaint_id}")
async def admin_complaint_detail(
    request: Request,
    complaint_id: int,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    complaint = db.scalar(
        select(Complaint)
        .options(selectinload(Complaint.user), *complaint_detail_options())
        .where(Complaint.id == complaint_id)
    )
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    complaint.updates = sorted(complaint.updates, key=lambda item: item.created_at, reverse=True)
    complaint.comments = sorted(complaint.comments, key=lambda item: item.created_at)
    departments = db.scalars(select(Department).order_by(Department.name.asc())).all()
    return templates.TemplateResponse(
        request,
        "admin_complaint_detail.html",
        {
            "title": f"تفاصيل البلاغ #{complaint.id}",
            "user": user,
            "slogan": settings.project_slogan,
            "complaint": complaint,
            "departments": departments,
            "status_labels": STATUS_LABELS,
        },
    )


@router.post("/admin/complaints/{complaint_id}")
async def admin_complaint_update(
    request: Request,
    complaint_id: int,
    department_id: int | None = Form(default=None),
    priority: str = Form(default="medium"),
    status_value: str = Form(default="new"),
    routing_reason: str = Form(default=""),
    admin_note: str = Form(default=""),
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    complaint = db.get(Complaint, complaint_id)
    if complaint is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Complaint not found")

    if priority not in ALLOWED_PRIORITIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid priority value")
    if status_value not in ALLOWED_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value")

    original_status = complaint.status
    old_status = original_status
    old_priority = complaint.priority
    previous_department_id = complaint.department_id
    previous_department_name = complaint.department.name if complaint.department else None

    if department_id is not None and department_id != previous_department_id:
        department = db.get(Department, department_id)
        if department is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected department is invalid")
        complaint.department_id = department.id
        complaint.assigned_at = datetime.now(timezone.utc)
        if complaint.status == "new":
            complaint.status = "assigned"
        if previous_department_name:
            note = f"تم تعديل الجهة المختصة من {previous_department_name} إلى {department.name}"
        else:
            note = f"تم توجيه البلاغ إلى {department.name}"
        complaint.routing_reason = routing_reason.strip() or note
        add_complaint_history(db, complaint, user, note, old_status)
        old_status = complaint.status

    if priority and priority != old_priority:
        note = f"تم تغيير الأولوية من {old_priority} إلى {priority}"
        complaint.priority = priority
        add_complaint_history(db, complaint, user, note, complaint.status)

    if status_value and status_value != original_status:
        status_before_change = complaint.status
        if status_value == "resolved":
            note = "تم حل البلاغ"
        elif status_value == "closed":
            note = "تم إغلاق البلاغ"
        else:
            note = f"تم تغيير الحالة من {STATUS_LABELS[status_before_change]} إلى {STATUS_LABELS[status_value]}"
        complaint.status = status_value
        if status_value == "resolved" and complaint.resolved_at is None:
            complaint.resolved_at = datetime.now(timezone.utc)
        if status_value != "resolved" and complaint.resolved_at is not None and status_value != "closed":
            complaint.resolved_at = None
        add_complaint_history(db, complaint, user, note, status_before_change)

    if complaint.department_id is None and routing_reason.strip() and routing_reason.strip() != (complaint.routing_reason or ""):
        complaint.routing_reason = routing_reason.strip()
        add_complaint_history(db, complaint, user, "تمت إضافة ملاحظة إدارية", complaint.status)

    if admin_note.strip():
        add_complaint_history(db, complaint, user, f"تمت إضافة ملاحظة إدارية: {admin_note.strip()}", complaint.status)

    complaint.updated_at = datetime.now(timezone.utc)
    db.commit()
    return RedirectResponse(url=f"/admin/complaints/{complaint.id}", status_code=status.HTTP_303_SEE_OTHER)
