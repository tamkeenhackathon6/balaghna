from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


class Settings(BaseSettings):
    project_name: str = "BALIGHNA"
    project_name_ar: str = "بلّغنا"
    project_slogan: str = "بلّغنا، والباقي علينا"
    app_env: str = "development"
    database_url: str = f"sqlite:///{DATA_DIR / 'app.db'}"
    secret_key: str = "change-me-in-production"
    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:4b"
    ollama_timeout: int = 20
    ai_analyzer_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
