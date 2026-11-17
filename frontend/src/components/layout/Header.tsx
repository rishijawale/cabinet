import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { Bookmark, Menu, Moon, Search, Sun, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, NavLink, useLocation } from "react-router-dom";

import { useSaved } from "../../hooks/useSaved";
import { useTheme } from "../../hooks/useTheme";
import { cn } from "../../lib/cn";

const NAV_LINKS = [
  { label: "Explore", href: "/explore" },
  { label: "Collections", href: "/collections" },
  { label: "Studio", href: "/studio" },
  { label: "Submit", href: "/submit" },
  { label: "About", href: "/about" },
];

export function Header() {
  const { pathname, search } = useLocation();
  const [open, setOpen] = useState(false);
  const { theme, toggle } = useTheme();
  const { items } = useSaved();
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    setOpen(false);
  }, [pathname, search]);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = "";
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <>
      <header className="sticky top-0 z-50 border-b border-line/80 bg-canvas/85 backdrop-blur-md">
      <div className="container-page flex h-16 items-center justify-between gap-6">
        <div className="flex items-center gap-8">
          <Link
            to="/"
            aria-label="Cabinet home"
            className="flex items-baseline gap-2 transition-opacity hover:opacity-70"
          >
            <span className="text-[15px] font-semibold uppercase tracking-[0.3em]">Cabinet</span>
            <span aria-hidden="true" className="h-1.5 w-1.5 translate-y-[-2px] bg-accent" />
          </Link>

          <nav aria-label="Main navigation" className="hidden items-center gap-7 lg:flex">
            {NAV_LINKS.map((link) => {
              const active = pathname === link.href || pathname.startsWith(`${link.href}/`);
              return (
                <NavLink
                  key={link.href}
                  to={link.href}
                  className={cn(
                    "relative py-1 text-[13px] font-medium transition-colors",
                    active ? "text-ink" : "text-muted hover:text-ink",
                  )}
                >
                  {link.label}
                  <span
                    aria-hidden="true"
                    className={cn(
                      "absolute -bottom-0.5 left-0 h-px w-full origin-left bg-accent transition-transform duration-300",
                      active ? "scale-x-100" : "scale-x-0",
                    )}
                  />
                </NavLink>
              );
            })}
          </nav>
        </div>

        <div className="flex items-center gap-1 sm:gap-2">
          <Link
            to="/explore?focus=search"
            aria-label="Search the archive"
            className="flex h-9 w-9 items-center justify-center text-muted transition-colors hover:text-ink"
          >
            <Search className="h-[18px] w-[18px]" />
          </Link>
          <Link
            to="/saved"
            aria-label={`Saved objects${items.length ? `, ${items.length} saved` : ""}`}
            className="relative flex h-9 w-9 items-center justify-center text-muted transition-colors hover:text-ink"
          >
            <Bookmark className="h-[18px] w-[18px]" />
            {items.length > 0 && (
              <span className="absolute right-1 top-1.5 h-1.5 w-1.5 rounded-full bg-accent" />
            )}
          </Link>
          <button
            type="button"
            onClick={toggle}
            aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
            className="flex h-9 w-9 items-center justify-center text-muted transition-colors hover:text-ink"
          >
            {theme === "dark" ? (
              <Sun className="h-[18px] w-[18px]" />
            ) : (
              <Moon className="h-[18px] w-[18px]" />
            )}
          </button>

          <button
            type="button"
            onClick={() => setOpen((value) => !value)}
            aria-expanded={open}
            aria-controls="mobile-navigation"
            aria-label={open ? "Close menu" : "Open menu"}
            className="ml-1 flex h-9 w-9 items-center justify-center text-ink lg:hidden"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>
      </header>

      <AnimatePresence>
        {open && (
          <motion.div
            id="mobile-navigation"
            initial={{ opacity: 0, y: reduceMotion ? 0 : -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: reduceMotion ? 0 : -8 }}
            transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
            className="fixed inset-x-0 top-16 bottom-0 z-40 overflow-y-auto border-t border-line bg-canvas lg:hidden"
          >
            <div className="container-page flex min-h-full flex-col justify-between py-10">
              <nav aria-label="Mobile navigation" className="flex flex-col">
                {NAV_LINKS.map((link, index) => (
                  <Link
                    key={link.href}
                    to={link.href}
                    className="group flex items-baseline justify-between border-b border-line py-5"
                  >
                    <span className="display text-4xl text-ink transition-colors group-hover:text-accent">
                      {link.label}
                    </span>
                    <span className="label-tight">{String(index + 1).padStart(2, "0")}</span>
                  </Link>
                ))}
                <Link
                  to="/saved"
                  className="group flex items-baseline justify-between border-b border-line py-5"
                >
                  <span className="display text-4xl text-ink transition-colors group-hover:text-accent">
                    Saved
                  </span>
                  <span className="label-tight">{items.length}</span>
                </Link>
              </nav>

              <div className="mt-12 flex items-center justify-between border-t border-line pt-6">
                <p className="label-tight max-w-[180px] leading-relaxed">
                  A place for things worth keeping.
                </p>
                <button
                  type="button"
                  onClick={toggle}
                  className="inline-flex items-center gap-2 text-sm text-muted"
                >
                  {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                  {theme === "dark" ? "Light theme" : "Dark theme"}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
