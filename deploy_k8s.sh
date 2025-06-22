#!/bin/bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

show_usage() {
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  deploy   - Build images, load to Minikube, and deploy all resources"
  echo "  undeploy - Delete all Kubernetes resources for this project"
  echo ""
}

if [[ -z "$1" ]]; then
  show_usage
  exit 1
fi

# Main script logic
case "${1}" in
    "deploy")
        echo -e "${YELLOW}Building backend image...${NC}"
        docker build -t aerialytic-backend:latest -f Dockerfile.backend .

        echo -e "${YELLOW}Building frontend image...${NC}"
        docker build -t aerialytic-frontend:latest -f frontend/Dockerfile.frontend.prod ./frontend

        echo -e "${YELLOW}Loading backend image into Minikube...${NC}"
        minikube image load aerialytic-backend:latest

        echo -e "${YELLOW}Loading frontend image into Minikube...${NC}"
        minikube image load aerialytic-frontend:latest

        echo -e "${YELLOW}Deploying PostgreSQL database...${NC}"
        kubectl apply -f k8s-db-deployment.yaml

        echo -e "${YELLOW}Waiting for PostgreSQL pod to be ready...${NC}"
        kubectl wait --for=condition=ready pod -l app=postgres --timeout=120s || true

        echo -e "${YELLOW}Deploying backend...${NC}"
        kubectl apply -f k8s-backend-deployment.yaml

        echo -e "${YELLOW}Deploying frontend...${NC}"
        kubectl apply -f k8s-frontend-deployment.yaml

        echo -e "${GREEN}All manifests applied. Current status:${NC}"
        kubectl get pods
        kubectl get services
        ;;
    "undeploy")
        echo -e "${YELLOW}Deleting frontend resources...${NC}"
        kubectl delete -f k8s-frontend-deployment.yaml || true
        echo -e "${YELLOW}Deleting backend resources...${NC}"
        kubectl delete -f k8s-backend-deployment.yaml || true
        echo -e "${YELLOW}Deleting database resources...${NC}"
        kubectl delete -f k8s-db-deployment.yaml || true
        echo -e "${GREEN}All Kubernetes resources for this project have been deleted.${NC}"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac 