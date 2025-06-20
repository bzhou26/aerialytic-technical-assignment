#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_usage() {
  echo "Usage: $0 [deploy|undeploy]"
  echo "  deploy   - Build images, load to Minikube, and deploy all resources (default)"
  echo "  undeploy - Delete all Kubernetes resources for this project"
}

if [[ "$1" == "undeploy" ]]; then
  echo -e "${YELLOW}Deleting frontend resources...${NC}"
  kubectl delete -f k8s-frontend-deployment.yaml || true
  echo -e "${YELLOW}Deleting backend resources...${NC}"
  kubectl delete -f k8s-backend-deployment.yaml || true
  echo -e "${YELLOW}Deleting database resources...${NC}"
  kubectl delete -f k8s-db-deployment.yaml || true
  echo -e "${GREEN}All Kubernetes resources for this project have been deleted.${NC}"
  exit 0
elif [[ -n "$1" && "$1" != "deploy" ]]; then
  show_usage
  exit 1
fi

# Build backend image
echo -e "${YELLOW}Building backend image...${NC}"
docker build -t aerialytic-backend:latest -f Dockerfile.backend .

# Build frontend image
echo -e "${YELLOW}Building frontend image...${NC}"
docker build -t aerialytic-frontend:latest -f frontend/Dockerfile.frontend ./frontend

# Load images into Minikube
echo -e "${YELLOW}Loading backend image into Minikube...${NC}"
minikube image load aerialytic-backend:latest

echo -e "${YELLOW}Loading frontend image into Minikube...${NC}"
minikube image load aerialytic-frontend:latest

# Deploy PostgreSQL database
echo -e "${YELLOW}Deploying PostgreSQL database...${NC}"
kubectl apply -f k8s-db-deployment.yaml

# Wait for PostgreSQL pod to be ready
echo -e "${YELLOW}Waiting for PostgreSQL pod to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s || true

# Deploy backend
echo -e "${YELLOW}Deploying backend...${NC}"
kubectl apply -f k8s-backend-deployment.yaml

# Deploy frontend
echo -e "${YELLOW}Deploying frontend...${NC}"
kubectl apply -f k8s-frontend-deployment.yaml

# Show status
echo -e "${GREEN}All manifests applied. Current status:${NC}"
kubectl get pods
kubectl get services 