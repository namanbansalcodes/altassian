Finalize the Altassian project:
1. Update docker-compose.yml: backend (Django) + frontend (Vite/nginx) + postgres + nginx reverse proxy
2. Create nginx.conf for routing /api to backend, / to frontend
3. Add production Dockerfiles for both backend and frontend
4. Create a seed data script (python manage.py seed) that creates sample users, spaces, and pages
5. Update README.md with full setup instructions (local dev + Docker)

Rules:
- Use venv at ./venv for any Python scripts.
- Git commit after each meaningful chunk.
- When completely finished, run: openclaw system event --text "Done: Altassian fully containerized with Docker Compose, seed data, and README" --mode now
