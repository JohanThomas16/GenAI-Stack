import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import uuid

from app.core.config import settings
from app.models.document import Document

class VectorStoreService:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=settings.CHROMA_URL.split("://")[1].split(":")[0],
            port=int(settings.CHROMA_URL.split(":")[-1]) if ":" in settings.CHROMA_URL.split("://")[1] else 8000,
            settings=Settings(anonymized_telemetry=False)
        )
        self.default_collection = settings.CHROMA_COLLECTION_NAME

    async def add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        collection_name: Optional[str] = None
    ) -> None:
        """Add documents to vector store"""
        
        try:
            collection_name = collection_name or self.default_collection
            
            # Get or create collection
            try:
                collection = self.client.get_collection(collection_name)
            except Exception:
                collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            
            # Prepare data for ChromaDB
            ids = []
            embeddings = []
            metadatas = []
            documents_text = []
            
            for doc in documents:
                ids.append(str(doc["id"]))
                embeddings.append(doc["embedding"])
                metadatas.append(doc["metadata"])
                documents_text.append(doc["content"])
            
            # Add to collection
            collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents_text
            )
            
        except Exception as e:
            raise ValueError(f"Error adding documents to vector store: {str(e)}")

    async def similarity_search(
        self,
        query: str,
        workflow_id: Optional[int] = None,
        k: int = 5,
        threshold: float = 0.7,
        collection_name: Optional[str] = None,
        db: Session = None
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        
        try:
            from app.services.llm_service import LLMService
            llm_service = LLMService()
            
            # Generate query embedding
            query_embedding = await llm_service.generate_embedding(query)
            
            collection_name = collection_name or self.default_collection
            
            # Get collection
            try:
                collection = self.client.get_collection(collection_name)
            except Exception:
                return []  # Collection doesn't exist
            
            # Prepare where clause for workflow filtering
            where_clause = {}
            if workflow_id:
                where_clause["workflow_id"] = workflow_id
            
            # Perform similarity search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i in range(len(results["documents"][0])):
                    distance = results["distances"][0][i] if results["distances"] else 1.0
                    similarity = 1 - distance  # Convert distance to similarity
                    
                    if similarity >= threshold:
                        formatted_results.append({
                            "content": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                            "similarity": similarity,
                            "distance": distance,
                            "title": results["metadatas"][0][i].get("document_title", "Unknown") if results["metadatas"] else "Unknown"
                        })
            
            # Sort by similarity (highest first)
            formatted_results.sort(key=lambda x: x["similarity"], reverse=True)
            
            return formatted_results
            
        except Exception as e:
            raise ValueError(f"Error performing similarity search: {str(e)}")

    async def delete_documents(
        self, 
        document_ids: List[str], 
        collection_name: Optional[str] = None
    ) -> None:
        """Delete documents from vector store"""
        
        try:
            collection_name = collection_name or self.default_collection
            
            # Get collection
            try:
                collection = self.client.get_collection(collection_name)
            except Exception:
                return  # Collection doesn't exist
            
            # Delete documents
            collection.delete(ids=document_ids)
            
        except Exception as e:
            raise ValueError(f"Error deleting documents from vector store: {str(e)}")

    async def update_document(
        self, 
        document_id: str, 
        content: str, 
        embedding: List[float], 
        metadata: Dict[str, Any],
        collection_name: Optional[str] = None
    ) -> None:
        """Update a document in vector store"""
        
        try:
            collection_name = collection_name or self.default_collection
            
            # Get collection
            try:
                collection = self.client.get_collection(collection_name)
            except Exception:
                raise ValueError(f"Collection {collection_name} not found")
            
            # Update document
            collection.update(
                ids=[document_id],
                embeddings=[embedding],
                metadatas=[metadata],
                documents=[content]
            )
            
        except Exception as e:
            raise ValueError(f"Error updating document in vector store: {str(e)}")

    async def get_document(
        self, 
        document_id: str, 
        collection_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Get a specific document from vector store"""
        
        try:
            collection_name = collection_name or self.default_collection
            
            # Get collection
            try:
                collection = self.client.get_collection(collection_name)
            except Exception:
                return None
            
            # Get document
            results = collection.get(
                ids=[document_id],
                include=["documents", "metadatas", "embeddings"]
            )
            
            if results["documents"] and results["documents"]:
                return {
                    "id": document_id,
                    "content": results["documents"][0],
                    "metadata": results["metadatas"][0] if results["metadatas"] else {},
                    "embedding": results["embeddings"][0] if results["embeddings"] else []
                }
            
            return None
            
        except Exception as e:
            raise ValueError(f"Error getting document from vector store: {str(e)}")

    async def get_collection_stats(
        self, collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get statistics about a collection"""
        
        try:
            collection_name = collection_name or self.default_collection
            
            # Get collection
            try:
                collection = self.client.get_collection(collection_name)
            except Exception:
                return {"exists": False, "count": 0}
            
            # Get count
            count = collection.count()
            
            return {
                "exists": True,
                "count": count,
                "name": collection_name
            }
            
        except Exception as e:
            return {"exists": False, "count": 0, "error": str(e)}

    async def list_collections(self) -> List[str]:
        """List all collections"""
        
        try:
            collections = self.client.list_collections()
            return [collection.name for collection in collections]
        except Exception as e:
            raise ValueError(f"Error listing collections: {str(e)}")

    async def create_collection(
        self, 
        name: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create a new collection"""
        
        try:
            self.client.create_collection(
                name=name,
                metadata=metadata or {"hnsw:space": "cosine"}
            )
        except Exception as e:
            raise ValueError(f"Error creating collection: {str(e)}")

    async def delete_collection(self, name: str) -> None:
        """Delete a collection"""
        
        try:
            self.client.delete_collection(name=name)
        except Exception as e:
            raise ValueError(f"Error deleting collection: {str(e)}")

    async def reset_collection(self, name: str) -> None:
        """Reset a collection (delete all documents)"""
        
        try:
            # Get collection
            collection = self.client.get_collection(name)
            
            # Get all document IDs
            results = collection.get(include=[])
            if results["ids"]:
                collection.delete(ids=results["ids"])
                
        except Exception as e:
            raise ValueError(f"Error resetting collection: {str(e)}")
