import type {
  Artwork,
  ArtworkDetail,
  ArtworkQuery,
  Category,
  Collection,
  CollectionDetail,
  DownloadInfo,
} from "../../types/api";
import { artworkParams, request } from "./client";

export async function fetchArtworks(
  query: ArtworkQuery,
): Promise<{ data: Artwork[]; meta: { page: number; limit: number; total: number; pages: number } }> {
  const response = await request<Artwork[]>("/artworks", artworkParams(query));
  return response as { data: Artwork[]; meta: { page: number; limit: number; total: number; pages: number } };
}

export async function fetchArtwork(slug: string): Promise<ArtworkDetail> {
  const response = await request<ArtworkDetail>(`/artworks/${encodeURIComponent(slug)}`);
  return response.data;
}

export async function fetchRandomArtwork(): Promise<Artwork> {
  const response = await request<Artwork>("/artworks/random");
  return response.data;
}

export async function fetchCategories(): Promise<Category[]> {
  const response = await request<Category[]>("/categories");
  return response.data;
}

export async function fetchCollections(): Promise<Collection[]> {
  const response = await request<Collection[]>("/collections");
  return response.data;
}

export async function fetchCollection(slug: string): Promise<CollectionDetail> {
  const response = await request<CollectionDetail>(`/collections/${encodeURIComponent(slug)}`);
  return response.data;
}

export async function requestDownload(slug: string): Promise<DownloadInfo> {
  const response = await request<DownloadInfo>(
    `/artworks/${encodeURIComponent(slug)}/download`,
  );
  return response.data;
}

export async function fetchText(url: string): Promise<string> {
  const response = await fetch(url);
  if (!response.ok) throw new Error("The text rendering could not be loaded.");
  return response.text();
}
