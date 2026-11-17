import { Skeleton } from "../ui/Skeleton";

/**
 * Shown while a lazily loaded route chunk downloads. It mirrors the gallery
 * layout so the header, footer and page frame stay stable during the swap.
 */
export function RouteFallback() {
  return (
    <div
      aria-busy="true"
      aria-live="polite"
      className="mx-auto w-full max-w-[1400px] px-5 py-16 sm:px-8"
    >
      <Skeleton className="h-3 w-28" />
      <Skeleton className="mt-6 h-10 w-72 max-w-full" />
      <div className="mt-10 grid grid-cols-2 gap-x-5 gap-y-10 sm:grid-cols-3 lg:grid-cols-4">
        {Array.from({ length: 8 }).map((_, index) => (
          <div key={index}>
            <Skeleton className="aspect-[4/3] w-full" />
            <Skeleton className="mt-3 h-3 w-20" />
            <Skeleton className="mt-2 h-4 w-36" />
          </div>
        ))}
      </div>
    </div>
  );
}
