"""Pytest configuration and fixtures."""

import pytest
import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.models.database import Base, User, Conversation, Message, Platform, MessageSender, MessageDirection, MessageStatus, ConversationStatus
from app.api.dependencies import get_db


def is_redis_available(host="localhost", port=6379, timeout=0.5):
    """Check if Redis is available without blocking."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return True
    except (socket.error, socket.timeout):
        return False


# Check Redis availability once at module load
REDIS_AVAILABLE = is_redis_available()

# Skip marker for tests that require Redis
requires_redis = pytest.mark.skipif(
    not REDIS_AVAILABLE,
    reason="Redis not available at localhost:6379"
)


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            # Do not close the session here as it is managed by the db fixture
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user(db):
    """Create a sample TikTok user."""
    user = User(
        platform=Platform.TIKTOK,
        platform_user_id="test_user_123",
        username="testuser",
        display_name="Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def linkedin_user(db):
    """Create a sample LinkedIn user."""
    user = User(
        platform=Platform.LINKEDIN,
        platform_user_id="linkedin_user_456",
        username="linkedinuser",
        display_name="LinkedIn Test User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def sample_conversation(db, sample_user):
    """Create a sample conversation with messages."""
    conv = Conversation(
        user_id=sample_user.id,
        platform=Platform.TIKTOK,
        platform_conversation_id="conv_123",
        status=ConversationStatus.ACTIVE,
        priority="normal"
    )
    db.add(conv)
    db.commit()
    
    # Add inbound message
    msg1 = Message(
        conversation_id=conv.id,
        sender_type=MessageSender.USER,
        direction=MessageDirection.INBOUND,
        content="Hello, I need help",
        platform_message_id="tiktok_conv_123_1000"
    )
    # Add outbound message
    msg2 = Message(
        conversation_id=conv.id,
        sender_type=MessageSender.AGENT,
        direction=MessageDirection.OUTBOUND,
        status=MessageStatus.SENT,
        content="How can I help you?"
    )
    db.add_all([msg1, msg2])
    db.commit()
    db.refresh(conv)
    return conv


@pytest.fixture(autouse=True)
def mock_celery_tasks(monkeypatch):
    """Mock Celery tasks to prevent actual queuing during tests.
    
    We must patch tasks where they are USED (in webhooks, messages routes),
    not where they are DEFINED (in tasks module), because the import happens
    at module load time before our mock is applied.
    """
    mock_task = Mock()
    mock_task.delay = Mock(return_value=Mock(id="test_task_123"))
    
    # Patch in the routes where tasks are imported and used
    from app.api.routes import webhooks, messages
    monkeypatch.setattr(webhooks, "process_incoming_message_task", mock_task)
    monkeypatch.setattr(messages, "send_message_task", mock_task)
    
    # Also patch in tasks module for backwards compatibility
    from app.services import tasks
    monkeypatch.setattr(tasks, "process_incoming_message_task", mock_task)
    monkeypatch.setattr(tasks, "send_message_task", mock_task)
    
    return mock_task


@pytest.fixture(autouse=True)
def mock_webhook_signatures(monkeypatch):
    """Mock webhook signature verification to always pass."""
    def mock_verify(*args, **kwargs):
        return True
    
    from app.integrations import tiktok, linkedin
    monkeypatch.setattr(tiktok.TikTokClient, "verify_webhook_signature", mock_verify)
    monkeypatch.setattr(linkedin.LinkedInClient, "verify_webhook_signature", mock_verify)


@pytest.fixture
def mock_platform_send(monkeypatch):
    """Mock platform send_message functions."""
    async def mock_send(*args, **kwargs):
        return True
    
    from app.services import message_processor
    monkeypatch.setattr(message_processor, "send_message_to_platform", mock_send)
    return mock_send

