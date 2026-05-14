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
  next_run: string | null;
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

export type SettingItem = {
  key: string;
  label: string;
  category: "notifications" | "data_sources" | "ai";
  is_secret: boolean;
  default: string | null;
  description: string | null;
  placeholder: string | null;
  is_set: boolean;
  value: string | null;
};

export type SettingsStatus = {
  has_master_password: boolean;
  is_unlocked: boolean;
  secret_count: number;
  encrypted_count: number;
};

export type SettingsListResponse = {
  items: SettingItem[];
  status: SettingsStatus;
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
    // Try to extract the structured `detail` field from FastAPI errors.
    let detail = "";
    try {
      const data = await res.json();
      detail = typeof data?.detail === "string" ? data.detail : JSON.stringify(data);
    } catch {
      detail = await res.text().catch(() => "");
    }
    throw new Error(`${res.status}: ${detail || res.statusText}`);
  }

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

  createRecipe: (yamlText: string) =>
    call<{ status: string; name: string; file: string }>("/api/recipes", {
      method: "POST",
      body: { yaml: yamlText },
    }),

  deleteRecipe: (name: string) =>
    call<{ status: string; name: string; file: string }>(
      `/api/recipes/${encodeURIComponent(name)}`,
      { method: "DELETE" },
    ),

  listRuns: (params: { recipe?: string; limit?: number } = {}) => {
    const qs = new URLSearchParams();
    if (params.recipe) qs.set("recipe", params.recipe);
    if (params.limit) qs.set("limit", String(params.limit));
    const suffix = qs.toString() ? `?${qs}` : "";
    return call<Run[]>(`/api/runs${suffix}`);
  },

  listSettings: () => call<SettingsListResponse>("/api/settings"),

  settingsStatus: () => call<SettingsStatus>("/api/settings/_status"),

  saveSetting: (key: string, value: string) =>
    call<{ status: string; key: string }>(
      `/api/settings/${encodeURIComponent(key)}`,
      { method: "PUT", body: { value } },
    ),

  deleteSetting: (key: string) =>
    call<{ status: string; key: string }>(
      `/api/settings/${encodeURIComponent(key)}`,
      { method: "DELETE" },
    ),

  setMasterPassword: (password: string) =>
    call<{ status: string }>("/api/settings/_set-master", {
      method: "POST",
      body: { password },
    }),

  unlockSettings: (password: string) =>
    call<{ status: string }>("/api/settings/_unlock", {
      method: "POST",
      body: { password },
    }),

  lockSettings: () =>
    call<{ status: string }>("/api/settings/_lock", { method: "POST" }),

  changeMasterPassword: (old_password: string, new_password: string) =>
    call<{ status: string }>("/api/settings/_change-master", {
      method: "POST",
      body: { old_password, new_password },
    }),
};
