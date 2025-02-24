import uvicorn
from pathlib import Path
from fastapi import FastAPI
from contextlib import asynccontextmanager
from logs.logger import logger
from fastapi.middleware.cors import CORSMiddleware
from api.api import upload_router, data_router, health_router



UPLOAD_DIR = Path("storage")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Creates necessary directories and performs startup checks.
    """
    UPLOAD_DIR.mkdir(exist_ok=True)
    logger.info("Storage directory initialized")
    
    yield
    
    logger.info("Shutting down application")


app = FastAPI(
    title="File Upload Service",
    description="Service for handling large file uploads with metadata",
    version="1.0.0",
    lifespan=lifespan
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api/uploads", tags=["uploads"])
app.include_router(data_router, prefix="/api/data", tags=["data"])
app.include_router(health_router, prefix="/api/health", tags=["health"])

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )