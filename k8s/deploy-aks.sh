#!/bin/bash
set -e

# Usage: ./deploy-aks.sh <resource-group> <acr-name> <aks-name>
# Requires: Azure CLI and kubectl configured

RG=$1
ACR_NAME=$2
AKS_NAME=$3
IMAGE_NAME=deepresearchai

if [ -z "$RG" ] || [ -z "$ACR_NAME" ] || [ -z "$AKS_NAME" ]; then
  echo "Usage: $0 <resource-group> <acr-name> <aks-name>"
  exit 1
fi

# Build and push the Docker image
FULL_IMAGE="$ACR_NAME.azurecr.io/$IMAGE_NAME:latest"

echo "Building Docker image $FULL_IMAGE"
docker build -f Dockerfile.production -t $FULL_IMAGE .
echo "Pushing image to ACR"
docker push $FULL_IMAGE

# Ensure kubectl is connected to the cluster
az aks get-credentials -g $RG -n $AKS_NAME --overwrite-existing

# Create Kubernetes secret from .env file
if [ -f .env ]; then
  echo "Creating Kubernetes secret from .env"
  kubectl delete secret deep-research-secret --ignore-not-found
  kubectl create secret generic deep-research-secret --from-env-file=.env
else
  echo "No .env file found. Please create one before deploying."
  exit 1
fi

# Update image name in app deployment
sed "s/<ACR_NAME>/$ACR_NAME/g" k8s/app.yaml | kubectl apply -f -

# Apply remaining manifests
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/postgres.yaml

echo "Deployment complete. Use 'kubectl get svc deep-research-app' to find the external IP."
