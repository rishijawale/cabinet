import { ArrowUpRight } from "lucide-react";
import { Link } from "react-router-dom";

import { cn } from "../../lib/cn";
import type { Artwork } from "../../types/api";

interface ArtworkCardProps {
  artwork: Artwork;
  className?: string;
  aspect?: string;
  sizes?: string;
  fit?: "cover" | "contain";
}

function aspectFor(artwork: Artwork): string {
  if (artwork.orientation === "portrait") return "aspect-[3/4]";
  if (artwork.orientation === "square") return "aspect-square";
  return "aspect-[4/3]";
}

export function ArtworkCard({ artwork, className, aspect, sizes, fit = "cover" }: ArtworkCardProps) {
  return (
    <Link
      to={`/object/${artwork.slug}`}
      className={cn("group block focus-visible:outline-none", className)}
    >
      <div className="relative overflow-hidden border border-line bg-surface-muted">
        <img
          src={artwork.preview.card}
          srcSet={`${artwork.preview.thumb} 320w, ${artwork.preview.card} 800w, ${artwork.preview.full} 1600w`}
          sizes={
            sizes ??
            "(min-width: 1280px) 24vw, (min-width: 768px) 32vw, 48vw"
          }
          alt={artwork.preview.alt}
          loading="lazy"
          decoding="async"
          className={cn(
            "h-full w-full transition-transform duration-700 ease-out group-hover:scale-[1.035]",
            fit === "contain" ? "object-contain" : "object-cover",
            aspect ?? aspectFor(artwork),
          )}
        />
        <span
          aria-hidden="true"
          className="pointer-events-none absolute inset-0 ring-1 ring-inset ring-black/[0.04] dark:ring-white/[0.06]"
        />
        {artwork.featured && (
          <span className="absolute left-3 top-3 border border-canvas/20 bg-canvas/90 px-2 py-1 text-[9px] font-medium uppercase tracking-[0.16em] text-ink backdrop-blur">
            Featured
          </span>
        )}
      </div>

      <div className="mt-3 flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="label-tight flex flex-wrap items-center gap-x-2 gap-y-1">
            <span>{artwork.category.name}</span>
            <span aria-hidden="true" className="text-line-strong">
              /
            </span>
            <span className="font-mono normal-case tracking-normal">
              {artwork.file_format.toUpperCase()}
            </span>
          </p>
          <h3 className="mt-1.5 text-[15px] font-medium leading-snug text-ink transition-colors group-hover:text-accent">
            {artwork.title}
          </h3>
          <p className="mt-0.5 truncate text-[13px] text-muted">{artwork.creator.display_name}</p>
        </div>
        <ArrowUpRight
          aria-hidden="true"
          className="mt-1 h-4 w-4 shrink-0 -translate-x-1 text-muted opacity-0 transition-all duration-300 group-hover:translate-x-0 group-hover:opacity-100"
        />
      </div>
    </Link>
  );
}
