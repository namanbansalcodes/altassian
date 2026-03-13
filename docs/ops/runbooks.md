# Ops Runbooks

## Restart stack (Docker)

docker compose down && docker compose up -d --build

## Collect static

python manage.py collectstatic --noinput

## Create superuser

python manage.py createsuperuser
