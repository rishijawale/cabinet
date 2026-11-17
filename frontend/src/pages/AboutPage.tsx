import { Link } from "react-router-dom";

import { EditorialPage, Section } from "../components/layout/EditorialPage";

export function AboutPage() {
  return (
    <EditorialPage
      label="About"
      title="A small, deliberate archive."
      intro="Cabinet keeps digital artwork that deserves a longer look: ASCII drawings, quiet wallpapers, pixel art and the visual culture that grew up around computers."
      canonicalPath="/about"
      description="Cabinet is a curated archive of digital artwork and internet culture, built with contributors rather than scraped from them."
    >
      <Section title="Why an archive?">
        <p>
          The internet is very good at producing things and very bad at keeping them. Work that took
          hours to make disappears behind a dead link, a redesign, or a platform that quietly changes
          its mind. Cabinet exists to slow that down.
        </p>
        <p>
          We are interested in work that is specific: a character grid, a limited palette, a
          wallpaper composed to do almost nothing at all. Objects are chosen by people, not ranked by
          an algorithm.
        </p>
      </Section>

      <Section title="How objects arrive">
        <p>
          Every object in the archive is either made for Cabinet or contributed with permission. We
          do not scrape galleries or re-host files we have no right to redistribute. When Cabinet can
          only show a preview, the object says so and points to its source.
        </p>
        <p>
          Licenses are recorded per object. Some are CC0, some require attribution, and some are
          link-only. The license panel on each object is the authoritative summary; the creator
          always remains the rights holder.
        </p>
      </Section>

      <Section title="What comes next">
        <p>
          This release is the archive itself: browsing, search, exhibitions and downloads. Accounts,
          favourites that follow you across devices, submissions and a curation studio are being
          built next.
        </p>
        <p>
          Until then, the{" "}
          <Link to="/guidelines" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent">
            guidelines
          </Link>{" "}
          explain what we look for, and the{" "}
          <Link to="/licenses" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent">
            licensing page
          </Link>{" "}
          explains how use works.
        </p>
      </Section>

      <Section title="Colophon">
        <p>
          Cabinet is set in Instrument Serif and Inter, with JetBrains Mono for the parts that need to
          behave like a terminal. The interface is built with React and a FastAPI service; the archive
          is stored in PostgreSQL. Seed objects are procedurally generated for this project and
          released under CC0.
        </p>
      </Section>
    </EditorialPage>
  );
}
