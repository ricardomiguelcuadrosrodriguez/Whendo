/**
 * Shared types and YAML serialization for the recipe form.
 * Kept dead simple — no external YAML library needed for our small schema.
 */

export type WhenKind = "every" | "webhook" | "on_startup";

export type SourceKind =
  | "none"
  | "weather"
  | "rss"
  | "github_releases"
  | "spotify_new_release"
  | "web_scrape"
  | "http_get";

export type ActionKind =
  | "notify_telegram"
  | "notify_ntfy"
  | "notify_email"
  | "notify_discord"
  | "notify_whatsapp"
  | "webhook_post"
  | "llm_summarize_and_notify"
  | "run_shell";

export type RecipeFormState = {
  name: string;
  description: string;
  enabled: boolean;
  // When
  whenKind: WhenKind;
  whenEvery: string;       // "day at 7am", "5 minutes", cron
  whenWebhook: string;     // path
  // Source (optional)
  sourceKind: SourceKind;
  sourceConfig: string;    // YAML-snippet text the user types
  // Action
  actionKind: ActionKind;
  actionConfig: string;    // YAML-snippet text the user types
};

export const DEFAULT_FORM: RecipeFormState = {
  name: "",
  description: "",
  enabled: true,
  whenKind: "every",
  whenEvery: "day at 9am",
  whenWebhook: "",
  sourceKind: "none",
  sourceConfig: "",
  actionKind: "notify_ntfy",
  actionConfig: 'topic: "my-topic"\nmessage: "Hello from whendo!"',
};

/** Indent every non-empty line by `n` spaces. */
function indent(text: string, n: number): string {
  const pad = " ".repeat(n);
  return text
    .split("\n")
    .map((line) => (line.trim() === "" ? "" : pad + line))
    .join("\n");
}

/** Quote a YAML string if it could be misinterpreted as something else. */
function safeYamlString(value: string): string {
  if (!value) return '""';
  if (/^[a-zA-Z][\w \-./@:,!?¡¿áéíóúüñÁÉÍÓÚÜÑ]*$/.test(value)) {
    // Wrap in double quotes anyway to be safe with reserved words.
    return `"${value.replace(/"/g, '\\"')}"`;
  }
  return `"${value.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
}

/** Convert a RecipeFormState into a YAML string. */
export function formToYaml(form: RecipeFormState): string {
  const lines: string[] = [];

  lines.push(`name: ${safeYamlString(form.name)}`);
  if (form.description.trim()) {
    lines.push(`description: ${safeYamlString(form.description)}`);
  }
  if (!form.enabled) {
    lines.push(`enabled: false`);
  }

  // when:
  lines.push(`when:`);
  if (form.whenKind === "every") {
    lines.push(`  every: ${safeYamlString(form.whenEvery)}`);
  } else if (form.whenKind === "webhook") {
    lines.push(`  webhook: ${safeYamlString(form.whenWebhook)}`);
  } else {
    lines.push(`  on_startup: true`);
  }

  // if: (optional)
  if (form.sourceKind !== "none") {
    lines.push(`if:`);
    lines.push(`  ${form.sourceKind}:`);
    const cfg = form.sourceConfig.trim();
    if (cfg) {
      lines.push(indent(cfg, 4));
    } else {
      lines.push(`    {}`);
    }
  }

  // then:
  lines.push(`then:`);
  lines.push(`  ${form.actionKind}:`);
  const actionCfg = form.actionConfig.trim();
  if (actionCfg) {
    lines.push(indent(actionCfg, 4));
  } else {
    lines.push(`    {}`);
  }

  return lines.join("\n") + "\n";
}
