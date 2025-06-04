#!/usr/bin/env python3
"""
Test script for comparing SerpAPI and Tavily search engines.
"""
import os
import asyncio
from dotenv import load_dotenv
from agent.web_research import WebResearchTool

load_dotenv()

async def test_search_engines():
    """Test both SerpAPI and Tavily search engines."""
    
    test_query = "Euro 2024 winner"
    
    print("🔍 Testing Search Engines")
    print("=" * 50)
    print(f"Query: {test_query}")
    print()
    
    # Test SerpAPI
    print("🔎 Testing SerpAPI...")
    serpapi_tool = WebResearchTool(search_engine="serpapi")
    
    if serpapi_tool.use_serpapi:
        try:
            serpapi_results = await serpapi_tool.research_query(test_query, max_sources=3)
            print(f"✅ SerpAPI: Found {serpapi_results['total_sources']} sources")
            for i, source in enumerate(serpapi_results['sources'][:2], 1):
                print(f"   {i}. {source['title'][:60]}...")
                print(f"      URL: {source['url']}")
                print(f"      Snippet: {source['snippet'][:100]}...")
                print()
        except Exception as e:
            print(f"❌ SerpAPI Error: {e}")
    else:
        print("⚠️  SerpAPI: Not configured (missing SERPAPI_API_KEY)")
    
    print("-" * 50)
    
    # Test Tavily
    print("🔎 Testing Tavily...")
    tavily_tool = WebResearchTool(search_engine="tavily")
    
    if tavily_tool.use_tavily:
        try:
            tavily_results = await tavily_tool.research_query(test_query, max_sources=3)
            print(f"✅ Tavily: Found {tavily_results['total_sources']} sources")
            for i, source in enumerate(tavily_results['sources'][:2], 1):
                print(f"   {i}. {source['title'][:60]}...")
                print(f"      URL: {source['url']}")
                print(f"      Snippet: {source['snippet'][:100]}...")
                print()
        except Exception as e:
            print(f"❌ Tavily Error: {e}")
    else:
        print("⚠️  Tavily: Not configured (missing TAVILY_API_KEY)")
    
    print("=" * 50)
    print("✨ Test completed!")
    
    # Environment check
    print("\n🔧 Environment Check:")
    print(f"SERPAPI_API_KEY: {'✅ Set' if os.getenv('SERPAPI_API_KEY') else '❌ Not set'}")
    print(f"TAVILY_API_KEY: {'✅ Set' if os.getenv('TAVILY_API_KEY') else '❌ Not set'}")

if __name__ == "__main__":
    asyncio.run(test_search_engines())
