# app/api/v1/api.py
from fastapi import APIRouter
from api.v1.endpoints import surveys, health

api_router = APIRouter()

# Include survey endpoints
api_router.include_router(surveys.router, prefix="/surveys", tags=["surveys"])

# Include health endpoints
api_router.include_router(health.router, prefix="/health", tags=["health"])
