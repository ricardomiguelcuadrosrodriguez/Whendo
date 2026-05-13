# whendo-web

The frontend for whendo.

## Stack
- Next.js 15 (App Router, React 19)
- TypeScript (strict)
- Tailwind CSS 3
- lucide-react icons
- Geist Sans + JetBrains Mono via `next/font`

## Local dev

The web app talks to the backend at `http://localhost:8000` by default.
Make sure the backend is running first:

```bash
# In another terminal, from the repo root:
make dev
```

Then start the web:

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000

## How API calls work

`next.config.js` rewrites every `/api/*` request to the backend. So in code
we just call `/api/recipes` and it gets proxied to `http://localhost:8000/api/recipes`.

To point at a different backend host, set `WHENDO_API_URL`:

```bash
WHENDO_API_URL=http://my-server:8000 npm run dev
```

## Design tokens

Defined in `tailwind.config.ts`:

| Token            | Hex       | Use                           |
|------------------|-----------|-------------------------------|
| `bg`             | `#0A0A0A` | Page background               |
| `bg.elevated`    | `#0F0F0F` | Header, nav, dropdowns        |
| `bg.card`        | `#121212` | Cards and rows                |
| `ink`            | `#E5E5E5` | Primary text                  |
| `ink.dim`        | `#8A8A8A` | Secondary text                |
| `ink.muted`      | `#5A5A5A` | Tertiary text, hints          |
| `lime`           | `#D4F574` | Primary accent (success, CTAs)|
| `flame`          | `#FF8C42` | Warm accent (actions)         |
| `border`         | `#1F1F1F` | Default border                |
| `border.strong`  | `#2A2A2A` | Hover/focus border            |
| `success`        | `#7ED957` | Success states                |
| `danger`         | `#FF5C5C` | Errors                        |
| `warning`        | `#FFB627` | Warnings                      |

Two fonts: JetBrains Mono (default for code/labels) and Geist Sans (for prose).
