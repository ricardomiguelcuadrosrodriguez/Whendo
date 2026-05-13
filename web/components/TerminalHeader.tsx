"use client";

import { Github } from "lucide-react";

import { useLocale } from "@/lib/locale-context";
import { Logo } from "./Logo";
import { LocaleSwitcher } from "./LocaleSwitcher";

export function TerminalHeader() {
  const { t } = useLocale();

  return (
    <header className="scanlines border-b border-border bg-bg-elevated">
      <div className="mx-auto max-w-6xl px-6 py-5">
        {/* Top strip */}
        <div className="flex items-center justify-between gap-4 font-mono text-sm">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              <span className="h-2.5 w-2.5 rounded-full bg-flame opacity-80" />
              <span className="h-2.5 w-2.5 rounded-full bg-warning opacity-60" />
              <span className="h-2.5 w-2.5 rounded-full bg-success opacity-60" />
            </div>
            <span className="text-ink-dim">~/whendo</span>
          </div>

          <div className="flex items-center gap-4">
            <LocaleSwitcher />
            <a
              href="https://github.com/ricardomiguelcuadrosrodriguez/Whendo"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2 text-ink-dim transition-colors hover:text-ink"
            >
              <Github className="h-4 w-4" />
              <span className="hidden sm:inline">github</span>
            </a>
          </div>
        </div>

        {/* Brand */}
        <div className="mt-7 flex items-center gap-4">
          <Logo size={56} className="text-ink shrink-0" />
          <div className="flex flex-col">
            <h1 className="font-mono text-4xl font-medium leading-none tracking-tight text-ink">
              whendo
              <span className="text-flame">.</span>
            </h1>
            <p className="mt-2 font-mono text-xs text-ink-dim">
              <span className="text-lime">$</span> {t("header.tagline")}
              <span className="cursor" />
            </p>
          </div>
        </div>

        {/* Subline */}
        <p className="mt-6 max-w-2xl font-mono text-xs leading-relaxed text-ink-dim">
          <span className="text-flame"># </span>
          {t("header.subline1")}
          <br />
          <span className="text-flame"># </span>
          {t("header.subline2")}
        </p>
      </div>
    </header>
  );
}
