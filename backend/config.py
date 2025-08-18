# backend/config.py
import os
from pathlib import Path
from pydantic_settings import BaseSettings  # ✅ Correct import for Pydantic v2

class Settings(BaseSettings):
    # Mongo
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "guardian")

    # Milvus
    MILVUS_HOST: str = os.getenv("MILVUS_HOST", "127.0.0.1")
    MILVUS_PORT: str = os.getenv("MILVUS_PORT", "19530")

    # Gemini
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Google Geocoding
    GOOGLE_GEOCODING_API_KEY: str = os.getenv("GOOGLE_GEOCODING_API_KEY", "")

    # Whisper
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "small")

    # Notifications mock config
    NOTIFIER_MODE: str = os.getenv("NOTIFIER_MODE", "mock")  # "mock", "email", "whatsapp", or "twilio"

    # Email (for email-to-sms)
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = os.getenv("SMTP_PORT", 465)
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    class Config:
        env_file = Path(__file__).parent / ".env"

settings = Settings()
