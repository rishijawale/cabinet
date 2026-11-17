import { ChevronDown } from "lucide-react";
import type { ComponentProps } from "react";

import { cn } from "../../lib/cn";

type SelectProps = ComponentProps<"select"> & {
  label: string;
  hideLabel?: boolean;
};

export function Select({ label, hideLabel, className, id, ...props }: SelectProps) {
  const selectId = id ?? `select-${label.toLowerCase().replace(/\s+/g, "-")}`;
  return (
    <label htmlFor={selectId} className="group flex min-w-0 flex-col gap-1.5">
      <span className={cn("label-tight", hideLabel && "sr-only")}>{label}</span>
      <div className="relative">
        <select
          id={selectId}
          className={cn(
            "h-9 w-full appearance-none border border-line bg-transparent py-0 pl-3 pr-8 text-[13px] text-ink transition-colors hover:border-line-strong focus:border-ink focus:outline-none",
            className,
          )}
          {...props}
        />
        <ChevronDown
          aria-hidden="true"
          className="pointer-events-none absolute right-2 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted"
        />
      </div>
    </label>
  );
}
