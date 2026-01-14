#!/bin/bash

# Start script for Feedly - starts both backend and frontend services

set -e

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to cleanup on exit
cleanup() {
    echo -e "\n${RED}Shutting down services...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit
}

# Trap Ctrl+C
trap cleanup INT TERM

# Check if venv exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Virtual environment not found. Please run: python -m venv venv${NC}"
    exit 1
fi

# Check if backend requirements are installed
if ! venv/bin/python -c "import fastapi" 2>/dev/null; then
    echo -e "${RED}Error: Backend dependencies not installed. Please run: pip install -r backend/requirements.txt${NC}"
    exit 1
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}Error: Frontend dependencies not installed. Please run: cd frontend && npm install${NC}"
    exit 1
fi

# Start backend
echo -e "${BLUE}Starting backend server...${NC}"
cd backend
source ../venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo -e "${BLUE}Starting frontend server...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo -e "${GREEN}✓ Services started!${NC}"
echo -e "${GREEN}Backend API: http://localhost:8000${NC}"
echo -e "${GREEN}Frontend App: http://localhost:3000${NC}"
echo -e "\nPress Ctrl+C to stop all services"

# Wait for both processes
wait
