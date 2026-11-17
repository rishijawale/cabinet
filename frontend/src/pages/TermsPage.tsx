import { EditorialPage, Section } from "../components/layout/EditorialPage";

export function TermsPage() {
  return (
    <EditorialPage
      label="Legal"
      title="Terms, in draft."
      intro="A working draft for the archive milestone. The archive is provided as-is while the service is being built; this page will be reviewed before accounts, submissions and downloads are expanded."
      canonicalPath="/terms"
      description="Cabinet's draft terms for the archive milestone."
      updated="17 November 2026"
    >
      <Section title="Using the archive">
        <p>
          You may browse, link to and share pages from Cabinet. Downloading an object grants only the
          rights described by that object's license. Where an object is preview-only, Cabinet does not
          grant any right to the original file.
        </p>
        <p>
          Do not attempt to overload the service, bypass rate limits, or use the archive to
          redistribute work in a way its license does not permit.
        </p>
      </Section>

      <Section title="Artwork remains with its creators">
        <p>
          Cabinet does not claim ownership of archived work. Creators can request correction or
          removal at any time, and the archive will record the change in its moderation log.
        </p>
      </Section>

      <Section title="No warranty">
        <p>
          The archive is provided on an as-is basis during development. Metadata may contain mistakes,
          links may break, and the service may be unavailable while it is being worked on. Nothing on
          this page is legal advice.
        </p>
      </Section>

      <Section title="Changes">
        <p>
          These terms will be replaced by a reviewed version before the service opens accounts or
          accepts public submissions. Material changes will be noted on this page.
        </p>
      </Section>
    </EditorialPage>
  );
}
