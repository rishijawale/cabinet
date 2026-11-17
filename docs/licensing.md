# Licensing

Cabinet keeps licensing per object rather than per site. The license panel on an object page is the authoritative summary for that file; this document explains the policy behind it.

## Seed content

All 100 seed objects are procedurally generated for this project by `scripts/asset_factory.py`. Nothing is scraped, re-hosted from a gallery, or sampled from third-party work. Some records intentionally use a preview-only license and a placeholder source URL (`https://example.org/archive/...`) to exercise the non-redistribution path; those records are for development and must be replaced with a real source before any public launch.

| License | Objects | Redistributable | Attribution required |
| --- | ---: | --- | --- |
| CC0 1.0 Universal (`CC0-1.0`) | 86 | Yes | No |
| Creative Commons Attribution 4.0 (`CC-BY-4.0`) | 11 | Yes | Yes |
| All rights reserved — link only (`ARR-LINK-ONLY`) | 3 | No | Yes |

The three preview-only objects are `distant-chorus`, `silent-field` and `small-satellite`.

## How the database records rights

Every artwork references a row in `licenses` with four booleans:

- `attribution_required`
- `commercial_use_allowed`
- `modification_allowed`
- `redistribution_allowed`

The artwork also stores:

- `redistribution_allowed` — whether Cabinet itself may serve the original file.
- `rights_notes` — a human-readable explanation shown near the license panel.
- `original_source_url` — the creator or source record.
- `original_key` — the stored original, present only when Cabinet may redistribute it.

A database check constraint enforces that a redistributable artwork has an original file. The API additionally requires both `redistribution_allowed` and `original_key` before serving a download, so preview-only records cannot leak a file through a bad flag combination.

## What the licenses mean here

### CC0 1.0 Universal

The creator has waived rights as far as the law allows. You may use, modify and redistribute the work, including commercially, without asking permission. Attribution is not required, though Cabinet still records and displays the maker.

### CC-BY 4.0

You may use, modify and redistribute the work, including commercially, provided you credit the creator, link to the license where practical, and indicate whether you changed the work. A reasonable credit:

> “Quiet Observer” by Ivo Sato, CC BY 4.0, via Cabinet. Changes: cropped.

### All rights reserved — link only

Cabinet shows a preview for reference only. The original file is not served and remains with its creator or source. Reuse requires permission from the rights holder. The object page says “Preview only”, disables the download button and links to the source record.

## Downloads

- A successful download grants exactly the rights in the object's license. It does not transfer ownership.
- Successful downloads increment a counter and insert a `downloads` audit row.
- Preview-only objects return a structured response with `downloadable: false`, a reason and `external_url`. They never increment the counter.
- Signed download URLs expire after `DOWNLOAD_URL_TTL_SECONDS` when using S3/R2. Local development serves public media paths.

## Submission policy

Public submissions are not open yet, but the rules the archive will enforce are already documented in the product:

1. Submit only work you made or work you have explicit permission to archive.
2. “Found on the internet” and reposted art with a caption credit are not acceptable sources.
3. Record the license at the object level. If you are the creator, choose CC0, CC-BY, or preview-only with the original hosted elsewhere.
4. Keep originals lossless where possible; pixel art should keep its native resolution and text art should be plain UTF-8.

## Corrections and takedowns

Creators can request correction or removal at any time. Until the reporting tool ships, use the contact route described on the About page. The intended workflow is:

1. Verify the request against the source record.
2. Unpublish the object or correct its metadata and license.
3. Record the action in `moderation_actions` so the archive can explain what changed.
4. Keep the audit trail even when the object is removed.

The schema already includes `reports` and `moderation_actions`; no public endpoints are exposed in this milestone.

## Verification

`scripts/validate_assets.py` checks that:

- redistributable objects have original files and matching sizes/dimensions/hashes;
- preview-only objects store no original, have a source URL and report zero downloads;
- a redistributable file does not point at a non-redistributable license;
- media referenced by categories and collections exists.

Run it with `--strict` to treat warnings as failures. This is a development guard, not a legal review.

## Not legal advice

This document describes the project's implementation and intent. It is not legal advice. Before operating publicly, have the privacy notice, terms and licensing policy reviewed, and replace placeholder source URLs in the seed with real records.
