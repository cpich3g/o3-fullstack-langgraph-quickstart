#!/usr/bin/env python3
"""
Test script to verify that only one final message is created (no duplicates).
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent.app import agent


async def test_single_message():
    """Test that only one final message is created, not duplicates."""
    
    print("🧪 Testing Single Message Output")
    print("=" * 50)
    
    # Simple test query that shouldn't need code analysis
    test_query = "What are the current trends in renewable energy adoption globally?"
    
    print(f"🔍 Research Query: {test_query}")
    print("\n" + "=" * 50)
    
    config = {
        "configurable": {
            "use_azure_ai_search": True,
            "enable_code_interpreter": True,
            "web_search_tool": "tavily",
            "user_id": "test_user",
            "thread_id": "test_single_msg"
        }
    }
    
    try:
        # Run the agent
        messages_input = [{"role": "user", "content": test_query}]
        
        print("🚀 Starting research agent...")
        
        message_count = 0
        final_state = None
        
        async for chunk in agent.astream({"messages": messages_input}, config=config):
            node_name = list(chunk.keys())[0]
            node_data = chunk[node_name]
            
            # Count messages being created
            if "messages" in node_data and node_data["messages"]:
                message_count += len(node_data["messages"])
                print(f"📝 {node_name} created {len(node_data['messages'])} message(s)")
                
                # Show message details
                for i, msg in enumerate(node_data["messages"]):
                    content_length = len(msg.content) if hasattr(msg, 'content') else 0
                    print(f"   Message {i+1}: {content_length} characters")
                    
                final_state = node_data
            
            # Track routing decisions
            if node_name == "finalize_answer":
                code_needed = node_data.get("code_analysis_needed", False)
                print(f"📊 finalize_answer: Code needed = {'✅' if code_needed else '❌'}")
                
        print(f"\n📊 SUMMARY:")
        print(f"   Total messages created: {message_count}")
        
        if message_count == 1:
            print("   ✅ SUCCESS: Only one final message created!")
        elif message_count > 1:
            print(f"   ❌ WARNING: {message_count} messages created (expected 1)")
        else:
            print("   ❌ ERROR: No messages created")
            
        # Verify final state
        if final_state and final_state.get("messages"):
            final_msg = final_state["messages"][0]
            additional_kwargs = getattr(final_msg, 'additional_kwargs', {})
            
            print(f"\n🔍 FINAL MESSAGE ANALYSIS:")
            print(f"   Content length: {len(final_msg.content)} characters")
            print(f"   Has metadata: {'✅' if additional_kwargs else '❌'}")
            
            if additional_kwargs:
                print(f"   Sources: {len(additional_kwargs.get('sources', []))}")
                print(f"   Has visualizations: {additional_kwargs.get('has_visualizations', False)}")
                print(f"   Analysis performed: {additional_kwargs.get('analysis_performed', False)}")
                
        print("\n" + "=" * 50)
        print("✅ Single message test completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_single_message())
