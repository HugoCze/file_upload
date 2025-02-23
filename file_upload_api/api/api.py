import json
import shutil
import asyncio
import logging
import aiofiles
from typing import List
from pathlib import Path
from datetime import datetime
from logs.logger import logger
from fastapi.responses import JSONResponse
from models.file_info import FileInfo, FileMetadata
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks

upload_router = APIRouter()
data_router = APIRouter()

UPLOAD_DIR = Path("storage")
CHUNK_SIZE = 1024 * 1024 
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.doc', '.docx', '.csv', '.dat'}


def is_valid_extension(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


async def save_file_info(file_info: FileInfo):
    async with aiofiles.open(UPLOAD_DIR / "file_index.json", "a+") as f:
        await f.write(json.dumps(file_info.dict()) + "\n")


@upload_router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    metadata: FileMetadata = None,
    background_tasks: BackgroundTasks = None
):

    try:
        if not is_valid_extension(file.filename):
            logger.error(f"Invalid file extension: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {ALLOWED_EXTENSIONS}"
            )

        # Unique filename 
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = UPLOAD_DIR / safe_filename

        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)

        file_info = FileInfo(
            filename=safe_filename,
            size=file_path.stat().st_size,
            storage_location=str(file_path),
            upload_time=datetime.now().isoformat(),
            metadata=metadata or FileMetadata(intended_location="/")
        )

        background_tasks.add_task(save_file_info, file_info)

        return JSONResponse(
            status_code=201,
            content={"message": "File uploaded successfully", "file_info": file_info.dict()}
        )

    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@data_router.get("/files/", response_model=List[FileInfo])
async def list_files():

    try:
        files = []
        index_path = UPLOAD_DIR / "file_index.json"
        
        if index_path.exists():
            async with aiofiles.open(index_path, "r") as f:
                async for line in f:
                    if line.strip():
                        files.append(json.loads(line))
        
        return files

    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file list")