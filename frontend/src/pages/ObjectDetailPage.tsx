import {
  ArrowLeft,
  ArrowUpRight,
  Bookmark,
  BookmarkCheck,
  Check,
  Download,
  ExternalLink,
  Link2,
  Loader2,
} from "lucide-react";
import { useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ArtworkGrid } from "../components/gallery/ArtworkGrid";
import { Badge } from "../components/ui/Badge";
import { Button, buttonStyles } from "../components/ui/Button";
import { Skeleton } from "../components/ui/Skeleton";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { useSaved } from "../hooks/useSaved";
import { cn } from "../lib/cn";
import {
  downloadName,
  formatBytes,
  formatDate,
  formatDimensions,
  formatMediaType,
  licenseSummary,
} from "../lib/format";
import { requestDownload } from "../services/api/archive";
import { queryKeys, useArtwork } from "../services/queries";
import type { ArtworkDetail, DownloadInfo } from "../types/api";

type DownloadState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "ready"; info: DownloadInfo }
  | { status: "error"; message: string };

export function ObjectDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const artwork = useArtwork(slug);
  const { isSaved, toggle } = useSaved();
  const queryClient = useQueryClient();
  const [download, setDownload] = useState<DownloadState>({ status: "idle" });
  const [copied, setCopied] = useState(false);

  const data = artwork.data;

  useDocumentMeta({
    title: data ? `${data.title} — ${data.creator.display_name}` : "Object",
    description: data?.description ?? undefined,
    image: data?.preview.full,
    canonicalPath: data ? `/object/${data.slug}` : undefined,
    type: "article",
    jsonLd: data
      ? {
          "@context": "https://schema.org",
          "@type": "VisualArtwork",
          name: data.title,
          description: data.description ?? undefined,
          image: data.preview.full,
          datePublished: data.published_at ?? undefined,
          creator: { "@type": "Person", name: data.creator.display_name },
          license:
            data.license?.license_url ??
            "https://creativecommons.org/publicdomain/zero/1.0/",
          url: `${window.location.origin}/object/${data.slug}`,
        }
      : undefined,
  });

  async function handleDownload() {
    if (!data) return;
    setDownload({ status: "loading" });
    try {
      const info = await requestDownload(data.slug);
      setDownload({ status: "ready", info });
      if (info.downloadable && info.url) {
        queryClient.setQueryData<ArtworkDetail>(queryKeys.artwork(data.slug), (current) =>
          current ? { ...current, download_count: current.download_count + 1 } : current,
        );
        const anchor = document.createElement("a");
        anchor.href = info.url;
        anchor.download = downloadName(data);
        anchor.target = "_blank";
        anchor.rel = "noopener";
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
      }
    } catch (error) {
      setDownload({
        status: "error",
        message: error instanceof Error ? error.message : "The download could not be prepared.",
      });
    }
  }

  async function handleShare() {
    if (!data) return;
    const url = `${window.location.origin}/object/${data.slug}`;
    try {
      if (navigator.share) {
        await navigator.share({ title: data.title, text: data.preview.alt, url });
        return;
      }
      await navigator.clipboard.writeText(url);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2200);
    } catch {
      // Share sheet dismissed: nothing to report.
    }
  }

  if (artwork.isLoading) return <ObjectSkeleton />;

  if (artwork.isError || !data) {
    return (
      <div className="container-page py-28 text-center">
        <p className="label">404 — Object not found</p>
        <h1 className="display mt-5 text-4xl text-ink sm:text-5xl">
          This object is not in the archive.
        </h1>
        <p className="mx-auto mt-4 max-w-md text-sm leading-6 text-muted">
          It may have been moved, removed by its creator, or the link may be incorrect.
        </p>
        <Link to="/explore" className={buttonStyles({ className: "mt-8" })}>
          Back to explore
        </Link>
      </div>
    );
  }

  const saved = isSaved(data.slug);

  return (
    <article className="container-page py-8 sm:py-12">
      <nav aria-label="Breadcrumb" className="flex flex-wrap items-center gap-2 text-[11px] text-muted">
        <Link to="/explore" className="inline-flex items-center gap-1.5 hover:text-ink">
          <ArrowLeft className="h-3 w-3" /> Archive
        </Link>
        <span aria-hidden="true">/</span>
        <Link to={`/explore/${data.category.slug}`} className="hover:text-ink">
          {data.category.name}
        </Link>
        <span aria-hidden="true">/</span>
        <span className="truncate text-ink">{data.title}</span>
      </nav>

      <div className="mt-8 grid gap-10 lg:grid-cols-12 lg:gap-12">
        <div className="min-w-0 lg:col-span-8">
          <div className="border border-line bg-surface p-2 sm:p-3">
            {data.media_type === "text" && data.text_url ? (
              <AsciiPreview url={data.text_url} alt={data.preview.alt} />
            ) : (
              <img
                src={data.preview.full}
                alt={data.preview.alt}
                className="max-h-[78vh] w-full object-contain"
              />
            )}
          </div>

          <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
            <p className="label-tight">
              {formatDimensions(data)} · {data.file_format.toUpperCase()}
              {data.file_size ? ` · ${formatBytes(data.file_size)}` : ""}
            </p>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleShare}
                className="inline-flex h-9 items-center gap-2 border border-line px-3 text-[12px] text-muted transition-colors hover:border-ink hover:text-ink"
              >
                {copied ? <Check className="h-3.5 w-3.5" /> : <Link2 className="h-3.5 w-3.5" />}
                {copied ? "Link copied" : "Share"}
              </button>
              <button
                type="button"
                onClick={() => toggle(data)}
                aria-pressed={saved}
                className={cn(
                  "inline-flex h-9 items-center gap-2 border px-3 text-[12px] transition-colors",
                  saved
                    ? "border-ink bg-ink text-canvas"
                    : "border-line text-muted hover:border-ink hover:text-ink",
                )}
              >
                {saved ? (
                  <BookmarkCheck className="h-3.5 w-3.5" />
                ) : (
                  <Bookmark className="h-3.5 w-3.5" />
                )}
                {saved ? "Saved" : "Save"}
              </button>
            </div>
          </div>

          {data.media_type === "text" && (
            <p className="mt-6 border-l-2 border-accent pl-4 text-[12px] leading-6 text-muted">
              This object is drawn with characters. Its preview is rendered from the original text
              file at full width; resize the window to see it reflow.
            </p>
          )}

          <section className="mt-14 border-t border-line pt-8">
            <div className="flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="label">More from {data.category.name}</p>
                <h2 className="display mt-3 text-3xl text-ink">Related objects</h2>
              </div>
              <Link
                to={`/explore/${data.category.slug}`}
                className="inline-flex items-center gap-2 text-[12px] font-medium text-muted hover:text-ink"
              >
                See the collection
                <ArrowUpRight className="h-3.5 w-3.5" />
              </Link>
            </div>
            <ArtworkGrid artworks={data.related} columns={3} className="mt-8" />
          </section>
        </div>

        <aside className="lg:col-span-4">
          <div className="lg:sticky lg:top-24">
            <Badge>{data.category.name}</Badge>
            <h1 className="display mt-4 text-4xl leading-[0.98] text-ink sm:text-5xl">
              {data.title}
            </h1>

            <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
              <span className="text-ink">
                {data.creator.anonymous ? (
                  "Anonymous"
                ) : data.creator.username ? (
                  <span>{data.creator.display_name}</span>
                ) : (
                  <span>{data.creator.display_name}</span>
                )}
              </span>
              <span aria-hidden="true">·</span>
              <span>{formatDate(data.published_at)}</span>
            </div>

            {data.description && (
              <div className="prose-editorial mt-6">
                <p>{data.description}</p>
              </div>
            )}

            <div className="mt-7 space-y-3">
              {data.downloadable ? (
                <Button
                  onClick={handleDownload}
                  disabled={download.status === "loading"}
                  className="w-full"
                  size="lg"
                >
                  {download.status === "loading" ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4" />
                  )}
                  Download original
                  <span className="ml-auto font-mono text-[11px] opacity-70">
                    {data.file_format.toUpperCase()}
                  </span>
                </Button>
              ) : (
                <div className="border border-line bg-surface p-4">
                  <p className="text-[12px] font-medium text-ink">Preview only</p>
                  <p className="mt-1.5 text-[12px] leading-5 text-muted">
                    Cabinet is not permitted to redistribute this file. The original lives with its
                    creator.
                  </p>
                  {data.original_source_url && (
                    <a
                      href={data.original_source_url}
                      target="_blank"
                      rel="noreferrer noopener"
                      className="mt-3 inline-flex items-center gap-1.5 text-[12px] font-medium text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent"
                    >
                      Visit the source
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  )}
                </div>
              )}

              {download.status === "ready" && !download.info.downloadable && (
                <p className="text-[12px] leading-5 text-muted">
                  {download.info.reason ?? "This object cannot be downloaded."}
                </p>
              )}
              {download.status === "error" && (
                <p className="text-[12px] leading-5 text-accent">{download.message}</p>
              )}
            </div>

            <dl className="mt-8 divide-y divide-line border-y border-line text-[12px]">
              <Meta label="Format" value={`${data.file_format.toUpperCase()}`} />
              <Meta label="Dimensions" value={formatDimensions(data)} />
              <Meta label="Media" value={formatMediaType(data.media_type)} />
              <Meta label="File size" value={formatBytes(data.file_size)} />
              <Meta label="Orientation" value={capitalize(data.orientation)} />
              <Meta label="Added" value={formatDate(data.published_at)} />
              <Meta label="Views" value={data.view_count.toLocaleString()} />
              <Meta label="Downloads" value={data.download_count.toLocaleString()} />
            </dl>

            <section className="mt-8 border border-line bg-surface p-5">
              <p className="label-tight">License</p>
              <p className="mt-2 text-sm font-medium text-ink">
                {data.license?.name ?? "Unknown license"}
              </p>
              <p className="mt-2 text-[12px] leading-5 text-muted">
                {licenseSummary(data.license)}
              </p>
              <ul className="mt-4 space-y-1.5 text-[12px] text-muted">
                <Permission allowed={data.license?.commercial_use_allowed} label="Commercial use" />
                <Permission allowed={data.license?.modification_allowed} label="Modification" />
                <Permission allowed={data.license?.redistribution_allowed} label="Redistribution" />
                <Permission allowed={data.license?.attribution_required} label="Attribution required" />
              </ul>
              {data.license?.license_url && (
                <a
                  href={data.license.license_url}
                  target="_blank"
                  rel="noreferrer noopener"
                  className="mt-4 inline-flex items-center gap-1.5 text-[12px] font-medium text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent"
                >
                  Read the license
                  <ArrowUpRight className="h-3 w-3" />
                </a>
              )}
            </section>

            {data.tags.length > 0 && (
              <div className="mt-8">
                <p className="label-tight">Tags</p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {data.tags.map((tag) => (
                    <Link
                      key={tag.slug}
                      to={`/explore?tag=${encodeURIComponent(tag.slug)}`}
                      className="border border-line px-2 py-1 text-[11px] text-muted transition-colors hover:border-ink hover:text-ink"
                    >
                      {tag.name}
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {data.rights_notes && (
              <p className="mt-8 border-t border-line pt-5 text-[11px] leading-5 text-muted">
                {data.rights_notes}
              </p>
            )}

            {data.original_source_url && (
              <a
                href={data.original_source_url}
                target="_blank"
                rel="noreferrer noopener"
                className="mt-5 inline-flex items-center gap-1.5 text-[11px] text-muted hover:text-ink"
              >
                Source record <ExternalLink className="h-3 w-3" />
              </a>
            )}
          </div>
        </aside>
      </div>
    </article>
  );
}

function AsciiPreview({ url, alt }: { url: string; alt: string }) {
  const [text, setText] = useState<string | null>(null);
  const [error, setError] = useState(false);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setText(null);
    setError(false);
    fetch(url)
      .then((response) => {
        if (!response.ok) throw new Error("failed");
        return response.text();
      })
      .then((value) => {
        if (!cancelled) setText(value);
      })
      .catch(() => {
        if (!cancelled) setError(true);
      });
    return () => {
      cancelled = true;
    };
  }, [url]);

  return (
    <div>
      <div
        className={cn(
          "relative overflow-hidden bg-[#11110f]",
          !expanded && "max-h-[70vh]",
        )}
      >
        {error ? (
          <div className="flex min-h-[320px] items-center justify-center p-8 text-center">
            <p className="text-[12px] text-white/60">
              The text rendering could not be loaded. The original file is still available.
            </p>
          </div>
        ) : text === null ? (
          <Skeleton className="min-h-[420px] w-full bg-white/10" />
        ) : (
          <pre
            aria-label={alt}
            className="overflow-x-auto p-4 font-mono text-[6px] leading-[1.05] text-[#ece9e0] sm:p-6 sm:text-[9px] md:text-[11px] lg:text-[12px]"
          >
            {text}
          </pre>
        )}
        {!expanded && text && (
          <div className="pointer-events-none absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-[#11110f] to-transparent" />
        )}
      </div>
      {text && (
        <button
          type="button"
          onClick={() => setExpanded((value) => !value)}
          className="mt-2 text-[11px] text-muted underline decoration-line-strong underline-offset-4 hover:text-ink"
        >
          {expanded ? "Collapse text" : "Show full text"}
        </button>
      )}
    </div>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 py-2.5">
      <dt className="text-muted">{label}</dt>
      <dd className="text-right text-ink">{value}</dd>
    </div>
  );
}

function Permission({ allowed, label }: { allowed: boolean | undefined; label: string }) {
  return (
    <li className="flex items-center gap-2">
      <span
        aria-hidden="true"
        className={cn(
          "inline-block h-1.5 w-1.5 rounded-full",
          allowed ? "bg-accent" : "bg-line-strong",
        )}
      />
      <span className={allowed ? "text-ink" : "text-muted line-through decoration-line-strong"}>
        {label}
      </span>
    </li>
  );
}

function capitalize(value: string): string {
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function ObjectSkeleton() {
  return (
    <div className="container-page py-10">
      <Skeleton className="h-3 w-64" />
      <div className="mt-8 grid gap-10 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <Skeleton className="aspect-[4/3] w-full" />
        </div>
        <div className="lg:col-span-4">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="mt-5 h-12 w-3/4" />
          <Skeleton className="mt-6 h-4 w-40" />
          <Skeleton className="mt-8 h-20 w-full" />
          <Skeleton className="mt-8 h-12 w-full" />
        </div>
      </div>
    </div>
  );
}
