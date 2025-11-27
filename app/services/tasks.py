"""Celery tasks for asynchronous processing."""

from celery import Celery
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.config import settings
from app.models.database import SessionLocal, Platform, Message, MessageStatus, MessageSender, MessageDirection
from app.services.message_processor import process_incoming_message, send_message_to_platform
from app.utils.logger import log

# Configure Celery with fast-fail connection settings for tests
celery_app = Celery(
    "agent_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure broker connection to fail fast (don't block on retries)
celery_app.conf.update(
    broker_connection_retry_on_startup=False,
    broker_connection_retry=False,
    broker_connection_max_retries=0,
    broker_connection_timeout=1,
    result_backend_transport_options={
        'retry_policy': {'max_retries': 0}
    },
)


@celery_app.task(name="process_incoming_message_task")
def process_incoming_message_task(
    platform: str,
    platform_user_id: str,
    platform_conversation_id: str,
    message_content: str,
    username: Optional[str] = None,
    extra_payload: Optional[dict] = None,
):
    """Celery task wrapper around process_incoming_message.

    Uses a fresh DB session and serializable primitives only.
    """
    log.info(
        f"[Celery] Processing message (platform={platform}, conv={platform_conversation_id})"
    )
    db: Session = SessionLocal()
    try:
        # Convert platform enum from string
        plat_enum = Platform(platform)
        # Run async service in blocking context
        # Use a new event loop to avoid conflicts with existing loops
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running (e.g., in tests), use nest_asyncio or run in thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        process_incoming_message(
                            db=db,
                            platform=plat_enum,
                            platform_user_id=platform_user_id,
                            platform_conversation_id=platform_conversation_id,
                            message_content=message_content,
                            extra_payload=extra_payload,
                            username=username,
                        )
                    )
                    future.result()
            else:
                loop.run_until_complete(
                    process_incoming_message(
                        db=db,
                        platform=plat_enum,
                        platform_user_id=platform_user_id,
                        platform_conversation_id=platform_conversation_id,
                        message_content=message_content,
                        extra_payload=extra_payload,
                        username=username,
                    )
                )
        except RuntimeError:
            # No event loop exists, create new one
            asyncio.run(
                process_incoming_message(
                    db=db,
                    platform=plat_enum,
                    platform_user_id=platform_user_id,
                    platform_conversation_id=platform_conversation_id,
                    message_content=message_content,
                    extra_payload=extra_payload,
                    username=username,
                )
            )
        log.info("[Celery] Message processed successfully")
        return {"status": "ok"}
    except Exception as e:
        log.error(f"[Celery] Error processing message: {e}")
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()


@celery_app.task(name="send_message_task")
def send_message_task(
    conversation_id: int,
    platform: str,
    message_content: str,
    platform_conversation_id: str,
    message_id: int,
):
    """
    Celery task to send message to platform asynchronously.
    
    Args:
        conversation_id: Internal conversation ID
        platform: Platform string ('tiktok' or 'linkedin')
        message_content: Message to send
        platform_conversation_id: Platform-specific conversation ID
        message_id: Internal message ID (already created in DB)
    """
    log.info(f"[Celery] Sending message {message_id} to {platform}")
    db: Session = SessionLocal()
    
    try:
        plat_enum = Platform(platform)
        
        # Get the message record
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            log.error(f"Message {message_id} not found")
            return {"status": "error", "detail": "Message not found"}
        
        # Update status to queued
        message.status = MessageStatus.QUEUED
        db.commit()
        
        # Send to platform
        import asyncio
        success = asyncio.run(
            send_message_to_platform(
                platform=plat_enum,
                conversation_id=platform_conversation_id,
                message=message_content,
                db=db
            )
        )
        
        # Update status based on result
        if success:
            message.status = MessageStatus.SENT
            log.info(f"[Celery] Message {message_id} sent successfully")
        else:
            message.status = MessageStatus.FAILED
            log.error(f"[Celery] Failed to send message {message_id}")
        
        db.commit()
        
        return {"status": "sent" if success else "failed", "message_id": message_id}
        
    except Exception as e:
        log.error(f"[Celery] Error in send_message_task: {e}")
        # Mark message as failed
        try:
            message = db.query(Message).filter(Message.id == message_id).first()
            if message:
                message.status = MessageStatus.FAILED
                db.commit()
        except Exception:
            pass
        return {"status": "error", "detail": str(e)}
    finally:
        db.close()
