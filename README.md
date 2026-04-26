# Altassian Backend

Markdown-first wiki backend. Django 5.2 + DRF on Postgres 16.
Spec: `docs/specs/2026-04-26-altassian-mvp-design.md`

## Local development

```bash
docker compose -f docker-compose.dev.yml up -d
python3.11 -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
python manage.py migrate
python manage.py create_admin --email=you@example.com --password=changeme --org-name=Altassian
python manage.py seed_demo   # optional
python manage.py runserver 0.0.0.0:8000
```

API at `http://localhost:8000/api/`. Admin at `http://localhost:8000/admin/`.

## Tests

```bash
pytest
```

## Architecture

- `user_accounts/` — `CustomUser` (email-as-username, role), `Organization` (singleton), invites, JWT cookie auth
- `spaces/` — wiki namespaces
- `pages/` — `Page`, `PageVersion`, `Comment`, `Attachment`; markdown rendered server-side and cached
- `search/` — `/api/search` (Postgres FTS)
- `public_api/` — `/api/public/spaces/<s>/pages/<p>` for `is_public` pages
