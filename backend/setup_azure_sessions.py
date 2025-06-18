#!/usr/bin/env python3
"""
Azure Container Apps Dynamic Sessions Setup Helper

This script helps validate and configure Azure Container Apps dynamic sessions
for the enhanced LangGraph agent.
"""

import os
import subprocess
import sys
from pathlib import Path

def check_azure_cli():
    """Check if Azure CLI is installed and user is authenticated."""
    try:
        result = subprocess.run(['az', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Azure CLI not found. Please install Azure CLI:")
            print("   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
            return False
        
        print("✅ Azure CLI found")
        
        # Check if user is authenticated
        result = subprocess.run(['az', 'account', 'show'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Not authenticated with Azure. Please run: az login")
            return False
        
        print("✅ Azure authentication verified")
        return True
        
    except FileNotFoundError:
        print("❌ Azure CLI not found. Please install Azure CLI:")
        print("   https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        return False

def check_container_apps_extension():
    """Check if Azure Container Apps extension is installed."""
    try:
        result = subprocess.run(['az', 'extension', 'list'], capture_output=True, text=True)
        if 'containerapp' not in result.stdout:
            print("⚠️  Azure Container Apps extension not found. Installing...")
            install_result = subprocess.run(['az', 'extension', 'add', '--name', 'containerapp'], 
                                          capture_output=True, text=True)
            if install_result.returncode == 0:
                print("✅ Azure Container Apps extension installed")
                return True
            else:
                print(f"❌ Failed to install Container Apps extension: {install_result.stderr}")
                return False
        else:
            print("✅ Azure Container Apps extension found")
            return True
            
    except Exception as e:
        print(f"❌ Error checking Container Apps extension: {e}")
        return False

def check_session_pools():
    """List available session pools."""
    try:
        result = subprocess.run(['az', 'containerapp', 'sessionpool', 'list'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip() == '[]':
                print("⚠️  No session pools found. You need to create one:")
                print("   Follow: https://docs.microsoft.com/en-us/azure/container-apps/sessions")
                print("   Or use Azure Portal to create a Container Apps session pool")
                return False
            else:
                print("✅ Session pools found:")
                import json
                try:
                    pools = json.loads(result.stdout)
                    for pool in pools:
                        name = pool.get('name', 'Unknown')
                        resource_group = pool.get('resourceGroup', 'Unknown')
                        print(f"   - {name} (Resource Group: {resource_group})")
                except:
                    print("   (Could not parse pool details)")
                return True
        else:
            print(f"⚠️  Could not list session pools: {result.stderr}")
            print("   You may need to create a session pool first")
            return False
            
    except Exception as e:
        print(f"❌ Error checking session pools: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set."""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_API_VERSION"
    ]
    
    optional_vars = [
        "AZURE_POOL_MANAGEMENT_ENDPOINT"
    ]
    
    print("\n🔧 Environment Variables Check:")
    print("-" * 40)
    
    all_required_set = True
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var}: Set")
        else:
            print(f"❌ {var}: Not set")
            all_required_set = False
    
    for var in optional_vars:
        if os.getenv(var):
            endpoint = os.getenv(var)
            print(f"✅ {var}: {endpoint[:50]}...")
        else:
            print(f"⚠️  {var}: Not set (will use subprocess fallback)")
    
    return all_required_set

def generate_env_file():
    """Generate a .env file template."""
    env_file = Path(".env")
    template_file = Path(".env.template")
    
    if env_file.exists():
        print(f"\n📄 .env file already exists at: {env_file.absolute()}")
        return
    
    if template_file.exists():
        print(f"\n📄 Copying .env.template to .env...")
        with open(template_file, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print(f"✅ Created .env file at: {env_file.absolute()}")
        print("   Please edit the .env file and add your configuration values")
    else:
        print(f"\n📄 Creating basic .env file...")
        content = """# Azure OpenAI Configuration (Required)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-azure-openai-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-12-01-preview

# Azure Container Apps Dynamic Sessions (Optional but Recommended)
AZURE_POOL_MANAGEMENT_ENDPOINT=your_azure_container_apps_sessions_endpoint_here
"""
        with open(env_file, 'w') as f:
            f.write(content)
        print(f"✅ Created .env file at: {env_file.absolute()}")
        print("   Please edit the .env file and add your configuration values")

def main():
    """Main setup validation function."""
    print("🚀 Azure Container Apps Dynamic Sessions Setup Helper")
    print("=" * 60)
    
    # Check Azure CLI
    if not check_azure_cli():
        print("\n❌ Setup incomplete. Please install and configure Azure CLI first.")
        return False
    
    # Check Container Apps extension
    if not check_container_apps_extension():
        print("\n❌ Setup incomplete. Could not install Container Apps extension.")
        return False
    
    # Check session pools
    has_pools = check_session_pools()
    
    # Check environment variables
    has_env_vars = check_environment_variables()
    
    # Generate .env file if needed
    generate_env_file()
    
    print("\n📋 Setup Summary:")
    print("-" * 20)
    print(f"Azure CLI: ✅")
    print(f"Container Apps Extension: ✅")
    print(f"Session Pools: {'✅' if has_pools else '⚠️'}")
    print(f"Environment Variables: {'✅' if has_env_vars else '❌'}")
    
    if has_pools and has_env_vars:
        print("\n🎉 Setup complete! You can now use Azure Container Apps dynamic sessions.")
        print("\nNext steps:")
        print("1. Update your .env file with the correct values")
        print("2. Set AZURE_POOL_MANAGEMENT_ENDPOINT to your session pool endpoint")
        print("3. Run the test: python test_enhanced_agent.py")
    elif has_env_vars:
        print("\n⚠️  Setup partially complete. You need to create session pools.")
        print("\nNext steps:")
        print("1. Create a Container Apps session pool in Azure Portal")
        print("2. Update AZURE_POOL_MANAGEMENT_ENDPOINT in your .env file")
        print("3. Run this script again to verify")
    else:
        print("\n❌ Setup incomplete. Please configure environment variables.")
        print("\nNext steps:")
        print("1. Update your .env file with Azure OpenAI credentials")
        print("2. Create a Container Apps session pool (optional)")
        print("3. Run this script again to verify")
    
    return has_pools and has_env_vars

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
