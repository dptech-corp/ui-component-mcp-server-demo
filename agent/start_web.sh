#!/bin/bash

set -e

echo "Starting Google ADK Agent in development mode..."

export MCP_SERVER_URL=${MCP_SERVER_URL:-"http://localhost:8001"}
export LLM_MODEL=${LLM_MODEL:-"gemini-1.5-flash"}
export OPENAI_API_KEY=${OPENAI_API_KEY}
export OPENAI_API_BASE_URL=${OPENAI_API_BASE_URL}
export SESSION_DB_URL=${SESSION_DB_URL}

cd /app/src

# Add the project root directory to PYTHONPATH to resolve import issues
export PYTHONPATH="$PYTHONPATH:/app/src"

# Check if SESSION_DB_URL is set and not empty
if [ -n "${SESSION_DB_URL}" ]; then
  uv run adk web --host 0.0.0.0 --port 8002 --session_service_uri $SESSION_DB_URL
else
  uv run adk web --host 0.0.0.0 --port 8002
fi
