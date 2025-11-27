"""Conversation endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.dependencies import get_db
from app.models.schemas import ConversationResponse
from app.models.database import Conversation, Platform, ConversationStatus
from app.utils.logger import log
from app.utils.exceptions import ConversationNotFoundError

router = APIRouter()


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get conversation details with message history.
    
    Args:
        conversation_id: Conversation ID
        db: Database session
        
    Returns:
        Conversation details
    """
    log.info(f"Retrieving conversation {conversation_id}")
    
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise ConversationNotFoundError(conversation_id)
    
    return conversation


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    escalated: Optional[bool] = Query(None),
    priority: Optional[str] = Query(None),
    assigned_to: Optional[int] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0),
    db: Session = Depends(get_db)
):
    """
    List all conversations with optional filters.
    
    Args:
        platform: Filter by platform (tiktok/linkedin)
        status: Filter by status (active/escalated/closed)
        escalated: Filter by escalation status
        priority: Filter by priority (high/normal/low)
        assigned_to: Filter by assigned agent ID
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session
        
    Returns:
        List of conversations
    """
    log.info(f"Listing conversations (platform={platform}, status={status})")
    
    query = db.query(Conversation)
    
    # Apply filters using enums where possible
    if platform:
        try:
            platform_enum = Platform(platform)
            query = query.filter(Conversation.platform == platform_enum)
        except ValueError:
            # Invalid platform string, return empty list
            return []
    if status:
        try:
            status_enum = ConversationStatus(status)
            query = query.filter(Conversation.status == status_enum)
        except ValueError:
            return []
    if escalated is not None:
        query = query.filter(Conversation.escalated == escalated)
    if priority:
        query = query.filter(Conversation.priority == priority)
    if assigned_to is not None:
        query = query.filter(Conversation.assigned_to == assigned_to)
    
    # Order by most recent
    query = query.order_by(desc(Conversation.updated_at))
    
    # Pagination
    conversations = query.offset(offset).limit(limit).all()
    
    return conversations
