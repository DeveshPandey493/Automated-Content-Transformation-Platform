import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

# Workspace root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    # Application
    APP_ENV: str = Field(default="development", description="Environment: development, test, production")
    APP_DEBUG: bool = Field(default=True, description="Enable debug mode and detailed logs")
    APP_NAME: str = Field(default="ACTP - Gen AI Automated Content Transformation", description="Application Title")
    PORT: int = Field(default=8000, description="Server port")
    HOST: str = Field(default="0.0.0.0", description="Server host")

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/content_transformer",
        description="Primary database connection string"
    )
    SQLITE_FALLBACK_URL: str = Field(
        default="sqlite:///./content_transformer.db",
        description="Local fallback database when PostgreSQL is unreachable in dev"
    )

    # Groq API
    GROQ_API_KEY: Optional[str] = Field(default=None, description="Groq API key")
    GROQ_MODEL: str = Field(default="openai/gpt-oss-120b", description="Primary Groq model identifier")

    # Hugging Face & Local Models
    HF_TOKEN: Optional[str] = Field(default=None, description="Hugging Face API token")
    HF_HOME: str = Field(default="./models_cache", description="Local model weights cache directory")
    FLAN_T5_MODEL: str = Field(default="google/flan-t5-base", description="FLAN-T5 model id")
    BART_MODEL: str = Field(default="facebook/bart-base", description="BART model id")
    DEVICE: str = Field(default="auto", description="Device placement: auto, cuda, cpu")

    # Storage
    UPLOAD_DIR: str = Field(default="./storage/uploads", description="Directory for uploaded source documents")
    EXPORT_DIR: str = Field(default="./storage/exports", description="Directory for exported artifacts")
    MAX_UPLOAD_SIZE_MB: int = Field(default=25, description="Maximum permitted upload size in MB")

    # Frontend / CORS
    NEXT_PUBLIC_API_URL: str = Field(default="http://localhost:8000", description="Backend public API URL")
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    class Config:
        env_file = str(ENV_FILE) if ENV_FILE.exists() else ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

_settings: Optional[Settings] = None

def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
        # Ensure storage folders exist
        os.makedirs(_settings.UPLOAD_DIR, exist_ok=True)
        os.makedirs(_settings.EXPORT_DIR, exist_ok=True)
        os.makedirs(_settings.HF_HOME, exist_ok=True)
    return _settings
