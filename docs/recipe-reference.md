# Recipe reference

Every recipe is a YAML file with three top-level blocks: `when:`, `if:` (optional) and `then:`.

```yaml
name: "Human-readable name"
description: "Optional one-liner."
enabled: true

when:
  every: "day at 7am"

if:
  weather:
    location: "Lima, PE"
    condition: "rain_today"

then:
  notify_telegram:
    message: "☔ Lleva casaca."
```

## `when:` — Triggers

Exactly one of these keys must be set.

| Key | Meaning | Example |
|---|---|---|
| `every` | A schedule string | `"day at 7am"`, `"5 minutes"`, `"monday at 6pm"`, `"0 9 * * *"` (cron) |
| `webhook` | Fire when `POST /webhooks/<path>` is called | `webhook: "my-trigger"` |
| `on_startup` | Run once each time the server starts | `on_startup: true` |

Supported `every` forms:

- `"day at HH:MM"` (e.g. `"day at 7am"`, `"day at 18:30"`)
- `"<weekday> at HH:MM"` (e.g. `"monday at 9am"`)
- `"N minutes"` / `"N hours"` / `"N days"`
- Any valid cron expression: `"0 9 * * *"`

## `if:` — Sources

Optional. If omitted, the action always runs when the trigger fires. Exactly one source key when set.

### `weather` (OpenWeatherMap)

```yaml
weather:
  location: "Lima, PE"
  condition: "rain_today"   # rain_today | rain_now | temp_above:N | temp_below:N
  api_key: "..."            # optional override; falls back to OPENWEATHER_API_KEY
```

**Context for templating:** `location`, `city`, `temp_c`, `feels_like_c`, `humidity`, `description`, `weather_main`, `precipitation_mm`.

### `rss`

```yaml
rss:
  url: "https://hnrss.org/frontpage"
```

Fires when there's a new entry since the last check. **State is persisted** per recipe — the first run primes the state without firing.

**Context:** `feed_url`, `feed_title`, `title`, `link`, `summary`, `author`, `published`, `is_first_run`.

### `github_releases`

```yaml
github_releases:
  repo: "fastapi/fastapi"           # owner/name
  include_prereleases: false        # optional
  token: "..."                       # optional; falls back to GITHUB_TOKEN
```

Fires on a new release tag. **State is persisted** per recipe.

**Context:** `repo`, `tag`, `name`, `url`, `body`, `author`, `published_at`, `is_first_run`.

### Coming soon

`spotify_new_release` · `youtube` · `web_scrape` · `http_get`

## `then:` — Actions

Exactly one action key. Every string field is Jinja2-rendered against the source context.

### `notify_telegram`

```yaml
notify_telegram:
  message: "☔ Lleva casaca hoy."
  bot_token: "..."           # optional override; falls back to settings / .env
  chat_id: "..."             # optional override; falls back to settings / .env
  parse_mode: "html"         # optional: html | markdown | markdownv2
```

### `notify_ntfy`

```yaml
notify_ntfy:
  topic: "my-topic"          # optional override; falls back to NTFY_DEFAULT_TOPIC
  message: "Hello"
  title: "Alert"             # optional, becomes the notification title
  priority: 4                # optional, 1-5
  tags: ["rain", "lima"]     # optional, emoji shortcodes work
  click: "https://example.com"  # optional, URL opened on tap
  server: "https://ntfy.sh"  # optional, override NTFY_SERVER
```

### `notify_email` (SMTP)

```yaml
notify_email:
  to: "you@example.com"
  subject: "Subject line"
  body: "Body text."
  # All SMTP credentials fall back to settings / .env if not specified:
  # smtp_host, smtp_port, smtp_user, smtp_pass, from
```

### Coming soon

`notify_discord` · `notify_whatsapp` · `webhook_post` · `llm_summarize_and_notify` · `run_shell`

## Resolution order for credentials

For every credential whendo needs (API keys, bot tokens, SMTP passwords, etc.) the lookup order is:

1. **Inline override in the recipe YAML** (e.g. `bot_token:` inside `notify_telegram:`)
2. **Settings store** configured at `/settings` in the web UI
3. **`.env` file** at the project root
4. **Error** — the action raises `RuntimeError` with a hint about what to configure
