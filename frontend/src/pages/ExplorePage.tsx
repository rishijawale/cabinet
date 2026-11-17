import { SlidersHorizontal, X } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";

import { ArtworkGrid } from "../components/gallery/ArtworkGrid";
import { Pagination } from "../components/gallery/Pagination";
import { SearchField } from "../components/ui/SearchField";
import { Select } from "../components/ui/Select";
import { Skeleton } from "../components/ui/Skeleton";
import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { cn } from "../lib/cn";
import { useArtworks, useCategories } from "../services/queries";
import type { ArtworkQuery } from "../types/api";

const SORT_OPTIONS = [
  { value: "recent", label: "Recently added" },
  { value: "popular", label: "Most viewed" },
  { value: "oldest", label: "Oldest first" },
] as const;

const MEDIA_OPTIONS = [
  { value: "", label: "All media" },
  { value: "image", label: "Images" },
  { value: "text", label: "Text" },
  { value: "animation", label: "Animation" },
];

const FORMAT_OPTIONS = [
  { value: "", label: "Any format" },
  { value: "png", label: "PNG" },
  { value: "jpg", label: "JPG" },
  { value: "txt", label: "TXT" },
  { value: "webp", label: "WEBP" },
];

const ORIENTATION_OPTIONS = [
  { value: "", label: "Any shape" },
  { value: "landscape", label: "Landscape" },
  { value: "portrait", label: "Portrait" },
  { value: "square", label: "Square" },
];

const LIMIT = 24;

export function ExplorePage() {
  const params = useParams<{ category?: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const categories = useCategories();

  const urlQuery = searchParams.get("q") ?? "";
  const [query, setQuery] = useState(urlQuery);
  const debounced = useDebouncedValue(query, 300);

  const page = Math.max(1, Number(searchParams.get("page") ?? "1") || 1);
  const sort = (searchParams.get("sort") ?? (urlQuery ? "relevance" : "recent")) as ArtworkQuery["sort"];
  const format = searchParams.get("format") ?? "";
  const mediaType = searchParams.get("media_type") ?? "";
  const orientation = searchParams.get("orientation") ?? "";
  const tag = searchParams.get("tag") ?? "";
  const category = params.category ?? searchParams.get("category") ?? "";

  const activeCategory = categories.data?.find((item) => item.slug === category);

  const filters: ArtworkQuery = useMemo(
    () => ({
      q: debounced.trim() || undefined,
      category: category || undefined,
      sort,
      format: format ? [format] : undefined,
      media_type: mediaType ? [mediaType] : undefined,
      orientation: orientation ? [orientation] : undefined,
      tags: tag ? [tag] : undefined,
      page,
      limit: LIMIT,
    }),
    [debounced, category, sort, format, mediaType, orientation, tag, page],
  );

  const artworks = useArtworks(filters);

  useDocumentMeta({
    title: activeCategory ? `${activeCategory.name} — Explore` : "Explore the archive",
    description:
      activeCategory?.description ??
      "Browse ASCII art, wallpapers, pixel art and visual experiments from the Cabinet archive.",
    canonicalPath: activeCategory ? `/explore/${activeCategory.slug}` : "/explore",
  });

  // Keep the URL in sync with the debounced search term.
  useEffect(() => {
    const current = searchParams.get("q") ?? "";
    if (debounced.trim() === current) return;
    const next = new URLSearchParams(searchParams);
    if (debounced.trim()) next.set("q", debounced.trim());
    else next.delete("q");
    next.delete("page");
    setSearchParams(next, { replace: true });
  }, [debounced, searchParams, setSearchParams]);

  function update(key: string, value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    next.delete("page");
    setSearchParams(next);
  }

  function changePage(value: number) {
    const next = new URLSearchParams(searchParams);
    if (value > 1) next.set("page", String(value));
    else next.delete("page");
    setSearchParams(next);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  const total = artworks.data?.meta.total ?? 0;
  const pages = artworks.data?.meta.pages ?? 0;
  const activeFilterCount = [format, mediaType, orientation, tag].filter(Boolean).length;

  return (
    <div className="container-page py-10 sm:py-14">
      <header className="border-b border-line pb-8">
        <p className="label">Browse the archive</p>
        <div className="mt-4 flex flex-wrap items-end justify-between gap-6">
          <h1 className="display max-w-2xl text-4xl leading-[0.95] text-ink sm:text-6xl">
            {activeCategory ? activeCategory.name : "Every object, considered."}
          </h1>
          <p className="max-w-sm text-sm leading-6 text-muted">
            {activeCategory?.description ??
              "The full archive: character grids, quiet wallpapers, small worlds and the occasional experiment."}
          </p>
        </div>
      </header>

      <div className="relative z-30 -mx-5 mb-8 border-b border-line bg-canvas/95 px-5 backdrop-blur sm:-mx-8 sm:px-8 lg:sticky lg:top-16 lg:-mx-12 lg:px-12">
        <div className="grid gap-5 py-5 lg:grid-cols-12 lg:items-end">
          <div className="lg:col-span-5">
            <SearchField
              value={query}
              onChange={setQuery}
              placeholder="Search titles, tags, makers…"
            />
          </div>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 lg:col-span-7">
            <Select
              label="Sort"
              value={sort}
              onChange={(event) => update("sort", event.target.value)}
            >
              {SORT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
            <Select
              label="Media"
              value={mediaType}
              onChange={(event) => update("media_type", event.target.value)}
            >
              {MEDIA_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
            <Select
              label="Format"
              value={format}
              onChange={(event) => update("format", event.target.value)}
            >
              {FORMAT_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
            <Select
              label="Shape"
              value={orientation}
              onChange={(event) => update("orientation", event.target.value)}
            >
              {ORIENTATION_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
          </div>
        </div>

        <div className="no-scrollbar -mx-5 flex items-center gap-1 overflow-x-auto px-5 pb-3 sm:-mx-8 sm:px-8">
          <CategoryTab to="/explore" active={!category}>
            All objects
          </CategoryTab>
          {categories.data?.map((item) => (
            <CategoryTab
              key={item.slug}
              to={`/explore/${item.slug}`}
              active={category === item.slug}
            >
              {item.name}
            </CategoryTab>
          ))}
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 pb-7">
        <p className="flex items-center gap-2 text-[12px] text-muted">
          <SlidersHorizontal className="h-3.5 w-3.5" />
          {artworks.isLoading
            ? "Loading the archive…"
            : `${total} ${total === 1 ? "object" : "objects"}`}
          {debounced.trim() && (
            <>
              <span aria-hidden="true">·</span>
              <span className="text-ink">“{debounced.trim()}”</span>
            </>
          )}
        </p>
        <div className="flex flex-wrap items-center gap-2">
          {tag && (
            <FilterChip label={`Tag: ${tag}`} onRemove={() => update("tag", "")} />
          )}
          {format && <FilterChip label={format.toUpperCase()} onRemove={() => update("format", "")} />}
          {mediaType && (
            <FilterChip label={mediaType} onRemove={() => update("media_type", "")} />
          )}
          {orientation && (
            <FilterChip label={orientation} onRemove={() => update("orientation", "")} />
          )}
          {activeFilterCount > 0 && (
            <button
              type="button"
              onClick={() => setSearchParams(queryParamsWithout(searchParams, ["format", "media_type", "orientation", "tag"]))}
              className="text-[11px] text-muted underline decoration-line-strong underline-offset-2 hover:text-ink"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {artworks.isError ? (
        <div className="border border-line bg-surface p-10 text-center">
          <p className="display text-2xl text-ink">The archive could not be reached.</p>
          <p className="mt-2 text-sm text-muted">Check your connection and try again.</p>
        </div>
      ) : artworks.isLoading ? (
        <div className="grid grid-cols-2 gap-x-4 gap-y-9 sm:gap-x-6 sm:gap-y-12 md:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, index) => (
            <div key={index}>
              <Skeleton className="aspect-[4/3] w-full" />
              <Skeleton className="mt-3 h-3 w-24" />
              <Skeleton className="mt-2 h-4 w-40" />
            </div>
          ))}
        </div>
      ) : artworks.data && artworks.data.data.length > 0 ? (
        <>
          <ArtworkGrid artworks={artworks.data.data} />
          <Pagination page={page} pages={pages} onChange={changePage} />
        </>
      ) : (
        <div className="border border-dashed border-line-strong px-6 py-24 text-center">
          <p className="display text-3xl text-ink">Nothing in this corner of the archive.</p>
          <p className="mx-auto mt-3 max-w-md text-sm leading-6 text-muted">
            No objects match these filters. Try a broader search, or clear the filters and start
            again.
          </p>
          <button
            type="button"
            onClick={() => setSearchParams(new URLSearchParams())}
            className="mt-6 border border-line-strong px-4 py-2 text-[12px] font-medium text-ink transition-colors hover:border-ink"
          >
            Clear everything
          </button>
        </div>
      )}
    </div>
  );
}

function CategoryTab({
  to,
  active,
  children,
}: {
  to: string;
  active: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link
      to={to}
      className={cn(
        "shrink-0 border-b-2 px-3 py-2 text-[12px] font-medium transition-colors",
        active
          ? "border-accent text-ink"
          : "border-transparent text-muted hover:text-ink",
      )}
    >
      {children}
    </Link>
  );
}

function FilterChip({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span className="inline-flex items-center gap-1.5 border border-line bg-surface px-2 py-1 text-[10px] uppercase tracking-[0.12em] text-muted">
      {label}
      <button type="button" onClick={onRemove} aria-label={`Remove ${label} filter`}>
        <X className="h-3 w-3 transition-colors hover:text-ink" />
      </button>
    </span>
  );
}

function queryParamsWithout(params: URLSearchParams, keys: string[]): URLSearchParams {
  const next = new URLSearchParams(params);
  for (const key of keys) next.delete(key);
  next.delete("page");
  return next;
}
