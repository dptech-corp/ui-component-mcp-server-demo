import time
import uuid
from typing import List, Optional
from ..models.code_interpreter import CodeInterpreterState
from ..database import database

class CodeInterpreterService:
    def __init__(self):
        pass
    
    async def create_python_notebook(self, state_id: str, code: str, description: str = "") -> CodeInterpreterState:
        """Create a new code interpreter state."""
        ticket_id = f"code-interpreter-{uuid.uuid4().hex[:8]}"
        timestamp = int(time.time() * 1000)
        widget_url = f"https://uni-interpreter.mlops.dp.tech/widget?instance_id={state_id}"
        
        state = CodeInterpreterState(
            id=state_id,
            ticket_id=ticket_id,
            code=code,
            description=description,
            status="pending",
            widget_url=widget_url,
            created_at=timestamp,
            updated_at=timestamp
        )
        
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO code_interpreter_states 
                       (id, ticket_id, code, description, status, result, widget_url, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (state.id, state.ticket_id, state.code, 
                     state.description, state.status, state.result, state.widget_url, 
                     state.created_at, state.updated_at)
                )
                await conn.commit()
                return state
    
    async def get_notebook_state(self, state_id: str) -> Optional[CodeInterpreterState]:
        """Get a code interpreter state by ID."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT id, ticket_id, code, description, status, 
                              result, widget_url, created_at, updated_at 
                       FROM code_interpreter_states WHERE id = %s""",
                    (state_id,)
                )
                row = await cursor.fetchone()
                
                if row and len(row) >= 9:
                    return CodeInterpreterState(
                        id=row[0],
                        ticket_id=row[1],
                        code=row[2],
                        description=row[3],
                        status=row[4],
                        result=row[5],
                        widget_url=row[6],
                        created_at=row[7],
                        updated_at=row[8]
                    )
                return None
    
    async def get_all_states(self) -> List[CodeInterpreterState]:
        """Get all code interpreter states."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """SELECT id, ticket_id, code, description, status, 
                              result, widget_url, created_at, updated_at 
                       FROM code_interpreter_states 
                       ORDER BY created_at DESC"""
                )
                rows = await cursor.fetchall()
                
                states = []
                for row in rows:
                    if len(row) >= 9:
                        state = CodeInterpreterState(
                            id=row[0],
                            ticket_id=row[1],
                            code=row[2],
                            description=row[3],
                            status=row[4],
                            result=row[5],
                            widget_url=row[6],
                            created_at=row[7],
                            updated_at=row[8]
                        )
                        states.append(state)
                
                return states
    
    async def update_state(self, state_id: str, **kwargs) -> Optional[CodeInterpreterState]:
        """Update a code interpreter state."""
        state = await self.get_notebook_state(state_id)
        if not state:
            return None
            
        timestamp = int(time.time() * 1000)
        
        update_fields = []
        update_values = []
        
        for field, value in kwargs.items():
            if hasattr(state, field) and value is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(value)
                setattr(state, field, value)
        
        if update_fields:
            update_fields.append("updated_at = %s")
            update_values.append(timestamp)
            update_values.append(state_id)
            
            async with database.get_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"UPDATE code_interpreter_states SET {', '.join(update_fields)} WHERE id = %s",
                        update_values
                    )
                    await conn.commit()
            
            state.updated_at = timestamp
        
        return state
    
    async def delete_state(self, state_id: str) -> bool:
        """Delete a code interpreter state."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM code_interpreter_states WHERE id = %s", (state_id,))
                await conn.commit()
                
                return cursor.rowcount > 0

code_interpreter_service = CodeInterpreterService()
