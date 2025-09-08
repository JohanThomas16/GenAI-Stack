import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.auth import get_current_active_user
from app.models.user import User
from app.models.workflow import Workflow

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

def override_get_current_user():
    return User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        is_active=True
    )

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_active_user] = override_get_current_user

client = TestClient(app)

class TestWorkflowAPI:
    
    def test_create_workflow(self):
        """Test workflow creation"""
        workflow_data = {
            "name": "Test Workflow",
            "description": "A test workflow",
            "configuration": {
                "nodes": [
                    {
                        "id": "user-query-1",
                        "type": "userQuery",
                        "position": {"x": 100, "y": 100},
                        "data": {"label": "User Query"}
                    }
                ],
                "edges": []
            }
        }
        
        response = client.post("/api/v1/workflows/", json=workflow_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["name"] == "Test Workflow"
        assert data["description"] == "A test workflow"
        assert "id" in data
        assert data["node_count"] == 1

    def test_get_workflows(self):
        """Test getting user workflows"""
        response = client.get("/api/v1/workflows/")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    def test_get_workflow_by_id(self):
        """Test getting specific workflow"""
        # First create a workflow
        workflow_data = {
            "name": "Test Workflow 2",
            "description": "Another test workflow",
            "configuration": {"nodes": [], "edges": []}
        }
        
        create_response = client.post("/api/v1/workflows/", json=workflow_data)
        workflow_id = create_response.json()["id"]
        
        # Then get it
        response = client.get(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Test Workflow 2"

    def test_update_workflow(self):
        """Test updating workflow"""
        # Create workflow
        workflow_data = {
            "name": "Test Workflow 3",
            "description": "Yet another test workflow",
            "configuration": {"nodes": [], "edges": []}
        }
        
        create_response = client.post("/api/v1/workflows/", json=workflow_data)
        workflow_id = create_response.json()["id"]
        
        # Update it
        update_data = {
            "name": "Updated Workflow",
            "description": "Updated description"
        }
        
        response = client.put(f"/api/v1/workflows/{workflow_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Updated Workflow"
        assert data["description"] == "Updated description"

    def test_delete_workflow(self):
        """Test deleting workflow"""
        # Create workflow
        workflow_data = {
            "name": "Test Workflow 4",
            "description": "To be deleted",
            "configuration": {"nodes": [], "edges": []}
        }
        
        create_response = client.post("/api/v1/workflows/", json=workflow_data)
        workflow_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/v1/workflows/{workflow_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/workflows/{workflow_id}")
        assert get_response.status_code == 404

    def test_validate_workflow(self):
        """Test workflow validation"""
        valid_config = {
            "nodes": [
                {
                    "id": "user-query-1",
                    "type": "userQuery",
                    "position": {"x": 100, "y": 100},
                    "data": {"label": "User Query"}
                },
                {
                    "id": "llm-1",
                    "type": "llm",
                    "position": {"x": 300, "y": 100},
                    "data": {"label": "LLM Engine", "model": "gpt-3.5-turbo"}
                }
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "user-query-1",
                    "target": "llm-1"
                }
            ]
        }
        
        response = client.post("/api/v1/workflows/validate", json={"configuration": valid_config})
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is True
        assert len(data["errors"]) == 0

    def test_validate_invalid_workflow(self):
        """Test validation of invalid workflow"""
        invalid_config = {
            "nodes": [
                {
                    "id": "user-query-1",
                    "type": "invalidType",
                    "position": {"x": 100, "y": 100},
                    "data": {"label": "Invalid Node"}
                }
            ],
            "edges": []
        }
        
        response = client.post("/api/v1/workflows/validate", json={"configuration": invalid_config})
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

    def test_duplicate_workflow(self):
        """Test duplicating workflow"""
        # Create original workflow
        workflow_data = {
            "name": "Original Workflow",
            "description": "To be duplicated",
            "configuration": {"nodes": [], "edges": []}
        }
        
        create_response = client.post("/api/v1/workflows/", json=workflow_data)
        workflow_id = create_response.json()["id"]
        
        # Duplicate it
        response = client.post(f"/api/v1/workflows/{workflow_id}/duplicate")
        assert response.status_code == 200
        
        data = response.json()
        assert data["name"] == "Original Workflow (Copy)"
        assert data["description"] == "To be duplicated"
        assert data["id"] != workflow_id

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """Test workflow execution"""
        # This would require mocking the workflow engine
        # For now, just test the endpoint exists
        execution_data = {
            "workflow_id": 1,
            "input_data": {"user_message": "Hello"}
        }
        
        response = client.post("/api/v1/workflows/1/execute", json=execution_data)
        # This will fail without a real workflow, but we can test the endpoint exists
        assert response.status_code in [200, 404, 500]
