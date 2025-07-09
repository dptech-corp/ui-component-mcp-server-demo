#!/bin/bash

set -e

echo "Starting Google ADK Agent API server..."

export MCP_SERVER_URL=${MCP_SERVER_URL:-"http://localhost:8001/sse"}
export LLM_MODEL=${LLM_MODEL:-"gemini-2.0-flash"}
export OPENAI_API_KEY=${OPENAI_API_KEY}
export OPENAI_API_BASE_URL=${OPENAI_API_BASE_URL}
export SESSION_DB_URL=${SESSION_DB_URL}


cat > /app/api_server.py << 'EOF'
import os
import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from src.representation import root_agent

app = FastAPI(title="Todo Assistant Agent API")
session_service = InMemorySessionService()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        content = types.Content(
            role='user',
            parts=[types.Part(text=request.message)]
        )
        
        runner = Runner(
            app_name="todo_agent_api",
            agent=root_agent,
            session_service=session_service
        )
        
        events = []
        async for event in runner.run_async(
            session_id=request.session_id,
            user_id="api_user",
            new_message=content
        ):
            events.append(event)
        
        return {"response": events, "session_id": request.session_id}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_sse")
async def run_sse(request: dict):
    try:
        from fastapi.responses import StreamingResponse
        import json
        
        content_data = request.get("content", {})
        parts = content_data.get("parts", [])
        if not parts or not parts[0].get("text"):
            raise HTTPException(status_code=400, detail="Invalid request format")
            
        content = types.Content(
            role=content_data.get('role', 'user'),
            parts=[types.Part(text=parts[0]["text"])]
        )
        
        runner = Runner(
            app_name="todo_agent_api",
            agent=root_agent,
            session_service=session_service
        )
        
        async def generate_sse():
            events = []
            session_id = request.get("sessionId", "default")
            
            try:
                session = await session_service.get_or_create_session(
                    session_id=session_id,
                    state={},
                    app_name="todo_agent_api",
                    user_id="api_user"
                )
                actual_session_id = session.id
            except:
                actual_session_id = session_id
            
            async for event in runner.run_async(
                session_id=actual_session_id,
                user_id="api_user",
                new_message=content
            ):
                events.append(event)
                event_data = json.dumps(event.model_dump() if hasattr(event, 'model_dump') else str(event))
                yield f"data: {event_data}\n\n"
            
            final_response = {"response": events, "session_id": request.get("sessionId", "default")}
            yield f"data: {json.dumps(final_response)}\n\n"
        
        return StreamingResponse(
            generate_sse(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF

cd /app
uv run uvicorn api_server:app --host 0.0.0.0 --port 8002
