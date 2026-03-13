![Build Status](https://img.shields.io/github/actions/workflow/status/namanbansalcodes/altassian_backend/python.yml?branch=master) ![License](https://img.shields.io/badge/license-MIT-green) ![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)

# Altassian Backend

Altassian is an open-source Confluence alternative — a wiki platform for teams to create, organize, and collaborate on documentation.

## Tech Stack

- **Backend:** Python 3.11, Django 5.2, Django REST Framework
- **Auth:** JWT via djangorestframework-simplejwt
- **Database:** SQLite (dev), PostgreSQL (prod/Docker)
- **Frontend:** SvelteKit (monorepo at `./frontend-svelte`)

## Features

- Markdown-based page editing with HTML rendering
- Hierarchical pages with parent/child relationships
- Spaces (wiki namespaces) for organizing content
- Page versioning with full history
- Comments with nested replies
- File attachments
- Full-text search across pages
- Activity feed
- JWT authentication with token refresh

## Project Structure

```
altassian_core/   # Django project settings, root URL config
user_accounts/    # CustomUser model (extends AbstractUser)
spaces/           # Space model (wiki namespaces)
pages/            # Page, PageVersion, Comment, Attachment models
frontend-svelte/  # SvelteKit app (SSR dev server)
```

## Local Development

### Prerequisites

- Python 3.11+
- pip
- Node 20+

### Setup

```bash
# Clone and enter the project
git clone <repo-url>
cd altassian_backend

# Backend
python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000

# Frontend (in another terminal)
cd frontend-svelte
npm i
npm run dev -- --host 0.0.0.0 --port 5173
```

- API: `http://localhost:8000/api/`
- Frontend: `http://localhost:5173/`

### Seed Data

`python manage.py seed` creates:

| Type   | Items |
|--------|-------|
| Users  | `admin` / `adminpass123`, `alice` / `alicepass123`, `bob` / `bobpass123`, `carol` / `carolpass123` |
| Spaces | Engineering (`ENG`), Product (`PROD`), Onboarding (`ONB`) |
| Pages  | Architecture Overview, API Reference, Development Setup, Q1 Roadmap, Welcome to Altassian |

## Docker (Reverse Proxy + Services)

### Prerequisites

- Docker and Docker Compose

### Start

```bash
docker compose up --build -d
```

This launches four services:

| Service           | Description                  | Port |
|-------------------|------------------------------|------|
| `db`              | PostgreSQL 16                | —    |
| `backend`         | Django + Gunicorn            | 8000 (internal) |
| `frontend-svelte` | SvelteKit dev server (SSR)   | 5173 (internal) |
| `nginx`           | Reverse proxy                | **8080 -> 80** |

Open: http://localhost:8080

### Routing

- `/api/*` and `/admin/*` → Django backend
- `/static/*` → collected static files (cached 7d)
- `/media/*` → user uploads (short cache)
- `/*` → SvelteKit app (HTML `Cache-Control: no-store`)
- `/assets/*` → SvelteKit assets (immutable cache)

### Run Migrations & Seed in Docker

```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed
```

### Stop

```bash
docker compose down          # keep data
docker compose down -v       # remove volumes (fresh start)
```

## API Endpoints

| Endpoint                  | Methods              | Auth     |
|---------------------------|----------------------|----------|
| `/api/auth/login/`        | POST                 | Public   |
| `/api/auth/token/refresh/`| POST                 | Public   |
| `/api/users/`             | GET, POST            | Public (register) / Auth |
| `/api/users/me/`          | GET                  | Auth     |
| `/api/spaces/`            | GET, POST            | Auth     |
| `/api/spaces/{id}/`       | GET, PUT, DELETE      | Auth     |
| `/api/pages/`             | GET, POST            | Auth     |
| `/api/pages/{id}/`        | GET, PUT, DELETE      | Auth     |
| `/api/pages/{id}/tree/`   | GET                  | Auth     |
| `/api/page-versions/`     | GET                  | Auth     |
| `/api/comments/`          | GET, POST            | Auth     |
| `/api/comments/{id}/`     | GET, PUT, DELETE      | Auth     |
| `/api/attachments/`       | GET, POST            | Auth     |

## Migration Note (Rollback)

If you need to temporarily restore the old React frontend:

1. Revert `docker-compose.yml` to the `frontend` service pointing at `./frontend`
2. Update `nginx.conf` upstream `frontend` to `frontend:80` and default `location /` to that upstream
3. Rebuild and up: `docker compose up --build -d`

## License

MIT
