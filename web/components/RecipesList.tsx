"use client";

import { useCallback, useEffect, useState, useTransition } from "react";
import { RefreshCw, AlertTriangle, FileWarning } from "lucide-react";

import { api, type LoadError, type RecipeSummary } from "@/lib/api";
import { cn } from "@/lib/utils";
import { RecipeCard } from "./RecipeCard";

export function RecipesList() {
  const [recipes, setRecipes] = useState<RecipeSummary[]>([]);
  const [errors, setErrors] = useState<LoadError[]>([]);
  const [loadState, setLoadState] = useState<"loading" | "ready" | "error">(
    "loading",
  );
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

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
      <div className="flex items-end justify-between gap-3">
        <div>
          <h2 className="font-mono text-xs uppercase tracking-wider text-ink-muted">
            // recipes
          </h2>
          <p className="mt-1 font-mono text-2xl text-ink">
            {loadState === "loading" ? (
              <LoadingDots />
            ) : (
              <>
                <span className="text-lime">{recipes.length}</span>{" "}
                <span className="text-ink-dim">
                  loaded
                  {errors.length > 0 && (
                    <>
                      , <span className="text-danger">{errors.length}</span> with
                      errors
                    </>
                  )}
                </span>
              </>
            )}
          </p>
        </div>

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
          reload
        </button>
      </div>

      {/* Errors block */}
      {errors.length > 0 && (
        <div className="mt-6 border border-danger/30 bg-danger/5 p-4">
          <div className="flex items-center gap-2 font-mono text-xs text-danger">
            <AlertTriangle className="h-4 w-4" />
            {errors.length} recipe{errors.length === 1 ? "" : "s"} failed to load
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

      {/* Loaded state */}
      {loadState === "error" && (
        <div className="mt-6 border border-danger/30 bg-danger/5 p-4">
          <p className="font-mono text-sm text-danger">
            <AlertTriangle className="inline h-4 w-4 mr-2" />
            Could not reach backend
          </p>
          <p className="mt-2 font-mono text-xs text-ink-dim">{loadError}</p>
          <p className="mt-3 font-mono text-xs text-ink-dim">
            Is the server running on{" "}
            <span className="text-lime">localhost:8000</span>? Try{" "}
            <span className="text-lime">make dev</span> in another terminal.
          </p>
        </div>
      )}

      {loadState === "ready" && recipes.length === 0 && errors.length === 0 && (
        <EmptyState />
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
    </section>
  );
}

function LoadingDots() {
  return (
    <span className="running-dots text-ink-dim">
      loading<span>.</span>
      <span>.</span>
      <span>.</span>
    </span>
  );
}

function EmptyState() {
  return (
    <div className="mt-10 border border-border bg-bg-card p-10 text-center">
      <p className="font-mono text-sm text-ink-dim">
        No recipes loaded yet.
      </p>
      <p className="mt-4 font-mono text-xs text-ink-muted">
        Drop a <span className="text-lime">.yaml</span> file in your{" "}
        <span className="text-lime">recipes/</span> folder, then click{" "}
        <span className="text-flame">reload</span>.
      </p>
      <p className="mt-6 font-mono text-xs text-ink-muted">
        Or copy one from <span className="text-lime">examples/</span> to get
        started.
      </p>
    </div>
  );
}
