# Contributing — Superpowers-style (TDD, YAGNI, DRY)

This repo follows the Superpowers workflow by obra (https://github.com/obra/superpowers):

- RED-GREEN-REFACTOR: write a failing test first; make it pass; clean up.
- YAGNI/DRY: implement the minimum to satisfy the spec; remove duplication.
- Small tasks: 2–5 min increments, descriptive commits.

## Local dev

- Python 3.11, Django REST + DRF SimpleJWT
- Frontend: Vite + React + Tailwind (Next.js to be added)
- Docker: `docker-compose up --build`

## Commands (Makefile)

- `make dev` — run backend locally
- `make test` — run Django tests
- `make seed` — load demo data
- `make fmt` — format (black, isort)
- `make lint` — flake8

## TDD flow

1. Create/extend a failing test in `user_accounts/tests.py`, `spaces/tests.py`, or `pages/tests.py`.
2. `make test` (watch it fail)
3. Implement the smallest change to pass
4. `make test` (green)
5. Refactor for clarity/DRY
6. Commit: `feat(scope): description` or `test(scope): add failing/green`

## CI

GitHub Actions runs tests on every push/PR (see `.github/workflows/ci.yml`).

## Coding style

- Black, isort, flake8 (line length 100)
- Typed code where practical; docstrings on public functions

## Frontend tests (planned)

- React Testing Library/Jest for components
- Playwright for basic flows (login, create space, create page, history, search)
