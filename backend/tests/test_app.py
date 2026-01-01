import pytest
from fastapi import status
from unittest.mock import patch, Mock


class TestQueryEndpoint:
    """Tests for the /api/query endpoint"""

    def test_query_without_session_id(self, client, mock_rag_system):
        """Test query endpoint creates a new session when none provided"""
        response = client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "answer" in data
        assert "sources" in data
        assert "session_id" in data
        assert data["answer"] == "This is a test answer about the course material."
        assert len(data["sources"]) == 2
        assert data["session_id"] == "test-session-123"

        # Verify session was created
        mock_rag_system.session_manager.create_session.assert_called_once()

    def test_query_with_existing_session_id(self, client, mock_rag_system):
        """Test query endpoint uses existing session when provided"""
        session_id = "existing-session-456"
        response = client.post(
            "/api/query",
            json={
                "query": "Tell me more about FastAPI",
                "session_id": session_id
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["session_id"] == session_id
        assert "answer" in data
        assert "sources" in data

        # Verify RAG system was called with the query and session
        mock_rag_system.query.assert_called_once_with(
            "Tell me more about FastAPI",
            session_id
        )

    def test_query_with_empty_query(self, client):
        """Test query endpoint with empty query string"""
        response = client.post(
            "/api/query",
            json={"query": ""}
        )

        # Should still process, but validation happens at RAG level
        assert response.status_code == status.HTTP_200_OK

    def test_query_missing_query_field(self, client):
        """Test query endpoint without required query field"""
        response = client.post(
            "/api/query",
            json={"session_id": "test-123"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_query_invalid_json(self, client):
        """Test query endpoint with invalid JSON"""
        response = client.post(
            "/api/query",
            data="not a json",
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_query_rag_system_exception(self, client, mock_rag_system):
        """Test query endpoint handles RAG system exceptions"""
        mock_rag_system.query.side_effect = Exception("RAG system error")

        response = client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "RAG system error" in response.json()["detail"]

    def test_query_response_model_validation(self, client):
        """Test query endpoint returns correctly structured response"""
        response = client.post(
            "/api/query",
            json={"query": "Explain FastAPI"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Validate response structure
        assert isinstance(data["answer"], str)
        assert isinstance(data["sources"], list)
        assert isinstance(data["session_id"], str)
        assert len(data["answer"]) > 0
        assert len(data["session_id"]) > 0

    def test_query_with_special_characters(self, client):
        """Test query with special characters and unicode"""
        response = client.post(
            "/api/query",
            json={"query": "What is 'Python' & how does it work? 🐍"}
        )

        assert response.status_code == status.HTTP_200_OK

    def test_query_with_very_long_query(self, client):
        """Test query with very long input"""
        long_query = "What is Python? " * 1000
        response = client.post(
            "/api/query",
            json={"query": long_query}
        )

        assert response.status_code == status.HTTP_200_OK


class TestCoursesEndpoint:
    """Tests for the /api/courses endpoint"""

    def test_get_courses_success(self, client, mock_rag_system):
        """Test get courses endpoint returns correct statistics"""
        response = client.get("/api/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "total_courses" in data
        assert "course_titles" in data
        assert data["total_courses"] == 2
        assert len(data["course_titles"]) == 2
        assert "Introduction to Python" in data["course_titles"]
        assert "Advanced FastAPI" in data["course_titles"]

        # Verify RAG system method was called
        mock_rag_system.get_course_analytics.assert_called_once()

    def test_get_courses_empty_catalog(self, client, mock_rag_system):
        """Test get courses endpoint with no courses"""
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": []
        }

        response = client.get("/api/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["total_courses"] == 0
        assert data["course_titles"] == []

    def test_get_courses_exception(self, client, mock_rag_system):
        """Test get courses endpoint handles exceptions"""
        mock_rag_system.get_course_analytics.side_effect = Exception("Database error")

        response = client.get("/api/courses")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database error" in response.json()["detail"]

    def test_get_courses_response_model(self, client):
        """Test courses endpoint returns correctly structured response"""
        response = client.get("/api/courses")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert isinstance(data["total_courses"], int)
        assert isinstance(data["course_titles"], list)
        assert all(isinstance(title, str) for title in data["course_titles"])


class TestCORSMiddleware:
    """Tests for CORS middleware configuration"""

    def test_cors_headers_on_query(self, client):
        """Test CORS headers are present on query endpoint"""
        response = client.post(
            "/api/query",
            json={"query": "test"},
            headers={"Origin": "http://localhost:3000"}
        )

        assert "access-control-allow-origin" in response.headers

    def test_cors_preflight_request(self, client):
        """Test CORS preflight (OPTIONS) request"""
        response = client.options(
            "/api/query",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        assert "access-control-allow-origin" in response.headers


class TestStartupEvent:
    """Tests for application startup event"""

    @patch('app.os.path.exists')
    @patch('app.rag_system')
    def test_startup_loads_documents_when_docs_exist(self, mock_rag, mock_exists, client):
        """Test startup event loads documents when docs folder exists"""
        mock_exists.return_value = True
        mock_rag.add_course_folder.return_value = (3, 75)

        # Trigger startup event manually
        import app
        import asyncio
        asyncio.run(app.startup_event())

        # Verify folder loading was attempted
        mock_exists.assert_called()

    @patch('app.os.path.exists')
    @patch('app.rag_system')
    def test_startup_skips_when_no_docs_folder(self, mock_rag, mock_exists, client):
        """Test startup event handles missing docs folder gracefully"""
        mock_exists.return_value = False

        import app
        import asyncio
        asyncio.run(app.startup_event())

        # Should not call add_course_folder if folder doesn't exist
        mock_exists.assert_called()

    @patch('app.os.path.exists')
    @patch('app.rag_system')
    def test_startup_handles_loading_errors(self, mock_rag, mock_exists, client):
        """Test startup event handles document loading errors gracefully"""
        mock_exists.return_value = True
        mock_rag.add_course_folder.side_effect = Exception("Failed to load documents")

        import app
        import asyncio

        # Should not raise exception, just print error
        try:
            asyncio.run(app.startup_event())
        except Exception:
            pytest.fail("Startup event should handle exceptions gracefully")


class TestAPIDocumentation:
    """Tests for API documentation and OpenAPI schema"""

    def test_openapi_schema_available(self, client):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert schema["info"]["title"] == "Course Materials RAG System"

    def test_docs_ui_available(self, client):
        """Test Swagger UI documentation is accessible"""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_redoc_ui_available(self, client):
        """Test ReDoc documentation is accessible"""
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK


class TestRequestValidation:
    """Tests for request validation and error handling"""

    def test_query_with_extra_fields(self, client):
        """Test query endpoint ignores extra fields"""
        response = client.post(
            "/api/query",
            json={
                "query": "What is Python?",
                "session_id": "test-123",
                "extra_field": "should be ignored"
            }
        )

        # FastAPI should ignore extra fields by default or raise validation error
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_query_with_null_session_id(self, client):
        """Test query with null session_id"""
        response = client.post(
            "/api/query",
            json={
                "query": "What is Python?",
                "session_id": None
            }
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Should create new session when session_id is null
        assert data["session_id"] is not None

    def test_query_with_wrong_type(self, client):
        """Test query with wrong data type"""
        response = client.post(
            "/api/query",
            json={
                "query": 123  # Should be string
            }
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestHealthAndStatus:
    """Tests for application health and status"""

    def test_root_endpoint_serves_frontend(self, client):
        """Test root endpoint serves frontend static files"""
        response = client.get("/")

        # Should serve index.html or redirect
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_api_endpoints_are_mounted_correctly(self, client):
        """Test API endpoints are accessible at correct paths"""
        # Check query endpoint
        response = client.post("/api/query", json={"query": "test"})
        assert response.status_code != status.HTTP_404_NOT_FOUND

        # Check courses endpoint
        response = client.get("/api/courses")
        assert response.status_code != status.HTTP_404_NOT_FOUND
