"""
Chat API endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.db.database import get_db
from app.schemas.schemas import ChatMessage, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("/message", response_model=ChatResponse)
async def send_message(message: ChatMessage, db: Session = Depends(get_db)):
    """Send a message to the chat bot"""
    
    # Generate session ID if not provided
    session_id = message.session_id or str(uuid.uuid4())
    
    # Process message
    chat_service = ChatService(db)
    response = chat_service.process_message(message.message, session_id)
    
    return ChatResponse(**response)


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, db: Session = Depends(get_db)):
    """Get chat history for a session"""
    from app.db.models import ChatHistory
    
    history = db.query(ChatHistory).filter(
        ChatHistory.session_id == session_id
    ).order_by(ChatHistory.created_at).all()
    
    return {
        "session_id": session_id,
        "messages": [
            {
                "user": h.user_message,
                "bot": h.bot_response,
                "intent": h.intent,
                "timestamp": h.created_at.isoformat()
            }
            for h in history
        ]
    }
