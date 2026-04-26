# Altassian MVP — Design

**Date:** 2026-04-26
**Status:** Approved (brainstorm complete, ready for implementation plan)
**Repo:** `~/.openclaw/workspace/altassian_backend/`
**Domain:** altassian.ai (Spaceship; routed via existing GCP load balancer)

## Vision

A markdown-first, dev-team wiki — "Linear for docs." Single-organization v1. Confluence/Notion clone in spirit, but markdown is the source of truth and the editor experience is split-pane (raw markdown ↔ live preview), not a block editor. Devs prefer this; it ships faster.

Long-term differentiation: AI-native features layered on top after v1 lands. Out of scope here.

## Scope

### In v1

- Email/password auth, JWT in httpOnly cookies, invite-only signup
- Single organization (no multi-tenancy)
- Spaces (wiki namespaces) with admin-controlled lifecycle
- Hierarchical pages with parent/child, drag-to-reorder, slugs
- Markdown editing in split-pane editor with live preview
- Page version history, with one-click restore
- Threaded comments on pages
- File attachments (images render inline; other files download)
- Full-text search across pages (Postgres FTS)
- Public pages (`is_public=True`) readable without login at `/p/<space>/<slug>`
- Two roles: admin, member

### Out of scope (deliberate; each is its own future spec)

Real-time collaborative editing · WYSIWYG/block editor · mentions and notifications · GitHub OAuth · GitHub/PR integrations · AI features · multi-organization · mobile native app · public page index/SEO · permissions beyond admin/member · file previews beyond images.

## Architecture

```
altassian.ai → existing GCP load balancer → data2dialog-v1-vm
                                                │
                                       docker-compose
                                       ├─ postgres:16
                                       ├─ django (gunicorn) — 127.0.0.1:8001
                                       └─ nextjs (node)     — 127.0.0.1:3001
```

- **Backend:** Django 5.2 + DRF, Python 3.11, JWT via djangorestframework-simplejwt
- **Frontend:** Next.js 16 (App Router) + React 19, TanStack Query, Jotai, ky, Tailwind v4, react-markdown + remark-gfm. Already scaffolded at `frontend-next/`.
- **DB:** Postgres 16 (no SQLite in any environment)
- **No Redis, no queue, no cache layer for v1.** Add when there's a concrete need.
- **LB routing:** Path-based on `altassian.ai`: `/api/*` → Django port, everything else → Next.js port. Existing LB; just add backend + URL map rule.
- **Bind to localhost** on the VM (`127.0.0.1:8001`, `127.0.0.1:3001`) to avoid colliding with existing services on 8000/3000.

## Data Model

```
Organization (singleton)
  id, name, logo_url, settings (JSONB), created_at

User (extends AbstractUser, AUTH_USER_MODEL = user_accounts.CustomUser)
  email (unique, used as USERNAME_FIELD), password, display_name, avatar_url,
  role (admin|member), is_active, joined_at

Invite
  id, email, token (unique), invited_by_fk, expires_at, accepted_at (nullable),
  created_at

Space
  id, slug (unique), name, description, icon (emoji or URL), position (int),
  created_by_fk, created_at, updated_at

Page
  id, space_fk, parent_fk (self, nullable), slug, title,
  body_md (text), body_html_cache (text), position (int),
  is_public (bool, default false), is_draft (bool, default false),
  created_by_fk, updated_by_fk, created_at, updated_at,
  deleted_at (nullable, for soft-delete),
  search_vector (tsvector, GIN-indexed)

  Constraint: UNIQUE (space_id, slug) WHERE deleted_at IS NULL

PageVersion
  id, page_fk, version_n (int), body_md, edited_by_fk, change_summary, created_at

  Constraint: UNIQUE (page_id, version_n)

Comment
  id, page_fk, author_fk, body_md, parent_fk (self, nullable for replies),
  created_at, deleted_at (nullable)

Attachment
  id, page_fk, file (FileField → /media/attachments/<uuid>/<filename>),
  original_filename, mime_type, size_bytes, uploaded_by_fk, created_at
```

**Notes:**
- `body_html_cache` is the rendered Markdown → HTML, regenerated on save (server-side via `markdown-it-py` or similar). Saves work on every page view.
- `search_vector` populated by Django `post_save` signal: `to_tsvector('english', title || ' ' || body_md)`.
- Soft-delete on `Page` and `Comment` so history stays intact; hard-delete is admin-only and uncommon.

## API Surface (DRF)

### Auth

```
POST   /api/auth/login            { email, password } → sets httpOnly access + refresh cookies
POST   /api/auth/logout           clears cookies + blacklists refresh token
POST   /api/auth/refresh          rotates access cookie from refresh cookie
GET    /api/auth/me               current user
```

### Invites

```
GET    /api/invites               (admin) list pending
POST   /api/invites               (admin) { email } → creates token, sends email
DELETE /api/invites/<id>          (admin) revoke
GET    /api/invites/<token>       public; returns email + validity for prefill
POST   /api/invites/<token>/accept { password, display_name } → creates user, logs in
```

### Spaces

```
GET    /api/spaces                list (auth users see all; public users see none here)
POST   /api/spaces                (admin) create
GET    /api/spaces/<slug>         detail with full page tree (nested)
PATCH  /api/spaces/<slug>         (admin) update
DELETE /api/spaces/<slug>         (admin) delete (cascades to pages — admin must confirm)
```

### Pages

```
POST   /api/pages                 { space, parent, title, body_md, is_draft } → creates Page + PageVersion 1
GET    /api/pages/<id>            detail (md + html + metadata + parent breadcrumb)
PATCH  /api/pages/<id>            update; on body_md change, creates new PageVersion
DELETE /api/pages/<id>            soft-delete (sets deleted_at)
POST   /api/pages/<id>/move       { parent_id, position } reorder/reparent
GET    /api/pages/<id>/versions   list (n, edited_by, summary, created_at)
GET    /api/pages/<id>/versions/<n>   one version (full body)
POST   /api/pages/<id>/restore/<n>    restore body_md from version n (creates new version)
```

### Comments

```
GET    /api/pages/<id>/comments   threaded (parent_fk for replies)
POST   /api/pages/<id>/comments   { body_md, parent_id? }
DELETE /api/comments/<id>         soft-delete (own comments; admins any)
```

### Attachments

```
POST   /api/pages/<id>/attachments   multipart upload
DELETE /api/attachments/<id>          (uploader or admin)
```

### Search

```
GET    /api/search?q=...&space=<slug>?  Postgres FTS, ts_rank ordered, ts_headline snippet
```

### Public read (no auth)

```
GET    /api/public/spaces/<space-slug>/pages/<page-slug>   only if page.is_public=True
```

### Permissions

- `IsAuthenticated` default on all `/api/*` except `/api/public/*`, `/api/auth/login`, `/api/invites/<token>` (GET), `/api/invites/<token>/accept`.
- `IsAdmin` on space create/delete/update, invite create/delete, user role changes.
- Object-level: only authors (or admins) can edit/delete their pages and comments. Member can edit any page in any space; that's a v1 simplification (everyone can write).

## Frontend Routes (Next.js App Router)

```
/                          if logged in → /home, else → /login
/login                     email + password
/invite/<token>            accept invite (set password + display name)
/home                      recent pages, your drafts, recent activity
/s/<space-slug>            space home: page tree sidebar + space welcome page
/s/<space-slug>/<page-slug>           page view (rendered HTML)
/s/<space-slug>/<page-slug>/edit      split-pane editor (md left, preview right)
/s/<space-slug>/<page-slug>/history   version list
/search?q=...              search results
/settings                  user settings (display name, password, avatar)
/settings/org              (admin) org name, logo, members, invites
/p/<space-slug>/<page-slug>           public page view (no auth)
```

### Layout

- Left sidebar: spaces list (collapsible), active space's page tree (with drag handles).
- Top bar: global search input, "+ New" menu (page/space), user menu.
- Main: page content. View mode shows rendered HTML with the comment thread below it. Edit mode replaces the content with a split-pane editor (CodeMirror 6 left, react-markdown render right, debounced sync).
- Mobile: sidebar becomes a drawer, top bar stays.

### State

- TanStack Query for server state (caching, mutations, invalidation).
- Jotai for ephemeral UI state (sidebar open, editor focus, draft buffer).
- ky for HTTP. Auth handled via httpOnly cookies — no token in JS.

## Auth Flow

1. **Bootstrap.** `python manage.py create_admin --email=naman@... --password=...` creates the first admin and the singleton `Organization` row.
2. **Login.** POST credentials. Backend returns access cookie (15 min, httpOnly, Secure, SameSite=Lax) and refresh cookie (14 days, same flags, restricted path `/api/auth/refresh`). No tokens in JSON body.
3. **Auth check.** Next.js middleware reads access cookie. On 401 from backend, frontend calls `/api/auth/refresh`; on success retries the original request, on failure redirects to `/login`.
4. **Invites.** Admin creates invite → token + expiry stored → email sent (SMTP via `EMAIL_BACKEND` configured in env; v1 OK with a single SMTP relay like Gmail app password). Token URL: `https://altassian.ai/invite/<token>`. Accept page POSTs to `/api/invites/<token>/accept`, server creates user, logs them in (sets cookies), redirects to `/home`.
5. **No public signup.** No "create account" button anywhere.

## Search

- Postgres `tsvector` column on `Page`, GIN-indexed.
- Populated by `post_save` signal on Page: `to_tsvector('english', coalesce(title, '') || ' ' || coalesce(body_md, ''))`.
- Query endpoint: `plainto_tsquery('english', :q)` + `ts_rank` for ordering + `ts_headline` for snippet.
- Returns: `[{ page_id, space_slug, page_slug, title, snippet_html, rank }]`, default 20 results.
- Filters: optional `space=<slug>`, auth-scoped (members see all non-deleted; anonymous would only hit `/api/public/*` which doesn't expose search).
- Latency target: <100 ms for an org with <10k pages. Plenty of headroom on Postgres FTS at this scale. Revisit (Meilisearch or Typesense) only if we cross ~100k pages or need fuzzy/typo tolerance.

## Deployment

### Compose stack on `data2dialog-v1-vm`

```yaml
# ~/altassian/docker-compose.yml (new location, separate from existing services)
services:
  postgres:
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]
    environment: [POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD]
    ports: ["127.0.0.1:5433:5432"]   # 5433 to avoid clash if existing pg on 5432
  django:
    build: ./altassian_backend
    env_file: .env
    depends_on: [postgres]
    command: ["sh","-c","python manage.py migrate && gunicorn altassian_core.wsgi -b 0.0.0.0:8000 -w 3"]
    ports: ["127.0.0.1:8001:8000"]
    volumes: [media:/app/media]
  nextjs:
    build: ./altassian_backend/frontend-next
    env_file: .env
    depends_on: [django]
    command: ["sh","-c","npm run build && npm run start -- -H 0.0.0.0 -p 3000"]
    ports: ["127.0.0.1:3001:3000"]
volumes: { pgdata: {}, media: {} }
```

### LB / DNS

- DNS (Spaceship): A record `altassian.ai` → existing LB IP. Same for `www.altassian.ai` (CNAME or A).
- GCP LB: add new backend service pointing to instance group → port 8001 for `/api/*`, port 3001 for everything else. Add URL map rule for host `altassian.ai`.
- Google-managed SSL cert for `altassian.ai` and `www.altassian.ai`.

### Backups

- Cron on the VM: `pg_dump altassian | gzip > ~/lb-backups/altassian/altassian-$(date +%F).sql.gz`, daily at 03:00 UTC, 30-day retention.

### Env vars (.env, gitignored)

```
DJANGO_SECRET_KEY=...
DATABASE_URL=postgres://altassian:...@postgres:5432/altassian
ALLOWED_HOSTS=altassian.ai,www.altassian.ai,localhost
JWT_ACCESS_LIFETIME=900
JWT_REFRESH_LIFETIME=1209600
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
DEFAULT_FROM_EMAIL=hello@altassian.ai
PUBLIC_BASE_URL=https://altassian.ai
NEXT_PUBLIC_API_BASE=/api
```

## Cleanup Phase (Day 1)

The repo at `~/.openclaw/workspace/altassian_backend/` was AI-built and is sprawling. Before any feature work, delete dead code so we're not fighting it.

### Delete outright

- `frontend/`, `frontend-svelte/` — old frontend attempts, replaced by `frontend-next/`
- `accounts/` — empty duplicate of `user_accounts/`
- `node_modules/` at repo root (only `frontend-next/node_modules` is needed)
- `db.sqlite3` — Postgres only from now on
- All openclaw artifacts: `PHASE1_PROMPT.md`, `PHASE3_PROMPT.md`, `PHASE4_TASK3_PROMPT.md`, `BUILD_STATUS.md`, `HEARTBEAT.md`, `IDENTITY.md`, `MEMORY.md`, `SOUL.md`, `STRATEGY.md`, `TASK_PROMPT.md`, `USER.md`, `AGENTS.md`, `ROLLBACK_NOTES.md`, `TOOLS.md`
- `analytics/`, `integrations/`, `notifications/`, `projects/`, `artifacts/` apps — delete unless an audit shows real, working models we want to keep. Bias toward delete; we re-add when we have a concrete need.

### Audit and rebuild

For each kept app (`user_accounts`, `spaces`, `pages`, `search`; `audit/` only if it has a working model worth keeping — otherwise delete):

- Keep `models.py` if the schema matches this design (it largely does for `pages`).
- Rebuild `serializers.py`, `views.py`, `urls.py`, `admin.py` cleanly to match the API surface above.
- Drop existing migrations, regenerate from scratch (no production data to preserve yet).
- Re-run `makemigrations` + `migrate` on a fresh Postgres DB.

### Update root config

- New `requirements.txt` (or `pyproject.toml`) reflecting actual dependencies.
- New `Dockerfile` for Django, new for Next.js (or use multi-stage in monorepo).
- New `docker-compose.yml` matching the stack above.
- Delete root `Makefile` if it doesn't apply; rewrite if useful.
- Single `README.md` rewritten for the new state.
- Update `.env.example`.
- New `.gitignore` audit (ensure `.env`, `media/`, `node_modules/`, `*.sqlite3`, `__pycache__/` covered).

### Then commit the cleanup as one or more atomic commits before any feature work. New baseline.

## Success Criteria for v1

- A logged-in user can create a space, create nested pages, edit them in the split-pane editor, see live preview, save, view history, comment, upload attachments.
- Search returns ranked results across all pages within <100 ms.
- An admin can invite a user via email; the user accepts and is logged in.
- A page marked public is readable at `https://altassian.ai/p/<space>/<slug>` with no auth.
- Site runs at `https://altassian.ai` with valid TLS.
- Basic mobile responsiveness (sidebar collapses to drawer, editor still usable).
- Nightly Postgres backup runs and a restore has been verified once.

## Risks & Open Questions

- **Existing-code drag.** "Clean up in place" can become a swamp if the legacy code is worse than expected. Mitigation: cleanup phase is its own commit; if we hit ~1 day of cleanup with no end in sight, switch to a fresh-start approach using only `models.py` files as reference.
- **GCP LB config gotchas.** Path-based routing across two backend ports on the same VM works, but health checks need to be wired correctly per backend service. We'll verify with a staging path before flipping `altassian.ai`.
- **SMTP for invites.** Gmail app passwords work but rate-limit; if invite volume grows, switch to Postmark/Resend later.
- **SSR vs CSR for Next.js.** Default to SSR for public pages (good for the `/p/*` route's eventual SEO), CSR-with-server-data for authed pages. Auth happens via cookies that the SSR pass can read.
- **Markdown rendering parity.** Server-side render (Python markdown-it-py) and client-side render (react-markdown + remark-gfm) must agree on output for stable hydration. Pick one rendering pipeline as canonical (server) and have client only re-render in the editor preview.

## Next Step

Hand off to `superpowers:writing-plans` to produce a phased implementation plan: cleanup → models/migrations → API → frontend skeleton → editor → search → deploy.
