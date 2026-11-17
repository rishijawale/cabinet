import type { ComponentProps } from "react";

import { cn } from "../../lib/cn";

type Variant = "primary" | "secondary" | "ghost" | "accent";
type Size = "sm" | "md" | "lg";

const sizes: Record<Size, string> = {
  sm: "h-9 px-3.5 text-[13px]",
  md: "h-11 px-5 text-sm",
  lg: "h-12 px-6 text-sm",
};

const variants: Record<Variant, string> = {
  primary:
    "bg-ink text-canvas hover:bg-accent hover:text-accent-contrast border border-transparent",
  secondary:
    "border border-line-strong bg-transparent text-ink hover:border-ink hover:bg-surface",
  ghost: "border border-transparent text-ink hover:bg-surface-muted",
  accent: "bg-accent text-accent-contrast hover:opacity-90 border border-transparent",
};

export function buttonStyles({
  variant = "primary",
  size = "md",
  className,
}: {
  variant?: Variant;
  size?: Size;
  className?: string;
} = {}): string {
  return cn(
    "inline-flex select-none items-center justify-center gap-2 whitespace-nowrap font-medium transition-colors duration-200 disabled:pointer-events-none disabled:opacity-45",
    sizes[size],
    variants[variant],
    className,
  );
}

type ButtonProps = ComponentProps<"button"> & {
  variant?: Variant;
  size?: Size;
};

export function Button({
  variant = "primary",
  size = "md",
  className,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button type={type} className={buttonStyles({ variant, size, className })} {...props} />
  );
}
