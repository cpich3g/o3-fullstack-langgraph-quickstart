"""
Test script to verify enhanced web research functionality
"""
import asyncio
from agent.web_research import research_tool, enhance_ai_research_with_real_data

def test_sync_search():
    print("Testing web research tool...")
    print(f"SerpAPI enabled: {research_tool.use_serpapi}")
    
    if research_tool.use_serpapi:
        print("Testing real web search...")
        result = research_tool.search_web("Euro 2024 winners", num_results=3)
        print(f"Search results: {len(result)} sources found")
        for i, source in enumerate(result[:2]):
            print(f"  {i+1}. {source['title'][:60]}...")
    else:
        print("SerpAPI not configured, testing AI enhancement...")
        ai_content = "Spain won Euro 2024 by defeating England 2-1 in the final."
        result = enhance_ai_research_with_real_data("Euro 2024 winners", ai_content)
        print(f"Enhancement type: {result['enhancement_type']}")
        print(f"Enhanced content length: {len(result['enhanced_content'])}")

async def test_async_research():
    if research_tool.use_serpapi:
        print("\nTesting async research...")
        result = await research_tool.research_query("Euro 2024 winners", max_sources=3)
        print(f"Research completed: {result['total_sources']} sources, {result['successful_scrapes']} scraped")

if __name__ == "__main__":
    test_sync_search()
    if research_tool.use_serpapi:
        asyncio.run(test_async_research())
