"""Todo business logic service."""

import time
import uuid
from typing import Dict, List, Optional

from ..models.todo import Todo, TodoCreate, TodoUpdate


class TodoService:
    """Todo service for managing todo items."""
    
    def __init__(self):
        self.todos: Dict[str, Todo] = {}
        
    async def get_all_todos(self) -> List[Todo]:
        """Get all todo items."""
        return list(self.todos.values())
        
    async def get_todo(self, todo_id: str) -> Optional[Todo]:
        """Get a specific todo item."""
        return self.todos.get(todo_id)
        
    async def create_todo(self, title: str, description: str = "") -> Todo:
        """Create a new todo item."""
        todo_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        
        todo = Todo(
            id=todo_id,
            title=title,
            description=description,
            completed=False,
            created_at=timestamp,
            updated_at=timestamp
        )
        
        self.todos[todo_id] = todo
        return todo
        
    async def update_todo(self, todo_id: str, **kwargs) -> Optional[Todo]:
        """Update a todo item."""
        todo = self.todos.get(todo_id)
        if not todo:
            return None
            
        for field, value in kwargs.items():
            if hasattr(todo, field) and value is not None:
                setattr(todo, field, value)
                
        todo.updated_at = int(time.time() * 1000)
        return todo
        
    async def delete_todo(self, todo_id: str) -> bool:
        """Delete a todo item."""
        if todo_id in self.todos:
            del self.todos[todo_id]
            return True
        return False
        
    async def toggle_todo(self, todo_id: str) -> Optional[Todo]:
        """Toggle todo completion status."""
        todo = self.todos.get(todo_id)
        if not todo:
            return None
            
        todo.completed = not todo.completed
        todo.updated_at = int(time.time() * 1000)
        return todo
