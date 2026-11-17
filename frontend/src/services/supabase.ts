import type { SupabaseClient } from "@supabase/supabase-js";

/**
 * Supabase Auth, config-driven.
 *
 * Both VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be present for auth
 * to exist at all; otherwise the app behaves exactly as before (local saves).
 * The client module itself is dynamically imported so the ~15 kB dependency
 * never reaches the browser when auth is switched off.
 */

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const authEnabled = Boolean(SUPABASE_URL && SUPABASE_ANON_KEY);

let clientPromise: Promise<SupabaseClient> | null = null;

export function getSupabase(): Promise<SupabaseClient> | null {
  if (!authEnabled) return null;
  clientPromise ??= import("@supabase/supabase-js").then((module) =>
    module.createClient(SUPABASE_URL as string, SUPABASE_ANON_KEY as string, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true,
      },
    }),
  );
  return clientPromise;
}

/** Current session's bearer token, or null when auth is off or signed out. */
export async function getAccessToken(): Promise<string | null> {
  const client = await getSupabase();
  if (!client) return null;
  const { data } = await client.auth.getSession();
  return data.session?.access_token ?? null;
}
