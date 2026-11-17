import { Link, useLocation } from "react-router-dom";

import { buttonStyles } from "../components/ui/Button";
import { useDocumentMeta } from "../hooks/useDocumentMeta";

const PAGES: Record<string, { label: string; title: string; body: string }> = {
  "/studio": {
    label: "Studio",
    title: "The studio is being prepared.",
    body: "A place to publish, arrange and care for objects in the archive. The archive itself stays open while we build it — curation tools arrive with the moderation milestone.",
  },
};

export function ComingSoonPage({ page }: { page?: keyof typeof PAGES }) {
  const location = useLocation();
  const content =
    (page ? PAGES[page] : undefined) ??
    PAGES[location.pathname] ?? {
      label: "Coming soon",
      title: "This room is not ready yet.",
      body: "A later milestone of Cabinet. The archive remains open while it is built.",
    };

  useDocumentMeta({
    title: content.label,
    description: content.body,
    canonicalPath: location.pathname,
  });

  return (
    <div className="container-page py-16 sm:py-24">
      <div className="max-w-2xl">
        <p className="label">{content.label}</p>
        <h1 className="display mt-5 text-4xl leading-[0.96] text-ink sm:text-6xl">
          {content.title}
        </h1>
        <p className="mt-6 text-base leading-7 text-muted sm:text-lg sm:leading-8">{content.body}</p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/explore" className={buttonStyles()}>
            Explore the archive
          </Link>
          <Link to="/about" className={buttonStyles({ variant: "secondary" })}>
            About Cabinet
          </Link>
        </div>
      </div>
    </div>
  );
}
