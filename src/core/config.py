import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "local"
    API_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"

    # Database settings
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_orc"

    # LLM settings (OpenAI-compatible)
    LLM_API_BASE: str = "https://api.openai.com"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"  # or whatever you'll actually use

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
