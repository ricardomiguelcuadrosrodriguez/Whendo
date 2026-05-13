"use client";

import { useEffect, useState, useTransition } from "react";
import {
  X,
  Save,
  AlertTriangle,
  CheckCircle2,
  FormInput,
  Code2,
} from "lucide-react";

import { api } from "@/lib/api";
import { useLocale } from "@/lib/locale-context";
import {
  DEFAULT_FORM,
  type RecipeFormState,
  formToYaml,
} from "@/lib/recipe-form";
import { cn } from "@/lib/utils";
import { RecipeFormBuilder } from "./RecipeFormBuilder";

type Props = {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
};

type Tab = "form" | "yaml";

export function NewRecipeDialog({ open, onClose, onCreated }: Props) {
  const { t } = useLocale();
  const [tab, setTab] = useState<Tab>("form");
  const [form, setForm] = useState<RecipeFormState>(DEFAULT_FORM);
  const [yamlText, setYamlText] = useState<string>("");
  const [yamlDirty, setYamlDirty] = useState(false);
  const [feedback, setFeedback] = useState<
    { type: "success" | "error"; message: string } | null
  >(null);
  const [isPending, startTransition] = useTransition();

  // When the dialog opens fresh, reset everything
  useEffect(() => {
    if (open) {
      setForm(DEFAULT_FORM);
      setYamlText(formToYaml(DEFAULT_FORM));
      setYamlDirty(false);
      setTab("form");
      setFeedback(null);
    }
  }, [open]);

  // Keep YAML in sync with form *unless* the user has manually edited the YAML
  useEffect(() => {
    if (!yamlDirty) {
      setYamlText(formToYaml(form));
    }
  }, [form, yamlDirty]);

  // Close on Escape
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  const handleSave = () => {
    setFeedback(null);
    // Always send the YAML text — it's the source of truth at save time.
    // If the user is in form mode and never touched YAML, this is the
    // generated YAML. If they edited YAML manually, this preserves it.
    const yamlToSave = tab === "yaml" || yamlDirty ? yamlText : formToYaml(form);

    startTransition(async () => {
      try {
        const res = await api.createRecipe(yamlToSave);
        setFeedback({
          type: "success",
          message: `${t("new_recipe.saved")} (${res.file})`,
        });
        onCreated();
        setTimeout(() => onClose(), 1200);
      } catch (e) {
        setFeedback({
          type: "error",
          message: (e as Error).message,
        });
      }
    });
  };

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 animate-fade-in"
      onClick={onClose}
    >
      <div
        className="flex h-full max-h-[720px] w-full max-w-3xl flex-col border border-border bg-bg-card"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between border-b border-border px-5 py-3">
          <h2 className="font-mono text-sm text-ink">
            {t("new_recipe.title")}
          </h2>
          <button
            onClick={onClose}
            className="text-ink-muted transition-colors hover:text-ink"
            aria-label="Close"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border bg-bg-elevated">
          <TabButton
            active={tab === "form"}
            onClick={() => setTab("form")}
            icon={FormInput}
            label={t("new_recipe.tab_form")}
          />
          <TabButton
            active={tab === "yaml"}
            onClick={() => {
              // Switching to YAML for the first time, snapshot the current form
              if (!yamlDirty) setYamlText(formToYaml(form));
              setTab("yaml");
            }}
            icon={Code2}
            label={t("new_recipe.tab_yaml")}
          />
        </div>

        {/* Tab content */}
        <div className="flex-1 overflow-y-auto">
          {tab === "form" ? (
            <RecipeFormBuilder form={form} onChange={setForm} />
          ) : (
            <textarea
              value={yamlText}
              onChange={(e) => {
                setYamlText(e.target.value);
                setYamlDirty(true);
              }}
              spellCheck={false}
              className="h-full min-h-[520px] w-full resize-none bg-bg p-4 font-mono text-sm text-ink outline-none"
            />
          )}
        </div>

        {/* Feedback */}
        {feedback && (
          <div
            className={cn(
              "border-t px-5 py-3 font-mono text-xs",
              feedback.type === "success"
                ? "border-success/30 bg-success/5 text-success"
                : "border-danger/30 bg-danger/5 text-danger",
            )}
          >
            {feedback.type === "success" ? (
              <CheckCircle2 className="mr-2 inline h-3.5 w-3.5" />
            ) : (
              <AlertTriangle className="mr-2 inline h-3.5 w-3.5" />
            )}
            {feedback.message}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 border-t border-border px-5 py-3">
          <button
            onClick={onClose}
            className="border border-border bg-bg px-3 py-1.5 font-mono text-xs text-ink-dim transition-colors hover:border-border-strong hover:text-ink"
          >
            {t("new_recipe.cancel")}
          </button>
          <button
            onClick={handleSave}
            disabled={isPending || !form.name.trim()}
            className={cn(
              "flex items-center gap-2 border border-lime bg-lime/10 px-3 py-1.5 font-mono text-xs text-lime",
              "transition-colors hover:bg-lime/20",
              "disabled:cursor-not-allowed disabled:border-border disabled:bg-transparent disabled:text-ink-muted",
            )}
          >
            <Save className="h-3 w-3" />
            {isPending ? t("new_recipe.saving") : t("new_recipe.save")}
          </button>
        </div>
      </div>
    </div>
  );
}

function TabButton({
  active,
  onClick,
  icon: Icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ComponentType<{ className?: string }>;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-2 border-b-2 px-5 py-3 font-mono text-xs",
        "transition-colors",
        active
          ? "border-lime bg-bg-card text-lime"
          : "border-transparent text-ink-dim hover:bg-bg-card hover:text-ink",
      )}
    >
      <Icon className="h-3.5 w-3.5" />
      {label}
    </button>
  );
}
