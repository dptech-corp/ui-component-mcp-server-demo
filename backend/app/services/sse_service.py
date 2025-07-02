"""SSE service for real-time events."""

import asyncio
import json
from typing import Any, Dict, Set
from fastapi import Request
from fastapi.responses import StreamingResponse


class SSEService:
    """Server-Sent Events service."""
    
    def __init__(self):
        self.connections: Set[asyncio.Queue] = set()
        self._cleanup_task = None
        self._start_cleanup_task()
        
    async def add_connection(self) -> asyncio.Queue:
        """Add a new SSE connection."""
        queue = asyncio.Queue()
        self.connections.add(queue)
        return queue
        
    async def remove_connection(self, queue: asyncio.Queue):
        """Remove an SSE connection."""
        self.connections.discard(queue)
        
    async def send_event(self, event: str, data: Dict[str, Any]):
        """Send an event to all connected clients."""
        if not self.connections:
            return
            
        event_data = {
            "event": event,
            "data": data
        }
        
        disconnected = set()
        for queue in self.connections:
            try:
                await queue.put(event_data)
            except Exception:
                disconnected.add(queue)
                
        for queue in disconnected:
            self.connections.discard(queue)
            
    async def event_stream(self, request: Request):
        """Generate SSE event stream."""
        queue = await self.add_connection()
        
        try:
            while True:
                if await request.is_disconnected():
                    break
                    
                try:
                    event_data = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {json.dumps(event_data)}\n\n"
                except asyncio.TimeoutError:
                    yield "data: {\"event\": \"heartbeat\"}\n\n"
                    
        except Exception as e:
            print(f"SSE stream error: {e}")
        finally:
            await self.remove_connection(queue)
            
    def _start_cleanup_task(self):
        """Start background task to clean up dead connections."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_connections())
    
    async def _cleanup_connections(self):
        """Periodically clean up dead connections."""
        while True:
            try:
                await asyncio.sleep(60)
                dead_connections = set()
                
                for queue in self.connections.copy():
                    try:
                        if queue.qsize() > 100:
                            dead_connections.add(queue)
                    except Exception:
                        dead_connections.add(queue)
                
                for queue in dead_connections:
                    self.connections.discard(queue)
                    
                if dead_connections:
                    print(f"Cleaned up {len(dead_connections)} dead SSE connections")
                    
            except Exception as e:
                print(f"Error in SSE cleanup task: {e}")
