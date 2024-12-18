import os
from enum import Enum

from pydantic_settings import BaseSettings
from starlette.config import Config

current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", "..", ".env")
config = Config(env_path)


class AppSettings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)


class CryptSettings(BaseSettings):
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7)


class FirstUserSettings(BaseSettings):
    ADMIN_NAME: str = config("ADMIN_NAME", default="admin")
    ADMIN_EMAIL: str = config("ADMIN_EMAIL", default="admin@admin.com")
    ADMIN_USERNAME: str = config("ADMIN_USERNAME", default="admin")
    ADMIN_PASSWORD: str = config("ADMIN_PASSWORD", default="!Ch4ng3Th1sP4ssW0rd!")


class TestSettings(BaseSettings):
    ...


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")

class FluxSettings(BaseSettings):
    FLUX_API_KEY: str = config("FLUX_API_KEY")


class FileStorageSettings(BaseSettings):
    UPLOAD_DIR: str = os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.dirname(__file__)),  # app directory
            "uploads"  # uploads directory inside app
        )
    )
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {"png", "jpg", "jpeg", "gif"}
    BASE_URL: str = "http://localhost:8000"


class DatabaseSettings(BaseSettings):
    # SQLite configuration
    DATABASE_URI: str = config(
        "DATABASE_URI",
        default="sqlite+aiosqlite:///./sql_app.db"
    )

    # Optional: For sync operations (if needed)
    DATABASE_SYNC_URI: str = config(
        "DATABASE_SYNC_URI",
        default="sqlite:///./sql_app.db"
    )

    DB_ECHO: bool = config("DB_ECHO", default=False, cast=bool)


class Settings(
    AppSettings,
    CryptSettings,
    FirstUserSettings,
    TestSettings,
    EnvironmentSettings,
    FluxSettings,
    FileStorageSettings,
    DatabaseSettings,
):
    pass


settings = Settings()
