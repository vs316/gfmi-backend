# app/api/v1/endpoints/health.py
from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.core.config import settings
from app.services.dremio_service import DremioService
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness/readiness probes

    Returns:
        200 OK if service is healthy
        503 Service Unavailable if service is unhealthy
    """
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "gfmi-backend",
            "version": "1.0.0",
        }

        return health_status

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service Unavailable")


@router.get("/ready")
async def readiness_check():
    """
    Readiness check endpoint for Kubernetes

    Checks if the service can handle requests by verifying:
    - Dremio connection

    Returns:
        200 OK if service is ready
        503 Service Unavailable if service is not ready
    """
    try:
        # Test Dremio connection
        dremio_service = DremioService()

        # Simple query to verify connection
        test_query = (
            f"SELECT 1 as health_check FROM {dremio_service.table_path} LIMIT 1"
        )
        dremio_service.api.execute_query(test_query)

        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {"dremio": "connected"},
        }

    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        raise HTTPException(
            status_code=503, detail={"status": "not ready", "error": str(e)}
        )
