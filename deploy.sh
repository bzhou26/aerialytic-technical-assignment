#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Aerialytic Docker Deployment${NC}"
echo ""

# Function to show usage
show_usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  dev       - Start development environment"
    echo "  down      - Stop all containers"
    echo "  logs      - Show logs"
    echo "  clean     - Clean up containers and volumes"
    echo "  db-reset  - Reset database (WARNING: This will delete all data)"
    echo ""
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}Docker is not running. Please start Docker and try again.${NC}"
        exit 1
    fi
}

# Function to start development environment
start_dev() {
    echo -e "${GREEN}Building images without cache for development...${NC}"
    docker compose -f docker-compose.yml -f docker-compose.override.yml build --no-cache
    echo -e "${GREEN}Starting development environment...${NC}"
    docker compose -f docker-compose.yml -f docker-compose.override.yml up --build
}

# Function to show logs
show_logs() {
    echo -e "${GREEN}Showing logs...${NC}"
    docker compose logs -f
}

# Function to clean up
clean_up() {
    echo -e "${YELLOW}Cleaning up containers and volumes...${NC}"
    docker compose down -v --remove-orphans
    docker system prune -f
}

# Function to reset database
reset_database() {
    echo -e "${RED}WARNING: This will delete all database data!${NC}"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Resetting database...${NC}"
        docker compose down -v
        docker volume rm aerialytic-technical-assignment_postgres_data 2>/dev/null || true
        echo -e "${GREEN}Database reset complete.${NC}"
    else
        echo -e "${YELLOW}Database reset cancelled.${NC}"
    fi
}

# Function to stop containers
stop_containers() {
    echo -e "${YELLOW}Stopping all containers...${NC}"
    docker compose down
}

# Check Docker
check_docker

# Main script logic
case "${1:-}" in
    "dev")
        start_dev
        ;;
    "down")
        stop_containers
        ;;
    "logs")
        show_logs
        ;;
    "clean")
        clean_up
        ;;
    "db-reset")
        reset_database
        ;;
    *)
        show_usage
        ;;
esac 