import { useEffect } from "react";

interface MetaOptions {
  title: string;
  description?: string;
  image?: string;
  canonicalPath?: string;
  type?: "website" | "article";
  jsonLd?: Record<string, unknown>;
}

function setMeta(attribute: "name" | "property", key: string, content: string) {
  let element = document.head.querySelector<HTMLMetaElement>(`meta[${attribute}="${key}"]`);
  if (!element) {
    element = document.createElement("meta");
    element.setAttribute(attribute, key);
    document.head.appendChild(element);
  }
  element.setAttribute("content", content);
}

export function useDocumentMeta({
  title,
  description,
  image,
  canonicalPath,
  type = "website",
  jsonLd,
}: MetaOptions) {
  useEffect(() => {
    const fullTitle = title.includes("Cabinet") ? title : `${title} — Cabinet`;
    document.title = fullTitle;

    const origin = window.location.origin;
    const path = canonicalPath ?? window.location.pathname;
    const canonical = `${origin}${path}`;

    if (description) {
      setMeta("name", "description", description);
      setMeta("property", "og:description", description);
      setMeta("name", "twitter:description", description);
    }

    setMeta("property", "og:title", fullTitle);
    setMeta("name", "twitter:title", fullTitle);
    setMeta("property", "og:type", type);
    setMeta("property", "og:url", canonical);
    setMeta("name", "twitter:card", image ? "summary_large_image" : "summary");

    if (image) {
      setMeta("property", "og:image", image);
      setMeta("name", "twitter:image", image);
    }

    let link = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]');
    if (!link) {
      link = document.createElement("link");
      link.rel = "canonical";
      document.head.appendChild(link);
    }
    link.href = canonical;

    const scriptId = "cabinet-page-jsonld";
    const existing = document.getElementById(scriptId);
    if (jsonLd) {
      const script = existing ?? document.createElement("script");
      script.id = scriptId;
      script.setAttribute("type", "application/ld+json");
      script.textContent = JSON.stringify(jsonLd);
      if (!existing) document.head.appendChild(script);
    } else if (existing) {
      existing.remove();
    }
  }, [title, description, image, canonicalPath, type, jsonLd]);
}
