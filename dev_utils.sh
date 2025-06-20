#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to show usage
show_usage() {
    echo -e "${BLUE}Development Utilities for Aerialytic${NC}"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  status     - Show status of development servers"
    echo "  kill-ports - Kill processes on ports 8001 and 5174"
    echo "  clean      - Clean up all development processes"
    echo "  restart    - Restart development environment"
    echo ""
}

# Function to check port status
check_port_status() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        local pid=$(lsof -ti :$port)
        echo -e "${GREEN}✓ $service is running on port $port (PID: $pid)${NC}"
    else
        echo -e "${RED}✗ $service is not running on port $port${NC}"
    fi
}

# Function to show status
show_status() {
    echo -e "${BLUE}Development Server Status:${NC}"
    echo ""
    check_port_status 8001 "Django Backend"
    check_port_status 5174 "React Frontend"
    echo ""
}

# Function to kill ports
kill_ports() {
    echo -e "${YELLOW}Killing processes on development ports...${NC}"
    
    # Kill Django port
    local django_pid=$(lsof -ti :8001)
    if [ ! -z "$django_pid" ]; then
        echo -e "${YELLOW}Killing Django process (PID: $django_pid)${NC}"
        kill -9 $django_pid 2>/dev/null
    fi
    
    # Kill React port
    local react_pid=$(lsof -ti :5174)
    if [ ! -z "$react_pid" ]; then
        echo -e "${YELLOW}Killing React process (PID: $react_pid)${NC}"
        kill -9 $react_pid 2>/dev/null
    fi
    
    sleep 2
    
    # Verify ports are free
    if ! lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null && ! lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${GREEN}✓ All development ports are now free${NC}"
    else
        echo -e "${RED}✗ Some ports are still in use${NC}"
        show_status
    fi
}

# Function to clean all development processes
clean_all() {
    echo -e "${YELLOW}Cleaning up all development processes...${NC}"
    
    # Kill any Python processes that might be Django
    pkill -f "manage.py runserver" 2>/dev/null
    
    # Kill any Node processes that might be React
    pkill -f "vite" 2>/dev/null
    
    # Kill specific ports
    kill_ports
    
    echo -e "${GREEN}✓ Cleanup completed${NC}"
}

# Function to restart development environment
restart_dev() {
    echo -e "${YELLOW}Restarting development environment...${NC}"
    
    # Clean up first
    clean_all
    
    # Wait a moment
    sleep 3
    
    # Start development servers
    echo -e "${GREEN}Starting development servers...${NC}"
    ./run_dev.sh
}

# Main script logic
case "${1:-}" in
    "status")
        show_status
        ;;
    "kill-ports")
        kill_ports
        ;;
    "clean")
        clean_all
        ;;
    "restart")
        restart_dev
        ;;
    *)
        show_usage
        ;;
esac 