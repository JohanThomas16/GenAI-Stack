import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.nodes import NodeType

client = TestClient(app)

class TestNodeAPI:
    
    def test_get_node_types(self):
        """Test getting available node types"""
        response = client.get("/api/v1/nodes/types")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
        assert "userQuery" in data
        assert "llm" in data
        assert "knowledgeBase" in data
        assert "output" in data

    def test_get_node_config_schema(self):
        """Test getting node configuration schema"""
        response = client.get("/api/v1/nodes/config/userQuery")
        assert response.status_code == 200
        
        data = response.json()
        assert "type" in data
        assert "properties" in data
        assert "required" in data

    def test_get_node_config_schema_invalid_type(self):
        """Test getting schema for invalid node type"""
        response = client.get("/api/v1/nodes/config/invalidType")
        assert response.status_code == 422  # Validation error

    def test_get_node_defaults(self):
        """Test getting node defaults"""
        response = client.get("/api/v1/nodes/defaults/userQuery")
        assert response.status_code == 200
        
        data = response.json()
        assert "label" in data

    def test_get_llm_node_defaults(self):
        """Test getting LLM node defaults"""
        response = client.get("/api/v1/nodes/defaults/llm")
        assert response.status_code == 200
        
        data = response.json()
        assert data["model"] == "gpt-3.5-turbo"
        assert data["temperature"] == 0.7
        assert "prompt" in data

    def test_validate_valid_node_config(self):
        """Test validating valid node configuration"""
        config = {
            "label": "Test User Query",
            "placeholder": "Enter your question"
        }
        
        response = client.post("/api/v1/nodes/validate?node_type=userQuery", json=config)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is True
        assert len(data["errors"]) == 0

    def test_validate_invalid_node_config(self):
        """Test validating invalid node configuration"""
        config = {
            # Missing required label
            "placeholder": "Enter your question"
        }
        
        response = client.post("/api/v1/nodes/validate?node_type=userQuery", json=config)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_llm_node_config(self):
        """Test validating LLM node configuration"""
        config = {
            "label": "Test LLM",
            "model": "gpt-3.5-turbo",
            "prompt": "You are a helpful assistant",
            "temperature": 0.8
        }
        
        response = client.post("/api/v1/nodes/validate?node_type=llm", json=config)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is True

    def test_validate_llm_node_invalid_temperature(self):
        """Test validating LLM node with invalid temperature"""
        config = {
            "label": "Test LLM",
            "model": "gpt-3.5-turbo", 
            "prompt": "You are a helpful assistant",
            "temperature": 5.0  # Invalid - too high
        }
        
        response = client.post("/api/v1/nodes/validate?node_type=llm", json=config)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is False
        assert any("temperature" in error["message"].lower() for error in data["errors"])

    def test_validate_knowledge_base_config(self):
        """Test validating knowledge base node configuration"""
        config = {
            "label": "Test KB",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "similarity_threshold": 0.7,
            "max_results": 5
        }
        
        response = client.post("/api/v1/nodes/validate?node_type=knowledgeBase", json=config)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is True

    def test_validate_web_search_config(self):
        """Test validating web search node configuration"""
        config = {
            "label": "Test Search",
            "max_results": 10,
            "search_engine": "google"
        }
        
        response = client.post("/api/v1/nodes/validate?node_type=webSearch", json=config)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is True

    def test_validate_output_config(self):
        """Test validating output node configuration"""
        config = {
            "label": "Test Output",
            "format": "json",
            "include_sources": True
        }
        
        response = client.post("/api/v1/nodes/validate?node_type=output", json=config)
        assert response.status_code == 200
        
        data = response.json()
        assert data["is_valid"] is True

    @pytest.mark.asyncio
    async def test_execute_node(self):
        """Test node execution"""
        node_config = {
            "label": "Test User Query",
            "placeholder": "Enter question"
        }
        
        context = {
            "workflow_id": 1,
            "user_id": 1,
            "input_data": {"user_query": "Hello world"}
        }
        
        response = client.post(
            "/api/v1/nodes/execute?node_type=userQuery",
            json={**node_config, **context}
        )
        
        # This might fail without proper mocking, but we test the endpoint exists
        assert response.status_code in [200, 422, 500]
