from functools import lru_cache

from app.core.config import settings
from app.storage.base import StorageBackend
from app.storage.local import LocalStorage

_S3_FIELDS = {
    "R2_ACCOUNT_ID": "r2_account_id",
    "R2_ACCESS_KEY_ID": "r2_access_key_id",
    "R2_SECRET_ACCESS_KEY": "r2_secret_access_key",
    "R2_BUCKET_NAME": "r2_bucket_name",
    "R2_PUBLIC_BASE_URL": "r2_public_base_url",
}


@lru_cache
def get_storage() -> StorageBackend:
    """Return the configured storage backend.

    `STORAGE_BACKEND=s3` requires every R2_* variable; a clear startup error
    beats a cryptic credential failure on the first upload.
    """
    if settings.storage_backend.lower() == "s3":
        missing = [
            name
            for name, attr in _S3_FIELDS.items()
            if not str(getattr(settings, attr, "")).strip()
        ]
        if missing:
            raise RuntimeError(
                "STORAGE_BACKEND=s3 but these variables are empty: "
                + ", ".join(missing)
                + ". Set them in backend/.env or switch STORAGE_BACKEND to local."
            )
        from app.storage.s3 import S3Storage

        return S3Storage(
            account_id=settings.r2_account_id,
            access_key_id=settings.r2_access_key_id,
            secret_access_key=settings.r2_secret_access_key,
            bucket=settings.r2_bucket_name,
            public_base_url=settings.r2_public_base_url,
        )
    return LocalStorage(settings.media_path, settings.media_base_url)
