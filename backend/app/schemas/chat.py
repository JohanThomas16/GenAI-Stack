from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    message_type: MessageType = MessageType.USER

class ChatMessageCreate(ChatMessageBase):
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatMessageUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    metadata: Optional[Dict[str, Any]] = None

class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    metadata: Dict[str, Any]
    execution_time: Optional[int] = None
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    is_edited: bool = False
    is_deleted: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ChatSessionBase(BaseModel):
    title: Optional[str] = None
    workflow_id: Optional[int] = None

class ChatSessionCreate(ChatSessionBase):
    session_metadata: Dict[str, Any] = Field(default_factory=dict)

class ChatSessionUpdate(BaseModel):
    title: Optional[str] = None
    is_active: Optional[bool] = None
    session_metadata: Optional[Dict[str, Any]] = None

class ChatSession(ChatSessionBase):
    id: int
    user_id: int
    is_active: bool
    started_at: datetime
    ended_at: Optional[datetime] = None
    last_activity: datetime
    session_metadata: Dict[str, Any]
    message_count: int = 0
    
    class Config:
        from_attributes = True

class ChatSessionWithMessages(ChatSession):
    messages: List[ChatMessage] = []

# Chat execution schemas
class ChatExecutionRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[int] = None
    workflow_id: Optional[int] = None
    context: Dict[str, Any] = Field(default_factory=dict)

class ChatExecutionResponse(BaseModel):
    message_id: int
    session_id: int
    response: str
    execution_time: int  # milliseconds
    tokens_used: Optional[int] = None
    model_used: Optional[str] = None
    timestamp: datetime
    
class ChatHistoryRequest(BaseModel):
    session_id: Optional[int] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]
    total_count: int
    has_more: bool
