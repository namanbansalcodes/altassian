# CLAUDE.md — Altassian Backend

## Project
Altassian is a Confluence/wiki clone. This is the Django + DRF backend.

## Tech Stack
- Python 3.11, Django 5.2, Django REST Framework
- JWT auth via djangorestframework-simplejwt
- SQLite for dev, Postgres for prod
- Virtual env at ./venv (always activate: `source ./venv/bin/activate`)

## Architecture
- `altassian_core/` — Django project settings, root URL config
- `user_accounts/` — CustomUser model extending AbstractUser
- `spaces/` — Space model (wiki namespaces)
- `pages/` — Page, PageVersion, Comment, Attachment models
- AUTH_USER_MODEL = "user_accounts.CustomUser"

## Code Standards
- Type hints on all function signatures
- Serializers with proper validation, nested where appropriate
- ViewSets with IsAuthenticated default, object-level permissions for owners
- All model changes require makemigrations + migrate
- Git commit after every meaningful unit of work
- No placeholder code or TODOs

## Known Issues
- settings.py may be incomplete or corrupted — verify it has all required Django config before doing anything else
- The `accounts/` app dir exists but is unused — `user_accounts/` is the real app
- Some apps may be missing __init__.py, apps.py, admin.py

## Commands
```bash
source ./venv/bin/activate
pip install -r requirements.txt  # if it exists
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
python manage.py test
```
