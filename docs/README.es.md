<div align="center">

<img src="../assets/logo.png" alt="whendo" width="180" />

# whendo

### *Dile a tu computadora cuándo hacer cosas. En lenguaje natural.*

[![Licencia: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hecho con FastAPI](https://img.shields.io/badge/Hecho%20con-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![Self-hosted](https://img.shields.io/badge/100%25-self--hosted-success.svg)](./installation.md)

**Herramienta de automatización self-hosted para tu vida personal — no para tu negocio.**

[Instalación](./installation.md) • [Referencia de recetas](./recipe-reference.md) • [Ejemplos](./examples.md) • [Arquitectura](./architecture.md) • [🇺🇸 English](../README.md)

> Las guías detalladas (instalación, troubleshooting, arquitectura, referencia) están por ahora solo en inglés. El README está disponible en ambos idiomas.

</div>

---

## ¿Qué es esto?

**whendo** corre en tu máquina y hace cosas por ti según un horario, cuando se cumple una condición, o cuando algo cambia en el mundo. Le describes qué quieres en un pequeño archivo YAML. whendo se encarga del resto.

```yaml
# recipes/aviso-lluvia.yaml
name: "Aviso de lluvia"
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

Guardas el archivo. whendo lo carga. Listo.

## ¿Por qué whendo?

Zapier es para empresas. IFTTT se murió. n8n es exagerado. **whendo es para ti.**

- 🧠 **YAML o lenguaje natural** — parser con LLM próximamente
- 🏠 **Self-hosted** — tus datos, tu servidor, tus reglas
- 🆓 **Gratis para siempre** — código abierto, MIT, sin cuentas
- 🔌 **Trae tu propio LLM** — Claude, OpenAI o Ollama local
- 📱 **Notifica a cualquier lado** — Telegram, ntfy, email, Discord, webhooks
- 🔐 **Cifrado opcional de secretos** — una contraseña maestra protege tus API keys en disco

## Inicio rápido

Necesitas Python 3.10+ y Node.js 20+. Abre dos terminales.

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

Abre **http://localhost:3000**. Configura tus credenciales en **http://localhost:3000/settings**.

Guía completa → [installation.md](./installation.md) (inglés). ¿Atascado? → [troubleshooting.md](./troubleshooting.md) (inglés).

## Roadmap

- [x] Esquema YAML de recetas con validación Pydantic
- [x] Motor de scheduler (APScheduler)
- [x] Web UI (dashboard en Next.js)
- [x] Historial de ejecuciones (SQLite)
- [x] Sources reales — weather, RSS, GitHub releases
- [x] Actions reales — Telegram, ntfy, email
- [x] Página de configuración con cifrado opcional de secretos
- [ ] Parser LLM — lenguaje natural → YAML
- [ ] Crear recetas desde la web UI (pestaña de lenguaje natural)
- [ ] Página de detalle de receta con logs en vivo
- [ ] Más sources — Spotify, YouTube, web scrape, HTTP get
- [ ] Más actions — Discord, WhatsApp, webhook POST, resumen con IA
- [ ] Setup con un solo comando vía Docker Compose

Revisa [los issues](https://github.com/ricardomiguelcuadrosrodriguez/Whendo/issues) para ver qué sigue.

## Contribuir

Los PRs son bienvenidos. Cada nuevo source o action son ~100 líneas. Lee [CONTRIBUTING.md](../CONTRIBUTING.md).

Dale ⭐ al repo si te sirve — es la única métrica que me importa.

## Licencia

MIT © Ricardo Miguel Cuadros Rodriguez

---

<div align="center">
<sub>Hecho con ❤️ en Lima, Perú</sub>
</div>
