import time
import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.workflow import Workflow
from app.models.user import User
from app.schemas.workflow import WorkflowExecutionResponse, WorkflowValidationResponse
from app.schemas.nodes import NodeType, WorkflowConfiguration
from app.services.node_processor import NodeProcessor
from app.services.llm_service import LLMService
from app.services.vector_store import VectorStoreService
from app.services.web_search import WebSearchService

class WorkflowEngine:
    def __init__(self):
        self.node_processor = NodeProcessor()
        self.llm_service = LLMService()
        self.vector_store = VectorStoreService()
        self.web_search = WebSearchService()

    async def execute_workflow(
        self,
        workflow: Workflow,
        input_data: Dict[str, Any],
        user_id: int,
        session_id: Optional[int] = None,
        db: Session = None
    ) -> WorkflowExecutionResponse:
        """Execute a complete workflow"""
        
        start_time = time.time()
        execution_id = str(uuid.uuid4())
        
        try:
            # Parse workflow configuration
            configuration = workflow.configuration
            nodes = configuration.get("nodes", [])
            edges = configuration.get("edges", [])
            
            if not nodes:
                raise ValueError("Workflow has no nodes")
            
            # Build execution order
            execution_order = self._build_execution_order(nodes, edges)
            
            # Execute nodes in order
            context = {
                "workflow_id": workflow.id,
                "user_id": user_id,
                "session_id": session_id,
                "input_data": input_data,
                "execution_id": execution_id
            }
            
            result = await self._execute_nodes(execution_order, context, db)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return WorkflowExecutionResponse(
                execution_id=execution_id,
                status="success",
                result=result,
                execution_time=execution_time,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            
            return WorkflowExecutionResponse(
                execution_id=execution_id,
                status="error",
                error=str(e),
                execution_time=execution_time,
                timestamp=datetime.utcnow()
            )

    def _build_execution_order(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Build execution order based on node connections"""
        
        # Create node lookup
        node_map = {node["id"]: node for node in nodes}
        
        # Build adjacency list
        adjacency = {node["id"]: [] for node in nodes}
        in_degree = {node["id"]: 0 for node in nodes}
        
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            if source in adjacency and target in adjacency:
                adjacency[source].append(target)
                in_degree[target] += 1
        
        # Topological sort
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        execution_order = []
        
        while queue:
            current_id = queue.pop(0)
            execution_order.append(node_map[current_id])
            
            for neighbor in adjacency[current_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(execution_order) != len(nodes):
            raise ValueError("Workflow contains cycles")
        
        return execution_order

    async def _execute_nodes(
        self, 
        execution_order: List[Dict], 
        context: Dict[str, Any], 
        db: Session
    ) -> Dict[str, Any]:
        """Execute nodes in the given order"""
        
        node_outputs = {}
        final_result = None
        
        for node in execution_order:
            node_id = node["id"]
            node_type = NodeType(node["type"])
            node_data = node.get("data", {})
            
            try:
                # Prepare node input
                node_input = self._prepare_node_input(node, node_outputs, context)
                
                # Execute node
                result = await self._execute_single_node(
                    node_type, node_data, node_input, context, db
                )
                
                node_outputs[node_id] = result
                
                # If this is an output node, capture the final result
                if node_type == NodeType.OUTPUT:
                    final_result = result.get("output", result)
                    
            except Exception as e:
                raise Exception(f"Error executing node {node_id} ({node_type}): {str(e)}")
        
        return {
            "response": final_result or "No output generated",
            "node_outputs": node_outputs,
            "context": context
        }

    def _prepare_node_input(
        self, 
        node: Dict, 
        node_outputs: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepare input data for a node based on its connections"""
        
        node_input = {
            "user_query": context["input_data"].get("user_message", ""),
            "context": context
        }
        
        # Add outputs from connected nodes
        # This is a simplified approach - in a full implementation,
        # you would trace the edges to get inputs from specific connected nodes
        for output_key, output_value in node_outputs.items():
            if isinstance(output_value, dict):
                node_input.update(output_value)
        
        return node_input

    async def _execute_single_node(
        self,
        node_type: NodeType,
        node_data: Dict[str, Any],
        node_input: Dict[str, Any],
        context: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Execute a single node"""
        
        if node_type == NodeType.USER_QUERY:
            return await self._execute_user_query_node(node_data, node_input)
        
        elif node_type == NodeType.KNOWLEDGE_BASE:
            return await self._execute_knowledge_base_node(node_data, node_input, context, db)
        
        elif node_type == NodeType.LLM_ENGINE:
            return await self._execute_llm_node(node_data, node_input, context)
        
        elif node_type == NodeType.WEB_SEARCH:
            return await self._execute_web_search_node(node_data, node_input)
        
        elif node_type == NodeType.OUTPUT:
            return await self._execute_output_node(node_data, node_input)
        
        else:
            raise ValueError(f"Unknown node type: {node_type}")

    async def _execute_user_query_node(
        self, node_data: Dict[str, Any], node_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute user query node"""
        return {
            "query": node_input.get("user_query", ""),
            "validated": True
        }

    async def _execute_knowledge_base_node(
        self, 
        node_data: Dict[str, Any], 
        node_input: Dict[str, Any],
        context: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """Execute knowledge base node"""
        
        query = node_input.get("query", node_input.get("user_query", ""))
        if not query:
            return {"documents": [], "context": ""}
        
        # Get workflow documents
        workflow_id = context["workflow_id"]
        max_results = node_data.get("max_results", 5)
        similarity_threshold = node_data.get("similarity_threshold", 0.7)
        
        try:
            documents = await self.vector_store.similarity_search(
                query=query,
                workflow_id=workflow_id,
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
                "document_count": len(documents)
            }
            
        except Exception as e:
            return {
                "documents": [],
                "context": "",
                "error": str(e)
            }

    async def _execute_llm_node(
        self, 
        node_data: Dict[str, Any], 
        node_input: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute LLM engine node"""
        
        query = node_input.get("query", node_input.get("user_query", ""))
        document_context = node_input.get("context", "")
        
        model = node_data.get("model", "gpt-3.5-turbo")
        prompt = node_data.get("prompt", "You are a helpful assistant.")
        temperature = node_data.get("temperature", 0.7)
        
        try:
            response = await self.llm_service.generate_response(
                query=query,
                context=document_context,
                model=model,
                system_prompt=prompt,
                temperature=temperature
            )
            
            return {
                "response": response["content"],
                "model_used": response["model"],
                "tokens_used": response.get("tokens_used", 0)
            }
            
        except Exception as e:
            return {
                "response": f"Error generating response: {str(e)}",
                "error": str(e)
            }

    async def _execute_web_search_node(
        self, node_data: Dict[str, Any], node_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute web search node"""
        
        query = node_input.get("query", node_input.get("user_query", ""))
        if not query:
            return {"results": [], "context": ""}
        
        max_results = node_data.get("max_results", 5)
        
        try:
            results = await self.web_search.search(
                query=query,
                max_results=max_results
            )
            
            # Combine search results
            context_text = "\n\n".join([
                f"Title: {result.get('title', '')}\nContent: {result.get('snippet', '')}"
                for result in results
            ])
            
            return {
                "results": results,
                "context": context_text,
                "result_count": len(results)
            }
            
        except Exception as e:
            return {
                "results": [],
                "context": "",
                "error": str(e)
            }

    async def _execute_output_node(
        self, node_data: Dict[str, Any], node_input: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute output node"""
        
        format_type = node_data.get("format", "text")
        include_sources = node_data.get("include_sources", True)
        
        response = node_input.get("response", "No response generated")
        
        if format_type == "json":
            output = {
                "response": response,
                "metadata": node_input.get("context", {})
            }
            if include_sources:
                output["sources"] = node_input.get("documents", [])
        else:
            output = response
            if include_sources and node_input.get("documents"):
                sources = [doc.get("title", "Unknown") for doc in node_input.get("documents", [])]
                output += f"\n\nSources: {', '.join(sources)}"
        
        return {"output": output}

    async def validate_workflow(
        self, configuration: Dict[str, Any]
    ) -> WorkflowValidationResponse:
        """Validate workflow configuration"""
        
        errors = []
        warnings = []
        
        try:
            nodes = configuration.get("nodes", [])
            edges = configuration.get("edges", [])
            
            if not nodes:
                errors.append("Workflow must contain at least one node")
                return WorkflowValidationResponse(is_valid=False, errors=errors)
            
            # Validate nodes
            node_ids = set()
            for node in nodes:
                node_id = node.get("id")
                if not node_id:
                    errors.append("All nodes must have an ID")
                    continue
                
                if node_id in node_ids:
                    errors.append(f"Duplicate node ID: {node_id}")
                node_ids.add(node_id)
                
                node_type = node.get("type")
                if not node_type:
                    errors.append(f"Node {node_id} must have a type")
                    continue
                
                try:
                    NodeType(node_type)
                except ValueError:
                    errors.append(f"Invalid node type: {node_type}")
            
            # Validate edges
            for edge in edges:
                source = edge.get("source")
                target = edge.get("target")
                
                if source not in node_ids:
                    errors.append(f"Edge source {source} does not exist")
                if target not in node_ids:
                    errors.append(f"Edge target {target} does not exist")
            
            # Check for cycles
            if not errors:
                try:
                    self._build_execution_order(nodes, edges)
                except ValueError as e:
                    errors.append(str(e))
            
            # Check for isolated nodes
            connected_nodes = set()
            for edge in edges:
                connected_nodes.add(edge.get("source"))
                connected_nodes.add(edge.get("target"))
            
            isolated_nodes = node_ids - connected_nodes
            if len(nodes) > 1 and isolated_nodes:
                warnings.append(f"Isolated nodes detected: {', '.join(isolated_nodes)}")
            
            return WorkflowValidationResponse(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            return WorkflowValidationResponse(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"]
            )
