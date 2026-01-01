# FastAPI Tests

Comprehensive test suite for the Course Materials RAG System FastAPI application.

## Test Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Shared fixtures and test configuration
├── test_app.py              # API endpoint tests
├── test_models.py           # Request/response model validation tests
└── test_integration.py      # End-to-end integration tests
```

## Test Coverage

### test_app.py
Tests for FastAPI endpoints and middleware:
- **QueryEndpoint**: POST /api/query endpoint
  - New session creation
  - Existing session handling
  - Input validation
  - Error handling
  - Special characters and edge cases
- **CoursesEndpoint**: GET /api/courses endpoint
  - Course statistics retrieval
  - Empty catalog handling
  - Error scenarios
- **CORSMiddleware**: CORS configuration
  - CORS headers on requests
  - Preflight OPTIONS requests
- **StartupEvent**: Application startup
  - Document loading on startup
  - Error handling during startup
- **APIDocumentation**: OpenAPI schema
  - Swagger UI accessibility
  - ReDoc accessibility
- **RequestValidation**: Input validation
  - Extra fields handling
  - Type validation
  - Null value handling

### test_models.py
Tests for Pydantic data models:
- **QueryRequest**: Input validation
  - Required fields
  - Optional fields
  - Type validation
  - Serialization
- **QueryResponse**: Output validation
  - Required fields
  - List validation
  - Type checking
- **CourseStats**: Course statistics
  - Field validation
  - Type enforcement
  - Unicode support

### test_integration.py
End-to-end integration tests:
- **EndToEndQueryFlow**: Complete user flows
  - New user query workflow
  - Multi-turn conversations
  - Concurrent sessions
- **ErrorHandlingIntegration**: Error scenarios
  - Graceful degradation
  - Session persistence during errors
- **ConversationContext**: History management
  - Context maintenance
  - Session isolation
- **SourceTracking**: Citation tracking
  - Source return with answers
  - Empty sources for general queries
- **CourseManagement**: Course operations
  - Statistics accuracy
  - Dynamic course updates
- **APIPerformance**: Performance tests
  - Concurrent request handling
  - Large response handling
- **CORSIntegration**: CORS functionality
  - Frontend request handling
  - CORS on all endpoints

## Running Tests

### Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### Run All Tests

```bash
# From project root
pytest

# Or from backend directory
cd backend && pytest
```

### Run Specific Test Files

```bash
# API endpoint tests only
pytest backend/tests/test_app.py

# Model validation tests only
pytest backend/tests/test_models.py

# Integration tests only
pytest backend/tests/test_integration.py
```

### Run Specific Test Classes or Functions

```bash
# Run specific test class
pytest backend/tests/test_app.py::TestQueryEndpoint

# Run specific test function
pytest backend/tests/test_app.py::TestQueryEndpoint::test_query_without_session_id
```

### Run Tests with Coverage

```bash
# Generate coverage report
pytest --cov=backend --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Run Tests with Different Verbosity

```bash
# Minimal output
pytest -q

# Verbose output (default)
pytest -v

# Very verbose with test output
pytest -vv -s
```

### Run Tests by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Fixtures

### Available Fixtures (defined in conftest.py)

- **mock_config**: Mock configuration object
- **mock_rag_system**: Mock RAGSystem with predefined responses
- **mock_vector_store**: Mock VectorStore
- **mock_session_manager**: Mock SessionManager
- **mock_ai_generator**: Mock AIGenerator
- **mock_document_processor**: Mock DocumentProcessor
- **client**: FastAPI TestClient with mocked dependencies
- **sample_course_document**: Sample course document content
- **cleanup_test_db**: Auto-cleanup fixture for test databases

## Writing New Tests

### Example Test Structure

```python
import pytest
from fastapi import status

class TestYourFeature:
    """Tests for your feature"""

    def test_something(self, client, mock_rag_system):
        """Test description"""
        # Arrange
        mock_rag_system.some_method.return_value = "expected"

        # Act
        response = client.post("/api/endpoint", json={"key": "value"})

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["field"] == "expected"
```

### Best Practices

1. **Use descriptive test names**: Test names should clearly describe what is being tested
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Use fixtures**: Leverage conftest.py fixtures to avoid duplication
4. **Mock external dependencies**: Always mock RAGSystem, AI generators, and vector stores
5. **Test edge cases**: Include tests for error conditions, empty inputs, and boundary values
6. **Keep tests isolated**: Each test should be independent
7. **Use markers**: Tag tests with appropriate markers (unit, integration, slow, etc.)

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    uv sync
    pytest --cov=backend --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure backend directory is in PYTHONPATH
   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
   ```

2. **Fixture not found**: Check conftest.py is in the correct location

3. **Database cleanup issues**: The cleanup_test_db fixture should handle this automatically

4. **Async test warnings**: Ensure pytest-asyncio is installed and asyncio_mode is set in pytest.ini

## Test Statistics

Run `pytest --cov=backend --cov-report=term` to see:
- Total number of tests
- Test pass/fail rate
- Code coverage percentage
- Coverage by file

## Contributing

When adding new features:
1. Write tests first (TDD approach recommended)
2. Ensure all tests pass before committing
3. Maintain test coverage above 80%
4. Add new fixtures to conftest.py if needed
5. Update this README if adding new test categories
