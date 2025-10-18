from typing import List, Optional, Dict
from fastapi import APIRouter, HTTPException, Query, Body
from app.models.filter import SurveyFilter, FilterOptions
from app.core.config import settings
import logging

# Conditionally import the service based on configuration
if settings.USE_LOCAL_DATA:
    from app.services.local_data_service import LocalDataService as DataService
else:
    from app.services.dremio_service import DremioService as DataService

from app.services.air_api_service import air_api_service

router = APIRouter()
logger = logging.getLogger(__name__)


def get_data_service():
    """Dependency to get data service"""
    if settings.USE_LOCAL_DATA:
        return DataService(csv_path=settings.LOCAL_DATA_PATH)
    else:
        return DataService()


@router.get("/", response_model=dict)
async def get_surveys(
    # Geographic filters
    country_geo_ids: Optional[List[str]] = Query(default=None),
    territories: Optional[List[str]] = Query(default=None),
    regions: Optional[List[str]] = Query(default=None),
    # Personnel filters
    msl_names: Optional[List[str]] = Query(default=None),
    titles: Optional[List[str]] = Query(default=None),
    departments: Optional[List[str]] = Query(default=None),
    user_types: Optional[List[str]] = Query(default=None),
    # Survey filters
    survey_names: Optional[List[str]] = Query(default=None),
    questions: Optional[List[str]] = Query(default=None),
    # Medical filters
    products: Optional[List[str]] = Query(default=None),
    product_expertise: Optional[List[str]] = Query(default=None),
    tumor_types: Optional[List[str]] = Query(default=None),
    # HCP filters
    account_names: Optional[List[str]] = Query(default=None),
    institutions: Optional[List[str]] = Query(default=None),
    specialties: Optional[List[str]] = Query(default=None),
    practice_settings: Optional[List[str]] = Query(default=None),
    # Event filters
    channels: Optional[List[str]] = Query(default=None),
    assignment_types: Optional[List[str]] = Query(default=None),
    # Pagination
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=1000),
):
    """Get surveys with multiple filter support"""
    try:
        filters = SurveyFilter(
            country_geo_ids=country_geo_ids or [],
            territories=territories or [],
            regions=regions or [],
            msl_names=msl_names or [],
            titles=titles or [],
            departments=departments or [],
            user_types=user_types or [],
            survey_names=survey_names or [],
            questions=questions or [],
            products=products or [],
            product_expertise=product_expertise or [],
            tumor_types=tumor_types or [],
            account_names=account_names or [],
            institutions=institutions or [],
            specialties=specialties or [],
            practice_settings=practice_settings or [],
            channels=channels or [],
            assignment_types=assignment_types or [],
            page=page,
            size=size,
        )

        logger.info(f"Received filters: {filters.dict(exclude_unset=True)}")

        data_service = get_data_service()
        result = data_service.get_surveys(filters)

        logger.info(
            f"Returning {len(result['surveys'])} surveys out of {result['total']} total"
        )

        return result

    except Exception as e:
        logger.error(f"Error in get_surveys endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{survey_id}")
async def get_survey(survey_id: str):
    """Get specific survey by ID"""
    try:
        data_service = get_data_service()
        result = data_service.get_survey_by_id(survey_id)

        if not result:
            raise HTTPException(status_code=404, detail="Survey not found")

        return {"data": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_survey endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
async def chat_with_data(
    query: str = Body(..., embed=True),
    filters: Optional[Dict[str, List[str]]] = Body(default=None, embed=True),
):
    """Send a natural language query to the AI-API service"""
    try:
        response = await air_api_service.send_chat_query(query, filters)
        return response

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
