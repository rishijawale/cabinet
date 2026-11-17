import type { Artwork } from "../../types/api";
import { request } from "./client";

export interface Account {
  id: string;
  username: string;
  display_name: string;
  email: string | null;
  avatar_url: string | null;
  status: string;
  created_at: string;
}

export interface FavoriteAction {
  saved: boolean;
  already_saved?: boolean;
  favorite_count: number;
}

export async function fetchAccount(): Promise<Account> {
  const response = await request<Account>("/auth/me");
  return response.data;
}

export async function fetchFavorites(): Promise<Artwork[]> {
  const response = await request<Artwork[]>("/favorites");
  return response.data;
}

export async function addFavorite(slug: string): Promise<FavoriteAction> {
  const response = await request<FavoriteAction>(
    `/favorites/${encodeURIComponent(slug)}`,
    undefined,
    { method: "POST" },
  );
  return response.data;
}

export async function removeFavorite(slug: string): Promise<FavoriteAction> {
  const response = await request<FavoriteAction>(
    `/favorites/${encodeURIComponent(slug)}`,
    undefined,
    { method: "DELETE" },
  );
  return response.data;
}

/**
 * Push locally saved slugs to the server after sign-in. Idempotent: the API
 * ignores favorites that already exist.
 */
export async function mergeLocalFavorites(slugs: string[]): Promise<void> {
  for (const slug of slugs) {
    await addFavorite(slug);
  }
}
