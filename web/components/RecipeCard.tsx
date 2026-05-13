"use client";

import { useState, useTransition } from "react";
import {
  ArrowRight,
  Clock,
  Loader2,
  Play,
  Power,
  PowerOff,
  Webhook,
  Zap,
} from "lucide-react";

import { api, type RecipeSummary } from "@/lib/api";
import { useLocale } from "@/lib/locale-context";
import { cn, formatRelativeTime } from "@/lib/utils";

type Props = {
  recipe: RecipeSummary;
  onRunComplete?: () => void;
};

export function RecipeCard({ recipe, onRunComplete }: Props) {
  const { t } = useLocale();
  const [isPending, startTransition] = useTransition();
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleRun = () => {
    setFeedback(null);
    startTransition(async () => {
      try {
        await api.runNow(recipe.name);
        setFeedback("queued");
        onRunComplete?.();
        setTimeout(() => setFeedback(null), 2400);
      } catch (e) {
        setFeedback((e as Error).message);
      }
    });
  };

  const trigger = recipe.when.every
    ? { icon: Clock, label: recipe.when.every }
    : recipe.when.webhook
      ? { icon: Webhook, label: `/webhooks/${recipe.when.webhook}` }
      : { icon: Zap, label: "on_startup" };

  const TriggerIcon = trigger.icon;
  const StatusIcon = recipe.enabled ? Power : PowerOff;

  return (
    <article
      className={cn(
        "group relative animate-fade-in border border-border bg-bg-card p-5",
        "transition-colors hover:border-border-strong",
        !recipe.enabled && "opacity-60",
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="truncate font-mono text-base font-medium text-ink">
            {recipe.name}
          </h3>
          {recipe.description && (
            <p className="mt-1 text-sm text-ink-dim">{recipe.description}</p>
          )}
        </div>
        <StatusIcon
          className={cn(
            "h-4 w-4 shrink-0",
            recipe.enabled ? "text-success" : "text-ink-muted",
          )}
        />
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2 font-mono text-xs">
        <span className="flex items-center gap-1.5 rounded border border-border bg-bg px-2 py-1 text-ink-dim">
          <TriggerIcon className="h-3 w-3" />
          {trigger.label}
        </span>

        {recipe.source && (
          <>
            <ArrowRight className="h-3 w-3 text-ink-muted" />
            <span className="rounded border border-border bg-bg px-2 py-1 text-lime">
              {recipe.source}
            </span>
          </>
        )}

        <ArrowRight className="h-3 w-3 text-ink-muted" />
        <span className="rounded border border-border bg-bg px-2 py-1 text-flame">
          {recipe.action}
        </span>
      </div>

      <div className="mt-4 flex items-center justify-between border-t border-border pt-3 text-xs">
        <div className="text-ink-dim">
          <span className="text-ink-muted">{t("card.next")} </span>
          <span className="font-mono text-ink">
            {formatRelativeTime(recipe.next_run)}
          </span>
        </div>

        <button
          onClick={handleRun}
          disabled={isPending || !recipe.enabled}
          className={cn(
            "flex items-center gap-1.5 px-2 py-1 font-mono text-xs",
            "border border-border text-ink-dim transition-colors",
            "hover:border-lime hover:text-lime",
            "disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:border-border disabled:hover:text-ink-dim",
          )}
        >
          {isPending ? (
            <Loader2 className="h-3 w-3 animate-spin" />
          ) : (
            <Play className="h-3 w-3" />
          )}
          {feedback === "queued" ? t("card.queued") : t("card.run_now")}
        </button>
      </div>

      {feedback && feedback !== "queued" && (
        <p className="mt-2 font-mono text-xs text-danger">{feedback}</p>
      )}
    </article>
  );
}
