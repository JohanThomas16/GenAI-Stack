from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Workflow configuration stored as JSON
    configuration = Column(JSON, nullable=False, default=dict)
    
    # Status and visibility
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    is_template = Column(Boolean, default=False)
    
    # Execution statistics
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    last_executed = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Tags and categorization
    tags = Column(JSON, default=list)  # List of string tags
    category = Column(String(100), default="general")
    
    # Owner relationship
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="workflows")
    
    # Related records
    documents = relationship("Document", back_populates="workflow", cascade="all, delete-orphan")
    chat_sessions = relationship("ChatSession", back_populates="workflow", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Workflow(id={self.id}, name='{self.name}', owner_id={self.owner_id})>"
    
    @property
    def node_count(self):
        """Return number of nodes in the workflow"""
        return len(self.configuration.get("nodes", []))
    
    @property
    def success_rate(self):
        """Calculate workflow success rate"""
        if self.execution_count == 0:
            return 0.0
        return (self.success_count / self.execution_count) * 100
    
    def increment_execution(self, success: bool = True):
        """Increment execution counters"""
        self.execution_count += 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
        self.last_executed = func.now()
