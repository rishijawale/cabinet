import { EditorialPage, Section } from "../components/layout/EditorialPage";

export function PrivacyPage() {
  return (
    <EditorialPage
      label="Legal"
      title="Privacy, in plain terms."
      intro="What Cabinet records when you browse, save or sign in. Written in plain language by the project's maintainers rather than copied from a template; it is not legal advice, and it will be re-reviewed before submissions open."
      canonicalPath="/privacy"
      description="What Cabinet stores when you browse, save or sign in: server logs, browser-local saves and optional Supabase accounts."
      updated="18 November 2026"
    >
      <Section title="The short version">
        <p>
          Cabinet runs no advertising, no third-party analytics and no cross-site tracking. Browsing
          the archive requires no account, and the public archive pages do not set tracking cookies.
          The data that exists about you is limited to short-lived request logs, your own browser
          storage, and — only if you sign in — the account record described below.
        </p>
      </Section>

      <Section title="What the server records about browsing">
        <p>
          The API keeps standard request logs: the requesting IP address, user agent, path and
          response status. They exist for rate limiting and debugging, and are the kind of record
          nearly every web server keeps. Rate limiting is applied per client IP address and held in
          memory only; it is not written to the database.
        </p>
        <p>
          Each object carries aggregate view and download counters. Download events are also
          recorded per object with a timestamp — useful for knowing what the archive is keeping
          alive — but they are never linked to an account, even when you are signed in.
        </p>
      </Section>

      <Section title="What your browser stores">
        <p>
          Two things live in your browser's local storage: your theme preference under{" "}
          <code>cabinet-theme</code>, and the objects you have saved under <code>cabinet-saved</code>.
          Both stay on your device. Clearing them from your browser settings removes them entirely.
        </p>
        <p>
          When you sign out or visit signed-out, saved objects return to this local store. Nothing
          in it is sent to the server unless you sign in and the one-time merge moves it into your
          account.
        </p>
      </Section>

      <Section title="Accounts, when they are switched on">
        <p>
          Accounts are optional and are currently disabled at this deployment's configuration. When
          enabled, sign-in is a passwordless magic link handled by Supabase Auth; Cabinet never sees
          or stores a password.
        </p>
        <p>
          On your first sign-in, Cabinet verifies the identity token against Supabase's published
          keys and creates a local account holding the claims it received: your Supabase user
          identifier, your email address (used to link the account to work already credited to that
          email), a display name from your profile — or the front of your email address if none is
          set — and your avatar URL, if your profile provides one. Signing in also links your saved
          objects to the account; from then on your saves live server-side.
        </p>
        <p>
          Supabase is the only third party involved, and only in this role: it processes sign-ins
          and holds your auth record. It receives no browsing data from Cabinet, and Cabinet receives
          from it only the claims listed above.
        </p>
      </Section>

      <Section title="What Cabinet never does">
        <p>
          Your email address is not used for marketing, because there is no marketing. Data is not
          sold, shared or brokered, because there is no such arrangement. Profiles are not built
          across sites, and behaviour is not profiled for advertising, because there is no
          advertising.
        </p>
      </Section>

      <Section title="Deleting your data">
        <p>
          Browser-local data (theme and saves) is yours to clear at any time. For an account, ask
          the maintainers through the project's repository issue tracker; the account and its saved
          objects will be removed. Aggregate counters — views and downloads per object — are not
          attributable to individuals, so they are not reverted on request.
        </p>
      </Section>

      <Section title="Changes">
        <p>
          Material changes to this notice will be recorded on this page with a new date. Before
          public submissions open, the notice will be reviewed again, because submissions will
          necessarily record more about the people making them.
        </p>
      </Section>
    </EditorialPage>
  );
}
