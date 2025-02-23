from pydantic import BaseModel
from typing import Optional, List



class FileInfo(BaseModel):
    filename: str
    size: int
    storage_location: str
    upload_date: str
    upload_duration: float
