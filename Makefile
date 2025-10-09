.PHONY: help install test clean docker-up docker-down run lint format verify

PYTHON := python
PIP := pip
DOCKER_COMPOSE := docker-compose
VENV := venv

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean build files"
	@echo "  make docker-up    - Start Docker"
	@echo "  make docker-down  - Stop Docker"
	@echo "  make run          - Run app"
	@echo "  make verify       - Verify setup"

install:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/$(PIP) install --upgrade pip
	$(VENV)/bin/$(PIP) install -r requirements.txt
	$(VENV)/bin/$(PIP) install -r requirements-dev.txt
	@echo "Installation complete."

test:
	$(VENV)/bin/pytest tests -v

lint:
	$(VENV)/bin/flake8 src/
	$(VENV)/bin/mypy src/

format:
	$(VENV)/bin/black src/ tests/
	$(VENV)/bin/isort src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache dist build *.egg-info

docker-up:
	$(DOCKER_COMPOSE) -f infrastructure/docker/docker-compose.yml up -d

docker-down:
	$(DOCKER_COMPOSE) -f infrastructure/docker/docker-compose.yml down

run:
	$(PYTHON) main.py

verify:
	$(VENV)/bin/python scripts/setup/verify.py
