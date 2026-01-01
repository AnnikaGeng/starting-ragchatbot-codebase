import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_config():
    """Mock configuration for tests"""
    config = Mock()
    config.ANTHROPIC_API_KEY = "test-api-key"
    config.ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
    config.EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    config.CHUNK_SIZE = 800
    config.CHUNK_OVERLAP = 100
    config.MAX_RESULTS = 5
    config.MAX_HISTORY = 2
    config.CHROMA_PATH = "./test_chroma_db"
    return config


@pytest.fixture
def mock_rag_system():
    """Mock RAGSystem for testing API endpoints"""
    rag_system = Mock()

    # Mock session manager
    rag_system.session_manager = Mock()
    rag_system.session_manager.create_session.return_value = "test-session-123"

    # Mock query method
    rag_system.query.return_value = (
        "This is a test answer about the course material.",
        ["Course: Test Course, Lesson 1, Chunk 0", "Course: Test Course, Lesson 2, Chunk 1"]
    )

    # Mock get_course_analytics method
    rag_system.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Introduction to Python", "Advanced FastAPI"]
    }

    # Mock add_course_folder method
    rag_system.add_course_folder.return_value = (2, 50)

    return rag_system


@pytest.fixture
def mock_vector_store():
    """Mock VectorStore for testing"""
    vector_store = Mock()
    vector_store.get_course_count.return_value = 2
    vector_store.get_existing_course_titles.return_value = ["Course 1", "Course 2"]
    vector_store.search_course_content.return_value = [
        ("Sample content chunk 1", {"course_title": "Course 1", "lesson_number": 1}),
        ("Sample content chunk 2", {"course_title": "Course 1", "lesson_number": 2})
    ]
    return vector_store


@pytest.fixture
def mock_session_manager():
    """Mock SessionManager for testing"""
    session_manager = Mock()
    session_manager.create_session.return_value = "test-session-abc"
    session_manager.get_conversation_history.return_value = "User: Previous question\nAssistant: Previous answer"
    session_manager.add_exchange.return_value = None
    return session_manager


@pytest.fixture
def mock_ai_generator():
    """Mock AIGenerator for testing"""
    ai_generator = Mock()
    ai_generator.generate_response.return_value = "This is a generated AI response."
    return ai_generator


@pytest.fixture
def mock_document_processor():
    """Mock DocumentProcessor for testing"""
    from models import Course, Lesson, CourseChunk

    processor = Mock()

    # Create a mock course
    course = Course(
        title="Test Course",
        link="https://test.com/course",
        instructor="Test Instructor",
        lessons=[
            Lesson(lesson_number=1, lesson_title="Introduction", lesson_link="https://test.com/lesson1")
        ]
    )

    # Create mock chunks
    chunks = [
        CourseChunk(
            content="Test content chunk 1",
            course_title="Test Course",
            lesson_number=1,
            chunk_index=0
        )
    ]

    processor.process_course_document.return_value = (course, chunks)
    return processor


@pytest.fixture
def client(mock_rag_system):
    """FastAPI test client with mocked RAGSystem"""
    with patch('app.RAGSystem') as mock_rag_class:
        mock_rag_class.return_value = mock_rag_system

        # Import app after patching
        from app import app

        # Override the rag_system in the app module
        import app as app_module
        app_module.rag_system = mock_rag_system

        with TestClient(app) as test_client:
            yield test_client


@pytest.fixture
def sample_course_document():
    """Sample course document content for testing"""
    return """Course Title: Introduction to Python
Course Link: https://example.com/python
Course Instructor: John Doe

Lesson 1: Getting Started
Lesson Link: https://example.com/python/lesson1
This is the introduction to Python programming. Python is a high-level programming language.

Lesson 2: Variables and Data Types
Lesson Link: https://example.com/python/lesson2
In this lesson, we learn about variables and different data types in Python.
"""


@pytest.fixture(autouse=True)
def cleanup_test_db():
    """Cleanup test database after each test"""
    yield
    # Cleanup code here if needed
    test_db_path = "./test_chroma_db"
    if os.path.exists(test_db_path):
        import shutil
        try:
            shutil.rmtree(test_db_path)
        except Exception:
            pass
