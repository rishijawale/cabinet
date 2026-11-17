import { Search, X } from "lucide-react";
import { useEffect, useRef } from "react";

import { cn } from "../../lib/cn";

interface SearchFieldProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
  className?: string;
  size?: "default" | "large";
}

export function SearchField({
  value,
  onChange,
  placeholder = "Search the archive",
  autoFocus,
  className,
  size = "default",
}: SearchFieldProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (autoFocus) inputRef.current?.focus();
  }, [autoFocus]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "/" && document.activeElement?.tagName !== "INPUT") {
        event.preventDefault();
        inputRef.current?.focus();
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <div
      className={cn(
        "group flex items-center gap-3 border-b border-line-strong transition-colors focus-within:border-ink",
        size === "large" ? "pb-4" : "pb-2",
        className,
      )}
    >
      <Search
        aria-hidden="true"
        className={cn("shrink-0 text-muted", size === "large" ? "h-6 w-6" : "h-4 w-4")}
      />
      <input
        ref={inputRef}
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        aria-label="Search the archive"
        className={cn(
          "w-full min-w-0 bg-transparent text-ink placeholder:text-muted/70 focus:outline-none [&::-webkit-search-cancel-button]:appearance-none",
          size === "large"
            ? "font-display text-2xl sm:text-3xl"
            : "text-sm sm:text-base",
        )}
      />
      {value ? (
        <button
          type="button"
          onClick={() => onChange("")}
          aria-label="Clear search"
          className="shrink-0 p-1 text-muted transition-colors hover:text-ink"
        >
          <X className="h-4 w-4" />
        </button>
      ) : (
        <kbd className="hidden shrink-0 border border-line px-1.5 py-0.5 font-mono text-[10px] text-muted sm:block">
          /
        </kbd>
      )}
    </div>
  );
}
