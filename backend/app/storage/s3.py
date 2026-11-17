from pathlib import Path

from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.storage.base import StorageBackend


class S3Storage(StorageBackend):
    """Cloudflare R2 / S3-compatible storage. boto3 is imported lazily.

    The client is pinned to path-style addressing and SigV4 signing, which is
    what R2's account-scoped endpoint expects; presigned download URLs use the
    same region-less configuration.
    """

    def __init__(
        self,
        *,
        account_id: str,
        access_key_id: str,
        secret_access_key: str,
        bucket: str,
        public_base_url: str,
    ) -> None:
        import boto3

        self.bucket = bucket
        self.public_base_url = public_base_url.rstrip("/")
        self.client = boto3.client(
            "s3",
            endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name="auto",
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                retries={"max_attempts": 3},
            ),
        )

    def public_url(self, key: str) -> str:
        return f"{self.public_base_url}/{key.lstrip('/')}"

    def signed_url(self, key: str, ttl_seconds: int) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=ttl_seconds,
        )

    def save(self, key: str, data: bytes, content_type: str) -> None:
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=data, ContentType=content_type
        )

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except (ClientError, BotoCoreError):
            # 404 surfaces as ClientError; network problems as BotoCoreError.
            # Either way the caller treats the object as missing.
            return False

    def local_path(self, key: str) -> Path | None:
        return None
