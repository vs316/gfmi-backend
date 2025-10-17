from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SurveyBase(BaseModel):
    survey_name: str
    question: Optional[str] = None
    response: Optional[str] = None
    msl_name: Optional[str] = None
    account_name: Optional[str] = None
    country_geo_id: Optional[str] = None
    territory: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None


class SurveyCreate(SurveyBase):
    survey_key: str
    msl_key: str
    account_key: Optional[str] = None
    src_cd: str
    assignment_type: str = "Territory_vod"
    channels: str = "CRM_vod"
    expired: str = "No"
    language: str = "en_US"
    status: str = "Published_vod"


class SurveyUpdate(BaseModel):
    survey_name: Optional[str] = None
    question: Optional[str] = None
    response: Optional[str] = None
    msl_name: Optional[str] = None
    account_name: Optional[str] = None
    territory: Optional[str] = None


class Survey(SurveyBase):
    survey_qstn_resp_id: str
    survey_qstn_resp_key: str
    survey_key: str
    msl_key: str
    src_cd: str
    account_key: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    useremail: Optional[str] = None
    usertype: Optional[str] = None
    company: Optional[str] = None
    name: Optional[str] = None

    class Config:
        from_attributes = True


class SurveyListResponse(BaseModel):
    surveys: List[Survey]
    total: int
    page: int
    size: int
    total_pages: int
