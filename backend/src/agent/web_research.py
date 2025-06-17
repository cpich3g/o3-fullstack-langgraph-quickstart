"""
Enhanced web research tools with SerpAPI and Tavily integration.
Falls back to AI-based research if no search engine is configured.
"""
import os
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from serpapi import GoogleSearch
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import Tavily
try:
    from langchain_tavily import TavilySearch
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False


class WebResearchTool:
    """Enhanced web research tool using SerpAPI, Tavily, and web scraping with AI fallback."""
    
    def __init__(self, search_engine: str = "serpapi"):
        self.search_engine = search_engine.lower()
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.tavily_key = os.getenv("TAVILY_API_KEY")
        
        # Initialize search tools based on availability and preference
        self.use_serpapi = False
        self.use_tavily = False
        self.tavily_tool = None
        
        if self.search_engine == "tavily" and self.tavily_key and TAVILY_AVAILABLE:
            try:
                self.tavily_tool = TavilySearch(
                    max_results=20,
                    topic="general",
                    include_answer=True,
                    include_raw_content=True,
                    search_depth="advanced"
                )
                self.use_tavily = True
                print(f"Initialized Tavily search engine")
            except Exception as e:
                print(f"Failed to initialize Tavily: {e}")
        
        elif self.search_engine == "serpapi" and self.serpapi_key:
            self.use_serpapi = True
            print(f"Initialized SerpAPI search engine")
        
        # Fallback logic
        if not self.use_tavily and not self.use_serpapi:
            if self.tavily_key and TAVILY_AVAILABLE:
                try:
                    self.tavily_tool = TavilySearch(
                        max_results=20,
                        topic="general",
                        include_answer=True,
                        include_raw_content=True,
                        search_depth="advanced"
                    )
                    self.use_tavily = True
                    print("Falling back to Tavily search engine")
                except Exception as e:
                    print(f"Tavily fallback failed: {e}")            
            elif self.serpapi_key:
                self.use_serpapi = True
                print("Falling back to SerpAPI search engine")
            else:
                print("No search engines available. Using AI-based research fallback.")
    
    def search_with_tavily(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search using Tavily API."""
        if not self.use_tavily or not self.tavily_tool:
            return []
        
        try:
            # Set max_results on the tool
            self.tavily_tool.max_results = min(num_results, 10)
            
            # Invoke the search
            result = self.tavily_tool.invoke({"query": query})
            
            formatted_results = []
            
            # Handle the response format
            if isinstance(result, dict) and "results" in result:
                results = result["results"]
            elif isinstance(result, list):
                results = result
            else:
                # If it's a string or other format, try to extract results
                return []
            
            for i, item in enumerate(results[:num_results]):
                formatted_results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:300] + "..." if len(item.get("content", "")) > 300 else item.get("content", ""),
                    "content": item.get("content", ""),
                    "position": i + 1
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching with Tavily: {e}")
            return []
    
    def search_web(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search the web using the configured search engine."""
        if self.use_tavily:
            return self.search_with_tavily(query, num_results)
        elif self.use_serpapi:
            return self.search_with_serpapi(query, num_results)
        else:
            return []
    
    def search_with_serpapi(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search the web using SerpAPI Google Search."""
        if not self.use_serpapi:
            return []
            
        try:
            search = GoogleSearch({
                "q": query,
                "api_key": self.serpapi_key,
                "num": num_results,
                "hl": "en",
                "gl": "us"
            })
            
            results = search.get_dict()
            
            if "organic_results" not in results:
                return []
            
            formatted_results = []
            for result in results["organic_results"]:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "content": "",  # SerpAPI doesn't provide full content
                    "position": result.get("position", 0)
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching with SerpAPI: {e}")
            return []
    
    async def scrape_content(self, url: str) -> Dict[str, Any]:
        """Scrape content from a URL."""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                async with session.get(url, timeout=10, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style", "nav", "footer", "header"]):
                            script.decompose()
                        
                        # Extract text content
                        text = soup.get_text()
                        lines = (line.strip() for line in text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        text = ' '.join(chunk for chunk in chunks if chunk)
                        return {
                            "url": url,
                            "content": text[:3000],  # Limit content length
                            "title": soup.title.string if soup.title else "",
                            "success": True
                        }
                    else:
                        return {"url": url, "content": "", "title": "", "success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            return {"url": url, "content": "", "title": "", "success": False, "error": str(e)}
    
    async def research_query(self, query: str, max_sources: int = 5) -> Dict[str, Any]:
        """Perform comprehensive research on a query."""
        if not self.use_tavily and not self.use_serpapi:
            return {
                "query": query,
                "sources": [],
                "summary": "No search engines configured. Using AI-based research fallback.",
                "search_engine": "none"
            }
        
        # Search for relevant URLs
        search_results = self.search_web(query, num_results=max_sources * 2)
        
        if not search_results:
            return {
                "query": query,
                "sources": [],
                "summary": "No search results found for the query.",
                "search_engine": self.search_engine
            }
        
        # For Tavily, we already have content, for SerpAPI we need to scrape
        sources = []
        scraping_tasks = []
        
        for result in search_results[:max_sources]:
            if self.use_tavily and result.get("content"):
                # Tavily already provides content
                sources.append({
                    "title": result["title"],
                    "url": result["url"],
                    "snippet": result["snippet"],
                    "content": result["content"][:2000],  # Limit content
                    "scraped_successfully": True
                })
            else:
                # SerpAPI requires scraping
                scraping_tasks.append(self.scrape_content(result["url"]))
        
        # If we have scraping tasks (SerpAPI), execute them
        if scraping_tasks:
            scraped_contents = await asyncio.gather(*scraping_tasks, return_exceptions=True)
            
            # Combine search results with scraped content
            for i, result in enumerate(search_results[:max_sources]):
                if i < len(scraped_contents):
                    scraped = scraped_contents[i] if not isinstance(scraped_contents[i], Exception) else {}
                    sources.append({
                        "title": result["title"],
                        "url": result["url"],
                        "snippet": result["snippet"],
                        "content": scraped.get("content", "")[:2000] if isinstance(scraped, dict) else "",
                        "scraped_successfully": scraped.get("success", False) if isinstance(scraped, dict) else False
                    })
        
        return {
            "query": query,
            "sources": sources,
            "total_sources": len(sources),
            "successful_scrapes": sum(1 for s in sources if s["scraped_successfully"]),
            "search_engine": self.search_engine
        }


# Initialize the research tool with default settings
research_tool = WebResearchTool()


async def enhance_ai_research_with_real_data(query: str, ai_generated_content: str, search_engine: str = "serpapi") -> Dict[str, Any]:
    """
    Enhance AI-generated research with real web data when search engines are available.
    This function can be called to augment existing AI research.
    """
    # Use the existing global tool or create a new one with specified engine
    if search_engine != research_tool.search_engine:
        tool = WebResearchTool(search_engine=search_engine)
    else:
        tool = research_tool
    
    if not tool.use_tavily and not tool.use_serpapi:
        return {
            "enhanced_content": ai_generated_content,
            "sources": [],
            "enhancement_type": "ai_only"
        }
    
    try:
        # Use await instead of asyncio.run since we're already in an async context
        research_result = await tool.research_query(query, max_sources=3)
        
        if research_result["sources"]:
            # Combine AI content with real sources
            source_summaries = []
            for source in research_result["sources"]:
                if source["content"] or source["snippet"]:
                    content_preview = source["content"] if source["content"] else source["snippet"]
                    source_summaries.append(f"**{source['title']}**: {content_preview[:200]}...")
            
            enhanced_content = ai_generated_content
            if source_summaries:
                enhanced_content += f"\n\n**Additional Sources Found ({research_result['search_engine'].upper()}):**\n" + "\n".join(source_summaries)
            
            return {
                "enhanced_content": enhanced_content,
                "sources": research_result["sources"],
                "enhancement_type": f"ai_plus_{research_result['search_engine']}"
            }
    except Exception as e:
        print(f"Error enhancing research: {e}")
    
    return {
        "enhanced_content": ai_generated_content,
        "sources": [],
        "enhancement_type": "ai_only"
    }
