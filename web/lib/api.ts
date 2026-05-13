/**
 * whendo backend API client.
 *
 * All calls go through Next.js rewrites (see next.config.js), so we
 * just use relative paths like "/api/recipes". This avoids CORS in dev
 * and works the same in production.
 */

export type WhenBlock = {
  every?: string;
  webhook?: string;
  on_startup?: boolean;
};

export type RecipeSummary = {
  name: string;
  description: string | null;
  enabled: boolean;
  when: WhenBlock;
  source: string | null;
  action: string;
  next_run: string | null; // ISO datetime
};

export type LoadError = {
  file: string;
  error: string;
};

export type Run = {
  id: number;
  recipe: string;
  started_at: string;
  finished_at: string | null;
  status: "success" | "failed" | "skipped" | "running";
  error: string | null;
  output: Record<string, unknown> | null;
};

type FetchOpts = { method?: string; body?: unknown; cache?: RequestCache };

async function call<T>(path: string, opts: FetchOpts = {}): Promise<T> {
  const res = await fetch(path, {
    method: opts.method ?? "GET",
    headers: opts.body ? { "Content-Type": "application/json" } : undefined,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
    cache: opts.cache ?? "no-store",
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(
      `${res.status} ${res.statusText}${text ? `: ${text}` : ""}`,
    );
  }
  // Treat 204 No Content gracefully.
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  health: () => call<{ status: string }>("/health"),
  listRecipes: () => call<RecipeSummary[]>("/api/recipes"),
  listErrors: () => call<LoadError[]>("/api/recipes/errors"),
  reloadRecipes: () =>
    call<{ loaded: number; errors: number; error_files: string[] }>(
      "/api/recipes/reload",
      { method: "POST" },
    ),
  runNow: (name: string) =>
    call<{ status: string; recipe: string }>(
      `/api/recipes/${encodeURIComponent(name)}/run`,
      { method: "POST" },
    ),
  listRuns: (params: { recipe?: string; limit?: number } = {}) => {
    const qs = new URLSearchParams();
    if (params.recipe) qs.set("recipe", params.recipe);
    if (params.limit) qs.set("limit", String(params.limit));
    const suffix = qs.toString() ? `?${qs}` : "";
    return call<Run[]>(`/api/runs${suffix}`);
  },
};
