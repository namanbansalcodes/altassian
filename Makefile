PY=python
MANAGE=$(PY) manage.py

.PHONY: dev test seed fmt lint

dev:
	$(MANAGE) runserver 0.0.0.0:8000

test:
	$(MANAGE) test -v 2

seed:
	$(MANAGE) seed || $(MANAGE) seed_demo || true

fmt:
	black . && isort .

lint:
	flake8 .
