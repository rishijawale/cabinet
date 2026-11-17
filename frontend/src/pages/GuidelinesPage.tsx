import { Link } from "react-router-dom";

import { EditorialPage, Section } from "../components/layout/EditorialPage";

export function GuidelinesPage() {
  return (
    <EditorialPage
      label="Project"
      title="Submission guidelines."
      intro="What Cabinet looks for, and what we need from you before an object can enter the archive. The submission workflow itself opens in a later milestone."
      canonicalPath="/guidelines"
      description="Cabinet submission guidelines: attribution, licensing, file quality and editorial criteria."
    >
      <Section title="What belongs here">
        <p>
          Cabinet collects digital-native work with a clear point of view: ASCII and text art,
          wallpapers, pixel art, small web experiments, interface artifacts and visual culture from
          the history of computing. The through-line is care rather than medium.
        </p>
        <p>
          We are less interested in volume than in intention. A single 32×32 sprite that someone
          spent a week on belongs here; a folder of exports does not.
        </p>
      </Section>

      <Section title="You must have the right to share it">
        <p>
          Only submit work you made, or work you have explicit permission to archive. Scraped
          galleries, reposted art with a credit in the caption, and “found on the internet” are not
          acceptable sources.
        </p>
        <p>
          If the work is already under a license, tell us which one. If you are the creator, choose
          the license you want: CC0, CC-BY, or preview-only with the original hosted elsewhere.
        </p>
      </Section>

      <Section title="Files and metadata">
        <p>
          Send the highest-quality original you have, not a screenshot. Include a title, a short
          description, the tools used if they matter, and the year. Pixel art should keep its native
          resolution; text art should arrive as plain UTF-8 text.
        </p>
        <p>
          We prefer lossless formats where they are appropriate. Large files are fine — the archive
          is built to keep originals, not thumbnails.
        </p>
      </Section>

      <Section title="Editorial process">
        <p>
          Every submission is reviewed by a person. We may ask for a better file, a license
          clarification, or a different description. Acceptance is not guaranteed and is not a
          judgement of quality.
        </p>
        <p>
          If an object is removed later, the record stays in the moderation log so the archive can
          explain itself. Creators can ask for their work to be removed at any time.
        </p>
      </Section>

      <Section title="Submitting">
        <p>
          The submission form lives on the{" "}
          <Link to="/submit" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent">
            submit page
          </Link>{" "}
          and needs an account, because every object in the archive has a maker on record. Proposals
          are reviewed by a person before anything is published; if a proposal is accepted, you will
          be asked for the original file and its license details.
        </p>
      </Section>
    </EditorialPage>
  );
}
