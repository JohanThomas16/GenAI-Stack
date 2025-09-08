from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.nodes import WorkflowNode

class WorkflowBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_public: bool = False
    is_template: bool = False
    tags: List[str] = []
    category: str = "general"

class WorkflowCreate(WorkflowBase):
    configuration: Dict[str, Any] = Field(default_factory=dict)

class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None

class WorkflowInDBBase(WorkflowBase):
    id: int
    owner_id: int
    is_active: bool
    execution_count: int
    success_count: int
    error_count: int
    last_executed: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    configuration: Dict[str, Any]
    
    class Config:
        from_attributes = True

class Workflow(WorkflowInDBBase):
    node_count: int = 0
    success_rate: float = 0.0

class WorkflowInDB(WorkflowInDBBase):
    pass

# Workflow execution schemas
class WorkflowExecutionRequest(BaseModel):
    workflow_id: int
    input_data: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[int] = None

class WorkflowExecutionResponse(BaseModel):
    execution_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: int  # milliseconds
    timestamp: datetime

class WorkflowValidationRequest(BaseModel):
    configuration: Dict[str, Any]

class WorkflowValidationResponse(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []

# Workflow template schemas
class WorkflowTemplate(BaseModel):
    id: int
    name: str
    description: str
    category: str
    tags: List[str]
    configuration: Dict[str, Any]
    usage_count: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True
