from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum

class NodeType(str, Enum):
    USER_QUERY = "userQuery"
    KNOWLEDGE_BASE = "knowledgeBase"
    LLM_ENGINE = "llm"
    WEB_SEARCH = "webSearch"
    OUTPUT = "output"

class NodePosition(BaseModel):
    x: float
    y: float

class NodeHandle(BaseModel):
    id: str
    type: str  # "source" or "target"
    position: str  # "top", "bottom", "left", "right"

class BaseNodeConfig(BaseModel):
    label: str
    description: Optional[str] = None

class UserQueryNodeConfig(BaseNodeConfig):
    placeholder: str = "Enter your question here..."
    validation_rules: Dict[str, Any] = Field(default_factory=dict)

class KnowledgeBaseNodeConfig(BaseNodeConfig):
    file_id: Optional[int] = None
    embedding_model: str = "text-embedding-3-large"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    similarity_threshold: float = 0.7
    max_results: int = 5

class LLMNodeConfig(BaseNodeConfig):
    model: str = "gpt-3.5-turbo"
    api_key: Optional[str] = None
    prompt: str = "You are a helpful assistant."
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    system_message: Optional[str] = None

class WebSearchNodeConfig(BaseNodeConfig):
    api_key: Optional[str] = None
    search_engine: str = "google"  # google, bing, duckduckgo
    max_results: int = 5
    country: str = "us"
    language: str = "en"
    safe_search: str = "moderate"

class OutputNodeConfig(BaseNodeConfig):
    format: str = "text"  # text, json, markdown
    template: Optional[str] = None
    include_sources: bool = True
    include_metadata: bool = False

# Union type for all node configurations
NodeConfig = Union[
    UserQueryNodeConfig,
    KnowledgeBaseNodeConfig, 
    LLMNodeConfig,
    WebSearchNodeConfig,
    OutputNodeConfig
]

class WorkflowNode(BaseModel):
    id: str = Field(..., description="Unique node identifier")
    type: NodeType
    position: NodePosition
    data: NodeConfig
    handles: List[NodeHandle] = Field(default_factory=list)
    
class WorkflowEdge(BaseModel):
    id: str
    source: str  # source node id
    target: str  # target node id
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None
    type: str = "default"
    animated: bool = False
    style: Dict[str, Any] = Field(default_factory=dict)

class WorkflowConfiguration(BaseModel):
    nodes: List[WorkflowNode]
    edges: List[WorkflowEdge]
    viewport: Dict[str, Any] = Field(default_factory=dict)

class NodeValidationError(BaseModel):
    node_id: str
    field: str
    message: str

class NodeValidationResponse(BaseModel):
    is_valid: bool
    errors: List[NodeValidationError] = []
    warnings: List[str] = []

# Node execution schemas
class NodeExecutionContext(BaseModel):
    workflow_id: int
    session_id: Optional[int] = None
    user_id: int
    input_data: Dict[str, Any] = Field(default_factory=dict)
    global_context: Dict[str, Any] = Field(default_factory=dict)

class NodeExecutionResult(BaseModel):
    node_id: str
    status: str  # "success", "error", "skipped"
    output_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time: int  # milliseconds
    metadata: Dict[str, Any] = Field(default_factory=dict)
