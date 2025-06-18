#!/usr/bin/env python3
"""
Test script for the enhanced LangGraph agent with Azure Code Interpreter and Report Generator.
"""

import os
import asyncio
import sys
from pathlib import Path

# Add the src directory to the path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from dotenv import load_dotenv
from agent.graph import graph
from langchain_core.messages import HumanMessage

# Load environment variables
load_dotenv()

async def test_enhanced_agent():
    """Test the enhanced agent with code interpretation and report generation."""
      # Check if required environment variables are set
    required_env_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_API_VERSION"
    ]
    
    # Optional Azure Container Apps sessions endpoint
    azure_sessions_endpoint = os.getenv("AZURE_POOL_MANAGEMENT_ENDPOINT")
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    if azure_sessions_endpoint:
        print(f"✅ Azure Container Apps sessions endpoint configured: {azure_sessions_endpoint[:50]}...")
    else:
        print("⚠️  Azure Container Apps sessions endpoint not configured (AZURE_POOL_MANAGEMENT_ENDPOINT)")
        print("   Code execution will fall back to subprocess method")
    
    print("🧪 Testing Enhanced LangGraph Agent with Azure Code Interpreter and Report Generator")
    print("=" * 80)    # Test configuration
    test_config = {
        "configurable": {
            "enable_code_interpreter": True,
            "enable_report_generator": True,
            "use_web_research": True,
            "use_azure_sessions": True,  # Enable Azure Container Apps sessions
            "azure_sessions_no_auth": True,  # Set to True for public endpoints
            "max_research_loops": 1,
            "number_of_initial_queries": 2
        }
    }
    
    # Test query that should trigger code analysis
    test_message = HumanMessage(content="""
    Analyze Apple's financial performance in 2024. I want to understand:
    1. Revenue growth compared to 2023
    2. iPhone sales trends
    3. Stock performance
    4. Market share analysis
    
    Please provide data analysis with calculations and a comprehensive report.
    """)
    
    try:
        print("🚀 Starting research and analysis...")
        
        # Run the graph
        result = await graph.ainvoke(
            {"messages": [test_message]},
            config=test_config
        )
          print("\n✅ Research completed successfully!")
        print("=" * 80)
        
        # Display results
        if result.get("final_report"):
            print("📊 FINAL REPORT:")
            print("-" * 40)
            print(result["final_report"])
            print("\n")
        
        if result.get("code_analysis_results"):
            print("🔬 CODE ANALYSIS RESULTS:")
            print("-" * 40)
            for i, analysis in enumerate(result["code_analysis_results"], 1):
                print(f"Analysis {i}:")
                if analysis.get("insights"):
                    print(f"  Insights: {analysis['insights']}")
                if analysis.get("results"):
                    print(f"  Results: {analysis['results']}")
                if analysis.get("execution_method"):
                    print(f"  Execution Method: {analysis['execution_method']}")
                if analysis.get("execution_time_ms"):
                    print(f"  Execution Time: {analysis['execution_time_ms']}ms")
                if analysis.get("visualizations"):
                    print(f"  Visualizations: {len(analysis['visualizations'])} generated")
                    for j, viz in enumerate(analysis["visualizations"], 1):
                        print(f"    {j}. {viz.get('type', 'Unknown')} ({viz.get('format', 'Unknown format')})")
                if analysis.get("errors"):
                    print(f"  Errors: {analysis['errors']}")
                print()
        
        # Display code generation info
        if result.get("code_analysis_needed"):
            print("📝 CODE GENERATION:")
            print("-" * 20)
            print(f"Code Analysis Needed: {result.get('code_analysis_needed', False)}")
            generated_code = result.get("generated_code", "")
            if generated_code:
                print(f"Generated Code Length: {len(generated_code)} characters")
                print("Code Preview:")
                print("```python")
                print(generated_code[:200] + "..." if len(generated_code) > 200 else generated_code)
                print("```")
            print()
        
        if result.get("sources_gathered"):
            print("📚 SOURCES:")
            print("-" * 40)
            for i, source in enumerate(result["sources_gathered"], 1):
                print(f"{i}. {source.get('label', 'N/A')}")
                print(f"   URL: {source.get('value', 'N/A')}")
                print()
        
        # Display research summary
        if result.get("messages") and result["messages"][-1].additional_kwargs:
            summary = result["messages"][-1].additional_kwargs.get("research_summary", {})
            print("📈 RESEARCH SUMMARY:")
            print("-" * 40)
            print(f"Total Queries: {summary.get('total_queries', 0)}")
            print(f"Research Loops: {summary.get('research_loops', 0)}")
            print(f"Sources Found: {summary.get('sources_found', 0)}")
            print(f"Report Generated: {summary.get('report_generated', False)}")
            
            if summary.get("research_steps"):
                print("\nResearch Steps:")
                for step in summary["research_steps"]:
                    print(f"  {step['step']}. [{step['type']}] {step['description']} - {step['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test the configuration system."""
    print("🔧 Testing Configuration System")
    print("-" * 40)
    
    from agent.configuration import Configuration
    
    # Test default configuration
    config = Configuration()
    print(f"✅ Default query generator model: {config.query_generator_model}")
    print(f"✅ Code interpreter enabled: {config.enable_code_interpreter}")
    print(f"✅ Report generator enabled: {config.enable_report_generator}")
    print(f"✅ Code interpreter model: {config.code_interpreter_model}")
    print(f"✅ Report generator model: {config.report_generator_model}")
    
    return True

if __name__ == "__main__":
    print("🎯 Enhanced LangGraph Agent Test Suite")
    print("=" * 80)
    
    # Test configuration first
    config_success = test_configuration()
    print()
    
    if config_success:
        # Test the full agent
        success = asyncio.run(test_enhanced_agent())
        
        if success:
            print("🎉 All tests passed! Enhanced agent is working correctly.")
        else:
            print("💥 Tests failed. Please check the configuration and try again.")
            sys.exit(1)
    else:
        print("💥 Configuration test failed.")
        sys.exit(1)
