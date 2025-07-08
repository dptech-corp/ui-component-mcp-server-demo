import time
import uuid
from typing import List, Optional

from ..database import database
from ..models.plan import Plan


class PlanService:
    def __init__(self):
        pass
    
    async def create_plan(self, plan: Plan) -> Plan:
        """Create a new plan."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO plans 
                       (id, session_id, title, description, status, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (plan.id, plan.session_id, plan.title, 
                     plan.description, plan.status, plan.created_at, 
                     plan.updated_at)
                )
                await conn.commit()
                return plan
    
    async def get_plan(self, plan_id: str) -> Optional[Plan]:
        """Get a plan by ID."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, session_id, title, description, status, created_at, updated_at FROM plans WHERE id = %s",
                    (plan_id,)
                )
                row = await cursor.fetchone()
                
                if row and len(row) >= 7:
                    return Plan(
                        id=row[0],
                        session_id=row[1],
                        title=row[2],
                        description=row[3] or "",
                        status=row[4],
                        created_at=row[5],
                        updated_at=row[6]
                    )
                return None
    
    async def get_all_plans(self, session_id: Optional[str] = None) -> List[Plan]:
        """Get all plans, optionally filtered by session_id."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                if session_id:
                    await cursor.execute(
                        "SELECT id, session_id, title, description, status, created_at, updated_at FROM plans WHERE session_id = %s ORDER BY created_at DESC",
                        (session_id,)
                    )
                else:
                    await cursor.execute(
                        "SELECT id, session_id, title, description, status, created_at, updated_at FROM plans ORDER BY created_at DESC"
                    )
                rows = await cursor.fetchall()
                
                plans = []
                for row in rows:
                    plan = Plan(
                        id=row[0],
                        session_id=row[1],
                        title=row[2],
                        description=row[3] or "",
                        status=row[4],
                        created_at=row[5],
                        updated_at=row[6]
                    )
                    plans.append(plan)
                
                return plans
    
    async def update_plan(self, plan_id: str, **kwargs) -> Optional[Plan]:
        """Update a plan."""
        plan = await self.get_plan(plan_id)
        if not plan:
            return None
            
        timestamp = int(time.time() * 1000)
        
        update_fields = []
        update_values = []
        
        for field, value in kwargs.items():
            if hasattr(plan, field) and value is not None:
                update_fields.append(f"{field} = %s")
                update_values.append(value)
                setattr(plan, field, value)
        
        if update_fields:
            update_fields.append("updated_at = %s")
            update_values.append(timestamp)
            update_values.append(plan_id)
            
            async with database.get_connection() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        f"UPDATE plans SET {', '.join(update_fields)} WHERE id = %s",
                        tuple(update_values)
                    )
                    await conn.commit()
            
            plan.updated_at = timestamp
        
        return plan
    
    async def update_plan_status(self, plan_id: str, status: str) -> Optional[Plan]:
        """Update the status of a plan."""
        return await self.update_plan(plan_id, status=status)
    
    async def delete_plan(self, plan_id: str) -> bool:
        """Delete a plan."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM plans WHERE id = %s", (plan_id,))
                await conn.commit()
                
                return cursor.rowcount > 0


plan_service = PlanService()
