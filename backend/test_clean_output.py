#!/usr/bin/env python3
"""
Test the enhanced report generation with cleaner output formatting.
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import the agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent.graph import graph
from agent.configuration import Configuration

async def test_clean_output():
    """Test that the agent provides clean, user-friendly output."""
    
    print("🧪 Testing Enhanced Clean Output Generation")
    print("=" * 60)
    
    # Test with the mobile brand pie chart query
    query = "pie chart of different mobile brands in Ireland and their share of market sentiment"
    
    config = Configuration(
        enable_code_interpreter=True,
        use_azure_sessions=False,  # Use subprocess for testing
        use_web_research=False,    # Disable web research for faster testing
        number_of_initial_queries=1,
        max_research_loops=1,
        enable_report_generator=True
    )
    
    print(f"🔍 Query: {query}")
    print("-" * 40)
    
    try:
        # Run the agent
        result = await graph.ainvoke(
            {"messages": [{"role": "user", "content": query}]},
            config={"configurable": config.__dict__}
        )
        
        # Check the final report
        final_report = result.get("final_report", "")
        print(f"✅ Agent completed successfully")
        print(f"\n📄 FINAL REPORT OUTPUT:")
        print("=" * 60)
        print(final_report)
        print("=" * 60)
        
        # Check metadata
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            additional_kwargs = getattr(last_message, 'additional_kwargs', {})
            
            print(f"\n📊 OUTPUT METADATA:")
            print(f"   Has visualizations: {additional_kwargs.get('has_visualizations', False)}")
            print(f"   Analysis performed: {additional_kwargs.get('analysis_performed', False)}")
            print(f"   Report type: {additional_kwargs.get('report_type', 'unknown')}")
            print(f"   Sources count: {len(additional_kwargs.get('sources', []))}")
        
        # Check for code analysis results
        code_results = result.get("code_analysis_results", [])
        if code_results:
            print(f"\n🔬 CODE ANALYSIS SUMMARY:")
            for i, result_data in enumerate(code_results, 1):
                if isinstance(result_data, dict):
                    print(f"   Result {i}:")
                    print(f"     Execution method: {result_data.get('execution_method', 'unknown')}")
                    print(f"     Has visualizations: {len(result_data.get('visualizations', []))} found")
                    print(f"     Insights: {result_data.get('insights', 'none')[:100]}...")
        
        # Quality checks
        print(f"\n✅ OUTPUT QUALITY CHECKS:")
        
        # Check that code isn't exposed to user
        if "```python" in final_report.lower() or "import " in final_report:
            print("   ❌ Code blocks found in user output - should be hidden")
        else:
            print("   ✅ No code blocks exposed to user")
        
        # Check for reasonable length
        if len(final_report) > 5000:
            print("   ⚠️  Output is quite long - consider condensing")
        elif len(final_report) < 100:
            print("   ⚠️  Output is very short - may be incomplete")
        else:
            print("   ✅ Output length is reasonable")
        
        # Check for markdown formatting
        if "#" in final_report or "*" in final_report:
            print("   ✅ Markdown formatting detected")
        else:
            print("   ⚠️  No markdown formatting detected")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Run the test."""
    print("🚀 Testing Enhanced Clean Output")
    await test_clean_output()

if __name__ == "__main__":
    asyncio.run(main())
