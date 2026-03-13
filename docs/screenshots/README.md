# Screenshot Pipeline

Automated Playwright-based screenshot capture for the Altassian frontend.

## Quick Start

```bash
# 1. Start backend + frontend
python manage.py runserver 0.0.0.0:8001   # backend
cd ../altassian_frontend && pnpm dev       # frontend on :5173

# 2. Run screenshots
pnpm snapshots   # or: npm run snapshots
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALTASSIAN_FRONTEND_URL` | `http://localhost:5173` | Frontend base URL |
| `ALTASSIAN_BACKEND_URL` | `http://localhost:8001` | Backend base URL |
| `ALTASSIAN_DEMO_EMAIL` | `admin` | Login username/email |
| `ALTASSIAN_DEMO_PASSWORD` | `AdminPass123` | Login password |

## Output Structure

```
docs/screenshots/
├── desktop/          # 1440×900
│   ├── home-light.png
│   ├── home-dark.png
│   └── ...
├── mobile/           # 390×844
│   ├── home-light.png
│   ├── home-dark.png
│   └── ...
├── manifest.json     # Route → file mapping
├── index.md          # Visual gallery with embedded images
└── README.md         # This file
```

## Viewports

- **Desktop**: 1440×900 (standard laptop)
- **Mobile**: 390×844 (iPhone 12/13/14)

## Themes

Both **light** and **dark** are captured for every route.

## Routes Captured

| Route | States |
|-------|--------|
| `/login` | light, dark |
| `/register` | light, dark |
| `/landing` | light, dark |
| `/` (dashboard) | light, dark |
| `/spaces` | light, dark |
| `/spaces/create` | light, dark |
| `/spaces/:key` | light, dark |
| `/spaces/:key/pages/:slug` | light, dark |
| `/spaces/:key/pages/:slug/edit` | light, dark, slash-menu |
| `/spaces/:key/pages/new` | light, dark |
| `/spaces/:key/pages/:slug/history` | light, dark |
| `/search` | empty, with results (light, dark) |
| `/spaces/:key/settings` | light, dark |
| `/*` (404) | light, dark |

## CI Usage

Add to your CI pipeline:

```yaml
- name: Screenshot capture
  run: |
    npx playwright install --with-deps chromium
    npm run snapshots
- uses: actions/upload-artifact@v4
  with:
    name: screenshots
    path: docs/screenshots/
```

## Sending to Naman

Screenshots should be sent to Naman via Telegram (user ID: 7863363002).
After committing, share the GitHub links to the `docs/screenshots/` directory.
