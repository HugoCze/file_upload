import logging
from typing import Optional
from datetime import datetime
from fastapi.responses import JSONResponse
from app.services.metadata import save_metadata
from app.models.file import FileResponse, FileMetadata
from app.utils.file_utils import allowed_file, save_upload_file
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["uploads"])

@router.post("/upload", response_model=FileResponse, status_code=201)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    location: str = Form(""),
    description: Optional[str] = Form(None)
) -> FileResponse:
    """Upload a file with metadata.
    
    Args:
        background_tasks: Background tasks runner.
        file: The file to upload.
        location: The target location in the storage system.
        description: A description of the file.
        
    Returns:
        FileResponse: Response with file metadata.
    """
    # Check if file is provided
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected")
    
    # Check file extension
    if not allowed_file(file.filename):
        raise HTTPException(status_code=400, detail="File type not allowed")
    
    try:
        # Save the file
        file_id, storage_location, file_size = await save_upload_file(file, location)
        
        # Create metadata
        file_metadata = FileMetadata(
            id=file_id,
            original_filename=file.filename,
            stored_filename=storage_location.split('/')[-1],
            storage_location=storage_location,
            size=file_size,
            upload_date=datetime.now(),
            description=description
        )
        
        # Save metadata in the background to improve response time
        background_tasks.add_task(save_metadata, file_metadata)
        
        logger.info(f"File uploaded successfully: {file.filename}")
        return FileResponse(
            message="File uploaded successfully",
            metadata=file_metadata
        )
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")