"""Agent API router."""

import os
import httpx
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
import json
import asyncio

from ..models.agent import AgentMessageRequest, AgentResponse, AgentRequest, NewMessage, MessagePart, AgentStreamRequest, SessionCreateRequest, SessionCreateResponse

router = APIRouter()


@router.post("/agent/message", response_model=AgentResponse)
async def send_message_to_agent(message_data: AgentMessageRequest, request: Request):
    """Send message to Google ADK Agent."""
    try:
        session_id = message_data.sessionId
        if not session_id:
            async with httpx.AsyncClient() as client:
                session_response = await client.post(
                    "http://ui-mcp-agent:8002/apps/representation/users/demo/sessions",
                    json={"additionalProp1": {}},
                    timeout=10.0
                )
                session_response.raise_for_status()
                session_result = session_response.json()
                session_id = session_result.get("id")
                
                if not session_id:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to create session"
                    )
        
        agent_request_data = {
            "appName": "representation", 
            "userId": "demo",
            "sessionId": session_id,
            "newMessage": {
                "parts": [
                    {
                        "text": message_data.message
                    }
                ],
                "role": "user"
            },
            "streaming": False
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://ui-mcp-agent:8002/run",
                json=agent_request_data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            return AgentResponse(
                success=True,
                response=result
            )
            
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to communicate with agent: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/agent/stream")
async def stream_message_to_agent(message_data: AgentStreamRequest, request: Request):
    """Send message to Google ADK Agent with streaming response."""
    try:
        session_id = None
        
        if not session_id:
            async with httpx.AsyncClient() as client:
                session_response = await client.post(
                    "http://ui-mcp-agent:8002/apps/representation/users/demo/sessions",
                    json={"additionalProp1": {}},
                    timeout=10.0
                )
                session_response.raise_for_status()
                session_result = session_response.json()
                session_id = session_result.get("id")
                
                if not session_id:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to create session"
                    )
        
        agent_request_data = {
            "appName": "representation",
            "userId": "demo",
            "sessionId": session_id,
            "newMessage": {
                "parts": [
                    {
                        "text": message_data.message
                    }
                ],
                "role": "user"
            },
            "streaming": True
        }
        
        async def generate_stream():
            try:
                import sys
                print(f"STREAM DEBUG: About to call /run_sse with data: {agent_request_data}", file=sys.stderr, flush=True)
                
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "http://ui-mcp-agent:8002/run_sse",
                        json=agent_request_data,
                        timeout=60.0
                    )
                    print(f"STREAM DEBUG: Response status: {response.status_code}", file=sys.stderr, flush=True)
                    print(f"STREAM DEBUG: Response headers: {response.headers}", file=sys.stderr, flush=True)
                    response.raise_for_status()
                    
                    result = response.text
                    
                    import sys
                    print(f"STREAM DEBUG: ADK response type: {type(result)}", file=sys.stderr, flush=True)
                    print(f"STREAM DEBUG: ADK response: {result}", file=sys.stderr, flush=True)
                    
                    try:
                        with open("/tmp/adk_debug.log", "a") as f:
                            f.write(f"ADK response: {result}\n")
                            f.flush()
                        print(f"DEBUG: Successfully wrote to debug file", file=sys.stderr, flush=True)
                    except Exception as e:
                        print(f"DEBUG: Failed to write to file: {e}", file=sys.stderr, flush=True)
                    
                    response_text = result if isinstance(result, str) else str(result)
                    
                    print(f"STREAM DEBUG: Raw response text: {response_text}", file=sys.stderr, flush=True)
                    
                    lines = response_text.split('\n')
                    accumulated_text = ""
                    
                    for line in lines:
                        if line.startswith('data: '):
                            try:
                                data = json.loads(line[6:])
                                if 'content' in data and 'parts' in data['content']:
                                    for part in data['content']['parts']:
                                        if 'text' in part and part['text']:
                                            accumulated_text += part['text']
                                            yield f"data: {json.dumps({'content': {'parts': [{'text': part['text']}]}, 'partial': data.get('partial', False)})}\n\n"
                            except json.JSONDecodeError as e:
                                print(f"STREAM DEBUG: Failed to parse line: {line}, error: {e}", file=sys.stderr, flush=True)
                                continue
                    
                    if not accumulated_text:
                        yield f"data: {json.dumps({'content': {'parts': [{'text': '收到响应，但无法解析文本内容'}]}, 'partial': False})}\n\n"
                    
                    yield f"data: {json.dumps({'done': True})}\n\n"
                                    
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to setup streaming with agent: {str(e)}"
        )


@router.post("/agent/session")
async def create_agent_session(session_data: SessionCreateRequest = SessionCreateRequest()):
    """Create a new agent session."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://ui-mcp-agent:8002/apps/representation/users/demo/sessions",
                json=session_data.dict(),
                timeout=10.0
            )
            response.raise_for_status()
            
            result = response.json()
            session_id = result.get("id")
            
            if session_id:
                return SessionCreateResponse(
                    sessionId=session_id,
                    success=True
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Session created but no sessionId returned"
                )
                
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to create session: {e.response.text}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.get("/agent/health")
async def check_agent_health():
    """Check agent health status."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://ui-mcp-agent:8002/health",
                timeout=5.0
            )
            return {"status": "healthy", "agent_status": response.status_code}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
