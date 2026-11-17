"""Validate every archive object against its database record and stored files.

Run from the repository root:

    .venv/Scripts/python scripts/validate_assets.py

Checks include preview variants, original files, hashes from the seed manifest,
dimensions, text encoding, license coherence and orphaned media directories.
Exit code is 1 when any error is found. Warnings only fail with --strict.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import io
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from PIL import Image, UnidentifiedImageError  # noqa: E402
from sqlalchemy import select  # noqa: E402
from sqlalchemy.orm import joinedload, selectinload  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.db import SessionLocal  # noqa: E402
from app.models import Artwork, Category, Collection  # noqa: E402
from app.models.enums import ArtworkStatus, MediaType  # noqa: E402
from app.storage import get_storage  # noqa: E402
from app.storage.local import LocalStorage  # noqa: E402

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
TEXT_FORMATS = {"txt"}
IMAGE_FORMATS = {"png", "jpg", "jpeg", "webp"}
MANIFEST_KEY = "seed-manifest.json"


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def check_webp(path: Path, label: str, report: Report) -> tuple[int, int] | None:
    try:
        data = path.read_bytes()
    except OSError as exc:
        report.error(f"{label}: cannot read file ({exc})")
        return None
    if len(data) < 16:
        report.error(f"{label}: file is too small to be a WebP image")
        return None
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        report.error(f"{label}: missing WebP signature")
        return None
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            return image.size
    except (UnidentifiedImageError, OSError) as exc:
        report.error(f"{label}: unreadable image ({exc})")
        return None


def check_text(data: bytes, label: str, report: Report) -> None:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        report.error(f"{label}: original text is not valid UTF-8 ({exc})")
        return
    if not text.strip():
        report.error(f"{label}: original text is empty")
        return
    printable = sum(1 for char in text if char.isprintable() or char in "\n\r\t")
    ratio = printable / max(len(text), 1)
    if ratio < 0.9:
        report.error(f"{label}: only {ratio:.0%} of the original text is printable")
    longest = max((len(line) for line in text.splitlines()), default=0)
    if longest > 500:
        report.warn(f"{label}: longest line is {longest} characters")


def check_image_dimensions(data: bytes, label: str, report: Report) -> tuple[int, int] | None:
    try:
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            return image.size
    except (UnidentifiedImageError, OSError) as exc:
        report.error(f"{label}: unreadable original image ({exc})")
        return None


def expected_orientation(width: int, height: int) -> str:
    if width == height:
        return "square"
    return "landscape" if width > height else "portrait"


def format_from_key(key: str) -> str:
    suffix = Path(key).suffix.lower().lstrip(".")
    return "jpg" if suffix == "jpeg" else suffix


async def load_manifest(storage, report: Report) -> dict[str, dict]:
    path = storage.local_path(MANIFEST_KEY) if hasattr(storage, "local_path") else None
    if not path or not path.is_file():
        report.warn("seed manifest not found; hash verification skipped")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.error(f"seed manifest is unreadable ({exc})")
        return {}
    objects = payload.get("objects")
    if not isinstance(objects, list):
        report.error("seed manifest has no objects array")
        return {}
    if len(objects) != payload.get("count"):
        report.error("seed manifest count does not match its object list")
    return {item["slug"]: item for item in objects if item.get("slug")}


async def validate() -> Report:
    report = Report()
    storage = get_storage()
    local = isinstance(storage, LocalStorage)
    manifest = await load_manifest(storage, report) if local else {}

    async with SessionLocal() as session:
        artworks = list(
            (
                await session.execute(
                    select(Artwork)
                    .where(Artwork.status == ArtworkStatus.PUBLISHED)
                    .options(
                        joinedload(Artwork.license),
                        joinedload(Artwork.category),
                        selectinload(Artwork.tags),
                    )
                    .order_by(Artwork.slug)
                )
            )
            .unique()
            .scalars()
            .all()
        )
        categories = list((await session.execute(select(Category))).scalars().all())
        collections = list(
            (
                await session.execute(
                    select(Collection).options(joinedload(Collection.cover_artwork))
                )
            )
            .unique()
            .scalars()
            .all()
        )

    if not artworks:
        report.error("no published artworks found; run scripts/seed_archive.py first")
        return report

    slugs = set()
    for artwork in artworks:
        label = f"artwork {artwork.slug}"
        slugs.add(artwork.slug)

        if not SLUG_PATTERN.match(artwork.slug):
            report.error(f"{label}: slug is not URL-safe")
        if artwork.slug in manifest:
            manifest[artwork.slug]["_seen"] = True
        elif manifest:
            report.warn(f"{label}: missing from the seed manifest")

        if not artwork.title.strip():
            report.error(f"{label}: title is empty")
        if not (artwork.description or "").strip():
            report.error(f"{label}: description is empty")
        if artwork.published_at is None:
            report.error(f"{label}: published object has no published_at")
        if artwork.license is None:
            report.error(f"{label}: no license attached")
        elif artwork.redistribution_allowed and not artwork.license.redistribution_allowed:
            report.error(f"{label}: redistributed file has a non-redistributable license")
        if not artwork.tags:
            report.warn(f"{label}: no tags")

        if artwork.file_format.lower() not in TEXT_FORMATS | IMAGE_FORMATS:
            report.warn(f"{label}: unusual file format {artwork.file_format!r}")
        if artwork.media_type == MediaType.TEXT and artwork.file_format.lower() not in TEXT_FORMATS:
            report.error(f"{label}: text media type with {artwork.file_format} file")
        if artwork.media_type in {MediaType.IMAGE, MediaType.ANIMATION}:
            if artwork.file_format.lower() not in IMAGE_FORMATS:
                report.warn(f"{label}: image media type with {artwork.file_format} file")

        if not artwork.preview_key:
            report.error(f"{label}: no preview key")
        elif local:
            full_size = None
            for variant in ("thumb", "card", "full"):
                key = f"{artwork.preview_key}-{variant}.webp"
                path = storage.local_path(key)
                if not path.is_file():
                    report.error(f"{label}: preview variant missing ({variant})")
                    continue
                size = check_webp(path, f"{label} preview {variant}", report)
                if variant == "full":
                    full_size = size
            if (
                full_size
                and artwork.width
                and artwork.height
                and artwork.media_type != MediaType.TEXT
            ):
                source_ratio = artwork.width / artwork.height
                preview_ratio = full_size[0] / full_size[1]
                if abs(preview_ratio - source_ratio) / source_ratio > 0.02:
                    report.warn(
                        f"{label}: preview aspect {full_size[0]}x{full_size[1]} does not match "
                        f"the recorded original {artwork.width}x{artwork.height}"
                    )

        if artwork.redistribution_allowed:
            if not artwork.original_key:
                report.error(f"{label}: redistributable object has no original key")
                continue
            key_format = format_from_key(artwork.original_key)
            if key_format != artwork.file_format.lower().replace("jpeg", "jpg"):
                report.error(
                    f"{label}: file_format {artwork.file_format!r} does not match "
                    f"original key {artwork.original_key!r}"
                )
            if not local:
                continue
            path = storage.local_path(artwork.original_key)
            if not path.is_file():
                report.error(f"{label}: original file is missing")
                continue
            data = path.read_bytes()
            if not data:
                report.error(f"{label}: original file is empty")
            if artwork.file_size != len(data):
                report.error(
                    f"{label}: recorded file_size {artwork.file_size} but file has {len(data)} bytes"
                )

            if artwork.file_format.lower() in TEXT_FORMATS:
                check_text(data, label, report)
            else:
                actual = check_image_dimensions(data, label, report)
                if actual and artwork.width and artwork.height:
                    if actual != (artwork.width, artwork.height):
                        report.error(
                            f"{label}: recorded dimensions {artwork.width}x{artwork.height} "
                            f"but file is {actual[0]}x{actual[1]}"
                        )
                elif actual:
                    report.warn(f"{label}: database is missing width/height")

            entry = manifest.get(artwork.slug)
            if entry and entry.get("sha256"):
                digest = hashlib.sha256(data).hexdigest()
                if digest != entry["sha256"]:
                    report.error(f"{label}: sha256 does not match the seed manifest")
        else:
            if artwork.original_key:
                report.error(f"{label}: preview-only object must not store an original")
            if not (artwork.original_source_url or "").startswith(("http://", "https://")):
                report.error(f"{label}: preview-only object needs an http(s) source URL")
            if artwork.download_count != 0:
                report.error(f"{label}: preview-only object has download_count > 0")
            if artwork.license and artwork.license.redistribution_allowed:
                report.error(f"{label}: preview-only object has a redistributable license")

        if artwork.width and artwork.height:
            expected = expected_orientation(artwork.width, artwork.height)
            if artwork.orientation.value != expected:
                report.error(
                    f"{label}: orientation {artwork.orientation.value!r} should be {expected!r}"
                )

    if manifest:
        for slug, entry in manifest.items():
            if slug not in slugs:
                report.error(f"manifest lists {slug}, which is not published in the database")

    for category in categories:
        if not category.cover_image:
            report.warn(f"category {category.slug}: no cover image")
        elif local:
            path = url_to_media_path(category.cover_image)
            if path is None or not path.is_file():
                report.error(f"category {category.slug}: cover image is missing")

    for collection in collections:
        if collection.cover_artwork is None:
            report.warn(f"collection {collection.slug}: no cover artwork")
        elif collection.cover_artwork.slug not in slugs:
            report.error(f"collection {collection.slug}: cover artwork is not published")

    if local:
        report_orphans(report, slugs)

    return report


def url_to_media_path(url: str) -> Path | None:
    base = settings.media_base_url.rstrip("/")
    if not url.startswith(base + "/"):
        return None
    key = url[len(base) + 1 :]
    from app.storage import get_storage

    return get_storage().local_path(key)


def report_orphans(report: Report, slugs: set[str]) -> None:
    from app.storage import get_storage

    storage = get_storage()
    root = storage.local_path("artworks")
    if not root or not root.is_dir():
        return
    on_disk = {path.name for path in root.iterdir() if path.is_dir()}
    for slug in sorted(on_disk - slugs):
        report.warn(f"media directory for {slug} has no published artwork")
    for slug in sorted(slugs - on_disk):
        report.warn(f"artwork {slug} has no media directory")


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--json", action="store_true", help="print a machine-readable report")
    args = parser.parse_args()

    report = await validate()
    failed = bool(report.errors) or (args.strict and bool(report.warnings))

    if args.json:
        print(
            json.dumps(
                {
                    "ok": not failed,
                    "errors": report.errors,
                    "warnings": report.warnings,
                },
                indent=2,
            )
        )
    else:
        for message in report.errors:
            print(f"ERROR   {message}")
        for message in report.warnings:
            print(f"WARNING {message}")
        status = "FAILED" if failed else "OK"
        print(
            f"{status}: {len(report.errors)} error(s), {len(report.warnings)} warning(s)"
        )

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
