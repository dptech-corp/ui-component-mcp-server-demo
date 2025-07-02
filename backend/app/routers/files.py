from fastapi import APIRouter, HTTPException
from typing import List
from ..models.file import File, FileCreate, FileResponse
from ..services.file_service import file_service

router = APIRouter()

@router.get("/files", response_model=List[FileResponse])
async def get_files():
    """Get all files."""
    try:
        files = await file_service.get_all_files()
        return [FileResponse(
            id=f.id,
            name=f.name,
            type=f.type,
            path=f.path,
            size=f.size,
            created_at=f.created_at,
            updated_at=f.updated_at
        ) for f in files]
    except Exception as e:
        print(f"Error getting files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/files/{file_id}", response_model=File)
async def get_file(file_id: str):
    """Get a specific file."""
    file = await file_service.get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """Delete a file."""
    try:
        from ..main import sse_service
        
        success = await file_service.delete_file(file_id)
        if not success:
            raise HTTPException(status_code=404, detail="File not found")
        
        await sse_service.send_event("file_deleted", {"fileId": file_id})
        
        return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
