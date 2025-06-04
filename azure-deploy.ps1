# Deep Research AI - Azure Container Instance Deployment

# Azure Container Instances (ACI) - Simple deployment
# This script deploys the application to Azure Container Instances

param(
    [Parameter(Mandatory=$true)]
    [string]$ResourceGroup,
    
    [Parameter(Mandatory=$true)]
    [string]$Location = "eastus",
    
    [Parameter(Mandatory=$true)]
    [string]$ContainerGroupName = "deep-research-ai",
    
    [string]$ImageName = "deepresearchai",
    
    [string]$RegistryName = "",
    
    [switch]$CreateRegistry,
    
    [switch]$Deploy
)

Write-Host "🚀 Azure Container Instance Deployment for Deep Research AI" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green

# Function to create Azure Container Registry
function New-ContainerRegistry {
    param($rgName, $location, $registryName)
    
    Write-Host "📦 Creating Azure Container Registry: $registryName" -ForegroundColor Cyan
    
    az acr create `
        --resource-group $rgName `
        --name $registryName `
        --sku Standard `
        --location $location `
        --admin-enabled true
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Container Registry created successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to create Container Registry" -ForegroundColor Red
        exit 1
    }
}

# Function to build and push Docker image
function Build-AndPushImage {
    param($registryName, $imageName)
    
    Write-Host "🔨 Building and pushing Docker image..." -ForegroundColor Cyan
    
    # Login to ACR
    az acr login --name $registryName
    
    # Build and push image
    $fullImageName = "$registryName.azurecr.io/$imageName:latest"
    
    docker build -f Dockerfile.production -t $fullImageName .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker image built successfully" -ForegroundColor Green
    } else {
        Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
        exit 1
    }
    
    docker push $fullImageName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker image pushed successfully" -ForegroundColor Green
        return $fullImageName
    } else {
        Write-Host "❌ Failed to push Docker image" -ForegroundColor Red
        exit 1
    }
}

# Function to deploy to Azure Container Instances
function Deploy-ToACI {
    param($rgName, $location, $containerGroupName, $fullImageName, $registryName)
    
    Write-Host "🚀 Deploying to Azure Container Instances..." -ForegroundColor Cyan
    
    # Get ACR credentials
    $acrUsername = az acr credential show --name $registryName --query username --output tsv
    $acrPassword = az acr credential show --name $registryName --query passwords[0].value --output tsv
    
    # Check if .env file exists for environment variables
    $envVars = @()
    if (Test-Path ".env") {
        $envContent = Get-Content ".env" | Where-Object { $_ -notmatch '^#' -and $_ -match '=' }
        foreach ($line in $envContent) {
            if ($line -match '([^=]+)=(.*)') {
                $key = $matches[1].Trim()
                $value = $matches[2].Trim()
                # Only add Azure and app-specific variables, not local database URLs
                if ($key -match "AZURE_|SEARCH_|LOG_LEVEL|CORS_") {
                    $envVars += "$key=$value"
                }
            }
        }
    }
    
    # Create container group with environment variables
    $envVarArgs = ""
    if ($envVars.Count -gt 0) {
        $envVarArgs = "--environment-variables " + ($envVars -join " ")
    }
    
    $deployCommand = @"
az container create \
    --resource-group $rgName \
    --name $containerGroupName \
    --image $fullImageName \
    --registry-login-server $registryName.azurecr.io \
    --registry-username $acrUsername \
    --registry-password $acrPassword \
    --cpu 2 \
    --memory 4 \
    --ports 8000 \
    --dns-name-label $containerGroupName \
    --location $location \
    $envVarArgs
"@
    
    Invoke-Expression $deployCommand
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Container deployed successfully" -ForegroundColor Green
        
        # Get the FQDN
        $fqdn = az container show --resource-group $rgName --name $containerGroupName --query ipAddress.fqdn --output tsv
        
        Write-Host ""
        Write-Host "🎉 Deployment completed!" -ForegroundColor Green
        Write-Host "📋 Container Information:" -ForegroundColor Cyan
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "🌐 Application URL:    http://$fqdn:8000" -ForegroundColor White
        Write-Host "🔍 API Documentation:  http://$fqdn:8000/docs" -ForegroundColor White
        Write-Host "📊 Health Check:       http://$fqdn:8000/health" -ForegroundColor White
        Write-Host "🏗️  Resource Group:     $rgName" -ForegroundColor White
        Write-Host "📦 Container Group:    $containerGroupName" -ForegroundColor White
        Write-Host ""
        Write-Host "🔧 Management Commands:" -ForegroundColor Cyan
        Write-Host "  View logs:     az container logs --resource-group $rgName --name $containerGroupName" -ForegroundColor White
        Write-Host "  Stop:          az container stop --resource-group $rgName --name $containerGroupName" -ForegroundColor White
        Write-Host "  Start:         az container start --resource-group $rgName --name $containerGroupName" -ForegroundColor White
        Write-Host "  Delete:        az container delete --resource-group $rgName --name $containerGroupName" -ForegroundColor White
        
    } else {
        Write-Host "❌ Failed to deploy container" -ForegroundColor Red
        exit 1
    }
}

# Main execution
try {
    # Validate prerequisites
    Write-Host "🔍 Checking prerequisites..." -ForegroundColor Cyan
    
    # Check if Azure CLI is installed
    $azVersion = az version 2>$null
    if (-not $azVersion) {
        Write-Host "❌ Azure CLI is not installed. Please install it first." -ForegroundColor Red
        Write-Host "   Download from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli" -ForegroundColor Yellow
        exit 1
    }
    
    # Check if Docker is running
    $dockerVersion = docker version 2>$null
    if (-not $dockerVersion) {
        Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
    
    # Check if logged in to Azure
    $azAccount = az account show 2>$null
    if (-not $azAccount) {
        Write-Host "❌ Not logged in to Azure. Please run 'az login' first." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Prerequisites validated" -ForegroundColor Green
    
    # Set default registry name if not provided
    if (-not $RegistryName) {
        $RegistryName = $ContainerGroupName.Replace("-", "") + "acr"
    }
    
    # Create ACR if requested
    if ($CreateRegistry) {
        New-ContainerRegistry -rgName $ResourceGroup -location $Location -registryName $RegistryName
    }
    
    # Build and push image
    $fullImageName = Build-AndPushImage -registryName $RegistryName -imageName $ImageName
    
    # Deploy to ACI if requested
    if ($Deploy) {
        Deploy-ToACI -rgName $ResourceGroup -location $Location -containerGroupName $ContainerGroupName -fullImageName $fullImageName -registryName $RegistryName
    }
    
    Write-Host ""
    Write-Host "🎉 Azure deployment process completed!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Deployment failed: $_" -ForegroundColor Red
    exit 1
}
