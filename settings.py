from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class DBSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def ASYNC_DB_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # noqa

    @property
    def DB_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"  # noqa

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class BackendSettings(BaseSettings):
    BACKEND_HOST: str
    BACKEND_PORT: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class RedisSettings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_USER: Optional[str] = None
    REDIS_PASSWORD: Optional[str] = None

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_USER and self.REDIS_PASSWORD:
            return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}"  # noqa
        else:
            return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class CelerySettings(BaseSettings):
    CELERY_APP_NAME: str
    CELERY_QUEUE_NAME: str
    CELERY_PROCESS_TRANSACTIONS_TASK_NAME: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


redis_settings = RedisSettings()
db_settings = DBSettings()
backend_settings = BackendSettings()
celery_settings = CelerySettings()
