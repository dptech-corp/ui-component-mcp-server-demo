#!/bin/bash


echo "Starting UI Component Backend Server..."

if ! command -v poetry &> /dev/null; then
    echo "Error: Poetry is not installed. Please install Poetry first."
    exit 1
fi

echo "Installing dependencies..."
poetry install

if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(cat .env | xargs)
fi

export REDIS_URL=${REDIS_URL:-"redis://localhost:6379"}
export CORS_ORIGINS=${CORS_ORIGINS:-"http://localhost:3000,http://localhost:5173"}

echo "Starting FastAPI server on http://localhost:8000"
echo "API documentation available at http://localhost:8000/docs"
echo "Health check available at http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"

poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
