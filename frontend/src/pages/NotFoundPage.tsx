import { Link, useLocation } from "react-router-dom";

import { buttonStyles } from "../components/ui/Button";
import { useDocumentMeta } from "../hooks/useDocumentMeta";

export function NotFoundPage() {
  const location = useLocation();

  useDocumentMeta({
    title: "Page not found",
    description: "The page you were looking for is not in the archive.",
    canonicalPath: location.pathname,
  });

  return (
    <div className="container-page py-24 sm:py-32">
      <div className="mx-auto max-w-2xl text-center">
        <p className="font-mono text-[11px] uppercase tracking-[0.24em] text-accent">404</p>
        <h1 className="display mt-6 text-5xl leading-[0.95] text-ink sm:text-7xl">
          An empty frame.
        </h1>
        <p className="mx-auto mt-6 max-w-md text-sm leading-7 text-muted">
          The page you were looking for is not in the archive. It may have been moved, renamed, or it
          never existed in the first place.
        </p>
        <div className="mt-9 flex flex-wrap justify-center gap-3">
          <Link to="/explore" className={buttonStyles()}>
            Explore the archive
          </Link>
          <Link to="/" className={buttonStyles({ variant: "secondary" })}>
            Return home
          </Link>
        </div>
      </div>
    </div>
  );
}
