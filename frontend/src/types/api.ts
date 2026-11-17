export type MediaType = "image" | "video" | "animation" | "text";
export type Orientation = "landscape" | "portrait" | "square";

export interface CategoryBrief {
  id: string;
  name: string;
  slug: string;
}

export interface Category extends CategoryBrief {
  description: string | null;
  cover_image: string | null;
  display_order: number;
  artwork_count: number;
}

export interface License {
  id: string;
  name: string;
  identifier: string;
  license_url: string | null;
  attribution_required: boolean;
  commercial_use_allowed: boolean;
  modification_allowed: boolean;
  redistribution_allowed: boolean;
}

export interface Creator {
  id: string | null;
  username: string | null;
  display_name: string;
  avatar_url: string | null;
  external_name: string | null;
  anonymous: boolean;
}

export interface Tag {
  name: string;
  slug: string;
}

export interface PreviewSet {
  thumb: string;
  card: string;
  full: string;
  alt: string;
}

export interface Artwork {
  id: string;
  slug: string;
  title: string;
  category: CategoryBrief;
  creator: Creator;
  media_type: MediaType;
  file_format: string;
  width: number | null;
  height: number | null;
  orientation: Orientation;
  preview: PreviewSet;
  license: License | null;
  redistributable: boolean;
  downloadable: boolean;
  featured: boolean;
  published_at: string | null;
  tags: Tag[];
}

export interface ArtworkDetail extends Artwork {
  description: string | null;
  original_source_url: string | null;
  rights_notes: string | null;
  file_size: number;
  text_url: string | null;
  view_count: number;
  download_count: number;
  created_at: string;
  updated_at: string;
  related: Artwork[];
}

export interface Collection {
  id: string;
  slug: string;
  title: string;
  description: string | null;
  cover: PreviewSet | null;
  cover_artwork_slug: string | null;
  curator: Creator | null;
  artwork_count: number;
  is_featured: boolean;
}

export interface CollectionDetail extends Collection {
  artworks: Artwork[];
  created_at: string;
}

export interface PageMeta {
  page: number;
  limit: number;
  total: number;
  pages: number;
}

export interface Paginated<T> {
  data: T[];
  meta: PageMeta;
}

export interface Envelope<T> {
  data: T;
  meta: Record<string, unknown>;
}

export interface DownloadInfo {
  downloadable: boolean;
  url?: string;
  external_url?: string | null;
  reason?: string;
  expires_at?: string;
  file_format?: string;
  file_size?: number;
  license?: License | null;
}

export interface ArtworkQuery {
  q?: string;
  category?: string;
  tags?: string[];
  format?: string[];
  media_type?: string[];
  orientation?: string[];
  sort?: "recent" | "popular" | "oldest" | "relevance";
  page?: number;
  limit?: number;
}
