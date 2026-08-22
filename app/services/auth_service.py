from __future__ import annotations

from typing import Optional

from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.services.privacy_service import encrypt_national_id, national_id_hash

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def get_user_by_email(email: str) -> Optional[User]:
    normalized_email = email.strip().lower()
    with SessionLocal() as db:
        return db.execute(select(User).where(User.email == normalized_email)).scalar_one_or_none()


def get_user_by_id(user_id: int) -> Optional[User]:
    with SessionLocal() as db:
        return db.get(User, user_id)


def authenticate_user(email: str, password: str) -> Optional[User]:
    user = get_user_by_email(email)
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user(name: str, email: str, password: str, role: str = "citizen", national_id: str | None = None, phone: str | None = None) -> User:
    normalized_name = name.strip()
    normalized_email = email.strip().lower()

    if not normalized_name or not normalized_email or not password:
        raise ValueError("الاسم والبريد الإلكتروني وكلمة المرور مطلوبة.")

    if get_user_by_email(normalized_email):
        raise ValueError("هذا البريد الإلكتروني مستخدم بالفعل.")
    if role == "citizen" and not national_id:
        raise ValueError("الرقم الوطني مطلوب.")

    national_hash = national_id_hash(national_id) if national_id else None
    if national_hash:
        with SessionLocal() as lookup_db:
            if lookup_db.execute(select(User).where(User.national_id_hash == national_hash)).scalar_one_or_none():
                raise ValueError("يوجد حساب مسجل مسبقاً بهذا الرقم الوطني.")

    user = User(
        name=normalized_name,
        email=normalized_email,
        hashed_password=hash_password(password),
        role="citizen",
        national_id_hash=national_hash,
        national_id_encrypted=encrypt_national_id(national_id) if national_id else None,
        phone=phone.strip() if phone else None,
    )

    db: Session = SessionLocal()
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    finally:
        db.close()


def create_field_employee(db: Session, directorate_admin: User, name: str, email: str, phone: str | None, job_title: str | None, password: str) -> User:
    if directorate_admin.role != "directorate_admin" or directorate_admin.department_id is None:
        raise ValueError("لا تملك صلاحية إنشاء موظف ميداني.")
    normalized_name = name.strip()
    normalized_email = email.strip().lower()
    if not normalized_name or not normalized_email or not password:
        raise ValueError("الاسم والبريد الإلكتروني وكلمة المرور مطلوبة.")
    if db.scalar(select(User).where(User.email == normalized_email)):
        raise ValueError("البريد الإلكتروني مستخدم مسبقاً.")

    employee = User(
        name=normalized_name,
        email=normalized_email,
        hashed_password=hash_password(password),
        role="field_employee",
        department_id=directorate_admin.department_id,
        phone=phone.strip() if phone else None,
        job_title=job_title.strip() if job_title else None,
        is_active=True,
    )
    try:
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return employee
    except IntegrityError as error:
        db.rollback()
        raise ValueError("تعذر إنشاء الموظف. تحقق من البيانات.") from error
