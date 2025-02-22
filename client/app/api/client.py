import os
import aiohttp
import logging
import asyncio
from typing import Dict, Any, Optional, Tuple
from app.config import settings

logger = logging.getLogger(__name__)

async def check_api_health() -> bool:
    """Check if the API is available.
    
    Returns:
        bool: True if the API is available, False otherwise.
    """
    try:
        health_url = f"{settings.API_URL}/health"
        async with aiohttp.ClientSession() as session:
            async with session.get(health_url, timeout=10) as response:
                if response.status == 200:
                    logger.info("API is available.")
                    return True
                logger.warning(f"API not ready (status code: {response.status}).")
                return False
    except Exception as e:
        logger.warning(f"API not available: {e}")
        return False

async def wait_for_api(max_retries: int = 10, retry_interval: int = 5) -> bool:
    """Wait for the API to be available.
    
    Args:
        max_retries: Maximum number of retries.
        retry_interval: Interval between retries in seconds.
        
    Returns:
        bool: True if the API became available, False otherwise.
    """
    for attempt in range(max_retries):
        if await check_api_health():
            return True
        logger.warning(f"API not available. Retry {attempt+1}/{max_retries}")
        if attempt < max_retries - 1:
            await asyncio.sleep(retry_interval)
    
    logger.error(f"API not available after {max_retries} attempts.")
    return False

async def upload_file(file_path: str, location: str, description: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """Upload a file to the API.
    
    Args:
        file_path: Path to the file to upload.
        location: Target location in the storage system.
        description: Description of the file.
        
    Returns:
        Tuple[bool, Optional[Dict[str, Any]]]: Success status and response data.
    """
    filename = os.path.basename(file_path)
    url = f"{settings.API_URL}/api/v1/upload"
    
    logger.info(f"Uploading file {filename} to location {location}")
    
    try:
        async with aiohttp.ClientSession() as session:
            # Prepare form data
            data = aiohttp.FormData()
            data.add_field('location', location)
            data.add_field('description', description)
            
            # Add file
            with open(file_path, 'rb') as f:
                data.add_field('file', 
                               f, 
                               filename=filename,
                               content_type='application/octet-stream')
            
            # Send request with timeout
            start_time = asyncio.get_event_loop().time()
            async with session.post(url, data=data, timeout=settings.TIMEOUT) as response:
                end_time = asyncio.get_event_loop().time()
                
                # Parse response
                response_data = await response.json()
                
                if response.status == 201:
                    upload_time = end_time - start_time
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    upload_speed = file_size_mb / upload_time if upload_time > 0 else 0
                    
                    logger.info(
                        f"Upload successful: {filename} "
                        f"({file_size_mb:.2f} MB in {upload_time:.2f}s, "
                        f"{upload_speed:.2f} MB/s)"
                    )
                    return True, response_data
                else:
                    logger.error(
                        f"Upload failed: {filename}, Status: {response.status}, "
                        f"Response: {response_data}"
                    )
                    return False, response_data
    except Exception as e:
        logger.error(f"Exception during upload: {e}")
        return False, None