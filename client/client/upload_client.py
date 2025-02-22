import os
import random
import string
import logging
import asyncio
from app.utils.file_generator import generate_temp_file
from app.api.client import wait_for_api, upload_file
from app.config import settings

logger = logging.getLogger(__name__)

async def run() -> None:
    """Run the file upload client."""
    try:
        # Wait for the API to be available
        if not await wait_for_api():
            logger.error("API is not available. Exiting.")
            return
        
        # Choose a random file size (up to the configured maximum)
        size = random.randint(1024 * 1024, settings.FILE_SIZE)  # At least 1MB
        extension = random.choice(settings.FILE_EXTENSIONS)
        
        # Generate random folder structure for storage
        depth = random.randint(0, 2)
        location_parts = []
        
        for _ in range(depth):
            folder = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
            location_parts.append(folder)
        
        location = '/'.join(location_parts)
        
        # Generate and upload file
        filename, file_path = await generate_temp_file(size, extension)
        description = f"Test file {filename} uploaded at {asyncio.get_event_loop().time()}"
        
        success, response_data = await upload_file(file_path, location, description)
        
        # Clean up the temporary file
        try:
            os.remove(file_path)
            logger.info(f"Temporary file {file_path} removed")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {file_path}: {e}")
        
        if success:
            logger.info("Upload completed successfully")
        else:
            logger.error("Upload failed")
            exit(1)
            
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        exit(1)