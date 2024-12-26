from typing import Optional, final

from pydantic import HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


@final
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.prod.env', '.dev.env', '.env'),
        env_file_encoding='utf-8',
        extra='ignore'
    )

    APP_TITLE: Optional[str] = "FastAPI"

    APP_SUMMARY: Optional[str] = "FastAPI with MongoDB"

    APP_BASE_URL: HttpUrl

    MONGODB_URI: str

    PROXY_URL: Optional[str] = None

    TELEGRAM_API_TOKEN: str

    TELEGRAM_WEBHOOK_PATH: Optional[str] = "/tgupdates"

    def get_mongodb_db_name(self):
        return self.MONGODB_URI.rsplit('/', 1)[1]


cfg = Settings()
