"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  ChevronRight,
  CircleDashed,
  Cog,
  History,
  RefreshCw,
  XCircle,
} from "lucide-react";

import { api, type Run } from "@/lib/api";
import { useLocale } from "@/lib/locale-context";
import { TerminalHeader } from "@/components/TerminalHeader";
import { cn, formatRelativePast } from "@/lib/utils";

export default function RunsPage() {
  const { t } = useLocale();
  const [runs, setRuns] = useState<Run[]>([]);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">(
    "loading",
  );
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<number | null>(null);

  const fetchRuns = useCallback(async () => {
    try {
      const r = await api.listRuns({ limit: 100 });
      setRuns(r);
      setLoadState("ready");
      setError(null);
    } catch (e) {
      setError((e as Error).message);
      setLoadState("error");
    }
  }, []);

  useEffect(() => {
    fetchRuns();
  }, [fetchRuns]);

  return (
    <main>
      <TerminalHeader />

      <nav className="border-b border-border bg-bg-elevated">
        <div className="mx-auto flex max-w-6xl items-center gap-1 px-6">
          <Link
            href="/"
            className="flex items-center gap-1.5 border-b-2 border-transparent px-3 py-3 font-mono text-xs text-ink-dim transition-colors hover:text-ink"
          >
            <ArrowLeft className="h-3 w-3" />
            {t("nav.recipes")}
          </Link>
          <span className="flex items-center gap-1.5 border-b-2 border-lime px-3 py-3 font-mono text-xs text-lime">
            <History className="h-3 w-3" />
            {t("nav.runs")}
          </span>
          <Link
            href="/settings"
            className="flex items-center gap-1.5 border-b-2 border-transparent px-3 py-3 font-mono text-xs text-ink-dim transition-colors hover:text-ink"
          >
            <Cog className="h-3 w-3" />
            {t("nav.settings")}
          </Link>
        </div>
      </nav>

      <section className="mx-auto max-w-6xl px-6 py-10">
        <div className="flex items-end justify-between gap-3">
          <div>
            <h2 className="font-mono text-xs uppercase tracking-wider text-ink-muted">
              {t("runs.title")}
            </h2>
            <p className="mt-1 font-mono text-2xl text-ink">
              <span className="text-lime">{runs.length}</span>{" "}
              <span className="text-ink-dim">{t("runs.executions")}</span>
            </p>
          </div>
          <button
            onClick={fetchRuns}
            className="flex items-center gap-2 border border-border bg-bg-card px-3 py-2 font-mono text-xs text-ink transition-colors hover:border-lime hover:text-lime"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            {t("runs.refresh")}
          </button>
        </div>

        {loadState === "error" && (
          <div className="mt-6 border border-danger/30 bg-danger/5 p-4">
            <p className="font-mono text-sm text-danger">
              <AlertTriangle className="inline h-4 w-4 mr-2" />
              {t("runs.could_not_load")}: {error}
            </p>
          </div>
        )}

        {loadState === "ready" && runs.length === 0 && (
          <div className="mt-10 border border-border bg-bg-card p-10 text-center">
            <p className="font-mono text-sm text-ink-dim">{t("runs.empty.title")}</p>
            <p className="mt-3 font-mono text-xs text-ink-muted">
              {t("runs.empty.hint")}
            </p>
          </div>
        )}

        {runs.length > 0 && (
          <div className="mt-6 border border-border bg-bg-card">
            {runs.map((run, i) => (
              <RunRow
                key={run.id}
                run={run}
                expanded={expanded === run.id}
                onToggle={() => setExpanded(expanded === run.id ? null : run.id)}
                isLast={i === runs.length - 1}
              />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

function RunRow({
  run,
  expanded,
  onToggle,
  isLast,
}: {
  run: Run;
  expanded: boolean;
  onToggle: () => void;
  isLast: boolean;
}) {
  const { t } = useLocale();

  const StatusIcon =
    run.status === "success"
      ? CheckCircle2
      : run.status === "failed"
        ? XCircle
        : run.status === "running"
          ? CircleDashed
          : CircleDashed;

  const statusColor =
    run.status === "success"
      ? "text-success"
      : run.status === "failed"
        ? "text-danger"
        : run.status === "running"
          ? "text-lime"
          : "text-ink-dim";

  return (
    <>
      <button
        onClick={onToggle}
        className={cn(
          "flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-bg-elevated",
          !isLast && "border-b border-border",
        )}
      >
        <StatusIcon className={cn("h-4 w-4 shrink-0", statusColor)} />
        <div className="min-w-0 flex-1">
          <div className="flex items-baseline justify-between gap-3">
            <span className="truncate font-mono text-sm text-ink">
              {run.recipe}
            </span>
            <span className="shrink-0 font-mono text-xs text-ink-muted">
              {formatRelativePast(run.started_at)}
            </span>
          </div>
        </div>
        <ChevronRight
          className={cn(
            "h-4 w-4 shrink-0 text-ink-muted transition-transform",
            expanded && "rotate-90",
          )}
        />
      </button>

      {expanded && (
        <div
          className={cn(
            "animate-fade-in space-y-3 bg-bg px-4 py-4 font-mono text-xs",
            !isLast && "border-b border-border",
          )}
        >
          <KV k={t("runs.status")} v={<span className={statusColor}>{run.status}</span>} />
          <KV k={t("runs.started_at")} v={run.started_at} />
          <KV k={t("runs.finished_at")} v={run.finished_at ?? "—"} />
          {run.error && (
            <KV
              k={t("runs.error")}
              v={<span className="text-danger">{run.error}</span>}
            />
          )}
          {run.output && (
            <details className="text-ink-dim">
              <summary className="cursor-pointer hover:text-ink">
                {t("runs.output")}
              </summary>
              <pre className="mt-2 overflow-x-auto rounded bg-bg-elevated p-3 text-[11px] text-ink-dim">
                {JSON.stringify(run.output, null, 2)}
              </pre>
            </details>
          )}
        </div>
      )}
    </>
  );
}

function KV({ k, v }: { k: string; v: React.ReactNode }) {
  return (
    <div className="flex gap-3">
      <span className="w-24 shrink-0 text-ink-muted">{k}:</span>
      <span className="text-ink">{v}</span>
    </div>
  );
}
