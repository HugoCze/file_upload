from fastapi import APIRouter, HTTPException
import logging
from app.models.file import FilesListResponse
from app.services.metadata import get_all_metadata

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["files"])

@router.get("/files", response_model=FilesListResponse)
async def list_files() -> FilesListResponse:
    """List all uploaded files.
    
    Returns:
        FilesListResponse: List of file metadata.
    """
    try:
        metadata_list = await get_all_metadata()
        return FilesListResponse(files=metadata_list)
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")