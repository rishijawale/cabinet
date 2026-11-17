import { ArrowUpRight } from "lucide-react";
import { Link } from "react-router-dom";

const ARCHIVE_LINKS = [
  { label: "Explore", href: "/explore" },
  { label: "ASCII", href: "/explore/ascii" },
  { label: "Wallpapers", href: "/explore/wallpapers" },
  { label: "Pixel Art", href: "/explore/pixel-art" },
  { label: "Collections", href: "/collections" },
];

const PROJECT_LINKS = [
  { label: "About", href: "/about" },
  { label: "Guidelines", href: "/guidelines" },
  { label: "Licensing", href: "/licenses" },
  { label: "Studio", href: "/studio" },
  { label: "Submit", href: "/submit" },
];

const LEGAL_LINKS = [
  { label: "Privacy", href: "/privacy" },
  { label: "Terms", href: "/terms" },
];

export function Footer() {
  return (
    <footer className="mt-24 border-t border-line">
      <div className="container-page py-14 lg:py-20">
        <div className="grid gap-12 lg:grid-cols-12">
          <div className="lg:col-span-5">
            <Link to="/" className="inline-flex items-baseline gap-2">
              <span className="text-[15px] font-semibold uppercase tracking-[0.3em]">Cabinet</span>
              <span aria-hidden="true" className="h-1.5 w-1.5 -translate-y-0.5 bg-accent" />
            </Link>
            <p className="display mt-6 max-w-sm text-3xl leading-tight text-ink">
              A place for things worth keeping.
            </p>
            <p className="mt-4 max-w-sm text-sm leading-6 text-muted">
              A free, community-supported archive of digital artwork, visual experiments and
              internet culture.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-8 sm:grid-cols-3 lg:col-span-7">
            <FooterColumn title="Archive" links={ARCHIVE_LINKS} />
            <FooterColumn title="Project" links={PROJECT_LINKS} />
            <FooterColumn title="Legal" links={LEGAL_LINKS} />
          </div>
        </div>

        <div className="mt-16 flex flex-col gap-4 border-t border-line pt-6 text-[11px] text-muted sm:flex-row sm:items-center sm:justify-between">
          <p>© {new Date().getFullYear()} Cabinet. Artwork remains the property of its creators.</p>
          <div className="flex items-center gap-5">
            <a
              href="https://github.com/"
              target="_blank"
              rel="noreferrer noopener"
              className="inline-flex items-center gap-1 transition-colors hover:text-ink"
            >
              Open source <ArrowUpRight className="h-3 w-3" />
            </a>
            <Link to="/about" className="transition-colors hover:text-ink">
              Colophon
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}

function FooterColumn({
  title,
  links,
}: {
  title: string;
  links: { label: string; href: string }[];
}) {
  return (
    <div>
      <p className="label-tight mb-4">{title}</p>
      <ul className="space-y-2.5">
        {links.map((link) => (
          <li key={link.href}>
            <Link
              to={link.href}
              className="text-sm text-muted transition-colors hover:text-ink"
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
