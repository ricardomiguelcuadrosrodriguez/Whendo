<div align="center">

<img src="./assets/logo.png" alt="whendo" width="180" />

# whendo

### *Tell your computer when to do things. In plain English.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Made with FastAPI](https://img.shields.io/badge/Made%20with-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![Self-hosted](https://img.shields.io/badge/100%25-self--hosted-success.svg)](./docs/installation.md)

**A self-hosted automation tool for your personal life — not your business.**

[Install](./docs/installation.md) • [Recipe reference](./docs/recipe-reference.md) • [Examples](./docs/examples.md) • [Architecture](./docs/architecture.md) • [🇵🇪 Español](./docs/README.es.md)

</div>

---

## What is this?

**whendo** runs on your machine and does things for you on a schedule, when conditions are met, or when stuff changes in the world. You describe what you want in a small YAML file. whendo handles the rest.

```yaml
# recipes/rain-alert.yaml
name: "Rain warning"
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

## Why whendo?

Zapier is for businesses. IFTTT died. n8n is overkill. **whendo is for you.**

- 🧠 **YAML or plain English** — natural-language parser coming soon
- 🏠 **Self-hosted** — your data, your server, your rules
- 🆓 **Free forever** — open source, MIT, no accounts
- 🔌 **Bring your own LLM** — Claude, OpenAI, or local Ollama
- 📱 **Notify anywhere** — Telegram, ntfy, email, Discord, webhooks
- 🔐 **Optional secret encryption** — master password protects API keys at rest

## Quickstart

You need Python 3.10+ and Node.js 20+. Open two terminals.

```bash
# Terminal 1 — backend
git clone https://github.com/ricardomiguelcuadrosrodriguez/Whendo.git
cd Whendo
python3 -m venv .venv && source .venv/bin/activate
pip install -r server/requirements.txt
cp .env.example .env
mkdir -p recipes data
cp examples/01-rain-alert.yaml recipes/
make dev
```

```bash
# Terminal 2 — frontend
cd Whendo
make install-web
make dev-web
```

Open **http://localhost:3000**. Configure your credentials at **http://localhost:3000/settings**.

Full walkthrough → [docs/installation.md](./docs/installation.md). Stuck? → [docs/troubleshooting.md](./docs/troubleshooting.md).

## Roadmap

- [x] Recipe YAML schema with Pydantic validation
- [x] Scheduler engine (APScheduler)
- [x] Web UI (Next.js dashboard)
- [x] Run history (SQLite)
- [x] Real sources — weather, RSS, GitHub releases
- [x] Real actions — Telegram, ntfy, email
- [x] Settings page with optional secret encryption
- [ ] LLM parser — plain English → YAML
- [ ] Create recipes from the web UI (natural language tab)
- [ ] Recipe detail page with live logs
- [ ] More sources — Spotify, YouTube, web scrape, HTTP get
- [ ] More actions — Discord, WhatsApp, webhook POST, AI summary
- [ ] Docker Compose one-command setup

Check [the issues](https://github.com/ricardomiguelcuadrosrodriguez/Whendo/issues) for what's next.

## Contributing

PRs welcome. Each new source or action is ~100 lines. See [CONTRIBUTING.md](./CONTRIBUTING.md).

Star ⭐ the repo if you find this useful — it's the only metric I care about.

## License

MIT © Ricardo Miguel Cuadros Rodriguez

---

<div align="center">
<sub>Built with ❤️ in Lima, Perú</sub>
</div>
