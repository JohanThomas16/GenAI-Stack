import os
import hashlib
from typing import List, Dict, Any, Optional
import fitz  # PyMuPDF
from sqlalchemy.orm import Session

from app.models.document import Document
from app.core.config import settings
from app.services.vector_store import VectorStoreService
from app.services.llm_service import LLMService

class DocumentProcessor:
    def __init__(self):
        self.vector_store = VectorStoreService()
        self.llm_service = LLMService()

    async def process_document(self, document: Document, db: Session) -> None:
        """Process uploaded document: extract text, generate embeddings, store in vector DB"""
        
        try:
            # Mark as processing
            document.mark_processing()
            db.commit()
            
            # Extract text content
            content = await self._extract_text(document.file_path, document.mime_type)
            
            if not content.strip():
                raise ValueError("No text content found in document")
            
            # Generate content hash
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Update document with extracted content
            document.content = content
            document.content_hash = content_hash
            
            # Extract metadata
            metadata = await self._extract_metadata(document.file_path, document.mime_type)
            document.metadata = metadata
            
            db.commit()
            
            # Generate embeddings and store in vector database
            await self._generate_and_store_embeddings(document, content, db)
            
            # Mark as processed
            document.mark_processed()
            db.commit()
            
        except Exception as e:
            document.mark_error(str(e))
            db.commit()
            raise

    async def _extract_text(self, file_path: str, mime_type: str) -> str:
        """Extract text from document based on file type"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")
        
        if mime_type == "application/pdf":
            return await self._extract_pdf_text(file_path)
        elif mime_type == "text/plain":
            return await self._extract_text_file(file_path)
        elif mime_type in ["application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
            return await self._extract_docx_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")

    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file"""
        
        try:
            doc = fitz.open(file_path)
            text_content = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text.strip():
                    text_content.append(f"Page {page_num + 1}:\n{text}")
            
            doc.close()
            return "\n\n".join(text_content)
            
        except Exception as e:
            raise ValueError(f"Error extracting PDF text: {str(e)}")

    async def _extract_text_file(self, file_path: str) -> str:
        """Extract text from plain text file"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading text file: {str(e)}")

    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file"""
        
        try:
            # This would require python-docx library
            # For now, return placeholder
            return "DOCX text extraction not implemented yet"
        except Exception as e:
            raise ValueError(f"Error extracting DOCX text: {str(e)}")

    async def _extract_metadata(self, file_path: str, mime_type: str) -> Dict[str, Any]:
        """Extract metadata from document"""
        
        metadata = {
            "file_size": os.path.getsize(file_path),
            "mime_type": mime_type
        }
        
        if mime_type == "application/pdf":
            try:
                doc = fitz.open(file_path)
                pdf_metadata = doc.metadata
                
                metadata.update({
                    "title": pdf_metadata.get("title", ""),
                    "author": pdf_metadata.get("author", ""),
                    "creator": pdf_metadata.get("creator", ""),
                    "producer": pdf_metadata.get("producer", ""),
                    "creation_date": pdf_metadata.get("creationDate", ""),
                    "modification_date": pdf_metadata.get("modDate", ""),
                    "page_count": len(doc)
                })
                
                doc.close()
            except Exception:
                pass  # Ignore metadata extraction errors
        
        return metadata

    async def _generate_and_store_embeddings(
        self, document: Document, content: str, db: Session
    ) -> None:
        """Generate embeddings for document content and store in vector database"""
        
        # Split content into chunks
        chunks = self._split_text_into_chunks(content)
        
        if not chunks:
            raise ValueError("No text chunks generated from document")
        
        # Generate embeddings for each chunk
        embeddings_data = []
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = await self.llm_service.generate_embedding(chunk)
            
            embeddings_data.append({
                "id": f"{document.id}_{i}",
                "content": chunk,
                "embedding": embedding,
                "metadata": {
                    "document_id": document.id,
                    "chunk_index": i,
                    "document_title": document.metadata.get("title", document.original_filename),
                    "document_type": document.mime_type,
                    "workflow_id": document.workflow_id
                }
            })
        
        # Store in vector database
        await self.vector_store.add_documents(
            documents=embeddings_data,
            collection_name=f"workflow_{document.workflow_id}" if document.workflow_id else "global"
        )
        
        # Update document with embedding info
        document.embedding_model = "text-embedding-ada-002"  # Default OpenAI model
        document.embedding_dimensions = 1536  # OpenAI ada-002 dimensions
        document.chunk_count = len(chunks)
        
        db.commit()

    def _split_text_into_chunks(
        self, text: str, chunk_size: int = 1000, overlap: int = 200
    ) -> List[str]:
        """Split text into overlapping chunks"""
        
        if not text or not text.strip():
            return []
        
        # Simple word-based chunking
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk_text = " ".join(chunk_words)
            
            if chunk_text.strip():
                chunks.append(chunk_text)
        
        return chunks

    async def search_document(
        self, document_id: int, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search within a specific document"""
        
        try:
            results = await self.vector_store.similarity_search(
                query=query,
                collection_name=f"document_{document_id}",
                k=limit
            )
            
            return results
            
        except Exception as e:
            raise ValueError(f"Document search failed: {str(e)}")

    async def get_document_summary(self, document: Document) -> str:
        """Generate a summary of the document content"""
        
        if not document.content:
            return "No content available for summary"
        
        # Use first 2000 characters for summary
        content_preview = document.content[:2000]
        
        try:
            summary = await self.llm_service.generate_response(
                query="Please provide a brief summary of this document content:",
                context=content_preview,
                model="gpt-3.5-turbo",
                system_prompt="You are a helpful assistant that creates concise document summaries.",
                max_tokens=200
            )
            
            return summary["content"]
            
        except Exception as e:
            return f"Could not generate summary: {str(e)}"

    async def delete_document_embeddings(self, document: Document) -> None:
        """Delete document embeddings from vector database"""
        
        try:
            await self.vector_store.delete_documents(
                document_ids=[str(document.id)],
                collection_name=f"workflow_{document.workflow_id}" if document.workflow_id else "global"
            )
        except Exception as e:
            # Log error but don't raise - document deletion should still proceed
            print(f"Error deleting embeddings for document {document.id}: {str(e)}")
