import json
import aiofiles
from typing import List
from pathlib import Path
from datetime import datetime
from logs.logger import logger
from fastapi.responses import JSONResponse
from models.file_info import FileInfo
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

upload_router = APIRouter()
data_router = APIRouter()

UPLOAD_DIR = Path("storage")
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.doc', '.docx', '.csv', '.dat'}
BUFFER_SIZE = 100 
file_info_buffer = []


def is_valid_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


async def flush_buffer():
    global file_info_buffer
    if file_info_buffer:
        async with aiofiles.open(UPLOAD_DIR / "file_index.json", "a+", buffering=8192) as f:
            await f.write("\n".join(file_info_buffer) + "\n")
        file_info_buffer.clear()


async def save_file_info(file_info: FileInfo):
    global file_info_buffer
    
    file_info_buffer.append(json.dumps(file_info.dict()))
    
    if len(file_info_buffer) >= BUFFER_SIZE:
        await flush_buffer()


def get_optimal_chunk_size(file_size: int) -> int:
    """
    Determine optimal chunk size based on file size
    """
    MIN_CHUNK = 5 * 1024 * 1024    # 5MB
    MAX_CHUNK = 20 * 1024 * 1024   # 20MB
    DEFAULT_CHUNK = 8 * 1024 * 1024  # 8MB for files where size can't be determined
    
    if not file_size:
        return DEFAULT_CHUNK
        
    if file_size <= 2 * 1024 * 1024 * 1024:    # 2GB
        return MIN_CHUNK
    elif file_size >= 8 * 1024 * 1024 * 1024:  # 8GB
        return MAX_CHUNK
    else:
        # Scale chunk size between min and max based on file size
        return min(MAX_CHUNK, max(MIN_CHUNK, file_size // 500))


@upload_router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    try:
        start_time = datetime.now()
        
        if not is_valid_extension(file.filename):
            logger.error(f"Invalid file extension: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {ALLOWED_EXTENSIONS}"
            )

        # Get file size if possible
        try:
            file_size = file.size  # Some upload handlers provide this
        except AttributeError:
            file_size = 0  # Will use default chunk size
            logger.warning("Could not determine file size, using default chunk size")

        chunk_size = get_optimal_chunk_size(file_size)
        
        # Unique filename 
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename

        async with aiofiles.open(file_path, 'wb', buffering=8192) as f:
            while chunk := await file.read(chunk_size):
                await f.write(chunk)

        upload_duration = (datetime.now() - start_time).total_seconds()

        file_info = FileInfo(
            filename=safe_filename,
            size=file_path.stat().st_size,
            storage_location=str(file_path),
            upload_date=start_time.strftime("%Y-%m-%d %H:%M:%S"),
            upload_duration=round(upload_duration, 2)  # Duration in seconds, rounded to 2 decimal places
        )

        background_tasks.add_task(save_file_info, file_info)
        background_tasks.add_task(flush_buffer)  # Ensure data is written even if buffer isn't full

        return JSONResponse(
            status_code=201,
            content={"message": "File uploaded successfully", "file_info": file_info.dict()}
        )

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@data_router.get("/", response_model=List[FileInfo])
async def list_files():

    try:
        files = []
        index_path = UPLOAD_DIR / "file_index.json"
        
        if index_path.exists():
            async with aiofiles.open(index_path, "r", buffering=8192) as f:
                async for line in f:
                    if line.strip():
                        files.append(json.loads(line))
        
        return files

    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file list")