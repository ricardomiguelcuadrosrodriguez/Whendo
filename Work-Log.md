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
