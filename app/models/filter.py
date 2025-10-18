from typing import List, Optional
from pydantic import BaseModel, Field


class SurveyFilter(BaseModel):
    # Geographic filters
    country_geo_ids: Optional[List[str]] = Field(
        default=None, description="List of country geo IDs"
    )
    territories: Optional[List[str]] = Field(
        default=None, description="List of territories"
    )
    regions: Optional[List[str]] = Field(default=None, description="List of regions")

    # Personnel filters
    msl_names: Optional[List[str]] = Field(
        default=None, description="List of MSL names"
    )
    titles: Optional[List[str]] = Field(default=None, description="List of titles")
    departments: Optional[List[str]] = Field(
        default=None, description="List of departments"
    )
    user_types: Optional[List[str]] = Field(
        default=None, description="List of user types"
    )

    # Survey filters
    survey_names: Optional[List[str]] = Field(
        default=None, description="List of survey names"
    )
    questions: Optional[List[str]] = Field(
        default=None, description="List of questions"
    )

    # Medical filters
    products: Optional[List[str]] = Field(default=None, description="List of products")
    product_expertise: Optional[List[str]] = Field(
        default=None, description="List of product expertise"
    )
    tumor_types: Optional[List[str]] = Field(
        default=None, description="List of tumor types (responses)"
    )

    # HCP filters
    account_names: Optional[List[str]] = Field(
        default=None, description="List of account names"
    )
    institutions: Optional[List[str]] = Field(
        default=None, description="List of institutions (companies)"
    )
    specialties: Optional[List[str]] = Field(
        default=None, description="List of specialties"
    )
    practice_settings: Optional[List[str]] = Field(
        default=None, description="List of practice settings"
    )

    # Event filters
    channels: Optional[List[str]] = Field(default=None, description="List of channels")
    assignment_types: Optional[List[str]] = Field(
        default=None, description="List of assignment types"
    )

    # Pagination
    page: Optional[int] = Field(default=1, ge=1, description="Page number")
    size: Optional[int] = Field(default=50, ge=1, le=1000, description="Page size")


class FilterOptions(BaseModel):
    """Available filter options"""

    country_geo_ids: List[str] = Field(default_factory=list)
    territories: List[str] = Field(default_factory=list)
    regions: List[str] = Field(default_factory=list)
    msl_names: List[str] = Field(default_factory=list)
    titles: List[str] = Field(default_factory=list)
    departments: List[str] = Field(default_factory=list)
    user_types: List[str] = Field(default_factory=list)
    survey_names: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    products: List[str] = Field(default_factory=list)
    product_expertise_options: List[str] = Field(default_factory=list)
    responses: List[str] = Field(default_factory=list)
    account_names: List[str] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    channels: List[str] = Field(default_factory=list)
    assignment_types: List[str] = Field(default_factory=list)
