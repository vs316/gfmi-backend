from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, List
from app.models.filter import FilterOptions
from app.services.filter_service import filter_service

router = APIRouter()


@router.get("/options", response_model=FilterOptions)
def get_filter_options():
    # \"\"\"Get all available filter options\"\"\"
    try:
        return filter_service.get_filter_options()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/related")
def get_related_filters(
    base_filter: str = Query(..., description="Base filter field name"),
    base_value: str = Query(..., description="Base filter value"),
) -> Dict[str, List[str]]:
    # \"\"\"Get related filter options based on a base filter selection\"\"\"
    try:
        return filter_service.get_related_filters(base_filter, base_value)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
