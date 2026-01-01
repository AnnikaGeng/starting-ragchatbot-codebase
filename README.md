# Course Materials RAG System

A Retrieval-Augmented Generation (RAG) system designed to answer questions about course materials using semantic search and AI-powered responses.

## Overview

This application is a full-stack web application that enables users to query course materials and receive intelligent, context-aware responses. It uses ChromaDB for vector storage, Anthropic's Claude for AI generation, and provides a web interface for interaction.


## Prerequisites

- Python 3.13 or higher
- uv (Python package manager)
- An Anthropic API key (for Claude AI)
- **For Windows**: Use Git Bash to run the application commands - [Download Git for Windows](https://git-scm.com/downloads/win)

## Installation

1. **Install uv** (if not already installed)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Python dependencies**
   ```bash
   uv sync --dev
   ```

3. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```bash
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

## Running the Application

### Quick Start

Use the provided shell script:
```bash
chmod +x run.sh
./run.sh
```

### Manual Start

```bash
cd backend
uv run uvicorn app:app --reload --port 8000
```

The application will be available at:
- Web Interface: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## Code Quality

This project uses several tools to maintain code quality:

- **Ruff**: Fast Python linter and formatter (replaces Black, Flake8, isort) - enforced
- **mypy**: Static type checker - available but optional (configured for future strict typing)
- **pre-commit**: Git hooks for automated quality checks before each commit

### Setup Pre-commit Hooks

Install pre-commit hooks to automatically check code quality before each commit:

```bash
uv run pre-commit install
```

### Running Quality Checks

Use the Makefile commands for easy quality management:

```bash
# Format code and auto-fix issues
make format

# Run linting checks
make lint

# Run all quality checks (format + lint)
make quality

# Run checks in CI mode (no auto-fix)
make check

# Optional: Run type checking (may show errors for existing code)
make type-check
```

Or run tools directly:

```bash
# Format code
uv run ruff format .

# Lint and auto-fix
uv run ruff check --fix .

# Type check (optional - informational only)
uv run mypy backend

# Run pre-commit on all files
uv run pre-commit run --all-files
```

### Code Quality Standards

The project enforces:
- **Formatting**: Consistent code style with 100 character line length
- **Linting**: Code quality checks including:
  - Error and warning detection (pycodestyle)
  - Unused imports and variables (pyflakes)
  - Import sorting and organization
  - Bug-prone pattern detection (flake8-bugbear)
  - Code simplification suggestions
  - Python upgrade syntax recommendations

Type checking with mypy is configured but optional, allowing gradual adoption of type hints.
