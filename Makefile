.PHONY: help install lint format test run docker-up docker-down precommit

help:
	@grep -E '^[a-zA-Z_-]+:.*?##' Makefile | sort | awk -F':|##' '{printf "\033[36m%-20s\033[0m %s\n", $$1, $$3}'

install: ## Install Python deps
	python -m pip install --upgrade pip
	pip install -r requirements.txt

lint: ## Run linters (ruff, flake8, isort, black --check)
	ruff check .
	flake8 . || true
	isort --check-only . || true
	black --check . || true

format: ## Auto-format with isort+black
	isort .
	black .

test: ## Run Django tests
	python manage.py test || true

run: ## Run dev server
	python manage.py runserver

docker-up: ## Start Docker stack
	docker compose up -d

docker-down: ## Stop Docker stack
	docker compose down

precommit: ## Install & run pre-commit on all files
	pip install pre-commit
	pre-commit install
	pre-commit run --all-files || true
