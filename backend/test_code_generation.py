#!/usr/bin/env python3
"""
Test script to validate that the code generator receives context (not code) 
and generates appropriate Python code based on analysis requirements.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.prompts import code_generator_instructions

# Azure OpenAI client
openai_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
)


def test_code_generation_prompt():
    """Test that the code generator creates Python code from research context."""
    
    print("🧪 Testing Code Generation Prompt")
    print("=" * 50)
    
    # Mock research context (like what would come from web research)
    research_content = """
    Apple Inc. Stock Performance:
    - Current stock price: $175.84 (as of December 2024)
    - 52-week high: $199.62, 52-week low: $164.08
    - Market cap: $2.7 trillion
    - Revenue growth: 2.8% year-over-year
    - P/E ratio: 28.5
    
    Microsoft Corp. Stock Performance:
    - Current stock price: $415.26 (as of December 2024)
    - 52-week high: $468.35, 52-week low: $362.90
    - Market cap: $3.1 trillion
    - Revenue growth: 15.7% year-over-year
    - P/E ratio: 34.2
    
    5-Year Historical Data:
    Apple: 2019: $293B market cap, 2024: $2.7T market cap
    Microsoft: 2019: $1.1T market cap, 2024: $3.1T market cap
    """
    
    research_topic = "Compare Apple and Microsoft stock performance over the last 5 years"
    analysis_type = "visualization"
    analysis_rationale = "Stock comparison data would benefit from charts showing price trends, market cap growth, and performance metrics"
    
    # Format the prompt
    formatted_prompt = code_generator_instructions.format(
        research_topic=research_topic,
        research_content=research_content,
        analysis_type=analysis_type,
        analysis_rationale=analysis_rationale,
    )
    
    print("📋 PROMPT BEING SENT TO AI:")
    print("-" * 30)
    print(formatted_prompt[:500] + "...")
    print("-" * 30)
    
    try:        # Generate code using the prompt
        completion = openai_client.chat.completions.create(
            model="gpt-4.1-mini",  # Using the model defined in configuration
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=0.1,
            max_tokens=1500,
        )
        
        generated_code = completion.choices[0].message.content.strip()
        
        print("\n🛠️  GENERATED CODE:")
        print("-" * 30)
        print(generated_code)
        print("-" * 30)
        
        # Validate the output
        print("\n🔍 VALIDATION:")
        
        # Check if it's actual Python code
        is_python = any(line.strip().startswith(('import ', 'from ', 'def ', 'class ', 'if ', 'for ', 'while ')) 
                       for line in generated_code.split('\n'))
        print(f"   Contains Python syntax: {'✅ YES' if is_python else '❌ NO'}")
        
        # Check if it's focused on the analysis type
        has_visualization = any(word in generated_code.lower() for word in ['plot', 'chart', 'graph', 'matplotlib', 'seaborn'])
        print(f"   Includes visualization code: {'✅ YES' if has_visualization else '❌ NO'}")
        
        # Check if it's self-contained
        has_imports = 'import' in generated_code
        print(f"   Has necessary imports: {'✅ YES' if has_imports else '❌ NO'}")
        
        # Check that it doesn't include explanations
        has_explanations = any(marker in generated_code for marker in ['```', '**', 'This code', 'The following'])
        print(f"   Free of explanatory text: {'✅ YES' if not has_explanations else '❌ NO'}")
        
        print("\n" + "=" * 50)
        print("✅ Code generation prompt test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_code_generation_prompt()
