# Quick Test Command Reference

## Basic Commands

```bash
# Run all tests
pytest

# Run all tests verbosely
pytest -v

# Run tests from backend directory
cd backend && pytest

# Stop at first failure
pytest -x

# Show test output (print statements)
pytest -s

# Run tests quietly
pytest -q
```

## Run Specific Tests

```bash
# Run a specific file
pytest backend/tests/test_app.py

# Run a specific class
pytest backend/tests/test_app.py::TestQueryEndpoint

# Run a specific test
pytest backend/tests/test_app.py::TestQueryEndpoint::test_query_without_session_id

# Run tests matching a pattern
pytest -k "query"
pytest -k "not slow"
```

## Coverage Reports

```bash
# Basic coverage
pytest --cov=backend

# Coverage with missing lines
pytest --cov=backend --cov-report=term-missing

# HTML coverage report
pytest --cov=backend --cov-report=html
open htmlcov/index.html

# Coverage for specific file
pytest --cov=app --cov-report=term
```

## Test Categories

```bash
# Run only API tests (requires markers)
pytest -m api

# Run only integration tests
pytest -m integration

# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"
```

## Debugging

```bash
# Show local variables on failure
pytest --showlocals
pytest -l

# Enter debugger on failure
pytest --pdb

# Enter debugger at start of test
pytest --trace

# Show full diff on failures
pytest -vv
```

## Parallel Execution

```bash
# Install pytest-xdist first
pip install pytest-xdist

# Run tests in parallel (4 workers)
pytest -n 4

# Run tests in parallel (auto-detect CPUs)
pytest -n auto
```

## Output Control

```bash
# Only show failed tests
pytest --tb=short

# Show only test summary
pytest --tb=no

# Show detailed traceback
pytest --tb=long

# Show only line of failure
pytest --tb=line
```

## Watch Mode

```bash
# Install pytest-watch first
pip install pytest-watch

# Auto-run tests on file changes
ptw
```

## Common Workflows

### During Development
```bash
# Run tests with output and stop on first failure
pytest -xvs

# Run specific test you're working on
pytest backend/tests/test_app.py::TestQueryEndpoint::test_query_without_session_id -v
```

### Before Committing
```bash
# Run all tests with coverage
pytest --cov=backend --cov-report=term-missing

# Run all tests verbosely
pytest -v
```

### CI/CD Pipeline
```bash
# Run all tests with coverage and XML report
pytest --cov=backend --cov-report=xml --cov-report=term -v

# Run with JUnit XML for CI integration
pytest --junitxml=test-results.xml
```

### Troubleshooting
```bash
# Clear cache and rerun
pytest --cache-clear

# Show fixtures being used
pytest --fixtures

# Show available markers
pytest --markers

# Collect tests without running
pytest --collect-only
```

## Installation

```bash
# Install dependencies
uv sync

# Or with pip
pip install -e .
```

## Quick Test
```bash
# Verify installation
pytest --version

# Run a quick test
pytest backend/tests/test_app.py::TestQueryEndpoint::test_query_without_session_id -v
```
