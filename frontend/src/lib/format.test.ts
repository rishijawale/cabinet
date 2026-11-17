import { describe, expect, it } from "vitest";

import type { Artwork, License } from "../types/api";
import {
  downloadName,
  formatBytes,
  formatDimensions,
  formatMediaType,
  initials,
  licenseSummary,
} from "./format";

const license: License = {
  id: "00000000-0000-0000-0000-000000000001",
  name: "CC0 1.0 Universal",
  identifier: "CC0-1.0",
  license_url: "https://creativecommons.org/publicdomain/zero/1.0/",
  attribution_required: false,
  commercial_use_allowed: true,
  modification_allowed: true,
  redistribution_allowed: true,
};

function artwork(overrides: Partial<Artwork> = {}): Artwork {
  return {
    id: "00000000-0000-0000-0000-000000000002",
    slug: "quiet-observer",
    title: "Quiet Observer",
    category: { id: "00000000-0000-0000-0000-000000000003", name: "ASCII", slug: "ascii" },
    creator: { id: null, username: null, display_name: "Ivo Sato", avatar_url: null, external_name: null, anonymous: false },
    media_type: "text",
    file_format: "txt",
    width: 96,
    height: 40,
    orientation: "landscape",
    preview: { thumb: "", card: "", full: "", alt: "" },
    license,
    redistributable: true,
    downloadable: true,
    featured: false,
    published_at: "2026-01-01T00:00:00Z",
    tags: [],
    ...overrides,
  };
}

describe("formatBytes", () => {
  it("returns an em dash for empty files", () => {
    expect(formatBytes(0)).toBe("—");
  });

  it("scales units and keeps one decimal below ten", () => {
    expect(formatBytes(512)).toBe("512 B");
    expect(formatBytes(1536)).toBe("1.5 KB");
    expect(formatBytes(5 * 1024 * 1024)).toBe("5.0 MB");
    expect(formatBytes(52 * 1024)).toBe("52 KB");
  });
});

describe("formatDimensions", () => {
  it("labels character grids and pixel images differently", () => {
    expect(formatDimensions(artwork())).toBe("96 × 40 characters");
    expect(formatDimensions(artwork({ media_type: "image", width: 2400, height: 1350 }))).toBe(
      "2400 × 1350 px",
    );
  });

  it("falls back when dimensions are unknown", () => {
    expect(formatDimensions(artwork({ width: null, height: null }))).toBe("—");
  });
});

describe("licenseSummary", () => {
  it("describes a redistributable license", () => {
    expect(licenseSummary(license)).toBe(
      "CC0 1.0 Universal. Permits commercial use, modification, redistribution.",
    );
  });

  it("marks preview-only objects", () => {
    expect(
      licenseSummary({ ...license, redistribution_allowed: false, name: "All rights reserved" }),
    ).toContain("Preview only");
  });

  it("handles missing licenses", () => {
    expect(licenseSummary(null)).toBe("Licensing information unavailable.");
  });
});

describe("small helpers", () => {
  it("builds initials from the first two words", () => {
    expect(initials("Mara Ellis")).toBe("ME");
    expect(initials("  ivo   sato ")).toBe("IS");
  });

  it("uses a stable download filename", () => {
    expect(downloadName(artwork())).toBe("quiet-observer.txt");
  });

  it("labels known media types and preserves unknown ones", () => {
    expect(formatMediaType("text")).toBe("Plain text");
    expect(formatMediaType("hologram")).toBe("hologram");
  });
});
