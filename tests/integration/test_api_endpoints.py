"""Comprehensive integration tests for updated API endpoints."""

from fastapi.testclient import TestClient
import json


# ============================================
# Basic Health Endpoints
# ============================================

def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data


def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ============================================
# Webhook Endpoints - Deduplication Tests
# ============================================

def test_webhook_verify(client: TestClient):
    """Test webhook verification endpoint."""
    response = client.get("/webhooks/verify?challenge=test123")
    assert response.status_code == 200
    data = response.json()
    assert data["challenge"] == "test123"


def test_tiktok_webhook_first_message(client: TestClient, mock_celery_tasks):
    """Test TikTok webhook accepts first message."""
    webhook_data = {
        "event_type": "message",
        "user_id": "tiktok_user_new",
        "message": "First message from this conversation",
        "conversation_id": "new_conv_999",
        "timestamp": 1234567890
    }
    
    response = client.post("/webhooks/tiktok", json=webhook_data, headers={"x-signature": "mock_sig"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    
    # Verify Celery task was called
    assert mock_celery_tasks.delay.called


def test_tiktok_webhook_deduplication(client: TestClient, sample_user, db):
    """Test TikTok webhook deduplicates messages."""
    from app.models.database import Message, MessageSender, MessageDirection, Conversation, ConversationStatus, Platform
    
    # Create existing conversation and message
    conv = Conversation(
        user_id=sample_user.id,
        platform=Platform.TIKTOK,
        platform_conversation_id="dup_conv_123",
        status=ConversationStatus.ACTIVE
    )
    db.add(conv)
    db.commit()
    
    platform_msg_id = "tiktok_dup_conv_123_9999"
    existing_msg = Message(
        conversation_id=conv.id,
        sender_type=MessageSender.USER,
        direction=MessageDirection.INBOUND,
        content="Duplicate message",
        platform_message_id=platform_msg_id
    )
    db.add(existing_msg)
    db.commit()
    db.refresh(existing_msg)
    
    # Send webhook with same timestamp/conversation_id
    webhook_data = {
        "event_type": "message",
        "user_id": sample_user.platform_user_id,
        "message": "Duplicate message",
        "conversation_id": "dup_conv_123",
        "timestamp": 9999
    }
    
    response = client.post("/webhooks/tiktok", json=webhook_data, headers={"x-signature": "mock_sig"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "internal_id" in data
    assert data["internal_id"] == existing_msg.id


def test_linkedin_webhook_deduplication(client: TestClient, linkedin_user, db):
    """Test LinkedIn webhook deduplicates messages."""
    from app.models.database import Message, MessageSender, MessageDirection, Conversation, ConversationStatus, Platform
    
    # Create existing conversation with message
    conv = Conversation(
        user_id=linkedin_user.id,
        platform=Platform.LINKEDIN,
        platform_conversation_id="linkedin_conv_456",
        status=ConversationStatus.ACTIVE
    )
    db.add(conv)
    db.commit()
    
    platform_msg_id = "linkedin_linkedin_conv_456_7777"
    existing_msg = Message(
        conversation_id=conv.id,
        sender_type=MessageSender.USER,
        direction=MessageDirection.INBOUND,
        content="Duplicate LinkedIn message",
        platform_message_id=platform_msg_id
    )
    db.add(existing_msg)
    db.commit()
    db.refresh(existing_msg)
    
    # Send duplicate webhook
    webhook_data = {
        "event_type": "message",
        "sender_id": linkedin_user.platform_user_id,
        "message_text": "Duplicate LinkedIn message",
        "conversation_id": "linkedin_conv_456",
        "timestamp": 7777
    }
    
    response = client.post("/webhooks/linkedin", json=webhook_data, headers={"x-signature": "mock_sig"})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert "internal_id" in data
    assert data["internal_id"] == existing_msg.id


def test_tiktok_webhook_missing_signature(client: TestClient, monkeypatch):
    """Test TikTok webhook rejects requests without signature."""
    # Temporarily un-mock signature validation for this test
    from app.integrations.tiktok import TikTokClient
    
    def real_verify(self, payload: str, signature: str) -> bool:
        if not signature:
            return False
        # For testing, just check if signature exists
        return True
    
    monkeypatch.setattr(TikTokClient, "verify_webhook_signature", real_verify)
    
    webhook_data = {
        "event_type": "message",
        "user_id": "user_123",
        "message": "Test message",
        "conversation_id": "conv_123",
        "timestamp": 1234567890
    }
    
    response = client.post("/webhooks/tiktok", json=webhook_data)
    assert response.status_code == 401


# ============================================
# Message Sending - Async Tests
# ============================================

def test_send_message_async_returns_202(client: TestClient, sample_conversation, mock_celery_tasks):
    """Test send message returns 202 Accepted with job_id."""
    request_data = {
        "conversation_id": sample_conversation.id,
        "platform": "tiktok",
        "message": "This is an async test response"
    }
    
    response = client.post("/messages/send", json=request_data)
    
    # Should return 202 Accepted
    assert response.status_code == 202
    
    data = response.json()
    assert data["success"] is True
    assert "message_id" in data
    assert "job_id" in data
    assert data["job_id"] == "test_task_123"  # From mock
    
    # Verify Celery task was called
    assert mock_celery_tasks.delay.called


def test_send_message_creates_queued_message(client: TestClient, sample_conversation, db):
    """Test send message creates message with QUEUED status."""
    from app.models.database import Message, MessageStatus, MessageDirection
    
    request_data = {
        "conversation_id": sample_conversation.id,
        "platform": "tiktok",
        "message": "Test queued message"
    }
    
    response = client.post("/messages/send", json=request_data)
    assert response.status_code == 202
    
    data = response.json()
    message_id = data["message_id"]
    
    # Verify message in database has correct fields
    message = db.query(Message).filter(Message.id == message_id).first()
    assert message is not None
    assert message.status == MessageStatus.QUEUED
    assert message.direction == MessageDirection.OUTBOUND
    assert message.content == "Test queued message"


def test_send_message_conversation_not_found(client: TestClient):
    """Test send message returns error for non-existent conversation."""
    request_data = {
        "conversation_id": 99999,  # Non-existent
        "platform": "tiktok",
        "message": "Test message"
    }
    
    response = client.post("/messages/send", json=request_data)
    assert response.status_code == 404


# ============================================
# Conversation Endpoints - New Paths
# ============================================

def test_get_conversations_new_path(client: TestClient, sample_conversation):
    """Test GET /conversations works (new path)."""
    response = client.get("/conversations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_conversation_by_id_new_path(client: TestClient, sample_conversation):
    """Test GET /conversations/{id} works (new path)."""
    response = client.get(f"/conversations/{sample_conversation.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_conversation.id
    assert "messages" in data


def test_conversations_filter_by_priority(client: TestClient, sample_conversation, db):
    """Test filtering conversations by priority."""
    from app.models.database import Conversation, Platform, ConversationStatus
    
    # Create high priority conversation
    from tests.conftest import TestingSessionLocal
    user = sample_conversation.user
    high_priority_conv = Conversation(
        user_id=user.id,
        platform=Platform.TIKTOK,
        platform_conversation_id="high_priority_conv",
        status=ConversationStatus.ACTIVE,
        priority="high"
    )
    db.add(high_priority_conv)
    db.commit()
    
    response = client.get("/conversations?priority=high")
    assert response.status_code == 200
    data = response.json()
    
    # Should only return high priority conversations
    assert all(conv["priority"] == "high" for conv in data if "priority" in conv)


def test_conversations_filter_by_assigned_to(client: TestClient, sample_conversation, db):
    """Test filtering conversations by assigned agent."""
    sample_conversation.assigned_to = 5
    db.commit()
    
    response = client.get("/conversations?assigned_to=5")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) >= 1
    assert any(conv["id"] == sample_conversation.id for conv in data)


def test_old_conversation_path_not_found(client: TestClient):
    """Test old path /messages/conversations returns 404."""
    response = client.get("/messages/conversations")
    assert response.status_code == 404


# ============================================
# Analytics Endpoints
# ============================================

def test_get_metrics(client: TestClient):
    """Test analytics metrics endpoint."""
    response = client.get("/analytics/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_messages" in data
    assert "total_conversations" in data
    assert "escalation_rate" in data


def test_get_conversation_insights(client: TestClient):
    """Test conversation insights endpoint."""
    response = client.get("/analytics/conversations")
    assert response.status_code == 200
    data = response.json()
    assert "insights" in data
    assert "total_conversations" in data


def test_get_escalation_stats(client: TestClient):
    """Test escalation statistics endpoint."""
    response = client.get("/analytics/escalations")
    assert response.status_code == 200
    data = response.json()
    assert "total_escalations" in data
    assert "escalation_rate" in data


# ============================================
# Admin Endpoints
# ============================================

def test_escalate_conversation(client: TestClient, sample_conversation, db):
    """Test manual conversation escalation."""
    response = client.post(
        f"/admin/escalate/{sample_conversation.id}",
        json={"reason": "Customer requested manager"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["escalated"] is True
    assert data["reason"] == "Customer requested manager"
    
    # Verify in database
    from app.models.database import Conversation, ConversationStatus
    db.refresh(sample_conversation)
    assert sample_conversation.escalated is True
    assert sample_conversation.status == ConversationStatus.ESCALATED


def test_override_message(client: TestClient, sample_conversation, db):
    """Test overriding AI response."""
    from app.models.database import Message
    
    # Get a message from the conversation
    message = db.query(Message).filter(Message.conversation_id == sample_conversation.id).first()
    
    response = client.put(
        f"/admin/override/{message.id}",
        json={
            "new_content": "This is the corrected response",
            "reason": "AI made an error"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["new_content"] == "This is the corrected response"


def test_get_logs(client: TestClient):
    """Test retrieving system logs."""
    response = client.get("/admin/logs?level=INFO&limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data


# ============================================
# Agent Management Endpoints
# ============================================

def test_agent_status(client: TestClient):
    """Test agent status endpoint."""
    response = client.get("/admin/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "total_conversations" in data


def test_configure_agent(client: TestClient):
    """Test agent configuration endpoint."""
    response = client.post(
        "/admin/agent/configure",
        params={
            "config_key": "test_config",
            "config_value": "test_value",
            "description": "Test configuration"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["config_key"] == "test_config"


def test_agent_status_alias(client: TestClient):
    """Test /agent/status alias works."""
    response = client.get("/agent/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


# ============================================
# Prometheus Metrics
# ============================================

def test_get_prometheus_metrics(client: TestClient):
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
