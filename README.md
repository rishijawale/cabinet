# Cabinet

[![CI](https://github.com/rishijawale/cabinet/actions/workflows/ci.yml/badge.svg)](https://github.com/rishijawale/cabinet/actions/workflows/ci.yml)

A curated digital archive for ASCII art, wallpapers, pixel art and the visual culture that grew up around computers. This repository contains the full Archive MVP: a FastAPI + PostgreSQL API, a React + Vite frontend, and 100 procedurally generated seed objects — 97 released under CC0 or CC-BY, and three preview-only records that exercise the non-redistribution path.

The design goal is a small, deliberate archive rather than an infinite feed: every object has a maker, a license and a reason to be here.

## What is included

- **Archive** — browse, search and filter 100 objects across ASCII, wallpapers and pixel art.
- **Object pages** — full preview, character-grid rendering for text art, metadata, license panel, related objects, share and save.
- **Collections** — five curated exhibitions with featured and standard layouts.
- **Downloads** — signed/redirected originals where redistribution is permitted; explicit preview-only handling where it is not.
- **Accounts and favorites** — optional, config-driven Supabase Auth: passwordless sign-in links, server-side favorites with atomic counters, and a one-time merge of browser-saved objects into the account at first sign-in. With no Supabase configuration the app behaves exactly as before.
- **Editorial pages** — About, submission guidelines, licensing, privacy and terms (draft copy).
- **SEO** — per-route titles, descriptions, canonical URLs and JSON-LD, plus a generated sitemap and robots file.
- **Local saved objects** — pre-sign-in saves live in the browser and migrate to the account on sign-in.
- **Accessibility and theming** — keyboard-friendly controls, reduced-motion support, light and dark themes.
- **Performance** — route-level code splitting with cached vendor chunks, so a first visit ships only the layout and the page it needs; supabase-js loads only when auth is enabled.
- **Cache policy** — every API and media response carries an explicit `Cache-Control`: browsable archive GETs cache for a minute and media for a week in production, while auth, favorites, downloads, mutations and errors are never cached.

Deferred to later milestones: submissions, moderation/admin tools, the Studio, reporting, user-created collections, R2 storage and FFmpeg derivatives. Production deployment is documented as a reference configuration ([Production deployment](#production-deployment)) rather than an automated pipeline.

## Stack

| Layer | Choice |
| --- | --- |
| API | Python 3.11, FastAPI, SQLAlchemy 2 (async), asyncpg, Alembic, PyJWT |
| Database | PostgreSQL 16 with full-text search and `pg_trgm` |
| Frontend | React 19, Vite 6, TypeScript, React Router, TanStack Query |
| Auth | Supabase Auth (JWT via JWKS), optional at runtime |
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
frontend/.env.example  Frontend environment template (API base URL, Supabase)
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

### Continuous integration

`.github/workflows/ci.yml` runs on every push to `main` and on pull requests:

- **API and database** — ruff, Alembic migrations against a PostgreSQL 16 service, the full seed pipeline, `validate_assets.py --strict`, then pytest.
- **Web client** — `npm ci`, TypeScript typecheck, Vitest, and a production Vite build.

## Configuration

Backend settings live in `backend/.env` and are documented in `.env.example`:

- `DATABASE_URL` — async SQLAlchemy URL (`postgresql+asyncpg://...`).
- `ALLOWED_ORIGINS` — comma-separated frontend origins.
- `PUBLIC_SITE_URL` — canonical origin used in metadata and the sitemap.
- `STORAGE_BACKEND` — `local` or `s3`; `MEDIA_ROOT` and `MEDIA_BASE_URL` apply to local storage.
- `R2_*` — Cloudflare R2 credentials and public base URL when using S3 storage.
- `DOWNLOAD_URL_TTL_SECONDS` — lifetime for signed download URLs.
- `API_CACHE_MAX_AGE` and `MEDIA_CACHE_MAX_AGE` — cache windows for browsable archive GETs (default 60 s) and media (default one week). They apply in production only; development serves `no-store`/`no-cache` regardless.
- `SUPABASE_URL` — leave empty to disable auth; set it to enable the auth and favorites endpoints. `SUPABASE_JWKS_URL`, `SUPABASE_AUDIENCE`, `SUPABASE_ISSUER` and `SUPABASE_LEEWAY_SECONDS` have sensible defaults derived from the project URL.

The frontend reads `VITE_API_BASE_URL` plus the optional `VITE_SUPABASE_URL` / `VITE_SUPABASE_ANON_KEY` from `frontend/.env`. Both Supabase values must be set for sign-in to appear; see [Enabling accounts](#enabling-accounts).

## Enabling accounts

Auth is off by default and needs no credentials to build or run. To turn it on:

1. Create a project at [supabase.com](https://supabase.com). No database integration is needed — Cabinet uses Supabase Auth only.
2. In **Authentication → URL Configuration**, add your frontend origin (for development `http://localhost:5173`) to the allowed redirect URLs.
3. In **Authentication → Sign In / Providers**, enable **Email** with "Confirm email" off so passwordless magic links work immediately.
4. Set the environment variables:

```bash
# backend/.env
SUPABASE_URL=https://your-project.supabase.co

# frontend/.env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-public-key
```

5. Restart the API and rebuild or restart the frontend. `/login` now sends magic links, favorites move server-side, and the saved page follows the account between devices. JWTs are verified against the project's published JWKS; the anon key is a public identifier and safe to ship in the browser.

## Production deployment

`deploy/nginx.conf` is a reference configuration for the intended shape: nginx serves the built frontend and reverse-proxies the API and media to uvicorn.

1. Configure the backend for production in `backend/.env`: `ENVIRONMENT=production`, real origins in `ALLOWED_ORIGINS`, the public site URL in `PUBLIC_SITE_URL`, and — ideally — `STORAGE_BACKEND=s3` with `R2_*` credentials instead of local disk. Startup logs a warning for each of these that still looks like a development leftover.
2. Build the frontend with `VITE_API_BASE_URL` pointed at the same origin's API path (for example `https://your-origin/api/v1`), plus the Supabase variables if accounts are enabled.
3. Regenerate the sitemap and robots file with the real origin: `python scripts/generate_sitemap.py --base-url https://your-origin`.
4. Run the API under a process manager (systemd, a container, etc.):

   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2 \
     --proxy-headers --forwarded-allow-ips="127.0.0.1"
   ```

   `--proxy-headers` matters: rate limiting and CORS otherwise see the proxy address instead of the real client IP from `X-Forwarded-For`.
5. Point `deploy/nginx.conf` at `frontend/dist`, replace `server_name`, and reload. `/assets/` is cached `immutable` for a year, `index.html` and the SPA fallback always revalidate, and `/api/` plus `/media/` are proxied with the cache headers the API sets itself.
6. Terminate TLS in front of nginx (`certbot --nginx` or a load balancer) and redirect `:80` to `:443`.

With `ENVIRONMENT=production` the API's cache policy switches on: browsable archive GETs are `public, max-age=60`, media is `public, max-age=604800`, and downloads, auth, favorites, mutations and errors stay `no-store`. Both windows are configurable via `API_CACHE_MAX_AGE` and `MEDIA_CACHE_MAX_AGE`; the full policy table is in [docs/api.md](docs/api.md).

## Documentation

- [Architecture](docs/architecture.md) — request flow, data model, storage and frontend structure.
- [API](docs/api.md) — endpoints, query parameters, envelopes and errors.
- [Licensing](docs/licensing.md) — seed licenses, preview-only policy and attribution.

## Licensing of seed content

The 100 objects are procedurally generated for this project and released under CC0-1.0, apart from a small number of CC-BY-4.0 records used to exercise attribution, and three preview-only records that exist to test the non-redistribution path. See [docs/licensing.md](docs/licensing.md). No third-party artwork is scraped or re-hosted.

## Status

The archive milestone is complete and verified locally, and optional Supabase Auth is implemented (config-driven, disabled until credentials are provided). Submissions and the Studio are intentionally not implemented; the pages that reference them explain that they arrive later.
