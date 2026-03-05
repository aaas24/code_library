# Manga Tracker

A self-hosted web app to track your manga reading list, detect new chapters, and discover recommendations. Deployed on a home Kubernetes (K3s) cluster via ArgoCD.

---

## Features

### Reading list
- **All Active** — full list of manga you are currently reading
- **Search** — filter by title or site as you type
- **Pre-filters** — one-click pills to show only:
  - Favorites (starred)
  - New chapters (published > last read)
  - Not started (never recorded a read chapter)
- **Default sort** — favorites first, then most recently read, then most pending chapters
- **Track progress** — edit the last chapter you read inline; saved with a single click
- **Read button** — always resumes from your last read chapter, not the latest published
- **Favorites** — star any manga to pin it to the top of the list
- **Pending badge** — shows how many unread chapters are waiting
- **Archive** — retire a manga as Finished or Skip so it no longer appears in the active list

### Bug reporting
- Flag any manga with a data problem directly from **All Active** using the "Report bug…" dropdown
- Bug types: **URL broken**, **Latest chapter not displayed**, **Wrong title**, **Other**
- A `⚠` badge appears next to the title of flagged manga
- The **Bugs** tab lists all flagged manga — change the bug type or clear the flag per row
- Cleared manga disappear from the Bugs tab immediately

### Updates
- Dedicated view for manga that have new chapters since your last read

### Recommendations
- Crawler discovers new titles based on themes in your reading list
- Each recommendation shows title, site, chapter count, score, and matched themes
- Actions: **Add to reading list** or **Ignore**

### Automation (APScheduler)
- **Daily at 2 am** — chapter check across all active manga (scrapers per site)
- **Weekly on Monday at 3 am** — recommendation discovery run
- Both jobs can also be triggered manually from the Settings page

---

## Stack

| Layer | Technology |
|---|---|
| Web | Flask (Python 3.11) |
| Database | SQLite via SQLAlchemy |
| Scheduling | APScheduler |
| Scraping | Per-domain crawlers (`crawler/`) |
| Container | Docker (ARM64) |
| Hosting | K3s (Raspberry Pi) via ArgoCD GitOps |
| Image registry | GitHub Container Registry (`ghcr.io`) |
| Persistence | Longhorn PVC (5 Gi, retain policy) |
| Secrets | Sealed Secrets (`kubeseal`) |
| Ingress | Traefik IngressRoute, internal TLS |

---

## Project structure

```
mangas/
  crawler/        # per-site chapter scrapers
  db/             # SQLAlchemy models, ops, JSON export
  import/         # one-time import scripts (Mangas.md → SQLite)
  scheduler/      # APScheduler job definitions
  tests/          # pytest test suite
  web/
    routes/       # Flask blueprints (active, updates, recommendations, settings, dashboard)
    templates/    # Jinja2 HTML templates
    app.py        # Flask app factory + scheduler init
  Dockerfile
  requirements.txt
```

---

## Data persistence

The SQLite database lives at `/app/data/mangas.db` inside the pod, mounted from a Longhorn PVC. A JSON snapshot (`/app/data/mangas.json`) is written after every database write.

```
PVC: manga-tracker-data (longhorn-retain, 5 Gi, ReadWriteOnce)
  /app/data/mangas.db    — SQLite (single source of truth)
  /app/data/mangas.json  — JSON export (written on every change)
```

---

## CI/CD

GitHub Actions (`.github/workflows/manga-deploy.yml`) runs on every push to `main`:

1. **Test** — runs the full pytest suite via the reusable `manga-test.yml` workflow
2. **Build & push** — builds an ARM64 Docker image and pushes it to `ghcr.io/aaas24/manga-tracker:latest`

Deployment is **manual**: after a push, run `kubectl rollout restart deployment/manga-tracker -n mangas` on the cluster to pull the new image.

---

## Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (SQLite written to data/mangas.db)
PYTHONPATH=. python web/app.py

# Run tests
pytest tests/
```

---

## One-time import

See [import/README.md](import/README.md) for instructions on importing a reading list from `Mangas.md`.
