"""Approval service for managing approval requests."""

import time
import uuid
from typing import List, Optional

from ..database import database
from ..models.approval import Approval, ApprovalCreate, ApprovalUpdate


class ApprovalService:
    """Service for managing approval requests."""
    
    async def create_approval(self, approval_data: ApprovalCreate) -> Approval:
        """Create a new approval request."""
        conn = await database.get_connection()
        
        approval_id = str(uuid.uuid4())
        current_time = int(time.time() * 1000)
        
        await conn.execute(
            """
            INSERT INTO approvals (id, session_id, function_call_id, description, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                approval_id,
                approval_data.session_id,
                approval_data.function_call_id,
                approval_data.description,
                approval_data.status,
                current_time,
                current_time
            )
        )
        await conn.commit()
        
        return Approval(
            id=approval_id,
            session_id=approval_data.session_id,
            function_call_id=approval_data.function_call_id,
            description=approval_data.description,
            status=approval_data.status,
            created_at=current_time,
            updated_at=current_time
        )
    
    async def get_approval(self, approval_id: str) -> Optional[Approval]:
        """Get an approval by ID."""
        conn = await database.get_connection()
        
        cursor = await conn.execute(
            "SELECT * FROM approvals WHERE id = ?",
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
                updated_at=row[6]
            )
        return None
    
    async def get_all_approvals(self) -> List[Approval]:
        """Get all approval requests."""
        conn = await database.get_connection()
        
        cursor = await conn.execute(
            "SELECT * FROM approvals ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()
        
        return [
            Approval(
                id=row[0],
                session_id=row[1],
                function_call_id=row[2],
                description=row[3],
                status=row[4],
                created_at=row[5],
                updated_at=row[6]
            )
            for row in rows
        ]
    
    async def update_approval(self, approval_id: str, update_data: ApprovalUpdate) -> Optional[Approval]:
        """Update an approval request."""
        conn = await database.get_connection()
        
        current_time = int(time.time() * 1000)
        
        await conn.execute(
            "UPDATE approvals SET status = ?, updated_at = ? WHERE id = ?",
            (update_data.status, current_time, approval_id)
        )
        await conn.commit()
        
        return await self.get_approval(approval_id)
    
    async def delete_approval(self, approval_id: str) -> bool:
        """Delete an approval request."""
        conn = await database.get_connection()
        
        cursor = await conn.execute(
            "DELETE FROM approvals WHERE id = ?",
            (approval_id,)
        )
        await conn.commit()
        
        return cursor.rowcount > 0
