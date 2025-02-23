from pydantic import BaseModel
from typing import Optional, List




class FileMetadata(BaseModel):
    intended_location: str
    description: Optional[str] = None
    content_type: Optional[str] = None


class FileInfo(BaseModel):
    filename: str
    size: int
    storage_location: str
    upload_time: str
    metadata: FileMetadata