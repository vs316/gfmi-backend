from pydantic import BaseModel
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
    msl_name: Optional[str] = None
    title: Optional[str] = None
    department: Optional[str] = None
    user_type: Optional[str] = None

    # Geographic
    region: Optional[str] = None
    country_geo_id: Optional[str] = None
    territory: Optional[str] = None

    # Medical
    response: Optional[str] = None  # tumor type
    product: Optional[str] = None

    # Healthcare provider (HCP)
    account_name: Optional[str] = None
    company: Optional[str] = None
    name: Optional[str] = None
    usertype: Optional[str] = None

    # Event & Engagement
    channels: Optional[str] = None
    assignment_type: Optional[str] = None

    # Surveys
    survey_name: Optional[str] = None
    question: Optional[str] = None

    # Pagination
    page: int = 1
    size: int = 50
