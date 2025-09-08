from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, BigInteger, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    mime_type = Column(String(100), nullable=False)
    
    # Processing status
    status = Column(String(50), default="uploaded")  # uploaded, processing, processed, error
    processing_error = Column(Text, nullable=True)
    
    # Extracted content
    content = Column(Text, nullable=True)
    content_hash = Column(String(64), nullable=True)  # SHA-256 hash of content
    
    # Embedding information
    embedding_model = Column(String(100), nullable=True)
    embedding_dimensions = Column(Integer, nullable=True)
    chunk_count = Column(Integer, default=0)
    
    # Metadata extracted from document
    metadata = Column(JSON, default=dict)  # title, author, creation_date, etc.
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="documents")
    
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=True)
    workflow = relationship("Workflow", back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"
    
    @property
    def is_processed(self):
        """Check if document has been processed"""
        return self.status == "processed"
    
    @property
    def size_mb(self):
        """Return file size in MB"""
        return round(self.file_size / (1024 * 1024), 2)
    
    def mark_processing(self):
        """Mark document as being processed"""
        self.status = "processing"
    
    def mark_processed(self):
        """Mark document as successfully processed"""
        self.status = "processed"
        self.processed_at = func.now()
    
    def mark_error(self, error_message: str):
        """Mark document processing as failed"""
        self.status = "error"
        self.processing_error = error_message
