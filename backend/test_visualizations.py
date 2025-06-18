#!/usr/bin/env python3
"""
Test script to verify visualizations are properly captured and included in responses.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.app import agent


async def test_visualizations():
    """Test that the agent creates and includes visualizations in responses."""
    
    print("🧪 Testing Visualization Integration")
    print("=" * 50)
    
    # Test query that should definitely need visualization
    test_query = "Compare the market performance of the top 5 tech companies (Apple, Microsoft, Google, Amazon, Meta) over the last 3 years. Create charts showing their stock price growth and market cap changes."
    
    print(f"🔍 Research Query: {test_query}")
    print("\n" + "=" * 50)
    
    config = {
        "configurable": {
            "use_azure_ai_search": True,
            "enable_code_interpreter": True,
            "web_search_tool": "tavily",
            "user_id": "test_user",
            "thread_id": "test_viz_thread"
        }
    }
    
    try:
        # Run the agent
        messages = [{"role": "user", "content": test_query}]
        
        print("🚀 Starting research agent...")
        final_response = None
        
        async for chunk in agent.astream({"messages": messages}, config=config):
            node_name = list(chunk.keys())[0]
            node_data = chunk[node_name]
            
            # Track the flow
            if node_name == "finalize_answer":
                code_needed = node_data.get("code_analysis_needed", False)
                analysis_type = node_data.get("analysis_type", "none")
                print(f"\n📊 FINALIZE ANSWER: Code needed = {'✅' if code_needed else '❌'}, Type = {analysis_type}")
                    
            elif node_name == "code_generator":
                generated_code = node_data.get("generated_code", "")
                if generated_code:
                    print(f"\n🛠️  CODE GENERATOR: Generated {len(generated_code)} chars of Python code")
                    
            elif node_name == "code_executor":
                results = node_data.get("code_analysis_results", [])
                print(f"\n⚡ CODE EXECUTOR: {len(results)} result(s)")
                for i, result in enumerate(results):
                    if isinstance(result, dict):
                        visualizations = result.get("visualizations", [])
                        print(f"   Result {i+1}: {len(visualizations)} visualization(s)")
                        if visualizations:
                            for j, viz in enumerate(visualizations):
                                print(f"     Viz {j+1}: {viz.get('type', 'unknown')} format={viz.get('format', 'unknown')}")
                                
            elif node_name == "report_generator":
                final_response = node_data
                report = node_data.get("final_report", "")
                messages = node_data.get("messages", [])
                
                print(f"\n📋 FINAL REPORT: {len(report)} characters")
                
                # Check message metadata for visualizations
                if messages:
                    msg = messages[0]
                    additional_kwargs = getattr(msg, 'additional_kwargs', {})
                    code_results = additional_kwargs.get('code_analysis_results', [])
                    
                    print(f"\n🔍 MESSAGE METADATA CHECK:")
                    print(f"   Has additional_kwargs: {'✅' if additional_kwargs else '❌'}")
                    print(f"   Has code_analysis_results: {'✅' if code_results else '❌'}")
                    
                    total_visualizations = 0
                    for result in code_results:
                        if isinstance(result, dict) and result.get("visualizations"):
                            total_visualizations += len(result["visualizations"])
                    
                    print(f"   Total visualizations in metadata: {total_visualizations}")
                    
                    if total_visualizations > 0:
                        print("   ✅ Visualizations are properly included in message metadata!")
                    else:
                        print("   ❌ No visualizations found in message metadata")
        
        print("\n" + "=" * 50)
        print("✅ Visualization test completed!")
        
        return final_response
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_visualizations())
    if result:
        print(f"\n💫 Test completed successfully with response containing {len(str(result))} characters")
