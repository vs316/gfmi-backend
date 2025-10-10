from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.models.survey import Survey, SurveyCreate, SurveyUpdate, SurveyListResponse
from app.models.filter import SurveyFilter
from app.services.survey_service import survey_service

router = APIRouter()


@router.post("/", response_model=Survey)
def create_survey(survey: SurveyCreate):

    try:
        return survey_service.create_survey(survey)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=SurveyListResponse)
def get_surveys(
    # Teams and Organizations
    msl_name: Optional[str] = Query(None, description="MSL Name"),
    title: Optional[str] = Query(None, description="Title"),
    department: Optional[str] = Query(None, description="Department"),
    user_type: Optional[str] = Query(None, description="User Type"),
    # Geographic
    region: Optional[str] = Query(None, description="Region"),
    country_geo_id: Optional[str] = Query(None, description="Country/Geo ID"),
    territory: Optional[str] = Query(None, description="Territory"),
    # Medical
    response: Optional[str] = Query(None, description="Tumor Type/Response"),
    product: Optional[str] = Query(None, description="Product"),
    # Healthcare provider (HCP)
    account_name: Optional[str] = Query(None, description="Account Name"),
    company: Optional[str] = Query(None, description="Company"),
    name: Optional[str] = Query(None, description="Name"),
    usertype: Optional[str] = Query(None, description="User Type"),
    # Event & Engagement
    channels: Optional[str] = Query(None, description="Channels"),
    assignment_type: Optional[str] = Query(None, description="Assignment Type"),
    # Surveys
    survey_name: Optional[str] = Query(None, description="Survey Name"),
    question: Optional[str] = Query(None, description="Question"),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
):

    try:
        filters = SurveyFilter(
            msl_name=msl_name,
            title=title,
            department=department,
            user_type=user_type,
            region=region,
            country_geo_id=country_geo_id,
            territory=territory,
            response=response,
            product=product,
            account_name=account_name,
            company=company,
            name=name,
            usertype=usertype,
            channels=channels,
            assignment_type=assignment_type,
            survey_name=survey_name,
            question=question,
            page=page,
            size=size,
        )
        return survey_service.get_surveys(filters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{survey_id}", response_model=Survey)
def get_survey(survey_id: str):

    survey = survey_service.get_survey(survey_id)
    if not survey:
        raise HTTPException(status_code=404, detail="Survey not found")
    return survey


@router.put("/{survey_id}", response_model=Survey)
def update_survey(survey_id: str, survey_update: SurveyUpdate):

    try:
        survey = survey_service.update_survey(survey_id, survey_update)
        if not survey:
            raise HTTPException(status_code=404, detail="Survey not found")
        return survey
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{survey_id}")
def delete_survey(survey_id: str):

    try:
        success = survey_service.delete_survey(survey_id)
        if not success:
            raise HTTPException(status_code=404, detail="Survey not found")
        return {"message": "Survey deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
