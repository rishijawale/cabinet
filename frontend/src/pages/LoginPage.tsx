import { Mail, Send } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { buttonStyles } from "../components/ui/Button";
import { useAuth } from "../hooks/useAuth";
import { useDocumentMeta } from "../hooks/useDocumentMeta";

export function LoginPage() {
  const { status, account, sendMagicLink, signOut } = useAuth();
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);
  const [sentTo, setSentTo] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useDocumentMeta({
    title: "Sign in",
    description: "Sign in to Cabinet so your saved objects follow you between devices.",
    canonicalPath: "/login",
  });

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!email.trim() || sending) return;
    setSending(true);
    setError(null);
    try {
      await sendMagicLink(email.trim());
      setSentTo(email.trim());
      setEmail("");
    } catch (cause) {
      setError(
        cause instanceof Error && cause.message
          ? cause.message
          : "The sign-in link could not be sent.",
      );
    } finally {
      setSending(false);
    }
  };

  if (status === "disabled") {
    return (
      <div className="container-page py-24 sm:py-32">
        <p className="label">Accounts</p>
        <h1 className="display mt-4 max-w-2xl text-4xl leading-[0.95] text-ink sm:text-6xl">
          Accounts aren't switched on yet.
        </h1>
        <p className="mt-6 max-w-lg text-sm leading-6 text-muted">
          Cabinet currently runs without accounts, so saving stays on this device. When accounts
          arrive, this page will let you sign in and take your saved objects with you.
        </p>
        <Link to="/explore" className={buttonStyles({ className: "mt-8" })}>
          Explore the archive
        </Link>
      </div>
    );
  }

  if (status === "signedIn" && account) {
    return (
      <div className="container-page py-24 sm:py-32">
        <p className="label">Signed in</p>
        <h1 className="display mt-4 text-4xl leading-[0.95] text-ink sm:text-6xl">
          {account.display_name}
        </h1>
        <p className="mt-6 max-w-lg text-sm leading-6 text-muted">
          Signed in as{" "}
          <span className="font-mono text-ink">{account.email ?? account.username}</span>. Favorites
          you save now follow this account between devices.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/saved" className={buttonStyles()}>
            Saved objects
          </Link>
          <button type="button" onClick={() => void signOut()} className={buttonStyles({ variant: "secondary" })}>
            Sign out
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container-page py-24 sm:py-32">
      <p className="label">Accounts</p>
      <h1 className="display mt-4 max-w-2xl text-4xl leading-[0.95] text-ink sm:text-6xl">
        Sign in to Cabinet.
      </h1>
      <p className="mt-6 max-w-lg text-sm leading-6 text-muted">
        We use sign-in links — no password to remember. Enter your email and we'll send a single-use
        link; opening it signs you in on this device.
      </p>

      {sentTo ? (
        <div className="mt-10 max-w-lg border border-line bg-surface p-6">
          <Mail className="h-5 w-5 text-accent" />
          <p className="display mt-4 text-2xl text-ink">Check your inbox.</p>
          <p className="mt-2 text-sm leading-6 text-muted">
            A sign-in link is on its way to <span className="font-mono text-ink">{sentTo}</span>. It
            expires after a short while and can be used once.
          </p>
        </div>
      ) : (
        <form onSubmit={submit} className="mt-10 flex max-w-lg flex-col gap-4">
          <label htmlFor="login-email" className="label-tight">
            Email address
          </label>
          <input
            id="login-email"
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            placeholder="you@example.com"
            className="h-11 border border-line bg-surface px-4 text-sm text-ink outline-none transition-colors placeholder:text-muted focus:border-ink"
          />
          <div className="flex flex-wrap items-center gap-4">
            <button type="submit" disabled={sending || !email.trim()} className={buttonStyles()}>
              <Send className="h-4 w-4" />
              {sending ? "Sending…" : "Send sign-in link"}
            </button>
            {error && <p className="text-sm text-accent">{error}</p>}
          </div>
        </form>
      )}

      <p className="mt-12 max-w-lg text-[12px] leading-6 text-muted">
        Signing in also merges anything you saved in this browser into your account, once.
      </p>
    </div>
  );
}
