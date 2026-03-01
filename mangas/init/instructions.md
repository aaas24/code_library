# Manga Tracker — Full Project Instructions

## Overview

A self-hosted manga tracking application that:
1. Monitors active manga for new chapters
2. Recommends new manga based on preferred themes
3. Tracks reading progress invisibly via redirect links
4. Runs on a Raspberry Pi 4 as a Docker container
5. Is accessible from a phone browser over home WiFi
6. Deploys automatically when code is pushed to GitHub

---

## File Structure

```
manga-tracker/
│
├── import/                          # ONE-TIME USE — run once, then retired
│   ├── parse_mangas_md.py           # Parses messy Mangas.md → clean DB records
│   ├── validate_import.py           # Verifies import results before retiring Mangas.md
│   └── README.md                    # "Run this once only. Do not run again."
│
├── scrapers/                        # Chapter checkers — one file per site
│   ├── base.py                      # BaseScraper abstract class
│   ├── registry.py                  # Auto-discovers scrapers, maps domain → class
│   ├── coffeemanga.py
│   ├── shibamanga.py
│   ├── kaliscan.py
│   └── manhuascan.py
│
├── crawler/                         # Recommendation discovery — one file per site
│   ├── base.py                      # BaseCrawler abstract class
│   ├── registry.py                  # Auto-discovers crawlers
│   ├── coffeemanga.py
│   ├── shibamanga.py
│   ├── kaliscan.py
│   └── manhuascan.py
│
├── db/
│   ├── models.py                    # SQLAlchemy models
│   ├── ops.py                       # All DB read/write operations
│   └── export.py                    # Auto-exports DB → data/mangas.json after writes
│
├── scheduler/
│   ├── jobs.py                      # Chapter check job + recommendation job
│   └── runner.py                    # APScheduler setup, reads config.yaml
│
├── web/
│   ├── app.py                       # Flask app factory, binds 0.0.0.0
│   ├── routes/
│   │   ├── dashboard.py             # GET /
│   │   ├── updates.py               # GET /updates
│   │   ├── active.py                # GET /active
│   │   ├── recommendations.py       # GET /recommendations
│   │   ├── read.py                  # GET /read/<manga_id>/<chapter> → log + redirect
│   │   └── settings.py              # GET/POST /settings
│   └── templates/                   # Mobile-friendly Jinja2 HTML templates
│       ├── base.html
│       ├── dashboard.html
│       ├── updates.html
│       ├── active.html
│       ├── recommendations.html
│       └── settings.html
│
├── utils/
│   ├── secrets.py                   # Central secrets interface: get_secret("key")
│   ├── setup_secrets.py             # ONE-TIME: interactively creates all 1Password entries
│   ├── onboard_site.py              # Helper: auto-detects CSS selectors for a new site
│   └── config_loader.py             # Loads + validates config.yaml
│
├── data/
│   ├── mangas.db                    # SQLite — primary source of truth (gitignored)
│   ├── mangas.json                  # Auto-exported human-readable backup (gitignored)
│   └── import/
│       └── Mangas.md                # Drop original file here before running import
│
├── tests/
│   ├── fixtures/                    # Saved HTML files for mocked scraper tests
│   │   ├── coffeemanga_chapter.html
│   │   ├── shibamanga_chapter.html
│   │   ├── kaliscan_chapter.html
│   │   └── manhuascan_chapter.html
│   ├── test_import_parser.py
│   ├── test_scrapers.py
│   ├── test_crawler.py
│   ├── test_db.py
│   ├── test_scheduler.py
│   ├── test_web.py
│   └── test_secrets.py
│
├── k8s/                             # Kubernetes manifests (future migration)
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── secret.yaml                  # References external secrets — never stores values
│
├── .github/
│   └── workflows/
│       ├── test.yml                 # Runs pytest on every push and PR
│       └── deploy.yml               # On push to main: build → push → deploy to Pi
│
├── Dockerfile                       # ARM64-compatible for Pi 4
├── docker-compose.yml               # For running on Pi
├── docker-compose.dev.yml           # Overrides for local development on Mac
├── config.yaml                      # User-editable: schedule, themes, site toggles
├── config_schema.py                 # Validates config.yaml on startup
├── secrets.config.yaml              # 1Password paths + field names (no values, safe to commit)
├── requirements.txt
├── .gitignore                       # Excludes data/, mangas.db, mangas.json
└── README.md
```

---

## Secrets Management (1Password)

### Architecture

All secrets are stored in a single 1Password item in the **Private** vault. The app never reads from `.env` files or hardcoded values — everything goes through `utils/secrets.py`.

The location of every secret is defined in **`secrets.config.yaml`** (committed to the repo). This file contains no secret values — only 1Password paths, field names, descriptions, and whether each field is required. It is the single source of truth for what secrets the app needs and where to find them.

**1Password item:** `Manga - Homelab Server` (Private vault)
**SSH key item:** `SSH Key - Homelab` (Private vault, separate SSH Key item type, linked as a related item)

**Authentication method:** 1Password Service Account
- The service account token is the only secret that lives outside 1Password
- On the Pi: stored as a Docker environment variable set at container start
- In GitHub Actions: stored as a GitHub Actions secret (`OP_SERVICE_ACCOUNT_TOKEN`)
- On your computer: stored in shell profile (`~/.zshrc` or `~/.bashrc`)

### secrets.config.yaml

This file lives at the project root and is committed to GitHub. It defines all secret locations and metadata:

```yaml
onepassword:
  vault: Private
  item: "Manga - Homelab Server"
  ssh_item: "SSH Key - Homelab"

  fields:
    pi_host:                            # Already exists in 1Password
      field: "pi_host"
      description: "Raspberry Pi fixed IP address"
      required: true

    pi_user:
      field: "pi_user"
      description: "Pi SSH username"
      required: true

    flask_secret_key:
      field: "flask_secret_key"
      description: "Flask session signing key"
      required: true

    op_service_account_token:
      field: "op_service_account_token"
      description: "1Password Service Account token"
      required: true

    github_deploy_key:
      field: "github_deploy_key"
      description: "GitHub Actions deploy key"
      required: true

    llm_api_key:
      field: "llm_api_key"
      description: "LLM API key for site onboarding (optional)"
      required: false

  ssh:
    item: "SSH Key - Homelab"
    private_key_field: "private key"
    public_key_field: "public key"
```

When adding a new secret to the app, add it here first — then `setup_secrets.py` and `secrets.py` automatically pick it up. No other files need to change.

### utils/secrets.py Interface

Reads `secrets.config.yaml` to know where to look, then calls the `op` CLI to fetch the value:

```python
# All other modules use this — never call 1Password directly
from utils.secrets import get_secret

host = get_secret("pi_host")
flask_key = get_secret("flask_secret_key")
```

Internally resolves to:
```bash
op read "op://Private/Manga - Homelab Server/pi_host"
op read "op://Private/Manga - Homelab Server/flask_secret_key"
```

SSH key is fetched via:
```bash
op item get "SSH Key - Homelab" --fields "private key" --vault Private
```

### utils/setup_secrets.py — One-Time Setup

Run this once on your computer when first setting up the project. It reads `secrets.config.yaml` and:
1. Checks that `op` CLI is installed and you are signed in
2. Verifies the `Manga - Homelab Server` item exists in your Private vault
3. Checks which fields already exist (e.g. `pi_host` is already there)
4. Prompts you for any missing required fields and creates them on the item
5. Checks that `SSH Key - Homelab` exists as a linked related item
6. Prints instructions for adding the service account token to the Pi and GitHub

```bash
python utils/setup_secrets.py
```

---

## One-Time Import Workflow

### Purpose
Parse the existing messy `Mangas.md` into clean database records. This runs exactly once. After it succeeds, `Mangas.md` is retired and SQLite becomes the source of truth.

`Mangas.md` is available in /tmp folder

### Steps

```bash
# 1. Place Mangas.md in the import location
cp tmp/Mangas.md

# 2. Run the parser
python import/parse_mangas_md.py

# 3. Review what was parsed
python import/validate_import.py

# 4. Confirm — locks the import, marks Mangas.md as retired
python import/validate_import.py --confirm
```

### Parser Rules

| Pattern | Example | Parsed As |
|---------|---------|-----------|
| Bare URL | `https://site.com/manga/title` | read, no episode data |
| URL + one number | `https://... 130` | read, published=130 |
| URL + two numbers | `https://... 99 100` | published=99, read=100 |
| Markdown link + number | `[text](url) 130` | read, published=130 |
| Bracketed numbers | `[257],[255]` | published=257, read=255 |
| Inline notes | `not loading`, `tv show` | stripped, saved as raw_note |
| Duplicate URLs | same URL twice | merged, entry with more data wins |

### Section Detection

| Heading in file | Status assigned |
|-----------------|-----------------|
| None (top of file) | `active` |
| `Didn't love` | `pass` |
| `Finished` | `finished` |
| `Pass` | `pass` |

---

## Config File (config.yaml)

```yaml
schedules:
  chapter_check: "0 2 * * *"        # daily at 2am
  recommendations: "0 3 * * 1"      # weekly Monday at 3am

sites:
  coffeemanga:
    scraper: true                    # used for chapter checking
    crawler: true                    # used for recommendations
  shibamanga:
    scraper: true
    crawler: true
  kaliscan:
    scraper: true
    crawler: true
  manhuascan:
    scraper: true
    crawler: true

themes:
  - villainess
  - reincarnation
  - historical romance
  - royalty
  - emperor
  - empress
  - noble
  - medical
  - healer
  - doctor
  - strong female lead

recommendations:
  min_chapters: 100

web:
  port: 5000
  host: "0.0.0.0"
```

Each site has independent `scraper` and `crawler` toggles — you can enable a site for chapter checking without using it for recommendations, or vice versa.

---

## Adding a New Site (Site Onboarding Workflow)

This is a separate, standalone workflow. Run it whenever you want to add a new manga website. It is completely independent from the regular chapter checking and recommendation crawling.

### Step 1 — Run the onboarding helper

```bash
python utils/onboard_site.py --url "https://newsite.com/manga/some-title"
```

The script:
1. Fetches the page HTML
2. Uses heuristics and optionally an LLM API call to identify candidate CSS selectors for chapter numbers
3. Presents its best guess: `"Found: Chapter 157 using selector .chapter-list li:first-child — correct? (y/n)"`
4. If confirmed, writes the site entry to `config.yaml` automatically
5. If not found, prompts you to inspect the HTML manually, accepts your selector, and writes it to config

### Step 2 — Test the selector

```bash
python utils/onboard_site.py --test "https://newsite.com/manga/some-title"
```

Fetches the page and prints the extracted chapter number using the saved config entry. Use this to verify the selector still works after a site redesign.

### Step 3 — Python escape hatch (complex sites only)

If the site uses JavaScript rendering, requires special headers, or has logic too complex for a CSS selector, create a Python scraper file:

```python
# scrapers/newsite.py
from scrapers.base import BaseScraper

class NewSiteScraper(BaseScraper):
    domain = "newsite.com"

    def get_latest_chapter(self, soup) -> int | None:
        element = soup.select_one(".episode-number")
        return int(element.text.strip()) if element else None
```

Drop it in `scrapers/` — the registry auto-discovers it on next startup. A Python scraper always takes priority over a config-defined selector for the same domain.

---

## Data Model (SQLite)

### `manga` table

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| url | TEXT UNIQUE | canonical URL |
| title | TEXT | parsed from page or URL slug |
| site | TEXT | domain name |
| last_episode_published | INTEGER | updated by crawler |
| last_episode_read | INTEGER | updated via /read/ redirect |
| status | TEXT | `active`, `didnt_love`, `finished`, `pass` |
| has_update | BOOLEAN | true when published > read |
| last_checked | DATETIME | |
| raw_note | TEXT | noise from import, informational only |

### `recommendation` table

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER PK | |
| url | TEXT UNIQUE | |
| title | TEXT | |
| site | TEXT | |
| chapter_count | INTEGER | |
| matched_themes | TEXT | JSON array |
| score | INTEGER | number of matched themes |
| seen | BOOLEAN | dismissed by user in UI |
| discovered_at | DATETIME | |

### Chapter Read Tracking

Every "Read" link in the web UI routes through:

```
GET /read/<manga_id>/<chapter_number>
```

This route:
1. Updates `last_episode_read` in the DB
2. Recalculates `has_update`
3. Triggers `mangas.json` export
4. Redirects browser to the actual manga URL on the external site

The user experiences this as a normal link — tracking is invisible.

---

## Web UI Pages

| Page | Path | Description |
|------|------|-------------|
| Dashboard | `/` | Summary counts: updates available, new recommendations |
| Updates | `/updates` | Active manga with new chapters since last check |
| All Active | `/active` | Full reading list with progress and read links |
| Recommendations | `/recommendations` | New suggested manga, unseen only |
| Settings | `/settings` | Edit schedule, toggle sites, trigger manual crawl |

### UI Requirements
- Mobile-first responsive design (readable on a phone)
- Each active manga shows: title, last chapter read, latest published, direct read link
- Recommendations show: title, site, chapter count, matched themes, Dismiss button
- Settings shows current cron schedule with a "Run Now" button for immediate crawl

---

## Docker Setup

### Dockerfile

- Base image: `python:3.11-slim` (ARM64 compatible for Pi 4)
- Confirm Pi architecture via SSH before building: `uname -m` should return `aarch64`
- SQLite data directory mounted as a Docker volume so data persists across restarts

### docker-compose.yml (Pi production)

```yaml
version: "3.9"
services:
  manga-tracker:
    image: ghcr.io/<your-github-username>/manga-tracker:latest
    restart: always
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - OP_SERVICE_ACCOUNT_TOKEN=${OP_SERVICE_ACCOUNT_TOKEN}
```

The service account token is the only environment variable — all other secrets are fetched from 1Password at runtime via `utils/secrets.py`.

### docker-compose.dev.yml (local Mac development)

Overrides for running on your Mac without a Pi. Mounts local source code for hot reload during development.

---

## CI/CD Pipeline (GitHub Actions)

### test.yml — triggers on every push and PR

1. Checkout code
2. Install Python dependencies
3. Run `pytest tests/` — must fully pass before deploy is allowed

### deploy.yml — triggers on push to `main` only (after tests pass)

1. Fetch Pi credentials from 1Password using service account token
2. Build Docker image for ARM64 (`linux/arm64`)
3. Push image to GitHub Container Registry (`ghcr.io`)
4. SSH into Pi using fetched credentials
5. Pull new image on Pi
6. Run `docker-compose up -d` to restart container with new image
7. Verify container is healthy

```
Push to main branch
        ↓
pytest passes
        ↓
Build ARM64 Docker image
        ↓
Push to ghcr.io
        ↓
SSH into Pi (credentials from 1Password)
        ↓
docker-compose pull && docker-compose up -d
        ↓
App updated — no manual steps required
```

---

## Raspberry Pi Setup Checklist

Run these steps once when setting up the Pi for the first time.

```bash
# 1. Confirm Pi model and architecture
uname -m                          # expect: aarch64
cat /proc/device-tree/model       # expect: Raspberry Pi 4 Model B

# 2. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker

# 3. Install Docker Compose plugin
sudo apt-get install -y docker-compose-plugin

# 4. Install 1Password CLI
# Full instructions: https://developer.1password.com/docs/cli/get-started/

# 5. Set service account token (persists across reboots)
echo 'export OP_SERVICE_ACCOUNT_TOKEN="your-token-here"' >> ~/.bashrc
source ~/.bashrc

# 6. Clone the repo
git clone https://github.com/<your-username>/manga-tracker.git
cd manga-tracker

# 7. Create data directory (persists outside container)
mkdir -p data

# 8. Start the container
docker-compose up -d

# 9. Verify
docker-compose ps
curl http://localhost:5000

# 10. Note the Pi's fixed IP for phone access
hostname -I
# Access from phone: http://<pi-ip>:5000
```

---

## Kubernetes Manifests (Future Migration)

The `k8s/` folder contains ready-to-use manifests. No code changes are needed when migrating — only the deployment target changes.

| File | Purpose |
|------|---------|
| `k8s/deployment.yaml` | Pod spec, image reference, resource limits |
| `k8s/service.yaml` | ClusterIP or LoadBalancer on port 5000 |
| `k8s/configmap.yaml` | Non-secret config (mirrors config.yaml) |
| `k8s/secret.yaml` | References external secret store — never stores values directly |

---

## TDD Test Plan

All tests in `tests/`, run with `pytest`. Tests are written **before** implementation.

### test_import_parser.py

| Test | Description |
|------|-------------|
| `test_parse_bare_url` | Bare URL → active, no episode data |
| `test_parse_url_one_number` | URL + one number → published set, read is None |
| `test_parse_url_two_numbers` | URL + two numbers → both fields populated |
| `test_parse_markdown_link` | `[text](url) 130` → URL extracted, published=130 |
| `test_parse_bracketed_numbers` | `[257],[255]` → published=257, read=255 |
| `test_section_active` | Entries before any heading → status=active |
| `test_section_didnt_love` | Entries under `Didn't love` → status=didnt_love |
| `test_section_finished` | Entries under `Finished` → status=finished |
| `test_section_pass` | Entries under `Pass` → status=pass |
| `test_deduplication` | Duplicate URLs merged, entry with more data wins |
| `test_noise_stripped` | Notes like `not loading` do not break parsing |
| `test_malformed_lines_skipped` | Non-URL lines skipped without error |

### test_scrapers.py (mocked HTML — no real network calls)

| Test | Description |
|------|-------------|
| `test_coffeemanga_chapter_extraction` | Fixture HTML → correct chapter number |
| `test_shibamanga_chapter_extraction` | Same for shibamanga |
| `test_kaliscan_chapter_extraction` | Same for kaliscan |
| `test_manhuascan_chapter_extraction` | Same for manhuascan |
| `test_scraper_returns_none_on_404` | HTTP error → returns None gracefully |
| `test_scraper_returns_none_missing_element` | Element not found → returns None |
| `test_registry_autodiscovers_scrapers` | New file in scrapers/ is auto-registered |
| `test_python_scraper_overrides_config` | Python file takes priority over config selector |
| `test_config_selector_used_as_fallback` | Falls back to config selector when no Python file |

### test_crawler.py (mocked HTML)

| Test | Description |
|------|-------------|
| `test_filters_by_min_chapters` | Titles with fewer than 100 chapters excluded |
| `test_filters_by_theme` | Only titles matching at least one theme pass |
| `test_excludes_known_urls` | URLs already in manga table excluded |
| `test_excludes_didnt_love` | Exact titles from didnt_love excluded |
| `test_excludes_finished` | Finished titles excluded |
| `test_excludes_pass` | Pass titles excluded |
| `test_scores_by_theme_count` | More matching themes = higher score |

### test_db.py

| Test | Description |
|------|-------------|
| `test_upsert_manga` | Same URL inserted twice → updates not duplicates |
| `test_has_update_true` | published > read → has_update=True |
| `test_has_update_false` | published <= read → has_update=False |
| `test_recommendation_not_in_history` | URL in manga table cannot appear in recommendations |
| `test_seen_flag_persists` | Marking recommendation seen persists correctly |
| `test_json_export_on_write` | DB write triggers mangas.json export |
| `test_read_updates_last_read` | /read/ route correctly updates last_episode_read |

### test_scheduler.py

| Test | Description |
|------|-------------|
| `test_config_cron_loaded` | Cron expression read correctly from config.yaml |
| `test_manual_trigger` | Trigger function invokes scraper directly |
| `test_schedule_reload` | Changing config cron + reloading updates the job |
| `test_scraper_disabled_site_skipped` | scraper=false site is not chapter-checked |
| `test_crawler_disabled_site_skipped` | crawler=false site skipped in recommendations |

### test_web.py

| Test | Description |
|------|-------------|
| `test_dashboard_200` | GET / → 200 |
| `test_updates_shows_only_updated` | /updates lists only has_update=True manga |
| `test_active_shows_all_active` | /active shows all status=active manga |
| `test_recommendations_shows_unseen` | /recommendations shows seen=False only |
| `test_dismiss_recommendation` | POST dismiss → seen=True in DB |
| `test_read_redirect` | GET /read/<id>/<chapter> → updates DB + redirects to site |
| `test_settings_200` | GET /settings → 200 |
| `test_run_now_triggers_crawl` | POST /settings/run-now → triggers immediate crawl |

### test_secrets.py

| Test | Description |
|------|-------------|
| `test_get_secret_calls_op_cli` | get_secret() calls `op read` with correct vault path |
| `test_get_secret_missing_key` | Missing key raises clear descriptive error |
| `test_setup_creates_vault` | setup_secrets.py creates vault if it does not exist |
| `test_setup_creates_all_entries` | All required secrets are created in 1Password |

### test_onboarding.py

| Test | Description |
|------|-------------|
| `test_selector_detection_finds_chapter` | Given fixture HTML, correct selector identified |
| `test_writes_config_on_confirm` | Confirmed selector written to config.yaml |
| `test_manual_selector_fallback` | Auto-detect failure → accepts manual selector |
| `test_test_mode_validates_selector` | --test flag fetches page and prints extracted chapter |

---

## Implementation Order (TDD)

Follow this sequence — each layer depends on the one before it:

1. Write all tests first — all will fail initially
2. `import/` — get import parser tests passing
3. `db/` — get DB tests passing
4. `utils/secrets.py` — get secrets tests passing
5. `scrapers/` and `crawler/` with fixture HTML — get scraper and crawler tests passing
6. `utils/onboard_site.py` — get onboarding tests passing
7. `scheduler/` — get scheduler tests passing
8. `web/` Flask routes and templates — get web tests passing
9. Docker build + local smoke test on Mac
10. Pi setup checklist + confirm model/architecture
11. `utils/setup_secrets.py` — create all 1Password entries
12. GitHub Actions CI/CD — push to main → auto-deploy to Pi
13. End-to-end: push code → tests pass → Pi updates → view UI on phone

---

## Acceptance Criteria

- [ ] `Mangas.md` fully parsed with zero unhandled exceptions on the real file
- [ ] All 4 sites return correct chapter numbers for known active manga URLs
- [ ] New chapters detected and shown on `/updates`
- [ ] Reading via the app updates `last_episode_read` invisibly via redirect
- [ ] At least 5 recommendations returned per crawl from the 4 approved sites
- [ ] Web UI reachable from phone browser on same WiFi via Pi IP
- [ ] Adding a new site via `onboard_site.py` requires no Python for standard sites
- [ ] All secrets fetched from 1Password — no `.env` files, no hardcoded values
- [ ] Push to `main` automatically deploys to Pi via GitHub Actions
- [ ] `k8s/` manifests are valid and ready for future migration
- [ ] All pytest tests pass: `pytest tests/`
- [ ] No test makes a real network request
