# Altassian Deploy — Implementation Plan (Plan 3)

> **For agentic workers:** Operational plan. Each task ends in a verifiable result.

**Goal:** `https://altassian.ai` and `https://www.altassian.ai` serve the Plan 1 backend + Plan 2 frontend over TLS, behind the existing GCP HTTPS load balancer at `34.49.90.97`.

**Strategy:** Re-use the working hiringsignal.ai pattern. Production stack runs on `data2dialog-v1-vm` via docker-compose, bound to `127.0.0.1:3002` (Next.js) and `127.0.0.1:8002` (Django). Existing LB gets two new backend services + a host rule. A new Google-managed SSL cert covers the apex + www. DNS A records at Spaceship point to the LB IP.

## Pre-flight

Free ports on the VM (per `gcloud compute instance-groups describe data2dialog-group`): `8002`, `8003`, `3002`, `3003` are unused. Picking **8002 (django)** + **3002 (nextjs)**. Picking **5434** for the prod Postgres on the VM (5432 + 5433 already in use by other services).

Existing LB IP: `34.49.90.97` (HTTPS) — same one hiringsignal.ai uses.

DNS provider: Spaceship (creds in memory). API at `https://spaceship.dev/api/v1/`.

---

## Task 1: Production Dockerfile for Django

**Files:** `Dockerfile.backend` (replaces the bare `Dockerfile` if any)

```dockerfile
# Dockerfile.backend
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DJANGO_SETTINGS_MODULE=altassian_core.settings

WORKDIR /app

# System deps for psycopg + Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev libjpeg-dev zlib1g-dev curl \
  && rm -rf /var/lib/apt/lists/*

# Install dependencies first for Docker layer cache
COPY pyproject.toml ./
RUN pip install -U pip && pip install \
    "Django==5.2.*" "djangorestframework==3.15.*" \
    "djangorestframework-simplejwt==5.3.*" "psycopg[binary]==3.2.*" \
    "markdown-it-py==3.0.*" "mdit-py-plugins==0.4.*" \
    "python-decouple==3.8" "Pillow==10.4.*" \
    "gunicorn==23.0.*"

# App code
COPY altassian_core ./altassian_core
COPY user_accounts ./user_accounts
COPY spaces ./spaces
COPY pages ./pages
COPY search ./search
COPY public_api ./public_api
COPY manage.py ./

# Static files
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn altassian_core.wsgi --bind 0.0.0.0:8000 --workers 3 --access-logfile - --error-logfile -"]
```

Test build:

```bash
cd ~/.openclaw/workspace/altassian_backend
docker build -f Dockerfile.backend -t altassian-backend:dev .
```

Commit `Dockerfile.backend`.

---

## Task 2: Production Dockerfile for Next.js

**Files:** `frontend-next/Dockerfile.prod` (the existing `Dockerfile` is fine to keep but write a clean prod one)

```dockerfile
# frontend-next/Dockerfile.prod
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1
RUN addgroup -g 1001 -S nodejs && adduser -S nextjs -u 1001
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
USER nextjs
EXPOSE 3000
CMD ["npm", "run", "start", "--", "-H", "0.0.0.0", "-p", "3000"]
```

Test build:

```bash
cd ~/.openclaw/workspace/altassian_backend/frontend-next
docker build -f Dockerfile.prod -t altassian-frontend:dev .
```

Commit `frontend-next/Dockerfile.prod`.

---

## Task 3: docker-compose.prod.yml

**Files:** `docker-compose.prod.yml` at repo root.

```yaml
# Bind containers to localhost only — GCP LB reaches the VM directly.
services:
  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - altassian_pgdata:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:5434:5432"
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "${POSTGRES_USER}", "-d", "${POSTGRES_DB}"]
      interval: 10s
      timeout: 3s
      retries: 5

  django:
    build:
      context: .
      dockerfile: Dockerfile.backend
    restart: unless-stopped
    env_file: .env.prod
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - altassian_media:/app/media
      - altassian_static:/app/staticfiles
    ports:
      - "127.0.0.1:8002:8000"

  nextjs:
    build:
      context: ./frontend-next
      dockerfile: Dockerfile.prod
    restart: unless-stopped
    env_file: .env.prod
    depends_on:
      - django
    ports:
      - "127.0.0.1:3002:3000"

volumes:
  altassian_pgdata:
  altassian_media:
  altassian_static:
```

Commit `docker-compose.prod.yml`.

---

## Task 4: Production env file

**Files:** `.env.prod` at repo root (gitignored — never committed).

```bash
cat > ~/.openclaw/workspace/altassian_backend/.env.prod <<'EOF'
# Django
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=__GENERATE_A_LONG_RANDOM_STRING__
ALLOWED_HOSTS=altassian.ai,www.altassian.ai,127.0.0.1,localhost

# Postgres (host inside docker network = "postgres")
POSTGRES_DB=altassian
POSTGRES_USER=altassian
POSTGRES_PASSWORD=__GENERATE_A_LONG_RANDOM_STRING__
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# JWT
JWT_ACCESS_LIFETIME=900
JWT_REFRESH_LIFETIME=1209600
JWT_COOKIE_SECURE=true
JWT_COOKIE_SAMESITE=Lax

# Email — use the host's existing SMTP relay (Gmail app password recommended).
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=true
DEFAULT_FROM_EMAIL=hello@altassian.ai

# App
PUBLIC_BASE_URL=https://altassian.ai
INVITE_TTL_DAYS=14

# Next.js (read at build time too — values used by frontend SSR)
NEXT_PUBLIC_API_BASE_URL=https://altassian.ai
INTERNAL_API_BASE_URL=http://django:8000
EOF
```

Generate real secrets:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(48))'  # for DJANGO_SECRET_KEY
python3 -c 'import secrets; print(secrets.token_urlsafe(24))'  # for POSTGRES_PASSWORD
```

Substitute the placeholders in `.env.prod`. Confirm `.env.prod` is in `.gitignore`.

---

## Task 5: CSRF + cross-origin Django config additions

**Files:** `altassian_core/settings.py`

We need the prod backend to accept CSRF from `altassian.ai`. Add (or merge into) settings.py near the JWT config:

```python
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="http://localhost:3000",
    cast=Csv(),
)
```

Add to `.env.prod`:

```
CSRF_TRUSTED_ORIGINS=https://altassian.ai,https://www.altassian.ai
```

Also: in production, the Next.js frontend SSR fetches the backend via `INTERNAL_API_BASE_URL=http://django:8000` (the docker network hostname). Django needs to accept that host. Add `django` to `ALLOWED_HOSTS` in `.env.prod`:

```
ALLOWED_HOSTS=altassian.ai,www.altassian.ai,django,127.0.0.1,localhost
```

Commit the `settings.py` change.

---

## Task 6: Update next.config.ts to honor INTERNAL_API_BASE_URL on the server

The current `next.config.ts` rewrite uses `NEXT_PUBLIC_API_BASE_URL` for dev. In prod, when running behind the LB, the rewrite shouldn't fire (the LB is doing the routing). But Next.js SSR fetches against the API directly — that's `lib/api.ts`'s `ssrApi`, which already uses `INTERNAL_API_BASE_URL`. So `next.config.ts` is fine as-is for prod (the rewrite doesn't matter when the LB strips/forwards `/api/*` to the Django backend).

No change needed. Verify `lib/api.ts` reads `INTERNAL_API_BASE_URL` (it does, per Plan 2 Task 2).

---

## Task 7: Build and start the prod stack on the VM

```bash
cd ~/.openclaw/workspace/altassian_backend
docker compose -f docker-compose.prod.yml --env-file .env.prod build
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d
sleep 15
docker compose -f docker-compose.prod.yml ps
# Expected: postgres healthy, django up, nextjs up

curl -i http://127.0.0.1:8002/api/health
# Expected: 200 + {"status":"ok"}

curl -i -s http://127.0.0.1:3002/login | head -10
# Expected: 200 + Next.js HTML
```

If any container is not running, `docker compose -f docker-compose.prod.yml logs <name>` and fix.

---

## Task 8: Bootstrap the prod org + admin

```bash
docker compose -f docker-compose.prod.yml exec django python manage.py create_admin \
  --email=naman.primary@gmail.com \
  --password='__PICK_ADMIN_PASSWORD__' \
  --org-name=Altassian
```

Verify by hitting the local login endpoint with the admin credentials:

```bash
curl -i -X POST http://127.0.0.1:8002/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"naman.primary@gmail.com","password":"__PICK_ADMIN_PASSWORD__"}' | head -15
# Expected: 200 + Set-Cookie altassian_access=...
```

(Optionally seed demo data: `docker compose -f docker-compose.prod.yml exec django python manage.py seed_demo`. Skip if you want a clean prod start.)

---

## Task 9: Add named ports to the GCP instance group

```bash
gcloud compute instance-groups set-named-ports data2dialog-group \
  --zone=us-central1-a \
  --named-ports=$(gcloud compute instance-groups describe data2dialog-group --zone=us-central1-a --format='value(namedPorts.list())' | tr ';' ',' | tr -d '{}'),altassian-back:8002,altassian-front:3002
```

Easier path (idempotent): explicitly list everything we want including the existing entries. Run:

```bash
gcloud compute instance-groups describe data2dialog-group --zone=us-central1-a --format='yaml(namedPorts)'
```

Copy the existing list, then run:

```bash
gcloud compute instance-groups set-named-ports data2dialog-group \
  --zone=us-central1-a \
  --named-ports='http:80,api:8000,n8n:8080,portfolio:4000,openclaw:8088,data-matic-front:3001,data-matic-back:8001,data-matic:9000,hs-front:3010,hs-back:8100,altassian-front:3002,altassian-back:8002'
```

Verify:

```bash
gcloud compute instance-groups describe data2dialog-group --zone=us-central1-a --format='value(namedPorts)' | tr ';' '\n' | grep altassian
# Expected:
# {'name': 'altassian-back', 'port': 8002}
# {'name': 'altassian-front', 'port': 3002}
```

---

## Task 10: Create backend services for altassian

We need two: `altassian-back` (django) and `altassian-front` (nextjs). Each needs a health check.

```bash
# Health check for the Django backend (hits /api/health)
gcloud compute health-checks create http altassian-back-hc \
  --port-name=altassian-back \
  --request-path=/api/health \
  --check-interval=10s \
  --timeout=5s \
  --healthy-threshold=2 \
  --unhealthy-threshold=3

# Health check for the Next.js frontend (hits /login since / does a 307 redirect)
gcloud compute health-checks create http altassian-front-hc \
  --port-name=altassian-front \
  --request-path=/login \
  --check-interval=10s \
  --timeout=5s \
  --healthy-threshold=2 \
  --unhealthy-threshold=3

# Backend service: django
gcloud compute backend-services create altassian-back \
  --global \
  --protocol=HTTP \
  --port-name=altassian-back \
  --health-checks=altassian-back-hc \
  --timeout=60s

gcloud compute backend-services add-backend altassian-back \
  --global \
  --instance-group=data2dialog-group \
  --instance-group-zone=us-central1-a

# Backend service: nextjs
gcloud compute backend-services create altassian-front \
  --global \
  --protocol=HTTP \
  --port-name=altassian-front \
  --health-checks=altassian-front-hc \
  --timeout=60s

gcloud compute backend-services add-backend altassian-front \
  --global \
  --instance-group=data2dialog-group \
  --instance-group-zone=us-central1-a
```

Verify:

```bash
gcloud compute backend-services list | grep altassian
# Expected: altassian-back, altassian-front
```

Within ~1 minute, both should report HEALTHY:

```bash
gcloud compute backend-services get-health altassian-back --global
gcloud compute backend-services get-health altassian-front --global
```

If a backend reports UNHEALTHY, debug:
- Make sure the docker-compose stack is up.
- `curl 127.0.0.1:8002/api/health` and `curl 127.0.0.1:3002/login` should both return 200 from the VM.
- The health check sees the LB-side IP, not localhost — make sure the GCP firewall allows the Google health-check ranges (`130.211.0.0/22`, `35.191.0.0/16`) to reach 8002/3002. (For data-matic and hiringsignal this is already configured at the firewall layer; same firewall rule should cover us.)

---

## Task 11: Add altassian.ai host rule to the URL map

We're patching `data2dialog-lb` with a new host rule + path matcher. Use a YAML export/import to be safe:

```bash
gcloud compute url-maps export data2dialog-lb --destination=/tmp/data2dialog-lb.yaml
```

Edit `/tmp/data2dialog-lb.yaml` to add to `hostRules`:

```yaml
- hosts:
  - altassian.ai
  - www.altassian.ai
  pathMatcher: altassian-matcher
```

And to `pathMatchers`:

```yaml
- defaultService: https://www.googleapis.com/compute/v1/projects/chat-data2dialog-ai/global/backendServices/altassian-front
  name: altassian-matcher
  pathRules:
  - paths:
    - /api/*
    - /admin/*
    - /static/*
    - /media/*
    service: https://www.googleapis.com/compute/v1/projects/chat-data2dialog-ai/global/backendServices/altassian-back
```

Then re-import:

```bash
gcloud compute url-maps import data2dialog-lb --source=/tmp/data2dialog-lb.yaml --quiet
```

Verify:

```bash
gcloud compute url-maps describe data2dialog-lb --format=yaml | grep -A 2 'altassian'
# Expected: altassian.ai, www.altassian.ai, altassian-matcher
```

---

## Task 12: Set DNS at Spaceship

Two A records: `@` and `www` → `34.49.90.97`. (Same target as hiringsignal.ai.)

Try the API first (fast, scriptable):

```bash
# Spaceship API uses X-API-Key + X-API-Secret. Creds in memory.
# (If creds-as-API-keys aren't set up, fall back to logging into spaceship.com directly.)
```

Actually — based on the Spaceship API memory, the `X-API-Key` and `X-API-Secret` are different from the username/password used for the web UI. The user may not have generated API keys yet. Easiest path: log into spaceship.com manually and add the records.

**Manual (recommended, fastest):**
1. Sign in at `https://spaceship.com` with the credentials in memory.
2. Find domain `altassian.ai`.
3. DNS records → add:
   - Type `A`, Name `@`, Value `34.49.90.97`, TTL `300` (5 min)
   - Type `A`, Name `www`, Value `34.49.90.97`, TTL `300`

Verify propagation:

```bash
dig +short A altassian.ai @8.8.8.8
dig +short A www.altassian.ai @8.8.8.8
# Expected (within minutes): 34.49.90.97 for both
```

If you used the Spaceship API and the memory file's keys are valid:

```bash
# Replace with real creds; do not commit.
KEY="..."
SECRET="..."
curl -X PUT "https://spaceship.dev/api/v1/dns/records/altassian.ai" \
  -H "X-API-Key: $KEY" -H "X-API-Secret: $SECRET" \
  -H "content-type: application/json" \
  -d '{"items":[
        {"type":"A","name":"@","address":"34.49.90.97","ttl":300},
        {"type":"A","name":"www","address":"34.49.90.97","ttl":300}
      ]}'
```

(Falls back to the web UI if API auth fails.)

---

## Task 13: Create + attach the SSL cert

Google-managed cert. Provisioning takes a few minutes once DNS is live.

```bash
gcloud compute ssl-certificates create altassian-ai-cert \
  --domains=altassian.ai,www.altassian.ai \
  --global
```

Attach to the existing HTTPS proxy. Find the proxy serving the existing certs:

```bash
gcloud compute target-https-proxies list
# Expected: data2dialog-lb-target-proxy-2 with several certs already
```

Add ours:

```bash
EXISTING=$(gcloud compute target-https-proxies describe data2dialog-lb-target-proxy-2 \
  --format='value(sslCertificates.list())' | tr ';' ',' )
gcloud compute target-https-proxies update data2dialog-lb-target-proxy-2 \
  --ssl-certificates="${EXISTING},altassian-ai-cert" \
  --global-ssl-certificates
```

(If the format of `sslCertificates.list()` doesn't pipe cleanly, do this manually: list existing, append `altassian-ai-cert`, pass the whole comma-separated list to `--ssl-certificates`.)

Wait for cert provisioning (5–60 min):

```bash
watch -n 30 'gcloud compute ssl-certificates describe altassian-ai-cert --format="value(managed.status,managed.domainStatus)"'
# Expected eventually: ACTIVE, altassian.ai=ACTIVE, www.altassian.ai=ACTIVE
```

If the cert reports `FAILED_NOT_VISIBLE` for either domain, the LB doesn't see DNS yet — wait longer or recheck `dig`.

---

## Task 14: Verify altassian.ai is live

```bash
# HTTPS apex
curl -I https://altassian.ai/
# Expected: HTTP/2 200 (or 307 to /login)

# Login API through the LB
curl -i -X POST https://altassian.ai/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"naman.primary@gmail.com","password":"__ADMIN_PASSWORD__"}' | head -15
# Expected: HTTP/2 200 + Set-Cookie altassian_access=...; Secure; HttpOnly

# Static frontend
curl -s https://altassian.ai/login | grep -o '<title>[^<]*' | head -1
# Expected: <title>Altassian
```

In a real browser:
- `https://altassian.ai` → redirect to `/login`
- Sign in as the admin → land on `/home`
- Click around: spaces, page tree, view, edit, search

If anything 502s or 503s, `gcloud compute backend-services get-health altassian-front --global` and check for unhealthy backends.

---

## Task 15: Nightly Postgres backup

```bash
mkdir -p ~/lb-backups/altassian
cat > ~/lb-backups/altassian/backup.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
ts=$(date +%F)
out=~/lb-backups/altassian/altassian-$ts.sql.gz
docker compose -f ~/.openclaw/workspace/altassian_backend/docker-compose.prod.yml \
  --env-file ~/.openclaw/workspace/altassian_backend/.env.prod \
  exec -T postgres pg_dump -U altassian altassian | gzip > "$out"
# Retain 30 days
find ~/lb-backups/altassian -name 'altassian-*.sql.gz' -mtime +30 -delete
EOF
chmod +x ~/lb-backups/altassian/backup.sh
```

Add to user crontab (`crontab -e`):

```
0 3 * * * /home/namanbansal/lb-backups/altassian/backup.sh >>/home/namanbansal/lb-backups/altassian/backup.log 2>&1
```

Run once now to verify:

```bash
~/lb-backups/altassian/backup.sh
ls -la ~/lb-backups/altassian/
# Expected: altassian-YYYY-MM-DD.sql.gz exists, non-empty
```

---

## Task 16: Final checks + tag

- [ ] `https://altassian.ai` returns 200 (or 307 to /login) with valid TLS
- [ ] `https://altassian.ai/login` renders
- [ ] Login as admin from the browser succeeds; redirect to `/home`
- [ ] `https://altassian.ai/api/auth/me` returns the admin user JSON when authenticated
- [ ] Health check `https://altassian.ai/api/health` → 200
- [ ] One nightly backup file exists
- [ ] Tag the milestone

```bash
cd ~/.openclaw/workspace/altassian_backend
git tag deploy-v0.1
```

---

## Risks & gotchas

- **Cert provisioning lag.** Google-managed certs require the LB to be serving the domain before they validate. Order of ops matters: DNS → URL map host rule → cert. If the cert fails, delete and recreate after DNS is fully propagated.
- **Firewall.** GCP HTTPS LB health checks come from `130.211.0.0/22` and `35.191.0.0/16`. The existing VM should already accept these (other backends work). If new backends report unhealthy, check the firewall rule that targets the data2dialog-group instance group.
- **Dual stacks on the same VM.** Six other docker-composes run on this VM (data-matic, hiringsignal, n8n, openclaw, portfolio). Memory is tight (~6 GB used of 7.8 GB). Adding altassian's three containers may push over. Watch `free -h`. If under pressure, the order to shed load: kill `openclaw-gateway` first (already done historically), then any unused dev next-server.
- **Static files in prod.** Django's `collectstatic` runs at image build. If `STATIC_ROOT` is broken or missing, admin static files (CSS/JS) won't load. The `Dockerfile.backend` has `python manage.py collectstatic --noinput || true` — verify this actually populates `/app/staticfiles` and that gunicorn is configured to serve them (or accept that the LB won't serve `/static/*` perfectly until we add a fix). For v1, Django admin styling matters less than user-facing UI; can revisit if it bothers.
