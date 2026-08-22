from __future__ import annotations

from fastapi import FastAPI, Request
from sqlalchemy import text
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import BASE_DIR, get_settings
from app.database import Base, engine
from app import seed
from app.routers.auth import router as auth_router
from app.services.i18n_service import department_label, governorate_label, language, priority_label, status_label, translate

settings = get_settings()
app = FastAPI(title=settings.project_name, version="0.1.0")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(BASE_DIR / "app" / "static" / "uploads")), name="uploads")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
templates.env.globals.update(t=translate, status_label=status_label, priority_label=priority_label, department_label=department_label, governorate_label=governorate_label, current_language=language)
app.include_router(auth_router)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request,
        "base.html",
        {"title": settings.project_name, "language": language(request)},
    )


@app.get("/health")
async def health_check():
    return JSONResponse({"status": "ok", "project": "BALIGHNA"})


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        existing_user_columns = {row[1] for row in connection.execute(text("PRAGMA table_info(users)"))}
        existing_complaint_columns = {row[1] for row in connection.execute(text("PRAGMA table_info(complaints)"))}
        for name, definition in {
            "department_id": "INTEGER", "national_id_hash": "VARCHAR(128)", "national_id_encrypted": "VARCHAR(512)",
            "phone": "VARCHAR(50)", "job_title": "VARCHAR(150)", "is_active": "BOOLEAN NOT NULL DEFAULT 1",
        }.items():
            if name not in existing_user_columns:
                connection.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))
        for name, definition in {
            "assigned_employee_id": "INTEGER", "employee_assigned_at": "DATETIME", "work_started_at": "DATETIME",
            "work_completed_at": "DATETIME", "completion_image_path": "VARCHAR(500)", "completion_note": "TEXT",
        }.items():
            if name not in existing_complaint_columns:
                connection.execute(text(f"ALTER TABLE complaints ADD COLUMN {name} {definition}"))
    try:
        seed.seed_data()
    except Exception:
        pass
