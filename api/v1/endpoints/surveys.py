# from fastapi import APIRouter, HTTPException, Query
# from typing import Optional, List
# from app.models.survey import Survey, SurveyCreate, SurveyUpdate, SurveyListResponse
# from app.models.filter import SurveyFilter
# from app.services.survey_service import survey_service

# router = APIRouter()


# @router.post("/", response_model=Survey)
# def create_survey(survey: SurveyCreate):
#     try:
#         return survey_service.create_survey(survey)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/", response_model=SurveyListResponse)
# def get_surveys(
#     # Teams and Organizations - Accept multiple values
#     msl_name: Optional[List[str]] = Query(None, description="MSL Name"),
#     title: Optional[List[str]] = Query(None, description="Title"),
#     department: Optional[List[str]] = Query(None, description="Department"),
#     user_type: Optional[List[str]] = Query(None, description="User Type"),
#     # Geographic
#     region: Optional[List[str]] = Query(None, description="Region"),
#     country_geo_id: Optional[List[str]] = Query(None, description="Country/Geo ID"),
#     territory: Optional[List[str]] = Query(None, description="Territory"),
#     # Medical
#     response: Optional[List[str]] = Query(None, description="Tumor Type/Response"),
#     product: Optional[List[str]] = Query(None, description="Product"),
#     # Healthcare provider (HCP)
#     account_name: Optional[List[str]] = Query(None, description="Account Name"),
#     company: Optional[List[str]] = Query(None, description="Company"),
#     name: Optional[List[str]] = Query(None, description="Name"),
#     usertype: Optional[List[str]] = Query(None, description="User Type"),
#     # Event & Engagement
#     channels: Optional[List[str]] = Query(None, description="Channels"),
#     assignment_type: Optional[List[str]] = Query(None, description="Assignment Type"),
#     # Surveys
#     survey_name: Optional[List[str]] = Query(None, description="Survey Name"),
#     question: Optional[str] = Query(
#         None, description="Question"
#     ),  # Keep as single value for LIKE search
#     # Pagination
#     page: int = Query(1, ge=1, description="Page number"),
#     size: int = Query(50, ge=1, le=1000, description="Page size"),
# ):
#     try:
#         filters = SurveyFilter(
#             msl_name=msl_name,
#             title=title,
#             department=department,
#             user_type=user_type,
#             region=region,
#             country_geo_id=country_geo_id,
#             territory=territory,
#             response=response,
#             product=product,
#             account_name=account_name,
#             company=company,
#             name=name,
#             usertype=usertype,
#             channels=channels,
#             assignment_type=assignment_type,
#             survey_name=survey_name,
#             question=question,
#             page=page,
#             size=size,
#         )
#         return survey_service.get_surveys(filters)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.get("/{survey_id}", response_model=Survey)
# def get_survey(survey_id: str):
#     survey = survey_service.get_survey(survey_id)
#     if not survey:
#         raise HTTPException(status_code=404, detail="Survey not found")
#     return survey


# @router.put("/{survey_id}", response_model=Survey)
# def update_survey(survey_id: str, survey_update: SurveyUpdate):
#     try:
#         survey = survey_service.update_survey(survey_id, survey_update)
#         if not survey:
#             raise HTTPException(status_code=404, detail="Survey not found")
#         return survey
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))


# @router.delete("/{survey_id}")
# def delete_survey(survey_id: str):
#     try:
#         success = survey_service.delete_survey(survey_id)
#         if not success:
#             raise HTTPException(status_code=404, detail="Survey not found")
#         return {"message": "Survey deleted successfully"}
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
# app/api/v1/endpoints/surveys.py
# from typing import List, Optional, Dict
# from fastapi import APIRouter, Depends, HTTPException, Query, Body
# from app.models.filter import SurveyFilter, FilterOptions
# from app.core.config import settings
# import logging

# # Conditionally import the service based on configuration
# if settings.USE_LOCAL_DATA:
#     from app.services.local_data_service import LocalDataService as DataService
# else:
#     from app.services.dremio_service import DremioService as DataService

# from app.services.air_api_service import air_api_service

# router = APIRouter()
# logger = logging.getLogger(__name__)


# def get_data_service():
#     """Dependency to get data service"""
#     if settings.USE_LOCAL_DATA:
#         return DataService(csv_path=settings.LOCAL_DATA_PATH)
#     else:
#         return DataService()


# @router.get("/", response_model=dict)
# async def get_surveys(
#     # Geographic filters
#     country_geo_id: Optional[List[str]] = Query(default=None),
#     territory: Optional[List[str]] = Query(default=None),
#     region: Optional[List[str]] = Query(default=None),
#     # Personnel filters
#     msl_name: Optional[List[str]] = Query(default=None),
#     msl_key: Optional[List[str]] = Query(default=None),
#     title: Optional[List[str]] = Query(default=None),
#     department: Optional[List[str]] = Query(default=None),
#     user_type: Optional[List[str]] = Query(default=None),
#     # Survey filters
#     survey_name: Optional[List[str]] = Query(default=None),
#     survey_key: Optional[List[str]] = Query(default=None),
#     question: Optional[List[str]] = Query(default=None),
#     # Medical filters
#     product: Optional[List[str]] = Query(default=None),
#     product_expertise: Optional[List[str]] = Query(default=None),
#     response: Optional[List[str]] = Query(default=None),
#     # HCP filters
#     account_name: Optional[List[str]] = Query(default=None),
#     account_key: Optional[List[str]] = Query(default=None),
#     company: Optional[List[str]] = Query(default=None),
#     # Event filters
#     channels: Optional[List[str]] = Query(default=None),
#     assignment_type: Optional[List[str]] = Query(default=None),
#     # Pagination
#     page: int = Query(default=1, ge=1),
#     size: int = Query(default=50, ge=1, le=1000),
# ):
#     """
#     Get surveys with multiple filter support

#     Examples:
#     - Single MSL: ?msl_name=carl.deluca@regeneron.com.mcrmeu
#     - Multiple MSLs: ?msl_name=carl.deluca@regeneron.com.mcrmeu&msl_name=johanna.hellinger@regeneron.com
#     - Multiple countries: ?country_geo_id=GB-UK-Ireland&country_geo_id=DE-Germany
#     """
#     try:
#         filters = SurveyFilter(
#             country_geo_id=country_geo_id or [],
#             territory=territory or [],
#             region=region or [],
#             msl_name=msl_name or [],
#             msl_key=msl_key or [],
#             title=title or [],
#             department=department or [],
#             user_type=user_type or [],
#             survey_name=survey_name or [],
#             survey_key=survey_key or [],
#             question=question or [],
#             product=product or [],
#             product_expertise=product_expertise or [],
#             response=response or [],
#             account_name=account_name or [],
#             account_key=account_key or [],
#             company=company or [],
#             channels=channels or [],
#             assignment_type=assignment_type or [],
#             page=page,
#             size=size,
#         )

#         data_service = get_data_service()
#         result = data_service.get_surveys(filters)
#         return result

#     except Exception as e:
#         logger.error(f"Error in get_surveys endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/filters/options", response_model=FilterOptions)
# async def get_filter_options():
#     """Get all available filter options without any filters applied"""
#     try:
#         data_service = get_data_service()
#         return data_service.get_filter_options()
#     except Exception as e:
#         logger.error(f"Error in get_filter_options endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/filters/progressive")
# async def get_progressive_filters(
#     applied_filters: Dict[str, List[str]] = Body(...),
#     target_filter: Optional[str] = Body(None),
# ):
#     """
#     Get progressive filter options based on currently applied filters
#     """
#     try:
#         data_service = get_data_service()

#         if target_filter:
#             # Get options for a specific filter
#             options = data_service.get_progressive_filter_options(
#                 target_filter, applied_filters
#             )
#             return {target_filter: options}
#         else:
#             # Get all filter options given the applied filters
#             return data_service.get_filter_options(applied_filters)

#     except Exception as e:
#         logger.error(f"Error in get_progressive_filters endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/{survey_id}")
# async def get_survey(survey_id: str):
#     """Get specific survey by ID"""
#     try:
#         data_service = get_data_service()

#         if settings.USE_LOCAL_DATA:
#             result = data_service.get_survey_by_id(survey_id)
#             if not result:
#                 raise HTTPException(status_code=404, detail="Survey not found")
#             return {"data": result}
#         else:
#             # Dremio version
#             safe_survey_id = survey_id.replace("'", "''")
#             query = f"""
#                 SELECT * FROM {data_service.table_path}
#                 WHERE survey_qstn_resp_id = '{safe_survey_id}'
#             """
#             result = data_service.api.execute_query(query)
#             if not result:
#                 raise HTTPException(status_code=404, detail="Survey not found")
#             return {"data": result}

#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error in get_survey endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))


# @router.post("/chat")
# async def chat_with_data(
#     query: str = Body(..., embed=True),
#     filters: Optional[Dict[str, List[str]]] = Body(default=None, embed=True),
# ):
#     """
#     Send a natural language query to the AI-API service along with selected filters
#     """
#     try:
#         response = await air_api_service.send_chat_query(query, filters)
#         return response

#     except Exception as e:
#         logger.error(f"Error in chat endpoint: {str(e)}")
#         raise HTTPException(status_code=500, detail=str(e))

# app/api/v1/endpoints/surveys.py
from typing import List, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, Query, Body
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
    country_geo_id: Optional[List[str]] = Query(default=None),
    territory: Optional[List[str]] = Query(default=None),
    region: Optional[List[str]] = Query(default=None),
    # Personnel filters
    msl_name: Optional[List[str]] = Query(default=None),
    msl_key: Optional[List[str]] = Query(default=None),
    title: Optional[List[str]] = Query(default=None),
    department: Optional[List[str]] = Query(default=None),
    user_type: Optional[List[str]] = Query(default=None),
    # Survey filters
    survey_name: Optional[List[str]] = Query(default=None),
    survey_key: Optional[List[str]] = Query(default=None),
    question: Optional[List[str]] = Query(default=None),
    # Medical filters
    product: Optional[List[str]] = Query(default=None),
    product_expertise: Optional[List[str]] = Query(default=None),
    response: Optional[List[str]] = Query(default=None),
    # HCP filters
    account_name: Optional[List[str]] = Query(default=None),
    account_key: Optional[List[str]] = Query(default=None),
    company: Optional[List[str]] = Query(default=None),
    # Event filters
    channels: Optional[List[str]] = Query(default=None),
    assignment_type: Optional[List[str]] = Query(default=None),
    # Pagination
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=1000),
):
    """
    Get surveys with multiple filter support

    Examples:
    - Single MSL: ?msl_name=carl.deluca@regeneron.com.mcrmeu
    - Multiple MSLs: ?msl_name=carl.deluca@regeneron.com.mcrmeu&msl_name=johanna.hellinger@regeneron.com
    - Multiple countries: ?country_geo_id=GB-UK-Ireland&country_geo_id=DE-Germany
    """
    try:
        filters = SurveyFilter(
            country_geo_id=country_geo_id or [],
            territory=territory or [],
            region=region or [],
            msl_name=msl_name or [],
            msl_key=msl_key or [],
            title=title or [],
            department=department or [],
            user_type=user_type or [],
            survey_name=survey_name or [],
            survey_key=survey_key or [],
            question=question or [],
            product=product or [],
            product_expertise=product_expertise or [],
            response=response or [],
            account_name=account_name or [],
            account_key=account_key or [],
            company=company or [],
            channels=channels or [],
            assignment_type=assignment_type or [],
            page=page,
            size=size,
        )

        data_service = get_data_service()
        result = data_service.get_surveys(filters)
        return result

    except Exception as e:
        logger.error(f"Error in get_surveys endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/filters/options", response_model=FilterOptions)
async def get_filter_options():
    """Get all available filter options without any filters applied"""
    try:
        data_service = get_data_service()
        return data_service.get_filter_options()
    except Exception as e:
        logger.error(f"Error in get_filter_options endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/filters/progressive")
async def get_progressive_filters(
    applied_filters: Dict[str, List[str]] = Body(...),
    target_filter: Optional[str] = Body(None),
):
    """
    Get progressive filter options based on currently applied filters
    """
    try:
        data_service = get_data_service()

        if target_filter:
            # Get options for a specific filter
            options = data_service.get_progressive_filter_options(
                target_filter, applied_filters
            )
            return {target_filter: options}
        else:
            # Get all filter options given the applied filters
            return data_service.get_filter_options(applied_filters)

    except Exception as e:
        logger.error(f"Error in get_progressive_filters endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{survey_id}")
async def get_survey(survey_id: str):
    """Get specific survey by ID"""
    try:
        data_service = get_data_service()

        if settings.USE_LOCAL_DATA:
            result = data_service.get_survey_by_id(survey_id)
            if not result:
                raise HTTPException(status_code=404, detail="Survey not found")
            return {"data": result}
        else:
            # Dremio version
            safe_survey_id = survey_id.replace("'", "''")
            query = f"""
                SELECT * FROM {data_service.table_path}
                WHERE survey_qstn_resp_id = '{safe_survey_id}'
            """
            result = data_service.api.execute_query(query)
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
    """
    Send a natural language query to the AI-API service along with selected filters
    """
    try:
        response = await air_api_service.send_chat_query(query, filters)
        return response

    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
