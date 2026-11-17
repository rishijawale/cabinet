from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: str = "development"
    database_url: str = "postgresql+asyncpg://cabinet:cabinet@127.0.0.1:5432/cabinet"
    allowed_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    public_site_url: str = "http://localhost:5173"

    storage_backend: str = "local"
    media_root: str = "media"
    media_base_url: str = "http://localhost:8000/media"

    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket_name: str = ""
    r2_public_base_url: str = ""

    download_url_ttl_seconds: int = 300
    default_page_size: int = 24
    max_page_size: int = 48

    secret_key: str = "dev-secret"
    supabase_url: str = ""
    supabase_jwks_url: str = ""

    @property
    def allowed_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def media_path(self) -> Path:
        path = Path(self.media_root)
        return path if path.is_absolute() else BACKEND_DIR / path

    @property
    def is_development(self) -> bool:
        return self.environment.lower() in {"development", "dev", "local"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
