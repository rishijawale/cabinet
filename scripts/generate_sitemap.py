"""Generate sitemap.xml and robots.txt for the public archive.

Run from the repository root:

    .venv/Scripts/python scripts/generate_sitemap.py --base-url https://cabinet.example

Without --base-url the value of PUBLIC_SITE_URL in backend/.env is used. The
files are written to frontend/public so Vite copies them into the build.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from datetime import date, datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from sqlalchemy import select  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.db import SessionLocal  # noqa: E402
from app.models import Artwork, Category, Collection  # noqa: E402
from app.models.enums import ArtworkStatus  # noqa: E402

STATIC_PAGES = [
    ("/", 1.0, "daily"),
    ("/explore", 0.9, "daily"),
    ("/collections", 0.8, "weekly"),
    ("/about", 0.4, "monthly"),
    ("/guidelines", 0.4, "monthly"),
    ("/licenses", 0.4, "monthly"),
    ("/privacy", 0.2, "yearly"),
    ("/terms", 0.2, "yearly"),
]


def iso_date(value: datetime | date | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date().isoformat()
    return value.isoformat()


def url_entry(
    loc: str,
    *,
    lastmod: str | None = None,
    changefreq: str | None = None,
    priority: float | None = None,
) -> str:
    parts = [f"    <loc>{escape(loc)}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{lastmod}</lastmod>")
    if changefreq:
        parts.append(f"    <changefreq>{changefreq}</changefreq>")
    if priority is not None:
        parts.append(f"    <priority>{priority:.1f}</priority>")
    body = "\n".join(parts)
    return f"  <url>\n{body}\n  </url>"


async def collect_urls(base_url: str) -> list[str]:
    base = base_url.rstrip("/")
    today = date.today().isoformat()
    entries: list[str] = []

    for path, priority, changefreq in STATIC_PAGES:
        entries.append(
            url_entry(
                f"{base}{path}",
                lastmod=today,
                changefreq=changefreq,
                priority=priority,
            )
        )

    async with SessionLocal() as session:
        categories = list(
            (
                await session.execute(
                    select(Category)
                    .where(Category.active.is_(True))
                    .order_by(Category.display_order.asc(), Category.name.asc())
                )
            )
            .scalars()
            .all()
        )
        collections = list(
            (
                await session.execute(
                    select(Collection)
                    .where(Collection.is_public.is_(True))
                    .order_by(Collection.created_at.desc())
                )
            )
            .scalars()
            .all()
        )
        artworks = list(
            (
                await session.execute(
                    select(Artwork)
                    .where(
                        Artwork.status == ArtworkStatus.PUBLISHED,
                        Artwork.published_at.is_not(None),
                    )
                    .order_by(Artwork.published_at.desc())
                )
            )
            .scalars()
            .all()
        )

    for category in categories:
        entries.append(
            url_entry(
                f"{base}/explore/{category.slug}",
                lastmod=today,
                changefreq="weekly",
                priority=0.7,
            )
        )

    for collection in collections:
        entries.append(
            url_entry(
                f"{base}/collections/{collection.slug}",
                lastmod=iso_date(collection.updated_at),
                changefreq="monthly",
                priority=0.7,
            )
        )

    for artwork in artworks:
        entries.append(
            url_entry(
                f"{base}/object/{artwork.slug}",
                lastmod=iso_date(artwork.updated_at or artwork.published_at),
                changefreq="monthly",
                priority=0.6,
            )
        )

    return entries


def render_sitemap(entries: list[str]) -> str:
    joined = "\n".join(entries)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{joined}\n"
        "</urlset>\n"
    )


def render_robots(base_url: str) -> str:
    base = base_url.rstrip("/")
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /saved\n"
        "Disallow: /studio\n"
        "Disallow: /submit\n"
        f"\nSitemap: {base}/sitemap.xml\n"
    )


async def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=settings.public_site_url,
        help="Canonical public origin (defaults to PUBLIC_SITE_URL)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "frontend" / "public",
        help="Directory for sitemap.xml and robots.txt",
    )
    args = parser.parse_args()

    base_url = args.base_url.strip()
    if not base_url.startswith(("http://", "https://")):
        parser.error("--base-url must start with http:// or https://")
    base_url = base_url.rstrip("/")

    entries = await collect_urls(base_url)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    sitemap_path = output_dir / "sitemap.xml"
    robots_path = output_dir / "robots.txt"
    sitemap_path.write_text(render_sitemap(entries), encoding="utf-8", newline="\n")
    robots_path.write_text(render_robots(base_url), encoding="utf-8", newline="\n")

    print(f"Wrote {len(entries)} URLs to {sitemap_path.relative_to(ROOT)}")
    print(f"Wrote {robots_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
