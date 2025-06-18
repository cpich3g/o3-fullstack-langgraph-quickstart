#!/usr/bin/env python3
"""
Demonstration script showing the enhanced code generation and execution separation.

This script demonstrates:
1. How the agent decides when code is needed vs when it's not
2. How only actual Python code gets sent to the sandbox
3. How the validation layers work
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent.graph import _is_actual_python_code

def demonstrate_code_validation():
    """Demonstrate the Python code validation in action."""
    print("🔍 Code Validation Demonstration")
    print("=" * 50)
    
    examples = [
        {
            "title": "✅ Valid Python Code - Data Analysis",
            "content": """import pandas as pd
import matplotlib.pyplot as plt

# Create sample data
data = {'year': [2020, 2021, 2022, 2023], 
        'renewable_percent': [15.2, 18.1, 21.7, 24.3]}
df = pd.DataFrame(data)

# Calculate growth rate
df['growth_rate'] = df['renewable_percent'].pct_change() * 100

# Create visualization
plt.figure(figsize=(10, 6))
plt.plot(df['year'], df['renewable_percent'], marker='o')
plt.title('Renewable Energy Adoption Growth')
plt.ylabel('Percentage')
plt.show()

print("Analysis complete!")""",
            "should_execute": True
        },
        {
            "title": "❌ Text Explanation - No Code",
            "content": """The main challenges facing renewable energy adoption include:

1. High initial capital costs
2. Intermittency issues with solar and wind
3. Grid infrastructure limitations
4. Policy and regulatory barriers
5. Storage technology constraints

These factors create a complex landscape that requires coordinated solutions across technology, policy, and financing domains.""",
            "should_execute": False
        },
        {
            "title": "❌ Markdown with Code Blocks - Not Executable",
            "content": """Here's how you would analyze the data:

```python
import pandas as pd
df = pd.read_csv('data.csv')
```

This approach allows you to load the data and then process it according to your needs.""",
            "should_execute": False
        },
        {
            "title": "❌ Comments Only - No Executable Code",
            "content": """# This would be the approach for data analysis
# 1. Load the data using pandas
# 2. Clean and preprocess the data
# 3. Perform statistical analysis
# 4. Create visualizations""",
            "should_execute": False
        },
        {
            "title": "✅ Valid Python Code - Mathematical Calculation",
            "content": """import numpy as np

# Calculate compound annual growth rate (CAGR)
beginning_value = 150  # Million dollars
ending_value = 340     # Million dollars
periods = 5            # Years

cagr = (ending_value / beginning_value) ** (1/periods) - 1
print(f"CAGR: {cagr:.2%}")

# Calculate future projections
projections = []
for year in range(1, 6):
    projected_value = ending_value * (1 + cagr) ** year
    projections.append(projected_value)

print("5-year projections:", projections)""",
            "should_execute": True
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. {example['title']}")
        print("-" * 40)
        
        # Show content preview
        content_preview = example['content'][:100] + "..." if len(example['content']) > 100 else example['content']
        print(f"Content: {content_preview}")
        
        # Test validation
        is_python = _is_actual_python_code(example['content'])
        expected = example['should_execute']
        
        print(f"Validation Result: {'✅ Python code detected' if is_python else '❌ Not Python code'}")
        print(f"Should Execute: {'✅ Yes' if expected else '❌ No'}")
        print(f"Validation Correct: {'✅ Correct' if is_python == expected else '❌ Incorrect'}")
        
        if is_python:
            print("🔄 This content WOULD be sent to the execution sandbox")
        else:
            print("🚫 This content would NOT be sent to the sandbox")

def demonstrate_decision_logic():
    """Demonstrate the decision logic for when code generation is needed."""
    print("\n\n🤖 Code Generation Decision Logic")
    print("=" * 50)
    
    scenarios = [
        {
            "query": "Analyze the growth trends of renewable energy adoption in the US with specific percentages and create visualizations",
            "research_type": "Quantitative data requiring calculations and visualizations",
            "code_needed": True,
            "rationale": "Contains numerical data that benefits from computational analysis and visualization"
        },
        {
            "query": "What are the main policy challenges facing renewable energy adoption?", 
            "research_type": "Qualitative policy analysis",
            "code_needed": False,
            "rationale": "Conceptual analysis that doesn't require computational processing"
        },
        {
            "query": "Compare the ROI of solar vs wind investments with financial projections",
            "research_type": "Financial modeling and calculations",
            "code_needed": True,
            "rationale": "Requires mathematical calculations and financial modeling"
        },
        {
            "query": "What is the current regulatory framework for renewable energy in Europe?",
            "research_type": "Regulatory and legal information",
            "code_needed": False,
            "rationale": "Factual research that doesn't involve computational analysis"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Query: {scenario['query']}")
        print(f"   Research Type: {scenario['research_type']}")
        print(f"   Code Needed: {'✅ Yes' if scenario['code_needed'] else '❌ No'}")
        print(f"   Rationale: {scenario['rationale']}")
        
        if scenario['code_needed']:
            print(f"   🔄 Agent would generate Python code for analysis")
        else:
            print(f"   📝 Agent would proceed directly to report generation")

def main():
    """Run the demonstration."""
    print("🚀 Enhanced Agent Code Separation Demonstration")
    print("=" * 60)
    
    demonstrate_code_validation()
    demonstrate_decision_logic()
    
    print("\n" + "=" * 60)
    print("🎯 Key Takeaways:")
    print("• Only actual Python code reaches the execution sandbox")
    print("• Multiple validation layers ensure content safety")
    print("• Smart decision making conserves computational resources")
    print("• Clear separation between generation and execution phases")
    print("• Robust fallback handling for edge cases")

if __name__ == "__main__":
    main()
