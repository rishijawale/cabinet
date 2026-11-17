# API

Base URL: `http://localhost:8000/api/v1`

Interactive documentation is available at `/api/docs` and the OpenAPI document at `/api/openapi.json`.

## Conventions

### Success envelope

Single objects:

```json
{
  "data": { "...": "..." },
  "meta": {}
}
```

Lists are wrapped in the same envelope, with pagination in `meta`:

```json
{
  "data": [],
  "meta": { "page": 1, "limit": 24, "total": 100, "pages": 5 }
}
```

`pages` is `0` when no records match.

### Error envelope

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid values.",
    "details": [{ "field": "query.page", "message": "Input should be greater than or equal to 1" }]
  }
}
```

`details` is omitted unless it adds information.

### Common status codes

| Status | Meaning |
| --- | --- |
| 200 | Success |
| 400 | Invalid filter or sort value |
| 401 | Authentication required or token invalid |
| 403 | Account suspended |
| 404 | Object or route not found |
| 422 | Parameter validation failed |
| 429 | Download rate limit exceeded |
| 500 | Unhandled server error |

### Authentication

Auth is **opt-in and config-driven**. When `SUPABASE_URL` is empty, authenticated
endpoints respond `401 AUTH_REQUIRED` and the archive behaves anonymously.
When it is set, requests present a Supabase access token:

```
Authorization: Bearer <supabase-access-token>
```

Tokens are verified against the project's published JWKS (ES256/RS256), with
`aud: "authenticated"` and `iss: {SUPABASE_URL}/auth/v1`. The first valid token
provisions (or email-links) a local account keyed by the token's `sub` claim.

### Pagination

`page` is 1-based and defaults to `1`. `limit` defaults to `24` and is capped at `48`. Values outside those bounds return `422 VALIDATION_ERROR`.

## Endpoints

### Health

```
GET /health
GET /api/v1/health
```

The versioned endpoint verifies the database connection.

```json
{
  "data": { "status": "ok", "environment": "development", "version": "0.1.0" },
  "meta": {}
}
```

### List categories

```
GET /api/v1/categories
```

Returns active categories ordered by `display_order`, each with a published artwork count and a cover image URL.

```json
{
  "data": [
    {
      "id": "…",
      "name": "ASCII",
      "slug": "ascii",
      "description": "Images made from characters…",
      "cover_image": "http://localhost:8000/media/artworks/quiet-observer/preview-card.webp",
      "display_order": 1,
      "artwork_count": 40
    }
  ],
  "meta": {}
}
```

### List and search artworks

```
GET /api/v1/artworks
```

| Parameter | Type | Notes |
| --- | --- | --- |
| `q` | string, max 140 | Full-text search across title, description, creator and tags, with a title substring fallback. |
| `category` | string | Category slug, for example `ascii`. |
| `tags` | string[] | Tag slugs. Repeat the parameter or use a comma-separated value. |
| `format` | string[] | File formats such as `txt`, `png` or `jpg`. Repeat or comma-separate. |
| `media_type` | enum[] | `image`, `video`, `animation` or `text`. |
| `orientation` | enum[] | `landscape`, `portrait` or `square`. |
| `sort` | enum | `recent`, `oldest`, `popular` or `relevance`. Defaults to `relevance` when `q` is set, otherwise `recent`. |
| `page` | integer | 1-based, default `1`. |
| `limit` | integer | Default `24`, maximum `48`. |

Invalid enum values return `400 INVALID_FILTER`; an unknown sort returns `400 INVALID_SORT`.

Example:

```bash
curl "http://localhost:8000/api/v1/artworks?q=terminal&category=ascii&format=txt&sort=recent&page=1"
```

Each item is an artwork card:

```json
{
  "id": "…",
  "slug": "quiet-observer",
  "title": "Quiet Observer",
  "category": { "id": "…", "name": "ASCII", "slug": "ascii" },
  "creator": {
    "id": "…",
    "username": "ivo-sato",
    "display_name": "Ivo Sato",
    "avatar_url": null,
    "external_name": null,
    "anonymous": false
  },
  "media_type": "text",
  "file_format": "txt",
  "width": 96,
  "height": 40,
  "orientation": "landscape",
  "preview": {
    "thumb": "http://localhost:8000/media/artworks/quiet-observer/preview-thumb.webp",
    "card": "http://localhost:8000/media/artworks/quiet-observer/preview-card.webp",
    "full": "http://localhost:8000/media/artworks/quiet-observer/preview-full.webp",
    "alt": "Quiet Observer — ASCII artwork by Ivo Sato"
  },
  "license": {
    "id": "…",
    "name": "CC0 1.0 Universal",
    "identifier": "CC0-1.0",
    "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
    "attribution_required": false,
    "commercial_use_allowed": true,
    "modification_allowed": true,
    "redistribution_allowed": true
  },
  "redistributable": true,
  "downloadable": true,
  "featured": false,
  "published_at": "2026-02-03T12:00:00Z",
  "tags": [{ "name": "Monochrome", "slug": "monochrome" }]
}
```

### Random artwork

```
GET /api/v1/artworks/random
```

Returns one published artwork card. This route is registered before `/artworks/{slug}` so the literal path is not treated as a slug. If the archive is empty it returns `404 NO_ARTWORKS`.

### Artwork detail

```
GET /api/v1/artworks/{slug}
```

Returns an artwork card plus:

| Field | Notes |
| --- | --- |
| `description` | Editorial description. May end with a preview-only note. |
| `original_source_url` | Creator or source record. |
| `rights_notes` | Human-readable rights context. |
| `file_size` | Original size in bytes. |
| `text_url` | Public URL of the original text file for redistributable text art; otherwise `null`. |
| `view_count` | Total views including this request. |
| `download_count` | Total successful downloads. |
| `created_at`, `updated_at` | Timestamps. |
| `related` | Up to four random published objects from the same category. |

Fetching detail increments the view counter atomically.

```bash
curl http://localhost:8000/api/v1/artworks/quiet-observer
```

Missing or unpublished slugs return `404 ARTWORK_NOT_FOUND`.

### Download

```
GET /api/v1/artworks/{slug}/download
```

Rate limit: 30 requests per minute per client.

Redistributable object:

```json
{
  "data": {
    "downloadable": true,
    "url": "http://localhost:8000/media/artworks/quiet-observer/original.txt",
    "expires_at": "2026-11-17T12:05:00+00:00",
    "file_format": "txt",
    "file_size": 3840,
    "license": { "...": "..." }
  },
  "meta": {}
}
```

The URL is a public path with local storage and a signed URL with S3/R2. A successful request increments `download_count` and inserts a `downloads` row.

Preview-only object:

```json
{
  "data": {
    "downloadable": false,
    "external_url": "https://example.org/archive/silent-field",
    "reason": "Cabinet can preview this object but is not permitted to redistribute the original file.",
    "license": { "...": "..." }
  },
  "meta": {}
}
```

No file is served and no counter changes. If the database permits redistribution but the stored file is missing, the endpoint returns `404 ASSET_MISSING`.

### List collections

```
GET /api/v1/collections
```

Returns public collections ordered by featured status and creation date. Each item includes a cover preview set, curator and artwork count.

```json
{
  "data": [
    {
      "id": "…",
      "slug": "tiny-worlds",
      "title": "Tiny Worlds",
      "description": "Entire places compressed into a few hundred pixels…",
      "cover": {
        "thumb": "…",
        "card": "…",
        "full": "…",
        "alt": "… — Pixel Art artwork by Mara Ellis"
      },
      "cover_artwork_slug": "tiny-orchard",
      "curator": { "…": "…" },
      "artwork_count": 16,
      "is_featured": false
    }
  ],
  "meta": {}
}
```

### Collection detail

```
GET /api/v1/collections/{slug}
```

Returns the collection card plus:

- `artworks` — published objects in display order, as artwork cards.
- `created_at` — collection creation timestamp.

Missing or non-public collections return `404 COLLECTION_NOT_FOUND`.

### Current account

```
GET /api/v1/auth/me
```

Requires a bearer token. Verifies it, provisions the account if this is the
first time the token's identity has been seen, and returns the profile.

```json
{
  "data": {
    "id": "…",
    "username": "collector-example",
    "display_name": "Collector Example",
    "email": "collector@example.com",
    "avatar_url": null,
    "status": "active",
    "created_at": "2026-11-17T12:00:00Z"
  },
  "meta": {}
}
```

Error cases: `401 AUTH_REQUIRED` (no token, or auth disabled), `401
TOKEN_INVALID` (bad signature, expired, wrong audience/issuer or unknown key),
`403 ACCOUNT_SUSPENDED`.

### List favorites

```
GET /api/v1/favorites
```

Requires a bearer token. Returns the caller's saved objects, newest first, as
artwork cards.

```json
{
  "data": [{ "…artwork card": "…" }],
  "meta": { "total": 1 }
}
```

### Save an object

```
POST /api/v1/favorites/{slug}
```

Requires a bearer token. Idempotent — saving twice leaves the state unchanged.

```json
{
  "data": { "saved": true, "already_saved": false, "favorite_count": 8 },
  "meta": {}
}
```

`favorite_count` feeds the popularity score and is updated atomically with the
favorite row. Unknown slugs return `404 ARTWORK_NOT_FOUND`.

### Remove a favorite

```
DELETE /api/v1/favorites/{slug}
```

Requires a bearer token. Also idempotent; the counter never goes below zero.

```json
{
  "data": { "saved": false, "favorite_count": 7 },
  "meta": {}
}
```

## Media files

With `STORAGE_BACKEND=local`, files are served from:

```
http://localhost:8000/media/artworks/{slug}/preview-thumb.webp
http://localhost:8000/media/artworks/{slug}/preview-card.webp
http://localhost:8000/media/artworks/{slug}/preview-full.webp
http://localhost:8000/media/artworks/{slug}/original.{ext}
```

The `original.*` path only exists for redistributable objects. Client applications should use `preview.*`, `text_url` or the download endpoint rather than constructing original URLs.

## Caching

Public GETs are cacheable but currently served with framework defaults. The frontend caches list and detail responses in memory for 60 seconds and keeps previous page data while a new request loads. Production deployment should add explicit cache headers and a CDN policy for media.
