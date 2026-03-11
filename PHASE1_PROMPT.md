You are building Altassian, a Confluence/wiki clone backend with Django + DRF.

CRITICAL FIRST: settings.py may be corrupted or misconfigured. Restore a complete Django settings.py with:
- SECRET_KEY, DEBUG=True, ALLOWED_HOSTS=["*"]
- INSTALLED_APPS including django.contrib.*, rest_framework, corsheaders, django_filters, spaces, pages, user_accounts (not accounts)
- AUTH_USER_MODEL = "user_accounts.CustomUser"
- REST_FRAMEWORK with JWT default auth, pagination (PageNumberPagination, page_size=20), filter backends
- SIMPLE_JWT config (access=60min, refresh=7days)
- CORS_ALLOW_ALL_ORIGINS=True (dev mode)
- MEDIA_URL, MEDIA_ROOT, STATIC_URL, STATIC_ROOT
- Middleware including corsheaders.middleware.CorsMiddleware (at the top) and common Django middleware

Then fix the apps:
- Ensure spaces/ and pages/ have __init__.py, apps.py, admin.py, tests.py
- Run makemigrations for ALL apps and migrate (using the venv at ./venv)
- Create serializers with nested relations where appropriate
- Create viewsets with IsAuthenticated permissions, filtering, search, ordering
- Set up URL routing with DRF routers under /api/
- Add JWT auth endpoints (register, login, token refresh, me)
- Add full-text search endpoint using Q objects
- Add page tree endpoint (nested hierarchy per space)
- Add page versioning (auto-create PageVersion on page update)
- Add activity feed endpoint (recent changes across all spaces)
- Register all models in admin.py
- Run the dev server to verify everything works: python manage.py runserver 0.0.0.0:8000
- Git commit after completing

Use the venv at ./venv (activate with: source ./venv/bin/activate). All pip installs go in the venv.

When completely finished, run: openclaw system event --text "Done: Altassian backend complete — all models, APIs, auth, search, versioning working" --mode now
