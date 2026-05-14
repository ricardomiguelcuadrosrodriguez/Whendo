# How whendo works

```
┌────────────────────────────────────────────────────────────────┐
│                       whendo server                            │
│                                                                │
│   recipes/*.yaml ──▶ Loader ──▶ Validator ──▶ Scheduler        │
│                                                  │             │
│                                                  ▼             │
│                                              Executor          │
│                                              │   │   │         │
│                                              ▼   ▼   ▼         │
│                                          Trigger Source Action │
└────────────────────────────────────────────────────────────────┘
```

1. **You write a recipe** as a YAML file under `recipes/`.
2. **whendo loads it** from `./recipes/` and validates with Pydantic.
3. **The scheduler** (APScheduler) registers a trigger for the recipe (cron, interval, on_startup, or webhook).
4. **When the trigger fires**, the executor calls the recipe's `if:` source (if any). The source returns `(should_fire, context)`.
5. **If `should_fire` is true**, the executor renders every string in the `then:` action's config as a Jinja2 template using the source context, then calls the registered action.
6. **The run is persisted** to SQLite for inspection in the web UI.

The LLM is only used to convert plain English → YAML at recipe-creation time (coming soon). **Runtime is deterministic, free, and fast** — no LLM call per execution.

## Components

| Path | Role |
|---|---|
| `server/main.py` | FastAPI app + lifespan (initialises DB and scheduler) |
| `server/scheduler/engine.py` | APScheduler wrapper |
| `server/scheduler/loader.py` | Reads YAML recipes from disk |
| `server/scheduler/trigger_parser.py` | Parses `every:` strings into APScheduler triggers |
| `server/scheduler/executor.py` | Dispatches source → render → action and persists the run |
| `server/sources/` | One module per source kind (weather, rss, github_releases) |
| `server/actions/` | One module per action kind (telegram, ntfy, email) |
| `server/settings_service.py` | Persistent settings store with optional Fernet encryption |
| `server/api/` | REST endpoints (recipes, runs, settings, health) |
| `server/db/schema.py` | Pydantic recipe schema + SQLAlchemy tables |
| `web/` | Next.js 15 frontend (App Router, Tailwind, custom palette) |

## Data flow

1. **Trigger** (`when:`) — comes from APScheduler. Schedule string parsed by `trigger_parser.py`.
2. **Source** (`if:`) — optional. Returns `(bool, dict)`. The dict is the context for templating.
3. **Action** (`then:`) — required. Receives the rendered config + the source context. Returns a result dict.
4. **Run** row — persisted in SQLite with status `success | failed | skipped`, the rendered output and any error.

## State persistence

- **SQLite at `data/whendo.db`** — runs, source state (last RSS entry, last GitHub tag), settings.
- **`recipes/*.yaml`** — recipe definitions. Reloaded from disk on request.
- **`.env`** — fallback for credentials when a setting is not configured in the DB.

## Why these choices

| Choice | Why |
|---|---|
| **SQLite, not Postgres** | Personal self-hosted. Zero setup. Easy backup (one file). |
| **APScheduler, not Celery** | No need for distributed workers. Everything in-process. |
| **Pydantic for recipes** | Validation errors that point at the exact field. |
| **Jinja2 for templating** | Battle-tested. Stays out of the way when no template syntax is used. |
| **Next.js, not Vite/CRA** | Server-side rendering for the eventual public landing page. |
| **No auth in v1** | Self-hosted on localhost. Adding auth before there's a real multi-user case is premature. |
