from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SurveyFilter(BaseModel):
    # Geographic filters - support multiple values
    country_geo_id: Optional[List[str]] = Field(
        default=None, description="List of country geo IDs"
    )
    territory: Optional[List[str]] = Field(
        default=None, description="List of territories"
    )
    region: Optional[List[str]] = Field(default=None, description="List of regions")

    # Personnel filters - support multiple values
    msl_name: Optional[List[str]] = Field(default=None, description="List of MSL names")
    msl_key: Optional[List[str]] = Field(default=None, description="List of MSL keys")
    title: Optional[List[str]] = Field(default=None, description="List of titles")
    department: Optional[List[str]] = Field(
        default=None, description="List of departments"
    )
    user_type: Optional[List[str]] = Field(
        default=None, description="List of user types"
    )

    # Survey filters - support multiple values
    survey_name: Optional[List[str]] = Field(
        default=None, description="List of survey names"
    )
    survey_key: Optional[List[str]] = Field(
        default=None, description="List of survey keys"
    )
    question: Optional[List[str]] = Field(default=None, description="List of questions")

    # Medical filters - support multiple values
    product: Optional[List[str]] = Field(default=None, description="List of products")
    product_expertise: Optional[List[str]] = Field(
        default=None, description="List of product expertise"
    )
    response: Optional[List[str]] = Field(
        default=None, description="List of tumor types/responses"
    )

    # HCP filters - support multiple values
    account_name: Optional[List[str]] = Field(
        default=None, description="List of account names"
    )
    account_key: Optional[List[str]] = Field(
        default=None, description="List of account keys"
    )
    company: Optional[List[str]] = Field(default=None, description="List of companies")

    # Event filters - support multiple values
    channels: Optional[List[str]] = Field(default=None, description="List of channels")
    assignment_type: Optional[List[str]] = Field(
        default=None, description="List of assignment types"
    )

    # Pagination
    page: Optional[int] = Field(default=1, ge=1, description="Page number")
    size: Optional[int] = Field(default=50, ge=1, le=1000, description="Page size")


class FilterOptions(BaseModel):
    """Available filter options"""

    country_geo_ids: List[str]
    territories: List[str]
    regions: List[str]
    msl_names: List[str]
    titles: List[str]
    departments: List[str]
    user_types: List[str]
    survey_names: List[str]
    questions: List[str]
    products: List[str]
    product_expertise_options: List[str]
    responses: List[str]
    account_names: List[str]
    companies: List[str]
    channels: List[str]
    assignment_types: List[str]
