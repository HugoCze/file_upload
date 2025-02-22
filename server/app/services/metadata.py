import os
import json
import logging
from typing import List, Dict, Any
from app.core.config import Settings
from app.models.file import FileMetadata


settings = Settings()
logger = logging.getLogger(__name__)

# Metadata storage file
METADATA_FILE = os.path.join(settings.UPLOAD_FOLDER, 'metadata.json')

async def initialize_metadata() -> None:
    """Initialize metadata storage if it doesn't exist."""
    os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
    if not os.path.exists(METADATA_FILE):
        async with open(METADATA_FILE, 'w') as f:
            await f.write(json.dumps([]))

async def save_metadata(file_metadata: FileMetadata) -> None:
    """Save file metadata to the metadata storage.
    
    Args:
        file_metadata: The file metadata to save.
    """
    try:
        await initialize_metadata()
        
        metadata_list = []
        if os.path.exists(METADATA_FILE) and os.path.getsize(METADATA_FILE) > 0:
            with open(METADATA_FILE, 'r') as f:
                metadata_list = json.load(f)
        
        metadata_list.append(file_metadata.model_dump())
        
        with open(METADATA_FILE, 'w') as f:
            json.dump(metadata_list, f, indent=2, default=str)
            
    except Exception as e:
        logger.error(f"Error saving metadata: {e}")
        raise

async def get_all_metadata() -> List[FileMetadata]:
    """Get all file metadata from storage.
    
    Returns:
        List of file metadata objects.
    """
    try:
        await initialize_metadata()
        
        if os.path.exists(METADATA_FILE) and os.path.getsize(METADATA_FILE) > 0:
            with open(METADATA_FILE, 'r') as f:
                metadata_list = json.load(f)
            return [FileMetadata.model_validate(item) for item in metadata_list]
        return []
    except Exception as e:
        logger.error(f"Error loading metadata: {e}")
        return []