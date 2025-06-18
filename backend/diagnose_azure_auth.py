#!/usr/bin/env python3
"""
Quick Diagnostic Script for Azure Container Apps Dynamic Sessions

This script helps identify and fix common authentication issues.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def diagnose_authentication_issue():
    """Diagnose the specific authentication issue you're experiencing."""
    
    print("🔍 Diagnosing Azure Container Apps Sessions Authentication Issue")
    print("=" * 65)
    
    # Check endpoint configuration
    endpoint = os.getenv("AZURE_POOL_MANAGEMENT_ENDPOINT")
    if not endpoint:
        print("❌ AZURE_POOL_MANAGEMENT_ENDPOINT is not set")
        print("   Please set this environment variable to your sessions endpoint")
        return False
    
    print(f"✅ Endpoint configured: {endpoint[:50]}...")
    
    # Check if this is a public endpoint
    no_auth = os.getenv("AZURE_SESSIONS_NO_AUTH", "").lower() in ['true', '1', 'yes']
    print(f"   No-auth mode: {'✅ Enabled' if no_auth else '❌ Disabled'}")
    
    # If you mentioned it's public, suggest the fix
    print("\n💡 Based on your feedback that the endpoint is public:")
    print("   You should set AZURE_SESSIONS_NO_AUTH=true")
    print()
    print("   Add this to your .env file:")
    print("   AZURE_SESSIONS_NO_AUTH=true")
    print()
    print("   Or set environment variable:")
    print("   export AZURE_SESSIONS_NO_AUTH=true")
    
    # Test the current configuration
    print("\n🧪 Testing Current Configuration:")
    print("-" * 40)
    
    try:
        from langchain_azure_dynamic_sessions import SessionsPythonREPLTool
        
        print("   Creating tool with current settings...")
        tool = SessionsPythonREPLTool(pool_management_endpoint=endpoint)
        
        print("   Testing simple execution...")
        result = tool.execute("2 + 2")
        
        print(f"✅ Success! Result: {result}")
        print("\n🎉 Azure Container Apps sessions are now working!")
        return True
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Still failing: {error_msg[:100]}...")
        
        if "DefaultAzureCredential" in error_msg:
            print("\n🔧 Authentication Issue Persists:")
            print("   The endpoint may still be trying to authenticate")
            print("   This could be a configuration issue with the SessionsPythonREPLTool")
            print()
            print("   Recommended actions:")
            print("   1. Verify the endpoint is truly public and accessible")
            print("   2. Check if there are any authentication headers required")
            print("   3. Contact the endpoint administrator for configuration details")
            print("   4. Use subprocess fallback for now (automatic in the agent)")
        
        return False

def show_fallback_info():
    """Show information about the automatic fallback."""
    print("\n🔄 Automatic Fallback Information:")
    print("-" * 35)
    print("✅ The enhanced LangGraph agent will automatically:")
    print("   1. Try Azure Container Apps sessions first")
    print("   2. Fall back to secure subprocess execution if Azure fails")
    print("   3. Continue processing without interruption")
    print()
    print("📊 Both methods provide:")
    print("   • Code execution with pandas, numpy, matplotlib")
    print("   • Data analysis and visualization capabilities") 
    print("   • Error handling and safety checks")
    print()
    print("🛡️ Subprocess fallback is secure and functional")
    print("   (Azure sessions provide additional isolation when available)")

def main():
    """Main diagnostic function."""
    success = diagnose_authentication_issue()
    show_fallback_info()
    
    print("\n📋 Summary:")
    print("-" * 12)
    
    if success:
        print("🎉 Azure Container Apps sessions are working!")
        print("   Your enhanced agent will use Azure sessions for optimal performance")
    else:
        print("⚠️  Azure sessions authentication issue persists")
        print("   Your enhanced agent will use subprocess fallback (still fully functional)")
        print("   Consider setting AZURE_SESSIONS_NO_AUTH=true if endpoint is public")
    
    print("\n🚀 Next Steps:")
    print("   • Run: python test_enhanced_agent.py")
    print("   • The agent will work regardless of Azure sessions status")
    print("   • Enjoy the enhanced research capabilities!")

if __name__ == "__main__":
    main()
