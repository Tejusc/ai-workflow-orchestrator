import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "local"
    API_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"

    # Database settings (used soon)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_orc"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
