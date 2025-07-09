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
        
        app_name = request.get("appName", "representation")
        user_id = request.get("userId", "demo")
        session_id = request.get("sessionId", "default")
        new_message = request.get("newMessage", {})
        streaming = request.get("streaming", True)
        
        parts = new_message.get("parts", [])
        if not parts or not parts[0].get("text"):
            raise HTTPException(status_code=400, detail="Invalid request format")
            
        content = types.Content(
            role=new_message.get('role', 'user'),
            parts=[types.Part(text=parts[0]["text"])]
        )
        
        runner = Runner(
            app_name=app_name,
            agent=root_agent,
            session_service=session_service
        )
        
        async def generate_sse():
            events = []
            
            try:
                existing_session = await session_service.get_session(session_id)
            except:
                try:
                    await session_service.create_session(
                        session_id=session_id,
                        app_name=app_name,
                        user_id=user_id,
                        state={}
                    )
                except Exception as create_error:
                    print(f"Session creation error: {create_error}")
            
            async for event in runner.run_async(
                session_id=session_id,
                user_id=user_id,
                new_message=content
            ):
                events.append(event)
                if hasattr(event, 'content') and hasattr(event.content, 'parts'):
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            event_data = {
                                "content": {
                                    "parts": [{"text": part.text}]
                                },
                                "partial": True
                            }
                            yield f"data: {json.dumps(event_data)}\n\n"
                elif hasattr(event, 'model_dump'):
                    event_data = event.model_dump()
                    yield f"data: {json.dumps(event_data)}\n\n"
                else:
                    event_data = {"content": {"parts": [{"text": str(event)}]}, "partial": True}
                    yield f"data: {json.dumps(event_data)}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        return StreamingResponse(
            generate_sse(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/apps/representation/users/demo/sessions")
async def create_session(request: dict = {}):
    try:
        import uuid
        session_id = str(uuid.uuid4())
        return {"id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/apps/representation/users/demo/sessions/{session_id}")
async def create_specific_session(session_id: str, request: dict = {}):
    try:
        return {"id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/apps/representation/users/demo/sessions/{session_id}")
async def get_session(session_id: str):
    try:
        return {"id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy"}
EOF

cd /app
uv run uvicorn api_server:app --host 0.0.0.0 --port 8002
