"""Todo business logic service."""

import time
import uuid
from typing import List, Optional

from ..database import database
from ..models.todo import Todo, TodoCreate, TodoUpdate


class TodoService:
    """Todo service for managing todo items with SQLite storage."""
    
    def __init__(self):
        pass
        
    async def get_all_todos(self, session_id: Optional[str] = None) -> List[Todo]:
        """Get all todo items, optionally filtered by session_id."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                if session_id:
                    await cursor.execute(
                        "SELECT id, title, description, completed, session_id, created_at, updated_at FROM todos WHERE session_id = %s ORDER BY created_at ASC",
                        (session_id,)
                    )
                else:
                    await cursor.execute(
                        "SELECT id, title, description, completed, session_id, created_at, updated_at FROM todos ORDER BY created_at ASC"
                    )
                rows = await cursor.fetchall()
                
                todos = []
                for row in rows:
                    todo = Todo(
                        id=row[0],
                        title=row[1],
                        description=row[2] or "",
                        completed=bool(row[3]),
                        session_id=row[4] or "default_session",
                        created_at=row[5],
                        updated_at=row[6]
                    )
                    todos.append(todo)
                
                return todos
        
    async def get_todo(self, todo_id: str) -> Optional[Todo]:
        """Get a specific todo item."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, title, description, completed, session_id, created_at, updated_at FROM todos WHERE id = %s",
                    (todo_id,)
                )
                row = await cursor.fetchone()
                
                if not row:
                    return None
                    
                return Todo(
                    id=row[0],
                    title=row[1],
                    description=row[2] or "",
                    completed=bool(row[3]),
                    session_id=row[4] or "default_session",
                    created_at=row[5],
                    updated_at=row[6]
                )
        
    async def create_todo(self, title: str, description: str = "", session_id: str = "default_session") -> Todo:
        """Create a new todo item."""
        todo_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "INSERT INTO todos (id, title, description, completed, session_id, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (todo_id, title, description, False, session_id, timestamp, timestamp)
                )
                await conn.commit()
        
        todo = Todo(
            id=todo_id,
            title=title,
            description=description,
            completed=False,
            session_id=session_id,
            created_at=timestamp,
            updated_at=timestamp
        )
        
        return todo
        
    async def update_todo(self, todo_id: str, **kwargs) -> Optional[Todo]:
        """Update a todo item."""
        todo = await self.get_todo(todo_id)
        if not todo:
            return None
            
        timestamp = int(time.time() * 1000)
        
        update_fields = []
        update_values = []
        
        for field, value in kwargs.items():
            if hasattr(todo, field) and value is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(value)
                setattr(todo, field, value)
        
        if update_fields:
            update_fields.append("updated_at = %s")
            update_values.append(timestamp)
            update_values.append(todo_id)
            
            async with database.get_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"UPDATE todos SET {', '.join(update_fields)} WHERE id = %s",
                        update_values
                    )
                    await conn.commit()
            
            todo.updated_at = timestamp
        
        return todo
        
    async def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo item."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
                await conn.commit()
                
                return cursor.rowcount > 0
        
    async def toggle_todo(self, todo_id: str) -> Optional[Todo]:
        """Toggle todo completion status."""
        todo = await self.get_todo(todo_id)
        if not todo:
            return None
            
        new_completed = not todo.completed
        timestamp = int(time.time() * 1000)
        
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "UPDATE todos SET completed = %s, updated_at = %s WHERE id = %s",
                    (new_completed, timestamp, todo_id)
                )
                await conn.commit()
        
        todo.completed = new_completed
        todo.updated_at = timestamp
        return todo
        
    async def clear_all_todos(self, session_id: str = "default_session") -> int:
        """Clear all todo items for a session."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "DELETE FROM todos WHERE session_id = %s", 
                    (session_id,)
                )
                await conn.commit()
                
                return cursor.rowcount
