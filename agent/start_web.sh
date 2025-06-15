#!/bin/bash

set -e

echo "Starting Google ADK Agent in development mode..."

export MCP_SERVER_URL=${MCP_SERVER_URL:-"http://localhost:8001"}
export LLM_MODEL=${LLM_MODEL:-"gemini-2.0-flash"}

cd /app/src
adk web --host 0.0.0.0 --port 8002
