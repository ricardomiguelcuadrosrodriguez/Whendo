"use client";

import { useState, useRef, useEffect } from "react";
import { Languages, Check } from "lucide-react";

import { LOCALES } from "@/lib/i18n";
import { useLocale } from "@/lib/locale-context";
import { cn } from "@/lib/utils";

export function LocaleSwitcher() {
  const { locale, setLocale } = useLocale();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const current = LOCALES.find((l) => l.code === locale) ?? LOCALES[0];

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 font-mono text-xs text-ink-dim transition-colors hover:text-ink"
        aria-label="Change language"
      >
        <Languages className="h-3.5 w-3.5" />
        <span>{current.code.toUpperCase()}</span>
      </button>

      {open && (
        <div
          className={cn(
            "absolute right-0 top-full z-50 mt-2 min-w-[140px]",
            "animate-fade-in border border-border bg-bg-elevated py-1",
          )}
        >
          {LOCALES.map((l) => (
            <button
              key={l.code}
              onClick={() => {
                setLocale(l.code);
                setOpen(false);
              }}
              className={cn(
                "flex w-full items-center justify-between gap-3 px-3 py-2 text-left font-mono text-xs",
                "transition-colors hover:bg-bg-card",
                locale === l.code ? "text-lime" : "text-ink-dim hover:text-ink",
              )}
            >
              <span className="flex items-center gap-2">
                <span>{l.flag}</span>
                <span>{l.label}</span>
              </span>
              {locale === l.code && <Check className="h-3 w-3" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
