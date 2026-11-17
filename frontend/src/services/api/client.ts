import type { ArtworkQuery } from "../../types/api";

const API_BASE =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000/api/v1";

type QueryValue = string | number | boolean | undefined | null | string[];

export class ApiError extends Error {
  code: string;
  status: number;
  details: { field: string; message: string }[];

  constructor(
    message: string,
    options: {
      code?: string;
      status?: number;
      details?: { field: string; message: string }[];
    } = {},
  ) {
    super(message);
    this.name = "ApiError";
    this.code = options.code ?? "REQUEST_FAILED";
    this.status = options.status ?? 500;
    this.details = options.details ?? [];
  }
}

function buildQuery(params?: Record<string, QueryValue>): string {
  if (!params) return "";
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value === undefined || value === null || value === "") continue;
    if (Array.isArray(value)) {
      for (const item of value) {
        if (item !== "") search.append(key, item);
      }
    } else {
      search.set(key, String(value));
    }
  }
  const query = search.toString();
  return query ? `?${query}` : "";
}

export async function request<T>(
  path: string,
  params?: Record<string, QueryValue>,
  init?: RequestInit,
): Promise<{ data: T; meta: Record<string, unknown> }> {
  const response = await fetch(`${API_BASE}${path}${buildQuery(params)}`, {
    headers: { Accept: "application/json" },
    ...init,
  });

  if (!response.ok) {
    let payload: {
      error?: { code?: string; message?: string; details?: { field: string; message: string }[] };
    } = {};
    try {
      payload = await response.json();
    } catch {
      // Non-JSON error response.
    }
    throw new ApiError(payload.error?.message ?? "The archive could not be reached.", {
      code: payload.error?.code,
      status: response.status,
      details: payload.error?.details,
    });
  }

  return (await response.json()) as { data: T; meta: Record<string, unknown> };
}

export function artworkParams(query: ArtworkQuery): Record<string, QueryValue> {
  return {
    q: query.q,
    category: query.category,
    tags: query.tags,
    format: query.format,
    media_type: query.media_type,
    orientation: query.orientation,
    sort: query.sort,
    page: query.page,
    limit: query.limit,
  };
}
