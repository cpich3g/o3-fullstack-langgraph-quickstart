# Kubernetes Deployment for Deep Research AI

This folder contains manifests and a helper script to deploy the application to **Azure Kubernetes Service (AKS)**. The setup mirrors the `docker-compose.production.yml` configuration.

## Files

- `redis.yaml` – Deployment and Service for Redis.
- `postgres.yaml` – Persistent volume claim, Deployment and Service for PostgreSQL.
- `configmap.yaml` – Non‑secret environment variables used by the application.
- `secret-template.yaml` – Example of the Kubernetes secret. The deployment script automatically creates a secret from your local `.env` file.
- `app.yaml` – Deployment and LoadBalancer Service for the main application. Replace `<ACR_NAME>` with your Azure Container Registry name.
- `deploy-aks.sh` – Convenience script that builds the Docker image, pushes it to ACR and applies all manifests to your AKS cluster.

## Usage

1. Create a `.env` file at the project root with the required values (see `.env.example`).
2. Authenticate with Azure and ensure you have an AKS cluster and ACR.
3. Run the deploy script:

```bash
# Install NGINX Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml
```


```bash
./k8s/deploy-aks.sh <resource-group> <acr-name> <aks-name>
```

After deployment, retrieve the external IP:

```bash
kubectl get svc deep-research-app
```

Open `http://<EXTERNAL-IP>:8000/app/` in your browser.
