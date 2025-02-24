import os
import uuid
import json
import aiofiles
from typing import List, Dict
from pathlib import Path
from datetime import datetime
from logs.logger import logger
from fastapi.responses import JSONResponse
from models.file_info import FileInfo
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form, Body

upload_router = APIRouter()
data_router = APIRouter()

UPLOAD_DIR = Path("storage")
ALLOWED_EXTENSIONS = {'.txt', '.pdf', '.doc', '.docx', '.csv', '.dat', '.mp4', '.wav'}
BUFFER_SIZE = 100 
file_info_buffer = []

active_uploads: Dict[str, dict] = {}

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
    
    file_info_buffer.append(json.dumps(file_info.model_dump()))
    
    if len(file_info_buffer) >= BUFFER_SIZE:
        await flush_buffer()


def get_optimal_chunk_size(file_size: int) -> int:

    MIN_CHUNK = 5 * 1024 * 1024    
    MAX_CHUNK = 20 * 1024 * 1024   
    DEFAULT_CHUNK = 8 * 1024 * 1024  
    
    if not file_size:
        return DEFAULT_CHUNK
        
    if file_size <= 2 * 1024 * 1024 * 1024:    # 2GB
        return MIN_CHUNK
    elif file_size >= 8 * 1024 * 1024 * 1024:  # 8GB
        return MAX_CHUNK
    else:
        return min(MAX_CHUNK, max(MIN_CHUNK, file_size // 500))


@upload_router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    client_id: str = Form(None),
    timestamp: str = Form(None),
    file_creation_time: str = Form(None),
    creation_duration: float = Form(None),
    background_tasks: BackgroundTasks = None
):
    try:
        start_time = datetime.now()
        
        if timestamp is None:
            timestamp = start_time.strftime("%Y%m%d_%H%M%S")
        if client_id is None:
            client_id = "default_client"
        if file_creation_time is None:
            file_creation_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
        if creation_duration is None:
            creation_duration = 0.0

        if not is_valid_extension(file.filename):
            logger.error(f"Invalid file extension: {file.filename}")
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {ALLOWED_EXTENSIONS}"
            )

        try:
            file_size = file.size  
        except AttributeError:
            file_size = 0  
            logger.warning("Could not determine file size, using default chunk size")

        chunk_size = get_optimal_chunk_size(file_size)
        

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
            upload_duration=round(upload_duration, 2),
            file_creation_time=file_creation_time,
            creation_duration=creation_duration
        )

        background_tasks.add_task(save_file_info, file_info)
        background_tasks.add_task(flush_buffer) 

        return JSONResponse(
            status_code=201,
            content={"message": "File uploaded successfully", "file_info": file_info.model_dump()}
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
                        file_info = json.loads(line)
                        # If there's a newer version of the same file, skip the older one
                        if not any(f['filename'] == file_info['filename'] and 
                                 f['upload_date'] > file_info['upload_date'] for f in files):
                            files = [f for f in files if f['filename'] != file_info['filename']]
                            files.append(file_info)
        
        return files

    except Exception as e:
        logger.error(f"Failed to list files: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file list")


@upload_router.post("/init")
async def initialize_upload(upload_info: dict = Body(...), background_tasks: BackgroundTasks = None):
    upload_id = str(uuid.uuid4())
    temp_dir = UPLOAD_DIR / "temp" / upload_id
    os.makedirs(temp_dir, exist_ok=True)
    
    file_info = FileInfo(
        filename=upload_info['filename'],
        size=upload_info['total_size'],
        storage_location=str(UPLOAD_DIR / upload_info['filename']),
        upload_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        upload_duration=0.0,
        file_creation_time=upload_info['file_creation_time'],
        client_id=upload_info['client_id'],
        status="pending"
    )
    
    active_uploads[upload_id] = {
        'filename': upload_info['filename'],
        'total_size': upload_info['total_size'],
        'chunks_received': 0,
        'temp_dir': temp_dir,
        'client_id': upload_info['client_id'],
        'timestamp': upload_info['timestamp'],
        'file_creation_time': upload_info['file_creation_time'],
        'file_info': file_info
    }
    
    # Save the pending file info
    background_tasks.add_task(save_file_info, file_info)
    background_tasks.add_task(flush_buffer)
    
    return {"upload_id": upload_id}

@upload_router.post("/chunk")
async def upload_chunk(
    chunk: bytes = File(...),
    chunk_number: int = Form(...),
    upload_id: str = Form(...)
):
    if upload_id not in active_uploads:
        raise HTTPException(status_code=400, detail="Invalid upload ID")
    
    upload_info = active_uploads[upload_id]
    chunk_path = upload_info['temp_dir'] / f"chunk_{chunk_number}"
    
    async with aiofiles.open(chunk_path, 'wb') as f:
        await f.write(chunk)
    
    upload_info['chunks_received'] += 1
    
    return {"status": "success"}

@upload_router.post("/finalize")
async def finalize_upload(
    upload_data: dict = Body(...),
    background_tasks: BackgroundTasks = None
):
    upload_id = upload_data['upload_id']
    if upload_id not in active_uploads:
        raise HTTPException(status_code=400, detail="Invalid upload ID")
    
    upload_info = active_uploads[upload_id]
    final_path = UPLOAD_DIR / upload_info['filename']
    
    async with aiofiles.open(final_path, 'wb') as final_file:
        chunk_files = sorted(upload_info['temp_dir'].glob("chunk_*"))
        for chunk_path in chunk_files:
            async with aiofiles.open(chunk_path, 'rb') as chunk_file:
                await final_file.write(await chunk_file.read())
    
    for chunk_file in chunk_files:
        os.remove(chunk_file)
    os.rmdir(upload_info['temp_dir'])
    

    file_info = FileInfo(
        filename=upload_info['filename'],
        size=os.path.getsize(final_path),
        storage_location=str(final_path),
        upload_date=upload_info['file_info'].upload_date,  
        upload_duration=upload_data.get('upload_duration', 0),
        file_creation_time=upload_info['file_creation_time'],
        client_id=upload_info['client_id'],
        status="completed"
    )
    
    background_tasks.add_task(save_file_info, file_info)
    background_tasks.add_task(flush_buffer)
    
    del active_uploads[upload_id]
    
    return JSONResponse(
        status_code=201,
        content={"message": "File uploaded successfully", "file_info": file_info.model_dump()}
    )