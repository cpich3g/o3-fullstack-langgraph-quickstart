#!/usr/bin/env python3
"""
Test script to verify visualization flow from code execution to final message.
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.app import agent


async def test_visualization_flow():
    """Test that visualizations flow properly from code execution to final message."""
    
    print("🧪 Testing Complete Visualization Flow")
    print("=" * 60)
    
    # Query that should definitely generate visualizations
    test_query = "Compare the population growth of the top 5 most populous countries over the last 10 years. Create a line chart showing the trends."
    
    print(f"🔍 Research Query: {test_query}")
    print("\n" + "=" * 60)
    
    config = {
        "configurable": {
            "use_azure_ai_search": True,
            "enable_code_interpreter": True,
            "web_search_tool": "tavily",
            "user_id": "test_user",
            "thread_id": "test_viz_flow"
        }
    }
    
    try:
        # Run the agent
        messages = [{"role": "user", "content": test_query}]
        
        print("🚀 Starting research agent...")
        
        final_response = None
        code_execution_results = None
        
        async for chunk in agent.astream({"messages": messages}, config=config):
            node_name = list(chunk.keys())[0]
            node_data = chunk[node_name]
            
            # Track each node's output
            if node_name == "finalize_answer":
                code_needed = node_data.get("code_analysis_needed", False)
                print(f"\n📊 FINALIZE_ANSWER: Code needed = {'✅ YES' if code_needed else '❌ NO'}")
                    
            elif node_name == "code_generator":
                generated_code = node_data.get("generated_code", "")
                if generated_code:
                    print(f"\n🛠️  CODE_GENERATOR: Generated {len(generated_code)} chars")
                    # Show first few lines
                    lines = generated_code.split('\n')[:3]
                    for line in lines:
                        print(f"   {line}")
                    if len(generated_code.split('\n')) > 3:
                        print("   ...")
                    
            elif node_name == "code_executor":
                code_execution_results = node_data.get("code_analysis_results", [])
                print(f"\n⚡ CODE_EXECUTOR: {len(code_execution_results)} result(s)")
                
                for i, result in enumerate(code_execution_results):
                    if isinstance(result, dict):
                        visualizations = result.get("visualizations", [])
                        insights = result.get("insights", "")
                        errors = result.get("errors", "")
                        
                        print(f"   Result {i+1}:")
                        print(f"     Visualizations: {len(visualizations)}")
                        if visualizations:
                            for j, viz in enumerate(visualizations):
                                viz_type = viz.get('type', 'unknown')
                                viz_format = viz.get('format', 'unknown')
                                data_size = len(viz.get('base64_data', ''))
                                print(f"       Viz {j+1}: {viz_type}/{viz_format} ({data_size} chars)")
                        print(f"     Insights: {insights[:100]}..." if insights else "     Insights: None")
                        if errors:
                            print(f"     Errors: {errors}")
                                
            elif node_name == "report_generator":
                final_response = node_data
                report = node_data.get("final_report", "")
                messages_output = node_data.get("messages", [])
                
                print(f"\n📋 REPORT_GENERATOR:")
                print(f"   Report length: {len(report)} characters")
                print(f"   Messages created: {len(messages_output)}")
                
                # Check message metadata
                if messages_output:
                    msg = messages_output[0]
                    additional_kwargs = getattr(msg, 'additional_kwargs', {})
                    
                    print(f"\n🔍 FINAL MESSAGE ANALYSIS:")
                    print(f"   Has additional_kwargs: {'✅' if additional_kwargs else '❌'}")
                    
                    if additional_kwargs:
                        code_results = additional_kwargs.get('code_analysis_results', [])
                        has_viz_flag = additional_kwargs.get('has_visualizations', False)
                        
                        print(f"   Code analysis results: {len(code_results)}")
                        print(f"   Has visualizations flag: {'✅' if has_viz_flag else '❌'}")
                        
                        # Check for actual visualization data
                        total_visualizations = 0
                        for result in code_results:
                            if isinstance(result, dict) and result.get("visualizations"):
                                viz_count = len(result["visualizations"])
                                total_visualizations += viz_count
                                print(f"     Result has {viz_count} visualization(s)")
                                
                                # Show details of first visualization
                                if viz_count > 0:
                                    first_viz = result["visualizations"][0]
                                    data_size = len(first_viz.get('base64_data', ''))
                                    print(f"       First viz: {first_viz.get('type', 'unknown')} ({data_size} chars data)")
                        
                        print(f"   Total visualizations in final message: {total_visualizations}")
                        
                        if total_visualizations > 0:
                            print("   ✅ SUCCESS: Visualizations properly included in final message!")
                        else:
                            print("   ❌ PROBLEM: No visualizations found in final message")
                            
                            # Debug: compare with code execution results
                            if code_execution_results:
                                exec_viz_count = sum(len(r.get("visualizations", [])) for r in code_execution_results if isinstance(r, dict))
                                print(f"   Debug: Code executor had {exec_viz_count} visualizations")
                                if exec_viz_count > 0:
                                    print("   🐛 Issue: Visualizations lost between code_executor and report_generator!")
        
        print("\n" + "=" * 60)
        if final_response:
            print("✅ Visualization flow test completed!")
        else:
            print("❌ Test failed - no final response")
        
        return final_response
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(test_visualization_flow())
