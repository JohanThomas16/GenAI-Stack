from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import json

from app.core.auth import get_current_active_user, get_current_user_optional
from app.core.database import get_db
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, MessageType
from app.models.workflow import Workflow
from app.schemas.chat import (
    ChatSession as ChatSessionSchema,
    ChatSessionCreate,
    ChatSessionUpdate,
    ChatMessage as ChatMessageSchema,
    ChatMessageCreate,
    ChatExecutionRequest,
    ChatExecutionResponse,
    ChatHistoryRequest,
    ChatHistoryResponse
)
from app.services.workflow_engine import WorkflowEngine

router = APIRouter()
workflow_engine = WorkflowEngine()

@router.get("/sessions", response_model=List[ChatSessionSchema])
def get_chat_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    workflow_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user chat sessions"""
    query = db.query(ChatSession).filter(ChatSession.user_id == current_user.id)
    
    if workflow_id:
        query = query.filter(ChatSession.workflow_id == workflow_id)
    
    sessions = query.order_by(ChatSession.last_activity.desc()).offset(skip).limit(limit).all()
    
    # Add message count
    for session in sessions:
        session.message_count = len(session.messages)
    
    return sessions

@router.post("/sessions", response_model=ChatSessionSchema, status_code=status.HTTP_201_CREATED)
def create_chat_session(
    session_data: ChatSessionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create new chat session"""
    
    # Validate workflow if provided
    if session_data.workflow_id:
        workflow = db.query(Workflow).filter(
            Workflow.id == session_data.workflow_id,
            Workflow.owner_id == current_user.id
        ).first()
        
        if not workflow:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workflow not found"
            )
    
    session = ChatSession(
        title=session_data.title,
        workflow_id=session_data.workflow_id,
        user_id=current_user.id,
        session_metadata=session_data.session_metadata
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    session.message_count = 0
    return session

@router.get("/sessions/{session_id}", response_model=ChatSessionSchema)
def get_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get specific chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    session.message_count = len(session.messages)
    return session

@router.put("/sessions/{session_id}", response_model=ChatSessionSchema)
def update_chat_session(
    session_id: int,
    session_data: ChatSessionUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    update_data = session_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    # Update last activity
    from sqlalchemy.sql import func
    session.last_activity = func.now()
    
    db.commit()
    db.refresh(session)
    
    session.message_count = len(session.messages)
    return session

@router.delete("/sessions/{session_id}")
def delete_chat_session(
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete chat session"""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.post("/execute", response_model=ChatExecutionResponse)
async def execute_chat(
    execution_request: ChatExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Execute chat message through workflow"""
    
    # Get or create session
    session = None
    if execution_request.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == execution_request.session_id,
            ChatSession.user_id == current_user.id
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
    else:
        # Create new session
        session = ChatSession(
            workflow_id=execution_request.workflow_id,
            user_id=current_user.id
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Save user message
    user_message = ChatMessage(
        content=execution_request.message,
        message_type=MessageType.USER,
        session_id=session.id
    )
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    
    try:
        # Execute workflow if specified
        if session.workflow_id:
            workflow = db.query(Workflow).filter(
                Workflow.id == session.workflow_id,
                Workflow.owner_id == current_user.id
            ).first()
            
            if not workflow:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Workflow not found"
                )
            
            # Execute workflow
            result = await workflow_engine.execute_workflow(
                workflow=workflow,
                input_data={"user_message": execution_request.message, **execution_request.context},
                user_id=current_user.id,
                session_id=session.id,
                db=db
            )
            
            response_content = result.result.get("response", "No response generated")
            execution_time = result.execution_time
            
        else:
            # Simple echo response for testing
            response_content = f"Echo: {execution_request.message}"
            execution_time = 100
        
        # Save assistant message
        assistant_message = ChatMessage(
            content=response_content,
            message_type=MessageType.ASSISTANT,
            session_id=session.id,
            execution_time=execution_time
        )
        db.add(assistant_message)
        
        # Update session last activity
        from sqlalchemy.sql import func
        session.last_activity = func.now()
        
        db.commit()
        db.refresh(assistant_message)
        
        return ChatExecutionResponse(
            message_id=assistant_message.id,
            session_id=session.id,
            response=response_content,
            execution_time=execution_time,
            timestamp=assistant_message.created_at
        )
        
    except Exception as e:
        # Save error message
        error_message = ChatMessage(
            content=f"Error: {str(e)}",
            message_type=MessageType.ASSISTANT,
            session_id=session.id,
            metadata={"error": True, "error_message": str(e)}
        )
        db.add(error_message)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat execution failed: {str(e)}"
        )

@router.get("/sessions/{session_id}/messages", response_model=ChatHistoryResponse)
def get_chat_messages(
    session_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get chat messages for a session"""
    
    # Verify session ownership
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get messages
    query = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id,
        ChatMessage.is_deleted == False
    )
    
    total_count = query.count()
    messages = query.order_by(ChatMessage.created_at.asc()).offset(skip).limit(limit).all()
    
    return ChatHistoryResponse(
        messages=messages,
        total_count=total_count,
        has_more=(skip + len(messages)) < total_count
    )

# WebSocket endpoint for real-time chat
@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Here you would implement real-time message processing
            # For now, just echo back
            response = {
                "type": "message",
                "content": f"Echo: {message_data.get('message', '')}",
                "timestamp": "2025-09-07T14:43:00Z"
            }
            
            await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))
