# Installation

whendo runs as two services: a Python backend (FastAPI + APScheduler) and a Next.js frontend. You need **two terminals** open.

## Prerequisites

- **Python 3.10+** (3.12 recommended)
- **Node.js 20+**
- **Git**

Check what you have:

```bash
python3 --version
node --version
git --version
```

## Step 1 — Clone the repo

```bash
git clone https://github.com/ricardomiguelcuadrosrodriguez/Whendo.git
cd Whendo
```

## Step 2 — Set up the backend (Terminal 1)

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

# Start the server
make dev
```

If everything worked you should see:

```
INFO whendo — whendo starting (tz=America/Lima)
INFO server.scheduler.loader — Loaded recipe 'Rain warning - Lima'
INFO server.scheduler.engine — Scheduled 'Rain warning - Lima': day at 7am
INFO Application startup complete.
INFO Uvicorn running on http://0.0.0.0:8000
```

Verify with `curl`:

```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

## Step 3 — Set up the frontend (Terminal 2)

Open a **second terminal** (don't close the first one):

```bash
cd ~/path/to/Whendo

# Install frontend dependencies (takes 2-3 min the first time)
make install-web

# Start the Next.js dev server
make dev-web
```

You should see:

```
▲ Next.js 15.1.0
- Local:  http://localhost:3000
✓ Ready in 2.1s
```

Open **http://localhost:3000** in your browser.

## Step 4 — Configure credentials

You can either edit `.env` directly, or visit **http://localhost:3000/settings** and fill in the forms there. The settings page is recommended for non-programmers and supports an optional master password that encrypts secrets at rest. See [settings.md](./settings.md) (coming soon) for details.

At minimum, to make the rain-alert example fire a real Telegram message, set:

- `OPENWEATHER_API_KEY` (free tier at openweathermap.org/api)
- `TELEGRAM_BOT_TOKEN` (talk to `@BotFather`)
- `TELEGRAM_DEFAULT_CHAT_ID` (message your bot, then visit `https://api.telegram.org/bot<token>/getUpdates`)

## Step 5 — Try it out

In the browser:

1. You should see the **Rain warning - Lima** recipe as a card
2. Click **`run now`** to trigger it manually
3. Click the **`runs`** tab to see the execution history
4. Add a new YAML file to `recipes/` and click **`reload`** to pick it up
5. Click the **`settings`** tab to configure credentials and API keys

## Stopping and restarting

To stop: **Ctrl + C** in each terminal.

To restart later:

```bash
# Terminal 1
cd ~/path/to/Whendo
source .venv/bin/activate
make dev

# Terminal 2
cd ~/path/to/Whendo
make dev-web
```

## Need help?

- Something not working? See [troubleshooting.md](./troubleshooting.md).
- Want to write your first recipe? See [recipe-reference.md](./recipe-reference.md) and [examples.md](./examples.md).
