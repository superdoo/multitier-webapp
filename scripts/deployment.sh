# #!/bin/bash
# set -e

# echo "🛠️  Using Minikube Docker daemon..."
# eval $(minikube -p minikube docker-env)

# echo "🐳 Building mt-backend image inside Minikube..."
# docker build -t mt-backend:latest -f ./helm/backend/mt-backend ./helm/backend

# echo "🐳 Building mt-frontend image inside Minikube..."
# docker build -t mt-frontend:latest ./helm/frontend

# echo "📦 Creating mt-* namespaces..."
# kubectl apply -f manifests/namespaces.yaml

# echo "⏭️  Skipping PostgreSQL deployment (already exists in 'postgres' namespace)."

echo "🚀 Installing mt-backend Helm chart..."
helm upgrade --install mt-backend ./helm/backend --namespace mt-backend

echo "🚀 Installing mt-frontend Helm chart..."
helm upgrade --install mt-frontend ./helm/frontend --namespace mt-frontend

echo "✅ Deployment complete!"
echo "🌐 Access mt-frontend via:"
echo "http://$(minikube ip):30080"
