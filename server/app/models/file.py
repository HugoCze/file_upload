from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class FileMetadata(BaseModel):
    """File metadata model.
    
    Attributes:
        id: Unique identifier for the file.
        original_filename: Original name of the file.
        stored_filename: Name of the file as stored in the system.
        storage_location: Path where the file is stored.
        size: Size of the file in bytes.
        upload_date: Date and time when the file was uploaded.
        description: Optional description of the file.
    """
    id: str
    original_filename: str
    stored_filename: str
    storage_location: str
    size: int
    upload_date: datetime
    description: Optional[str] = None
    
class FileResponse(BaseModel):
    """Response model for file upload.
    
    Attributes:
        message: Success or error message.
        metadata: Metadata of the uploaded file.
    """
    message: str
    metadata: FileMetadata
    
class FilesListResponse(BaseModel):
    """Response model for listing files.
    
    Attributes:
        files: List of file metadata.
    """
    files: list[FileMetadata]
    
class HealthResponse(BaseModel):
    """Response model for health check.
    
    Attributes:
        status: Health status of the service.
    """
    status: str = "healthy"