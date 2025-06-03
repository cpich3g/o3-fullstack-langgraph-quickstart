"""
Enhanced web research tools with SerpAPI integration.
Falls back to AI-based research if SerpAPI is not configured.
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


class WebResearchTool:
    """Enhanced web research tool using SerpAPI and web scraping with AI fallback."""
    
    def __init__(self):
        self.serpapi_key = os.getenv("SERPAPI_API_KEY")
        self.use_serpapi = bool(self.serpapi_key)
        if not self.use_serpapi:
            print("SerpAPI key not found. Using AI-based research fallback.")
    
    def search_web(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
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
        if not self.use_serpapi:
            return {
                "query": query,
                "sources": [],
                "summary": "SerpAPI not configured. Using AI-based research fallback.",
                "serpapi_enabled": False
            }
        
        # Search for relevant URLs
        search_results = self.search_web(query, num_results=max_sources * 2)
        
        if not search_results:
            return {
                "query": query,
                "sources": [],
                "summary": "No search results found for the query.",
                "serpapi_enabled": True
            }
        
        # Scrape content from top results
        scraping_tasks = []
        for result in search_results[:max_sources]:
            scraping_tasks.append(self.scrape_content(result["url"]))
        
        scraped_contents = await asyncio.gather(*scraping_tasks, return_exceptions=True)
        
        # Combine search results with scraped content
        sources = []
        for i, result in enumerate(search_results[:max_sources]):
            scraped = scraped_contents[i] if i < len(scraped_contents) and not isinstance(scraped_contents[i], Exception) else {}
            sources.append({
                "title": result["title"],
                "url": result["url"],
                "snippet": result["snippet"],
                "content": scraped.get("content", "")[:2000] if isinstance(scraped, dict) else "",  # Limit content
                "scraped_successfully": scraped.get("success", False) if isinstance(scraped, dict) else False
            })
        
        return {
            "query": query,
            "sources": sources,
            "total_sources": len(sources),
            "successful_scrapes": sum(1 for s in sources if s["scraped_successfully"]),
            "serpapi_enabled": True
        }


# Initialize the research tool
research_tool = WebResearchTool()


async def enhance_ai_research_with_real_data(query: str, ai_generated_content: str) -> Dict[str, Any]:
    """
    Enhance AI-generated research with real web data when SerpAPI is available.
    This function can be called to augment existing AI research.
    """
    if not research_tool.use_serpapi:
        return {
            "enhanced_content": ai_generated_content,
            "sources": [],
            "enhancement_type": "ai_only"
        }
    
    try:
        # Use await instead of asyncio.run since we're already in an async context
        research_result = await research_tool.research_query(query, max_sources=3)
        
        if research_result["sources"]:
            # Combine AI content with real sources
            source_summaries = []
            for source in research_result["sources"]:
                if source["content"]:
                    source_summaries.append(f"**{source['title']}**: {source['snippet']}")
            
            enhanced_content = ai_generated_content
            if source_summaries:
                enhanced_content += "\n\n**Additional Sources Found:**\n" + "\n".join(source_summaries)
            
            return {
                "enhanced_content": enhanced_content,
                "sources": research_result["sources"],
                "enhancement_type": "ai_plus_web"
            }
    except Exception as e:
        print(f"Error enhancing research: {e}")
    
    return {
        "enhanced_content": ai_generated_content,
        "sources": [],
        "enhancement_type": "ai_only"
    }
