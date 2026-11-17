import { ArrowLeft } from "lucide-react";
import { Link, useParams } from "react-router-dom";

import { ArtworkGrid } from "../components/gallery/ArtworkGrid";
import { buttonStyles } from "../components/ui/Button";
import { Skeleton } from "../components/ui/Skeleton";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { formatDate } from "../lib/format";
import { useCollection } from "../services/queries";

export function CollectionDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const collection = useCollection(slug);
  const data = collection.data;

  useDocumentMeta({
    title: data ? data.title : "Collection",
    description: data?.description ?? undefined,
    image: data?.cover?.full,
    canonicalPath: data ? `/collections/${data.slug}` : undefined,
    jsonLd: data
      ? {
          "@context": "https://schema.org",
          "@type": "CollectionPage",
          name: data.title,
          description: data.description ?? undefined,
          url: `${window.location.origin}/collections/${data.slug}`,
          hasPart: data.artworks.map((artwork) => ({
            "@type": "VisualArtwork",
            name: artwork.title,
            url: `${window.location.origin}/object/${artwork.slug}`,
          })),
        }
      : undefined,
  });

  if (collection.isLoading) {
    return (
      <div className="container-page py-12">
        <Skeleton className="h-3 w-40" />
        <Skeleton className="mt-6 h-16 w-3/4" />
        <Skeleton className="mt-6 h-5 w-1/2" />
        <Skeleton className="mt-10 aspect-[21/9] w-full" />
      </div>
    );
  }

  if (collection.isError || !data) {
    return (
      <div className="container-page py-28 text-center">
        <p className="label">404 — Collection not found</p>
        <h1 className="display mt-5 text-4xl text-ink sm:text-5xl">
          This exhibition is not on view.
        </h1>
        <p className="mx-auto mt-4 max-w-md text-sm leading-6 text-muted">
          It may have been unpublished or the link may be incorrect.
        </p>
        <Link to="/collections" className={buttonStyles({ className: "mt-8" })}>
          All exhibitions
        </Link>
      </div>
    );
  }

  return (
    <article>
      <header className="container-page py-10 sm:py-14">
        <Link
          to="/collections"
          className="inline-flex items-center gap-1.5 text-[11px] text-muted hover:text-ink"
        >
          <ArrowLeft className="h-3 w-3" /> All exhibitions
        </Link>

        <div className="mt-8 grid gap-8 border-b border-line pb-10 lg:grid-cols-12 lg:items-end">
          <div className="lg:col-span-8">
            <p className="label">
              {data.artwork_count} objects
              {data.curator ? ` · Curated by ${data.curator.display_name}` : ""}
              {` · ${formatDate(data.created_at)}`}
            </p>
            <h1 className="display mt-5 max-w-3xl text-4xl leading-[0.94] text-ink sm:text-6xl">
              {data.title}
            </h1>
            {data.description && (
              <p className="mt-6 max-w-2xl text-base leading-7 text-muted sm:text-lg sm:leading-8">
                {data.description}
              </p>
            )}
          </div>
          <div className="lg:col-span-4">
            {data.cover && (
              <img
                src={data.cover.card}
                alt={data.cover.alt}
                className="aspect-[4/3] w-full border border-line object-cover"
              />
            )}
          </div>
        </div>
      </header>

      <section className="container-page pb-6">
        <ArtworkGrid
          artworks={data.artworks}
          sizes="(min-width: 1280px) 24vw, (min-width: 768px) 32vw, 48vw"
        />
      </section>
    </article>
  );
}
