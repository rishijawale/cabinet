import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useDebouncedValue } from "../hooks/useDebouncedValue";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { useArtworks, useCategories, useCollections, useRandomArtwork } from "../services/queries";
import type { Artwork, Collection, Category } from "../types/api";
import { ArtworkCard } from "../components/gallery/ArtworkCard";
import { ArtworkGrid } from "../components/gallery/ArtworkGrid";
import { Badge } from "../components/ui/Badge";
import { Button, buttonStyles } from "../components/ui/Button";
import { SearchField } from "../components/ui/SearchField";
import { Skeleton, SkeletonCard } from "../components/ui/Skeleton";
import { cn } from "../lib/cn";
import { ArrowRight, ArrowUpRight, RefreshCw } from "lucide-react";
import { useNavigate } from "react-router-dom";

export function HomePage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const debounced = useDebouncedValue(query, 200);
  const recent = useArtworks({ limit: 8, sort: "recent" });
  const categories = useCategories();
  const collections = useCollections();
  const random = useRandomArtwork();

  useDocumentMeta({
    title: "Cabinet — A place for things worth keeping",
    description:
      "A curated archive of ASCII art, wallpapers, pixel art and digital experiments. Free to explore, made to be kept.",
    image: recent.data?.data[0]?.preview.card,
    jsonLd: {
      "@context": "https://schema.org",
      "@type": "WebSite",
      name: "Cabinet",
      url: window.location.origin,
      description: "A curated digital archive for things worth keeping.",
    },
  });

  useEffect(() => {
    if (debounced.trim()) {
      navigate(`/explore?q=${encodeURIComponent(debounced.trim())}`, { replace: true });
    }
  }, [debounced, navigate]);

  const artworks = recent.data?.data ?? [];
  const featuredCollection =
    collections.data?.find((collection) => collection.is_featured) ?? collections.data?.[0];
  const total = recent.data?.meta.total ?? 0;

  return (
    <>
      <Hero
        artworks={artworks}
        loading={recent.isLoading}
        total={total}
        categoryCount={categories.data?.length ?? 0}
        exhibitionCount={collections.data?.length ?? 0}
      />

      <section aria-label="Search the archive" className="border-y border-line">
        <div className="container-page py-10 sm:py-12">
          <form
            onSubmit={(event) => {
              event.preventDefault();
              if (query.trim()) navigate(`/explore?q=${encodeURIComponent(query.trim())}`);
            }}
            className="mx-auto max-w-3xl"
          >
            <SearchField
              value={query}
              onChange={setQuery}
              size="large"
              placeholder="Search objects, makers, tags…"
            />
          </form>
          <div className="mx-auto mt-5 flex max-w-3xl flex-wrap items-center gap-2">
            <span className="label-tight mr-1">Try</span>
            {["terminal", "monochrome", "tiny worlds", "minimal", "pixel"].map((term) => (
              <Link
                key={term}
                to={`/explore?q=${encodeURIComponent(term)}`}
                className="border border-line px-2.5 py-1 text-[11px] text-muted transition-colors hover:border-ink hover:text-ink"
              >
                {term}
              </Link>
            ))}
          </div>
        </div>
      </section>

      {featuredCollection && (
        <FeaturedExhibition collection={featuredCollection} loading={collections.isLoading} />
      )}

      <section className="container-page mt-20 sm:mt-28">
        <SectionHeading
          label="Curated discoveries"
          title="Objects worth a second look"
          href="/explore"
          linkLabel="View all objects"
        />
        {recent.isLoading ? (
          <div className="mt-10 grid grid-cols-2 gap-4 md:grid-cols-12 md:gap-6">
            {Array.from({ length: 5 }).map((_, index) => (
              <div key={index} className={index < 2 ? "md:col-span-6" : "md:col-span-4"}>
                <SkeletonCard aspect={index === 0 ? "aspect-[16/11]" : "aspect-[4/3]"} />
              </div>
            ))}
          </div>
        ) : (
          <div className="mt-10 grid grid-cols-2 gap-4 md:grid-cols-12 md:gap-6">
            {artworks.slice(0, 5).map((artwork, index) => (
              <ArtworkCard
                key={artwork.id}
                artwork={artwork}
                className={cn(
                  index < 2 ? "md:col-span-6" : "md:col-span-4",
                  index === 0 && "col-span-2 md:col-span-7",
                  index === 1 && "md:col-span-5",
                )}
                aspect={index === 0 ? "aspect-[16/11]" : index === 1 ? "aspect-[4/5]" : "aspect-[4/3]"}
                sizes={
                  index < 2
                    ? "(min-width: 768px) 48vw, 100vw"
                    : "(min-width: 768px) 32vw, 50vw"
                }
              />
            ))}
          </div>
        )}
      </section>

      <CategoryStrip categories={categories.data ?? []} loading={categories.isLoading} />

      <section className="container-page mt-20 sm:mt-28">
        <SectionHeading
          label="Recently added"
          title="New to the archive"
          href="/explore?sort=recent"
          linkLabel="Browse chronologically"
        />
        <ArtworkGrid
          artworks={artworks.slice(3, 7)}
          loading={recent.isLoading}
          skeletonCount={4}
          className="mt-10"
        />
      </section>

      <RandomDiscovery
        artwork={random.data}
        loading={random.isLoading}
        onRefresh={() => void random.refetch()}
        isFetching={random.isFetching}
      />

      <CommunityCallout />
    </>
  );
}

function Hero({
  artworks,
  loading,
  total,
  categoryCount,
  exhibitionCount,
}: {
  artworks: Artwork[];
  loading: boolean;
  total: number;
  categoryCount: number;
  exhibitionCount: number;
}) {
  return (
    <section className="container-page pb-14 pt-12 sm:pb-20 sm:pt-20">
      <div className="grid items-center gap-14 lg:grid-cols-12 lg:gap-4">
        <div className="lg:col-span-7 lg:pr-12">
          <p className="label flex items-center gap-2">
            <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-accent" />
            The archive is open
          </p>
          <h1 className="display mt-7 text-[clamp(3.3rem,6.4vw,6.3rem)] leading-[0.9] text-balance text-ink">
            The internet has a lot of <em className="italic text-accent">beautiful</em> things.
          </h1>
          <p className="mt-7 max-w-md text-base leading-7 text-muted sm:text-lg">
            We collect the ones worth keeping. An archive of digital artwork, small experiments and
            the corners of the internet that deserve a longer look.
          </p>

          <div className="mt-9 flex flex-wrap items-center gap-3">
            <Link to="/explore" className={buttonStyles({ size: "lg" })}>
              Explore the archive
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to="/studio" className={buttonStyles({ variant: "secondary", size: "lg" })}>
              Visit the studio
            </Link>
          </div>

          <dl className="mt-12 flex max-w-lg flex-wrap gap-x-10 gap-y-5 border-t border-line pt-6">
            <Stat value={total || "—"} label="Published objects" />
            <Stat value={categoryCount || "03"} label="Collections" />
            <Stat value={exhibitionCount || "05"} label="Exhibitions" />
            <Stat value="Free" label="To explore" />
          </dl>
        </div>

        <div className="lg:col-span-5">
          {loading ? (
            <Skeleton className="aspect-[4/5] w-full" />
          ) : (
            <div className="relative mx-auto max-w-[440px] lg:ml-auto">
              {artworks[0] ? (
                <Link to={`/object/${artworks[0].slug}`} className="group block">
                  <div className="frame">
                    <img
                      src={artworks[0].preview.card}
                      alt={artworks[0].preview.alt}
                      className="aspect-[4/5] w-full object-cover transition-transform duration-700 group-hover:scale-[1.02]"
                    />
                  </div>
                  <div className="mt-3 flex items-baseline justify-between gap-4">
                    <p className="text-sm text-ink">{artworks[0].title}</p>
                    <p className="label-tight shrink-0">{artworks[0].category.name}</p>
                  </div>
                </Link>
              ) : null}

              {artworks[1] && (
                <Link
                  to={`/object/${artworks[1].slug}`}
                  className="absolute left-6 top-8 hidden w-40 border border-canvas bg-surface p-1.5 shadow-sm transition-transform duration-500 hover:-translate-y-1 sm:block lg:-left-16"
                >
                  <img
                    src={artworks[1].preview.thumb}
                    alt={artworks[1].preview.alt}
                    className="aspect-square w-full object-cover"
                  />
                  <p className="mt-2 truncate px-1 text-[10px] text-muted">
                    {artworks[1].title}
                  </p>
                </Link>
              )}

              <span className="display absolute -right-3 -top-10 hidden text-[64px] leading-none text-line-strong lg:block">
                {String(artworks.length || 1).padStart(2, "0")}
              </span>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function Stat({ value, label }: { value: string | number; label: string }) {
  return (
    <div>
      <dt className="sr-only">{label}</dt>
      <dd className="display text-2xl text-ink">{value}</dd>
      <dd className="label-tight mt-1">{label}</dd>
    </div>
  );
}

function SectionHeading({
  label,
  title,
  href,
  linkLabel,
}: {
  label: string;
  title: string;
  href?: string;
  linkLabel?: string;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-6 border-b border-line pb-6">
      <div>
        <p className="label">{label}</p>
        <h2 className="display mt-3 text-3xl text-ink sm:text-4xl">{title}</h2>
      </div>
      {href && linkLabel && (
        <Link
          to={href}
          className="group inline-flex items-center gap-2 text-[12px] font-medium text-muted transition-colors hover:text-ink"
        >
          {linkLabel}
          <ArrowUpRight className="h-3.5 w-3.5 transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
        </Link>
      )}
    </div>
  );
}

function FeaturedExhibition({
  collection,
  loading,
}: {
  collection: Collection;
  loading: boolean;
}) {
  if (loading) {
    return (
      <section className="container-page mt-20 sm:mt-28">
        <Skeleton className="aspect-[21/9] w-full" />
      </section>
    );
  }

  return (
    <section className="container-page mt-20 sm:mt-28">
      <div className="grid overflow-hidden border border-line lg:grid-cols-12">
        <Link
          to={`/collections/${collection.slug}`}
          className="group relative block lg:col-span-7"
        >
          {collection.cover ? (
            <img
              src={collection.cover.card}
              alt={collection.cover.alt}
              className="aspect-[16/10] h-full w-full object-cover transition-transform duration-700 group-hover:scale-[1.02] lg:aspect-auto lg:min-h-[520px]"
            />
          ) : (
            <div className="aspect-[16/10] bg-surface-muted lg:min-h-[520px]" />
          )}
          <span className="absolute left-4 top-4 border border-canvas/20 bg-canvas/90 px-2.5 py-1 text-[9px] font-medium uppercase tracking-[0.16em] text-ink backdrop-blur">
            Featured exhibition
          </span>
        </Link>

        <div className="flex flex-col justify-between gap-10 bg-surface p-7 sm:p-10 lg:col-span-5 lg:p-12">
          <div>
            <p className="label">
              {collection.artwork_count} objects · Curated by{" "}
              {collection.curator?.display_name ?? "the archive"}
            </p>
            <h2 className="display mt-5 text-4xl leading-[0.98] text-ink sm:text-5xl">
              {collection.title}
            </h2>
            <p className="mt-5 line-clamp-6 text-sm leading-7 text-muted">
              {collection.description}
            </p>
          </div>

          <div>
            <Link
              to={`/collections/${collection.slug}`}
              className={buttonStyles({ variant: "secondary", className: "w-full sm:w-auto" })}
            >
              Enter the exhibition
              <ArrowRight className="h-4 w-4" />
            </Link>
            <p className="mt-5 text-[11px] leading-5 text-muted">
              Exhibitions are curated around a single idea. No algorithm, no infinite feed — just a
              room with a point of view.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

function CategoryStrip({ categories, loading }: { categories: Category[]; loading: boolean }) {
  return (
    <section className="container-page mt-20 sm:mt-28">
      <SectionHeading
        label="The collections"
        title="Browse by category"
        href="/explore"
        linkLabel="Explore everything"
      />
      <div className="mt-10 grid gap-8 sm:grid-cols-3 sm:gap-5">
        {loading
          ? Array.from({ length: 3 }).map((_, index) => (
              <div key={index}>
                <Skeleton className="aspect-[4/3] w-full" />
                <Skeleton className="mt-4 h-6 w-32" />
              </div>
            ))
          : categories.map((item, index) => (
              <Link
                key={item.slug}
                to={`/explore/${item.slug}`}
                className={cn("group block", index === 1 && "sm:mt-10")}
              >
                <div className="relative overflow-hidden border border-line bg-surface-muted">
                  {item.cover_image ? (
                    <img
                      src={item.cover_image}
                      alt={`${item.name} collection`}
                      loading="lazy"
                      className="aspect-[4/3] w-full object-cover transition-transform duration-700 group-hover:scale-[1.03]"
                    />
                  ) : (
                    <div className="aspect-[4/3] w-full bg-surface-muted" />
                  )}
                  <span className="absolute right-3 top-3 bg-canvas/90 px-2 py-1 font-mono text-[10px] text-ink backdrop-blur">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                </div>
                <div className="mt-4 flex items-baseline justify-between gap-3 border-b border-line pb-3">
                  <div>
                    <h3 className="display text-2xl text-ink transition-colors group-hover:text-accent">
                      {item.name}
                    </h3>
                    <p className="mt-1 text-[11px] text-muted">{item.artwork_count} objects</p>
                  </div>
                  <ArrowUpRight className="h-4 w-4 text-muted transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
                </div>
              </Link>
            ))}
      </div>
    </section>
  );
}

function RandomDiscovery({
  artwork,
  loading,
  onRefresh,
  isFetching,
}: {
  artwork: Artwork | undefined;
  loading: boolean;
  onRefresh: () => void;
  isFetching: boolean;
}) {
  return (
    <section className="container-page mt-20 sm:mt-28">
      <div className="grid gap-8 border border-line bg-surface p-6 sm:p-10 lg:grid-cols-12 lg:items-center">
        <div className="lg:col-span-5">
          <p className="label flex items-center gap-2">
            <span aria-hidden="true" className="h-1.5 w-1.5 rounded-full bg-accent" />
            Random access
          </p>
          <h2 className="display mt-5 text-4xl leading-[0.98] text-ink sm:text-5xl">
            Leave it to chance.
          </h2>
          <p className="mt-4 max-w-sm text-sm leading-6 text-muted">
            The archive holds more than a hundred objects. Pull one at random and see what the
            internet left behind.
          </p>
          <Button
            variant="secondary"
            onClick={onRefresh}
            disabled={isFetching}
            className="mt-7"
          >
            <RefreshCw className={cn("h-4 w-4", isFetching && "animate-spin")} />
            Show me another
          </Button>
        </div>

        <div className="lg:col-span-7">
          {loading || !artwork ? (
            <Skeleton className="aspect-[16/10] w-full" />
          ) : (
            <Link to={`/object/${artwork.slug}`} className="group grid gap-5 sm:grid-cols-12">
              <div className="overflow-hidden border border-line sm:col-span-8">
                <img
                  src={artwork.preview.card}
                  alt={artwork.preview.alt}
                  className="aspect-[4/3] w-full object-cover transition-transform duration-700 group-hover:scale-[1.025]"
                />
              </div>
              <div className="flex flex-col justify-between sm:col-span-4">
                <div>
                  <Badge>{artwork.category.name}</Badge>
                  <h3 className="display mt-3 text-2xl leading-tight text-ink transition-colors group-hover:text-accent">
                    {artwork.title}
                  </h3>
                  <p className="mt-2 text-[12px] text-muted">
                    {artwork.creator.display_name}
                  </p>
                </div>
                <p className="label-tight mt-5">
                  {artwork.file_format.toUpperCase()} · {artwork.orientation}
                </p>
              </div>
            </Link>
          )}
        </div>
      </div>
    </section>
  );
}

function CommunityCallout() {
  return (
    <section className="container-page mt-20 sm:mt-28">
      <div className="grid gap-8 bg-ink p-8 text-canvas sm:p-12 lg:grid-cols-12 lg:items-end lg:p-16">
        <div className="lg:col-span-7">
          <p className="text-[11px] font-medium uppercase tracking-[0.18em] text-canvas/60">
            Community
          </p>
          <h2 className="display mt-5 max-w-xl text-4xl leading-[0.98] sm:text-5xl">
            Have something worth keeping?
          </h2>
          <p className="mt-5 max-w-lg text-sm leading-7 text-canvas/70">
            Cabinet is built with contributors, not scraped from them. The submission workflow is
            being prepared for the next release; until then, the guidelines explain exactly what we
            look for and how attribution works.
          </p>
        </div>
        <div className="flex flex-wrap gap-3 lg:col-span-5 lg:justify-end">
          <Link
            to="/guidelines"
            className={buttonStyles({
              className: "border-transparent bg-canvas text-ink hover:bg-accent hover:text-accent-contrast",
            })}
          >
            Read the guidelines
          </Link>
          <Link
            to="/submit"
            className={buttonStyles({
              variant: "ghost",
              className: "border border-canvas/20 text-canvas hover:bg-canvas/10 hover:text-canvas",
            })}
          >
            About submissions
          </Link>
        </div>
      </div>
    </section>
  );
}
