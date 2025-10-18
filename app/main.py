from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.endpoints import health
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="GFMI Insight Buddy API - Survey Data Management",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(health.router, tags=["health"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    mode = "Local CSV" if settings.USE_LOCAL_DATA else "Dremio"

    return {
        "message": "GFMI Insight Buddy API",
        "version": settings.VERSION,
        "mode": mode,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "surveys": f"{settings.API_V1_STR}/surveys/",
            "filters": f"{settings.API_V1_STR}/filters/options",
        },
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(
        f"Starting GFMI API in {'LOCAL' if settings.USE_LOCAL_DATA else 'DREMIO'} mode"
    )
    uvicorn.run(
        "app.main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
