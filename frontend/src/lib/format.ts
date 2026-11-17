import type { Artwork, License } from "../types/api";

export function formatBytes(bytes: number): string {
  if (!bytes) return "—";
  const units = ["B", "KB", "MB", "GB"];
  const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
  const value = bytes / 1024 ** exponent;
  return `${value >= 10 || exponent === 0 ? Math.round(value) : value.toFixed(1)} ${units[exponent]}`;
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Intl.DateTimeFormat("en", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(new Date(value));
}

export function formatDimensions(artwork: Artwork): string {
  if (!artwork.width || !artwork.height) return "—";
  if (artwork.media_type === "text") {
    return `${artwork.width} × ${artwork.height} characters`;
  }
  return `${artwork.width} × ${artwork.height} px`;
}

export function formatMediaType(value: string): string {
  const labels: Record<string, string> = {
    image: "Still image",
    text: "Plain text",
    animation: "Animation",
    video: "Video",
  };
  return labels[value] ?? value;
}

export function licenseSummary(license: License | null): string {
  if (!license) return "Licensing information unavailable.";
  if (!license.redistribution_allowed) {
    return `${license.name}. Preview only; the original file is hosted at the source.`;
  }
  const freedoms: string[] = [];
  if (license.commercial_use_allowed) freedoms.push("commercial use");
  if (license.modification_allowed) freedoms.push("modification");
  freedoms.push("redistribution");
  return `${license.name}. Permits ${freedoms.join(", ")}.`;
}

export function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join("");
}

export function downloadName(artwork: Artwork): string {
  return `${artwork.slug}.${artwork.file_format}`;
}
