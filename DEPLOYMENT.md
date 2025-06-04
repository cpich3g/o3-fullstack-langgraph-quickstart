# Quick Start Commands for Deep Research AI

## Local Development with Docker

### Prerequisites
- Docker Desktop installed and running
- Copy `.env.example` to `.env` and configure your Azure OpenAI settings

### Windows (PowerShell)
```powershell
# Copy environment template
Copy-Item .env.example .env

# Edit .env file with your Azure OpenAI credentials
notepad .env

# Deploy locally
.\deploy.ps1

# View logs
.\deploy.ps1 -Logs

# Stop services
.\deploy.ps1 -Stop

# Clean environment
.\deploy.ps1 -Clean
```

### Linux/macOS (Bash)
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your Azure OpenAI credentials
nano .env

# Make script executable
chmod +x deploy.sh

# Deploy locally
./deploy.sh
```

## Azure Deployment

### Option 1: Azure Container Instances (ACI) - Recommended for testing
```powershell
# Login to Azure
az login

# Create resource group
az group create --name deep-research-rg --location eastus

# Create container registry and deploy
.\azure-deploy.ps1 -ResourceGroup "deep-research-rg" -Location "eastus" -CreateRegistry -Deploy
```

### Option 2: Azure Container Apps (ACA) - Recommended for production
```powershell
# Create Azure Container Apps environment
az containerapp env create \
  --name deep-research-env \
  --resource-group deep-research-rg \
  --location eastus

# Deploy container app
az containerapp create \
  --name deep-research-app \
  --resource-group deep-research-rg \
  --environment deep-research-env \
  --image deepresearchaiacr.azurecr.io/deepresearchai:latest \
  --target-port 8000 \
  --ingress external \
  --env-vars AZURE_OPENAI_API_KEY=your_key AZURE_OPENAI_ENDPOINT=your_endpoint
```

## Service Endpoints

### Local Development
- **Application**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Azure Deployment
- **Application**: http://your-container-group.eastus.azurecontainer.io:8000
- **API Docs**: http://your-container-group.eastus.azurecontainer.io:8000/docs
- **Health Check**: http://your-container-group.eastus.azurecontainer.io:8000/health

## Environment Variables

Required variables in your `.env` file:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Search Engine Configuration
SEARCH_API_KEY=your_search_api_key_here
SEARCH_ENGINE_ID=your_search_engine_id_here

# Database Configuration (for local development)
POSTGRES_PASSWORD=your_secure_postgres_password_here
```

## Troubleshooting

### Check service status
```powershell
# Local
docker-compose -f docker-compose.production.yml ps

# Azure
az container show --resource-group deep-research-rg --name deep-research-ai
```

### View logs
```powershell
# Local
docker-compose -f docker-compose.production.yml logs -f

# Azure
az container logs --resource-group deep-research-rg --name deep-research-ai
```

### Restart services
```powershell
# Local
docker-compose -f docker-compose.production.yml restart

# Azure
az container restart --resource-group deep-research-rg --name deep-research-ai
```
