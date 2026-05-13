<div align="center">

<img src="../assets/logo.png" alt="whendo" width="180" />

# whendo

### *Dile a tu computadora cuándo hacer cosas. En español llano.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hecho con FastAPI](https://img.shields.io/badge/Hecho%20con-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Self-hosted](https://img.shields.io/badge/100%25-self--hosted-success.svg)](#-empezar)

**Herramienta de automatización self-hosted para tu vida personal — no para tu negocio.**

[Empezar](#-empezar) • [Ejemplos](#-ejemplos) • [Cómo funciona](#-cómo-funciona) • [🇺🇸 English](../README.md)

</div>

---

## 🤔 ¿Qué es esto?

**whendo** corre en tu máquina y hace cosas por ti según un horario, cuando se cumple una condición, o cuando algo cambia en el mundo. Le describes qué quieres en un pequeño archivo YAML. whendo se encarga del resto.

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

## 🎯 ¿Por qué whendo?

Zapier es para empresas. IFTTT se murió. n8n es exagerado. **whendo es para ti.**

- 🧠 **YAML o lenguaje natural** (parser LLM próximamente)
- 🏠 **Self-hosted** — tu data, tu servidor, tus reglas
- 🆓 **Gratis para siempre** — código abierto, MIT, sin cuentas
- 🐳 **Un solo comando** — `docker compose up`
- 🔌 **Trae tu propio LLM** — Claude, OpenAI, o Ollama local
- 📱 **Notifica donde sea** — Telegram, ntfy, email, Discord, webhooks

---

## ⚡ Empezar

Necesitas **dos terminales** abiertas. Backend y frontend corren como servicios separados.

### Requisitos previos

- **Python 3.10+** (3.12 recomendado)
- **Node.js 20+**
- **Git**

Verifica qué tienes:
```bash
python3 --version
node --version
git --version
```

### Paso 1 — Clonar el repo

```bash
git clone https://github.com/ricardomiguelcuadrosrodriguez/Whendo.git
cd Whendo
```

### Paso 2 — Configurar el backend (Terminal 1)

```bash
# Crear un entorno virtual de Python (para no contaminar el sistema)
python3 -m venv .venv
source .venv/bin/activate
# Deberías ver (.venv) en tu prompt ahora

# Instalar las dependencias del backend
pip install -r server/requirements.txt

# Crear tu archivo de configuración
cp .env.example .env

# Crear las carpetas que el servidor necesita
mkdir -p recipes data

# Copiar una recipe de ejemplo para que tenga algo que cargar
cp examples/01-rain-alert.yaml recipes/

# ¡Arrancá el servidor!
make dev
```

Si todo funcionó, vas a ver:
```
INFO whendo — whendo starting (tz=America/Lima)
INFO server.scheduler.loader — Loaded recipe 'Rain warning - Lima'
INFO server.scheduler.engine — Scheduled 'Rain warning - Lima': day at 7am
INFO Application startup complete.
INFO Uvicorn running on http://0.0.0.0:8000
```

✅ El backend está corriendo en **http://localhost:8000**.

Verificá con `curl`:
```bash
curl http://localhost:8000/health
# → {"status":"ok"}
```

### Paso 3 — Configurar el frontend (Terminal 2)

Abrí una **segunda terminal** (¡no cierres la primera!):

```bash
cd ~/ruta/a/Whendo

# Instalar las dependencias del frontend (tarda 2-3 min la primera vez)
make install-web

# Arrancar el servidor de desarrollo de Next.js
make dev-web
```

Vas a ver:
```
▲ Next.js 15.1.0
- Local:  http://localhost:3000
✓ Ready in 2.1s
```

✅ Abrí **http://localhost:3000** en tu navegador. 🎉

### Paso 4 — Probálo

En el navegador:
1. Vas a ver la recipe **Rain warning - Lima** como una card
2. Click en **`run now`** para dispararla manualmente
3. Click en el tab **`runs`** para ver el historial de ejecuciones
4. Agrega un nuevo archivo YAML en `recipes/` y haz clic en **`reload`** para que lo cargue

### Para detener todo

En cada terminal: **Ctrl + C**

### Para reiniciar después

```bash
# Terminal 1
cd ~/ruta/a/Whendo
source .venv/bin/activate
make dev

# Terminal 2
cd ~/ruta/a/Whendo
make dev-web
```

---

## 🐛 Solución de problemas

<details>
<summary><b>"ModuleNotFoundError: No module named 'server'"</b></summary>

Estás corriendo `uvicorn` desde adentro de la carpeta `server/`. Corrélo desde la raíz del proyecto:
```bash
cd ~/ruta/a/Whendo  # NO cd server/
make dev
```
</details>

<details>
<summary><b>"externally-managed-environment" al hacer pip install</b></summary>

Te olvidaste de activar el venv. Hacé:
```bash
source .venv/bin/activate
# Ahora deberías ver (.venv) en tu prompt
which python  # debería apuntar a .venv/bin/python
```
</details>

<details>
<summary><b>La web muestra "Could not reach backend"</b></summary>

El frontend no puede comunicarse con el backend. Asegúrate de que la Terminal 1 sigue corriendo y verifica:
```bash
curl http://localhost:8000/health
```
Si eso falla, el backend se cayó — revisa los logs en Terminal 1.
</details>

<details>
<summary><b>Puerto 8000 o 3000 ya en uso</b></summary>

Algo más está usando ese puerto. Matálo:
```bash
kill -9 $(lsof -t -i:8000)
kill -9 $(lsof -t -i:3000)
```
</details>

---

## 📚 Ejemplos

Recipes reales que vienen en [`examples/`](../examples). Ver el [README en inglés](../README.md#-examples) para el catálogo completo.

---

## 🤝 Contribuir

PRs bienvenidos. Cada source/action nuevo es ~100 líneas. Ver [CONTRIBUTING.md](../CONTRIBUTING.md).

Dale ⭐ al repo si te sirve — es la única métrica que me importa.

---

## 📜 Licencia

MIT © Ricardo Miguel Cuadros Rodriguez

---

<div align="center">
<sub>Hecho con ❤️ en Lima, Perú</sub>
</div>
