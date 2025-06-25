import asyncio
import time
from typing import List, Optional
from ..models.approval import Approval
from ..database import database

class ApprovalService:
    def __init__(self):
        pass
    
    async def create_approval(self, approval: Approval) -> Approval:
        """Create a new approval request."""
        print(f"DEBUG: create_approval called with approval: {approval}")
        
        if not database.pool:
            print("DEBUG: Database pool is None, connecting...")
            await database.connect()
            print(f"DEBUG: After connect, database.pool is None: {database.pool is None}")
        
        async with database.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO approvals 
                       (id, session_id, function_call_id, description, status, created_at, updated_at, result)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                    (approval.id, approval.session_id, approval.function_call_id, 
                     approval.description, approval.status, approval.created_at, 
                     approval.updated_at, approval.result)
                )
                await conn.commit()
                print(f"DEBUG: Approval created successfully: {approval.id}")
                return approval
    
    async def get_approval(self, approval_id: str) -> Optional[Approval]:
        """Get an approval request by ID."""
        if not database.pool:
            await database.connect()
        
        async with database.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM approvals WHERE id = %s",
                    (approval_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    return Approval(
                        id=row[0],
                        session_id=row[1],
                        function_call_id=row[2],
                        description=row[3],
                        status=row[4],
                        created_at=row[5],
                        updated_at=row[6],
                        result=row[7]
                    )
                return None
    
    async def update_approval_status(self, approval_id: str, status: str, result: Optional[str] = None) -> Optional[Approval]:
        """Update the status of an approval request."""
        if not database.pool:
            await database.connect()
        
        updated_at = int(time.time() * 1000)
        
        async with database.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "UPDATE approvals SET status = %s, result = %s, updated_at = %s WHERE id = %s",
                    (status, result, updated_at, approval_id)
                )
                await conn.commit()
                
                if cursor.rowcount > 0:
                    return await self.get_approval(approval_id)
                return None
    
    async def get_all_approvals(self) -> List[Approval]:
        """Get all approval requests."""
        print(f"DEBUG: get_all_approvals called, database.pool is None: {database.pool is None}")
        
        if not database.pool:
            print("DEBUG: Database pool is None, connecting...")
            await database.connect()
            print(f"DEBUG: After connect, database.pool is None: {database.pool is None}")
        
        async with database.pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT * FROM approvals ORDER BY created_at DESC"
                )
                rows = await cursor.fetchall()
                print(f"DEBUG: Query executed, found {len(rows)} rows")
                
                return [
                    Approval(
                        id=row[0],
                        session_id=row[1],
                        function_call_id=row[2],
                        description=row[3],
                        status=row[4],
                        created_at=row[5],
                        updated_at=row[6],
                        result=row[7]
                    )
                    for row in rows
                ]

approval_service = ApprovalService()
