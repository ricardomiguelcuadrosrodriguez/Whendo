/**
 * Lightweight i18n. Pure objects, no library.
 * Add a new language by adding a new entry to TRANSLATIONS.
 */

export type Locale = "en" | "es";

export const LOCALES: { code: Locale; label: string; flag: string }[] = [
  { code: "en", label: "English", flag: "🇺🇸" },
  { code: "es", label: "Español", flag: "🇵🇪" },
];

export const DEFAULT_LOCALE: Locale = "en";

type TranslationKey =
  // Header
  | "header.tagline"
  | "header.subline1"
  | "header.subline2"
  // Nav
  | "nav.recipes"
  | "nav.runs"
  // Recipes page
  | "recipes.title"
  | "recipes.loaded"
  | "recipes.with_errors"
  | "recipes.loading"
  | "recipes.reload"
  | "recipes.errors_title"
  | "recipes.failed_to_load"
  | "recipes.empty.title"
  | "recipes.empty.hint1"
  | "recipes.empty.hint2"
  | "recipes.backend_down.title"
  | "recipes.backend_down.hint"
  | "recipes.new"
  // Card
  | "card.next"
  | "card.run_now"
  | "card.queued"
  // Runs page
  | "runs.title"
  | "runs.executions"
  | "runs.refresh"
  | "runs.empty.title"
  | "runs.empty.hint"
  | "runs.could_not_load"
  | "runs.status"
  | "runs.started_at"
  | "runs.finished_at"
  | "runs.error"
  | "runs.output"
  // Footer
  | "footer.version"
  // New recipe dialog
  | "new_recipe.title"
  | "new_recipe.tab_form"
  | "new_recipe.tab_yaml"
  | "new_recipe.cancel"
  | "new_recipe.save"
  | "new_recipe.saving"
  | "new_recipe.saved"
  // Form fields
  | "form.name"
  | "form.name_placeholder"
  | "form.description"
  | "form.description_placeholder"
  | "form.enabled"
  | "form.section_when"
  | "form.section_when_help"
  | "form.when_every"
  | "form.when_webhook"
  | "form.when_on_startup"
  | "form.when_every_placeholder"
  | "form.when_every_hint"
  | "form.when_webhook_placeholder"
  | "form.when_on_startup_hint"
  | "form.section_if"
  | "form.section_if_help"
  | "form.source_none"
  | "form.source_config"
  | "form.source_config_hint"
  | "form.section_then"
  | "form.section_then_help"
  | "form.action_config"
  | "form.action_config_hint"
  // Friendly names for sources
  | "source.weather"
  | "source.rss"
  | "source.github_releases"
  | "source.spotify_new_release"
  | "source.web_scrape"
  | "source.http_get"
  // Friendly names for actions
  | "action.notify_telegram"
  | "action.notify_ntfy"
  | "action.notify_email"
  | "action.notify_discord"
  | "action.notify_whatsapp"
  | "action.webhook_post"
  | "action.llm_summarize_and_notify"
  | "action.run_shell";

type Translations = Record<Locale, Record<TranslationKey, string>>;

export const TRANSLATIONS: Translations = {
  en: {
    "header.tagline": "tell your computer when to do things",
    "header.subline1":
      "Self-hosted personal automation. Plain English or YAML.",
    "header.subline2": "Open source, free forever.",
    "nav.recipes": "automations",
    "nav.runs": "history",
    "recipes.title": "// automations",
    "recipes.loaded": "loaded",
    "recipes.with_errors": "with errors",
    "recipes.loading": "loading",
    "recipes.reload": "reload",
    "recipes.errors_title": "failed to load",
    "recipes.failed_to_load": "automation(s) failed to load",
    "recipes.empty.title": "No automations yet.",
    "recipes.empty.hint1":
      "Click 'new automation' to create your first one.",
    "recipes.empty.hint2":
      "Or drop a .yaml file in the recipes/ folder and click reload.",
    "recipes.backend_down.title": "Could not reach the server",
    "recipes.backend_down.hint":
      "Is the backend running on localhost:8000? Try 'make dev' in another terminal.",
    "recipes.new": "new automation",
    "card.next": "next:",
    "card.run_now": "run now",
    "card.queued": "queued ✓",
    "runs.title": "// recent executions",
    "runs.executions": "executions",
    "runs.refresh": "refresh",
    "runs.empty.title": "No executions yet.",
    "runs.empty.hint":
      "Automations will run when their schedule fires, or you can run them manually from the automations page.",
    "runs.could_not_load": "Could not load executions",
    "runs.status": "status",
    "runs.started_at": "started",
    "runs.finished_at": "finished",
    "runs.error": "error",
    "runs.output": "output",
    "footer.version": "whendo v0.1.0",
    "new_recipe.title": "// new automation",
    "new_recipe.tab_form": "form",
    "new_recipe.tab_yaml": "yaml",
    "new_recipe.cancel": "cancel",
    "new_recipe.save": "save",
    "new_recipe.saving": "saving",
    "new_recipe.saved": "saved ✓",
    "form.name": "Name",
    "form.name_placeholder": "e.g. Morning weather alert",
    "form.description": "Description (optional)",
    "form.description_placeholder": "Short note about what this does",
    "form.enabled": "Enabled",
    "form.section_when": "When should it run?",
    "form.section_when_help":
      "Pick a schedule, a webhook, or run it once at startup.",
    "form.when_every": "On a schedule",
    "form.when_webhook": "When a webhook is called",
    "form.when_on_startup": "Once at server startup",
    "form.when_every_placeholder": "day at 9am",
    "form.when_every_hint":
      "Examples: 'day at 7am' · 'monday at 6pm' · '5 minutes' · '0 9 * * *' (cron)",
    "form.when_webhook_placeholder": "my-trigger",
    "form.when_on_startup_hint":
      "Runs once each time the whendo server starts.",
    "form.section_if": "Check something first? (optional)",
    "form.section_if_help":
      "Only run the action if a condition is met. Leave empty to always run.",
    "form.source_none": "Always run (no condition)",
    "form.source_config": "Source settings",
    "form.source_config_hint":
      "Configure the source in YAML. Each source has its own fields.",
    "form.section_then": "What should happen?",
    "form.section_then_help": "The action that runs when the recipe fires.",
    "form.action_config": "Action settings",
    "form.action_config_hint":
      "Configure the action in YAML. Available fields depend on the action.",
    // Friendly names for sources
    "source.weather": "Weather forecast",
    "source.rss": "RSS feed",
    "source.github_releases": "GitHub releases",
    "source.spotify_new_release": "Spotify new release",
    "source.web_scrape": "Scrape a webpage",
    "source.http_get": "HTTP request",
    // Friendly names for actions
    "action.notify_telegram": "Send Telegram message",
    "action.notify_ntfy": "Send push notification (ntfy)",
    "action.notify_email": "Send email",
    "action.notify_discord": "Send Discord message",
    "action.notify_whatsapp": "Send WhatsApp message",
    "action.webhook_post": "POST to a webhook",
    "action.llm_summarize_and_notify": "Summarize with AI and notify",
    "action.run_shell": "Run a shell command",
  },
  es: {
    "header.tagline": "dile a tu computadora cuándo hacer cosas",
    "header.subline1":
      "Automatización personal self-hosted. Lenguaje natural o YAML.",
    "header.subline2": "Código abierto, gratis para siempre.",
    "nav.recipes": "automatizaciones",
    "nav.runs": "historial",
    "recipes.title": "// automatizaciones",
    "recipes.loaded": "cargadas",
    "recipes.with_errors": "con errores",
    "recipes.loading": "cargando",
    "recipes.reload": "recargar",
    "recipes.errors_title": "no se pudieron cargar",
    "recipes.failed_to_load": "automatización(es) no se cargaron",
    "recipes.empty.title": "Todavía no hay automatizaciones.",
    "recipes.empty.hint1":
      "Haz clic en 'nueva automatización' para crear la primera.",
    "recipes.empty.hint2":
      "O coloca un archivo .yaml en la carpeta recipes/ y haz clic en recargar.",
    "recipes.backend_down.title": "No se pudo conectar al servidor",
    "recipes.backend_down.hint":
      "¿Está corriendo el backend en localhost:8000? Prueba 'make dev' en otra terminal.",
    "recipes.new": "nueva automatización",
    "card.next": "próx.:",
    "card.run_now": "ejecutar",
    "card.queued": "en cola ✓",
    "runs.title": "// ejecuciones recientes",
    "runs.executions": "ejecuciones",
    "runs.refresh": "refrescar",
    "runs.empty.title": "Todavía no hay ejecuciones.",
    "runs.empty.hint":
      "Las automatizaciones se ejecutan cuando dispara su horario, o las puedes ejecutar manualmente desde la página de automatizaciones.",
    "runs.could_not_load": "No se pudieron cargar las ejecuciones",
    "runs.status": "estado",
    "runs.started_at": "inició",
    "runs.finished_at": "terminó",
    "runs.error": "error",
    "runs.output": "salida",
    "footer.version": "whendo v0.1.0",
    "new_recipe.title": "// nueva automatización",
    "new_recipe.tab_form": "formulario",
    "new_recipe.tab_yaml": "yaml",
    "new_recipe.cancel": "cancelar",
    "new_recipe.save": "guardar",
    "new_recipe.saving": "guardando",
    "new_recipe.saved": "guardada ✓",
    "form.name": "Nombre",
    "form.name_placeholder": "ej. Aviso de lluvia matutino",
    "form.description": "Descripción (opcional)",
    "form.description_placeholder": "Una línea sobre qué hace",
    "form.enabled": "Activa",
    "form.section_when": "¿Cuándo debe ejecutarse?",
    "form.section_when_help":
      "Elige un horario, un webhook, o que corra una vez al iniciar.",
    "form.when_every": "Con un horario",
    "form.when_webhook": "Cuando se llama un webhook",
    "form.when_on_startup": "Una vez al iniciar el servidor",
    "form.when_every_placeholder": "day at 9am",
    "form.when_every_hint":
      "Ejemplos: 'day at 7am' · 'monday at 6pm' · '5 minutes' · '0 9 * * *' (cron)",
    "form.when_webhook_placeholder": "mi-disparador",
    "form.when_on_startup_hint":
      "Se ejecuta una vez cada vez que arranca el servidor de whendo.",
    "form.section_if": "¿Chequear algo primero? (opcional)",
    "form.section_if_help":
      "Solo ejecutar la acción si se cumple una condición. Deja vacío para que siempre se ejecute.",
    "form.source_none": "Siempre ejecutar (sin condición)",
    "form.source_config": "Configuración de la fuente",
    "form.source_config_hint":
      "Configura la fuente en YAML. Cada fuente tiene sus propios campos.",
    "form.section_then": "¿Qué debe hacer?",
    "form.section_then_help":
      "La acción que se ejecuta cuando dispara la automatización.",
    "form.action_config": "Configuración de la acción",
    "form.action_config_hint":
      "Configura la acción en YAML. Los campos disponibles dependen de la acción.",
    // Nombres amigables para fuentes
    "source.weather": "Pronóstico del clima",
    "source.rss": "Feed RSS",
    "source.github_releases": "Releases de GitHub",
    "source.spotify_new_release": "Nuevo lanzamiento en Spotify",
    "source.web_scrape": "Scrapear una página web",
    "source.http_get": "Petición HTTP",
    // Nombres amigables para acciones
    "action.notify_telegram": "Enviar mensaje por Telegram",
    "action.notify_ntfy": "Enviar notificación push (ntfy)",
    "action.notify_email": "Enviar email",
    "action.notify_discord": "Enviar mensaje a Discord",
    "action.notify_whatsapp": "Enviar mensaje por WhatsApp",
    "action.webhook_post": "POST a un webhook",
    "action.llm_summarize_and_notify": "Resumir con IA y notificar",
    "action.run_shell": "Ejecutar un comando del sistema",
  },
};

export function t(locale: Locale, key: TranslationKey): string {
  return TRANSLATIONS[locale][key] ?? TRANSLATIONS[DEFAULT_LOCALE][key] ?? key;
}
