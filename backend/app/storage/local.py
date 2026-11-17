from pathlib import Path, PurePosixPath

from app.storage.base import StorageBackend


class LocalStorage(StorageBackend):
    """Development storage backed by the local filesystem and served at /media."""

    def __init__(self, root: Path, base_url: str) -> None:
        self.root = root
        self.base_url = base_url.rstrip("/")
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        clean = PurePosixPath(key)
        if clean.is_absolute() or ".." in clean.parts:
            raise ValueError(f"Unsafe storage key: {key!r}")
        return self.root.joinpath(*clean.parts)

    def public_url(self, key: str) -> str:
        return f"{self.base_url}/{key.lstrip('/')}"

    def signed_url(self, key: str, ttl_seconds: int) -> str:
        # Local files are public in development; the interface matches S3 so the
        # download service does not change when R2 is configured.
        return self.public_url(key)

    def save(self, key: str, data: bytes, content_type: str) -> None:
        path = self._resolve(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def exists(self, key: str) -> bool:
        try:
            return self._resolve(key).is_file()
        except ValueError:
            return False

    def local_path(self, key: str) -> Path | None:
        return self._resolve(key)
