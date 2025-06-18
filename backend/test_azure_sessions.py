#!/usr/bin/env python3
"""
Azure Container Apps Dynamic Sessions Connection Test

This script tests the connection to Azure Container Apps dynamic sessions
and helps debug authentication issues.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_azure_sessions_direct():
    """Test Azure Container Apps dynamic sessions directly."""
    
    try:
        from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
    except ImportError:
        print("❌ langchain-azure-dynamic-sessions not installed")
        print("   Install with: pip install langchain-azure-dynamic-sessions")
        return False
    
    endpoint = os.getenv("AZURE_POOL_MANAGEMENT_ENDPOINT")
    if not endpoint:
        print("❌ AZURE_POOL_MANAGEMENT_ENDPOINT not set")
        print("   Please set this environment variable to your Azure Container Apps sessions endpoint")
        return False
    
    print(f"🔗 Testing connection to: {endpoint}")
    
    try:
        # Try to create the tool
        print("   Creating SessionsPythonREPLTool...")
        tool = SessionsPythonREPLTool(pool_management_endpoint=endpoint)
        print("   ✅ Tool created successfully")
        
        # Try a simple execution
        print("   Testing simple code execution...")
        result = tool.execute("print('Hello from Azure Container Apps!')")
        print("   ✅ Code execution successful")
        
        print(f"   Result: {result}")
        
        # Try a more complex execution with data analysis
        print("   Testing data analysis code...")
        analysis_code = """
import pandas as pd
import numpy as np

# Create sample data
data = {'values': [1, 2, 3, 4, 5], 'squared': [1, 4, 9, 16, 25]}
df = pd.DataFrame(data)

# Calculate mean
mean_value = df['values'].mean()
print(f"Mean value: {mean_value}")

# Return result
mean_value
"""
        result = tool.execute(analysis_code)
        print("   ✅ Data analysis execution successful")
        print(f"   Result: {result}")
        
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Connection failed: {error_msg}")
        
        # Provide specific guidance based on error type
        if "DefaultAzureCredential" in error_msg:
            print("\n🔧 Authentication Issue Detected:")
            print("   This error suggests Azure authentication is required")
            print("   For public endpoints that don't require auth, this might be a configuration issue")
            print("\n   Try these solutions:")
            print("   1. Set AZURE_SESSIONS_NO_AUTH=true in your .env file")
            print("   2. If authentication is required, run: az login")
            print("   3. Verify your endpoint URL is correct")
            
        elif "endpoint" in error_msg.lower():
            print("\n🔧 Endpoint Issue Detected:")
            print("   Please verify your AZURE_POOL_MANAGEMENT_ENDPOINT is correct")
            print("   It should look like: https://your-sessions-endpoint.region.azurecontainerapps.io")
            
        elif "timeout" in error_msg.lower():
            print("\n🔧 Network Issue Detected:")
            print("   The endpoint might be unreachable or slow to respond")
            print("   Check your network connection and endpoint availability")
            
        else:
            print(f"\n🔧 General Error:")
            print(f"   {error_msg}")
            print("   Check the Azure Container Apps sessions documentation")
        
        return False

def test_fallback_execution():
    """Test the fallback subprocess execution method."""
    print("\n🔄 Testing Fallback Subprocess Execution:")
    print("-" * 50)
    
    try:
        import tempfile
        import subprocess
        
        # Simple test code
        test_code = """
import pandas as pd
import numpy as np

# Simple calculation
result = 2 + 2
print(f"Test calculation: {result}")
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name
        
        # Execute
        result = subprocess.run([sys.executable, temp_file], 
                              capture_output=True, text=True, timeout=10)
        
        # Clean up
        os.unlink(temp_file)
        
        if result.returncode == 0:
            print("✅ Subprocess execution successful")
            print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Subprocess execution failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Subprocess test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Azure Container Apps Dynamic Sessions Connection Test")
    print("=" * 60)
    
    # Test Azure sessions
    azure_success = test_azure_sessions_direct()
    
    # Test fallback
    fallback_success = test_fallback_execution()
    
    print("\n📋 Test Summary:")
    print("-" * 20)
    print(f"Azure Container Apps Sessions: {'✅ Working' if azure_success else '❌ Failed'}")
    print(f"Subprocess Fallback: {'✅ Working' if fallback_success else '❌ Failed'}")
    
    if azure_success:
        print("\n🎉 Azure Container Apps dynamic sessions are working correctly!")
        print("   Your enhanced LangGraph agent will use Azure sessions for code execution.")
    elif fallback_success:
        print("\n⚠️  Azure sessions failed, but fallback is working.")
        print("   Your enhanced LangGraph agent will use subprocess execution.")
        print("   Consider fixing the Azure sessions connection for better security and features.")
    else:
        print("\n❌ Both Azure sessions and fallback failed.")
        print("   Please check your configuration and dependencies.")
    
    return azure_success or fallback_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
