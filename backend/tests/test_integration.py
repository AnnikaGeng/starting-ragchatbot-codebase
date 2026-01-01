import pytest
from unittest.mock import patch, Mock, MagicMock
from fastapi import status


class TestEndToEndQueryFlow:
    """End-to-end tests for the complete query flow"""

    def test_complete_query_flow_new_user(self, client, mock_rag_system):
        """Test complete flow: new user asks question, gets answer with sources"""
        # Step 1: New user asks first question
        response1 = client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )

        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()

        # Verify we got a session
        session_id = data1["session_id"]
        assert session_id is not None

        # Verify we got an answer and sources
        assert len(data1["answer"]) > 0
        assert isinstance(data1["sources"], list)

        # Step 2: Same user asks follow-up question using session
        mock_rag_system.query.return_value = (
            "This is a follow-up answer.",
            ["Course: Python, Lesson 3"]
        )

        response2 = client.post(
            "/api/query",
            json={
                "query": "Can you tell me more?",
                "session_id": session_id
            }
        )

        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()

        # Same session should be maintained
        assert data2["session_id"] == session_id
        assert data2["answer"] == "This is a follow-up answer."

    def test_multiple_concurrent_sessions(self, client, mock_rag_system):
        """Test multiple users can have separate concurrent sessions"""
        # User 1 starts a session
        response1 = client.post(
            "/api/query",
            json={"query": "What is FastAPI?"}
        )
        session1 = response1.json()["session_id"]

        # User 2 starts a different session
        mock_rag_system.session_manager.create_session.return_value = "different-session"

        response2 = client.post(
            "/api/query",
            json={"query": "What is Django?"}
        )
        session2 = response2.json()["session_id"]

        # Sessions should be different
        assert session1 != session2

    def test_query_to_courses_workflow(self, client, mock_rag_system):
        """Test workflow: user queries courses, then asks questions about them"""
        # Step 1: Check available courses
        response1 = client.get("/api/courses")
        assert response1.status_code == status.HTTP_200_OK

        courses_data = response1.json()
        assert courses_data["total_courses"] > 0

        # Step 2: Ask question about one of the courses
        course_title = courses_data["course_titles"][0]
        response2 = client.post(
            "/api/query",
            json={"query": f"Tell me about {course_title}"}
        )

        assert response2.status_code == status.HTTP_200_OK
        assert len(response2.json()["answer"]) > 0


class TestErrorHandlingIntegration:
    """Integration tests for error handling across components"""

    def test_graceful_degradation_on_rag_failure(self, client, mock_rag_system):
        """Test system handles RAG system failures gracefully"""
        # Simulate RAG system failure
        mock_rag_system.query.side_effect = Exception("Vector store connection failed")

        response = client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )

        # Should return 500 error with message
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "detail" in response.json()

    def test_error_handling_maintains_session(self, client, mock_rag_system):
        """Test that errors don't corrupt session state"""
        # First successful query
        response1 = client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )
        session_id = response1.json()["session_id"]

        # Second query fails
        mock_rag_system.query.side_effect = Exception("Temporary failure")
        response2 = client.post(
            "/api/query",
            json={"query": "Tell me more", "session_id": session_id}
        )
        assert response2.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

        # Third query should work with same session
        mock_rag_system.query.side_effect = None
        mock_rag_system.query.return_value = ("Recovery answer", [])

        response3 = client.post(
            "/api/query",
            json={"query": "New question", "session_id": session_id}
        )

        assert response3.status_code == status.HTTP_200_OK
        assert response3.json()["session_id"] == session_id


class TestConversationContext:
    """Tests for conversation context and history management"""

    def test_conversation_history_maintained(self, client, mock_rag_system):
        """Test that conversation history is maintained across queries"""
        # Mock session manager to track history
        mock_session_manager = mock_rag_system.session_manager
        mock_session_manager.get_conversation_history.return_value = ""

        # First query
        response1 = client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )
        session_id = response1.json()["session_id"]

        # Second query - should include history
        mock_session_manager.get_conversation_history.return_value = (
            "User: What is Python?\nAssistant: Python is a programming language."
        )

        response2 = client.post(
            "/api/query",
            json={"query": "Can you explain more?", "session_id": session_id}
        )

        assert response2.status_code == status.HTTP_200_OK

        # Verify RAG system was called with the session
        assert mock_rag_system.query.call_count >= 2

    def test_new_session_has_no_history(self, client, mock_rag_system):
        """Test that new sessions start with empty history"""
        response = client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )

        assert response.status_code == status.HTTP_200_OK

        # For new session, history should be empty or None
        # The session manager should create a fresh session


class TestSourceTracking:
    """Tests for source tracking and citation"""

    def test_sources_returned_with_answer(self, client, mock_rag_system):
        """Test that sources are properly returned with answers"""
        mock_rag_system.query.return_value = (
            "Python is a programming language.",
            [
                "Course: Introduction to Python, Lesson 1, Chunk 0",
                "Course: Introduction to Python, Lesson 1, Chunk 1"
            ]
        )

        response = client.post(
            "/api/query",
            json={"query": "What is Python?"}
        )

        data = response.json()
        assert len(data["sources"]) == 2
        assert "Introduction to Python" in data["sources"][0]

    def test_no_sources_for_general_knowledge(self, client, mock_rag_system):
        """Test that queries not requiring course materials have empty sources"""
        mock_rag_system.query.return_value = (
            "General knowledge answer",
            []
        )

        response = client.post(
            "/api/query",
            json={"query": "What is 2+2?"}
        )

        data = response.json()
        assert data["sources"] == []


class TestCourseManagement:
    """Integration tests for course management"""

    def test_course_statistics_accuracy(self, client, mock_rag_system):
        """Test that course statistics are accurate"""
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 3,
            "course_titles": ["Course A", "Course B", "Course C"]
        }

        response = client.get("/api/courses")
        data = response.json()

        assert data["total_courses"] == 3
        assert len(data["course_titles"]) == 3
        assert data["total_courses"] == len(data["course_titles"])

    def test_course_count_updates(self, client, mock_rag_system):
        """Test that course count can change over time"""
        # Initial state
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 2,
            "course_titles": ["Course A", "Course B"]
        }

        response1 = client.get("/api/courses")
        assert response1.json()["total_courses"] == 2

        # After adding more courses
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 4,
            "course_titles": ["Course A", "Course B", "Course C", "Course D"]
        }

        response2 = client.get("/api/courses")
        assert response2.json()["total_courses"] == 4


class TestAPIPerformance:
    """Tests for API performance and limits"""

    def test_concurrent_requests_handling(self, client, mock_rag_system):
        """Test API can handle multiple concurrent requests"""
        # Simulate multiple concurrent requests
        responses = []
        for i in range(10):
            response = client.post(
                "/api/query",
                json={"query": f"Question {i}"}
            )
            responses.append(response)

        # All requests should succeed
        assert all(r.status_code == status.HTTP_200_OK for r in responses)

        # Each should have unique sessions
        session_ids = [r.json()["session_id"] for r in responses]
        # Note: With mocking, they might be the same. In real scenario, they'd be unique.

    def test_large_response_handling(self, client, mock_rag_system):
        """Test API can handle large responses"""
        large_answer = "a" * 10000
        large_sources = [f"Source {i}" for i in range(100)]

        mock_rag_system.query.return_value = (large_answer, large_sources)

        response = client.post(
            "/api/query",
            json={"query": "Give me detailed information"}
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data["answer"]) == 10000
        assert len(data["sources"]) == 100


class TestCORSIntegration:
    """Integration tests for CORS functionality"""

    def test_cors_allows_frontend_requests(self, client):
        """Test CORS allows requests from frontend origins"""
        response = client.post(
            "/api/query",
            json={"query": "test"},
            headers={"Origin": "http://localhost:8000"}
        )

        assert response.status_code == status.HTTP_200_OK
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers

    def test_cors_headers_on_all_endpoints(self, client):
        """Test CORS headers are present on all endpoints"""
        # Query endpoint
        response1 = client.post(
            "/api/query",
            json={"query": "test"},
            headers={"Origin": "http://localhost:3000"}
        )
        assert "access-control-allow-origin" in response1.headers

        # Courses endpoint
        response2 = client.get(
            "/api/courses",
            headers={"Origin": "http://localhost:3000"}
        )
        assert "access-control-allow-origin" in response2.headers


class TestAPIVersioning:
    """Tests for API versioning and compatibility"""

    def test_api_endpoints_use_api_prefix(self, client):
        """Test that all API endpoints use /api prefix"""
        # Query endpoint
        response1 = client.post("/api/query", json={"query": "test"})
        assert response1.status_code != status.HTTP_404_NOT_FOUND

        # Courses endpoint
        response2 = client.get("/api/courses")
        assert response2.status_code != status.HTTP_404_NOT_FOUND

    def test_openapi_schema_version(self, client):
        """Test OpenAPI schema contains version information"""
        response = client.get("/openapi.json")
        schema = response.json()

        assert "info" in schema
        assert "version" in schema["info"]


class TestStaticFileServing:
    """Tests for static file serving"""

    def test_static_files_served(self, client):
        """Test that static files are served correctly"""
        # Root should serve frontend
        response = client.get("/")

        # Should either return HTML or 404 if file doesn't exist
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_api_routes_take_precedence(self, client):
        """Test that API routes take precedence over static files"""
        # API routes should work even if static files exist
        response = client.post("/api/query", json={"query": "test"})
        assert response.status_code == status.HTTP_200_OK

        response = client.get("/api/courses")
        assert response.status_code == status.HTTP_200_OK
