"""Storage backends: local filesystem plus S3/R2 with a stubbed boto3 client."""

import sys
import types
from pathlib import Path

import pytest

from app.core.config import settings
from app.storage import get_storage
from app.storage.local import LocalStorage


class StubS3Client:
    """Records calls so the wrappers can be asserted without network."""

    def __init__(self, *, fail_head: bool = False):
        self.calls: list[tuple[str, dict]] = []
        self.fail_head = fail_head

    def generate_presigned_url(self, operation: str, Params: dict, ExpiresIn: int) -> str:
        self.calls.append(("presign", {**Params, "ttl": ExpiresIn}))
        return f"https://signed.example/{Params['Key']}?ttl={ExpiresIn}"

    def put_object(self, **kwargs) -> None:
        self.calls.append(("put", kwargs))

    def head_object(self, **kwargs) -> None:
        self.calls.append(("head", kwargs))
        if self.fail_head:
            from botocore.exceptions import ClientError

            raise ClientError(
                {"Error": {"Code": "404", "Message": "Not Found"}},
                "HeadObject",
            )


@pytest.fixture
def stub_boto3(monkeypatch):
    clients: dict[str, StubS3Client] = {}

    def fake_client(service: str, **kwargs) -> StubS3Client:
        assert service == "s3"
        stub = StubS3Client()
        stub.init_kwargs = kwargs
        clients["s3"] = stub
        return stub

    module = types.ModuleType("boto3")
    module.client = fake_client
    monkeypatch.setitem(sys.modules, "boto3", module)
    get_storage.cache_clear()
    yield clients
    get_storage.cache_clear()


@pytest.fixture
def r2_settings(monkeypatch):
    monkeypatch.setattr(settings, "storage_backend", "s3")
    monkeypatch.setattr(settings, "r2_account_id", "acct")
    monkeypatch.setattr(settings, "r2_access_key_id", "key")
    monkeypatch.setattr(settings, "r2_secret_access_key", "secret")
    monkeypatch.setattr(settings, "r2_bucket_name", "cabinet")
    monkeypatch.setattr(settings, "r2_public_base_url", "https://cdn.example/cabinet/")
    return settings


def test_local_storage_urls_and_paths(tmp_path: Path) -> None:
    storage = LocalStorage(tmp_path, "http://localhost:8000/media")
    storage.save("artworks/x/preview-card.webp", b"pretend-webp", "image/webp")
    assert storage.exists("artworks/x/preview-card.webp")
    assert storage.local_path("artworks/x/preview-card.webp") == (
        tmp_path / "artworks" / "x" / "preview-card.webp"
    )
    assert storage.public_url("artworks/x/preview-card.webp").startswith(
        "http://localhost:8000/media/"
    )
    assert not storage.exists("../escape.txt")


def test_default_backend_is_local(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "storage_backend", "local")
    get_storage.cache_clear()
    try:
        assert isinstance(get_storage(), LocalStorage)
    finally:
        get_storage.cache_clear()


def test_s3_config_must_be_complete(monkeypatch) -> None:
    monkeypatch.setattr(settings, "storage_backend", "s3")
    monkeypatch.setattr(settings, "r2_account_id", "")
    get_storage.cache_clear()
    try:
        with pytest.raises(RuntimeError) as exc:
            get_storage()
        assert "R2_ACCOUNT_ID" in str(exc.value)
    finally:
        get_storage.cache_clear()


def test_s3_backend_delegates_to_client(r2_settings, stub_boto3) -> None:
    storage = get_storage()
    assert "s3" in stub_boto3
    client = stub_boto3["s3"]
    assert client.init_kwargs["endpoint_url"] == "https://acct.r2.cloudflarestorage.com"

    assert storage.public_url("/artworks/x/card.webp") == (
        "https://cdn.example/cabinet/artworks/x/card.webp"
    )

    url = storage.signed_url("artworks/x/original.txt", 300)
    assert url.startswith("https://signed.example/artworks/x/original.txt")
    presign = next(call for name, call in client.calls if name == "presign")
    assert presign["Bucket"] == "cabinet" and presign["ttl"] == 300

    storage.save("artworks/x/original.txt", b"ascii", "text/plain")
    put = next(call for name, call in client.calls if name == "put")
    assert put["Key"] == "artworks/x/original.txt" and put["ContentType"] == "text/plain"

    assert storage.exists("artworks/x/original.txt") is True
    assert storage.local_path("artworks/x/original.txt") is None


def test_s3_exists_treats_errors_as_missing(r2_settings) -> None:
    import sys
    import types

    def fake_client(service: str, **kwargs) -> StubS3Client:
        return StubS3Client(fail_head=True)

    module = types.ModuleType("boto3")
    module.client = fake_client
    sys.modules["boto3"] = module
    get_storage.cache_clear()
    try:
        assert get_storage().exists("artworks/x/original.txt") is False
    finally:
        get_storage.cache_clear()
        sys.modules.pop("boto3", None)
