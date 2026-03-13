# Quickstart

## Prereqs
- Python 3.11
- Docker + Docker Compose (optional)
- Node (for frontend proxy, optional)

## Local (no Docker)

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver

## Docker

docker compose -f docker-compose.yml up --build

App served via Nginx on http://localhost:8080
