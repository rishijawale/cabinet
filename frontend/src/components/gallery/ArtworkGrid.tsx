import { SkeletonCard } from "../ui/Skeleton";
import { cn } from "../../lib/cn";
import type { Artwork } from "../../types/api";
import { ArtworkCard } from "./ArtworkCard";

interface ArtworkGridProps {
  artworks: Artwork[];
  loading?: boolean;
  skeletonCount?: number;
  className?: string;
  columns?: 3 | 4;
  sizes?: string;
}

export function ArtworkGrid({
  artworks,
  loading,
  skeletonCount = 8,
  className,
  columns = 4,
  sizes,
}: ArtworkGridProps) {
  const columnClasses =
    columns === 3
      ? "grid-cols-2 md:grid-cols-2 lg:grid-cols-3"
      : "grid-cols-2 md:grid-cols-3 xl:grid-cols-4";

  return (
    <div className={cn("grid items-start gap-x-4 gap-y-9 sm:gap-x-6 sm:gap-y-12", columnClasses, className)}>
      {loading
        ? Array.from({ length: skeletonCount }).map((_, index) => (
            <SkeletonCard key={`skeleton-${index}`} aspect="aspect-[4/3]" />
          ))
        : artworks.map((artwork) => (
            <ArtworkCard
              key={artwork.id}
              artwork={artwork}
              sizes={sizes}
              aspect="aspect-[4/3]"
              fit="contain"
            />
          ))}
    </div>
  );
}
