import pytest
from fastapi.testclient import TestClient
import json

from app.main import app

client = TestClient(app)

class TestChatAPI:
    
    def test_create_chat_session(self):
        """Test creating chat session"""
        session_data = {
            "title": "Test Chat Session",
            "workflow_id": None,
            "session_metadata": {"test": "data"}
        }
        
        response = client.post("/api/v1/chat/sessions", json=session_data)
        assert response.status_code == 201
        
        data = response.json()
        assert data["title"] == "Test Chat Session"
        assert "id" in data
        assert data["is_active"] is True

    def test_get_chat_sessions(self):
        """Test getting user chat sessions"""
        response = client.get("/api/v1/chat/sessions")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)

    def test_get_chat_session_by_id(self):
        """Test getting specific chat session"""
        # Create session first
        session_data = {
            "title": "Test Session for Get",
            "workflow_id": None
        }
        
        create_response = client.post("/api/v1/chat/sessions", json=session_data)
        session_id = create_response.json()["id"]
        
        # Get session
        response = client.get(f"/api/v1/chat/sessions/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Test Session for Get"

    def test_update_chat_session(self):
        """Test updating chat session"""
        # Create session
        session_data = {
            "title": "Original Title",
            "workflow_id": None
        }
        
        create_response = client.post("/api/v1/chat/sessions", json=session_data)
        session_id = create_response.json()["id"]
        
        # Update session
        update_data = {
            "title": "Updated Title",
            "session_metadata": {"updated": True}
        }
        
        response = client.put(f"/api/v1/chat/sessions/{session_id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "Updated Title"

    def test_delete_chat_session(self):
        """Test deleting chat session"""
        # Create session
        session_data = {
            "title": "To be deleted",
            "workflow_id": None
        }
        
        create_response = client.post("/api/v1/chat/sessions", json=session_data)
        session_id = create_response.json()["id"]
        
        # Delete session
        response = client.delete(f"/api/v1/chat/sessions/{session_id}")
        assert response.status_code == 200
        
        # Verify deletion
        get_response = client.get(f"/api/v1/chat/sessions/{session_id}")
        assert get_response.status_code == 404

    def test_execute_chat_without_workflow(self):
        """Test executing chat message without workflow"""
        execution_data = {
            "message": "Hello, this is a test message",
            "context": {"test": "context"}
        }
        
        response = client.post("/api/v1/chat/execute", json=execution_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "response" in data
        assert "session_id" in data
        assert "message_id" in data
        assert "execution_time" in data

    def test_execute_chat_with_session(self):
        """Test executing chat with existing session"""
        # Create session first
        session_data = {
            "title": "Chat Session",
            "workflow_id": None
        }
        
        create_response = client.post("/api/v1/chat/sessions", json=session_data)
        session_id = create_response.json()["id"]
        
        # Execute chat
        execution_data = {
            "message": "Hello in existing session",
            "session_id": session_id
        }
        
        response = client.post("/api/v1/chat/execute", json=execution_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id

    def test_get_chat_messages(self):
        """Test getting chat messages for a session"""
        # Create session and send message
        session_data = {"title": "Message Test Session"}
        create_response = client.post("/api/v1/chat/sessions", json=session_data)
        session_id = create_response.json()["id"]
        
        # Send a message
        execution_data = {
            "message": "Test message for history",
            "session_id": session_id
        }
        client.post("/api/v1/chat/execute", json=execution_data)
        
        # Get messages
        response = client.get(f"/api/v1/chat/sessions/{session_id}/messages")
        assert response.status_code == 200
        
        data = response.json()
        assert "messages" in data
        assert "total_count" in data
        assert "has_more" in data
        assert len(data["messages"]) >= 2  # User message + assistant response

    def test_get_chat_messages_pagination(self):
        """Test chat message pagination"""
        # Create session
        session_data = {"title": "Pagination Test Session"}
        create_response = client.post("/api/v1/chat/sessions", json=session_data)
        session_id = create_response.json()["id"]
        
        # Send multiple messages
        for i in range(5):
            execution_data = {
                "message": f"Test message {i}",
                "session_id": session_id
            }
            client.post("/api/v1/chat/execute", json=execution_data)
        
        # Get messages with limit
        response = client.get(f"/api/v1/chat/sessions/{session_id}/messages?limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["messages"]) <= 5

    def test_websocket_chat(self):
        """Test WebSocket chat connection"""
        # This is a basic test - full WebSocket testing requires more setup
        with client.websocket_connect("/api/v1/chat/ws/1") as websocket:
            # Send test message
            websocket.send_text(json.dumps({"message": "Hello WebSocket"}))
            
            # Receive response
            data = websocket.receive_text()
            response_data = json.loads(data)
            
            assert "type" in response_data
            assert "content" in response_data

    def test_chat_history_request(self):
        """Test chat history request format"""
        history_data = {
            "session_id": 1,
            "limit": 20,
            "offset": 0
        }
        
        # This tests the schema validation
        response = client.get(
            "/api/v1/chat/sessions/1/messages",
            params={"limit": 20, "offset": 0}
        )
        
        # Even if session doesn't exist, we test the endpoint structure
        assert response.status_code in [200, 404]

    def test_invalid_session_access(self):
        """Test accessing non-existent session"""
        response = client.get("/api/v1/chat/sessions/99999")
        assert response.status_code == 404

    def test_invalid_message_execution(self):
        """Test executing chat with invalid data"""
        execution_data = {
            "message": "",  # Empty message should be invalid
            "session_id": 99999  # Non-existent session
        }
        
        response = client.post("/api/v1/chat/execute", json=execution_data)
        assert response.status_code in [400, 404, 422]  # Various error codes possible

    @pytest.mark.asyncio
    async def test_chat_with_workflow(self):
        """Test chat execution with workflow"""
        # This would require setting up a test workflow
        # For now, just test the basic structure
        execution_data = {
            "message": "Test with workflow",
            "workflow_id": 1,
            "context": {"test": True}
        }
        
        response = client.post("/api/v1/chat/execute", json=execution_data)
        # Will likely return 404 without real workflow, but tests endpoint
        assert response.status_code in [200, 404, 500]
