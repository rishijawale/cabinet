/** Reports and submissions — engagement endpoints. */

import { request } from "./client";

export interface ReportPayload {
  reason: string;
  details?: string;
}

export interface ReportReceipt {
  report_id: string;
  status: string;
  artwork_slug: string;
}

export async function reportArtwork(
  slug: string,
  payload: ReportPayload,
): Promise<ReportReceipt> {
  const response = await request<ReportReceipt>(
    `/artworks/${encodeURIComponent(slug)}/report`,
    undefined,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
  return response.data;
}

export interface Submission {
  id: string;
  title: string;
  description: string | null;
  source_url: string | null;
  license_confirmation: boolean;
  permission_confirmation: boolean;
  status: string;
  created_at: string;
  reviewed_at: string | null;
  review_notes: string | null;
}

export interface SubmissionPayload {
  title: string;
  description?: string;
  source_url?: string;
  license_confirmation: true;
  permission_confirmation: true;
}

export interface SubmissionListResult {
  items: Submission[];
  total: number;
}

export async function createSubmission(payload: SubmissionPayload): Promise<Submission> {
  const response = await request<Submission>("/submissions", undefined, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return response.data;
}

export async function fetchMySubmissions(page = 1): Promise<SubmissionListResult> {
  const response = await request<Submission[]>("/submissions", { page, limit: 48 });
  return {
    items: response.data,
    total: Number(response.meta.total ?? response.data.length),
  };
}
