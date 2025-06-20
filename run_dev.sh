#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting Aerialytic Development Environment...${NC}"
echo -e "${YELLOW}This will start both Django backend and React frontend${NC}"
echo ""

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${RED}Port $port is already in use!${NC}"
        echo -e "${YELLOW}Attempting to kill process on port $port...${NC}"
        local pid=$(lsof -ti :$port)
        if [ ! -z "$pid" ]; then
            kill -9 $pid 2>/dev/null
            sleep 2
            if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
                echo -e "${RED}Failed to free port $port. Please manually stop the process using:${NC}"
                echo -e "${YELLOW}sudo lsof -ti :$port | xargs kill -9${NC}"
                return 1
            else
                echo -e "${GREEN}Successfully freed port $port${NC}"
            fi
        fi
    fi
    return 0
}

# Check and free ports if needed
echo -e "${GREEN}Checking for port conflicts...${NC}"
if ! check_port 8001; then
    exit 1
fi
if ! check_port 5174; then
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install Django dependencies if not already installed
echo -e "${GREEN}Installing Django dependencies...${NC}"
pip install -r requirements.txt

# Install frontend dependencies if not already installed
echo -e "${GREEN}Installing frontend dependencies...${NC}"
cd frontend
npm install
cd ..

# Function to cleanup on exit
cleanup() {
    echo -e "\n${RED}Shutting down servers...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}Starting Django server on http://192.168.1.102:8001${NC}"
echo -e "${GREEN}Starting React frontend on http://192.168.1.102:5174${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Start Django server in background
python manage.py runserver 0.0.0.0:8001 &
DJANGO_PID=$!

# Start React frontend in background (accessible from network)
cd frontend
npm run dev -- --host 0.0.0.0 --port 5174 &
FRONTEND_PID=$!
cd ..

# Wait for both processes
wait $DJANGO_PID $FRONTEND_PID 