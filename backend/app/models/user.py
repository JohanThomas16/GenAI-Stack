from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Profile information
    bio = Column(Text, nullable=True)
    company = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    
    # Preferences
    theme = Column(String(20), default="light")
    language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    
    # Relationships
    workflows = relationship("Workflow", back_populates="owner", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"
    
    @property
    def display_name(self):
        """Return display name (full_name or email)"""
        return self.full_name or self.email.split('@')[0]
