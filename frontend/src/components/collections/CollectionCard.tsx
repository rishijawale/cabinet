import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

import { cn } from "../../lib/cn";
import type { Collection } from "../../types/api";

export function CollectionCard({
  collection,
  className,
  featured,
}: {
  collection: Collection;
  className?: string;
  featured?: boolean;
}) {
  return (
    <Link
      to={`/collections/${collection.slug}`}
      className={cn("group grid gap-5 focus-visible:outline-none", className)}
    >
      <div className="relative overflow-hidden border border-line bg-surface-muted">
        {collection.cover ? (
          <img
            src={collection.cover.card}
            srcSet={`${collection.cover.thumb} 320w, ${collection.cover.card} 800w, ${collection.cover.full} 1600w`}
            sizes={featured ? "(min-width: 1024px) 58vw, 100vw" : "(min-width: 1024px) 50vw, 100vw"}
            alt={collection.cover.alt}
            loading="lazy"
            decoding="async"
            className={cn(
              "w-full object-cover transition-transform duration-700 ease-out group-hover:scale-[1.025]",
              featured ? "aspect-[16/9]" : "aspect-[16/10]",
            )}
          />
        ) : (
          <div className={cn("w-full bg-surface-muted", featured ? "aspect-[16/9]" : "aspect-[16/10]")} />
        )}
        <span className="absolute left-3 top-3 border border-canvas/20 bg-canvas/90 px-2 py-1 text-[9px] font-medium uppercase tracking-[0.16em] text-ink backdrop-blur">
          Exhibition
        </span>
      </div>

      <div>
        <p className="label-tight">
          {collection.artwork_count} objects
          {collection.curator ? ` · Curated by ${collection.curator.display_name}` : ""}
        </p>
        <h3
          className={cn(
            "display mt-2 leading-[1.02] text-ink transition-colors group-hover:text-accent",
            featured ? "text-4xl sm:text-5xl" : "text-3xl sm:text-4xl",
          )}
        >
          {collection.title}
        </h3>
        {collection.description && (
          <p className="mt-3 line-clamp-2 max-w-xl text-sm leading-6 text-muted">
            {collection.description}
          </p>
        )}
        <span className="mt-4 inline-flex items-center gap-2 text-[12px] font-medium text-ink">
          View exhibition
          <ArrowRight className="h-3.5 w-3.5 transition-transform duration-300 group-hover:translate-x-1" />
        </span>
      </div>
    </Link>
  );
}
