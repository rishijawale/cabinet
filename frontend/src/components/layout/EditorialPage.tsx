import type { ReactNode } from "react";

import { useDocumentMeta } from "../../hooks/useDocumentMeta";

interface EditorialPageProps {
  label: string;
  title: string;
  intro?: string;
  canonicalPath: string;
  description: string;
  updated?: string;
  children: ReactNode;
}

export function EditorialPage({
  label,
  title,
  intro,
  canonicalPath,
  description,
  updated,
  children,
}: EditorialPageProps) {
  useDocumentMeta({ title, description, canonicalPath });

  return (
    <article className="container-page py-10 sm:py-14">
      <header className="max-w-3xl border-b border-line pb-10">
        <p className="label">{label}</p>
        <h1 className="display mt-5 text-4xl leading-[0.96] text-ink sm:text-6xl">{title}</h1>
        {intro && (
          <p className="mt-6 text-base leading-7 text-muted sm:text-lg sm:leading-8">{intro}</p>
        )}
        {updated && <p className="label-tight mt-6">Last updated {updated}</p>}
      </header>

      <div className="mt-12 grid gap-12 lg:grid-cols-12">
        <div className="lg:col-span-3">
          <div className="border-t border-line pt-4 text-[11px] leading-5 text-muted lg:sticky lg:top-24">
            Cabinet is an independent archive. Editorial decisions are made by its curators; licensing
            decisions belong to each object's creator.
          </div>
        </div>
        <div className="space-y-10 lg:col-span-8 lg:col-start-5">{children}</div>
      </div>
    </article>
  );
}

export function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section>
      <h2 className="display text-2xl text-ink sm:text-3xl">{title}</h2>
      <div className="prose-editorial mt-4 space-y-4">{children}</div>
    </section>
  );
}
