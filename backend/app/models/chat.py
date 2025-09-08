from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

from app.core.database import Base

class MessageType(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Session metadata
    session_metadata = Column(JSON, default=dict)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="chat_sessions")
    
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    workflow = relationship("Workflow", back_populates="chat_sessions")
    
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession(id={self.id}, user_id={self.user_id}, workflow_id={self.workflow_id})>"
    
    @property
    def message_count(self):
        """Return number of messages in session"""
        return len(self.messages)
    
    @property
    def duration(self):
        """Return session duration in seconds"""
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds()
        return (func.now() - self.started_at).total_seconds()
    
    def end_session(self):
        """Mark session as ended"""
        self.is_active = False
        self.ended_at = func.now()

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    message_type = Column(SQLEnum(MessageType), nullable=False)
    
    # Message metadata
    metadata = Column(JSON, default=dict)  # tokens_used, model, execution_time, etc.
    
    # Execution information
    execution_time = Column(Integer, nullable=True)  # milliseconds
    tokens_used = Column(Integer, nullable=True)
    model_used = Column(String(100), nullable=True)
    
    # Status
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage(id={self.id}, type='{self.message_type}', session_id={self.session_id})>"
    
    @property
    def word_count(self):
        """Return word count of message content"""
        return len(self.content.split())
    
    @property
    def char_count(self):
        """Return character count of message content"""
        return len(self.content)
