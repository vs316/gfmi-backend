from fastapi import APIRouter, HTTPException, Body
from app.models.filter import FilterOptions
from app.core.config import settings
from typing import List, Optional, Dict
import logging

# Conditionally import the service based on configuration
if settings.USE_LOCAL_DATA:
    from app.services.local_data_service import LocalDataService as DataService
else:
    from app.services.dremio_service import DremioService as DataService

router = APIRouter()
logger = logging.getLogger(__name__)


def get_data_service():
    """Dependency to get data service"""
    if settings.USE_LOCAL_DATA:
        return DataService(csv_path=settings.LOCAL_DATA_PATH)
    else:
        return DataService()


@router.get("/options", response_model=FilterOptions)
async def get_filter_options():
    """Get all available filter options without any filters applied"""
    try:
        data_service = get_data_service()
        options = data_service.get_filter_options()

        logger.info(f"Returning filter options with {len(options.msl_names)} MSL names")

        return options
    except Exception as e:
        logger.error(f"Error in get_filter_options endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/progressive")
async def get_progressive_filters(
    applied_filters: Dict[str, List[str]] = Body(...),
    target_filter: Optional[str] = Body(None),
):
    """Get progressive filter options based on currently applied filters

    This endpoint allows filtering options to update dynamically based on
    other selected filters, providing a progressive disclosure UX.
    """
    try:
        data_service = get_data_service()

        if target_filter:
            # Get options for a specific filter field
            options = data_service.get_progressive_filter_options(
                target_filter, applied_filters
            )
            return {target_filter: options}
        else:
            # Get all filter options based on current selections
            return data_service.get_filter_options(applied_filters)

    except Exception as e:
        logger.error(f"Error in get_progressive_filters endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
