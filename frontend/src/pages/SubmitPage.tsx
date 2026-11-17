import { ArrowLeft, Check, CircleAlert, Send } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import { Button, buttonStyles } from "../components/ui/Button";
import { useAuth } from "../hooks/useAuth";
import { useDocumentMeta } from "../hooks/useDocumentMeta";
import { createSubmission, type Submission, type SubmissionPayload } from "../services/api/engagement";
import { queryKeys, useMySubmissions } from "../services/queries";

const STATUS_LABEL: Record<string, string> = {
  submitted: "In review",
  reviewing: "In review",
  approved: "Approved",
  rejected: "Not accepted",
};

export function SubmitPage() {
  const { status } = useAuth();
  const queryClient = useQueryClient();
  const submissions = useMySubmissions();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [sourceUrl, setSourceUrl] = useState("");
  const [licenseConfirmed, setLicenseConfirmed] = useState(false);
  const [permissionConfirmed, setPermissionConfirmed] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [received, setReceived] = useState<Submission | null>(null);

  useDocumentMeta({
    title: "Submit an object",
    description:
      "Propose an object for Cabinet: every arrival carries permission, attribution and the right license.",
    canonicalPath: "/submit",
  });

  const mutation = useMutation({
    mutationFn: (payload: SubmissionPayload) => createSubmission(payload),
    onSuccess: (submission) => {
      setReceived(submission);
      void queryClient.invalidateQueries({ queryKey: queryKeys.mySubmissions });
    },
    onError: (cause) => {
      setError(cause instanceof Error && cause.message ? cause.message : "The submission could not be sent.");
    },
  });

  if (status === "disabled") {
    return (
      <div className="container-page py-24 sm:py-32">
        <p className="label">Submit</p>
        <h1 className="display mt-4 max-w-2xl text-4xl leading-[0.95] text-ink sm:text-6xl">
          Submissions arrive with accounts.
        </h1>
        <p className="mt-6 max-w-lg text-sm leading-6 text-muted">
          Cabinet is built with contributors, not scraped from them. Submitting needs an account so
          every object has a maker on record — and accounts are not switched on at this deployment
          yet. The archive itself stays open.
        </p>
        <Link to="/explore" className={buttonStyles({ className: "mt-8" })}>
          Explore the archive
        </Link>
      </div>
    );
  }

  if (status === "signedOut" || status === "loading") {
    return (
      <div className="container-page py-24 sm:py-32">
        <p className="label">Submit</p>
        <h1 className="display mt-4 max-w-2xl text-4xl leading-[0.95] text-ink sm:text-6xl">
          Sign in to submit.
        </h1>
        <p className="mt-6 max-w-lg text-sm leading-6 text-muted">
          Submissions are tied to an account so every object in the archive has a maker on record.
          Sign in with a passwordless link and the form opens here.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link to="/login" className={buttonStyles()}>
            Sign in
          </Link>
          <Link to="/guidelines" className={buttonStyles({ variant: "secondary" })}>
            Read the guidelines first
          </Link>
        </div>
      </div>
    );
  }

  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (mutation.isPending) return;
    setError(null);
    mutation.mutate({
      title: title.trim(),
      description: description.trim() || undefined,
      source_url: sourceUrl.trim() || undefined,
      license_confirmation: true,
      permission_confirmation: true,
    });
  };

  const previous = submissions.data?.items ?? [];

  return (
    <div className="container-page py-12 sm:py-16">
      <div className="max-w-2xl">
        <p className="label">Submit</p>
        <h1 className="display mt-5 text-4xl leading-[0.96] text-ink sm:text-6xl">
          Propose an object.
        </h1>
        <p className="mt-6 text-base leading-7 text-muted sm:text-lg sm:leading-8">
          Tell us about work you made, or work you have permission to archive. A moderator reviews
          every submission; media files are exchanged once the proposal is accepted.
        </p>
      </div>

      {received ? (
        <div className="mt-10 max-w-2xl border border-line bg-surface p-6">
          <Check className="h-5 w-5 text-accent" />
          <p className="display mt-4 text-2xl text-ink">Submission received.</p>
          <p className="mt-2 text-sm leading-6 text-muted">
            <span className="font-medium text-ink">{received.title}</span> is in the review queue. If
            it is accepted, you will be asked for the original file and its license details.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Button variant="secondary" onClick={() => setReceived(null)}>
              Submit another
            </Button>
            <Link to="/explore" className={buttonStyles({ variant: "ghost" })}>
              Back to the archive
            </Link>
          </div>
        </div>
      ) : (
        <form onSubmit={submit} className="mt-10 flex max-w-2xl flex-col gap-5">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="submit-title" className="label-tight">
              Title
            </label>
            <input
              id="submit-title"
              required
              maxLength={200}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="What is the object called?"
              className="h-11 border border-line bg-surface px-4 text-sm text-ink outline-none transition-colors placeholder:text-muted focus:border-ink"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="submit-description" className="label-tight">
              Description <span className="text-muted">(optional)</span>
            </label>
            <textarea
              id="submit-description"
              rows={4}
              maxLength={4000}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="A few sentences: what it is, how it was made, why it matters."
              className="border border-line bg-surface px-4 py-3 text-sm leading-6 text-ink outline-none transition-colors placeholder:text-muted focus:border-ink"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="submit-source" className="label-tight">
              Link to the original <span className="text-muted">(optional)</span>
            </label>
            <input
              id="submit-source"
              type="url"
              maxLength={2000}
              value={sourceUrl}
              onChange={(event) => setSourceUrl(event.target.value)}
              placeholder="https://…"
              className="h-11 border border-line bg-surface px-4 text-sm text-ink outline-none transition-colors placeholder:text-muted focus:border-ink"
            />
          </div>

          <div className="flex flex-col gap-3 border border-line bg-surface-muted p-5">
            <label className="flex cursor-pointer items-start gap-3 text-[13px] leading-5 text-muted">
              <input
                type="checkbox"
                required
                checked={licenseConfirmed}
                onChange={(event) => setLicenseConfirmed(event.target.checked)}
                className="mt-0.5 h-4 w-4 shrink-0 accent-[var(--accent)]"
              />
              <span>
                The work is released under a license I will name — CC0, CC-BY, or a link-only
                arrangement — as described on the{" "}
                <Link to="/licenses" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent">
                  licensing page
                </Link>
                .
              </span>
            </label>
            <label className="flex cursor-pointer items-start gap-3 text-[13px] leading-5 text-muted">
              <input
                type="checkbox"
                required
                checked={permissionConfirmed}
                onChange={(event) => setPermissionConfirmed(event.target.checked)}
                className="mt-0.5 h-4 w-4 shrink-0 accent-[var(--accent)]"
              />
              <span>
                I made this work, or I have the right holder's permission to archive it.
              </span>
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-4">
            <Button type="submit" disabled={mutation.isPending || !title.trim()}>
              <Send className="h-4 w-4" />
              {mutation.isPending ? "Sending…" : "Send submission"}
            </Button>
            {error && (
              <p className="inline-flex items-center gap-2 text-sm text-accent">
                <CircleAlert className="h-4 w-4" /> {error}
              </p>
            )}
          </div>
        </form>
      )}

      {previous.length > 0 && (
        <section className="mt-16 max-w-2xl border-t border-line pt-8">
          <h2 className="display text-2xl text-ink">Your submissions</h2>
          <ul className="mt-5 divide-y divide-line border border-line bg-surface">
            {previous.map((item) => (
              <li key={item.id} className="flex items-center justify-between gap-4 px-5 py-4">
                <div className="min-w-0">
                  <p className="truncate text-sm font-medium text-ink">{item.title}</p>
                  <p className="mt-0.5 truncate text-[12px] text-muted">
                    {item.review_notes ?? "Awaiting review by a moderator."}
                  </p>
                </div>
                <span className="label-tight shrink-0">{STATUS_LABEL[item.status] ?? item.status}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <p className="mt-10 flex max-w-2xl items-start gap-2 text-[12px] leading-6 text-muted">
        <ArrowLeft className="mt-1 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
        Not sure what belongs in the archive? The{" "}
        <Link to="/guidelines" className="text-ink underline decoration-line-strong underline-offset-4 hover:decoration-accent">
          submission guidelines
        </Link>{" "}
        explain what we look for and what we turn away.
      </p>
    </div>
  );
}
