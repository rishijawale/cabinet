import type { HTMLAttributes } from "react";

import { cn } from "../../lib/cn";

export function Skeleton({
  className,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      aria-hidden="true"
      className={cn("animate-pulse bg-surface-muted", className)}
      {...props}
    />
  );
}

export function SkeletonCard({ aspect = "aspect-[4/5]" }: { aspect?: string }) {
  return (
    <div>
      <Skeleton className={cn("w-full", aspect)} />
      <Skeleton className="mt-3 h-3 w-24" />
      <Skeleton className="mt-2 h-4 w-40" />
      <Skeleton className="mt-2 h-3 w-28" />
    </div>
  );
}
