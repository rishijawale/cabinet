from functools import lru_cache

from app.core.config import settings
from app.storage.base import StorageBackend
from app.storage.local import LocalStorage


@lru_cache
def get_storage() -> StorageBackend:
    if settings.storage_backend.lower() == "s3":
        from app.storage.s3 import S3Storage

        return S3Storage(
            account_id=settings.r2_account_id,
            access_key_id=settings.r2_access_key_id,
            secret_access_key=settings.r2_secret_access_key,
            bucket=settings.r2_bucket_name,
            public_base_url=settings.r2_public_base_url,
        )
    return LocalStorage(settings.media_path, settings.media_base_url)
