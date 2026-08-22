from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.config import BASE_DIR, get_settings
from app.database import Base, engine
from app import seed
from app.routers.auth import router as auth_router

settings = get_settings()
app = FastAPI(title=settings.project_name, version="0.1.0")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(BASE_DIR / "app" / "static" / "uploads")), name="uploads")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
app.include_router(auth_router)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        request,
        "base.html",
        {"title": settings.project_name},
    )


@app.get("/health")
async def health_check():
    return JSONResponse({"status": "ok", "project": "BALIGHNA"})


@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    try:
        seed.seed_data()
    except Exception:
        pass
