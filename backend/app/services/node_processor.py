import time
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.schemas.nodes import NodeType, NodeValidationResponse, NodeExecutionContext, NodeExecutionResult
from app.services.llm_service import LLMService
from app.services.vector_store import VectorStoreService
from app.services.web_search import WebSearchService

class NodeProcessor:
    def __init__(self):
        self.llm_service = LLMService()
        self.vector_store = VectorStoreService()
        self.web_search = WebSearchService()

    async def validate_node_config(
        self, node_type: NodeType, config: Dict[str, Any]
    ) -> NodeValidationResponse:
        """Validate node configuration"""
        
        errors = []
        warnings = []
        
        try:
            # Common validation
            if not config.get("label"):
                errors.append("Node must have a label")
            
            # Type-specific validation
            if node_type == NodeType.USER_QUERY:
                errors.extend(self._validate_user_query_config(config))
            elif node_type == NodeType.KNOWLEDGE_BASE:
                errors.extend(self._validate_knowledge_base_config(config))
            elif node_type == NodeType.LLM_ENGINE:
                errors.extend(self._validate_llm_config(config))
            elif node_type == NodeType.WEB_SEARCH:
                errors.extend(self._validate_web_search_config(config))
            elif node_type == NodeType.OUTPUT:
                errors.extend(self._validate_output_config(config))
            
            return NodeValidationResponse(
                is_valid=len(errors) == 0,
                errors=[{"node_id": "current", "field": "config", "message": error} for error in errors],
                warnings=warnings
            )
            
        except Exception as e:
            return NodeValidationResponse(
                is_valid=False,
                errors=[{"node_id": "current", "field": "config", "message": f"Validation error: {str(e)}"}]
            )

    def _validate_user_query_config(self, config: Dict[str, Any]) -> list:
        """Validate user query node configuration"""
        errors = []
        
        placeholder = config.get("placeholder")
        if placeholder and len(placeholder) > 500:
            errors.append("Placeholder text too long (max 500 characters)")
        
        return errors

    def _validate_knowledge_base_config(self, config: Dict[str, Any]) -> list:
        """Validate knowledge base node configuration"""
        errors = []
        
        chunk_size = config.get("chunk_size", 1000)
        if not isinstance(chunk_size, int) or chunk_size < 100 or chunk_size > 10000:
            errors.append("Chunk size must be between 100 and 10000")
        
        chunk_overlap = config.get("chunk_overlap", 200)
        if not isinstance(chunk_overlap, int) or chunk_overlap < 0 or chunk_overlap >= chunk_size:
            errors.append("Chunk overlap must be non-negative and less than chunk size")
        
        similarity_threshold = config.get("similarity_threshold", 0.7)
        if not isinstance(similarity_threshold, (int, float)) or similarity_threshold < 0 or similarity_threshold > 1:
            errors.append("Similarity threshold must be between 0 and 1")
        
        max_results = config.get("max_results", 5)
        if not isinstance(max_results, int) or max_results < 1 or max_results > 50:
            errors.append("Max results must be between 1 and 50")
        
        return errors

    def _validate_llm_config(self, config: Dict[str, Any]) -> list:
        """Validate LLM node configuration"""
        errors = []
        
        model = config.get("model")
        if not model:
            errors.append("Model is required")
        elif model not in ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "text-davinci-003"]:
            errors.append("Unsupported model")
        
        prompt = config.get("prompt")
        if not prompt:
            errors.append("Prompt is required")
        elif len(prompt) > 4000:
            errors.append("Prompt too long (max 4000 characters)")
        
        temperature = config.get("temperature", 0.7)
        if not isinstance(temperature, (int, float)) or temperature < 0 or temperature > 2:
            errors.append("Temperature must be between 0 and 2")
        
        max_tokens = config.get("max_tokens")
        if max_tokens is not None:
            if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 4000:
                errors.append("Max tokens must be between 1 and 4000")
        
        return errors

    def _validate_web_search_config(self, config: Dict[str, Any]) -> list:
        """Validate web search node configuration"""
        errors = []
        
        max_results = config.get("max_results", 5)
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            errors.append("Max results must be between 1 and 20")
        
        search_engine = config.get("search_engine", "google")
        if search_engine not in ["google", "bing", "duckduckgo"]:
            errors.append("Unsupported search engine")
        
        return errors

    def _validate_output_config(self, config: Dict[str, Any]) -> list:
        """Validate output node configuration"""
        errors = []
        
        format_type = config.get("format", "text")
        if format_type not in ["text", "json", "markdown"]:
            errors.append("Unsupported output format")
        
        template = config.get("template")
        if template and len(template) > 2000:
            errors.append("Template too long (max 2000 characters)")
        
        return errors

    async def execute_node(
        self,
        node_type: NodeType,
        config: Dict[str, Any],
        context: NodeExecutionContext,
        db: Session
    ) -> NodeExecutionResult:
        """Execute a single node"""
        
        start_time = time.time()
        
        try:
            if node_type == NodeType.USER_QUERY:
                result = await self._execute_user_query(config, context)
            elif node_type == NodeType.KNOWLEDGE_BASE:
                result = await self._execute_knowledge_base(config, context, db)
            elif node_type == NodeType.LLM_ENGINE:
                result = await self._execute_llm(config, context)
            elif node_type == NodeType.WEB_SEARCH:
                result = await self._execute_web_search(config, context)
            elif node_type == NodeType.OUTPUT:
                result = await self._execute_output(config, context)
            else:
                raise ValueError(f"Unknown node type: {node_type}")
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return NodeExecutionResult(
                node_id=f"{node_type}-{int(time.time())}",
                status="success",
                output_data=result,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            return NodeExecutionResult(
                node_id=f"{node_type}-{int(time.time())}",
                status="error",
                error_message=str(e),
                execution_time=execution_time
            )

    async def _execute_user_query(
        self, config: Dict[str, Any], context: NodeExecutionContext
    ) -> Dict[str, Any]:
        """Execute user query node"""
        
        user_input = context.input_data.get("user_query", "")
        
        # Simple validation
        if not user_input or not user_input.strip():
            raise ValueError("User query is required")
        
        return {
            "query": user_input.strip(),
            "validated": True,
            "placeholder": config.get("placeholder", "")
        }

    async def _execute_knowledge_base(
        self, config: Dict[str, Any], context: NodeExecutionContext, db: Session
    ) -> Dict[str, Any]:
        """Execute knowledge base node"""
        
        query = context.input_data.get("user_query", "")
        if not query:
            return {"documents": [], "context": ""}
        
        max_results = config.get("max_results", 5)
        similarity_threshold = config.get("similarity_threshold", 0.7)
        
        # Search for relevant documents
        documents = await self.vector_store.similarity_search(
            query=query,
            workflow_id=context.workflow_id,
            k=max_results,
            threshold=similarity_threshold,
            db=db
        )
        
        # Combine document content
        context_text = "\n\n".join([
            f"Document: {doc.get('title', 'Unknown')}\nContent: {doc.get('content', '')}"
            for doc in documents
        ])
        
        return {
            "documents": documents,
            "context": context_text,
            "document_count": len(documents),
            "similarity_threshold": similarity_threshold
        }

    async def _execute_llm(
        self, config: Dict[str, Any], context: NodeExecutionContext
    ) -> Dict[str, Any]:
        """Execute LLM node"""
        
        query = context.input_data.get("user_query", "")
        document_context = context.global_context.get("context", "")
        
        model = config.get("model", "gpt-3.5-turbo")
        prompt = config.get("prompt", "You are a helpful assistant.")
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens")
        
        # Generate response
        response = await self.llm_service.generate_response(
            query=query,
            context=document_context,
            model=model,
            system_prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return {
            "response": response["content"],
            "model_used": response["model"],
            "tokens_used": response.get("tokens_used", 0),
            "finish_reason": response.get("finish_reason", "stop")
        }

    async def _execute_web_search(
        self, config: Dict[str, Any], context: NodeExecutionContext
    ) -> Dict[str, Any]:
        """Execute web search node"""
        
        query = context.input_data.get("user_query", "")
        if not query:
            return {"results": [], "context": ""}
        
        max_results = config.get("max_results", 5)
        search_engine = config.get("search_engine", "google")
        
        # Perform search
        results = await self.web_search.search(
            query=query,
            max_results=max_results,
            engine=search_engine
        )
        
        # Combine search results
        context_text = "\n\n".join([
            f"Title: {result.get('title', '')}\nSnippet: {result.get('snippet', '')}\nURL: {result.get('link', '')}"
            for result in results
        ])
        
        return {
            "results": results,
            "context": context_text,
            "result_count": len(results),
            "search_engine": search_engine
        }

    async def _execute_output(
        self, config: Dict[str, Any], context: NodeExecutionContext
    ) -> Dict[str, Any]:
        """Execute output node"""
        
        response = context.global_context.get("response", context.input_data.get("user_query", ""))
        format_type = config.get("format", "text")
        include_sources = config.get("include_sources", True)
        template = config.get("template")
        
        if template:
            # Apply template formatting
            try:
                formatted_response = template.format(
                    response=response,
                    **context.global_context
                )
            except KeyError as e:
                formatted_response = f"Template error: Missing variable {str(e)}"
        else:
            formatted_response = response
        
        if format_type == "json":
            output = {
                "response": formatted_response,
                "metadata": context.global_context
            }
            if include_sources:
                output["sources"] = context.global_context.get("documents", [])
        elif format_type == "markdown":
            output = f"# Response\n\n{formatted_response}"
            if include_sources and context.global_context.get("documents"):
                sources = [doc.get("title", "Unknown") for doc in context.global_context.get("documents", [])]
                output += f"\n\n## Sources\n\n" + "\n".join([f"- {source}" for source in sources])
        else:
            output = formatted_response
            if include_sources and context.global_context.get("documents"):
                sources = [doc.get("title", "Unknown") for doc in context.global_context.get("documents", [])]
                output += f"\n\nSources: {', '.join(sources)}"
        
        return {
            "output": output,
            "format": format_type,
            "include_sources": include_sources
        }
