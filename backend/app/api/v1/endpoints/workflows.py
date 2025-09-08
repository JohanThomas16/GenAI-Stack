from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.models.user import User
from app.models.workflow import Workflow
from app.schemas.workflow import (
    Workflow as WorkflowSchema,
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowExecutionRequest,
    WorkflowExecutionResponse,
    WorkflowValidationRequest,
    WorkflowValidationResponse
)
from app.services.workflow_engine import WorkflowEngine

router = APIRouter()
workflow_engine = WorkflowEngine()

@router.get("/", response_model=List[WorkflowSchema])
def get_workflows(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    is_public: Optional[bool] = Query(None),
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get user workflows with optional filtering"""
    query = db.query(Workflow).filter(Workflow.owner_id == current_user.id)
    
    if is_public is not None:
        query = query.filter(Workflow.is_public == is_public)
    
    if category:
        query = query.filter(Workflow.category == category)
    
    if tag:
        query = query.filter(Workflow.tags.contains([tag]))
    
    workflows = query.offset(skip).limit(limit).all()
    
    # Add computed properties
    for workflow in workflows:
        workflow.node_count = len(workflow.configuration.get("nodes", []))
        workflow.success_rate = workflow.success_rate
    
    return workflows

@router.post("/", response_model=WorkflowSchema, status_code=status.HTTP_201_CREATED)
def create_workflow(
    workflow_data: WorkflowCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create a new workflow"""
    workflow = Workflow(
        **workflow_data.dict(),
        owner_id=current_user.id
    )
    
    db.add(workflow)
    db.commit()
    db.refresh(workflow)
    
    # Add computed properties
    workflow.node_count = len(workflow.configuration.get("nodes", []))
    workflow.success_rate = 0.0
    
    return workflow

@router.get("/{workflow_id}", response_model=WorkflowSchema)
def get_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Get specific workflow by ID"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Add computed properties
    workflow.node_count = len(workflow.configuration.get("nodes", []))
    workflow.success_rate = workflow.success_rate
    
    return workflow

@router.put("/{workflow_id}", response_model=WorkflowSchema)
def update_workflow(
    workflow_id: int,
    workflow_data: WorkflowUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Update workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    update_data = workflow_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    
    # Add computed properties
    workflow.node_count = len(workflow.configuration.get("nodes", []))
    workflow.success_rate = workflow.success_rate
    
    return workflow

@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Delete workflow"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    db.delete(workflow)
    db.commit()
    
    return {"message": "Workflow deleted successfully"}

@router.post("/{workflow_id}/execute", response_model=WorkflowExecutionResponse)
async def execute_workflow(
    workflow_id: int,
    execution_request: WorkflowExecutionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Execute workflow with given input"""
    workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    try:
        result = await workflow_engine.execute_workflow(
            workflow=workflow,
            input_data=execution_request.input_data,
            user_id=current_user.id,
            session_id=execution_request.session_id,
            db=db
        )
        
        # Update execution statistics
        workflow.increment_execution(success=True)
        db.commit()
        
        return result
        
    except Exception as e:
        # Update execution statistics
        workflow.increment_execution(success=False)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Workflow execution failed: {str(e)}"
        )

@router.post("/validate", response_model=WorkflowValidationResponse)
async def validate_workflow(
    validation_request: WorkflowValidationRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Validate workflow configuration"""
    try:
        validation_result = await workflow_engine.validate_workflow(
            configuration=validation_request.configuration
        )
        return validation_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation failed: {str(e)}"
        )

@router.post("/{workflow_id}/duplicate", response_model=WorkflowSchema)
def duplicate_workflow(
    workflow_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Duplicate an existing workflow"""
    original_workflow = db.query(Workflow).filter(
        Workflow.id == workflow_id,
        Workflow.owner_id == current_user.id
    ).first()
    
    if not original_workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found"
        )
    
    # Create duplicate
    duplicate = Workflow(
        name=f"{original_workflow.name} (Copy)",
        description=original_workflow.description,
        configuration=original_workflow.configuration,
        category=original_workflow.category,
        tags=original_workflow.tags,
        owner_id=current_user.id
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    # Add computed properties
    duplicate.node_count = len(duplicate.configuration.get("nodes", []))
    duplicate.success_rate = 0.0
    
    return duplicate
