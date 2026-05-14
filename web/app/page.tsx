"use client";

import Link from "next/link";
import { Cog, History } from "lucide-react";

import { useLocale } from "@/lib/locale-context";
import { TerminalHeader } from "@/components/TerminalHeader";
import { RecipesList } from "@/components/RecipesList";

export default function HomePage() {
  const { t } = useLocale();

  return (
    <main>
      <TerminalHeader />

      <nav className="border-b border-border bg-bg-elevated">
        <div className="mx-auto flex max-w-6xl items-center gap-1 px-6">
          <NavLink href="/" active>
            {t("nav.recipes")}
          </NavLink>
          <NavLink href="/runs">
            <History className="h-3 w-3" />
            {t("nav.runs")}
          </NavLink>
          <NavLink href="/settings">
            <Cog className="h-3 w-3" />
            {t("nav.settings")}
          </NavLink>
        </div>
      </nav>

      <RecipesList />

      <footer className="border-t border-border py-6 text-center">
        <p className="font-mono text-xs text-ink-muted">
          <span className="text-lime">$</span> {t("footer.version")} ·{" "}
          <a
            href="https://github.com/ricardomiguelcuadrosrodriguez/Whendo"
            target="_blank"
            rel="noreferrer"
            className="text-ink-dim hover:text-lime"
          >
            github
          </a>{" "}
          · MIT
        </p>
      </footer>
    </main>
  );
}

function NavLink({
  href,
  active,
  children,
}: {
  href: string;
  active?: boolean;
  children: React.ReactNode;
}) {
  return (
    <Link
      href={href}
      className={`flex items-center gap-1.5 border-b-2 px-3 py-3 font-mono text-xs transition-colors ${
        active
          ? "border-lime text-lime"
          : "border-transparent text-ink-dim hover:text-ink"
      }`}
    >
      {children}
    </Link>
  );
}
