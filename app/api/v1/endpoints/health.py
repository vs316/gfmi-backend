import logging
from fastapi import APIRouter, HTTPException
from app.core.config import settings

# Conditionally import the service based on configuration
if settings.USE_LOCAL_DATA:
    from app.services.local_data_service import LocalDataService as DataService
else:
    from app.services.dremio_service import DremioService as DataService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_data_service():
    """Get the appropriate data service based on configuration"""
    if settings.USE_LOCAL_DATA:
        return DataService(csv_path=settings.LOCAL_DATA_PATH)
    else:
        return DataService()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        data_service = get_data_service()

        # Try to get a count of records
        filters_from_zero = {"page": 1, "size": 1}

        if settings.USE_LOCAL_DATA:
            from app.models.filter import SurveyFilter

            result = data_service.get_surveys(SurveyFilter(**filters_from_zero))
            total_records = result.get("total", 0)
        else:
            # For Dremio, we'd need to implement a similar check
            total_records = None

        return {
            "status": "healthy",
            "mode": "Local CSV" if settings.USE_LOCAL_DATA else "Dremio",
            "data_source": (
                settings.LOCAL_DATA_PATH if settings.USE_LOCAL_DATA else "Dremio"
            ),
            "total_records": total_records,
        }

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")


@router.get("/")
async def health_check_root():
    """Alternative health check at root of health router"""
    return await health_check()
