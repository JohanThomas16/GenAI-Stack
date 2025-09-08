from fastapi import APIRouter

from app.api.v1.endpoints import auth, workflows, nodes, documents, chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(nodes.router, prefix="/nodes", tags=["nodes"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
