import { Bookmark, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";

import { buttonStyles } from "../components/ui/Button";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { useSaved } from "../hooks/useSaved";

export function SavedPage() {
  const { items, remove } = useSaved();

  useDocumentMeta({
    title: "Saved objects",
    description: "Objects you have saved to this device.",
    canonicalPath: "/saved",
  });

  return (
    <div className="container-page py-10 sm:py-14">
      <header className="border-b border-line pb-8">
        <p className="label">Your cabinet</p>
        <div className="mt-4 flex flex-wrap items-end justify-between gap-6">
          <h1 className="display text-4xl leading-[0.95] text-ink sm:text-6xl">Saved objects.</h1>
          <p className="max-w-sm text-sm leading-6 text-muted">
            Saved to this browser. Accounts arrive in a later milestone, at which point favourites
            will follow you between devices.
          </p>
        </div>
      </header>

      {items.length === 0 ? (
        <div className="mt-16 border border-dashed border-line-strong px-6 py-24 text-center">
          <Bookmark className="mx-auto h-6 w-6 text-muted" />
          <p className="display mt-5 text-3xl text-ink">Nothing saved yet.</p>
          <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-muted">
            Use the save button on any object to keep it here for later.
          </p>
          <Link to="/explore" className={buttonStyles({ className: "mt-7" })}>
            Explore the archive
          </Link>
        </div>
      ) : (
        <>
          <p className="mt-6 text-[12px] text-muted">
            {items.length} {items.length === 1 ? "object" : "objects"}
          </p>
          <ul className="mt-8 grid grid-cols-2 gap-x-4 gap-y-10 sm:gap-x-6 md:grid-cols-3 xl:grid-cols-4">
            {items.map((item) => (
              <li key={item.slug}>
                <Link to={`/object/${item.slug}`} className="group block">
                  <div className="overflow-hidden border border-line bg-surface-muted">
                    <img
                      src={item.preview}
                      alt={item.alt}
                      loading="lazy"
                      className="aspect-[4/3] w-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
                    />
                  </div>
                  <p className="label-tight mt-3">
                    {item.categoryName} /{" "}
                    <span className="font-mono normal-case tracking-normal">
                      {item.fileFormat.toUpperCase()}
                    </span>
                  </p>
                  <h2 className="mt-1.5 text-[15px] font-medium leading-snug text-ink transition-colors group-hover:text-accent">
                    {item.title}
                  </h2>
                  <p className="mt-0.5 truncate text-[13px] text-muted">{item.creatorName}</p>
                </Link>
                <button
                  type="button"
                  onClick={() => remove(item.slug)}
                  className="mt-3 inline-flex items-center gap-1.5 text-[11px] text-muted transition-colors hover:text-accent"
                >
                  <Trash2 className="h-3 w-3" /> Remove
                </button>
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
