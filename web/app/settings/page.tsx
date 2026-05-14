"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowLeft,
  Bell,
  Check,
  Cog,
  Database,
  History,
  Lock,
  LockOpen,
  RefreshCw,
  Sparkles,
} from "lucide-react";

import {
  api,
  type SettingItem,
  type SettingsListResponse,
  type SettingsStatus,
} from "@/lib/api";
import { useLocale } from "@/lib/locale-context";
import { TerminalHeader } from "@/components/TerminalHeader";
import { cn } from "@/lib/utils";

type CategoryKey = "notifications" | "data_sources" | "ai";
const CATEGORY_ORDER: CategoryKey[] = ["notifications", "data_sources", "ai"];

const SERVICE_TITLES: Record<string, string> = {
  telegram: "Telegram",
  ntfy: "ntfy",
  smtp: "Email (SMTP)",
  discord: "Discord",
  twilio: "WhatsApp (Twilio)",
  openweather: "OpenWeatherMap",
  spotify: "Spotify",
  youtube: "YouTube",
  github: "GitHub",
  llm: "LLM provider",
};

export default function SettingsPage() {
  const { t } = useLocale();
  const [data, setData] = useState<SettingsListResponse | null>(null);
  const [loadState, setLoadState] =
    useState<"loading" | "ready" | "error">("loading");
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    try {
      const r = await api.listSettings();
      setData(r);
      setLoadState("ready");
      setError(null);
    } catch (e) {
      setError((e as Error).message);
      setLoadState("error");
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return (
    <main>
      <TerminalHeader />
      <NavBar />

      <section className="mx-auto max-w-6xl space-y-8 px-6 py-10">
        <header>
          <h2 className="font-mono text-xs uppercase tracking-wider text-ink-muted">
            {t("settings.title")}
          </h2>
          <p className="mt-3 max-w-2xl font-mono text-xs leading-relaxed text-ink-dim">
            {t("settings.subtitle")}
          </p>
        </header>

        {loadState === "loading" && (
          <div className="font-mono text-xs text-ink-dim">
            <RefreshCw className="mr-2 inline h-3.5 w-3.5 animate-spin" />
            {t("settings.loading")}
          </div>
        )}

        {loadState === "error" && (
          <div className="border border-danger/30 bg-danger/5 p-4">
            <p className="font-mono text-sm text-danger">
              <AlertTriangle className="mr-2 inline h-4 w-4" />
              {error}
            </p>
          </div>
        )}

        {data && (
          <>
            <SecurityPanel status={data.status} onChanged={refresh} />

            {CATEGORY_ORDER.map((category) => (
              <CategorySection
                key={category}
                category={category}
                items={data.items.filter((i) => i.category === category)}
                status={data.status}
                onSaved={refresh}
              />
            ))}
          </>
        )}
      </section>
    </main>
  );
}

function NavBar() {
  const { t } = useLocale();
  return (
    <nav className="border-b border-border bg-bg-elevated">
      <div className="mx-auto flex max-w-6xl items-center gap-1 px-6">
        <Link
          href="/"
          className="flex items-center gap-1.5 border-b-2 border-transparent px-3 py-3 font-mono text-xs text-ink-dim transition-colors hover:text-ink"
        >
          <ArrowLeft className="h-3 w-3" />
          {t("nav.recipes")}
        </Link>
        <Link
          href="/runs"
          className="flex items-center gap-1.5 border-b-2 border-transparent px-3 py-3 font-mono text-xs text-ink-dim transition-colors hover:text-ink"
        >
          <History className="h-3 w-3" />
          {t("nav.runs")}
        </Link>
        <span className="flex items-center gap-1.5 border-b-2 border-lime px-3 py-3 font-mono text-xs text-lime">
          <Cog className="h-3 w-3" />
          {t("nav.settings")}
        </span>
      </div>
    </nav>
  );
}

function categoryTitle(c: CategoryKey, t: ReturnType<typeof useLocale>["t"]) {
  if (c === "notifications") return t("settings.cat.notifications");
  if (c === "data_sources") return t("settings.cat.data_sources");
  return t("settings.cat.ai");
}

function categoryHint(c: CategoryKey, t: ReturnType<typeof useLocale>["t"]) {
  if (c === "notifications") return t("settings.cat.notifications_hint");
  if (c === "data_sources") return t("settings.cat.data_sources_hint");
  return t("settings.cat.ai_hint");
}

function CategoryIcon({ c }: { c: CategoryKey }) {
  if (c === "notifications") return <Bell className="h-4 w-4 text-ink-dim" />;
  if (c === "data_sources") return <Database className="h-4 w-4 text-ink-dim" />;
  return <Sparkles className="h-4 w-4 text-ink-dim" />;
}

function SecurityPanel({
  status,
  onChanged,
}: {
  status: SettingsStatus;
  onChanged: () => void;
}) {
  const { t } = useLocale();
  const [password, setPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [feedback, setFeedback] =
    useState<{ kind: "ok" | "err"; msg: string } | null>(null);

  const noMaster = !status.has_master_password;
  const isLocked = status.has_master_password && !status.is_unlocked;
  const unlocked = status.has_master_password && status.is_unlocked;

  const statusText = noMaster
    ? t("settings.security.status_no_master")
    : isLocked
      ? t("settings.security.status_locked")
      : t("settings.security.status_unlocked");

  async function run(fn: () => Promise<unknown>) {
    setBusy(true);
    setFeedback(null);
    try {
      await fn();
      onChanged();
    } catch (e) {
      setFeedback({ kind: "err", msg: (e as Error).message });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4 border border-border bg-bg-card p-5">
      <h3 className="flex items-center gap-2 font-mono text-sm text-ink">
        {isLocked && <Lock className="h-4 w-4 text-warning" />}
        {unlocked && <LockOpen className="h-4 w-4 text-success" />}
        {noMaster && <Cog className="h-4 w-4 text-ink-dim" />}
        {t("settings.security.title")}
      </h3>

      <p className="font-mono text-xs leading-relaxed text-ink-dim">
        {statusText}
      </p>

      {noMaster && (
        <p className="font-mono text-xs leading-relaxed text-ink-muted">
          {t("settings.security.master_help")}
        </p>
      )}

      <div className="flex flex-wrap items-end gap-2">
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder={t("settings.security.master_placeholder")}
          className="min-w-[200px] flex-1 border border-border bg-bg px-3 py-2 font-mono text-sm text-ink placeholder:text-ink-muted focus:border-lime focus:outline-none"
        />
        {unlocked && (
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            placeholder={t("settings.security.master_new_placeholder")}
            className="min-w-[200px] flex-1 border border-border bg-bg px-3 py-2 font-mono text-sm text-ink placeholder:text-ink-muted focus:border-lime focus:outline-none"
          />
        )}

        {noMaster && (
          <button
            onClick={() =>
              run(async () => {
                await api.setMasterPassword(password);
                setPassword("");
              })
            }
            disabled={!password || busy}
            className="border border-lime bg-lime/10 px-3 py-2 font-mono text-xs text-lime transition-colors hover:bg-lime/20 disabled:opacity-40"
          >
            {t("settings.security.set_master")}
          </button>
        )}

        {isLocked && (
          <button
            onClick={() =>
              run(async () => {
                await api.unlockSettings(password);
                setPassword("");
              })
            }
            disabled={!password || busy}
            className="border border-lime bg-lime/10 px-3 py-2 font-mono text-xs text-lime transition-colors hover:bg-lime/20 disabled:opacity-40"
          >
            {t("settings.security.unlock")}
          </button>
        )}

        {unlocked && (
          <>
            <button
              onClick={() =>
                run(async () => {
                  await api.changeMasterPassword(password, newPassword);
                  setPassword("");
                  setNewPassword("");
                })
              }
              disabled={!password || !newPassword || busy}
              className="border border-lime bg-lime/10 px-3 py-2 font-mono text-xs text-lime transition-colors hover:bg-lime/20 disabled:opacity-40"
            >
              {t("settings.security.change_master")}
            </button>
            <button
              onClick={() => run(() => api.lockSettings())}
              disabled={busy}
              className="border border-border bg-bg px-3 py-2 font-mono text-xs text-ink-dim transition-colors hover:text-ink disabled:opacity-40"
            >
              {t("settings.security.lock")}
            </button>
          </>
        )}
      </div>

      {feedback && (
        <p
          className={cn(
            "font-mono text-xs",
            feedback.kind === "err" ? "text-danger" : "text-success",
          )}
        >
          {feedback.msg}
        </p>
      )}
    </div>
  );
}

function CategorySection({
  category,
  items,
  status,
  onSaved,
}: {
  category: CategoryKey;
  items: SettingItem[];
  status: SettingsStatus;
  onSaved: () => void;
}) {
  const { t } = useLocale();

  const byService = new Map<string, SettingItem[]>();
  for (const item of items) {
    const service = item.key.split(".")[0];
    if (!byService.has(service)) byService.set(service, []);
    byService.get(service)!.push(item);
  }

  if (byService.size === 0) return null;

  return (
    <section className="space-y-3">
      <header className="flex items-baseline gap-3">
        <CategoryIcon c={category} />
        <h3 className="font-mono text-sm uppercase tracking-wider text-ink">
          {categoryTitle(category, t)}
        </h3>
        <span className="font-mono text-xs text-ink-muted">
          {categoryHint(category, t)}
        </span>
      </header>

      <div className="grid gap-3 md:grid-cols-2">
        {Array.from(byService.entries()).map(([service, serviceItems]) => (
          <ServiceCard
            key={service}
            service={service}
            items={serviceItems}
            status={status}
            onSaved={onSaved}
          />
        ))}
      </div>
    </section>
  );
}

function ServiceCard({
  service,
  items,
  status,
  onSaved,
}: {
  service: string;
  items: SettingItem[];
  status: SettingsStatus;
  onSaved: () => void;
}) {
  const { t } = useLocale();
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const [justSaved, setJustSaved] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const title = SERVICE_TITLES[service] ?? service;
  const isConfigured = items.some((i) => i.is_set);
  const hasSecret = items.some((i) => i.is_secret);
  const isLockedAndHasSecret =
    hasSecret && status.has_master_password && !status.is_unlocked;

  function valueOf(item: SettingItem): string {
    if (item.key in drafts) return drafts[item.key];
    return item.value ?? "";
  }

  function setDraft(key: string, v: string) {
    setDrafts((prev) => ({ ...prev, [key]: v }));
    setJustSaved(false);
    setErr(null);
  }

  async function handleSave() {
    setBusy(true);
    setErr(null);
    try {
      for (const item of items) {
        const v = drafts[item.key];
        if (v === undefined) continue;
        if (item.is_secret && v === "") continue;
        if (v === "" && !item.is_set) continue;
        if (v === "") {
          await api.deleteSetting(item.key);
        } else {
          await api.saveSetting(item.key, v);
        }
      }
      setDrafts({});
      setJustSaved(true);
      onSaved();
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const hasChanges = Object.keys(drafts).length > 0;

  return (
    <div className="space-y-3 border border-border bg-bg-card p-4">
      <header className="flex items-center justify-between">
        <h4 className="font-mono text-sm text-ink">{title}</h4>
        <span
          className={cn(
            "font-mono text-[10px] uppercase tracking-wider",
            isConfigured ? "text-success" : "text-ink-muted",
          )}
        >
          {isConfigured
            ? t("settings.configured")
            : t("settings.not_configured")}
        </span>
      </header>

      {isLockedAndHasSecret && (
        <p className="border border-warning/30 bg-warning/5 px-3 py-2 font-mono text-xs text-warning">
          {t("settings.security.locked_warning")}
        </p>
      )}

      <div className="space-y-3">
        {items.map((item) => (
          <Field
            key={item.key}
            item={item}
            value={valueOf(item)}
            onChange={(v) => setDraft(item.key, v)}
            disabled={item.is_secret && isLockedAndHasSecret}
          />
        ))}
      </div>

      <div className="flex items-center justify-end gap-2 pt-1">
        {err && <p className="flex-1 font-mono text-xs text-danger">{err}</p>}
        {justSaved && !busy && !err && (
          <p className="flex items-center gap-1 font-mono text-xs text-success">
            <Check className="h-3 w-3" />
            {t("settings.saved")}
          </p>
        )}
        <button
          onClick={handleSave}
          disabled={busy || !hasChanges}
          className="border border-lime bg-lime/10 px-3 py-1.5 font-mono text-xs text-lime transition-colors hover:bg-lime/20 disabled:opacity-40"
        >
          {busy ? t("settings.saving") : t("settings.save")}
        </button>
      </div>
    </div>
  );
}

function Field({
  item,
  value,
  onChange,
  disabled,
}: {
  item: SettingItem;
  value: string;
  onChange: (v: string) => void;
  disabled?: boolean;
}) {
  const { t } = useLocale();
  const inputType = item.is_secret ? "password" : "text";
  const placeholder =
    item.is_set && item.is_secret
      ? t("settings.empty_keep_existing")
      : item.placeholder ?? item.default ?? "";

  return (
    <div>
      <label className="mb-1 block font-mono text-xs text-ink-dim">
        {item.label}
        {item.is_secret && <span className="ml-1 text-flame">•</span>}
      </label>
      <input
        type={inputType}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        className="w-full border border-border bg-bg px-3 py-1.5 font-mono text-sm text-ink placeholder:text-ink-muted focus:border-lime focus:outline-none disabled:opacity-50"
      />
      {item.description && (
        <p className="mt-1 font-mono text-[11px] leading-relaxed text-ink-muted">
          {item.description}
        </p>
      )}
    </div>
  );
}
