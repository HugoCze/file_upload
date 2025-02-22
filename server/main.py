
import os
import logging
import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.routers import health, files, uploads



logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(
    title="""Quantee - Task:
                File Upload Service""",
    description="My implementation of the file upload service",
    version="1.0.0",
)

app.include_router(health.router)
app.include_router(files.router)
app.include_router(uploads.router)

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting server with upload folder: {settings.UPLOAD_FOLDER}")
    logger.info(f"Maximum content length: {settings.MAX_CONTENT_LENGTH} bytes")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)