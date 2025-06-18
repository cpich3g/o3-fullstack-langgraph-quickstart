#!/usr/bin/env python3
"""
Test script to generate a simple base64 visualization and verify frontend support.
"""

import base64
import matplotlib.pyplot as plt
import matplotlib
import io
import json

# Use non-interactive backend
matplotlib.use('Agg')

def create_sample_visualization():
    """Create a simple chart and convert to base64."""
    
    # Create sample data
    companies = ['Apple', 'Microsoft', 'Google', 'Amazon', 'Meta']
    market_caps = [3000, 2800, 1800, 1500, 800]  # in billions
    
    # Create a bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(companies, market_caps, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    
    # Customize the chart
    plt.title('Tech Companies Market Cap Comparison (2024)', fontsize=16, fontweight='bold')
    plt.ylabel('Market Cap (Billions USD)', fontsize=12)
    plt.xlabel('Company', fontsize=12)
    plt.xticks(rotation=45)
    
    # Add value labels on bars
    for bar, value in zip(bars, market_caps):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
                f'${value}B', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    
    # Convert to base64
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    
    img_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    plt.close()
    
    return img_base64

def create_sample_message():
    """Create a sample message structure that mimics the agent's response."""
    
    # Generate the visualization
    viz_base64 = create_sample_visualization()
    
    # Create the message structure
    message_content = """# Tech Giants Market Analysis

Based on the latest financial data, here's a comprehensive comparison of the top tech companies:

## Key Findings

- **Apple** leads with the highest market capitalization at $3 trillion
- **Microsoft** follows closely at $2.8 trillion  
- **Google (Alphabet)** holds $1.8 trillion in market value
- **Amazon** maintains $1.5 trillion despite recent challenges
- **Meta** has recovered to $800 billion after metaverse investments

## Market Insights

The visualization below illustrates the significant gap between the top two companies (Apple and Microsoft) and the rest of the tech sector. This demonstrates the duopoly these companies have established in terms of market value.

*Note: Data visualizations have been generated to illustrate key findings.*"""
    
    # Additional kwargs that would be sent by the backend
    additional_kwargs = {
        "sources": [
            {"label": "Yahoo Finance", "value": "https://finance.yahoo.com", "snippet": "Latest market data"},
            {"label": "Bloomberg", "value": "https://bloomberg.com", "snippet": "Tech company analysis"}
        ],
        "has_visualizations": True,
        "analysis_performed": True,
        "report_type": "user_friendly",
        "code_analysis_results": [
            {
                "type": "computational_analysis",
                "insights": "Market cap analysis reveals significant concentration in top tech companies",
                "results": "Generated comparative visualization of market capitalizations",
                "code_executed": "# Chart generation code (hidden from user)",
                "visualizations": [
                    {
                        "type": "image",
                        "format": "png", 
                        "base64_data": viz_base64,
                        "description": "Bar chart comparing market capitalizations of top 5 tech companies"
                    }
                ],
                "errors": "",
                "execution_method": "subprocess"
            }
        ]
    }
    
    return {
        "content": message_content,
        "additional_kwargs": additional_kwargs
    }

def save_sample_data():
    """Save sample data for frontend testing."""
    
    sample_message = create_sample_message()
    
    # Save to a JSON file
    with open('sample_message_with_viz.json', 'w') as f:
        json.dump(sample_message, f, indent=2)
    
    print("✅ Sample message with visualization saved to 'sample_message_with_viz.json'")
    print(f"📊 Visualization data size: {len(sample_message['additional_kwargs']['code_analysis_results'][0]['visualizations'][0]['base64_data'])} characters")
    print("🎯 You can use this data to test the frontend visualization display")
    
    # Also print a snippet for manual testing
    viz_data = sample_message['additional_kwargs']['code_analysis_results'][0]['visualizations'][0]['base64_data']
    print(f"\n📋 Sample base64 data (first 100 chars): {viz_data[:100]}...")

if __name__ == "__main__":
    print("🧪 Generating Sample Visualization Data")
    print("=" * 50)
    save_sample_data()
