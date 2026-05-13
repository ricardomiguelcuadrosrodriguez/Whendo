<div align="center">

<img src="./assets/logo.png" alt="whendo" width="180" />

# whendo

### *Tell your computer when to do things. In plain English.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with FastAPI](https://img.shields.io/badge/Made%20with-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![Self-hosted](https://img.shields.io/badge/100%25-self--hosted-success.svg)](#-quickstart)

**A self-hosted automation tool for your personal life — not your business.**

[Quickstart](#-quickstart) • [Examples](#-examples) • [How it works](#-how-it-works) • [🇪🇸 Español](./docs/README.es.md)

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

## 🎯 Why whendo?

Zapier is for businesses. IFTTT died. n8n is overkill. **whendo is for you.**

- 🧠 **YAML or plain English** (LLM parser coming soon)
- 🏠 **Self-hosted** — your data, your server, your rules
- 🆓 **Free forever** — open source, MIT, no accounts
- 🐳 **One-command install** — `docker compose up`
- 🔌 **Bring your own LLM** — Claude, OpenAI, or local Ollama
- 📱 **Notify anywhere** — Telegram, ntfy, email, Discord, webhooks

---

## ⚡ Quickstart

You need **two terminals** open. Backend and frontend run as separate services.

### Prerequisites

- **Python 3.10+** (3.12 recommended)
- **Node.js 20+**
- **Git**

Check what you have:
```bash
python3 --version
node --version
git --version
```

### Step 1 — Clone the repo

```bash
git clone https://github.com/ricardomiguelcuadrosrodriguez/Whendo.git
cd Whendo
```

### Step 2 — Set up the backend (Terminal 1)

```bash
# Create a Python virtual environment (so deps don't pollute your system)
python3 -m venv .venv
source .venv/bin/activate
# You should see (.venv) in your prompt now

# Install backend dependencies
pip install -r server/requirements.txt

# Create your config file
cp .env.example .env

# Create folders the server needs
mkdir -p recipes data

# Copy an example recipe so there's something to load
cp examples/01-rain-alert.yaml recipes/

# Start the server!
make dev
```

If everything worked, you'll see:
```
INFO whendo — whendo starting (tz=America/Lima)
INFO server.scheduler.loader — Loaded recipe 'Rain warning - Lima'
INFO server.scheduler.engine — Scheduled 'Rain warning - Lima': day at 7am
INFO Application startup complete.
INFO Uvicorn running on http://0.0.0.0:8000
```

✅ Backend is now running at **http://localhost:8000**.

Verify with `curl`:
```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

### Step 3 — Set up the frontend (Terminal 2)

Open a **second terminal** (don't close the first one!):

```bash
cd ~/path/to/Whendo

# Install frontend dependencies (takes 2-3 min the first time)
make install-web

# Start the Next.js dev server
make dev-web
```

You'll see:
```
▲ Next.js 15.1.0
- Local:  http://localhost:3000
✓ Ready in 2.1s
```

✅ Open **http://localhost:3000** in your browser. 🎉

### Step 4 — Try it out

In the browser:
1. You should see the **Rain warning - Lima** recipe as a card
2. Click **`run now`** to trigger it manually
3. Click the **`runs`** tab to see the execution history
4. Add a new YAML file to `recipes/` and click **`reload`** to pick it up

### To stop everything

In each terminal: **Ctrl + C**

### To restart later

```bash
# Terminal 1
cd ~/path/to/Whendo
source .venv/bin/activate
make dev

# Terminal 2
cd ~/path/to/Whendo
make dev-web
```

---

## 🐛 Troubleshooting

<details>
<summary><b>"ModuleNotFoundError: No module named 'server'"</b></summary>

You're running `uvicorn` from inside the `server/` folder. Run it from the project root:
```bash
cd ~/path/to/Whendo  # NOT cd server/
make dev
```
</details>

<details>
<summary><b>"externally-managed-environment" on pip install</b></summary>

You forgot to activate the virtual env. Run:
```bash
source .venv/bin/activate
# You should now see (.venv) in your prompt
which python  # should point to .venv/bin/python
```
</details>

<details>
<summary><b>Web shows "Could not reach backend"</b></summary>

The frontend can't talk to the backend. Make sure Terminal 1 is still running and check:
```bash
curl http://localhost:8000/health
```
If that fails, the backend crashed — look at the logs in Terminal 1.
</details>

<details>
<summary><b>Port 8000 or 3000 already in use</b></summary>

Something else is using that port. Kill it:
```bash
kill -9 $(lsof -t -i:8000)
kill -9 $(lsof -t -i:3000)
```
</details>

<details>
<summary><b>"make: command not found"</b></summary>

Install make: `sudo apt install make` (Debian/Ubuntu) or `brew install make` (macOS).
</details>

---

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
    message: "🎵 Nuevo de Morat: {{ release.name }}"
```
</details>

<details>
<summary><b>📰 AI digest</b></summary>

```yaml
name: "Monday AI digest"
when: { every: "monday at 9am" }
if:
  rss: { url: "https://news.smol.ai/rss.xml", since: "last_run" }
then:
  llm_summarize_and_notify:
    channel: "email"
    prompt: "Top 3 most interesting AI news, 1 line each."
```
</details>

---

## 🛠️ How it works

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

1. **You write a recipe** as a YAML file
2. **whendo loads it** from `./recipes/` and validates with Pydantic
3. **The scheduler** watches for the trigger (time, webhook, poll)
4. **When fired**, whendo fetches the source data and checks the condition
5. **If true**, whendo runs the action (Telegram, email, etc.)
6. **The run is logged** to SQLite for later inspection

The LLM is only used to convert plain English → YAML at recipe-creation time. **Runtime is deterministic, free, and fast.**

---

## 🧩 Building blocks

### Triggers (`when:`)
`schedule` (cron, "day at 7am") • `webhook` • `poll` (every N min) • `on_startup`

### Sources (`if:`) — *coming soon*
`weather` • `rss` • `youtube` • `spotify` • `github_releases` • `web_scrape` • `http_get`

### Actions (`then:`) — *coming soon*
`notify_telegram` • `notify_whatsapp` • `notify_email` • `notify_ntfy` • `notify_discord` • `webhook_post` • `llm_summarize_and_notify`

---

## 🗺️ Roadmap

- [x] Recipe YAML schema
- [x] Scheduler engine (APScheduler)
- [x] Web UI (Next.js dashboard)
- [x] Recipe loader with validation
- [x] Run history (SQLite)
- [ ] Real sources (weather, rss, github)
- [ ] Real actions (telegram, ntfy, email)
- [ ] LLM parser (Claude Haiku) — plain English → YAML
- [ ] Web UI: create recipes inline
- [ ] Docker Compose one-command setup
- [ ] Mobile companion app

Check [the issues](https://github.com/ricardomiguelcuadrosrodriguez/Whendo/issues) for what's next.

---

## 🤝 Contributing

PRs welcome. Each new source or action is ~100 lines. See [CONTRIBUTING.md](./CONTRIBUTING.md).

Star ⭐ the repo if you find this useful — it's the only metric I care about.

---

## 📜 License

MIT © Ricardo Cuadros

---

<div align="center">
<sub>Built with ❤️ in Lima, Perú</sub>
</div>
