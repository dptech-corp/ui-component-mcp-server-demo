"""Backlog business logic service."""

import time
import uuid
from typing import List, Optional

from ..database import database
from ..models.backlog import Backlog, BacklogCreate, BacklogUpdate


class BacklogService:
    """Backlog service for managing backlog items with SQLite storage."""
    
    def __init__(self):
        pass
        
    async def get_all_backlogs(self) -> List[Backlog]:
        """Get all backlog items."""
        async with await database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, title, description, created_at, updated_at FROM backlog ORDER BY created_at DESC"
                )
                rows = await cursor.fetchall()
                
                backlogs = []
                for row in rows:
                    backlog = Backlog(
                        id=row[0],
                        title=row[1],
                        description=row[2] or "",
                        created_at=row[3],
                        updated_at=row[4]
                    )
                    backlogs.append(backlog)
                
                return backlogs
        
    async def get_backlog(self, backlog_id: str) -> Optional[Backlog]:
        """Get a specific backlog item."""
        async with await database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, title, description, created_at, updated_at FROM backlog WHERE id = %s",
                    (backlog_id,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return None
                    
                return Backlog(
                    id=row[0],
                    title=row[1],
                    description=row[2] or "",
                    created_at=row[3],
                    updated_at=row[4]
                )
        
    async def create_backlog(self, title: str, description: str = "") -> Backlog:
        """Create a new backlog item."""
        backlog_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        
        async with await database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO backlog (id, title, description, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                    (backlog_id, title, description, timestamp, timestamp)
                )
                await conn.commit()
        
        backlog = Backlog(
            id=backlog_id,
            title=title,
            description=description,
            created_at=timestamp,
            updated_at=timestamp
        )
        
        return backlog
        
    async def update_backlog(self, backlog_id: str, **kwargs) -> Optional[Backlog]:
        """Update a backlog item."""
        backlog = await self.get_backlog(backlog_id)
        if not backlog:
            return None
            
        timestamp = int(time.time() * 1000)
        
        update_fields = []
        update_values = []
        
        for field, value in kwargs.items():
            if hasattr(backlog, field) and value is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(value)
                setattr(backlog, field, value)
        
        if update_fields:
            update_fields.append("updated_at = %s")
            update_values.append(timestamp)
            update_values.append(backlog_id)
            
            async with await database.get_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"UPDATE backlog SET {', '.join(update_fields)} WHERE id = %s",
                        tuple(update_values)
                    )
                    await conn.commit()
            
            backlog.updated_at = timestamp
        
        return backlog
        
    async def delete_backlog(self, backlog_id: str) -> bool:
        """Delete a backlog item."""
        async with await database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM backlog WHERE id = %s", (backlog_id,))
                rowcount = cursor.rowcount
                await conn.commit()
        
        return rowcount > 0
        
    async def send_to_todo(self, backlog_id: str) -> Optional[dict]:
        """Move backlog item to todo and delete from backlog."""
        from .todo_service import TodoService
        
        backlog = await self.get_backlog(backlog_id)
        print(f"send_to_todo 0000000000: get_backlog {backlog}")
        if not backlog:
            print(f"send_to_todo 2222222222: backlog not found")
            return None
            
        todo_service = TodoService()
        todo = await todo_service.create_todo(
            title=backlog.title,
            description=backlog.description
        )
        print(f"send_to_todo 1111111111: create_todo {todo}")
        
        await self.delete_backlog(backlog_id)
        
        return {
            "backlog_id": backlog_id,
            "todo": todo.dict()
        }
