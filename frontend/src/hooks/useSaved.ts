import { useSyncExternalStore } from "react";

import type { Artwork } from "../types/api";

export interface SavedItem {
  slug: string;
  title: string;
  categoryName: string;
  categorySlug: string;
  creatorName: string;
  preview: string;
  thumb: string;
  alt: string;
  fileFormat: string;
  savedAt: string;
}

const STORAGE_KEY = "cabinet-saved";
const listeners = new Set<() => void>();

function read(): SavedItem[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as SavedItem[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

let cache: SavedItem[] = typeof window === "undefined" ? [] : read();

function write(next: SavedItem[]) {
  cache = next;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  } catch {
    // Quota or private mode: keep the in-memory value for this session.
  }
  for (const listener of listeners) listener();
}

function subscribe(listener: () => void) {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function snapshot() {
  return cache;
}

export function toSavedItem(artwork: Artwork): SavedItem {
  return {
    slug: artwork.slug,
    title: artwork.title,
    categoryName: artwork.category.name,
    categorySlug: artwork.category.slug,
    creatorName: artwork.creator.display_name,
    preview: artwork.preview.card,
    thumb: artwork.preview.thumb,
    alt: artwork.preview.alt,
    fileFormat: artwork.file_format,
    savedAt: new Date().toISOString(),
  };
}

export function useSaved() {
  const items = useSyncExternalStore(subscribe, snapshot, snapshot);

  const toggle = (artwork: Artwork) => {
    if (cache.some((item) => item.slug === artwork.slug)) {
      write(cache.filter((item) => item.slug !== artwork.slug));
    } else {
      write([toSavedItem(artwork), ...cache]);
    }
  };

  const remove = (slug: string) => {
    write(cache.filter((item) => item.slug !== slug));
  };

  const isSaved = (slug: string) => items.some((item) => item.slug === slug);

  return { items, toggle, remove, isSaved };
}

/** Non-hook accessors for the local store, used by the sign-in merge. */
export function getLocalSavedSlugs(): string[] {
  return cache.map((item) => item.slug);
}

export function clearLocalSaved(): void {
  write([]);
}
