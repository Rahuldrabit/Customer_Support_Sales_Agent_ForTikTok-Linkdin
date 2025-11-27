"""Message handling endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.dependencies import get_db
from app.models.schemas import (
    SendMessageRequest,
    SendMessageResponse,
    ConversationResponse,
    MessageResponse
)
from app.models.database import Conversation, Message, User, Platform, ConversationStatus, MessageSender, MessageDirection, MessageStatus
from app.services.message_processor import send_message_to_platform
from app.services.tasks import send_message_task
from app.utils.logger import log
from app.utils.exceptions import ConversationNotFoundError

router = APIRouter()


@router.post("/send", response_model=SendMessageResponse, status_code=status.HTTP_202_ACCEPTED)
async def send_message(
    request: SendMessageRequest,
    db: Session = Depends(get_db)
):
    """
    Enqueue a message to be sent to a platform (async).
    
    Args:
        request: Send message request
        db: Database session
        
    Returns:
        Send message response with job_id (202 Accepted)
    """
    log.info(f"Enqueueing message for conversation {request.conversation_id}")
    
    try:
        # Get conversation
        conversation = db.query(Conversation).filter(
            Conversation.id == request.conversation_id
        ).first()
        
        if not conversation:
            raise ConversationNotFoundError(request.conversation_id)
        
        # Create message record with QUEUED status
        message = Message(
            conversation_id=conversation.id,
            sender_type=MessageSender.AGENT,
            direction=MessageDirection.OUTBOUND,
            status=MessageStatus.QUEUED,
            content=request.message
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Enqueue send job
        platform = Platform(request.platform)
        task = send_message_task.delay(
            conversation_id=conversation.id,
            platform=platform.value,
            message_content=request.message,
            platform_conversation_id=conversation.platform_conversation_id,
            message_id=message.id
        )
        
        log.info(f"Message {message.id} queued with task {task.id}")
        
        return SendMessageResponse(
            success=True,
            message_id=message.id,
            job_id=task.id
        )
            
    except ConversationNotFoundError:
        raise
    except Exception as e:
        log.error(f"Error enqueueing message: {e}")
        return SendMessageResponse(
            success=False,
            error=str(e)
        )
