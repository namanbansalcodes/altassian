Task: Phase 4 — Run backend tests and fix failures.

In this repo:
1) Activate venv: source ./venv/bin/activate
2) Run tests: python manage.py test -v 2
3) Fix any failures (models, serializers, views, permissions). Add/adjust minimal tests if needed.
4) Ensure JWT auth endpoints covered and a basic API smoke test passes.
5) Commit and PUSH after each meaningful change.

When completely finished, run: openclaw system event --text "Done: Phase 4 — Backend tests passing and basic API smoke tests added" --mode now
