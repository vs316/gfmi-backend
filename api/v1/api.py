from fastapi import APIRouter
from api.v1.endpoints import surveys, filters

api_router = APIRouter()

api_router.include_router(surveys.router, prefix="/surveys", tags=["surveys"])
api_router.include_router(filters.router, prefix="/filters", tags=["filters"])
