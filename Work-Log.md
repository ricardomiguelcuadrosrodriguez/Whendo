# Whendo — Work Log

> A running log of what got done in each session. Update this file at the end of every session.

---

## Session 1 — Project setup (May 12-13, 2026)

**Worked on:** Initial scaffolding, repo creation, backend scheduler, web UI.

**Done:**
- Decided product direction: personal-first, self-hosted, YAML+LLM, OSS MIT
- Created GitHub repo at `ricardomiguelcuadrosrodriguez/Whendo`
- Backend skeleton: FastAPI + APScheduler + SQLAlchemy + Pydantic
  - `server/main.py` — app + lifespan
  - `server/config.py` — settings from .env
  - `server/db/schema.py` — Recipe (Pydantic) + Run/SourceState (SQLAlchemy)
  - `server/db/connection.py` — engine + sessions
  - `server/scheduler/engine.py` — wraps APScheduler
  - `server/scheduler/loader.py` — reads YAML
  - `server/scheduler/trigger_parser.py` — parses "day at 7am" etc.
  - `server/scheduler/executor.py` — STUB only
  - `server/api/health.py`, `recipes.py`, `runs.py`
  - 22 tests passing
- Frontend: Next.js 15 + Tailwind + TypeScript strict
  - Custom palette: bg/ink/lime/flame
  - Terminal-aesthetic header with logo SVG (14 ellipses)
  - Logo PNG variants for README
  - Recipe cards with pipeline viz
  - Runs history view with expandable details
  - i18n EN/ES (no library, just objects + React context)
  - LocaleSwitcher dropdown
  - NewRecipeDialog with Form/YAML tabs and sync
  - Humanized labels for sources/actions in dropdowns
- Docker compose, Makefile, README with full setup steps

**Bugs encountered + fixes:**
- `make dev` failed with `ModuleNotFoundError: No module named 'server'`
  - Cause: Makefile had `cd server && uvicorn ...`
  - Fix: Removed `cd`, run uvicorn from project root
- Same setup also failed because `server/config.py` was missing
  - Cause: When merging tar bundles, config.py got lost
  - Fix: Re-added the file
- EADDRINUSE port 3000 errors
  - Cause: Zombie Next.js processes from Trash folder
  - Fix: Kill processes manually

**State at end of session:**
- Backend running on :8000, frontend on :3000
- Rain-alert recipe loads, scheduler works, but `notify_telegram` is a stub (only logs)

---

## Session 2 — Sources + Actions reales (May 13, 2026)

**Worked on:** Wiring real sources and actions so `01-rain-alert.yaml` can fire a real Telegram message.

**Done:**
- Spanish localization cleanup before starting (separate commit):
  - Author name corrected to full legal form in LICENSE/README/docs
  - Argentine voseo replaced with neutral tú forms across i18n.ts and Spanish README
  - 🇪🇸 → 🇵🇪 in the README language switcher
- Created `recipes/` directory and seeded with `01-rain-alert.yaml`
- `server/actions/` package:
  - `base.py` — `Action` ABC with `async run(config, context) -> dict`
  - `rendering.py` — Jinja2 `render_value()` walks dicts/lists recursively, renders only strings, leaves non-templates untouched, uses `StrictUndefined` to fail loudly on missing vars
  - `telegram.py` — `TelegramAction` via `python-telegram-bot` Bot.send_message, supports optional ParseMode
  - `ntfy.py` — `NtfyAction` via httpx POST, supports Title/Priority/Tags/Click headers
  - `email.py` — `EmailAction` via smtplib in `asyncio.to_thread`
  - `__init__.py` — `ACTIONS` registry dict
- `server/sources/` package:
  - `base.py` — `Source` ABC with `async check(config, *, recipe_name) -> (bool, dict)`
  - `weather.py` — `WeatherSource` (OpenWeatherMap), supports `rain_today` (forecast endpoint, filters today in city TZ), `rain_now`, `temp_above:N`, `temp_below:N`
  - `rss.py` — `RssSource` (feedparser) with SourceState persistence to track last seen entry
  - `github_releases.py` — `GithubReleasesSource` (GitHub API) with SourceState for last seen tag
  - `__init__.py` — `SOURCES` registry dict
- Replaced executor stub in `server/scheduler/executor.py`:
  - Resolves source from registry, calls `check()`
  - If False → persists Run with `status="skipped"`, returns early
  - If True or no source → renders action config via Jinja2 with source context
  - Dispatches to action registry, persists Run with `status="success"` or `"failed"`
- New tests (25 total, all passing alongside the 22 original = **47/47**):
  - `test_rendering.py` — 6 cases for Jinja2 rendering
  - `test_weather_source.py` — 6 cases for forecast + current-weather paths
  - `test_ntfy_action.py` — 3 cases for HTTP POST, missing topic/message validation

**Bugs encountered + fixes:**
- Test `test_rain_today_fires_when_forecast_has_rain` failed initially
  - Cause: Used `dt: 0` (Unix epoch, Jan 1 1970) for the forecast entry; executor's "is this entry today?" filter correctly excluded it
  - Fix: Use `int(time.time())` so the stub entry matches today's date

**End-to-end smoke tests (with stubbed source/action):**
- Skip path: source returns `False` → run persisted as `skipped`, action never called ✅
- Fire path: source returns `(True, {location, description, precipitation_mm})`, action receives Jinja-rendered config like `"☔ Llueve en Lima: lluvia ligera (1.2mm)"` ✅
- Recipe loads from `recipes/`, registries populate at import time ✅

**State at end of session:**
- Backend wires sources → executor → actions end-to-end
- No `.env` secrets configured yet — Telegram/Email/Weather all raise clear `RuntimeError` if missing keys
- To send a real Telegram message: fill `OPENWEATHER_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_DEFAULT_CHAT_ID` in `.env`, restart the server, the recipe fires at 7am Lima time (or change `every` to `1 minute` for testing)

---

## Session 2.5 — Settings UI (May 14, 2026)

**Worked on:** Replacing the `.env`-only configuration with a proper Settings store + web UI, since end users are not programmers and shouldn't have to edit dotfiles.

**Done:**
- Backend: persistent settings store
  - `cryptography>=43` added to `server/requirements.txt`
  - New tables `app_setting` (key, value, is_secret, is_encrypted, updated_at) and `app_meta` (master salt / verifier / KDF iters)
  - `server/settings_service.py` with:
    - `SETTINGS_CATALOG` declaring 22 user-configurable keys across 3 categories (notifications, data_sources, ai)
    - Optional master password (PBKDF2-SHA256 with 600k iters → Fernet key, stored only in memory)
    - `init_master_password`, `unlock`, `lock`, `change_master_password` (re-encrypts all secrets)
    - `set/get/delete/is_set/list_visible` (secrets masked as `••••••` in list)
    - `resolve(key, recipe_override, env_fallback)` for the runtime resolver
  - `server/api/settings.py` with REST endpoints: list, _status, PUT/DELETE per-key, _set-master, _unlock, _lock, _change-master
  - Refactored Telegram / ntfy / Email actions and Weather / GitHub Releases sources to read credentials via `settings_service.resolve(...)` so the priority is `recipe override → DB → .env → error`
- Frontend: `/settings` page
  - `web/lib/api.ts` extended with `listSettings`, `settingsStatus`, `saveSetting`, `deleteSetting`, `setMasterPassword`, `unlockSettings`, `lockSettings`, `changeMasterPassword`
  - `web/app/settings/page.tsx`: Security panel (status, set master / unlock / lock / change master) and per-service cards grouped by category, with masked password inputs for secrets, "configured / not configured" badges, per-card save buttons, "leave empty to keep current" UX for already-set secrets
  - Settings link added to the nav on `/` and `/runs`
  - 31 new i18n keys (EN/ES) for nav.settings and settings.*
- Tests
  - 14 new pytest cases in `test_settings_service.py` covering plain roundtrip, master init re-encrypts existing secrets, lock/unlock, wrong password, change master re-encrypts, runtime resolver priority — **61/61 total backend tests pass**
- End-to-end API smoke (via FastAPI TestClient):
  - GET /api/settings → 22 catalog items returned, secrets masked
  - PUT plain + PUT secret + GET → secret value is `••••••` in list, ntfy plain is the real value
  - POST /_set-master → encrypted_count goes 0 → 1 (existing secret encrypted in place)
  - Lock → unlock works; wrong password returns 401; unknown key returns 404
- TypeScript `tsc --noEmit` clean

**Bugs encountered + fixes:**
- During the i18n edit, the IDE diagnostic reported missing keys on the `en` / `es` objects between sequential edits to the type union and the two locale blocks — false positive that cleared once all three edits landed. Confirmed clean with `tsc --noEmit`.

**State at end of session:**
- A non-programmer can now open `/settings`, paste their Telegram bot token + chat ID, hit Save and have whendo send a real message. They never need to touch `.env`.
- Master password is optional — if not set, secrets are stored as plain text in the local SQLite DB (same security surface as the previous `.env`). If set, secrets are Fernet-encrypted on disk and require an unlock after each server restart.
- Sources / actions fall back to `.env` when a DB value isn't present, so existing `.env`-only setups keep working.

---

## Session 3 — Frontend polish (NEXT)

**Goal:** Recipe detail page + live logs.

**Plan:**
- New route `/recipes/[name]`
- YAML view (read-only)
- Logs in real-time (poll runs endpoint every 2s for now; WebSocket later if needed)
- Edit button (opens NewRecipeDialog with prefilled data)
- Delete button with confirmation

---

## Session 4 — LLM Parser

**Goal:** Natural language → YAML.

**Plan:**
- `server/parser/llm.py` with anthropic / openai / ollama backends
- System prompt with Recipe schema + few-shot examples
- API endpoint `POST /api/recipes/parse` body `{text: string}` → returns YAML
- CLI command `python -m server.cli new "your description"`
- Retry once if Pydantic validation fails on first response

---

## Session 5 — AI chatbox in dialog

**Goal:** Third tab in NewRecipeDialog for natural-language creation.

**Plan:**
- New tab "AI" alongside Form and YAML
- Textarea + "Generate" button
- Calls `POST /api/recipes/parse`
- Shows generated YAML
- User can edit before saving

---

## Session 6 — Launch prep

**Goal:** Ship publicly.

**Plan:**
- E2E tests with Playwright
- Demo video (30-45s) recorded with OBS
- README polish with GIFs embedded
- Launch on HN "Show HN", r/selfhosted, r/Python, X

---

## How to use this log

After every session:
1. Move "NEXT" goal to a new "Session N" header
2. Fill in what got Done / Bugs / State
3. Write the new NEXT plan
4. Commit the file
