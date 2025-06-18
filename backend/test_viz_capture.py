#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from agent.graph import _execute_python_code

# Test visualization capture
test_code = """import matplotlib.pyplot as plt

# Create simple pie chart
labels = ['Apple', 'Samsung', 'Xiaomi', 'OnePlus', 'Google']
sizes = [25, 23, 19, 17, 16]
colors = ['#FF9999', '#66B3FF', '#99FF99', '#FFCC99', '#C2C2F0']

plt.figure(figsize=(8, 6))
plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
plt.title('Test Pie Chart')
plt.show()

print('Chart created successfully')"""

print('Testing visualization capture...')
result = _execute_python_code(test_code)
print('Execution success:', result.get('success'))
print('Visualizations found:', len(result.get('visualizations', [])))
print('Output:', result.get('output'))
if result.get('error'):
    print('Error:', result.get('error'))

if result.get('visualizations'):
    print('Visualization data length:', len(result['visualizations'][0].get('base64_data', '')))
    print('First visualization type:', result['visualizations'][0].get('type'))
