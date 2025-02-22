from fastapi import APIRouter
from app.models.file import HealthResponse

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.
    
    Returns:
        HealthResponse: Health status of the service.
    """
    return HealthResponse()