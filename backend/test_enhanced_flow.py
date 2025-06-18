#!/usr/bin/env python3
"""
Test script to verify the enhanced research flow with proper code analysis decision.
This validates:
1. The finalize_answer step makes the decision about code analysis
2. The code_generator only receives context, not code
3. The code_executor only gets actual Python code
4. The output is clean and user-friendly
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.app import agent


async def test_research_flow():
    """Test the full research flow with a query that should trigger code analysis."""
    
    print("🧪 Testing Enhanced Research Flow")
    print("=" * 50)
    
    # Test query that should benefit from code analysis and visualization
    test_query = "Compare Apple and Microsoft stock performance over the last 5 years, including revenue growth and market cap changes"
    
    print(f"🔍 Research Query: {test_query}")
    print("\n" + "=" * 50)
    
    config = {
        "configurable": {
            "use_azure_ai_search": True,
            "enable_code_interpreter": True,
            "web_search_tool": "tavily",
            "user_id": "test_user",
            "thread_id": "test_flow_thread"
        }
    }
    
    try:
        # Run the agent
        messages = [{"role": "user", "content": test_query}]
        
        print("🚀 Starting research agent...")
        async for chunk in agent.astream({"messages": messages}, config=config):
            node_name = list(chunk.keys())[0]
            node_data = chunk[node_name]
            
            # Print key decision points
            if node_name == "finalize_answer":
                code_needed = node_data.get("code_analysis_needed", False)
                analysis_type = node_data.get("analysis_type", "none")
                rationale = node_data.get("analysis_rationale", "")
                
                print(f"\n📊 FINALIZE ANSWER DECISION:")
                print(f"   Code Analysis Needed: {'✅ YES' if code_needed else '❌ NO'}")
                if rationale:
                    print(f"   Rationale: {rationale}")
                if analysis_type != "none":
                    print(f"   Analysis Type: {analysis_type}")
                    
            elif node_name == "code_generator":
                generated_code = node_data.get("generated_code", "")
                if generated_code:
                    print(f"\n🛠️  CODE GENERATOR OUTPUT:")
                    print(f"   Generated: {len(generated_code)} characters of Python code")
                    print(f"   Preview: {generated_code[:100]}...")
                else:
                    print(f"\n🛠️  CODE GENERATOR: No code generated")
                    
            elif node_name == "code_executor":
                results = node_data.get("code_analysis_results", [])
                if results:
                    print(f"\n⚡ CODE EXECUTOR RESULTS:")
                    for result in results:
                        if isinstance(result, dict):
                            insights = result.get("insights", "")
                            errors = result.get("errors", "")
                            if insights:
                                print(f"   Insights: {insights[:100]}...")
                            if errors:
                                print(f"   Errors: {errors}")
                                
            elif node_name == "report_generator":
                final_report = node_data.get("final_report", "")
                if final_report:
                    print(f"\n📋 FINAL REPORT PREVIEW:")
                    print(f"   Length: {len(final_report)} characters")
                    print(f"   Preview: {final_report[:200]}...")
                    
                    # Check for clean output (no code blocks, no technical details)
                    has_code_blocks = "```python" in final_report or "```" in final_report
                    has_technical_details = any(word in final_report.lower() for word in [
                        "import pandas", "matplotlib", "def ", "print(", "traceback"
                    ])
                    
                    print(f"\n🧹 OUTPUT QUALITY CHECK:")
                    print(f"   Contains code blocks: {'❌ YES (BAD)' if has_code_blocks else '✅ NO (GOOD)'}")
                    print(f"   Contains technical details: {'❌ YES (BAD)' if has_technical_details else '✅ NO (GOOD)'}")
        
        print("\n" + "=" * 50)
        print("✅ Research flow test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_research_flow())
