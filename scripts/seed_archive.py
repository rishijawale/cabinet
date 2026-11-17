"""Seed Cabinet with 100 original CC0/CC-BY objects, curators and exhibitions.

Run from the repository root:

    .venv/Scripts/python scripts/seed_archive.py
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from sqlalchemy import select  # noqa: E402

from app.core.db import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    Artwork,
    Category,
    Collection,
    CollectionItem,
    License,
    Tag,
    User,
)
from app.models.enums import (  # noqa: E402
    ArtworkStatus,
    MediaType,
    Orientation,
    UserRole,
)
from app.storage import get_storage  # noqa: E402
from scripts.asset_factory import (  # noqa: E402
    ASCII_TITLES,
    PIXEL_TITLES,
    WALLPAPER_TITLES,
    generate_archive,
    slugify,
)

NOW = datetime(2026, 11, 10, 12, 0, tzinfo=UTC)
EXTERNAL_ONLY = {8, 47, 86}
EXTERNAL_CREATORS = ["Studio Kō", "N. Ardent", "Vela Archives"]
EXTERNAL_DESCRIPTIONS = {
    "ascii": (
        "A dense field of glyphs that resolves into a shape only when you step back. "
        "Preview only — the original file remains with its creator."
    ),
    "pixel-art": (
        "A tiny scene drawn on a strict grid, shown here at preview resolution. "
        "Preview only — the original file remains with its creator."
    ),
    "wallpapers": (
        "A quiet abstract field composed for wide screens. "
        "Preview only — the original file remains with its creator."
    ),
}
FEATURED = {1, 33, 55, 70, 87, 96}

CREATORS = [
    (
        "mara-ellis",
        "Mara Ellis",
        "Curator, pixel artist and collector of small worlds. Interested in the edges where old hardware meets new ideas.",
        UserRole.USER,
    ),
    (
        "ivo-sato",
        "Ivo Sato",
        "Works with text, terminals and generative systems. Believes a character grid is a perfectly good canvas.",
        UserRole.USER,
    ),
    (
        "nadia-brenner",
        "Nadia Brenner",
        "Designer and archivist. Makes quiet images for loud screens.",
        UserRole.USER,
    ),
    (
        "theo-vance",
        "Theo Vance",
        "Interested in early internet aesthetics, dithering and the dignity of a 16-colour palette.",
        UserRole.USER,
    ),
    (
        "lin-qiao",
        "Lin Qiao",
        "Generative artist. Writes small programs that draw landscapes nobody asked for.",
        UserRole.USER,
    ),
    (
        "archive-ops",
        "Archive Ops",
        "Maintains the Cabinet collection and its metadata.",
        UserRole.ADMIN,
    ),
]

USERS = {username: (display, bio, role) for username, display, bio, role in CREATORS}

CATEGORIES = [
    (
        "ascii",
        "ASCII",
        "Images made from characters. A discipline of restraint, spacing and the willingness to let a letter do the work of a pixel.",
        "ascii",
        1,
    ),
    (
        "wallpapers",
        "Wallpapers",
        "Quiet abstract fields and minimal compositions, sized for the screen you look at every day.",
        "wallpaper",
        2,
    ),
    (
        "pixel-art",
        "Pixel Art",
        "Small grids, limited palettes and hard edges. Work that treats every pixel as a decision.",
        "pixel-art",
        3,
    ),
]

LICENSES = [
    {
        "name": "CC0 1.0 Universal",
        "identifier": "CC0-1.0",
        "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
        "attribution_required": False,
        "commercial_use_allowed": True,
        "modification_allowed": True,
        "redistribution_allowed": True,
    },
    {
        "name": "Creative Commons Attribution 4.0",
        "identifier": "CC-BY-4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution_required": True,
        "commercial_use_allowed": True,
        "modification_allowed": True,
        "redistribution_allowed": True,
    },
    {
        "name": "All rights reserved — link only",
        "identifier": "ARR-LINK-ONLY",
        "license_url": None,
        "attribution_required": True,
        "commercial_use_allowed": False,
        "modification_allowed": False,
        "redistribution_allowed": False,
    },
]

COLLECTIONS = [
    {
        "slug": "the-terminal-age",
        "title": "The Terminal Age",
        "description": (
            "Before the screen was a window, it was a page of text. This exhibition gathers work made "
            "inside that constraint: character grids, teletype rhythms and images that only exist "
            "because a machine agreed to print them. Step back from the monitor and the noise becomes a picture."
        ),
        "curator": "ivo-sato",
        "artworks": ASCII_TITLES[0:16],
        "featured": True,
    },
    {
        "slug": "digital-silence",
        "title": "Digital Silence",
        "description": (
            "A room with the volume turned down. Soft gradients, layered grain and compositions that "
            "leave most of the screen alone. These are wallpapers designed to disappear behind your work."
        ),
        "curator": "nadia-brenner",
        "artworks": WALLPAPER_TITLES[0:14],
        "featured": False,
    },
    {
        "slug": "tiny-worlds",
        "title": "Tiny Worlds",
        "description": (
            "Entire places compressed into a few hundred pixels. A village, a creature, a horizon — "
            "each one built from a palette small enough to count on two hands."
        ),
        "curator": "mara-ellis",
        "artworks": PIXEL_TITLES[0:16],
        "featured": False,
    },
    {
        "slug": "early-internet",
        "title": "Early Internet",
        "description": (
            "The visual grammar of a slower network: hard edges, default palettes, and the sense that "
            "someone made this at home because they wanted to see if they could."
        ),
        "curator": "theo-vance",
        "artworks": ASCII_TITLES[18:26] + PIXEL_TITLES[8:18],
        "featured": False,
    },
    {
        "slug": "monochrome-experiments",
        "title": "Monochrome Experiments",
        "description": (
            "What survives when colour is removed? Structure, density and light. A study of work that "
            "commits to a single tone and finds more than enough to say."
        ),
        "curator": "lin-qiao",
        "artworks": ASCII_TITLES[8:16] + WALLPAPER_TITLES[14:22],
        "featured": False,
    },
]


async def upsert_user(session, username: str) -> User:
    existing = (
        await session.execute(select(User).where(User.username == username))
    ).scalar_one_or_none()
    if existing:
        return existing
    display, bio, role = USERS[username]
    user = User(
        email=f"{username}@cabinet.local",
        username=username,
        display_name=display,
        bio=bio,
        role=role,
        avatar_url=None,
    )
    session.add(user)
    await session.flush()
    return user


async def main() -> None:
    storage = get_storage()
    users = {}
    async with SessionLocal() as session:
        for username in USERS:
            users[username] = await upsert_user(session, username)

        category_map: dict[str, Category] = {}
        for slug, name, description, _cover_slug, order in CATEGORIES:
            category = (
                await session.execute(select(Category).where(Category.slug == slug))
            ).scalar_one_or_none()
            if category is None:
                category = Category(
                    slug=slug,
                    name=name,
                    description=description,
                    display_order=order,
                    active=True,
                )
                session.add(category)
                await session.flush()
            else:
                category.description = description
                category.name = name
                category.display_order = order
            category_map[slug] = category

        license_map: dict[str, License] = {}
        for payload in LICENSES:
            license_row = (
                await session.execute(
                    select(License).where(License.identifier == payload["identifier"])
                )
            ).scalar_one_or_none()
            if license_row is None:
                license_row = License(**payload)
                session.add(license_row)
                await session.flush()
            license_map[payload["identifier"]] = license_row

        tag_map: dict[str, Tag] = {}

        async def tag_for(name: str) -> Tag:
            slug = slugify(name)
            if slug in tag_map:
                return tag_map[slug]
            existing = (
                await session.execute(select(Tag).where(Tag.slug == slug))
            ).scalar_one_or_none()
            if existing is None:
                existing = Tag(name=name, slug=slug)
                session.add(existing)
                await session.flush()
            tag_map[slug] = existing
            return existing

        print("Generating original artwork (this takes a minute)...")
        pieces = generate_archive()

        creator_usernames = [
            "mara-ellis",
            "ivo-sato",
            "nadia-brenner",
            "theo-vance",
            "lin-qiao",
        ]
        manifest: list[dict] = []
        created = 0

        for index, piece in enumerate(pieces):
            existing = (
                await session.execute(select(Artwork).where(Artwork.slug == piece.slug))
            ).scalar_one_or_none()
            if existing is not None:
                continue

            external_only = index in EXTERNAL_ONLY
            anonymous = index % 23 == 5 and not external_only
            license_identifier = (
                "ARR-LINK-ONLY"
                if external_only
                else ("CC-BY-4.0" if index % 9 == 4 else "CC0-1.0")
            )

            creator_id = None
            external_creator_name = None
            if external_only:
                external_creator_name = EXTERNAL_CREATORS[
                    sorted(EXTERNAL_ONLY).index(index)
                ]
            elif anonymous:
                external_creator_name = None
            else:
                creator_id = users[creator_usernames[index % len(creator_usernames)]].id

            preview_key = f"artworks/{piece.slug}/preview"
            original_key = None
            if piece.original is not None and not external_only:
                original_key = f"artworks/{piece.slug}/original.{piece.original_ext}"

            for variant, data in piece.previews.items():
                storage.save(
                    f"{preview_key}-{variant}.webp", data, "image/webp"
                )
            if original_key and piece.original is not None:
                mime = "text/plain" if piece.original_ext == "txt" else (
                    "image/png" if piece.original_ext == "png" else "image/jpeg"
                )
                storage.save(original_key, piece.original, mime)

            published_at = NOW - timedelta(days=(index * 7) % 420, hours=index % 24)
            source_url = (
                f"https://example.org/archive/{piece.slug}" if external_only else None
            )

            artwork = Artwork(
                slug=piece.slug,
                title=piece.title,
                description=(
                    EXTERNAL_DESCRIPTIONS[piece.category]
                    if external_only
                    else piece.description
                ),
                category_id=category_map[piece.category].id,
                creator_id=creator_id,
                external_creator_name=external_creator_name,
                creator_anonymous=anonymous,
                original_source_url=source_url,
                preview_key=preview_key,
                original_key=original_key,
                media_type=MediaType(piece.media_type),
                file_format=piece.file_format,
                file_size=len(piece.original) if piece.original else 0,
                width=piece.width,
                height=piece.height,
                orientation=Orientation(piece.orientation),
                license_id=license_map[license_identifier].id,
                redistribution_allowed=not external_only,
                rights_notes=(
                    "Preview shown for reference. The original file is hosted by the source and is not redistributed by Cabinet."
                    if external_only
                    else "Created for Cabinet. Redistribution permitted under the stated license."
                ),
                status=ArtworkStatus.PUBLISHED,
                featured=index in FEATURED,
                published_at=published_at,
                view_count=(index * 37) % 240 + 15,
                download_count=0 if external_only else (index * 13) % 60,
                favorite_count=(index * 7) % 40,
            )
            artwork.tags = [await tag_for(name) for name in dict.fromkeys(piece.tags)]
            session.add(artwork)
            await session.flush()
            created += 1

            manifest.append(
                {
                    "slug": piece.slug,
                    "title": piece.title,
                    "category": piece.category,
                    "license": license_identifier,
                    "redistributable": not external_only,
                    "original": original_key,
                    "preview_key": preview_key,
                    "sha256": hashlib.sha256(piece.original).hexdigest()
                    if piece.original
                    else None,
                    "style": piece.style,
                }
            )

        await session.flush()

        # Category covers use a published object from that category.
        for _slug, category in category_map.items():
            if category.cover_image:
                continue
            cover = (
                await session.execute(
                    select(Artwork)
                    .where(
                        Artwork.category_id == category.id,
                        Artwork.status == ArtworkStatus.PUBLISHED,
                    )
                    .order_by(Artwork.featured.desc(), Artwork.published_at.desc())
                )
            ).scalars().first()
            if cover and cover.preview_key:
                category.cover_image = storage.public_url(
                    f"{cover.preview_key}-card.webp"
                )

        slug_to_artwork = {
            row.slug: row
            for row in (
                await session.execute(
                    select(Artwork).where(Artwork.status == ArtworkStatus.PUBLISHED)
                )
            )
            .scalars()
            .all()
        }

        for definition in COLLECTIONS:
            collection = (
                await session.execute(
                    select(Collection).where(Collection.slug == definition["slug"])
                )
            ).scalar_one_or_none()
            if collection is None:
                collection = Collection(
                    slug=definition["slug"],
                    title=definition["title"],
                    description=definition["description"],
                    curator_id=users[definition["curator"]].id,
                    is_featured=definition["featured"],
                    is_public=True,
                )
                session.add(collection)
                await session.flush()

            existing_items = int(
                (
                    await session.execute(
                        select(CollectionItem).where(
                            CollectionItem.collection_id == collection.id
                        )
                    )
                )
                .scalars()
                .all()
                .__len__()
            )
            if existing_items:
                continue

            order = 0
            first_slug = None
            for title in definition["artworks"]:
                artwork = slug_to_artwork.get(slugify(title))
                if artwork is None:
                    continue
                if first_slug is None:
                    first_slug = artwork.slug
                session.add(
                    CollectionItem(
                        collection_id=collection.id,
                        artwork_id=artwork.id,
                        display_order=order,
                    )
                )
                order += 1
                if order >= 18:
                    break

            if first_slug:
                cover = slug_to_artwork[first_slug]
                collection.cover_artwork_id = cover.id

        manifest_payload = {
            "generated_at": NOW.isoformat(),
            "count": len(manifest),
            "objects": manifest,
        }
        storage.save(
            "seed-manifest.json",
            json.dumps(manifest_payload, indent=2, ensure_ascii=False).encode("utf-8"),
            "application/json",
        )

        await session.commit()

        totals = {
            "categories": len(category_map),
            "licenses": len(license_map),
            "artworks_created": created,
            "artworks_total": len(
                (
                    await session.execute(
                        select(Artwork).where(Artwork.status == ArtworkStatus.PUBLISHED)
                    )
                )
                .scalars()
                .all()
            ),
            "collections": len(
                (await session.execute(select(Collection))).scalars().all()
            ),
            "tags": len(
                (await session.execute(select(Tag))).scalars().all()
            ),
        }

    print(json.dumps(totals, indent=2))
    print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
