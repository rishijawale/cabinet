import { Link } from "react-router-dom";

import { EditorialPage, Section } from "../components/layout/EditorialPage";

const REPO_ISSUES = "https://github.com/rishijawale/cabinet/issues";

export function TermsPage() {
  return (
    <EditorialPage
      label="Legal"
      title="Terms, in plain terms."
      intro="The rules for using Cabinet: what downloads grant, what accounts carry, and what the service does not promise. Written by the project's maintainers in plain language; it is not legal advice."
      canonicalPath="/terms"
      description="How Cabinet may be used, what downloads grant, what accounts carry and what the service does not promise."
      updated="18 November 2026"
    >
      <Section title="The arrangement">
        <p>
          Cabinet is an independent, open-source archive of digital artwork. By using it you agree
          to these terms. The service is offered as it exists today, while it is being actively
          built; features may change, move or disappear with the milestones.
        </p>
      </Section>

      <Section title="Using the archive and downloads">
        <p>
          You may browse, link to and share pages from Cabinet freely. Downloading an object grants
          only the rights described by that object's license, shown on the object's license panel
          and summarised on the{" "}
          <Link
            to="/licenses"
            className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent"
          >
            licensing page
          </Link>
          . Where a license requires attribution, keep it when you reuse the work. Where an object
          is preview-only, Cabinet grants no right to the original file at all; the object page says
          so and points to its source.
        </p>
      </Section>

      <Section title="Acceptable use">
        <p>
          Do not attempt to overload the service, circumvent its rate limits, or take the archive
          apart faster than it can respond. Do not use Cabinet to redistribute work in a way its
          license does not permit, and do not misrepresent authorship or strip attribution from
          licensed work.
        </p>
        <p>
          Do not use the service for anything unlawful, and do not use it to publish content you do
          not have the right to publish. Accounts used for these purposes may be suspended.
        </p>
      </Section>

      <Section title="Accounts">
        <p>
          Accounts are optional and may be switched off at any deployment's configuration. When
          available, sign-in is a passwordless email link; keep access to that mailbox, because it
          is what controls the account. You are responsible for activity under your account.
        </p>
        <p>
          An account currently carries your saved objects and nothing else. Cabinet may suspend an
          account that breaks these terms; moderation decisions are recorded so the archive can
          explain itself.
        </p>
      </Section>

      <Section title="Artwork remains with its creators">
        <p>
          Cabinet does not claim ownership of archived work. The creator, or the rights holder they
          name, always remains the holder of the work. Creators can request correction or removal
          through the project's repository issue tracker, and the change is recorded in the
          moderation log.
        </p>
      </Section>

      <Section title="No warranty">
        <p>
          The archive is provided on an as-is basis, without warranty of availability, accuracy or
          fitness for a particular purpose. Metadata may contain mistakes, links may break, and the
          service may be unavailable while it is being worked on. To the fullest extent permitted by
          law, the maintainers are not liable for loss arising from use of the service.
        </p>
      </Section>

      <Section title="Contact and changes">
        <p>
          Questions, correction requests and removal requests go through the project's repository
          issue tracker at{" "}
          <a
            href={REPO_ISSUES}
            target="_blank"
            rel="noreferrer"
            className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent"
          >
            github.com/rishijawale/cabinet
          </a>
          .
        </p>
        <p>
          These terms will be reviewed before the service opens accounts publicly or accepts
          submissions. Material changes will be noted on this page with a new date.
        </p>
      </Section>
    </EditorialPage>
  );
}
