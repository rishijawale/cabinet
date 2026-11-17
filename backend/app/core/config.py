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
    allowed_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173"
    )
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

    # Cache policy. Public archive GETs are cached briefly so browsers and CDNs
    # absorb repeat traffic; auth surfaces and mutations are never cached.
    api_cache_max_age: int = 60
    media_cache_max_age: int = 604800  # one week; previews regenerate deterministically

    secret_key: str = "dev-secret"
    supabase_url: str = ""
    supabase_jwks_url: str = ""
    supabase_audience: str = "authenticated"
    supabase_issuer: str = ""
    supabase_leeway_seconds: int = 30

    @property
    def auth_enabled(self) -> bool:
        """Auth is opt-in: set SUPABASE_URL to turn it on, leave empty to disable."""
        return bool(self.supabase_url.strip())

    @property
    def auth_jwks_url(self) -> str:
        configured = self.supabase_jwks_url.strip()
        if configured:
            return configured
        return f"{self.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"

    @property
    def auth_issuer(self) -> str:
        configured = self.supabase_issuer.strip()
        if configured:
            return configured
        return f"{self.supabase_url.rstrip('/')}/auth/v1"

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

    @property
    def is_production(self) -> bool:
        return self.environment.lower() in {"production", "prod"}


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
