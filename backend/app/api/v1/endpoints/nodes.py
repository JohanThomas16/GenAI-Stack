from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.nodes import (
    NodeConfig,
    NodeType,
    NodeValidationResponse,
    NodeExecutionContext,
    NodeExecutionResult
)
from app.services.node_processor import NodeProcessor

router = APIRouter()
node_processor = NodeProcessor()

@router.get("/types", response_model=List[str])
def get_node_types() -> Any:
    """Get all available node types"""
    return [node_type.value for node_type in NodeType]

@router.get("/config/{node_type}")
def get_node_config_schema(node_type: NodeType) -> Any:
    """Get configuration schema for a specific node type"""
    schemas = {
        NodeType.USER_QUERY: {
            "type": "object",
            "properties": {
                "label": {"type": "string", "minLength": 1},
                "placeholder": {"type": "string", "default": "Enter your question here..."},
                "validation_rules": {"type": "object", "default": {}}
            },
            "required": ["label"]
        },
        NodeType.KNOWLEDGE_BASE: {
            "type": "object", 
            "properties": {
                "label": {"type": "string", "minLength": 1},
                "file_id": {"type": "integer", "nullable": True},
                "embedding_model": {"type": "string", "default": "text-embedding-3-large"},
                "chunk_size": {"type": "integer", "default": 1000, "minimum": 100},
                "chunk_overlap": {"type": "integer", "default": 200, "minimum": 0},
                "similarity_threshold": {"type": "number", "default": 0.7, "minimum": 0, "maximum": 1},
                "max_results": {"type": "integer", "default": 5, "minimum": 1}
            },
            "required": ["label"]
        },
        NodeType.LLM_ENGINE: {
            "type": "object",
            "properties": {
                "label": {"type": "string", "minLength": 1},
                "model": {"type": "string", "default": "gpt-3.5-turbo"},
                "api_key": {"type": "string", "nullable": True},
                "prompt": {"type": "string", "default": "You are a helpful assistant."},
                "temperature": {"type": "number", "default": 0.7, "minimum": 0, "maximum": 2},
                "max_tokens": {"type": "integer", "nullable": True, "minimum": 1},
                "top_p": {"type": "number", "default": 1.0, "minimum": 0, "maximum": 1},
                "frequency_penalty": {"type": "number", "default": 0.0, "minimum": -2, "maximum": 2},
                "presence_penalty": {"type": "number", "default": 0.0, "minimum": -2, "maximum": 2}
            },
            "required": ["label", "model", "prompt"]
        },
        NodeType.WEB_SEARCH: {
            "type": "object",
            "properties": {
                "label": {"type": "string", "minLength": 1},
                "api_key": {"type": "string", "nullable": True},
                "search_engine": {"type": "string", "default": "google", "enum": ["google", "bing", "duckduckgo"]},
                "max_results": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20},
                "country": {"type": "string", "default": "us"},
                "language": {"type": "string", "default": "en"},
                "safe_search": {"type": "string", "default": "moderate", "enum": ["off", "moderate", "strict"]}
            },
            "required": ["label"]
        },
        NodeType.OUTPUT: {
            "type": "object",
            "properties": {
                "label": {"type": "string", "minLength": 1},
                "format": {"type": "string", "default": "text", "enum": ["text", "json", "markdown"]},
                "template": {"type": "string", "nullable": True},
                "include_sources": {"type": "boolean", "default": True},
                "include_metadata": {"type": "boolean", "default": False}
            },
            "required": ["label"]
        }
    }
    
    schema = schemas.get(node_type)
    if not schema:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schema not found for node type: {node_type}"
        )
    
    return schema

@router.post("/validate", response_model=NodeValidationResponse)
async def validate_node_config(
    node_type: NodeType,
    config: dict,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Validate node configuration"""
    try:
        validation_result = await node_processor.validate_node_config(node_type, config)
        return validation_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(e)}"
        )

@router.post("/execute", response_model=NodeExecutionResult)
async def execute_node(
    node_type: NodeType,
    config: dict,
    context: NodeExecutionContext,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Execute a single node with given configuration and context"""
    try:
        result = await node_processor.execute_node(
            node_type=node_type,
            config=config,
            context=context,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Node execution failed: {str(e)}"
        )

@router.get("/defaults/{node_type}")
def get_node_defaults(node_type: NodeType) -> Any:
    """Get default configuration for a node type"""
    defaults = {
        NodeType.USER_QUERY: {
            "label": "User Query",
            "placeholder": "Enter your question here...",
            "validation_rules": {}
        },
        NodeType.KNOWLEDGE_BASE: {
            "label": "Knowledge Base",
            "embedding_model": "text-embedding-3-large",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "similarity_threshold": 0.7,
            "max_results": 5
        },
        NodeType.LLM_ENGINE: {
            "label": "LLM Engine",
            "model": "gpt-3.5-turbo",
            "prompt": "You are a helpful assistant.",
            "temperature": 0.7,
            "top_p": 1.0,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0
        },
        NodeType.WEB_SEARCH: {
            "label": "Web Search",
            "search_engine": "google",
            "max_results": 5,
            "country": "us",
            "language": "en",
            "safe_search": "moderate"
        },
        NodeType.OUTPUT: {
            "label": "Output",
            "format": "text",
            "include_sources": True,
            "include_metadata": False
        }
    }
    
    return defaults.get(node_type, {})
