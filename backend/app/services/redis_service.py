"""Redis service for message handling."""

import asyncio
import json
from typing import Optional

from redis.asyncio import Redis


class RedisService:
    """Redis service for handling pub/sub messages."""
    # TODO 封装成 BaseRedisService 放到 dp.agent.ui.mq.redis.consumer
    
    def __init__(self):
        self.redis: Optional[Redis] = None
        self.pubsub = None
        
    async def connect(self, redis_url: str):
        """Connect to Redis."""
        self.redis = Redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
        
        await self.pubsub.subscribe("todo:actions")
        
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        if self.redis:
            await self.redis.close()
            
    async def listen_for_messages(self):
        """Listen for Redis messages and process them."""
        if not self.pubsub:
            return
            
        async for message in self.pubsub.listen():
            if message["type"] == "message":
                try:
                    data = json.loads(message["data"])
                    await self._process_message(data)
                except Exception as e:
                    print(f"Error processing message: {e}")
                    
    async def _process_message(self, message: dict):
        """Process a received message."""
        # TODO class BaseRedisService 中把这个作为 abstractmethod,然后让子类实现
        message_type = message.get("type")
        
        if message_type == "todo_action":
            await self._handle_todo_action(message)
        else:
            print(f"Unknown message type: {message_type}")
            
    async def _handle_todo_action(self, message: dict):
        """Handle todo action messages."""
        from ..main import todo_service, sse_service
        
        payload = message.get("payload", {})
        action = payload.get("action")
        
        try:
            if action == "add":
                data = payload.get("data", {})
                todo = await todo_service.create_todo(
                    title=data.get("title", ""),
                    description=data.get("description", "")
                )
                await sse_service.send_event("todo_added", {"todo": todo.dict()})
                
            elif action == "delete":
                todo_id = payload.get("todoId")
                if todo_id:
                    await todo_service.delete_todo(todo_id)
                    await sse_service.send_event("todo_deleted", {"todoId": todo_id})
                    
            elif action == "update":
                todo_id = payload.get("todoId")
                data = payload.get("data", {})
                if todo_id:
                    todo = await todo_service.update_todo(todo_id, **data)
                    if todo:
                        await sse_service.send_event("todo_updated", {"todo": todo.dict()})
                        
            elif action == "toggle":
                todo_id = payload.get("todoId")
                if todo_id:
                    todo = await todo_service.toggle_todo(todo_id)
                    if todo:
                        await sse_service.send_event("todo_updated", {"todo": todo.dict()})
                        
            elif action == "list":
                todos = await todo_service.get_all_todos()
                todos_data = [todo.dict() for todo in todos]
                await sse_service.send_event("todo_list", {"todos": todos_data})
                        
        except Exception as e:
            print(f"Error handling todo action: {e}")
