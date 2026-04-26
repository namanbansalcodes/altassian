# Altassian Backend MVP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a tested Django + DRF API for a single-organization markdown wiki. Output: every endpoint in the design spec works against a real Postgres DB, covered by pytest tests that pass green.

**Architecture:** Django 5.2 + DRF, Python 3.11. JWT (simplejwt) issued as httpOnly cookies. Postgres 16 only (no SQLite anywhere). Markdown rendered server-side and cached in `body_html_cache`. Search via Postgres FTS (`tsvector` + GIN). Single Django project (`altassian_core`). Apps reset to a clean baseline by dropping migrations and the `db.sqlite3` file at the start.

**Tech Stack:** Python 3.11, Django 5.2, djangorestframework, djangorestframework-simplejwt, psycopg[binary], markdown-it-py, mdit-py-plugins (gfm-style tables, task-lists, strikethrough), python-decouple (env), pytest + pytest-django, factory_boy.

**Spec:** `docs/specs/2026-04-26-altassian-mvp-design.md`

---

## File Map

After this plan, the backend repo at `~/.openclaw/workspace/altassian_backend/` will look like:

```
altassian_backend/
  altassian_core/
    __init__.py
    settings.py            # rewritten clean
    urls.py                # rewritten
    wsgi.py asgi.py        # kept (Django default)
  user_accounts/
    __init__.py
    apps.py
    models.py              # CustomUser (email-as-username, role, display_name) + Organization (singleton)
    serializers.py
    views.py               # LoginView, LogoutView, RefreshView, MeView
    invite_models.py       # Invite model
    invite_serializers.py
    invite_views.py        # invite CRUD + accept
    urls.py
    admin.py
    permissions.py         # IsAdmin
    management/commands/
      create_admin.py      # bootstrap singleton org + first admin
      seed_demo.py         # optional dev seed (admin + 2 spaces + 5 pages)
  spaces/
    __init__.py apps.py admin.py
    models.py              # Space
    serializers.py
    views.py               # ViewSet
    urls.py
  pages/
    __init__.py apps.py admin.py
    models.py              # Page, PageVersion, Comment, Attachment
    serializers.py
    views.py               # PageViewSet, CommentViewSet, AttachmentViewSet, version & restore actions
    urls.py
    rendering.py           # markdown_to_html()
    signals.py             # post_save: html cache + search vector + version create
    permissions.py         # IsAuthorOrAdmin (object-level)
  search/
    __init__.py apps.py
    views.py               # /api/search
    urls.py
  public_api/
    __init__.py apps.py
    views.py               # /api/public/spaces/<s>/pages/<p>
    urls.py
  tests/
    __init__.py
    conftest.py            # fixtures: api_client, admin_user, member_user, space, page, etc.
    factories.py           # factory_boy factories
    test_auth.py
    test_invites.py
    test_spaces.py
    test_pages.py
    test_versions.py
    test_comments.py
    test_attachments.py
    test_search.py
    test_public.py
    test_rendering.py
  manage.py                # kept
  pyproject.toml           # new (replaces requirements.txt)
  pytest.ini
  .env.example             # rewritten
  Dockerfile               # rewritten (Python 3.11-slim)
  docker-compose.dev.yml   # local Postgres only
  README.md                # rewritten
```

Apps deleted in cleanup: `accounts/`, `analytics/`, `artifacts/`, `audit/`, `integrations/`, `notifications/`, `projects/`, `shared/`, plus root `frontend/`, `frontend-svelte/`, `node_modules/`, `db.sqlite3`, `package.json`/`package-lock.json` at root, openclaw artifact docs, `nginx.conf`, `screenshots/`, `scripts/`. (The Next.js frontend at `frontend-next/` stays untouched in this plan — it's Plan 2's territory.)

---

## Phase A — Cleanup

The repo was AI-built and sprawling. Strip to a clean baseline before writing a line of new code.

### Task A1: Delete dead frontends and root JS

**Files:** Delete `frontend/`, `frontend-svelte/`, root `node_modules/`, root `package.json`, root `package-lock.json`.

- [ ] **Step 1: Delete**

```bash
cd ~/.openclaw/workspace/altassian_backend
rm -rf frontend frontend-svelte node_modules package.json package-lock.json
```

- [ ] **Step 2: Verify they're gone**

```bash
ls frontend frontend-svelte 2>&1 | tail -2
# Expected: "No such file or directory" for both
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: delete dead frontends and root JS package files"
```

### Task A2: Delete openclaw artifacts

**Files:** Delete openclaw build/identity files at repo root.

- [ ] **Step 1: Delete**

```bash
cd ~/.openclaw/workspace/altassian_backend
rm -f PHASE1_PROMPT.md PHASE3_PROMPT.md PHASE4_TASK3_PROMPT.md ROLLBACK_NOTES.md \
      docker-compose.override.yml nginx.conf
rm -rf screenshots scripts
```

- [ ] **Step 2: Commit**

```bash
git add -A
git commit -m "chore: delete openclaw build artifacts"
```

### Task A3: Delete dead Django apps

**Files:** Delete `accounts/`, `analytics/`, `artifacts/`, `audit/`, `integrations/`, `notifications/`, `projects/`, `shared/`.

- [ ] **Step 1: Delete**

```bash
cd ~/.openclaw/workspace/altassian_backend
rm -rf accounts analytics artifacts audit integrations notifications projects shared
```

- [ ] **Step 2: Verify the four apps we're keeping still exist**

```bash
ls -d user_accounts spaces pages search 2>&1
# Expected: all four listed, no errors
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: delete unused Django apps"
```

### Task A4: Drop sqlite and stale migrations

**Files:** Delete `db.sqlite3`, all migration files in kept apps (regenerate fresh against Postgres).

- [ ] **Step 1: Delete**

```bash
cd ~/.openclaw/workspace/altassian_backend
rm -f db.sqlite3
for app in user_accounts spaces pages search; do
  find $app/migrations -type f -name "0*.py" -delete 2>/dev/null
  find $app/migrations -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
done
```

- [ ] **Step 2: Verify only `__init__.py` remains in each migrations dir**

```bash
for app in user_accounts spaces pages search; do
  ls $app/migrations/ 2>/dev/null
  echo "---"
done
# Expected: each dir shows only __init__.py
```

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "chore: drop sqlite and stale migrations for fresh Postgres baseline"
```

### Task A5: Stand up local Postgres via docker-compose

**Files:**
- Create: `docker-compose.dev.yml`

- [ ] **Step 1: Write `docker-compose.dev.yml`**

```yaml
services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: altassian
      POSTGRES_USER: altassian
      POSTGRES_PASSWORD: altassian
    ports:
      - "127.0.0.1:5433:5432"
    volumes:
      - altassian_pgdata:/var/lib/postgresql/data
volumes:
  altassian_pgdata:
```

- [ ] **Step 2: Start it**

```bash
cd ~/.openclaw/workspace/altassian_backend
docker compose -f docker-compose.dev.yml up -d
sleep 3
docker compose -f docker-compose.dev.yml ps
# Expected: postgres service "Up"
```

- [ ] **Step 3: Verify connection**

```bash
PGPASSWORD=altassian psql -h 127.0.0.1 -p 5433 -U altassian -d altassian -c "SELECT 1;"
# Expected: returns 1
```

- [ ] **Step 4: Commit**

```bash
git add docker-compose.dev.yml
git commit -m "chore: add dev docker-compose with Postgres 16"
```

### Task A6: Replace requirements.txt with pyproject.toml

**Files:**
- Create: `pyproject.toml`
- Delete: `requirements.txt`, root `Dockerfile` (will be rewritten in Plan 3), `Makefile`, `ruff.toml`, root `docker-compose.yml`

- [ ] **Step 1: Delete the old build/config files**

```bash
cd ~/.openclaw/workspace/altassian_backend
rm -f requirements.txt Dockerfile Makefile ruff.toml docker-compose.yml
```

- [ ] **Step 2: Write `pyproject.toml`**

```toml
[project]
name = "altassian-backend"
version = "0.1.0"
description = "Altassian — markdown-first wiki backend"
requires-python = ">=3.11"
dependencies = [
  "Django==5.2.*",
  "djangorestframework==3.15.*",
  "djangorestframework-simplejwt==5.3.*",
  "psycopg[binary]==3.2.*",
  "markdown-it-py==3.0.*",
  "mdit-py-plugins==0.4.*",
  "python-decouple==3.8",
  "Pillow==10.4.*",
]

[project.optional-dependencies]
dev = [
  "pytest==8.3.*",
  "pytest-django==4.9.*",
  "factory_boy==3.3.*",
  "ruff==0.6.*",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP"]
ignore = ["E501"]
```

- [ ] **Step 3: Recreate the venv from scratch**

```bash
cd ~/.openclaw/workspace/altassian_backend
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
```

- [ ] **Step 4: Verify Django imports**

```bash
source venv/bin/activate
python -c "import django; print(django.get_version())"
# Expected: 5.2.x
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: replace requirements.txt with pyproject.toml; clean venv"
```

### Task A7: Set up pytest

**Files:**
- Create: `pytest.ini`
- Create: `tests/__init__.py` (empty)
- Create: `tests/conftest.py` (initial; expanded in Phase C)

- [ ] **Step 1: Write `pytest.ini`**

```ini
[pytest]
DJANGO_SETTINGS_MODULE = altassian_core.settings
python_files = test_*.py
addopts = -v --tb=short --reuse-db
```

- [ ] **Step 2: Create empty test package**

```bash
cd ~/.openclaw/workspace/altassian_backend
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 3: Write minimal `tests/conftest.py`**

```python
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()
```

- [ ] **Step 4: Commit**

```bash
git add pytest.ini tests/
git commit -m "test: scaffold pytest with pytest-django + APIClient fixture"
```

---

## Phase B — Foundation (settings, root URLs, env)

### Task B1: Write fresh `altassian_core/settings.py`

**Files:**
- Replace: `altassian_core/settings.py`

- [ ] **Step 1: Replace with the following**

```python
"""Django settings for altassian_core."""
from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("DJANGO_SECRET_KEY", default="dev-insecure-change-me")
DEBUG = config("DJANGO_DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "user_accounts",
    "spaces",
    "pages",
    "search",
    "public_api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "altassian_core.urls"
WSGI_APPLICATION = "altassian_core.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": [
            "django.template.context_processors.request",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
        ]},
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTGRES_DB", default="altassian"),
        "USER": config("POSTGRES_USER", default="altassian"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="altassian"),
        "HOST": config("POSTGRES_HOST", default="127.0.0.1"),
        "PORT": config("POSTGRES_PORT", default="5433"),
    }
}

AUTH_USER_MODEL = "user_accounts.CustomUser"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "user_accounts.authentication.CookieJWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 50,
}

JWT_ACCESS_LIFETIME = config("JWT_ACCESS_LIFETIME", default=900, cast=int)
JWT_REFRESH_LIFETIME = config("JWT_REFRESH_LIFETIME", default=1209600, cast=int)
JWT_COOKIE_SECURE = config("JWT_COOKIE_SECURE", default=False, cast=bool)
JWT_COOKIE_SAMESITE = config("JWT_COOKIE_SAMESITE", default="Lax")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(seconds=JWT_ACCESS_LIFETIME),
    "REFRESH_TOKEN_LIFETIME": timedelta(seconds=JWT_REFRESH_LIFETIME),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Email — local memory backend in dev/test, real SMTP in prod.
EMAIL_BACKEND = config("EMAIL_BACKEND", default="django.core.mail.backends.locmem.EmailBackend")
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="hello@altassian.ai")

PUBLIC_BASE_URL = config("PUBLIC_BASE_URL", default="http://localhost:3000")
INVITE_TTL_DAYS = config("INVITE_TTL_DAYS", default=14, cast=int)
```

- [ ] **Step 2: Write `.env` for local dev**

```bash
cat > .env <<'EOF'
DJANGO_DEBUG=true
DJANGO_SECRET_KEY=dev-insecure-change-me
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=altassian
POSTGRES_USER=altassian
POSTGRES_PASSWORD=altassian
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5433
EOF
```

- [ ] **Step 3: Confirm Django check passes (will fail at auth import — that's expected; we'll write it next)**

```bash
source venv/bin/activate
python manage.py check 2>&1 | tail -5
# Will fail with ImportError on user_accounts.authentication.CookieJWTAuthentication.
# That is expected; we wire it up in Task C5.
```

- [ ] **Step 4: Commit**

```bash
git add altassian_core/settings.py .env
# .env should be in .gitignore — verify before adding
grep -q "^.env$" .gitignore || echo ".env" >> .gitignore
git add .gitignore
git commit -m "feat: rewrite settings.py for Postgres + JWT; add dev .env"
```

### Task B2: Write `.env.example`

**Files:**
- Replace: `.env.example`

- [ ] **Step 1: Replace contents**

```bash
cat > .env.example <<'EOF'
# Django
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=replace-me
ALLOWED_HOSTS=altassian.ai,www.altassian.ai

# Postgres
POSTGRES_DB=altassian
POSTGRES_USER=altassian
POSTGRES_PASSWORD=replace-me
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# JWT cookies (production)
JWT_ACCESS_LIFETIME=900
JWT_REFRESH_LIFETIME=1209600
JWT_COOKIE_SECURE=true
JWT_COOKIE_SAMESITE=Lax

# Email (production: real SMTP)
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
EOF
```

- [ ] **Step 2: Commit**

```bash
git add .env.example
git commit -m "docs: rewrite .env.example for Postgres + JWT + email config"
```

### Task B3: Write fresh root `urls.py`

**Files:**
- Replace: `altassian_core/urls.py`

- [ ] **Step 1: Replace contents**

```python
"""Root URL configuration."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("user_accounts.urls")),
    path("api/", include("user_accounts.invite_urls")),
    path("api/spaces/", include("spaces.urls")),
    path("api/", include("pages.urls")),
    path("api/search/", include("search.urls")),
    path("api/public/", include("public_api.urls")),
]
```

- [ ] **Step 2: Commit (will fail check until apps exist; that's OK)**

```bash
git add altassian_core/urls.py
git commit -m "feat: define root URL structure"
```

---

## Phase C — User accounts, Organization, JWT cookie auth

### Task C1: Write `user_accounts/models.py`

**Files:**
- Replace: `user_accounts/models.py`

- [ ] **Step 1: Write the file**

```python
"""User and Organization models."""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Organization(models.Model):
    """Singleton: there is exactly one Organization row in this single-org MVP."""
    name = models.CharField(max_length=200)
    logo_url = models.URLField(blank=True, default="")
    settings = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.name

    @classmethod
    def get_singleton(cls) -> "Organization":
        org = cls.objects.first()
        if org is None:
            raise Organization.DoesNotExist("No Organization row exists. Run create_admin.")
        return org


class CustomUserManager(BaseUserManager):
    """Email is the unique identifier."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        extra.setdefault("role", CustomUser.Role.ADMIN)
        return self._create_user(email, password, **extra)


class CustomUser(AbstractUser):
    """Email-as-username user with org role."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    username = None  # disabled
    email = models.EmailField("email address", unique=True)
    display_name = models.CharField(max_length=120, blank=True, default="")
    avatar_url = models.URLField(blank=True, default="")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN
```

- [ ] **Step 2: Verify import**

```bash
source venv/bin/activate
python -c "import django; django.setup()" 2>&1 | tail -3
# Expected: ImportError on missing user_accounts.authentication module — fine, comes in C5.
```

- [ ] **Step 3: Commit**

```bash
git add user_accounts/models.py
git commit -m "feat(user_accounts): add CustomUser (email-username, role) and Organization singleton"
```

### Task C2: `user_accounts/apps.py` and `admin.py`

**Files:**
- Replace: `user_accounts/apps.py`
- Replace: `user_accounts/admin.py`

- [ ] **Step 1: Write `user_accounts/apps.py`**

```python
from django.apps import AppConfig


class UserAccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "user_accounts"
```

- [ ] **Step 2: Write `user_accounts/admin.py`**

```python
from django.contrib import admin

from .models import CustomUser, Organization


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "display_name", "role", "is_active", "joined_at")
    search_fields = ("email", "display_name")
    list_filter = ("role", "is_active")


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
```

- [ ] **Step 3: Commit**

```bash
git add user_accounts/apps.py user_accounts/admin.py
git commit -m "feat(user_accounts): app config and admin registrations"
```

### Task C3: Write `user_accounts/permissions.py`

**Files:**
- Create: `user_accounts/permissions.py`

- [ ] **Step 1: Write the file**

```python
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    message = "Admin role required."

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)
```

- [ ] **Step 2: Commit**

```bash
git add user_accounts/permissions.py
git commit -m "feat(user_accounts): IsAdmin permission"
```

### Task C4: Write `tests/factories.py` and seed `conftest.py`

**Files:**
- Create: `tests/factories.py`
- Modify: `tests/conftest.py`

- [ ] **Step 1: Write `tests/factories.py`**

```python
import factory
from django.contrib.auth import get_user_model

from user_accounts.models import Organization

User = get_user_model()


class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = "Altassian"


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    display_name = factory.Sequence(lambda n: f"User {n}")
    role = User.Role.MEMBER
    is_active = True

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or "testpass123")
        if create:
            obj.save()


class AdminFactory(UserFactory):
    role = User.Role.ADMIN
```

- [ ] **Step 2: Replace `tests/conftest.py`**

```python
import pytest
from rest_framework.test import APIClient

from tests.factories import AdminFactory, OrganizationFactory, UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def organization(db):
    return OrganizationFactory()


@pytest.fixture
def admin_user(db, organization):
    return AdminFactory()


@pytest.fixture
def member_user(db, organization):
    return UserFactory()


@pytest.fixture
def admin_client(api_client, admin_user):
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def member_client(api_client, member_user):
    api_client.force_authenticate(user=member_user)
    return api_client
```

- [ ] **Step 3: Commit**

```bash
git add tests/factories.py tests/conftest.py
git commit -m "test: add user/org factories and authenticated client fixtures"
```

### Task C5: Cookie-based JWT authentication class

**Files:**
- Create: `user_accounts/authentication.py`

- [ ] **Step 1: Write the file**

```python
"""DRF auth that reads the access JWT from an httpOnly cookie."""
from rest_framework_simplejwt.authentication import JWTAuthentication


ACCESS_COOKIE = "altassian_access"
REFRESH_COOKIE = "altassian_refresh"


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate by validating the JWT in the `altassian_access` cookie."""

    def authenticate(self, request):
        raw_token = request.COOKIES.get(ACCESS_COOKIE)
        if not raw_token:
            return None
        validated = self.get_validated_token(raw_token)
        return self.get_user(validated), validated
```

- [ ] **Step 2: `python manage.py check` should now pass**

```bash
source venv/bin/activate
python manage.py check 2>&1 | tail -3
# Expected: "System check identified no issues (0 silenced)."
```

- [ ] **Step 3: Commit**

```bash
git add user_accounts/authentication.py
git commit -m "feat(auth): cookie-based JWT authentication for DRF"
```

### Task C6: First migrations + migrate

**Files:** generated migration files in `user_accounts/migrations/`

- [ ] **Step 1: Make migrations**

```bash
source venv/bin/activate
python manage.py makemigrations user_accounts
# Expected: creates 0001_initial.py
```

- [ ] **Step 2: Migrate**

```bash
python manage.py migrate
# Expected: applies all built-in + simplejwt + user_accounts migrations cleanly
```

- [ ] **Step 3: Smoke-test**

```bash
python manage.py shell -c "from user_accounts.models import CustomUser, Organization; print(CustomUser.objects.count(), Organization.objects.count())"
# Expected: 0 0
```

- [ ] **Step 4: Commit**

```bash
git add user_accounts/migrations/
git commit -m "feat(user_accounts): initial migration"
```

### Task C7: `create_admin` management command

**Files:**
- Create: `user_accounts/management/__init__.py` (empty)
- Create: `user_accounts/management/commands/__init__.py` (empty)
- Create: `user_accounts/management/commands/create_admin.py`

- [ ] **Step 1: Write the test first**

```python
# tests/test_create_admin.py
import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from user_accounts.models import Organization

User = get_user_model()


@pytest.mark.django_db
def test_create_admin_creates_org_and_admin():
    call_command("create_admin", "--email=naman@example.com", "--password=secret123", "--org-name=Altassian")

    assert Organization.objects.count() == 1
    assert Organization.objects.first().name == "Altassian"

    admin = User.objects.get(email="naman@example.com")
    assert admin.is_admin
    assert admin.is_staff is True
    assert admin.is_superuser is True
    assert admin.check_password("secret123")


@pytest.mark.django_db
def test_create_admin_idempotent_on_org_but_errors_on_existing_email():
    call_command("create_admin", "--email=naman@example.com", "--password=secret123", "--org-name=Altassian")
    with pytest.raises(SystemExit):
        call_command("create_admin", "--email=naman@example.com", "--password=other", "--org-name=Altassian")
```

- [ ] **Step 2: Run test — should fail (command doesn't exist)**

```bash
pytest tests/test_create_admin.py -v
# Expected: errors with "Unknown command: 'create_admin'"
```

- [ ] **Step 3: Implement the command**

```bash
mkdir -p user_accounts/management/commands
touch user_accounts/management/__init__.py user_accounts/management/commands/__init__.py
```

```python
# user_accounts/management/commands/create_admin.py
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from user_accounts.models import Organization

User = get_user_model()


class Command(BaseCommand):
    help = "Create the singleton Organization (if missing) and a first admin user."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True)
        parser.add_argument("--password", required=True)
        parser.add_argument("--org-name", default="Altassian")
        parser.add_argument("--display-name", default="")

    def handle(self, *args, **opts):
        email = opts["email"].lower().strip()
        with transaction.atomic():
            org, created_org = Organization.objects.get_or_create(
                pk=1, defaults={"name": opts["org_name"]}
            )
            if not created_org and org.name != opts["org_name"]:
                self.stdout.write(self.style.WARNING(f"Org already named {org.name!r}; not renaming"))

            if User.objects.filter(email=email).exists():
                raise CommandError(f"User {email!r} already exists")

            user = User.objects.create_superuser(
                email=email,
                password=opts["password"],
                display_name=opts["display_name"] or email.split("@")[0],
                role=User.Role.ADMIN,
            )
            self.stdout.write(self.style.SUCCESS(f"Created admin {user.email} in org {org.name!r}"))
```

- [ ] **Step 4: Run test — should pass**

```bash
pytest tests/test_create_admin.py -v
# Expected: 2 passed
```

- [ ] **Step 5: Commit**

```bash
git add user_accounts/management/ tests/test_create_admin.py
git commit -m "feat(user_accounts): create_admin management command"
```

---

## Phase D — Auth endpoints (login, logout, refresh, me)

The four endpoints all use httpOnly cookies. We test each end-to-end through `APIClient`.

### Task D1: Auth views skeleton + serializers

**Files:**
- Create: `user_accounts/serializers.py`
- Create: `user_accounts/views.py`
- Create: `user_accounts/urls.py`

- [ ] **Step 1: Write the test first**

```python
# tests/test_auth.py
import pytest

from user_accounts.authentication import ACCESS_COOKIE, REFRESH_COOKIE


@pytest.mark.django_db
def test_login_sets_access_and_refresh_cookies(api_client, member_user):
    r = api_client.post("/api/auth/login", {"email": member_user.email, "password": "testpass123"}, format="json")
    assert r.status_code == 200, r.content
    assert ACCESS_COOKIE in r.cookies
    assert REFRESH_COOKIE in r.cookies
    assert r.cookies[ACCESS_COOKIE]["httponly"]
    assert r.cookies[REFRESH_COOKIE]["httponly"]


@pytest.mark.django_db
def test_login_wrong_password_returns_401(api_client, member_user):
    r = api_client.post("/api/auth/login", {"email": member_user.email, "password": "wrong"}, format="json")
    assert r.status_code == 401


@pytest.mark.django_db
def test_login_unknown_email_returns_401(api_client):
    r = api_client.post("/api/auth/login", {"email": "noone@example.com", "password": "x"}, format="json")
    assert r.status_code == 401


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    r = api_client.get("/api/auth/me")
    assert r.status_code == 401


@pytest.mark.django_db
def test_me_returns_user_after_login(api_client, member_user):
    api_client.post("/api/auth/login", {"email": member_user.email, "password": "testpass123"}, format="json")
    r = api_client.get("/api/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == member_user.email


@pytest.mark.django_db
def test_logout_clears_cookies(api_client, member_user):
    api_client.post("/api/auth/login", {"email": member_user.email, "password": "testpass123"}, format="json")
    r = api_client.post("/api/auth/logout")
    assert r.status_code == 204
    assert r.cookies[ACCESS_COOKIE].value == ""
    assert r.cookies[REFRESH_COOKIE].value == ""


@pytest.mark.django_db
def test_refresh_rotates_access_cookie(api_client, member_user):
    api_client.post("/api/auth/login", {"email": member_user.email, "password": "testpass123"}, format="json")
    old_access = api_client.cookies[ACCESS_COOKIE].value
    r = api_client.post("/api/auth/refresh")
    assert r.status_code == 200
    assert r.cookies[ACCESS_COOKIE].value
    assert r.cookies[ACCESS_COOKIE].value != old_access
```

- [ ] **Step 2: Run tests — should fail (404s)**

```bash
pytest tests/test_auth.py -v
# Expected: every test fails, mostly 404
```

- [ ] **Step 3: Implement `user_accounts/serializers.py`**

```python
from rest_framework import serializers

from .models import CustomUser


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "email", "display_name", "avatar_url", "role", "joined_at")
        read_only_fields = fields
```

- [ ] **Step 4: Implement `user_accounts/views.py`**

```python
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import ACCESS_COOKIE, REFRESH_COOKIE
from .serializers import LoginSerializer, UserSerializer


def _set_cookie(response, name: str, value: str, lifetime: int) -> None:
    response.set_cookie(
        name,
        value,
        max_age=lifetime,
        httponly=True,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
        path="/" if name == ACCESS_COOKIE else "/api/auth/",
    )


def _delete_cookie(response, name: str) -> None:
    response.delete_cookie(name, path="/" if name == ACCESS_COOKIE else "/api/auth/")


class LoginView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def post(self, request):
        s = LoginSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = authenticate(request, email=s.validated_data["email"], password=s.validated_data["password"])
        if user is None or not user.is_active:
            return Response({"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        resp = Response(UserSerializer(user).data)
        _set_cookie(resp, ACCESS_COOKIE, str(refresh.access_token), settings.JWT_ACCESS_LIFETIME)
        _set_cookie(resp, REFRESH_COOKIE, str(refresh), settings.JWT_REFRESH_LIFETIME)
        return resp


class LogoutView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def post(self, request):
        raw_refresh = request.COOKIES.get(REFRESH_COOKIE)
        if raw_refresh:
            try:
                RefreshToken(raw_refresh).blacklist()
            except TokenError:
                pass
        resp = Response(status=status.HTTP_204_NO_CONTENT)
        _delete_cookie(resp, ACCESS_COOKIE)
        _delete_cookie(resp, REFRESH_COOKIE)
        return resp


class RefreshView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def post(self, request):
        from django.contrib.auth import get_user_model

        raw_refresh = request.COOKIES.get(REFRESH_COOKIE)
        if not raw_refresh:
            return Response({"detail": "No refresh cookie."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            old = RefreshToken(raw_refresh)
        except (InvalidToken, TokenError):
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = old["user_id"]
        try:
            old.blacklist()
        except TokenError:
            pass

        user = get_user_model().objects.get(pk=user_id)
        new_refresh = RefreshToken.for_user(user)
        resp = Response({"detail": "ok"})
        _set_cookie(resp, ACCESS_COOKIE, str(new_refresh.access_token), settings.JWT_ACCESS_LIFETIME)
        _set_cookie(resp, REFRESH_COOKIE, str(new_refresh), settings.JWT_REFRESH_LIFETIME)
        return resp


class MeView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response(UserSerializer(request.user).data)
```

- [ ] **Step 5: Implement `user_accounts/urls.py`**

```python
from django.urls import path

from .views import LoginView, LogoutView, MeView, RefreshView

urlpatterns = [
    path("login", LoginView.as_view()),
    path("logout", LogoutView.as_view()),
    path("refresh", RefreshView.as_view()),
    path("me", MeView.as_view()),
]
```

- [ ] **Step 6: Run tests — all pass**

```bash
pytest tests/test_auth.py -v
# Expected: 7 passed
```

- [ ] **Step 7: Commit**

```bash
git add user_accounts/serializers.py user_accounts/views.py user_accounts/urls.py tests/test_auth.py
git commit -m "feat(auth): cookie-based login/logout/refresh/me endpoints with tests"
```

---

## Phase E — Invites

### Task E1: Invite model

**Files:**
- Create: `user_accounts/invite_models.py`

- [ ] **Step 1: Write the model**

```python
import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


def _generate_token() -> str:
    return secrets.token_urlsafe(32)


def _default_expiry():
    return timezone.now() + timedelta(days=settings.INVITE_TTL_DAYS)


class Invite(models.Model):
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, default=_generate_token)
    invited_by = models.ForeignKey("user_accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name="invites_sent")
    expires_at = models.DateTimeField(default=_default_expiry)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def is_valid(self) -> bool:
        return self.accepted_at is None and self.expires_at > timezone.now()

    def __str__(self) -> str:
        return f"Invite<{self.email}>"
```

- [ ] **Step 2: Add to `user_accounts/models.py` re-export so admin can find it**

Append at the bottom of `user_accounts/models.py`:

```python
from .invite_models import Invite  # noqa: E402, F401
```

- [ ] **Step 3: Make migrations**

```bash
source venv/bin/activate
python manage.py makemigrations user_accounts
python manage.py migrate
```

- [ ] **Step 4: Commit**

```bash
git add user_accounts/invite_models.py user_accounts/models.py user_accounts/migrations/
git commit -m "feat(invites): Invite model with token + expiry"
```

### Task E2: Invite endpoints — TDD

**Files:**
- Create: `tests/test_invites.py`
- Create: `user_accounts/invite_serializers.py`
- Create: `user_accounts/invite_views.py`
- Create: `user_accounts/invite_urls.py`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_invites.py
import pytest
from django.core import mail
from django.utils import timezone

from user_accounts.invite_models import Invite

@pytest.mark.django_db
def test_admin_can_create_invite_and_email_is_sent(admin_client, organization):
    mail.outbox.clear()
    r = admin_client.post("/api/invites", {"email": "new@example.com"}, format="json")
    assert r.status_code == 201, r.content
    body = r.json()
    assert body["email"] == "new@example.com"
    assert "token" not in body  # token never returned to admin

    invite = Invite.objects.get(email="new@example.com")
    assert invite.is_valid()
    assert len(mail.outbox) == 1
    assert "new@example.com" in mail.outbox[0].to
    assert invite.token in mail.outbox[0].body

@pytest.mark.django_db
def test_member_cannot_create_invite(member_client):
    r = member_client.post("/api/invites", {"email": "x@example.com"}, format="json")
    assert r.status_code == 403

@pytest.mark.django_db
def test_admin_lists_invites(admin_client, admin_user):
    Invite.objects.create(email="a@example.com", invited_by=admin_user)
    Invite.objects.create(email="b@example.com", invited_by=admin_user)
    r = admin_client.get("/api/invites")
    assert r.status_code == 200
    assert len(r.json()["results"]) == 2

@pytest.mark.django_db
def test_admin_revokes_invite(admin_client, admin_user):
    inv = Invite.objects.create(email="x@example.com", invited_by=admin_user)
    r = admin_client.delete(f"/api/invites/{inv.id}")
    assert r.status_code == 204
    assert not Invite.objects.filter(pk=inv.pk).exists()

@pytest.mark.django_db
def test_get_invite_by_token_public(api_client, admin_user):
    inv = Invite.objects.create(email="z@example.com", invited_by=admin_user)
    r = api_client.get(f"/api/invites/by-token/{inv.token}")
    assert r.status_code == 200
    assert r.json()["email"] == "z@example.com"

@pytest.mark.django_db
def test_get_invite_by_token_expired(api_client, admin_user):
    from datetime import timedelta
    inv = Invite.objects.create(email="z@example.com", invited_by=admin_user)
    inv.expires_at = timezone.now() - timedelta(days=1)
    inv.save(update_fields=["expires_at"])
    r = api_client.get(f"/api/invites/by-token/{inv.token}")
    assert r.status_code == 410  # Gone

@pytest.mark.django_db
def test_accept_invite_creates_user_and_logs_in(api_client, admin_user):
    inv = Invite.objects.create(email="newuser@example.com", invited_by=admin_user)
    r = api_client.post(
        f"/api/invites/by-token/{inv.token}/accept",
        {"password": "newuserpass123", "display_name": "New User"},
        format="json",
    )
    assert r.status_code == 200, r.content
    from user_accounts.authentication import ACCESS_COOKIE
    assert ACCESS_COOKIE in r.cookies
    inv.refresh_from_db()
    assert inv.accepted_at is not None
    from django.contrib.auth import get_user_model
    User = get_user_model()
    u = User.objects.get(email="newuser@example.com")
    assert u.check_password("newuserpass123")
    assert u.role == User.Role.MEMBER

@pytest.mark.django_db
def test_accept_invite_rejected_if_already_accepted(api_client, admin_user):
    inv = Invite.objects.create(email="x@example.com", invited_by=admin_user, accepted_at=timezone.now())
    r = api_client.post(
        f"/api/invites/by-token/{inv.token}/accept",
        {"password": "p", "display_name": "x"},
        format="json",
    )
    assert r.status_code == 410
```

- [ ] **Step 2: Run — should all fail**

```bash
pytest tests/test_invites.py -v
# Expected: all fail (404 / route missing)
```

- [ ] **Step 3: Implement `user_accounts/invite_serializers.py`**

```python
from rest_framework import serializers

from .invite_models import Invite


class InviteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ("id", "email", "expires_at", "accepted_at", "created_at")
        read_only_fields = ("id", "expires_at", "accepted_at", "created_at")


class InvitePublicSerializer(serializers.ModelSerializer):
    """What the unauthenticated `/by-token/<t>` GET returns."""

    class Meta:
        model = Invite
        fields = ("email", "expires_at")
        read_only_fields = fields


class InviteAcceptSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
    display_name = serializers.CharField(max_length=120)
```

- [ ] **Step 4: Implement `user_accounts/invite_views.py`**

```python
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .authentication import ACCESS_COOKIE, REFRESH_COOKIE
from .invite_models import Invite
from .invite_serializers import InviteAcceptSerializer, InviteCreateSerializer, InvitePublicSerializer
from .permissions import IsAdmin
from .serializers import UserSerializer
from .views import _set_cookie

User = get_user_model()


def _send_invite_email(invite: Invite) -> None:
    accept_url = f"{settings.PUBLIC_BASE_URL}/invite/{invite.token}"
    body = (
        f"You've been invited to Altassian.\n\n"
        f"Accept your invite: {accept_url}\n\n"
        f"Token: {invite.token}\n"
        f"Expires: {invite.expires_at:%Y-%m-%d %H:%M UTC}\n"
    )
    send_mail(
        subject="You're invited to Altassian",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invite.email],
        fail_silently=False,
    )


class InviteListCreateView(generics.ListCreateAPIView):
    serializer_class = InviteCreateSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    queryset = Invite.objects.all()

    def perform_create(self, serializer):
        invite = serializer.save(invited_by=self.request.user)
        _send_invite_email(invite)


class InviteDeleteView(generics.DestroyAPIView):
    serializer_class = InviteCreateSerializer
    permission_classes = (IsAuthenticated, IsAdmin)
    queryset = Invite.objects.all()


class InviteByTokenView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def get(self, request, token):
        invite = get_object_or_404(Invite, token=token)
        if not invite.is_valid():
            return Response({"detail": "Invite expired or already accepted."}, status=status.HTTP_410_GONE)
        return Response(InvitePublicSerializer(invite).data)


class InviteAcceptView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def post(self, request, token):
        invite = get_object_or_404(Invite, token=token)
        if not invite.is_valid():
            return Response({"detail": "Invite expired or already accepted."}, status=status.HTTP_410_GONE)
        s = InviteAcceptSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        with transaction.atomic():
            user = User.objects.create_user(
                email=invite.email,
                password=s.validated_data["password"],
                display_name=s.validated_data["display_name"],
                role=User.Role.MEMBER,
                is_active=True,
            )
            invite.accepted_at = timezone.now()
            invite.save(update_fields=["accepted_at"])

        refresh = RefreshToken.for_user(user)
        resp = Response(UserSerializer(user).data)
        _set_cookie(resp, ACCESS_COOKIE, str(refresh.access_token), settings.JWT_ACCESS_LIFETIME)
        _set_cookie(resp, REFRESH_COOKIE, str(refresh), settings.JWT_REFRESH_LIFETIME)
        return resp
```

- [ ] **Step 5: Implement `user_accounts/invite_urls.py`**

```python
from django.urls import path

from .invite_views import InviteAcceptView, InviteByTokenView, InviteDeleteView, InviteListCreateView

urlpatterns = [
    path("invites", InviteListCreateView.as_view()),
    path("invites/<int:pk>", InviteDeleteView.as_view()),
    path("invites/by-token/<str:token>", InviteByTokenView.as_view()),
    path("invites/by-token/<str:token>/accept", InviteAcceptView.as_view()),
]
```

- [ ] **Step 6: Add `Invite` admin registration**

Append to `user_accounts/admin.py`:

```python
from .invite_models import Invite


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ("email", "invited_by", "expires_at", "accepted_at", "created_at")
    search_fields = ("email",)
    readonly_fields = ("token", "created_at")
```

- [ ] **Step 7: Run tests — pass**

```bash
pytest tests/test_invites.py -v
# Expected: 8 passed
```

- [ ] **Step 8: Commit**

```bash
git add user_accounts/ tests/test_invites.py
git commit -m "feat(invites): create/list/revoke + token lookup + accept (creates user, logs in)"
```

---

## Phase F — Spaces

### Task F1: Space model

**Files:**
- Replace: `spaces/models.py`
- Create/replace: `spaces/apps.py`, `spaces/admin.py`

- [ ] **Step 1: Write `spaces/models.py`**

```python
from django.db import models


class Space(models.Model):
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=64, blank=True, default="")  # emoji or short URL
    position = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        "user_accounts.CustomUser", on_delete=models.SET_NULL, null=True, related_name="spaces_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("position", "name")

    def __str__(self) -> str:
        return self.name
```

- [ ] **Step 2: Write `spaces/apps.py`**

```python
from django.apps import AppConfig


class SpacesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "spaces"
```

- [ ] **Step 3: Write `spaces/admin.py`**

```python
from django.contrib import admin

from .models import Space


@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "position", "created_by", "created_at")
    search_fields = ("slug", "name")
```

- [ ] **Step 4: Migrate**

```bash
source venv/bin/activate
python manage.py makemigrations spaces
python manage.py migrate
```

- [ ] **Step 5: Commit**

```bash
git add spaces/
git commit -m "feat(spaces): Space model"
```

### Task F2: Space endpoints — TDD

**Files:**
- Create: `tests/test_spaces.py`
- Create: `spaces/serializers.py`
- Create: `spaces/views.py`
- Create: `spaces/urls.py`
- Modify: `tests/factories.py` (add SpaceFactory)

- [ ] **Step 1: Add `SpaceFactory` to `tests/factories.py`**

Append:

```python
from spaces.models import Space


class SpaceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Space

    slug = factory.Sequence(lambda n: f"space-{n}")
    name = factory.Sequence(lambda n: f"Space {n}")
```

- [ ] **Step 2: Write tests**

```python
# tests/test_spaces.py
import pytest

from spaces.models import Space
from tests.factories import SpaceFactory


@pytest.mark.django_db
def test_admin_creates_space(admin_client):
    r = admin_client.post(
        "/api/spaces/",
        {"slug": "eng", "name": "Engineering", "description": "All things engineering"},
        format="json",
    )
    assert r.status_code == 201, r.content
    assert Space.objects.filter(slug="eng").exists()


@pytest.mark.django_db
def test_member_cannot_create_space(member_client):
    r = member_client.post("/api/spaces/", {"slug": "x", "name": "X"}, format="json")
    assert r.status_code == 403


@pytest.mark.django_db
def test_anyone_authed_lists_spaces(member_client):
    SpaceFactory(slug="eng", name="Eng")
    SpaceFactory(slug="prod", name="Prod")
    r = member_client.get("/api/spaces/")
    assert r.status_code == 200
    slugs = {s["slug"] for s in r.json()["results"]}
    assert slugs == {"eng", "prod"}


@pytest.mark.django_db
def test_unauthed_cannot_list_spaces(api_client):
    r = api_client.get("/api/spaces/")
    assert r.status_code == 401


@pytest.mark.django_db
def test_space_detail_includes_page_tree_field(member_client):
    s = SpaceFactory(slug="eng")
    r = member_client.get(f"/api/spaces/{s.slug}/")
    assert r.status_code == 200
    body = r.json()
    assert body["slug"] == "eng"
    assert "pages" in body  # tree present (empty list at this point)


@pytest.mark.django_db
def test_admin_updates_space(admin_client):
    s = SpaceFactory(slug="eng", name="Old")
    r = admin_client.patch(f"/api/spaces/{s.slug}/", {"name": "New"}, format="json")
    assert r.status_code == 200
    s.refresh_from_db()
    assert s.name == "New"


@pytest.mark.django_db
def test_admin_deletes_space(admin_client):
    s = SpaceFactory(slug="eng")
    r = admin_client.delete(f"/api/spaces/{s.slug}/")
    assert r.status_code == 204
    assert not Space.objects.filter(slug="eng").exists()
```

- [ ] **Step 3: Run — all fail**

```bash
pytest tests/test_spaces.py -v
# Expected: all fail
```

- [ ] **Step 4: Implement `spaces/serializers.py`**

```python
from rest_framework import serializers

from .models import Space


class SpaceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Space
        fields = ("id", "slug", "name", "description", "icon", "position", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class SpaceDetailSerializer(SpaceListSerializer):
    pages = serializers.SerializerMethodField()

    class Meta(SpaceListSerializer.Meta):
        fields = SpaceListSerializer.Meta.fields + ("pages",)

    def get_pages(self, obj):
        # Imported here to avoid circular import.
        from pages.serializers import PageTreeNodeSerializer
        roots = obj.page_set.filter(parent__isnull=True, deleted_at__isnull=True).order_by("position", "id")
        return PageTreeNodeSerializer(roots, many=True).data
```

> **Note:** `obj.page_set` works only after `pages.Page` exists with `space = ForeignKey(Space)`. We add that in Phase G; tests for the page tree pass at the end of Phase G. Until then, `pages` will return `[]` because `page_set` is empty (the `pages` app already has Page from before; we'll rebuild it).

- [ ] **Step 5: Implement `spaces/views.py`**

```python
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user_accounts.permissions import IsAdmin

from .models import Space
from .serializers import SpaceDetailSerializer, SpaceListSerializer


class SpaceViewSet(viewsets.ModelViewSet):
    queryset = Space.objects.all()
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return SpaceDetailSerializer
        return SpaceListSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
```

- [ ] **Step 6: Implement `spaces/urls.py`**

```python
from rest_framework.routers import DefaultRouter

from .views import SpaceViewSet

router = DefaultRouter(trailing_slash=True)
router.register("", SpaceViewSet, basename="space")

urlpatterns = router.urls
```

- [ ] **Step 7: Run tests**

```bash
pytest tests/test_spaces.py -v
# Expected: 7 passed (page tree test passes because page_set is empty)
```

- [ ] **Step 8: Commit**

```bash
git add spaces/ tests/test_spaces.py tests/factories.py
git commit -m "feat(spaces): list/create/detail/update/delete with admin gating"
```

---

## Phase G — Pages, markdown rendering, version history

This phase is the core of the app and the largest. Done in three steps: model + rendering, page CRUD, version history.

### Task G1: Markdown renderer + tests

**Files:**
- Create: `pages/rendering.py`
- Create: `tests/test_rendering.py`

- [ ] **Step 1: Write the test**

```python
# tests/test_rendering.py
from pages.rendering import markdown_to_html


def test_renders_basic_markdown():
    out = markdown_to_html("# Hello\n\nWorld")
    assert "<h1>Hello</h1>" in out
    assert "<p>World</p>" in out


def test_renders_gfm_table():
    md = "| a | b |\n|---|---|\n| 1 | 2 |\n"
    out = markdown_to_html(md)
    assert "<table>" in out
    assert "<td>1</td>" in out


def test_renders_task_list():
    out = markdown_to_html("- [x] done\n- [ ] todo\n")
    assert 'type="checkbox"' in out


def test_strikethrough():
    assert "<s>" in markdown_to_html("~~gone~~")


def test_escapes_raw_html_to_prevent_xss():
    out = markdown_to_html("<script>alert(1)</script>")
    assert "<script>" not in out
```

- [ ] **Step 2: Run — should fail (module missing)**

```bash
pytest tests/test_rendering.py -v
# Expected: ImportError
```

- [ ] **Step 3: Implement `pages/rendering.py`**

```python
"""Server-side Markdown → HTML rendering.

Single source of truth for the rendered HTML stored in body_html_cache.
The frontend's react-markdown renders the editor preview only — final view
uses this output to keep parity.
"""
from markdown_it import MarkdownIt
from mdit_py_plugins.tasklists import tasklists_plugin


def _build_renderer() -> MarkdownIt:
    md = MarkdownIt("gfm-like", {"html": False, "linkify": True, "typographer": True})
    md.use(tasklists_plugin, enabled=True)
    md.enable("table")
    md.enable("strikethrough")
    return md


_RENDERER = _build_renderer()


def markdown_to_html(text: str) -> str:
    if not text:
        return ""
    return _RENDERER.render(text)
```

- [ ] **Step 4: Run — pass**

```bash
pytest tests/test_rendering.py -v
# Expected: 5 passed
```

- [ ] **Step 5: Commit**

```bash
git add pages/rendering.py tests/test_rendering.py
git commit -m "feat(pages): markdown renderer (gfm tables, task lists, strike, html-safe)"
```

### Task G2: Page, PageVersion, Comment, Attachment models

**Files:**
- Replace: `pages/models.py`
- Replace: `pages/apps.py`, `pages/admin.py`

- [ ] **Step 1: Write `pages/models.py`**

```python
import uuid

from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils.text import slugify


def _attachment_path(instance: "Attachment", filename: str) -> str:
    return f"attachments/{uuid.uuid4()}/{filename}"


class Page(models.Model):
    space = models.ForeignKey("spaces.Space", on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    slug = models.SlugField(max_length=220)
    title = models.CharField(max_length=200)
    body_md = models.TextField(blank=True, default="")
    body_html_cache = models.TextField(blank=True, default="")
    position = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "user_accounts.CustomUser", on_delete=models.CASCADE, related_name="pages_created"
    )
    updated_by = models.ForeignKey(
        "user_accounts.CustomUser", on_delete=models.CASCADE, related_name="pages_updated"
    )
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("space", "slug"),
                condition=models.Q(deleted_at__isnull=True),
                name="unique_active_page_slug_per_space",
            )
        ]
        indexes = [GinIndex(fields=("search_vector",), name="page_search_vector_gin")]
        ordering = ("position", "id")

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "page"
            candidate = base
            i = 2
            while (
                Page.objects.filter(space=self.space, slug=candidate, deleted_at__isnull=True)
                .exclude(pk=self.pk)
                .exists()
            ):
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class PageVersion(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="versions")
    version_n = models.IntegerField()
    body_md = models.TextField()
    edited_by = models.ForeignKey("user_accounts.CustomUser", on_delete=models.CASCADE)
    change_summary = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("page", "version_n"), name="unique_page_version")]
        ordering = ("-version_n",)

    def __str__(self) -> str:
        return f"v{self.version_n} of {self.page_id}"


class Comment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey("user_accounts.CustomUser", on_delete=models.CASCADE)
    body_md = models.TextField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="replies")
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self) -> str:
        return self.body_md[:30]


class Attachment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to=_attachment_path)
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=128, default="application/octet-stream")
    size_bytes = models.BigIntegerField(default=0)
    uploaded_by = models.ForeignKey("user_accounts.CustomUser", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.original_filename
```

- [ ] **Step 2: Write `pages/apps.py`**

```python
from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pages"

    def ready(self) -> None:
        from . import signals  # noqa: F401
```

- [ ] **Step 3: Write `pages/admin.py`**

```python
from django.contrib import admin

from .models import Attachment, Comment, Page, PageVersion


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("title", "space", "slug", "is_public", "is_draft", "deleted_at", "updated_at")
    search_fields = ("title", "slug")
    list_filter = ("space", "is_public", "is_draft")


@admin.register(PageVersion)
class PageVersionAdmin(admin.ModelAdmin):
    list_display = ("page", "version_n", "edited_by", "created_at")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("page", "author", "created_at", "deleted_at")


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("page", "original_filename", "mime_type", "size_bytes", "uploaded_by", "created_at")
```

- [ ] **Step 4: Implement `pages/signals.py` (empty stub for now; filled in G3)**

```python
"""Post-save signals: html cache, search vector, version recording."""
```

- [ ] **Step 5: Migrate**

```bash
source venv/bin/activate
python manage.py makemigrations pages
python manage.py migrate
```

- [ ] **Step 6: Commit**

```bash
git add pages/
git commit -m "feat(pages): Page, PageVersion, Comment, Attachment models with FTS column + GIN index"
```

### Task G3: Save signal — html cache, search vector, version on body change

**Files:**
- Replace: `pages/signals.py`
- Create: `tests/test_pages_signals.py`

- [ ] **Step 1: Write tests first**

```python
# tests/test_pages_signals.py
import pytest

from pages.models import Page, PageVersion
from tests.factories import SpaceFactory, UserFactory


@pytest.fixture
def make_page(db):
    user = UserFactory()
    space = SpaceFactory()

    def _make(**overrides):
        return Page.objects.create(
            space=space, title=overrides.get("title", "T"),
            body_md=overrides.get("body_md", "# h"),
            created_by=user, updated_by=user,
        )

    return _make


@pytest.mark.django_db
def test_html_cache_populated_on_create(make_page):
    p = make_page(body_md="# Title")
    p.refresh_from_db()
    assert "<h1>Title</h1>" in p.body_html_cache


@pytest.mark.django_db
def test_first_save_creates_version_1(make_page):
    p = make_page(body_md="# v1")
    assert p.versions.count() == 1
    assert p.versions.first().version_n == 1
    assert p.versions.first().body_md == "# v1"


@pytest.mark.django_db
def test_body_change_creates_new_version(make_page):
    p = make_page(body_md="# v1")
    p.body_md = "# v2"
    p.save()
    assert p.versions.count() == 2
    assert p.versions.order_by("version_n").last().body_md == "# v2"


@pytest.mark.django_db
def test_no_version_created_when_body_unchanged(make_page):
    p = make_page(body_md="# same")
    p.title = "different title"
    p.save()
    assert p.versions.count() == 1


@pytest.mark.django_db
def test_search_vector_populated(make_page):
    p = make_page(body_md="alpha beta gamma")
    p.refresh_from_db()
    assert p.search_vector is not None
    # Postgres FTS match
    assert Page.objects.filter(search_vector="gamma").filter(pk=p.pk).exists()
```

- [ ] **Step 2: Run — all fail**

```bash
pytest tests/test_pages_signals.py -v
# Expected: failures (no signal, no html cache, no versions)
```

- [ ] **Step 3: Implement `pages/signals.py`**

```python
"""Post-save signals: html cache, search vector, version recording.

Strategy: pre_save snapshots the prior body_md; post_save renders html,
updates search_vector via SQL, and creates a new PageVersion if body_md changed.
"""
from django.contrib.postgres.search import SearchVector
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Page, PageVersion
from .rendering import markdown_to_html

_PRIOR_BODY_ATTR = "_prior_body_md"


@receiver(pre_save, sender=Page)
def _capture_prior_body(sender, instance: Page, **kwargs):
    if instance.pk:
        try:
            old = Page.objects.only("body_md").get(pk=instance.pk)
            setattr(instance, _PRIOR_BODY_ATTR, old.body_md)
        except Page.DoesNotExist:
            setattr(instance, _PRIOR_BODY_ATTR, None)
    else:
        setattr(instance, _PRIOR_BODY_ATTR, None)


@receiver(post_save, sender=Page)
def _on_page_saved(sender, instance: Page, created: bool, **kwargs):
    new_html = markdown_to_html(instance.body_md or "")
    prior = getattr(instance, _PRIOR_BODY_ATTR, None)
    body_changed = created or (prior != instance.body_md)

    # Update html cache + search vector in one UPDATE without re-triggering signals.
    Page.objects.filter(pk=instance.pk).update(
        body_html_cache=new_html,
        search_vector=SearchVector("title", "body_md", config="english"),
    )

    if body_changed:
        last_n = PageVersion.objects.filter(page=instance).order_by("-version_n").values_list("version_n", flat=True).first()
        next_n = (last_n or 0) + 1
        PageVersion.objects.create(
            page=instance,
            version_n=next_n,
            body_md=instance.body_md or "",
            edited_by=instance.updated_by,
        )
```

- [ ] **Step 4: Run tests — pass**

```bash
pytest tests/test_pages_signals.py -v
# Expected: 5 passed
```

- [ ] **Step 5: Commit**

```bash
git add pages/signals.py tests/test_pages_signals.py
git commit -m "feat(pages): post-save signal for html cache, search vector, version recording"
```

### Task G4: Page CRUD + tree endpoints

**Files:**
- Create: `pages/serializers.py`
- Create: `pages/views.py`
- Create: `pages/urls.py`
- Create: `pages/permissions.py`
- Create: `tests/test_pages.py`
- Modify: `tests/factories.py` (PageFactory)

- [ ] **Step 1: Add `PageFactory` to `tests/factories.py`**

```python
from pages.models import Page


class PageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Page

    space = factory.SubFactory(SpaceFactory)
    title = factory.Sequence(lambda n: f"Page {n}")
    body_md = "# default"
    created_by = factory.SubFactory(UserFactory)
    updated_by = factory.LazyAttribute(lambda o: o.created_by)
```

- [ ] **Step 2: Write tests**

```python
# tests/test_pages.py
import pytest

from pages.models import Page
from tests.factories import PageFactory, SpaceFactory


@pytest.mark.django_db
def test_member_creates_page(member_client, member_user):
    s = SpaceFactory(slug="eng")
    r = member_client.post(
        "/api/pages/",
        {"space": s.id, "title": "Hello", "body_md": "# Hi"},
        format="json",
    )
    assert r.status_code == 201, r.content
    body = r.json()
    assert body["title"] == "Hello"
    assert "<h1>Hi</h1>" in body["body_html"]
    assert body["slug"] == "hello"


@pytest.mark.django_db
def test_unauthed_cannot_create_page(api_client):
    s = SpaceFactory()
    r = api_client.post("/api/pages/", {"space": s.id, "title": "x", "body_md": "x"}, format="json")
    assert r.status_code == 401


@pytest.mark.django_db
def test_page_detail_returns_md_and_html(member_client):
    p = PageFactory(title="T", body_md="# X")
    r = member_client.get(f"/api/pages/{p.id}/")
    assert r.status_code == 200
    body = r.json()
    assert body["body_md"] == "# X"
    assert "<h1>X</h1>" in body["body_html"]


@pytest.mark.django_db
def test_update_page_changes_body_and_creates_version(member_client, member_user):
    p = PageFactory(body_md="# v1", created_by=member_user, updated_by=member_user)
    r = member_client.patch(f"/api/pages/{p.id}/", {"body_md": "# v2"}, format="json")
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.body_md == "# v2"
    assert p.versions.count() == 2


@pytest.mark.django_db
def test_soft_delete_page(member_client, member_user):
    p = PageFactory(created_by=member_user, updated_by=member_user)
    r = member_client.delete(f"/api/pages/{p.id}/")
    assert r.status_code == 204
    p.refresh_from_db()
    assert p.deleted_at is not None


@pytest.mark.django_db
def test_deleted_pages_excluded_from_list(member_client, member_user):
    from django.utils import timezone
    s = SpaceFactory()
    PageFactory(space=s, title="alive", created_by=member_user, updated_by=member_user)
    dead = PageFactory(space=s, title="dead", created_by=member_user, updated_by=member_user)
    Page.objects.filter(pk=dead.pk).update(deleted_at=timezone.now())
    r = member_client.get(f"/api/spaces/{s.slug}/")
    titles = [p["title"] for p in r.json()["pages"]]
    assert "alive" in titles
    assert "dead" not in titles


@pytest.mark.django_db
def test_move_page_changes_parent_and_position(member_client, member_user):
    s = SpaceFactory()
    parent = PageFactory(space=s, created_by=member_user, updated_by=member_user)
    child = PageFactory(space=s, created_by=member_user, updated_by=member_user)
    r = member_client.post(
        f"/api/pages/{child.id}/move",
        {"parent_id": parent.id, "position": 0},
        format="json",
    )
    assert r.status_code == 200
    child.refresh_from_db()
    assert child.parent_id == parent.id
    assert child.position == 0


@pytest.mark.django_db
def test_page_tree_nested_in_space_detail(member_client, member_user):
    s = SpaceFactory()
    root = PageFactory(space=s, title="Root", created_by=member_user, updated_by=member_user)
    PageFactory(space=s, title="Child", parent=root, created_by=member_user, updated_by=member_user)
    r = member_client.get(f"/api/spaces/{s.slug}/")
    assert r.status_code == 200
    pages = r.json()["pages"]
    assert len(pages) == 1
    assert pages[0]["title"] == "Root"
    assert len(pages[0]["children"]) == 1
    assert pages[0]["children"][0]["title"] == "Child"
```

- [ ] **Step 3: Run — all fail**

```bash
pytest tests/test_pages.py -v
# Expected: failures, no pages routes
```

- [ ] **Step 4: Implement `pages/permissions.py`**

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """Members can read; only the page author or an admin can mutate."""

    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_admin or obj.created_by_id == request.user.id
```

> **Note:** v1 spec says "members can edit any page" — but the API endpoint also covers single-author edit/delete protection on _delete_. We'll keep edits open to all members but require admin OR author for delete. (Adjust if you want to harden later.)

- [ ] **Step 5: Implement `pages/serializers.py`**

```python
from rest_framework import serializers

from .models import Page


class PageTreeNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ("id", "slug", "title", "is_draft", "is_public", "position", "children")

    def get_children(self, obj):
        kids = obj.children.filter(deleted_at__isnull=True).order_by("position", "id")
        return PageTreeNodeSerializer(kids, many=True).data


class PageDetailSerializer(serializers.ModelSerializer):
    body_html = serializers.CharField(source="body_html_cache", read_only=True)

    class Meta:
        model = Page
        fields = (
            "id", "space", "parent", "slug", "title", "body_md", "body_html",
            "position", "is_public", "is_draft",
            "created_by", "updated_by", "created_at", "updated_at",
        )
        read_only_fields = (
            "id", "slug", "body_html",
            "created_by", "updated_by", "created_at", "updated_at",
        )


class PageMoveSerializer(serializers.Serializer):
    parent_id = serializers.IntegerField(allow_null=True, required=False)
    position = serializers.IntegerField(required=True)
```

- [ ] **Step 6: Implement `pages/views.py`**

```python
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Page
from .permissions import IsAuthorOrAdminOrReadOnly
from .serializers import PageDetailSerializer, PageMoveSerializer


class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.filter(deleted_at__isnull=True)
    serializer_class = PageDetailSerializer
    permission_classes = (IsAuthenticated, IsAuthorOrAdminOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        page = self.get_object()
        page.deleted_at = timezone.now()
        page.save(update_fields=["deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"], url_path="move")
    def move(self, request, pk=None):
        page = self.get_object()
        s = PageMoveSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        parent_id = s.validated_data.get("parent_id")
        if parent_id is not None:
            parent = get_object_or_404(Page, pk=parent_id, space=page.space, deleted_at__isnull=True)
            if parent.pk == page.pk:
                return Response({"detail": "A page cannot be its own parent."}, status=400)
            page.parent = parent
        else:
            page.parent = None
        page.position = s.validated_data["position"]
        page.updated_by = request.user
        page.save(update_fields=["parent", "position", "updated_by", "updated_at"])
        return Response(PageDetailSerializer(page).data)
```

- [ ] **Step 7: Implement `pages/urls.py`**

```python
from rest_framework.routers import DefaultRouter

from .views import PageViewSet

router = DefaultRouter(trailing_slash=True)
router.register("pages", PageViewSet, basename="page")

urlpatterns = router.urls
```

- [ ] **Step 8: Run tests**

```bash
pytest tests/test_pages.py -v
# Expected: 8 passed
```

- [ ] **Step 9: Commit**

```bash
git add pages/serializers.py pages/views.py pages/urls.py pages/permissions.py tests/test_pages.py tests/factories.py
git commit -m "feat(pages): CRUD + move + nested tree in space detail"
```

---

## Phase H — Page version history

### Task H1: Version list, get, restore endpoints

**Files:**
- Create: `tests/test_versions.py`
- Modify: `pages/views.py` (add actions)
- Modify: `pages/serializers.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_versions.py
import pytest

from tests.factories import PageFactory


@pytest.mark.django_db
def test_versions_listed(member_client, member_user):
    p = PageFactory(body_md="v1", created_by=member_user, updated_by=member_user)
    p.body_md = "v2"; p.save()
    r = member_client.get(f"/api/pages/{p.id}/versions")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 2
    assert {v["version_n"] for v in body} == {1, 2}


@pytest.mark.django_db
def test_get_one_version(member_client, member_user):
    p = PageFactory(body_md="v1", created_by=member_user, updated_by=member_user)
    p.body_md = "v2"; p.save()
    r = member_client.get(f"/api/pages/{p.id}/versions/1")
    assert r.status_code == 200
    assert r.json()["body_md"] == "v1"


@pytest.mark.django_db
def test_restore_version_creates_new_version_with_old_body(member_client, member_user):
    p = PageFactory(body_md="v1", created_by=member_user, updated_by=member_user)
    p.body_md = "v2"; p.save()
    r = member_client.post(f"/api/pages/{p.id}/restore/1")
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.body_md == "v1"
    assert p.versions.count() == 3   # v1, v2, then v3 = restore of v1
```

- [ ] **Step 2: Run — fails (404)**

```bash
pytest tests/test_versions.py -v
```

- [ ] **Step 3: Add `PageVersionSerializer` to `pages/serializers.py`**

Append:

```python
from .models import PageVersion


class PageVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageVersion
        fields = ("id", "version_n", "body_md", "edited_by", "change_summary", "created_at")
        read_only_fields = fields
```

- [ ] **Step 4: Add three new `@action` methods inside the existing `PageViewSet` class in `pages/views.py`**

First, add these imports at the top of `pages/views.py` (next to existing imports):

```python
from .models import Attachment, Comment, Page, PageVersion  # PageVersion is the new addition
from .serializers import (
    AttachmentSerializer,
    CommentSerializer,
    PageDetailSerializer,
    PageMoveSerializer,
    PageVersionSerializer,  # new
)
```

Then, *inside the `PageViewSet` class body* (alongside the existing `move` action, indented one level), add:

```python
    @action(detail=True, methods=["get"], url_path="versions")
    def versions(self, request, pk=None):
        page = self.get_object()
        qs = page.versions.order_by("version_n")
        return Response(PageVersionSerializer(qs, many=True).data)

    @action(detail=True, methods=["get"], url_path=r"versions/(?P<version_n>\d+)")
    def version_detail(self, request, pk=None, version_n=None):
        page = self.get_object()
        v = get_object_or_404(PageVersion, page=page, version_n=int(version_n))
        return Response(PageVersionSerializer(v).data)

    @action(detail=True, methods=["post"], url_path=r"restore/(?P<version_n>\d+)")
    def restore(self, request, pk=None, version_n=None):
        page = self.get_object()
        v = get_object_or_404(PageVersion, page=page, version_n=int(version_n))
        page.body_md = v.body_md
        page.updated_by = request.user
        page.save()  # signal creates a new PageVersion
        return Response(PageDetailSerializer(page).data)
```

> The `Attachment`, `Comment`, `AttachmentSerializer`, `CommentSerializer` references in the import block above are forward-looking — Phases I and J add those classes. Until then, just import what currently exists; you'll re-edit the import in I1 and J1.

- [ ] **Step 5: Run tests — pass**

```bash
pytest tests/test_versions.py -v
# Expected: 3 passed
```

- [ ] **Step 6: Commit**

```bash
git add pages/views.py pages/serializers.py tests/test_versions.py
git commit -m "feat(pages): version list, get, restore actions"
```

---

## Phase I — Comments

### Task I1: Comment endpoints — TDD

**Files:**
- Create: `tests/test_comments.py`
- Modify: `pages/serializers.py` (CommentSerializer)
- Modify: `pages/views.py` (CommentViewSet)
- Modify: `pages/urls.py` (register)

- [ ] **Step 1: Write tests**

```python
# tests/test_comments.py
import pytest

from pages.models import Comment
from tests.factories import PageFactory, UserFactory


@pytest.mark.django_db
def test_create_comment(member_client, member_user):
    p = PageFactory()
    r = member_client.post(
        f"/api/pages/{p.id}/comments",
        {"body_md": "Looks good"},
        format="json",
    )
    assert r.status_code == 201, r.content
    assert Comment.objects.filter(page=p).count() == 1


@pytest.mark.django_db
def test_threaded_replies(member_client, member_user):
    p = PageFactory()
    parent = Comment.objects.create(page=p, author=member_user, body_md="root")
    r = member_client.post(
        f"/api/pages/{p.id}/comments",
        {"body_md": "reply", "parent": parent.id},
        format="json",
    )
    assert r.status_code == 201
    assert Comment.objects.get(parent=parent).body_md == "reply"


@pytest.mark.django_db
def test_list_comments(member_client, member_user):
    p = PageFactory()
    Comment.objects.create(page=p, author=member_user, body_md="a")
    Comment.objects.create(page=p, author=member_user, body_md="b")
    r = member_client.get(f"/api/pages/{p.id}/comments")
    assert r.status_code == 200
    assert len(r.json()) == 2


@pytest.mark.django_db
def test_author_can_delete_own_comment(member_client, member_user):
    p = PageFactory()
    c = Comment.objects.create(page=p, author=member_user, body_md="own")
    r = member_client.delete(f"/api/comments/{c.id}")
    assert r.status_code == 204
    c.refresh_from_db()
    assert c.deleted_at is not None


@pytest.mark.django_db
def test_member_cannot_delete_others_comment(member_client):
    p = PageFactory()
    other = UserFactory()
    c = Comment.objects.create(page=p, author=other, body_md="other")
    r = member_client.delete(f"/api/comments/{c.id}")
    assert r.status_code == 403


@pytest.mark.django_db
def test_admin_can_delete_any_comment(admin_client):
    p = PageFactory()
    other = UserFactory()
    c = Comment.objects.create(page=p, author=other, body_md="other")
    r = admin_client.delete(f"/api/comments/{c.id}")
    assert r.status_code == 204
```

- [ ] **Step 2: Run — fails**

```bash
pytest tests/test_comments.py -v
```

- [ ] **Step 3: Add `CommentSerializer` to `pages/serializers.py`** (append)

```python
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "page", "author", "body_md", "parent", "created_at", "deleted_at")
        read_only_fields = ("id", "author", "created_at", "deleted_at")
```

- [ ] **Step 4: Add comment views to `pages/views.py`** (append, with imports updated)

```python
from rest_framework.exceptions import PermissionDenied

from .models import Comment
from .serializers import CommentSerializer


class CommentListCreateView(viewsets.GenericViewSet):
    """Custom small viewset for the nested page → comments route."""
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def list(self, request, page_pk=None):
        qs = Comment.objects.filter(page_id=page_pk, deleted_at__isnull=True).select_related("author")
        return Response(CommentSerializer(qs, many=True).data)

    def create(self, request, page_pk=None):
        page = get_object_or_404(Page, pk=page_pk, deleted_at__isnull=True)
        s = CommentSerializer(data={**request.data, "page": page.id})
        s.is_valid(raise_exception=True)
        s.save(author=request.user, page=page)
        return Response(s.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def destroy(self, request, pk=None):
        c = get_object_or_404(Comment, pk=pk, deleted_at__isnull=True)
        if not (request.user.is_admin or c.author_id == request.user.id):
            raise PermissionDenied()
        c.deleted_at = timezone.now()
        c.save(update_fields=["deleted_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
```

- [ ] **Step 5: Wire URLs in `pages/urls.py`**

Replace the file:

```python
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CommentDeleteView,
    CommentListCreateView,
    PageViewSet,
)

router = DefaultRouter(trailing_slash=True)
router.register("pages", PageViewSet, basename="page")

urlpatterns = router.urls + [
    path("pages/<int:page_pk>/comments", CommentListCreateView.as_view({"get": "list", "post": "create"})),
    path("comments/<int:pk>", CommentDeleteView.as_view({"delete": "destroy"})),
]
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_comments.py -v
# Expected: 6 passed
```

- [ ] **Step 7: Commit**

```bash
git add pages/serializers.py pages/views.py pages/urls.py tests/test_comments.py
git commit -m "feat(comments): list/create + author/admin soft-delete"
```

---

## Phase J — Attachments

### Task J1: Attachment upload + delete

**Files:**
- Create: `tests/test_attachments.py`
- Modify: `pages/serializers.py`
- Modify: `pages/views.py`
- Modify: `pages/urls.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_attachments.py
import io

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from pages.models import Attachment
from tests.factories import PageFactory, UserFactory


@pytest.mark.django_db
def test_upload_attachment(member_client, member_user, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    p = PageFactory(created_by=member_user, updated_by=member_user)
    f = SimpleUploadedFile("hi.txt", b"hello", content_type="text/plain")
    r = member_client.post(f"/api/pages/{p.id}/attachments", {"file": f}, format="multipart")
    assert r.status_code == 201, r.content
    body = r.json()
    assert body["original_filename"] == "hi.txt"
    assert Attachment.objects.filter(page=p).count() == 1


@pytest.mark.django_db
def test_uploader_can_delete_own_attachment(member_client, member_user, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    p = PageFactory(created_by=member_user, updated_by=member_user)
    a = Attachment.objects.create(
        page=p, file=SimpleUploadedFile("x.txt", b"x"),
        original_filename="x.txt", uploaded_by=member_user,
    )
    r = member_client.delete(f"/api/attachments/{a.id}")
    assert r.status_code == 204
    assert not Attachment.objects.filter(pk=a.pk).exists()


@pytest.mark.django_db
def test_member_cannot_delete_others_attachment(member_client, tmp_path, settings):
    settings.MEDIA_ROOT = tmp_path
    other = UserFactory()
    p = PageFactory()
    a = Attachment.objects.create(
        page=p, file=SimpleUploadedFile("x.txt", b"x"),
        original_filename="x.txt", uploaded_by=other,
    )
    r = member_client.delete(f"/api/attachments/{a.id}")
    assert r.status_code == 403
```

- [ ] **Step 2: Run — fails**

```bash
pytest tests/test_attachments.py -v
```

- [ ] **Step 3: Add `AttachmentSerializer` to `pages/serializers.py`**

```python
from .models import Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ("id", "page", "file_url", "original_filename", "mime_type", "size_bytes", "uploaded_by", "created_at")
        read_only_fields = ("id", "page", "file_url", "uploaded_by", "created_at", "original_filename", "mime_type", "size_bytes")

    def get_file_url(self, obj):
        request = self.context.get("request")
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return obj.file.url if obj.file else ""
```

- [ ] **Step 4: Add attachment views to `pages/views.py`**

```python
from .models import Attachment
from .serializers import AttachmentSerializer


class AttachmentUploadView(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AttachmentSerializer

    def create(self, request, page_pk=None):
        page = get_object_or_404(Page, pk=page_pk, deleted_at__isnull=True)
        f = request.FILES.get("file")
        if not f:
            return Response({"detail": "No file uploaded."}, status=400)
        att = Attachment.objects.create(
            page=page,
            file=f,
            original_filename=f.name,
            mime_type=f.content_type or "application/octet-stream",
            size_bytes=f.size,
            uploaded_by=request.user,
        )
        return Response(
            AttachmentSerializer(att, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class AttachmentDeleteView(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = AttachmentSerializer

    def destroy(self, request, pk=None):
        a = get_object_or_404(Attachment, pk=pk)
        if not (request.user.is_admin or a.uploaded_by_id == request.user.id):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied()
        a.file.delete(save=False)
        a.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

- [ ] **Step 5: Wire URLs in `pages/urls.py`**

Append:

```python
urlpatterns += [
    path("pages/<int:page_pk>/attachments", AttachmentUploadView.as_view({"post": "create"})),
    path("attachments/<int:pk>", AttachmentDeleteView.as_view({"delete": "destroy"})),
]
```

(Update the import line for views accordingly.)

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_attachments.py -v
# Expected: 3 passed
```

- [ ] **Step 7: Commit**

```bash
git add pages/serializers.py pages/views.py pages/urls.py tests/test_attachments.py
git commit -m "feat(attachments): upload + uploader/admin delete"
```

---

## Phase K — Search (Postgres FTS)

### Task K1: `/api/search` endpoint

**Files:**
- Create: `search/views.py`
- Create: `search/urls.py`
- Create: `search/apps.py`
- Create: `tests/test_search.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_search.py
import pytest

from tests.factories import PageFactory, SpaceFactory


@pytest.mark.django_db
def test_search_returns_pages_matching_body(member_client, member_user):
    s1 = SpaceFactory()
    PageFactory(space=s1, title="Auth design", body_md="JWT cookies are great", created_by=member_user, updated_by=member_user)
    PageFactory(space=s1, title="Random", body_md="apples and bananas", created_by=member_user, updated_by=member_user)
    r = member_client.get("/api/search/?q=jwt")
    assert r.status_code == 200
    titles = [p["title"] for p in r.json()["results"]]
    assert titles == ["Auth design"]


@pytest.mark.django_db
def test_search_results_include_snippet_and_rank(member_client, member_user):
    s = SpaceFactory()
    PageFactory(space=s, title="Auth", body_md="JWT cookie security", created_by=member_user, updated_by=member_user)
    r = member_client.get("/api/search/?q=cookie")
    res = r.json()["results"][0]
    assert "snippet_html" in res
    assert "rank" in res
    assert "<b>" in res["snippet_html"] or "cookie" in res["snippet_html"].lower()


@pytest.mark.django_db
def test_search_filters_by_space(member_client, member_user):
    s1 = SpaceFactory(slug="eng")
    s2 = SpaceFactory(slug="prod")
    PageFactory(space=s1, title="A", body_md="alpha thing", created_by=member_user, updated_by=member_user)
    PageFactory(space=s2, title="B", body_md="alpha thing", created_by=member_user, updated_by=member_user)
    r = member_client.get("/api/search/?q=alpha&space=eng")
    titles = {p["title"] for p in r.json()["results"]}
    assert titles == {"A"}


@pytest.mark.django_db
def test_search_excludes_deleted_pages(member_client, member_user):
    from pages.models import Page
    from django.utils import timezone
    s = SpaceFactory()
    p = PageFactory(space=s, title="findme", body_md="alpha", created_by=member_user, updated_by=member_user)
    Page.objects.filter(pk=p.pk).update(deleted_at=timezone.now())
    r = member_client.get("/api/search/?q=alpha")
    assert r.json()["results"] == []


@pytest.mark.django_db
def test_search_unauthed_rejected(api_client):
    r = api_client.get("/api/search/?q=x")
    assert r.status_code == 401
```

- [ ] **Step 2: Run — fails**

```bash
pytest tests/test_search.py -v
```

- [ ] **Step 3: Implement `search/apps.py`**

```python
from django.apps import AppConfig


class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "search"
```

- [ ] **Step 4: Implement `search/views.py`**

```python
from django.contrib.postgres.search import SearchHeadline, SearchQuery, SearchRank
from django.db.models import F
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from pages.models import Page


class SearchView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        space_slug = request.query_params.get("space")
        if not q:
            return Response({"results": []})

        query = SearchQuery(q, config="english")
        qs = Page.objects.filter(deleted_at__isnull=True, search_vector=query)
        if space_slug:
            qs = qs.filter(space__slug=space_slug)
        qs = (
            qs.annotate(rank=SearchRank(F("search_vector"), query))
            .annotate(
                snippet_html=SearchHeadline(
                    "body_md", query, config="english",
                    start_sel="<b>", stop_sel="</b>", max_words=30, min_words=15,
                )
            )
            .select_related("space")
            .order_by("-rank")[:20]
        )

        results = [
            {
                "page_id": p.id,
                "space_slug": p.space.slug,
                "page_slug": p.slug,
                "title": p.title,
                "snippet_html": p.snippet_html,
                "rank": float(p.rank),
            }
            for p in qs
        ]
        return Response({"results": results})
```

- [ ] **Step 5: Implement `search/urls.py`**

```python
from django.urls import path

from .views import SearchView

urlpatterns = [path("", SearchView.as_view())]
```

- [ ] **Step 6: Make sure `search/__init__.py` and `search/migrations/__init__.py` exist**

```bash
touch search/__init__.py search/migrations/__init__.py 2>/dev/null
mkdir -p search/migrations
touch search/migrations/__init__.py
```

- [ ] **Step 7: Run tests**

```bash
pytest tests/test_search.py -v
# Expected: 5 passed
```

- [ ] **Step 8: Commit**

```bash
git add search/ tests/test_search.py
git commit -m "feat(search): /api/search with Postgres FTS, ts_rank, ts_headline, space filter"
```

---

## Phase L — Public page read

### Task L1: `public_api` app + tests

**Files:**
- Create: `public_api/__init__.py`, `public_api/apps.py`, `public_api/views.py`, `public_api/urls.py`
- Create: `tests/test_public.py`

- [ ] **Step 1: Write tests**

```python
# tests/test_public.py
import pytest

from tests.factories import PageFactory, SpaceFactory


@pytest.mark.django_db
def test_public_page_readable_unauthed(api_client):
    s = SpaceFactory(slug="docs")
    p = PageFactory(space=s, title="Public", body_md="# Hello", is_public=True)
    r = api_client.get(f"/api/public/spaces/{s.slug}/pages/{p.slug}")
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "Public"
    assert "<h1>Hello</h1>" in body["body_html"]


@pytest.mark.django_db
def test_private_page_returns_404_on_public_endpoint(api_client):
    s = SpaceFactory(slug="docs")
    p = PageFactory(space=s, is_public=False)
    r = api_client.get(f"/api/public/spaces/{s.slug}/pages/{p.slug}")
    assert r.status_code == 404


@pytest.mark.django_db
def test_deleted_public_page_returns_404(api_client):
    from pages.models import Page
    from django.utils import timezone
    s = SpaceFactory(slug="docs")
    p = PageFactory(space=s, is_public=True)
    Page.objects.filter(pk=p.pk).update(deleted_at=timezone.now())
    r = api_client.get(f"/api/public/spaces/{s.slug}/pages/{p.slug}")
    assert r.status_code == 404
```

- [ ] **Step 2: Run — fails**

```bash
pytest tests/test_public.py -v
```

- [ ] **Step 3: Implement `public_api/apps.py`**

```python
from django.apps import AppConfig


class PublicApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "public_api"
```

- [ ] **Step 4: Implement `public_api/views.py`**

```python
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from pages.models import Page


class PublicPageView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes: list = []

    def get(self, request, space_slug, page_slug):
        page = get_object_or_404(
            Page,
            space__slug=space_slug,
            slug=page_slug,
            is_public=True,
            deleted_at__isnull=True,
        )
        return Response({
            "title": page.title,
            "body_md": page.body_md,
            "body_html": page.body_html_cache,
            "updated_at": page.updated_at,
        })
```

- [ ] **Step 5: Implement `public_api/urls.py`**

```python
from django.urls import path

from .views import PublicPageView

urlpatterns = [
    path("spaces/<slug:space_slug>/pages/<slug:page_slug>", PublicPageView.as_view()),
]
```

- [ ] **Step 6: Run tests**

```bash
pytest tests/test_public.py -v
# Expected: 3 passed
```

- [ ] **Step 7: Commit**

```bash
git add public_api/ tests/test_public.py
git commit -m "feat(public): /api/public/spaces/<s>/pages/<p> for is_public pages"
```

---

## Phase M — Final wiring

### Task M1: Run the full suite

- [ ] **Step 1: Run all tests**

```bash
source venv/bin/activate
pytest -v
# Expected: every test passes. Should be ~50+ tests across all files.
```

- [ ] **Step 2: If any failure, fix; do not proceed until all green.**

### Task M2: `seed_demo` management command (helpful for manual smoke + demos)

**Files:**
- Create: `user_accounts/management/commands/seed_demo.py`

- [ ] **Step 1: Write the command**

```python
from django.core.management.base import BaseCommand
from django.db import transaction

from pages.models import Page
from spaces.models import Space
from user_accounts.models import CustomUser, Organization


class Command(BaseCommand):
    help = "Seed a demo org with admin + member, two spaces, a few pages. Idempotent."

    def handle(self, *args, **opts):
        with transaction.atomic():
            org, _ = Organization.objects.get_or_create(pk=1, defaults={"name": "Altassian Demo"})
            admin, _ = CustomUser.objects.get_or_create(
                email="admin@altassian.local",
                defaults={
                    "display_name": "Admin",
                    "role": CustomUser.Role.ADMIN,
                    "is_staff": True,
                    "is_superuser": True,
                    "is_active": True,
                },
            )
            admin.set_password("adminpass123"); admin.save()

            member, _ = CustomUser.objects.get_or_create(
                email="alice@altassian.local",
                defaults={"display_name": "Alice", "role": CustomUser.Role.MEMBER, "is_active": True},
            )
            member.set_password("alicepass123"); member.save()

            eng, _ = Space.objects.get_or_create(slug="eng", defaults={"name": "Engineering", "created_by": admin})
            prod, _ = Space.objects.get_or_create(slug="prod", defaults={"name": "Product", "created_by": admin})

            for space, title, body in [
                (eng, "Architecture", "# Architecture\n\nDjango + Next.js."),
                (eng, "Onboarding", "# Onboarding\n\nWelcome aboard."),
                (prod, "Roadmap", "# Roadmap\n\n- [ ] ship MVP\n- [ ] dogfood\n"),
            ]:
                Page.objects.get_or_create(
                    space=space, slug=title.lower(),
                    defaults={"title": title, "body_md": body, "created_by": admin, "updated_by": admin},
                )

            self.stdout.write(self.style.SUCCESS("Seeded. Login admin@altassian.local / adminpass123."))
```

- [ ] **Step 2: Run it once to verify**

```bash
source venv/bin/activate
python manage.py seed_demo
# Expected: "Seeded. ..."
```

- [ ] **Step 3: Commit**

```bash
git add user_accounts/management/commands/seed_demo.py
git commit -m "chore: seed_demo management command for local dogfooding"
```

### Task M3: Rewrite `README.md`

**Files:**
- Replace: `README.md`

- [ ] **Step 1: Write a concise README**

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for new MVP shape"
```

### Task M4: Final verification

- [ ] **Step 1: Run full test suite green**

```bash
source venv/bin/activate
pytest -v
# Expected: all tests pass.
```

- [ ] **Step 2: Boot dev server and hit the API once**

```bash
python manage.py runserver 0.0.0.0:8000 &
SERVER_PID=$!
sleep 3
curl -i -s http://localhost:8000/api/auth/login -d '{"email":"admin@altassian.local","password":"adminpass123"}' -H 'Content-Type: application/json' | head -20
kill $SERVER_PID
# Expected: 200 OK with Set-Cookie altassian_access=... and altassian_refresh=...
```

- [ ] **Step 3: Tag the milestone**

```bash
git tag backend-mvp-v0.1
```

---

## Self-Review (run when plan complete)

**Spec coverage map:**

| Spec section | Implementing task(s) |
|---|---|
| Auth: login/logout/refresh/me, JWT cookies | D1 |
| Invite-only signup | E1, E2 |
| Singleton Organization, first-admin bootstrap | C1, C7 |
| Spaces CRUD, admin-gated mutations | F1, F2 |
| Pages CRUD, slug autogeneration, soft-delete | G2, G4 |
| Page tree (nested in space detail) | G4 (space tree comes via `pages` field on `SpaceDetailSerializer`) |
| Page move/reorder | G4 |
| Page versions (auto on body change), restore | G3, H1 |
| Markdown → HTML server-side, cached | G1, G3 |
| Comments threaded, soft-delete, author/admin perms | I1 |
| Attachments upload + delete (uploader/admin) | J1 |
| Postgres FTS search with rank + snippet, space filter | K1, G3 (vector population) |
| Public page endpoint (no auth) | L1 |
| Cleanup of openclaw cruft | A1–A7 |
| Postgres-only (no SQLite) | A4, A5, B1 |
| `.env.example` with prod-shaped values | B2 |
| `pyproject.toml` (vs requirements.txt) | A6 |
| pytest test infra | A7, C4 |

**Out of scope (intentionally not in this plan):** Next.js frontend, GCP LB config, Dockerfile for prod (Plans 2 and 3).
