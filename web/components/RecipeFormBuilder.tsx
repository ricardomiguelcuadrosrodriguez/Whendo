"use client";

import {
  Calendar,
  CloudRain,
  Github,
  Globe,
  Mail,
  MessageCircle,
  MessageSquare,
  Music,
  Power,
  Radio,
  Rss,
  Send,
  Sparkles,
  Terminal,
  Webhook,
} from "lucide-react";

import { useLocale } from "@/lib/locale-context";
import {
  type RecipeFormState,
  type ActionKind,
  type SourceKind,
} from "@/lib/recipe-form";
import { cn } from "@/lib/utils";

type Props = {
  form: RecipeFormState;
  onChange: (form: RecipeFormState) => void;
};

// Source options with friendly labels and icons
const SOURCE_OPTIONS: {
  kind: SourceKind;
  labelKey: "source.weather" | "source.rss" | "source.github_releases" | "source.spotify_new_release" | "source.web_scrape" | "source.http_get";
  icon: React.ComponentType<{ className?: string }>;
  placeholder: string;
}[] = [
  {
    kind: "weather",
    labelKey: "source.weather",
    icon: CloudRain,
    placeholder: 'location: "Lima, PE"\ncondition: "rain_today"',
  },
  {
    kind: "rss",
    labelKey: "source.rss",
    icon: Rss,
    placeholder: 'url: "https://example.com/feed.xml"\nsince: "last_run"',
  },
  {
    kind: "github_releases",
    labelKey: "source.github_releases",
    icon: Github,
    placeholder: 'repo: "anthropics/anthropic-sdk-python"',
  },
  {
    kind: "spotify_new_release",
    labelKey: "source.spotify_new_release",
    icon: Music,
    placeholder: 'artist: "Morat"\ntypes: ["album", "single"]',
  },
  {
    kind: "web_scrape",
    labelKey: "source.web_scrape",
    icon: Globe,
    placeholder: 'url: "https://example.com/product"\nselector: ".price"\nbelow: 100',
  },
  {
    kind: "http_get",
    labelKey: "source.http_get",
    icon: Radio,
    placeholder: 'url: "https://api.example.com/status"\nexpect_json_path: "$.online"\nequals: true',
  },
];

// Action options with friendly labels and icons
const ACTION_OPTIONS: {
  kind: ActionKind;
  labelKey:
    | "action.notify_ntfy"
    | "action.notify_telegram"
    | "action.notify_email"
    | "action.notify_discord"
    | "action.notify_whatsapp"
    | "action.webhook_post"
    | "action.llm_summarize_and_notify"
    | "action.run_shell";
  icon: React.ComponentType<{ className?: string }>;
  placeholder: string;
}[] = [
  {
    kind: "notify_ntfy",
    labelKey: "action.notify_ntfy",
    icon: Send,
    placeholder: 'topic: "my-topic"\nmessage: "Hello from whendo!"',
  },
  {
    kind: "notify_telegram",
    labelKey: "action.notify_telegram",
    icon: MessageCircle,
    placeholder: 'message: "Hello from whendo!"',
  },
  {
    kind: "notify_email",
    labelKey: "action.notify_email",
    icon: Mail,
    placeholder: 'to: "you@example.com"\nsubject: "Hello"\nbody: "Body of the email"',
  },
  {
    kind: "notify_discord",
    labelKey: "action.notify_discord",
    icon: MessageSquare,
    placeholder: 'message: "Hello from whendo!"',
  },
  {
    kind: "notify_whatsapp",
    labelKey: "action.notify_whatsapp",
    icon: MessageCircle,
    placeholder: 'to: "+51999999999"\nmessage: "Hello!"',
  },
  {
    kind: "webhook_post",
    labelKey: "action.webhook_post",
    icon: Webhook,
    placeholder: 'url: "https://example.com/hook"\nbody:\n  text: "Hello"',
  },
  {
    kind: "llm_summarize_and_notify",
    labelKey: "action.llm_summarize_and_notify",
    icon: Sparkles,
    placeholder: 'channel: "email"\nto: "you@example.com"\nprompt: "Summarize in 3 lines"',
  },
  {
    kind: "run_shell",
    labelKey: "action.run_shell",
    icon: Terminal,
    placeholder: 'command: "echo hello >> /tmp/whendo.log"',
  },
];

export function RecipeFormBuilder({ form, onChange }: Props) {
  const { t } = useLocale();
  const patch = (p: Partial<RecipeFormState>) => onChange({ ...form, ...p });

  return (
    <div className="space-y-7 p-5">
      {/* Basics */}
      <div className="space-y-3">
        <Field label={t("form.name")}>
          <input
            type="text"
            value={form.name}
            onChange={(e) => patch({ name: e.target.value })}
            placeholder={t("form.name_placeholder")}
            className={inputClass}
            autoFocus
          />
        </Field>

        <Field label={t("form.description")}>
          <input
            type="text"
            value={form.description}
            onChange={(e) => patch({ description: e.target.value })}
            placeholder={t("form.description_placeholder")}
            className={inputClass}
          />
        </Field>

        <label className="flex items-center gap-2 font-sans text-sm text-ink-dim">
          <input
            type="checkbox"
            checked={form.enabled}
            onChange={(e) => patch({ enabled: e.target.checked })}
            className="h-4 w-4 cursor-pointer accent-lime"
          />
          <Power className="h-3.5 w-3.5 text-success" />
          {t("form.enabled")}
        </label>
      </div>

      {/* WHEN */}
      <Section
        title={t("form.section_when")}
        help={t("form.section_when_help")}
      >
        <div className="flex flex-wrap gap-2">
          <RadioPill
            checked={form.whenKind === "every"}
            onClick={() => patch({ whenKind: "every" })}
            icon={Calendar}
            label={t("form.when_every")}
          />
          <RadioPill
            checked={form.whenKind === "webhook"}
            onClick={() => patch({ whenKind: "webhook" })}
            icon={Webhook}
            label={t("form.when_webhook")}
          />
          <RadioPill
            checked={form.whenKind === "on_startup"}
            onClick={() => patch({ whenKind: "on_startup" })}
            icon={Power}
            label={t("form.when_on_startup")}
          />
        </div>

        {form.whenKind === "every" && (
          <>
            <input
              type="text"
              value={form.whenEvery}
              onChange={(e) => patch({ whenEvery: e.target.value })}
              placeholder={t("form.when_every_placeholder")}
              className={cn(inputClass, "font-mono")}
            />
            <Hint>{t("form.when_every_hint")}</Hint>
          </>
        )}

        {form.whenKind === "webhook" && (
          <input
            type="text"
            value={form.whenWebhook}
            onChange={(e) => patch({ whenWebhook: e.target.value })}
            placeholder={t("form.when_webhook_placeholder")}
            className={cn(inputClass, "font-mono")}
          />
        )}

        {form.whenKind === "on_startup" && (
          <Hint>{t("form.when_on_startup_hint")}</Hint>
        )}
      </Section>

      {/* IF (optional) */}
      <Section title={t("form.section_if")} help={t("form.section_if_help")}>
        <select
          value={form.sourceKind}
          onChange={(e) =>
            patch({ sourceKind: e.target.value as SourceKind })
          }
          className={cn(inputClass, "cursor-pointer")}
        >
          <option value="none" className="bg-bg-card">
            {t("form.source_none")}
          </option>
          {SOURCE_OPTIONS.map((s) => (
            <option key={s.kind} value={s.kind} className="bg-bg-card">
              {t(s.labelKey)}
            </option>
          ))}
        </select>

        {form.sourceKind !== "none" && (
          <>
            <Field label={t("form.source_config")} small>
              <textarea
                value={form.sourceConfig}
                onChange={(e) => patch({ sourceConfig: e.target.value })}
                placeholder={
                  SOURCE_OPTIONS.find((s) => s.kind === form.sourceKind)
                    ?.placeholder ?? ""
                }
                rows={4}
                className={cn(inputClass, "resize-none font-mono")}
                spellCheck={false}
              />
            </Field>
            <Hint>{t("form.source_config_hint")}</Hint>
          </>
        )}
      </Section>

      {/* THEN */}
      <Section
        title={t("form.section_then")}
        help={t("form.section_then_help")}
      >
        <select
          value={form.actionKind}
          onChange={(e) =>
            patch({ actionKind: e.target.value as ActionKind })
          }
          className={cn(inputClass, "cursor-pointer")}
        >
          {ACTION_OPTIONS.map((a) => (
            <option key={a.kind} value={a.kind} className="bg-bg-card">
              {t(a.labelKey)}
            </option>
          ))}
        </select>

        <Field label={t("form.action_config")} small>
          <textarea
            value={form.actionConfig}
            onChange={(e) => patch({ actionConfig: e.target.value })}
            placeholder={
              ACTION_OPTIONS.find((a) => a.kind === form.actionKind)
                ?.placeholder ?? ""
            }
            rows={5}
            className={cn(inputClass, "resize-none font-mono")}
            spellCheck={false}
          />
        </Field>
        <Hint>{t("form.action_config_hint")}</Hint>
      </Section>
    </div>
  );
}

// -----------------------------------------------------------------------
// Internal building blocks
// -----------------------------------------------------------------------

const inputClass = cn(
  "w-full border border-border bg-bg px-3 py-2",
  "font-sans text-sm text-ink outline-none transition-colors",
  "placeholder:text-ink-muted focus:border-lime",
);

function Field({
  label,
  small,
  children,
}: {
  label: string;
  small?: boolean;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label
        className={cn(
          "block font-sans uppercase tracking-wider text-ink-muted",
          small ? "text-[10px]" : "text-[11px]",
        )}
      >
        {label}
      </label>
      {children}
    </div>
  );
}

function Section({
  title,
  help,
  children,
}: {
  title: string;
  help?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-2.5 border-t border-border pt-6">
      <div>
        <h3 className="font-sans text-base font-medium text-lime">
          {title}
        </h3>
        {help && <p className="mt-1 text-xs text-ink-dim">{help}</p>}
      </div>
      <div className="space-y-2.5">{children}</div>
    </div>
  );
}

function Hint({ children }: { children: React.ReactNode }) {
  return <p className="text-[11px] text-ink-muted">{children}</p>;
}

function RadioPill({
  checked,
  onClick,
  icon: Icon,
  label,
}: {
  checked: boolean;
  onClick: () => void;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 border px-3 py-1.5 text-xs transition-colors",
        checked
          ? "border-lime bg-lime/10 text-lime"
          : "border-border bg-bg-card text-ink-dim hover:border-border-strong hover:text-ink",
      )}
    >
      <Icon className="h-3 w-3" />
      {label}
    </button>
  );
}
