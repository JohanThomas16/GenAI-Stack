import httpx
from typing import List, Dict, Any, Optional
from serpapi import GoogleSearch

from app.core.config import settings

class WebSearchService:
    def __init__(self):
        self.serp_api_key = settings.SERP_API_KEY
        self.timeout = 10.0

    async def search(
        self,
        query: str,
        max_results: int = 5,
        engine: str = "google",
        country: str = "us",
        language: str = "en",
        safe_search: str = "moderate"
    ) -> List[Dict[str, Any]]:
        """Perform web search using specified engine"""
        
        if engine == "google" and self.serp_api_key:
            return await self._search_with_serpapi(
                query, max_results, country, language, safe_search
            )
        elif engine == "duckduckgo":
            return await self._search_with_duckduckgo(query, max_results)
        else:
            # Fallback to DuckDuckGo if no API key
            return await self._search_with_duckduckgo(query, max_results)

    async def _search_with_serpapi(
        self,
        query: str,
        max_results: int,
        country: str,
        language: str,
        safe_search: str
    ) -> List[Dict[str, Any]]:
        """Search using SerpAPI (Google)"""
        
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": self.serp_api_key,
                "num": max_results,
                "gl": country,
                "hl": language,
                "safe": safe_search
            })
            
            results = search.get_dict()
            
            if "organic_results" not in results:
                return []
            
            formatted_results = []
            for result in results["organic_results"][:max_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "position": result.get("position", 0),
                    "source": "google"
                })
            
            return formatted_results
            
        except Exception as e:
            raise ValueError(f"SerpAPI search error: {str(e)}")

    async def _search_with_duckduckgo(
        self, query: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo (free, no API key required)"""
        
        try:
            # DuckDuckGo Instant Answer API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://api.duckduckgo.com/",
                    params={
                        "q": query,
                        "format": "json",
                        "no_html": "1",
                        "skip_disambig": "1"
                    }
                )
                
                if response.status_code != 200:
                    raise ValueError(f"DuckDuckGo API returned status {response.status_code}")
                
                data = response.json()
                
                formatted_results = []
                
                # Add instant answer if available
                if data.get("Abstract"):
                    formatted_results.append({
                        "title": data.get("Heading", query),
                        "link": data.get("AbstractURL", ""),
                        "snippet": data.get("Abstract", ""),
                        "position": 1,
                        "source": "duckduckgo_instant"
                    })
                
                # Add related topics
                for i, topic in enumerate(data.get("RelatedTopics", [])[:max_results-1]):
                    if isinstance(topic, dict) and topic.get("Text"):
                        formatted_results.append({
                            "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                            "link": topic.get("FirstURL", ""),
                            "snippet": topic.get("Text", ""),
                            "position": i + 2,
                            "source": "duckduckgo_related"
                        })
                
                return formatted_results[:max_results]
                
        except Exception as e:
            # Fallback to mock results for demo purposes
            return await self._get_mock_search_results(query, max_results)

    async def _get_mock_search_results(
        self, query: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Return mock search results for demo purposes"""
        
        mock_results = []
        
        for i in range(min(max_results, 3)):
            mock_results.append({
                "title": f"Search result {i+1} for: {query}",
                "link": f"https://example.com/result_{i+1}",
                "snippet": f"This is a mock search result snippet for query '{query}'. This would normally contain relevant information from web search.",
                "position": i + 1,
                "source": "mock"
            })
        
        return mock_results

    async def search_news(
        self,
        query: str,
        max_results: int = 5,
        country: str = "us",
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Search for news articles"""
        
        if not self.serp_api_key:
            return []
        
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": self.serp_api_key,
                "tbm": "nws",  # News search
                "num": max_results,
                "gl": country,
                "hl": language
            })
            
            results = search.get_dict()
            
            if "news_results" not in results:
                return []
            
            formatted_results = []
            for result in results["news_results"][:max_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "date": result.get("date", ""),
                    "source": result.get("source", ""),
                    "position": result.get("position", 0)
                })
            
            return formatted_results
            
        except Exception as e:
            raise ValueError(f"News search error: {str(e)}")

    async def search_images(
        self,
        query: str,
        max_results: int = 10,
        size: str = "medium",
        type: str = "photo"
    ) -> List[Dict[str, Any]]:
        """Search for images"""
        
        if not self.serp_api_key:
            return []
        
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": self.serp_api_key,
                "tbm": "isch",  # Image search
                "num": max_results,
                "imgsz": size,
                "imgtype": type
            })
            
            results = search.get_dict()
            
            if "images_results" not in results:
                return []
            
            formatted_results = []
            for result in results["images_results"][:max_results]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "thumbnail": result.get("thumbnail", ""),
                    "original": result.get("original", ""),
                    "source": result.get("source", ""),
                    "position": result.get("position", 0)
                })
            
            return formatted_results
            
        except Exception as e:
            raise ValueError(f"Image search error: {str(e)}")

    async def get_search_suggestions(self, query: str) -> List[str]:
        """Get search suggestions for a query"""
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    "https://suggestqueries.google.com/complete/search",
                    params={
                        "client": "firefox",
                        "q": query
                    }
                )
                
                if response.status_code == 200:
                    # Parse JSON response
                    data = response.json()
                    if len(data) > 1 and isinstance(data[1], list):
                        return data[1][:5]  # Return top 5 suggestions
                
                return []
                
        except Exception as e:
            return []

    def get_search_engines(self) -> List[str]:
        """Get list of available search engines"""
        
        engines = ["duckduckgo"]
        
        if self.serp_api_key:
            engines.append("google")
        
        return engines

    async def validate_api_key(self) -> bool:
        """Validate SerpAPI key"""
        
        if not self.serp_api_key:
            return False
        
        try:
            search = GoogleSearch({
                "q": "test",
                "api_key": self.serp_api_key,
                "num": 1
            })
            
            results = search.get_dict()
            return "error" not in results
            
        except Exception:
            return False
