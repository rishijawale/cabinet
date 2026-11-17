import { EditorialPage, Section } from "../components/layout/EditorialPage";

export function PrivacyPage() {
  return (
    <EditorialPage
      label="Legal"
      title="Privacy, in draft."
      intro="This is a working draft for the archive milestone. It will be reviewed before accounts and submissions are introduced."
      canonicalPath="/privacy"
      description="Cabinet's draft privacy notice for the archive milestone."
      updated="17 November 2026"
    >
      <Section title="What this release stores">
        <p>
          Browsing the archive does not require an account. The only data stored in your browser is
          your theme preference and the list of objects you have saved; both live in local storage and
          can be cleared from your browser settings at any time.
        </p>
        <p>
          Server logs record standard request information — IP address, user agent, path and response
          status — for rate limiting and debugging. Aggregate view and download counters are stored
          against each object without identifying individual visitors.
        </p>
      </Section>

      <Section title="What this release does not do">
        <p>
          There is no advertising, no third-party analytics, and no cross-site tracking. No account
          data is collected because accounts are not part of this milestone.
        </p>
      </Section>

      <Section title="When accounts arrive">
        <p>
          Authentication will be handled by Supabase. This notice will be replaced with a reviewed
          policy covering account data, deletion and retention before that feature ships. Continuing to
          operate without one would be dishonest, so it is a release blocker rather than a nice-to-have.
        </p>
      </Section>
    </EditorialPage>
  );
}
