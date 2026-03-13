# Frontend (SvelteKit)

New SvelteKit + TypeScript app lives here. This does not replace the existing frontend yet.

- Dev: `npm run dev` (proxies `/api` to Django; set VITE_DEV_PROXY_TARGET=http://localhost:8000)
- Build: `npm run build`
- Preview: `npm run preview`

Routes:
- `/login`, `/register`
- `/` Dashboard
- `/spaces`, `/spaces/[key]`, `/spaces/[key]/pages/[slug]`

Auth: access/refresh tokens in localStorage, eager refresh on 401.

Playwright tests in `tests/` (to be expanded).

Docker: see docker-compose service `frontend-svelte`.
