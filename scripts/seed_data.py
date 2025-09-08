#!/usr/bin/env python3
"""
GenAI Stack Data Seeding Script
===============================
This script seeds the database with initial data for development and testing.
"""

import os
import sys
import logging
from datetime import datetime, timezone
import json

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

from app.models.user import User
from app.models.workflow import Workflow
from app.models.document import Document
from app.models.chat import ChatSession, ChatMessage, MessageType
from app.core.database import Base
from app.core.config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_engine_and_session():
    """Create database engine and session"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal()

def seed_users(db):
    """Seed user data"""
    logger.info("Seeding users...")
    
    users_data = [
        {
            "email": "admin@genai-stack.com",
            "password": "admin123",
            "full_name": "Admin User",
            "is_superuser": True,
            "is_active": True,
            "bio": "System administrator",
            "company": "GenAI Stack Inc.",
            "location": "San Francisco, CA"
        },
        {
            "email": "demo@genai-stack.com",
            "password": "demo123",
            "full_name": "Demo User",
            "is_superuser": False,
            "is_active": True,
            "bio": "Demo user for testing workflows",
            "company": "Demo Corp",
            "location": "New York, NY"
        },
        {
            "email": "john.doe@example.com",
            "password": "password123",
            "full_name": "John Doe",
            "is_superuser": False,
            "is_active": True,
            "bio": "Software developer interested in AI workflows",
            "company": "Tech Innovations",
            "location": "Austin, TX"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            logger.info(f"User {user_data['email']} already exists, skipping...")
            created_users.append(existing_user)
            continue
        
        # Create new user
        password = user_data.pop("password")
        user = User(
            **user_data,
            password_hash=get_password_hash(password)
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        created_users.append(user)
        logger.info(f"Created user: {user.email}")
    
    return created_users

def seed_workflows(db, users):
    """Seed workflow data"""
    logger.info("Seeding workflows...")
    
    # Sample workflow configurations
    workflows_data = [
        {
            "name": "Customer Support Bot",
            "description": "AI-powered customer support workflow that answers questions using knowledge base",
            "owner": users[0],  # Admin user
            "configuration": {
                "nodes": [
                    {
                        "id": "user-query-1",
                        "type": "userQuery",
                        "position": {"x": 100, "y": 100},
                        "data": {
                            "label": "Customer Question",
                            "placeholder": "What can I help you with today?",
                            "description": "Entry point for customer queries"
                        }
                    },
                    {
                        "id": "knowledge-base-1",
                        "type": "knowledgeBase",
                        "position": {"x": 300, "y": 100},
                        "data": {
                            "label": "Help Documentation",
                            "description": "Search through help documents",
                            "embeddingModel": "text-embedding-3-large",
                            "chunkSize": 1000,
                            "chunkOverlap": 200,
                            "similarityThreshold": 0.7,
                            "maxResults": 5
                        }
                    },
                    {
                        "id": "llm-1",
                        "type": "llm",
                        "position": {"x": 500, "y": 100},
                        "data": {
                            "label": "AI Assistant",
                            "description": "Generate helpful responses",
                            "model": "gpt-3.5-turbo",
                            "prompt": "You are a helpful customer support assistant. Use the provided context to answer customer questions accurately and helpfully.",
                            "temperature": 0.7,
                            "maxTokens": 300
                        }
                    },
                    {
                        "id": "output-1",
                        "type": "output",
                        "position": {"x": 700, "y": 100},
                        "data": {
                            "label": "Support Response",
                            "description": "Final response to customer",
                            "format": "text",
                            "includeSources": True,
                            "includeMetadata": False
                        }
                    }
                ],
                "edges": [
                    {
                        "id": "edge-1",
                        "source": "user-query-1",
                        "target": "knowledge-base-1"
                    },
                    {
                        "id": "edge-2",
                        "source": "knowledge-base-1",
                        "target": "llm-1"
                    },
                    {
                        "id": "edge-3",
                        "source": "llm-1",
                        "target": "output-1"
                    }
                ]
            },
            "category": "customer-support",
            "tags": ["support", "chatbot", "knowledge-base"],
            "is_active": True,
            "is_public": True
        },
        {
            "name": "Document Q&A Assistant",
            "description": "Upload documents and ask questions about their content",
            "owner": users[1],  # Demo user
            "configuration": {
                "nodes": [
                    {
                        "id": "user-query-1",
                        "type": "userQuery",
                        "position": {"x": 100, "y": 100},
                        "data": {
                            "label": "Document Question",
                            "placeholder": "Ask a question about your documents...",
                            "description": "What would you like to know?"
                        }
                    },
                    {
                        "id": "knowledge-base-1",
                        "type": "knowledgeBase",
                        "position": {"x": 300, "y": 100},
                        "data": {
                            "label": "Uploaded Documents",
                            "description": "Search through your documents",
                            "embeddingModel": "text-embedding-3-large",
                            "chunkSize": 800,
                            "chunkOverlap": 150,
                            "similarityThreshold": 0.75,
                            "maxResults": 7
                        }
                    },
                    {
                        "id": "llm-1",
                        "type": "llm",
                        "position": {"x": 500, "y": 100},
                        "data": {
                            "label": "Document Analyzer",
                            "description": "Analyze and answer based on documents",
                            "model": "gpt-4",
                            "prompt": "You are an expert document analyst. Answer questions based strictly on the provided document context. If the answer isn't in the documents, say so clearly.",
                            "temperature": 0.3,
                            "maxTokens": 500
                        }
                    },
                    {
                        "id": "output-1",
                        "type": "output",
                        "position": {"x": 700, "y": 100},
                        "data": {
                            "label": "Document Answer",
                            "description": "Answer with source citations",
                            "format": "markdown",
                            "includeSources": True,
                            "includeMetadata": True
                        }
                    }
                ],
                "edges": [
                    {
                        "id": "edge-1",
                        "source": "user-query-1",
                        "target": "knowledge-base-1"
                    },
                    {
                        "id": "edge-2",
                        "source": "knowledge-base-1",
                        "target": "llm-1"
                    },
                    {
                        "id": "edge-3",
                        "source": "llm-1",
                        "target": "output-1"
                    }
                ]
            },
            "category": "document-analysis",
            "tags": ["documents", "q&a", "analysis"],
            "is_active": True,
            "is_public": False
        },
        {
            "name": "Research Assistant with Web Search",
            "description": "AI assistant that can search the web for current information",
            "owner": users[2],  # John Doe
            "configuration": {
                "nodes": [
                    {
                        "id": "user-query-1",
                        "type": "userQuery",
                        "position": {"x": 50, "y": 100},
                        "data": {
                            "label": "Research Query",
                            "placeholder": "What would you like to research?",
                            "description": "Enter your research question"
                        }
                    },
                    {
                        "id": "web-search-1",
                        "type": "webSearch",
                        "position": {"x": 250, "y": 50},
                        "data": {
                            "label": "Web Search",
                            "description": "Search for current information",
                            "searchEngine": "google",
                            "maxResults": 5,
                            "country": "us",
                            "language": "en"
                        }
                    },
                    {
                        "id": "knowledge-base-1",
                        "type": "knowledgeBase",
                        "position": {"x": 250, "y": 150},
                        "data": {
                            "label": "Knowledge Base",
                            "description": "Search existing
