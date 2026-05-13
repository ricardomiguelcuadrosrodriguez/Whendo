<div align="center">

# ⏰ whendo

### *Dile a tu computadora cuándo hacer cosas. En español llano.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hecho con FastAPI](https://img.shields.io/badge/Hecho%20con-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

**Herramienta de automatización self-hosted para tu vida personal — no para tu negocio.**

[Empezar](#empezar-en-60-segundos) • [Ejemplos](#ejemplos) • [Cómo funciona](#cómo-funciona) • [English](../README.md)

</div>

---

## 🤔 ¿Qué es esto?

**whendo** corre en tu máquina y hace cosas por ti según un horario, cuando se cumple una condición, o cuando algo cambia en el mundo. Le describes qué querés en un archivo YAML chiquito. whendo se encarga del resto.

```yaml
# recipes/aviso-lluvia.yaml
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

Guardás el archivo. whendo lo levanta. Listo.

¿No te gusta YAML? Describílo en lenguaje natural y el parser lo escribe por vos:

```bash
$ whendo new "avísame por telegram cuando llueva en lima"
✓ Recipe creada: recipes/aviso-lluvia.yaml
```

## 🎯 ¿Por qué whendo?

Zapier es para empresas. IFTTT se murió. n8n es exagerado. **whendo es para vos.**

- 🧠 **Español llano o YAML** — vos elegís, ambos funcionan
- 🏠 **Self-hosted** — tu data, tu servidor, tus reglas
- 🆓 **Gratis para siempre** — código abierto, MIT
- 🐳 **Un solo comando** — `docker compose up`
- 🔌 **Trae tu propio LLM** — Claude (default), OpenAI, o todo local con Ollama
- 📱 **Notifica donde sea** — Telegram, WhatsApp, email, ntfy, Discord
- 🌎 **Pensado para la vida real** — clima, RSS, YouTube, Spotify, precios, scraping

## ⚡ Empezar en 60 segundos

```bash
git clone https://github.com/ricardomiguelcuadrosrodriguez/whendo
cd whendo
cp .env.example .env   # agregá tu API key de Claude + token de bot de Telegram
docker compose up
```

Abrí `http://localhost:3000` y listo. Tirá un archivo `.yaml` en `recipes/` y whendo lo correrá.

> 💡 **¿Sin API key?** whendo funciona 100% offline con [Ollama](https://ollama.com). Poné `LLM_PROVIDER=ollama` en `.env`.

## 📚 Ejemplos

Recipes reales que vienen en [`examples/`](../examples). Copiá, ajustá, ejecutá.

Ver el [README en inglés](../README.md#examples) para el catálogo completo.

## 🤝 Contribuir

PRs bienvenidos, especialmente para nuevos sources y actions — cada uno es ~100 líneas. Ver [CONTRIBUTING.md](../CONTRIBUTING.md).

Dale ⭐ al repo si te sirve. Es la única métrica que me importa.

## 📜 Licencia

MIT © Ricardo Cuadros

---

<div align="center">
<sub>Hecho con ❤️ en Lima, Perú</sub>
</div>
