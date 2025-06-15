#!/bin/bash

set -e

echo "Starting Google ADK Agent in development mode..."

export MCP_SERVER_URL=${MCP_SERVER_URL:-"http://localhost:8001"}
export LLM_MODEL=${LLM_MODEL:-"gemini-1.5-flash"}
export OPENAI_API_KEY=${OPENAI_API_KEY}
export OPENAI_API_BASE_URL=${OPENAI_API_BASE_URL}

cd /app/src
uv run adk web --host 0.0.0.0 --port 8002
