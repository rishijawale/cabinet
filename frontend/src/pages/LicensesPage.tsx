import { Link } from "react-router-dom";

import { EditorialPage, Section } from "../components/layout/EditorialPage";

const LICENSES = [
  {
    name: "CC0 1.0 Universal",
    identifier: "CC0-1.0",
    summary:
      "The creator has waived their rights as far as the law allows. You can use, modify and redistribute the work, including commercially, without asking permission.",
    url: "https://creativecommons.org/publicdomain/zero/1.0/",
  },
  {
    name: "Creative Commons Attribution 4.0",
    identifier: "CC-BY-4.0",
    summary:
      "You can use, modify and redistribute the work, including commercially, as long as you credit the creator and indicate any changes. The credit must be reasonable to the medium.",
    url: "https://creativecommons.org/licenses/by/4.0/",
  },
  {
    name: "All rights reserved — link only",
    identifier: "ARR-LINK-ONLY",
    summary:
      "Cabinet shows a preview for reference only. The original file is not redistributed and remains with its creator or source. Reuse requires permission from the rights holder.",
    url: null,
  },
];

export function LicensesPage() {
  return (
    <EditorialPage
      label="Project"
      title="Licensing, plainly."
      intro="Every object records its license. The panel on the object page is the authoritative summary; this page explains what the common licenses mean in practice."
      canonicalPath="/licenses"
      description="How licensing works on Cabinet: CC0, CC-BY and preview-only objects, and what each permits."
    >
      <Section title="The short version">
        <p>
          The creator always holds the rights to their work. Cabinet either has permission to
          redistribute a file or it does not. When it does not, the object is marked{" "}
          <span className="text-ink">preview only</span> and the download panel points to the source
          instead.
        </p>
        <p>
          A download from Cabinet does not transfer ownership. It grants exactly the rights stated in
          the object's license — no more.
        </p>
      </Section>

      <div className="space-y-4">
        {LICENSES.map((license) => (
          <section key={license.identifier} className="border border-line bg-surface p-6">
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <h2 className="text-base font-medium text-ink">{license.name}</h2>
              <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">
                {license.identifier}
              </span>
            </div>
            <p className="mt-3 text-[13px] leading-6 text-muted">{license.summary}</p>
            {license.url && (
              <a
                href={license.url}
                target="_blank"
                rel="noreferrer noopener"
                className="mt-4 inline-block text-[12px] font-medium text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent"
              >
                Read the full license
              </a>
            )}
          </section>
        ))}
      </div>

      <Section title="Attribution in practice">
        <p>
          For CC-BY objects, credit the creator by name, link back to the object or the license, and
          say whether you changed the work. A caption such as “Title by Creator, CC BY 4.0, via
          Cabinet” is usually enough.
        </p>
        <p>
          For CC0 objects, attribution is not required, but it is always appreciated. Cabinet records
          the creator regardless.
        </p>
      </Section>

      <Section title="Reporting a mistake">
        <p>
          If an object is misattributed or its license is wrong, the record can be corrected. Until
          the reporting tool ships, use the{" "}
          <Link to="/about" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent">
            project contact
          </Link>{" "}
          described on the About page.
        </p>
      </Section>
    </EditorialPage>
  );
}
