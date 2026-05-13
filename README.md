<div align="center">

<img src="./assets/logo.png" alt="whendo" width="180" />

# whendo

### *Tell your computer when to do things. In plain English.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with FastAPI](https://img.shields.io/badge/Made%20with-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Self-hosted](https://img.shields.io/badge/100%25-self--hosted-success.svg)](#get-started-in-60-seconds)
[![Stars welcome](https://img.shields.io/badge/⭐-star_this_repo-yellow.svg)](#)

**A self-hosted automation tool for your personal life — not your business.**

[Get Started](#get-started-in-60-seconds) • [Examples](#examples) • [How it works](#how-it-works) • [Docs](./docs) • [🇪🇸 Español](./docs/README.es.md)

</div>

---

## 🤔 What is this?

**whendo** runs on your machine and does things for you on a schedule, when conditions are met, or when stuff changes in the world. You describe what you want in a small YAML file. whendo handles the rest.

```yaml
# recipes/rain-alert.yaml
name: "Avísame cuando llueva"
when:
  every: "day at 7am"
if:
  weather:
    location: "Lima, PE"
    condition: "rain_today"
then:
  notify_telegram:
    message: "☔ Hoy llueve. Lleva casaca."
```

Save the file. whendo picks it up. Done.

Not into YAML? Describe it in plain English and the built-in parser writes the YAML for you:

```bash
$ whendo new "tell me on telegram when it rains in lima"
✓ Created recipes/rain-alert.yaml
```

## 🎯 Why whendo?

Zapier is for businesses. IFTTT died. n8n is overkill. **whendo is for you.**

- 🧠 **Plain English or YAML** — your call, both work
- 🏠 **Self-hosted** — your data, your server, your rules
- 🆓 **Free forever** — open source, MIT license, no accounts
- 🐳 **One command install** — `docker compose up`
- 🔌 **Bring your own LLM** — Claude (default), OpenAI, or fully local with Ollama
- 📱 **Notify anywhere** — Telegram, WhatsApp, email, ntfy, Discord, webhooks
- 🌎 **Built for real life** — weather, RSS, YouTube, Spotify, prices, scraping

## ⚡ Get started in 60 seconds

```bash
git clone https://github.com/ricardomiguelcuadrosrodriguez/whendo
cd whendo
cp .env.example .env   # add your Claude API key + Telegram bot token
docker compose up
```

Open `http://localhost:3000` and you're in. Drop a `.yaml` file into `recipes/` and whendo will run it.

> 💡 **No API key?** whendo works fully offline with [Ollama](https://ollama.com). Set `LLM_PROVIDER=ollama` in `.env`.

## 📚 Examples

Real recipes that ship in [`examples/`](./examples). Copy, tweak, run.

<details>
<summary><b>☔ Weather alerts</b></summary>

```yaml
name: "Rain warning"
when: { every: "day at 7am" }
if:
  weather: { location: "Lima, PE", condition: "rain_today" }
then:
  notify_telegram: { message: "☔ Lleva casaca hoy." }
```
</details>

<details>
<summary><b>🎵 New music releases</b></summary>

```yaml
name: "New from Morat"
when: { every: "friday at 6pm" }
if:
  spotify_new_release: { artist: "Morat" }
then:
  notify_telegram:
    message: "🎵 Nuevo de Morat: {{ release.name }} — {{ release.url }}"
```
</details>

<details>
<summary><b>💸 Price drop watcher</b></summary>

```yaml
name: "Tesla Model Y deal"
when: { every: "6 hours" }
if:
  web_scrape:
    url: "https://www.mercadolibre.com.pe/tesla-model-y"
    selector: ".price"
    below: 35000
then:
  notify_whatsapp:
    to: "+51999999999"
    message: "🚗 Tesla bajó a {{ price }}!"
```
</details>

<details>
<summary><b>📰 AI news digest</b></summary>

```yaml
name: "Monday AI digest"
when: { every: "monday at 9am" }
if:
  rss: { url: "https://news.smol.ai/rss.xml", since: "last_run" }
then:
  llm_summarize_and_notify:
    channel: "email"
    prompt: "Top 3 most interesting AI news this weekend, 1 line each."
```
</details>

<details>
<summary><b>🚨 Earthquake alerts (Peru)</b></summary>

```yaml
name: "Sismo cerca de Lima"
when: { every: "5 minutes" }
if:
  rss:
    url: "https://www.igp.gob.pe/feed/sismos"
    contains: "Lima"
    magnitude_above: 4.0
then:
  notify_ntfy:
    topic: "ricardo-alerts"
    title: "🚨 Sismo cerca"
    message: "Magnitud {{ item.magnitude }} a {{ item.distance }}km"
```
</details>

[See all 20+ examples →](./examples)

## 🛠️ How it works

```
┌────────────────────────────────────────────────────────────────┐
│                        whendo server                           │
│                                                                │
│   recipes/*.yaml ──▶ Parser ──▶ Validator ──▶ Scheduler        │
│        ▲                                          │            │
│        │                                          ▼            │
│   "new" CLI ──▶ LLM (Claude) ──▶ YAML       Executor           │
│                                              │   │   │         │
│                                              ▼   ▼   ▼         │
│                                          Trigger  Source  Action │
│                                          (cron)   (api)  (send) │
└────────────────────────────────────────────────────────────────┘
```

1. **You write a recipe** (YAML file) or describe it in English
2. **whendo loads it** from `./recipes/` and validates the schema
3. **The scheduler watches** for the trigger (a time, a webhook, a poll interval)
4. **When fired**, whendo fetches the source data and checks the condition
5. **If the condition is true**, whendo runs the action (sends a notification, etc.)

The LLM is only used at recipe-creation time, not at runtime. **Runtime is deterministic, free, and fast.**

## 🧩 Building blocks

### Triggers
`schedule` (cron) • `webhook` • `poll` (every N minutes) • `email_received`

### Sources
`weather` • `rss` • `youtube` • `spotify` • `github_releases` • `web_scrape` • `http_get` • `tweet` • `reddit`

### Actions
`notify_telegram` • `notify_whatsapp` • `notify_email` • `notify_ntfy` • `notify_discord` • `webhook_post` • `llm_summarize_and_notify` • `run_shell`

[Full catalog →](./docs/building-blocks.md)

## 🗺️ Roadmap

- [x] Recipe YAML schema
- [x] Scheduler (APScheduler)
- [x] LLM parser (Claude Haiku)
- [x] Core sources: weather, RSS, github releases
- [x] Core actions: telegram, ntfy, email
- [ ] Web UI for browsing/editing recipes
- [ ] More sources: youtube, spotify, web_scrape
- [ ] Recipe marketplace (community-shared recipes)
- [ ] Mobile app companion (optional)

## 🤝 Contributing

PRs welcome. Especially for new sources and actions — each one is ~100 lines. See [CONTRIBUTING.md](./CONTRIBUTING.md).

Star ⭐ the repo if you find this useful. It's the only metric I care about.

## 📜 License

MIT © Ricardo Cuadros

---

<div align="center">
<sub>Built with ❤️ in Lima, Perú</sub>
</div>
