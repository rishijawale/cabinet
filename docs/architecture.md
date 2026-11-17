# Architecture

Cabinet is a two-application monorepo: a JSON API backed by PostgreSQL, and a single-page React client. The archive milestone deliberately keeps the system small enough to run on one machine while leaving clear seams for accounts, submissions and remote storage.

## System overview

```
Browser
  │
  │  React 19 + Vite (localhost:5173)
  │  · routes, React Query, local saved objects
  ▼
FastAPI (localhost:8000)
  │  /api/v1  JSON envelope
  │  /media   static previews and originals in development
  ▼
PostgreSQL 16
  · artworks, taxonomy, collections, users, engagement
  · full-text search vectors maintained by triggers
```

The frontend and API are separate origins in development. CORS origins are controlled by `ALLOWED_ORIGINS`; media URLs are absolute and derived from `MEDIA_BASE_URL`.

## Backend

### Layers

| Package | Responsibility |
| --- | --- |
| `app/api/v1` | HTTP routes, query parsing and validation, rate limits. |
| `app/repositories` | SQLAlchemy queries and counter writes. Routes do not build SQL. |
| `app/services` | Pydantic serializers that turn ORM objects into API shapes. |
| `app/models` | SQLAlchemy mappings and Postgres enums. |
| `app/schemas` | Response models (`ArtworkCard`, `ArtworkDetail`, etc.). |
| `app/core` | Settings, database session, pagination, errors, responses, rate limiting. |
| `app/storage` | Storage protocol with local filesystem and S3/R2 implementations. |

### Request flow

1. FastAPI resolves `SessionDep` into one async SQLAlchemy session per request.
2. The route parses and validates query parameters. Invalid enum filters and sort keys raise `AppError`, which is rendered as the standard error envelope.
3. A repository function builds a `select()` with eager loading (`selectinload` for collections, `joinedload` for creator/license), applies filters, sorting, offset and limit, and runs a separate count query.
4. Serializers convert ORM objects to Pydantic models. Media URLs come from the configured storage backend.
5. Routes wrap payloads in `ok()` or `paginated()`, producing `{ "data": ..., "meta": ... }`.

Detail requests intentionally differ from list requests: the payload is serialized before the view counter is incremented, then the fresh counter is written into the payload. This keeps the displayed number inclusive of the current view without a second query.

### Data model

Core archive:

- `artworks` — slug, title, description, category, creator or external creator, anonymity flag, preview key, original key, media type, format, dimensions, orientation, license, redistribution flag, rights notes, status, featured flag, publication date, denormalized counters and `search_vector`.
- `categories` — display name, slug, description, cover image URL, display order and active flag.
- `tags` — unique name and slug, many-to-many with artworks.
- `licenses` — identifier plus explicit booleans for attribution, commercial use, modification and redistribution.
- `users` — archive creators and curators. The schema supports email, role and suspension, but no auth flow is exposed in this milestone.
- `collections`, `collection_items` — curated exhibitions with a cover artwork, curator, ordering and public/featured flags.
- `downloads` — one row per successful download, used for auditing and future analytics.
- `favorites`, `submissions`, `reports`, `moderation_actions` — schema present for later milestones; endpoints are not exposed.

Important constraints:

- A published artwork must have a publication date and some form of attribution (user, external name or the anonymous flag).
- A redistributable artwork must have an `original_key`.
- File size cannot be negative.
- The search vector and title trigram index are backed by Postgres `pg_trgm` and trigger functions created in the initial migration.

### Search, filtering and sorting

- Search uses `websearch_to_tsquery('simple', q)` against a weighted vector: title (A), description (B), external creator and tags (C). Title also falls back to a case-insensitive substring match.
- Filters can be combined: category slug, tag slugs, file formats, media types and orientation.
- Sort options are `recent`, `oldest`, `popular` and `relevance`. `relevance` only applies when a query is present; otherwise recent is used.
- Popularity is a denormalized score: `download_count * 3 + favorite_count * 2 + view_count`. This avoids expensive aggregate joins on every listing.
- Pagination is 1-based. The default page size is 24; the maximum is 48. `pages` is zero for an empty result.

### Downloads

`GET /artworks/{slug}/download` has two paths:

1. **Redistributable** — the storage backend creates a signed URL (a public URL in local development), the download counter is incremented, and a `downloads` row is written. The frontend immediately triggers a browser download.
2. **Preview only** — no file is served. The response explains why and includes the creator's source URL when one exists. No counter is incremented.

The check is based on both `redistribution_allowed` and the presence of `original_key`; the database constraint prevents the two from disagreeing for published objects. The endpoint is rate-limited to 30 requests per minute per client.

### Errors

Controlled failures use a single shape:

```json
{
  "error": {
    "code": "ARTWORK_NOT_FOUND",
    "message": "The requested artwork could not be found.",
    "details": []
  }
}
```

Validation errors are `422 VALIDATION_ERROR` with field-level details. Unexpected exceptions are logged and returned as `500 INTERNAL_ERROR` without leaking internals.

### Storage

`StorageBackend` defines `public_url`, `signed_url`, `save`, `exists` and `local_path`. Development uses `LocalStorage`, which serves files from `/media`; production can use `S3Storage` for Cloudflare R2 without changing callers. Preview variants are fixed-name WebP files: `-thumb`, `-card` and `-full`.

## Frontend

### Structure

```
src/
  components/      layout, gallery, collections, UI primitives
  hooks/           theme, auth, saved objects, document metadata, debounce
  lib/             formatting and class-name helpers
  pages/           one module per route
  services/api/    fetch wrapper, archive and account endpoints
  services/        React Query keys and hooks; Supabase client
  styles/          Tailwind v4 entry and design tokens
  types/           API response types
```

### Routes

| Path | Page |
| --- | --- |
| `/` | Home: hero, featured exhibition, categories, random object |
| `/explore`, `/explore/:category` | Searchable, filterable gallery |
| `/object/:slug` | Object detail with download, save and share |
| `/collections`, `/collections/:slug` | Exhibitions index and detail |
| `/saved` | Saved objects (account or local storage) |
| `/login` | Sign-in page (magic link) |
| `/about`, `/guidelines`, `/licenses`, `/privacy`, `/terms` | Editorial and legal pages |
| `/studio`, `/submit` | Coming-soon pages |
| `*` | Not-found page |

All routes render inside `RootLayout`, which provides the header, mobile navigation, footer and theme handling.

### Data fetching

TanStack Query owns server state. Query keys are centralized in `services/queries.ts`; list queries keep previous data while the next page or filter loads. Artwork detail queries use the slug. After a successful download the detail cache is updated in place so the counter changes immediately. Favorites live under a single `["favorites"]` key, refreshed after every save/remove.

Explore state lives in the URL: `q`, `category`, `sort`, `format`, `media_type`, `orientation`, `tag` and `page`. Search input is debounced and written back with `replace`, so filtering is deep-linkable and survives refreshes.

### Authentication

`AuthProvider` wraps the router. It is config-driven: with both `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` set, `@supabase/supabase-js` is dynamically imported (so it never loads when auth is off), sessions persist in local storage and the access token is attached to every archive API request by the fetch wrapper. `/auth/me` provisions the account server-side on first sign-in.

Sign-in is a passwordless magic link sent from `/login` with `emailRedirectTo` set to the same page. On the first signed-in session, favorites saved in the browser are merged to the server once and the local store is cleared; from then on the Saved page, saved badge and object save button all read server favorites, with optimistic updates on save/remove. When auth is disabled or the visitor is signed out, saving behaves exactly as before (browser-local).

### Local state

- Theme is stored under `cabinet-theme` and applied before React mounts by a small inline script, avoiding a flash.
- Saved objects are stored under `cabinet-saved` with enough metadata to render the saved page without extra requests. This store is the pre-sign-in buffer: once signed in its contents migrate to the account.

### SEO

`useDocumentMeta` updates the document title, description, canonical link, Open Graph/Twitter tags and optional JSON-LD per route. Object pages emit `VisualArtwork` structured data; collection pages emit `CollectionPage` with `hasPart`. The sitemap and robots file are generated from the database by `scripts/generate_sitemap.py`. The checked-in copies point at the placeholder origin `https://cabinet.example` so a production build never ships `localhost` URLs; regenerate them with the real origin as part of deployment. Because this is a client-rendered SPA, crawlers that do not execute JavaScript see the shell metadata from `index.html`; richer static rendering or prerendering belongs to the deployment milestone.

## Verification

- Backend: pytest with httpx ASGI transport. Tests run against the seeded database inside a transaction that is rolled back, and use a dedicated NullPool engine so async connections stay on the test's event loop. Auth tests verify real ES256-signed tokens; only the JWKS transport is stubbed.
- Frontend: TypeScript typecheck, Vitest unit tests for formatting helpers, production Vite build.
- Integration: headless browser checks covered every route, search/filter/pagination, save flow, mobile navigation, downloads and both themes during development.
- Assets: `scripts/validate_assets.py` verifies previews, originals, dimensions, UTF-8 text, seed hashes, license coherence and orphaned media.

## Deliberate trade-offs

- **Auth is optional at runtime.** Accounts ride on Supabase and switch on with two frontend env vars plus one backend var; with auth off, favorites endpoints return 401 and the frontend keeps browser-local saves. Submissions, reports and moderation still have no write endpoints.
- **Counters are denormalized.** Seeded counts are illustrative; favorites and downloads keep them correct with atomic `UPDATE ... RETURNING` statements.
- **Local media in development.** The storage interface is stable, but R2 is not exercised by tests.
- **Route-level code splitting.** Every page is a separate chunk loaded behind a `Suspense` boundary inside the layout, and React, React Query and Framer Motion are cached as stable vendor chunks. The initial JavaScript payload is roughly 120 kB gzipped instead of one 540 kB bundle, and supabase-js only loads when auth is enabled.
- **Draft legal copy.** Privacy and terms are explicitly marked as drafts and are release blockers before public submissions.
