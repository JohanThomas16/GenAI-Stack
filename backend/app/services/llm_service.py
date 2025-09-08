import openai
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import time

from app.core.config import settings

class LLMService:
    def __init__(self):
        # Configure OpenAI
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
        
        # Configure Gemini
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)

    async def generate_response(
        self,
        query: str,
        context: str = "",
        model: str = "gpt-3.5-turbo",
        system_prompt: str = "You are a helpful assistant.",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using specified LLM"""
        
        if model.startswith("gpt"):
            return await self._generate_openai_response(
                query, context, model, system_prompt, temperature, max_tokens, **kwargs
            )
        elif model.startswith("gemini"):
            return await self._generate_gemini_response(
                query, context, model, system_prompt, temperature, max_tokens, **kwargs
            )
        else:
            raise ValueError(f"Unsupported model: {model}")

    async def _generate_openai_response(
        self,
        query: str,
        context: str,
        model: str,
        system_prompt: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        try:
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system", 
                    "content": f"Context information:\n{context}"
                })
            
            messages.append({"role": "user", "content": query})
            
            start_time = time.time()
            
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "content": response.choices[0].message.content,
                "model": model,
                "tokens_used": response.usage.total_tokens,
                "execution_time": execution_time,
                "finish_reason": response.choices[0].finish_reason
            }
            
        except Exception as e:
            raise ValueError(f"OpenAI API error: {str(e)}")

    async def _generate_gemini_response(
        self,
        query: str,
        context: str,
        model: str,
        system_prompt: str,
        temperature: float,
        max_tokens: Optional[int],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using Gemini"""
        
        if not settings.GEMINI_API_KEY:
            raise ValueError("Gemini API key not configured")
        
        try:
            # Initialize Gemini model
            gemini_model = genai.GenerativeModel(model)
            
            # Prepare prompt
            full_prompt = f"{system_prompt}\n\n"
            if context:
                full_prompt += f"Context:\n{context}\n\n"
            full_prompt += f"Query: {query}"
            
            start_time = time.time()
            
            response = await gemini_model.generate_content_async(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                )
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "content": response.text,
                "model": model,
                "tokens_used": response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                "execution_time": execution_time,
                "finish_reason": "stop"
            }
            
        except Exception as e:
            raise ValueError(f"Gemini API error: {str(e)}")

    async def generate_embedding(
        self, text: str, model: str = "text-embedding-ada-002"
    ) -> List[float]:
        """Generate embedding for text"""
        
        if model.startswith("text-embedding"):
            return await self._generate_openai_embedding(text, model)
        else:
            raise ValueError(f"Unsupported embedding model: {model}")

    async def _generate_openai_embedding(
        self, text: str, model: str
    ) -> List[float]:
        """Generate embedding using OpenAI"""
        
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key not configured")
        
        try:
            response = await openai.Embedding.acreate(
                model=model,
                input=text
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            raise ValueError(f"OpenAI embedding error: {str(e)}")

    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """Check content for policy violations using OpenAI moderation"""
        
        if not settings.OPENAI_API_KEY:
            return {"flagged": False, "categories": {}}
        
        try:
            response = await openai.Moderation.acreate(input=text)
            moderation_result = response.results[0]
            
            return {
                "flagged": moderation_result.flagged,
                "categories": moderation_result.categories,
                "category_scores": moderation_result.category_scores
            }
            
        except Exception as e:
            print(f"Moderation error: {str(e)}")
            return {"flagged": False, "categories": {}}

    async def count_tokens(self, text: str, model: str = "gpt-3.5-turbo") -> int:
        """Estimate token count for text"""
        
        # Simple estimation: ~4 characters per token for English text
        # This is a rough approximation - for accurate counting, use tiktoken library
        return len(text) // 4

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models"""
        
        models = {
            "openai": [],
            "gemini": []
        }
        
        if settings.OPENAI_API_KEY:
            models["openai"] = [
                "gpt-3.5-turbo",
                "gpt-4",
                "gpt-4-turbo",
                "text-davinci-003"
            ]
        
        if settings.GEMINI_API_KEY:
            models["gemini"] = [
                "gemini-pro",
                "gemini-pro-vision"
            ]
        
        return models

    async def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        
        model_info = {
            "gpt-3.5-turbo": {
                "provider": "openai",
                "max_tokens": 4096,
                "cost_per_1k_tokens": 0.002,
                "context_window": 4096
            },
            "gpt-4": {
                "provider": "openai", 
                "max_tokens": 8192,
                "cost_per_1k_tokens": 0.03,
                "context_window": 8192
            },
            "gemini-pro": {
                "provider": "google",
                "max_tokens": 2048,
                "cost_per_1k_tokens": 0.001,
                "context_window": 32768
            }
        }
        
        return model_info.get(model, {"provider": "unknown"})
