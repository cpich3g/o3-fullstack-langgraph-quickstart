#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent.graph import _is_actual_python_code

# Test the validation function
test_cases = [
    ("import pandas as pd\ndf = pd.DataFrame({'a': [1,2,3]})", True),
    ("This is just text explaining concepts", False),
    ("# Just comments\n# More comments", False),
    ("", False),
    ("print('Hello world')\nx = 5 + 3", True)
]

print("Testing Python code validation:")
for code, expected in test_cases:
    result = _is_actual_python_code(code)
    status = "✅" if result == expected else "❌"
    print(f"{status} Expected: {expected}, Got: {result}")
    if len(code) > 50:
        print(f"   Code: {code[:50]}...")
    else:
        print(f"   Code: {repr(code)}")

print("\nFunction test completed!")
