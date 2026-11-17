# Cabinet

A curated digital archive for ASCII art, wallpapers, pixel art and the visual culture that grew up around computers. This repository contains the full Archive MVP: a FastAPI + PostgreSQL API, a React + Vite frontend, and 100 procedurally generated seed objects — 97 released under CC0 or CC-BY, and three preview-only records that exercise the non-redistribution path.

The design goal is a small, deliberate archive rather than an infinite feed: every object has a maker, a license and a reason to be here.

## What is included

- **Archive** — browse, search and filter 100 objects across ASCII, wallpapers and pixel art.
- **Object pages** — full preview, character-grid rendering for text art, metadata, license panel, related objects, share and save.
- **Collections** — five curated exhibitions with featured and standard layouts.
- **Downloads** — signed/redirected originals where redistribution is permitted; explicit preview-only handling where it is not.
- **Editorial pages** — About, submission guidelines, licensing, privacy and terms (draft copy).
- **SEO** — per-route titles, descriptions, canonical URLs and JSON-LD, plus a generated sitemap and robots file.
- **Local saved objects** — browser-only saves until accounts ship.
- **Accessibility and theming** — keyboard-friendly controls, reduced-motion support, light and dark themes.
- **Performance** — route-level code splitting with cached vendor chunks, so a first visit ships only the layout and the page it needs.

Deferred to later milestones: authentication (Supabase), favourites that sync across devices, submissions, moderation/admin tools, the Studio, reporting, user-created collections, R2 storage, FFmpeg derivatives and production deployment.

## Stack

| Layer | Choice |
| --- | --- |
| API | Python 3.11, FastAPI, SQLAlchemy 2 (async), asyncpg, Alembic |
| Database | PostgreSQL 16 with full-text search and `pg_trgm` |
| Frontend | React 19, Vite 6, TypeScript, React Router, TanStack Query |
| Styling | Tailwind CSS v4, Instrument Serif / Inter / JetBrains Mono |
| Media | Local filesystem in development; S3-compatible interface ready for Cloudflare R2 |
| Tests | pytest + httpx (API), Vitest (frontend utilities) |

## Repository layout

```
backend/            FastAPI app, models, repositories, Alembic migration
frontend/           React application and Vite build
scripts/            Seed pipeline, asset validator, sitemap generator
docs/               Architecture, API and licensing notes
docker-compose.yml  PostgreSQL for local development
.env.example        Backend environment template
```

## Quick start

### Prerequisites

- Python 3.11+
- Node.js 20+ and npm
- PostgreSQL 16, either through Docker or a local install

### 1. Start PostgreSQL

With Docker:

```bash
docker compose up -d db
```

Without Docker, create a database and user matching the defaults:

```
database: cabinet
user:     cabinet
password: cabinet
port:     5432
```

If your instance uses different credentials, set `DATABASE_URL` in `backend/.env`.

### 2. Configure and install the API

From the repository root:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r backend\requirements.txt -r backend\requirements-dev.txt
Copy-Item .env.example backend\.env
```

On macOS or Linux use `python3 -m venv .venv`, `.venv/bin/python`, and `cp` instead.

Run the migration and seed the archive from the repository root:

```powershell
Push-Location backend
..\.venv\Scripts\python -m alembic upgrade head
Pop-Location
.venv\Scripts\python scripts\seed_archive.py
```

The seed writes 100 objects and their WebP previews into `backend/media`, plus `backend/media/seed-manifest.json`.

### 3. Run the API

From `backend/`:

```powershell
..\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

- API root: `http://localhost:8000/api/v1`
- Health: `http://localhost:8000/api/v1/health`
- OpenAPI docs: `http://localhost:8000/api/docs`
- Media: `http://localhost:8000/media/...`

### 4. Run the frontend

From `frontend/`:

```powershell
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`. Use `localhost` rather than `127.0.0.1` so the default CORS configuration matches.

## Scripts

| Command | Purpose |
| --- | --- |
| `.venv\Scripts\python scripts\seed_archive.py` | Generate media and insert seed objects, users, collections and tags. Safe to re-run; existing objects are skipped. |
| `.venv\Scripts\python scripts\validate_assets.py` | Check every object, preview, original, dimension, hash and license against the database. Add `--strict` to fail on warnings. |
| `.venv\Scripts\python scripts\generate_sitemap.py --base-url https://example.com` | Write `frontend/public/sitemap.xml` and `robots.txt` from the database. Defaults to `PUBLIC_SITE_URL`. The committed files use the placeholder origin `https://cabinet.example`; regenerate them with the real origin before deploying. |

## Tests and checks

Backend tests run against the seeded development database. Each test is wrapped in a transaction that is rolled back, so counters do not leak.

```powershell
Push-Location backend
..\.venv\Scripts\python -m pytest
Pop-Location
```

Frontend:

```powershell
Push-Location frontend
npm run typecheck
npm test
npm run build
Pop-Location
```

## Configuration

Backend settings live in `backend/.env` and are documented in `.env.example`:

- `DATABASE_URL` — async SQLAlchemy URL (`postgresql+asyncpg://...`).
- `ALLOWED_ORIGINS` — comma-separated frontend origins.
- `PUBLIC_SITE_URL` — canonical origin used in metadata and the sitemap.
- `STORAGE_BACKEND` — `local` or `s3`; `MEDIA_ROOT` and `MEDIA_BASE_URL` apply to local storage.
- `R2_*` — Cloudflare R2 credentials and public base URL when using S3 storage.
- `DOWNLOAD_URL_TTL_SECONDS` — lifetime for signed download URLs.

The frontend reads `VITE_API_BASE_URL` from `frontend/.env`.

## Documentation

- [Architecture](docs/architecture.md) — request flow, data model, storage and frontend structure.
- [API](docs/api.md) — endpoints, query parameters, envelopes and errors.
- [Licensing](docs/licensing.md) — seed licenses, preview-only policy and attribution.

## Licensing of seed content

The 100 objects are procedurally generated for this project and released under CC0-1.0, apart from a small number of CC-BY-4.0 records used to exercise attribution, and three preview-only records that exist to test the non-redistribution path. See [docs/licensing.md](docs/licensing.md). No third-party artwork is scraped or re-hosted.

## Status

The archive milestone is complete and verified locally. Authentication, submissions and the Studio are intentionally not implemented; the pages that reference them explain that they arrive later.
