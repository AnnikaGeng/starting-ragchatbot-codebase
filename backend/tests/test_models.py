import pytest
from pydantic import ValidationError
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import QueryRequest, QueryResponse, CourseStats


class TestQueryRequest:
    """Tests for QueryRequest model validation"""

    def test_query_request_valid_minimal(self):
        """Test QueryRequest with minimal required fields"""
        request = QueryRequest(query="What is Python?")

        assert request.query == "What is Python?"
        assert request.session_id is None

    def test_query_request_valid_with_session(self):
        """Test QueryRequest with all fields"""
        request = QueryRequest(
            query="Explain FastAPI",
            session_id="session-123"
        )

        assert request.query == "Explain FastAPI"
        assert request.session_id == "session-123"

    def test_query_request_empty_query(self):
        """Test QueryRequest accepts empty query string"""
        request = QueryRequest(query="")
        assert request.query == ""

    def test_query_request_missing_query(self):
        """Test QueryRequest raises error when query is missing"""
        with pytest.raises(ValidationError) as exc_info:
            QueryRequest()

        assert "query" in str(exc_info.value)

    def test_query_request_invalid_query_type(self):
        """Test QueryRequest raises error for non-string query"""
        with pytest.raises(ValidationError):
            QueryRequest(query=123)

    def test_query_request_invalid_session_type(self):
        """Test QueryRequest raises error for non-string session_id"""
        with pytest.raises(ValidationError):
            QueryRequest(query="test", session_id=456)

    def test_query_request_with_long_query(self):
        """Test QueryRequest handles very long query strings"""
        long_query = "a" * 10000
        request = QueryRequest(query=long_query)
        assert len(request.query) == 10000

    def test_query_request_with_unicode(self):
        """Test QueryRequest handles unicode characters"""
        request = QueryRequest(query="What is Python? 🐍 学习编程")
        assert "🐍" in request.query
        assert "学习编程" in request.query

    def test_query_request_serialization(self):
        """Test QueryRequest can be serialized to JSON"""
        request = QueryRequest(query="test", session_id="abc")
        json_data = request.model_dump()

        assert json_data["query"] == "test"
        assert json_data["session_id"] == "abc"

    def test_query_request_from_dict(self):
        """Test QueryRequest can be created from dictionary"""
        data = {"query": "What is FastAPI?", "session_id": "test-123"}
        request = QueryRequest(**data)

        assert request.query == data["query"]
        assert request.session_id == data["session_id"]


class TestQueryResponse:
    """Tests for QueryResponse model validation"""

    def test_query_response_valid(self):
        """Test QueryResponse with valid data"""
        response = QueryResponse(
            answer="Python is a programming language",
            sources=["Source 1", "Source 2"],
            session_id="session-123"
        )

        assert response.answer == "Python is a programming language"
        assert len(response.sources) == 2
        assert response.session_id == "session-123"

    def test_query_response_empty_sources(self):
        """Test QueryResponse with empty sources list"""
        response = QueryResponse(
            answer="General knowledge answer",
            sources=[],
            session_id="session-456"
        )

        assert response.answer == "General knowledge answer"
        assert response.sources == []

    def test_query_response_missing_required_fields(self):
        """Test QueryResponse raises error when required fields missing"""
        with pytest.raises(ValidationError):
            QueryResponse(answer="test")

        with pytest.raises(ValidationError):
            QueryResponse(sources=[], session_id="123")

    def test_query_response_invalid_sources_type(self):
        """Test QueryResponse raises error for non-list sources"""
        with pytest.raises(ValidationError):
            QueryResponse(
                answer="test",
                sources="not a list",
                session_id="123"
            )

    def test_query_response_invalid_answer_type(self):
        """Test QueryResponse raises error for non-string answer"""
        with pytest.raises(ValidationError):
            QueryResponse(
                answer=123,
                sources=[],
                session_id="123"
            )

    def test_query_response_sources_with_non_strings(self):
        """Test QueryResponse raises error for non-string items in sources"""
        with pytest.raises(ValidationError):
            QueryResponse(
                answer="test",
                sources=["valid", 123, "another"],
                session_id="123"
            )

    def test_query_response_serialization(self):
        """Test QueryResponse can be serialized to JSON"""
        response = QueryResponse(
            answer="Test answer",
            sources=["Source 1", "Source 2"],
            session_id="abc"
        )
        json_data = response.model_dump()

        assert json_data["answer"] == "Test answer"
        assert json_data["sources"] == ["Source 1", "Source 2"]
        assert json_data["session_id"] == "abc"

    def test_query_response_with_long_answer(self):
        """Test QueryResponse handles long answer strings"""
        long_answer = "a" * 10000
        response = QueryResponse(
            answer=long_answer,
            sources=[],
            session_id="test"
        )

        assert len(response.answer) == 10000

    def test_query_response_with_many_sources(self):
        """Test QueryResponse handles many sources"""
        sources = [f"Source {i}" for i in range(100)]
        response = QueryResponse(
            answer="test",
            sources=sources,
            session_id="test"
        )

        assert len(response.sources) == 100


class TestCourseStats:
    """Tests for CourseStats model validation"""

    def test_course_stats_valid(self):
        """Test CourseStats with valid data"""
        stats = CourseStats(
            total_courses=5,
            course_titles=["Course 1", "Course 2", "Course 3", "Course 4", "Course 5"]
        )

        assert stats.total_courses == 5
        assert len(stats.course_titles) == 5

    def test_course_stats_empty_catalog(self):
        """Test CourseStats with no courses"""
        stats = CourseStats(
            total_courses=0,
            course_titles=[]
        )

        assert stats.total_courses == 0
        assert stats.course_titles == []

    def test_course_stats_missing_fields(self):
        """Test CourseStats raises error when fields are missing"""
        with pytest.raises(ValidationError):
            CourseStats(total_courses=5)

        with pytest.raises(ValidationError):
            CourseStats(course_titles=["Course 1"])

    def test_course_stats_invalid_total_type(self):
        """Test CourseStats raises error for non-integer total_courses"""
        with pytest.raises(ValidationError):
            CourseStats(
                total_courses="five",
                course_titles=["Course 1"]
            )

    def test_course_stats_invalid_titles_type(self):
        """Test CourseStats raises error for non-list course_titles"""
        with pytest.raises(ValidationError):
            CourseStats(
                total_courses=1,
                course_titles="Course 1"
            )

    def test_course_stats_titles_with_non_strings(self):
        """Test CourseStats raises error for non-string titles"""
        with pytest.raises(ValidationError):
            CourseStats(
                total_courses=3,
                course_titles=["Course 1", 123, "Course 3"]
            )

    def test_course_stats_negative_total(self):
        """Test CourseStats with negative total_courses"""
        # Pydantic allows negative integers by default
        stats = CourseStats(
            total_courses=-1,
            course_titles=[]
        )
        assert stats.total_courses == -1

    def test_course_stats_count_mismatch(self):
        """Test CourseStats when count doesn't match list length"""
        # This should be valid - no constraint between them
        stats = CourseStats(
            total_courses=10,
            course_titles=["Course 1", "Course 2"]
        )

        assert stats.total_courses == 10
        assert len(stats.course_titles) == 2

    def test_course_stats_serialization(self):
        """Test CourseStats can be serialized to JSON"""
        stats = CourseStats(
            total_courses=3,
            course_titles=["Python", "FastAPI", "Django"]
        )
        json_data = stats.model_dump()

        assert json_data["total_courses"] == 3
        assert json_data["course_titles"] == ["Python", "FastAPI", "Django"]

    def test_course_stats_with_unicode_titles(self):
        """Test CourseStats handles unicode in course titles"""
        stats = CourseStats(
            total_courses=2,
            course_titles=["Python 编程", "FastAPI 🚀"]
        )

        assert "编程" in stats.course_titles[0]
        assert "🚀" in stats.course_titles[1]


class TestModelInteroperability:
    """Tests for model interactions and data flow"""

    def test_query_request_to_response_flow(self):
        """Test data flow from request to response"""
        # Create request
        request = QueryRequest(
            query="What is Python?",
            session_id="test-session"
        )

        # Simulate processing and create response
        response = QueryResponse(
            answer="Python is a programming language",
            sources=["Course: Python 101, Lesson 1"],
            session_id=request.session_id or "new-session"
        )

        assert response.session_id == request.session_id

    def test_models_json_compatibility(self):
        """Test all models can be converted to/from JSON"""
        import json

        # QueryRequest
        request = QueryRequest(query="test")
        request_json = json.dumps(request.model_dump())
        assert json.loads(request_json)["query"] == "test"

        # QueryResponse
        response = QueryResponse(answer="answer", sources=[], session_id="123")
        response_json = json.dumps(response.model_dump())
        assert json.loads(response_json)["answer"] == "answer"

        # CourseStats
        stats = CourseStats(total_courses=1, course_titles=["Course 1"])
        stats_json = json.dumps(stats.model_dump())
        assert json.loads(stats_json)["total_courses"] == 1

    def test_model_defaults(self):
        """Test model default values"""
        # QueryRequest should have session_id=None by default
        request = QueryRequest(query="test")
        assert request.session_id is None

    def test_model_field_assignment(self):
        """Test that model fields can be reassigned with validation"""
        request = QueryRequest(query="test")

        # Pydantic v2 models are mutable by default
        # But setting a new value will validate it
        request.query = "new value"
        assert request.query == "new value"

        # However, invalid types should raise validation error when using model_validate
        with pytest.raises(ValidationError):
            QueryRequest.model_validate({"query": 123})
