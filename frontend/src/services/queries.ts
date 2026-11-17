import { keepPreviousData, useQuery } from "@tanstack/react-query";

import type { ArtworkQuery } from "../types/api";
import {
  fetchArtwork,
  fetchArtworks,
  fetchCategories,
  fetchCollection,
  fetchCollections,
  fetchRandomArtwork,
} from "./api/archive";

export const queryKeys = {
  artworks: (query: ArtworkQuery) => ["artworks", query] as const,
  artwork: (slug: string) => ["artwork", slug] as const,
  random: ["artwork", "random"] as const,
  categories: ["categories"] as const,
  collections: ["collections"] as const,
  collection: (slug: string) => ["collection", slug] as const,
};

export function useArtworks(query: ArtworkQuery) {
  return useQuery({
    queryKey: queryKeys.artworks(query),
    queryFn: () => fetchArtworks(query),
    placeholderData: keepPreviousData,
  });
}

export function useArtwork(slug: string | undefined) {
  return useQuery({
    queryKey: queryKeys.artwork(slug ?? ""),
    queryFn: () => fetchArtwork(slug as string),
    enabled: Boolean(slug),
  });
}

export function useRandomArtwork() {
  return useQuery({
    queryKey: queryKeys.random,
    queryFn: fetchRandomArtwork,
    staleTime: 0,
    gcTime: 0,
  });
}

export function useCategories() {
  return useQuery({
    queryKey: queryKeys.categories,
    queryFn: fetchCategories,
    staleTime: 5 * 60_000,
  });
}

export function useCollections() {
  return useQuery({
    queryKey: queryKeys.collections,
    queryFn: fetchCollections,
    staleTime: 5 * 60_000,
  });
}

export function useCollection(slug: string | undefined) {
  return useQuery({
    queryKey: queryKeys.collection(slug ?? ""),
    queryFn: () => fetchCollection(slug as string),
    enabled: Boolean(slug),
  });
}
