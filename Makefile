.PHONY: help install test lint format clean docker-build docker-run setup-dev

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev-install - Install development dependencies"
	@echo "  test        - Run tests with coverage"
	@echo "  test-unit   - Run only unit tests"
	@echo "  test-integration - Run only integration tests"
	@echo "  test-api    - Run only API tests"
	@echo "  test-watch  - Run tests in watch mode"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code with black and isort"
	@echo "  format-check - Check code formatting"
	@echo "  type-check  - Run type checking with mypy"
	@echo "  security    - Run security scans"
	@echo "  quality-check - Run all quality checks"
	@echo "  clean       - Clean up temporary files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run application with Docker Compose"
	@echo "  docker-test - Run tests in Docker"
	@echo "  setup-dev   - Set up development environment"
	@echo "  migrate     - Run database migrations"
	@echo "  upgrade-db  - Upgrade database to latest migration"
	@echo "  serve       - Run development server"
	@echo "  ci-install  - Install dependencies for CI"
	@echo "  ci-test     - Run tests for CI"
	@echo "  ci-quality  - Run quality checks for CI"

# Installation
install:
	pip install --upgrade pip
	pip install -r backend/requirements.txt
	pip install pytest pytest-asyncio pytest-cov httpx flake8 black isort mypy bandit safety

# Testing
test:
	python -m pytest tests/ -v --cov=backend --cov-report=html --cov-report=xml

test-unit:
	python -m pytest tests/ -v -m "unit" --cov=backend

test-integration:
	python -m pytest tests/ -v -m "integration" --cov=backend

test-watch:
	python -m pytest tests/ -v --cov=backend -f

# Code quality
lint:
	flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 backend/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	mypy backend/ --ignore-missing-imports

format:
	black backend/
	isort backend/

format-check:
	black --check --diff backend/
	isort --check-only --diff backend/

# Security
security:
	bandit -r backend/ -f json -o bandit-report.json
	safety check --json --output safety-report.json

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/
	rm -f bandit-report.json safety-report.json coverage.xml

# Docker operations
docker-build:
	docker build -t fastapi-shop-app .

docker-run:
	docker-compose up --build

docker-test:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

docker-down:
	docker-compose down

# Development setup
setup-dev: install
	pre-commit install
	python -m alembic upgrade head

# Database operations
migrate:
	python -m alembic upgrade head

migrate-create:
	python -m alembic revision --autogenerate -m "$(MESSAGE)"

# Development server
serve:
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

# CI/CD helpers
ci-install:
	pip install --upgrade pip
	pip install -r backend/requirements.txt
	pip install pytest pytest-asyncio pytest-cov httpx

ci-test: ci-install
	python -m pytest tests/ -v --cov=backend --cov-report=xml

ci-lint:
	flake8 backend/ --count --select=E9,F63,F7,F82 --show-source --statistics

ci-format-check:
	black --check backend/
	isort --check-only backend/

# All quality checks
check-all: format-check lint security test

# Release helpers
release-patch:
	bump2version patch

release-minor:
	bump2version minor

release-major:
	bump2version major
