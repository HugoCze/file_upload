import os
import uuid
import logging
from typing import Optional
from fastapi import UploadFile
from app.core.config import Settings

settings = Settings()
logger = logging.getLogger(__name__)

def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed.
    
    Args:
        filename: The filename to check.
        
    Returns:
        True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

async def save_upload_file(upload_file: UploadFile, target_location: str) -> tuple[str, str, int]:
    """Save an uploaded file to the target location.
    
    Args:
        upload_file: The uploaded file object.
        target_location: The directory where the file should be saved.
        
    Returns:
        A tuple containing the file ID, path to the saved file, and file size.
    """
    # Generate a unique filename to prevent collisions
    original_filename = upload_file.filename
    file_id = str(uuid.uuid4())
    
    if not original_filename:
        raise ValueError("Filename is required")
    
    # Secure the filename
    safe_filename = ''.join(c for c in original_filename if c.isalnum() or c in '._- ')
    filename = f"{file_id}_{safe_filename}"
    
    # Create directory structure if it doesn't exist
    target_path = os.path.join(settings.UPLOAD_FOLDER, target_location)
    os.makedirs(target_path, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(target_path, filename)
    
    # Write file in chunks to handle large files
    file_size = 0
    with open(file_path, "wb") as buffer:
        # Process the file in chunks of 1MB
        chunk_size = 1024 * 1024
        while True:
            chunk = await upload_file.read(chunk_size)
            if not chunk:
                break
            buffer.write(chunk)
            file_size += len(chunk)
    
    return file_id, os.path.join(target_location, filename), file_size