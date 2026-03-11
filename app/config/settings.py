from urllib.parse import quote

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    user: str = Field(..., alias="POSTGRES_USER")
    password: str = Field(..., alias="POSTGRES_PASSWORD")
    host: str = Field("localhost", alias="POSTGRES_HOST")
    port: int = Field(5432, alias="POSTGRES_PORT")
    db: str = Field(..., alias="POSTGRES_DB")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def url_async(self) -> str:
        user = quote(self.user, safe="")
        password = quote(self.password, safe="")
        return (
            f"postgresql+asyncpg://{user}:{password}"
            f"@{self.host}:{self.port}/{self.db}"
        )


class BotSettings(BaseSettings):
    token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    admin_ids: list[int] = Field(default_factory=list, alias="ADMIN_TELEGRAM_IDS")
    standup_timezone: str = Field("UTC", alias="STANDUP_TIMEZONE")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("admin_ids", mode="before")
    @classmethod
    def parse_admin_ids(cls, v: str | list[int]) -> list[int]:
        if isinstance(v, str):
            return [int(x.strip()) for x in v.split(",") if x.strip()]
        return v or []


class Settings(BaseSettings):
    db: PostgresSettings = Field(default_factory=PostgresSettings)
    bot: BotSettings = Field(default_factory=BotSettings)
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

__all__ = ["Settings", "settings", "PostgresSettings", "BotSettings"]
