#!/usr/bin/env python3
"""
Test script to validate the enhanced code generation and execution separation.

This script tests:
1. That only actual Python code gets sent to the sandbox
2. That the agent correctly validates and routes based on code presence
3. That the code generator makes intelligent decisions about when code is needed
"""

import asyncio
import sys
import os

# Add the src directory to the path so we can import the agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent.graph import graph
from agent.configuration import Configuration

async def test_code_separation():
    """Test that the agent properly separates code generation from execution."""
    
    print("🧪 Testing Enhanced Code Generation and Execution Separation")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "name": "Research requiring computational analysis",
            "query": "Analyze the growth trends of renewable energy adoption in the US from 2010 to 2023 with specific percentages and create visualizations",
            "expect_code": True
        },
        {
            "name": "Conceptual research without computational needs",
            "query": "What are the main challenges facing renewable energy adoption in developing countries?",
            "expect_code": False
        },
        {
            "name": "Financial data analysis requiring calculations", 
            "query": "Compare the ROI of solar vs wind investments over the past 5 years with specific financial metrics and projections",
            "expect_code": True
        },
        {
            "name": "Simple factual research",
            "query": "What is the current policy framework for renewable energy in California?",
            "expect_code": False
        }
    ]
    
    config = Configuration(
        enable_code_interpreter=True,
        use_azure_sessions=False,  # Use subprocess for testing
        use_web_research=False,    # Disable web research for faster testing
        number_of_initial_queries=1,
        max_research_loops=1
    )
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        print(f"Query: {test_case['query']}")
        print("-" * 40)
        
        try:
            # Run the agent
            result = await graph.ainvoke(
                {"messages": [{"role": "user", "content": test_case['query']}]},
                config={"configurable": config.__dict__}
            )
            
            # Check the results
            code_analysis_needed = result.get("code_analysis_needed", False)
            generated_code = result.get("generated_code", "").strip()
            code_analysis_results = result.get("code_analysis_results", [])
            
            print(f"✅ Agent completed successfully")
            print(f"   Code analysis needed: {code_analysis_needed}")
            print(f"   Code generated: {'Yes' if generated_code else 'No'}")
            print(f"   Code executed: {'Yes' if code_analysis_results and code_analysis_results[0] != 'No code to execute' else 'No'}")
            
            if generated_code:
                print(f"   Code preview: {generated_code[:100]}{'...' if len(generated_code) > 100 else ''}")
            
            # Validate expectations
            if test_case["expect_code"]:
                if code_analysis_needed and generated_code:
                    print(f"✅ Correctly identified need for computational analysis")
                else:
                    print(f"⚠️  Expected code generation but none occurred")
            else:
                if not code_analysis_needed:
                    print(f"✅ Correctly determined no computational analysis needed")
                else:
                    print(f"⚠️  Unexpected code generation for conceptual query")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("🏁 Code separation testing completed")

def test_python_code_validation():
    """Test the Python code validation function."""
    print("\n🧪 Testing Python Code Validation Function")
    print("=" * 40)
    
    from agent.graph import _is_actual_python_code
    
    test_cases = [
        {
            "name": "Valid Python code",
            "code": "import pandas as pd\ndf = pd.DataFrame({'a': [1, 2, 3]})\nprint(df.head())",
            "expected": True
        },
        {
            "name": "Text explanation, not code",
            "code": "This is a text explanation about data analysis methods and approaches.",
            "expected": False
        },
        {
            "name": "Markdown with code blocks",
            "code": "Here's how to analyze data:\n```python\nimport pandas as pd\n```",
            "expected": False
        },
        {
            "name": "Empty content",
            "code": "",
            "expected": False
        },
        {
            "name": "Comments only",
            "code": "# This is just a comment\n# Another comment",
            "expected": False
        },
        {
            "name": "Python with matplotlib",
            "code": "import matplotlib.pyplot as plt\nplt.figure(figsize=(10, 6))\nplt.plot([1, 2, 3])\nplt.show()",
            "expected": True
        }
    ]
    
    for test_case in test_cases:
        result = _is_actual_python_code(test_case["code"])
        status = "✅" if result == test_case["expected"] else "❌"
        print(f"{status} {test_case['name']}: {result}")
        if result != test_case["expected"]:
            print(f"   Expected: {test_case['expected']}, Got: {result}")
            print(f"   Code: {test_case['code'][:50]}...")

async def main():
    """Run all tests."""
    print("🚀 Starting Enhanced Agent Tests")
    
    # Test the validation function first
    test_python_code_validation()
    
    # Test the agent workflow
    await test_code_separation()

if __name__ == "__main__":
    asyncio.run(main())
