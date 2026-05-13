"use client";

import { useCallback, useEffect, useState, useTransition } from "react";
import { RefreshCw, AlertTriangle, FileWarning, Plus } from "lucide-react";

import { api, type LoadError, type RecipeSummary } from "@/lib/api";
import { useLocale } from "@/lib/locale-context";
import { cn } from "@/lib/utils";
import { RecipeCard } from "./RecipeCard";
import { NewRecipeDialog } from "./NewRecipeDialog";

export function RecipesList() {
  const { t } = useLocale();
  const [recipes, setRecipes] = useState<RecipeSummary[]>([]);
  const [errors, setErrors] = useState<LoadError[]>([]);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">(
    "loading",
  );
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();
  const [dialogOpen, setDialogOpen] = useState(false);

  const fetchAll = useCallback(async () => {
    try {
      const [r, e] = await Promise.all([api.listRecipes(), api.listErrors()]);
      setRecipes(r);
      setErrors(e);
      setLoadState("ready");
      setLoadError(null);
    } catch (err) {
      setLoadError((err as Error).message);
      setLoadState("error");
    }
  }, []);

  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  const handleReload = () => {
    startTransition(async () => {
      try {
        await api.reloadRecipes();
        await fetchAll();
      } catch (err) {
        setLoadError((err as Error).message);
      }
    });
  };

  return (
    <section className="mx-auto max-w-6xl px-6 py-10">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="font-mono text-xs uppercase tracking-wider text-ink-muted">
            {t("recipes.title")}
          </h2>
          <p className="mt-1 font-mono text-2xl text-ink">
            {loadState === "loading" ? (
              <LoadingDots />
            ) : (
              <>
                <span className="text-lime">{recipes.length}</span>{" "}
                <span className="text-ink-dim">
                  {t("recipes.loaded")}
                  {errors.length > 0 && (
                    <>
                      , <span className="text-danger">{errors.length}</span>{" "}
                      {t("recipes.with_errors")}
                    </>
                  )}
                </span>
              </>
            )}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setDialogOpen(true)}
            className={cn(
              "flex items-center gap-2 border border-lime bg-lime/10 px-3 py-2",
              "font-mono text-xs text-lime transition-colors",
              "hover:bg-lime/20",
            )}
          >
            <Plus className="h-3.5 w-3.5" />
            {t("recipes.new")}
          </button>

          <button
            onClick={handleReload}
            disabled={isPending}
            className={cn(
              "flex items-center gap-2 border border-border bg-bg-card px-3 py-2",
              "font-mono text-xs text-ink transition-colors",
              "hover:border-lime hover:text-lime",
              "disabled:cursor-not-allowed disabled:opacity-50",
            )}
          >
            <RefreshCw className={cn("h-3.5 w-3.5", isPending && "animate-spin")} />
            {t("recipes.reload")}
          </button>
        </div>
      </div>

      {/* Errors block */}
      {errors.length > 0 && (
        <div className="mt-6 border border-danger/30 bg-danger/5 p-4">
          <div className="flex items-center gap-2 font-mono text-xs text-danger">
            <AlertTriangle className="h-4 w-4" />
            {errors.length} {t("recipes.failed_to_load")}
          </div>
          <ul className="mt-3 space-y-2">
            {errors.map((e, i) => (
              <li key={i} className="font-mono text-xs">
                <span className="text-ink-dim">
                  <FileWarning className="inline h-3 w-3 mr-1.5" />
                  {e.file}
                </span>
                <span className="text-danger"> → {e.error}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Backend down state */}
      {loadState === "error" && (
        <div className="mt-6 border border-danger/30 bg-danger/5 p-4">
          <p className="font-mono text-sm text-danger">
            <AlertTriangle className="inline h-4 w-4 mr-2" />
            {t("recipes.backend_down.title")}
          </p>
          <p className="mt-2 font-mono text-xs text-ink-dim">{loadError}</p>
          <p className="mt-3 font-mono text-xs text-ink-dim">
            {t("recipes.backend_down.hint")}
          </p>
        </div>
      )}

      {/* Empty state */}
      {loadState === "ready" && recipes.length === 0 && errors.length === 0 && (
        <div className="mt-10 border border-border bg-bg-card p-10 text-center">
          <p className="font-mono text-sm text-ink-dim">
            {t("recipes.empty.title")}
          </p>
          <p className="mt-4 font-mono text-xs text-ink-muted">
            {t("recipes.empty.hint1")}
          </p>
          <p className="mt-2 font-mono text-xs text-ink-muted">
            {t("recipes.empty.hint2")}
          </p>
        </div>
      )}

      {/* Recipes grid */}
      {recipes.length > 0 && (
        <div className="mt-6 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {recipes.map((recipe) => (
            <RecipeCard
              key={recipe.name}
              recipe={recipe}
              onRunComplete={fetchAll}
            />
          ))}
        </div>
      )}

      {/* Create-recipe dialog */}
      <NewRecipeDialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        onCreated={fetchAll}
      />
    </section>
  );
}

function LoadingDots() {
  const { t } = useLocale();
  return (
    <span className="running-dots text-ink-dim">
      {t("recipes.loading")}<span>.</span>
      <span>.</span>
      <span>.</span>
    </span>
  );
}
