from pydantic import BaseModel, Field
from typing import Optional, List


class FilterOptions(BaseModel):
    # Teams and Organizations
    msl_names: List[str] = []
    titles: List[str] = []
    departments: List[str] = []
    user_types: List[str] = []

    # Geographic
    regions: List[str] = []
    countries: List[str] = []
    territories: List[str] = []

    # Medical
    tumor_types: List[str] = []
    products: List[str] = []

    # Healthcare provider (HCP)
    account_names: List[str] = []
    institutions: List[str] = []
    specialties: List[str] = []

    # Event & Engagement
    channels: List[str] = []
    assignment_types: List[str] = []

    # Surveys
    survey_names: List[str] = []
    questions: List[str] = []


class SurveyFilter(BaseModel):
    # Teams and Organizations
    msl_name: Optional[List[str]] = None
    title: Optional[List[str]] = None
    department: Optional[List[str]] = None
    user_type: Optional[List[str]] = None

    # Geographic
    region: Optional[List[str]] = None
    country_geo_id: Optional[List[str]] = None
    territory: Optional[List[str]] = None

    # Medical
    response: Optional[List[str]] = None
    product: Optional[List[str]] = None

    # Healthcare provider (HCP)
    account_name: Optional[List[str]] = None
    company: Optional[List[str]] = None
    name: Optional[List[str]] = None
    usertype: Optional[List[str]] = None

    # Event & Engagement
    channels: Optional[List[str]] = None
    assignment_type: Optional[List[str]] = None

    # Surveys
    survey_name: Optional[List[str]] = None
    question: Optional[str] = None  # Keep as string for LIKE search

    # Pagination
    page: int = Field(1, ge=1)
    size: int = Field(50, ge=1, le=1000)
