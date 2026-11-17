import { ChevronLeft, ChevronRight } from "lucide-react";

import { cn } from "../../lib/cn";

interface PaginationProps {
  page: number;
  pages: number;
  onChange: (page: number) => void;
}

function pageList(page: number, pages: number): (number | "ellipsis")[] {
  if (pages <= 7) return Array.from({ length: pages }, (_, index) => index + 1);
  const items: (number | "ellipsis")[] = [1];
  if (page > 3) items.push("ellipsis");
  for (let value = Math.max(2, page - 1); value <= Math.min(pages - 1, page + 1); value += 1) {
    items.push(value);
  }
  if (page < pages - 2) items.push("ellipsis");
  items.push(pages);
  return items;
}

export function Pagination({ page, pages, onChange }: PaginationProps) {
  if (pages <= 1) return null;

  return (
    <nav aria-label="Pagination" className="mt-16 flex items-center justify-between gap-4 border-t border-line pt-6">
      <button
        type="button"
        onClick={() => onChange(page - 1)}
        disabled={page <= 1}
        className="inline-flex items-center gap-2 text-[13px] text-muted transition-colors hover:text-ink disabled:pointer-events-none disabled:opacity-35"
      >
        <ChevronLeft className="h-4 w-4" />
        Previous
      </button>

      <div className="hidden items-center gap-1 sm:flex">
        {pageList(page, pages).map((item, index) =>
          item === "ellipsis" ? (
            <span key={`ellipsis-${index}`} className="px-2 text-muted">
              …
            </span>
          ) : (
            <button
              key={item}
              type="button"
              onClick={() => onChange(item)}
              aria-current={item === page ? "page" : undefined}
              className={cn(
                "h-8 min-w-8 border px-2 text-[12px] transition-colors",
                item === page
                  ? "border-ink bg-ink text-canvas"
                  : "border-transparent text-muted hover:border-line hover:text-ink",
              )}
            >
              {item}
            </button>
          ),
        )}
      </div>

      <p className="text-[12px] text-muted sm:hidden">
        Page {page} of {pages}
      </p>

      <button
        type="button"
        onClick={() => onChange(page + 1)}
        disabled={page >= pages}
        className="inline-flex items-center gap-2 text-[13px] text-muted transition-colors hover:text-ink disabled:pointer-events-none disabled:opacity-35"
      >
        Next
        <ChevronRight className="h-4 w-4" />
      </button>
    </nav>
  );
}
