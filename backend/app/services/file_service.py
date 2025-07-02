import time
import uuid
from typing import List, Optional
from ..models.file import File
from ..database import database

class FileService:
    def __init__(self):
        pass
    
    async def create_file(self, file: File) -> File:
        """Create a new file."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    """INSERT INTO files 
                       (id, session_id, name, type, path, size, content, created_at, updated_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (file.id, file.session_id, file.name, file.type, 
                     file.path, file.size, file.content, file.created_at, file.updated_at)
                )
                await conn.commit()
                return file
    
    async def get_all_files(self) -> List[File]:
        """Get all files (not filtered by session_id as per user requirement)."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, session_id, name, type, path, size, content, created_at, updated_at FROM files ORDER BY path ASC"
                )
                rows = await cursor.fetchall()
                
                files = []
                for row in rows:
                    file = File(
                        id=row[0],
                        session_id=row[1],
                        name=row[2],
                        type=row[3],
                        path=row[4],
                        size=row[5],
                        content=row[6],
                        created_at=row[7],
                        updated_at=row[8]
                    )
                    files.append(file)
                return files
    
    async def get_file(self, file_id: str) -> Optional[File]:
        """Get a file by ID."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(
                    "SELECT id, session_id, name, type, path, size, content, created_at, updated_at FROM files WHERE id = %s",
                    (file_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    return File(
                        id=row[0],
                        session_id=row[1],
                        name=row[2],
                        type=row[3],
                        path=row[4],
                        size=row[5],
                        content=row[6],
                        created_at=row[7],
                        updated_at=row[8]
                    )
                return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file."""
        async with database.get_connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
                await conn.commit()
                return cursor.rowcount > 0

file_service = FileService()
