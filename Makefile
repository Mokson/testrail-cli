.PHONY: help install dev test lint format type-check clean pre-commit build publish

help:
	@echo "Available commands:"
	@echo "  make install      Install production dependencies"
	@echo "  make dev          Install development dependencies"
	@echo "  make test         Run test suite with coverage"
	@echo "  make lint         Run linter (ruff)"
	@echo "  make format       Format code with ruff"
	@echo "  make type-check   Run type checker (mypy)"
	@echo "  make clean        Remove build artifacts and cache"
	@echo "  make pre-commit   Install pre-commit hooks"
	@echo "  make build        Build distribution packages"
	@echo "  make publish      Publish to PyPI"

install:
	poetry install --only main

dev:
	poetry install

test:
	poetry run pytest

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

type-check:
	poetry run mypy testrail_cli

clean:
	rm -rf build dist *.egg-info .coverage htmlcov .pytest_cache .mypy_cache .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

pre-commit:
	poetry run pre-commit install

build:
	poetry build

publish:
	poetry publish
