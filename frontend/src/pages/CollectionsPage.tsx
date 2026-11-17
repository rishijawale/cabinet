import { ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

import { CollectionCard } from "../components/collections/CollectionCard";
import { Skeleton } from "../components/ui/Skeleton";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { useCollections } from "../services/queries";

export function CollectionsPage() {
  const collections = useCollections();

  useDocumentMeta({
    title: "Collections",
    description:
      "Curated exhibitions from the Cabinet archive: themed rooms of ASCII art, wallpapers, pixel art and internet culture.",
    canonicalPath: "/collections",
  });

  const items = collections.data ?? [];
  const featured = items.filter((collection) => collection.is_featured);
  const rest = items.filter((collection) => !collection.is_featured);

  return (
    <div className="container-page py-10 sm:py-14">
      <header className="border-b border-line pb-8">
        <p className="label">Exhibitions</p>
        <div className="mt-4 flex flex-wrap items-end justify-between gap-6">
          <h1 className="display max-w-2xl text-4xl leading-[0.95] text-ink sm:text-6xl">
            Rooms with a point of view.
          </h1>
          <p className="max-w-sm text-sm leading-6 text-muted">
            Each collection is assembled around a single idea. No algorithm, no infinite feed — just
            a small, deliberate selection.
          </p>
        </div>
      </header>

      {collections.isLoading ? (
        <div className="mt-12 grid gap-12 lg:grid-cols-2">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index}>
              <Skeleton className="aspect-[16/10] w-full" />
              <Skeleton className="mt-5 h-4 w-40" />
              <Skeleton className="mt-3 h-10 w-3/4" />
            </div>
          ))}
        </div>
      ) : items.length === 0 ? (
        <p className="mt-16 text-sm text-muted">No public exhibitions yet.</p>
      ) : (
        <>
          {featured.length > 0 && (
            <section className="mt-12 space-y-10">
              {featured.map((collection) => (
                <Link
                  key={collection.id}
                  to={`/collections/${collection.slug}`}
                  className="group grid overflow-hidden border border-line lg:grid-cols-12"
                >
                  <div className="relative lg:col-span-7">
                    {collection.cover ? (
                      <img
                        src={collection.cover.card}
                        alt={collection.cover.alt}
                        className="aspect-[16/10] w-full object-cover transition-transform duration-700 group-hover:scale-[1.02] lg:h-full lg:min-h-[420px]"
                      />
                    ) : (
                      <div className="aspect-[16/10] bg-surface-muted lg:h-full lg:min-h-[420px]" />
                    )}
                    <span className="absolute left-4 top-4 border border-canvas/20 bg-canvas/90 px-2.5 py-1 text-[9px] font-medium uppercase tracking-[0.16em] text-ink backdrop-blur">
                      Featured exhibition
                    </span>
                  </div>

                  <div className="flex flex-col justify-between gap-10 bg-surface p-7 sm:p-10 lg:col-span-5">
                    <div>
                      <p className="label">
                        {collection.artwork_count} objects
                        {collection.curator ? ` · ${collection.curator.display_name}` : ""}
                      </p>
                      <h2 className="display mt-4 text-4xl leading-[0.98] text-ink transition-colors group-hover:text-accent sm:text-5xl">
                        {collection.title}
                      </h2>
                      {collection.description && (
                        <p className="mt-5 line-clamp-5 text-sm leading-7 text-muted">
                          {collection.description}
                        </p>
                      )}
                    </div>
                    <span className="inline-flex items-center gap-2 text-[12px] font-medium text-ink">
                      Enter the exhibition
                      <ArrowRight className="h-3.5 w-3.5 transition-transform duration-300 group-hover:translate-x-1" />
                    </span>
                  </div>
                </Link>
              ))}
            </section>
          )}

          {rest.length > 0 && (
            <section className="mt-16 sm:mt-24">
              <div className="flex items-end justify-between gap-4 border-b border-line pb-5">
                <h2 className="display text-2xl text-ink sm:text-3xl">More exhibitions</h2>
                <Link
                  to="/explore"
                  className="text-[12px] text-muted transition-colors hover:text-ink"
                >
                  Or browse every object
                </Link>
              </div>
              <div className="mt-10 grid gap-x-6 gap-y-14 lg:grid-cols-2">
                {rest.map((collection) => (
                  <CollectionCard key={collection.id} collection={collection} />
                ))}
              </div>
            </section>
          )}
        </>
      )}
    </div>
  );
}
