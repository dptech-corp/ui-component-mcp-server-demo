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
        
        async with database.get_connection() as conn:
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
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, session_id, function_call_id, description, status, created_at, updated_at, result FROM approvals WHERE id = %s",
                    (approval_id,)
                )
                row = await cursor.fetchone()
                
                if row and len(row) >= 8:
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
        updated_at = int(time.time() * 1000)
        
        async with database.get_connection() as conn:
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
        print(f"DEBUG: get_all_approvals called")
        
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, session_id, function_call_id, description, status, created_at, updated_at, result FROM approvals ORDER BY created_at DESC"
                )
                rows = await cursor.fetchall()
                print(f"DEBUG: Query executed, found {len(rows)} rows")
                
                approvals = []
                for row in rows:
                    try:
                        print(f"DEBUG: Processing row with {len(row)} columns: {row}")
                        approval = Approval(
                            id=row[0] if len(row) > 0 else "",
                            session_id=row[1] if len(row) > 1 else "",
                            function_call_id=row[2] if len(row) > 2 else "",
                            description=row[3] if len(row) > 3 else "",
                            status=row[4] if len(row) > 4 else "pending",
                            created_at=row[5] if len(row) > 5 else 0,
                            updated_at=row[6] if len(row) > 6 else 0,
                            result=row[7] if len(row) > 7 else None
                        )
                        approvals.append(approval)
                    except Exception as e:
                        print(f"DEBUG: Error processing row {row}: {str(e)}")
                        continue
                
                return approvals

approval_service = ApprovalService()
