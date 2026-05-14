# Recipe examples

Real recipes that ship in [`../examples/`](../examples). Copy any of them into your `recipes/` folder, edit the values, click **reload** in the web UI.

## ☔ Weather alerts

```yaml
name: "Rain warning"
when:
  every: "day at 7am"
if:
  weather:
    location: "Lima, PE"
    condition: "rain_today"
then:
  notify_telegram:
    message: "☔ Lleva casaca hoy."
```

Supported `condition` values: `rain_today`, `rain_now`, `temp_above:N`, `temp_below:N`.

You can also template the message with values produced by the source:

```yaml
notify_telegram:
  message: "☔ Hoy llueve en {{ city }} ({{ precipitation_mm }}mm)."
```

## 🎵 New music releases (coming soon)

```yaml
name: "New from Morat"
when:
  every: "friday at 6pm"
if:
  spotify_new_release:
    artist: "Morat"
then:
  notify_telegram:
    message: "🎵 Nuevo de Morat: {{ release.name }}"
```

## 📰 RSS feed monitor

```yaml
name: "Hacker News headlines"
when:
  every: "1 hour"
if:
  rss:
    url: "https://hnrss.org/frontpage"
then:
  notify_ntfy:
    title: "{{ title }}"
    message: "{{ summary }}"
    click: "{{ link }}"
```

whendo remembers the last entry it saw per recipe, so you only get new items.

## 🐙 GitHub release watcher

```yaml
name: "FastAPI releases"
when:
  every: "6 hours"
if:
  github_releases:
    repo: "fastapi/fastapi"
    include_prereleases: false
then:
  notify_ntfy:
    title: "FastAPI {{ tag }}"
    message: "{{ name }} — {{ url }}"
```

## 📨 Email digest (coming soon — LLM action)

```yaml
name: "Monday AI digest"
when:
  every: "monday at 9am"
if:
  rss:
    url: "https://news.smol.ai/rss.xml"
then:
  llm_summarize_and_notify:
    channel: "email"
    prompt: "Top 3 most interesting AI news, 1 line each."
```

---

## Available source / action keys

See [recipe-reference.md](./recipe-reference.md) for the full list of `when:`, `if:` and `then:` keys.
