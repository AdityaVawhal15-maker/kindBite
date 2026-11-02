"""
KindBite Backend — Core Configuration
Reads settings from environment variables / .env file.
"""
from __future__ import annotations

import os
from typing import List
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Application ----
    APP_NAME: str = "KindBite"
    APP_ENV: str = "development"
    APP_URL: str = "http://localhost:3000"

    # ---- Backend ----
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    DEBUG: bool = True

    # ---- Security ----
    SECRET_KEY: str = "CHANGE_ME_use_a_64_char_random_string_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ---- Database ----
    DATABASE_URL: str = "postgresql+asyncpg://kindbite:kindbite_dev_pass@localhost:5432/kindbite"
    DATABASE_SYNC_URL: str = "postgresql://kindbite:kindbite_dev_pass@localhost:5432/kindbite"

    # ---- CORS ----
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # ---- Email ----
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@kindbite.in"

    @property
    def email_configured(self) -> bool:
        return bool(self.SMTP_HOST and self.SMTP_USER)

    # ---- Uploads ----
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "./uploads"

    # ---- ML ----
    ML_MODELS_DIR: str = "./ml/models/artifacts"
    ML_DATA_DIR: str = "./data"

    # ---- Maps ----
    GOOGLE_MAPS_API_KEY: str = ""

    @property
    def maps_configured(self) -> bool:
        return bool(self.GOOGLE_MAPS_API_KEY)


settings = Settings()
