Rollback instructions for frontend switch

- Current: nginx routes / to frontend-next (Next.js at port 3000)
- Previous: Svelte frontend at port 5173

How to rollback:
1) Edit nginx.conf: change upstream frontend_next -> frontend_svelte and / location proxy_pass to http://frontend_svelte; (see git history prior to this change)
2) Edit docker-compose.yml: in nginx depends_on, swap to frontend-svelte if removed
3) docker compose up -d --build nginx frontend-svelte

Blue/green tip:
- Keep both services up; toggle only nginx upstream to switch traffic instantly
