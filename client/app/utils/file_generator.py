import os
import random
import string
import uuid
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

def generate_random_data(size: int) -> bytes:
    """Generate random data of specified size
    
    Args:
        size: Size of data to generate in bytes
        
    Returns:
        bytes: Random data
    """
    # Generate in chunks to avoid memory issues
    chunk_size = 1024 * 1024  # 1MB chunks
    remaining = size
    data = b''
    
    logger.info(f"Generating {size / (1024 * 1024)} MB of random data")
    
    while remaining > 0:
        chunk = min(chunk_size, remaining)
        data += ''.join(random.choice(string.ascii_letters) for _ in range(chunk)).encode()
        remaining -= chunk
        
        # Log progress for large files
        if size > 100 * 1024 * 1024 and remaining % (100 * 1024 * 1024) == 0:
            logger.info(f"Generated {(size - remaining) / (1024 * 1024)} MB so far")
    
    return data

async def generate_temp_file(size: int, extension: str) -> Tuple[str, str]:
    """Generate a temporary file with random data
    
    Args:
        size: Size of file in bytes
        extension: File extension
        
    Returns:
        Tuple[str, str]: Filename and path to the generated file
    """
    filename = f"temp_{uuid.uuid4()}.{extension}"
    file_path = os.path.join("/tmp", filename)
    logger.info(f"Generating temporary file: {filename}")
    
    with open(file_path, 'wb') as f:
        f.write(generate_random_data(size))
    
    logger.info(f"File {filename} generated successfully")
    return filename, file_path