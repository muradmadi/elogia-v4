"""Health check router for API status monitoring."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/status")
async def health_status() -> dict:
    """
    Basic health check endpoint.
    
    Returns:
        dict: Status information about the API.
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "app_env": settings.app_env,
    }


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)) -> dict:
    """
    Readiness check endpoint that verifies database connectivity.
    
    Args:
        db: Async database session.
    
    Returns:
        dict: Readiness status with database connection info.
    """
    try:
        # Test database connection
        await db.execute("SELECT 1")
        return {
            "status": "ready",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "database": "disconnected",
            "error": str(e),
        }


@router.get("/live")
async def liveness_check() -> dict:
    """
    Liveness check endpoint for Kubernetes/Docker health probes.
    
    Returns:
        dict: Liveness status.
    """
    return {"status": "alive"}
