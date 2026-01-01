.PHONY: help install format lint type-check quality check clean

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies (including dev dependencies)"
	@echo "  make format        - Format code with Ruff"
	@echo "  make lint          - Lint code with Ruff"
	@echo "  make type-check    - Run type checking with mypy (optional, may have errors)"
	@echo "  make quality       - Run all quality checks (format + lint)"
	@echo "  make check         - Run quality checks without fixing (CI mode)"
	@echo "  make clean         - Remove cache and build artifacts"

install:
	uv sync --dev

format:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .

type-check:
	@echo "Note: Type checking may show errors for existing codebase - this is informational only"
	-uv run mypy backend --ignore-missing-imports

quality: format lint
	@echo "✓ All quality checks passed!"

check:
	uv run ruff format --check .
	uv run ruff check .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
