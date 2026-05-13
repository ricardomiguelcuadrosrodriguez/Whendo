# Contributing to whendo

Thanks for your interest! whendo is built to be **extended easily**. Most contributions are new sources, new actions, or example recipes — each one is about 100 lines of code.

## Quick start

```bash
git clone https://github.com/ricardomiguelcuadrosrodriguez/whendo
cd whendo
cp .env.example .env
docker compose up --build
```

## Where to contribute

| What | Where | Effort |
|------|-------|--------|
| 🌍 New **source** (data input) | `server/sources/` | ~1-2 hours |
| 📤 New **action** (output) | `server/actions/` | ~1-2 hours |
| 📋 New **example recipe** | `examples/` | ~10 minutes |
| 🐛 Bug fix | anywhere | varies |
| 📚 Docs | `docs/` | varies |

## Adding a new source

A source fetches data from somewhere. Example: `weather`, `rss`, `spotify`.

1. Create `server/sources/your_source.py`
2. Implement the `Source` interface:

```python
from server.sources.base import Source, SourceResult

class YourSource(Source):
    name = "your_source"

    async def check(self, config: dict) -> SourceResult:
        # Fetch data using config (the YAML block from the recipe)
        # Return SourceResult(matched=True/False, data={...})
        ...
```

3. Register it in `server/sources/__init__.py`
4. Add an example recipe in `examples/`
5. Document it in `docs/building-blocks.md`

## Adding a new action

An action does something with the data. Example: `notify_telegram`, `webhook_post`.

Same pattern as sources, but inside `server/actions/`.

## Code style

- Python: `ruff` + `black`. Run `make fmt`.
- TypeScript/Next.js: `biome`. Run `pnpm fmt`.
- Commits: [Conventional Commits](https://www.conventionalcommits.org/) (e.g. `feat(sources): add spotify_new_release`).

## Pull request checklist

- [ ] Tests added for new functionality
- [ ] Example recipe added if it's a new source/action
- [ ] Docs updated
- [ ] `make test` passes
- [ ] One change per PR (easier to review)

## Questions?

Open an issue or ping me on X [@ricardo](https://x.com/) (TODO: real handle). I respond fast.
