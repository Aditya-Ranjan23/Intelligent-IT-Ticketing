import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Intelligent IT Ticket Auto-Resolution System"
    VERSION: str = "0.2.0"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # PostgreSQL Database URL (defaults to postgresql://postgres:postgres@localhost:5432/it_ticketing)
    POSTGRES_URI: str = "postgresql://postgres:postgres@localhost:5432/it_ticketing"
    
    # Redis URL
    REDIS_URL: str = "redis://localhost:6379/0"

    # ML & Classification Thresholds
    CONFIDENCE_THRESHOLD: float = 0.72
    CACHE_SIMILARITY_THRESHOLD: float = 0.82
    STORE_PLAYBOOK_HITS: bool = True
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    # Google Gemini LLM settings
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # OCR settings
    OCR_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
