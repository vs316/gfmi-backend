# from typing import List
# from pydantic_settings import BaseSettings


# class Settings(BaseSettings):
#     PROJECT_NAME: str = "GFMI Insight Buddy API"
#     VERSION: str = "1.0.0"
#     API_V1_STR: str = "/api/v1"

#     # Database
#     DREMIO_HOST: str
#     DREMIO_PORT: int
#     DREMIO_USERNAME: str
#     DREMIO_PASSWORD: str
#     DREMIO_DATABASE: str

#     # Security
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

#     # CORS
#     ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

#     class Config:
#         env_file = ".env"


# settings = Settings()
from typing import List
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "GFMI Insight Buddy API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # For local testing, we don't need Dremio settings
    # These are only used when connecting to actual Dremio
    DREMIO_HOST: str = os.getenv("DREMIO_HOST", "localhost")
    DREMIO_PORT: int = int(os.getenv("DREMIO_PORT", "31010"))
    DREMIO_USERNAME: str = os.getenv("DREMIO_USERNAME", "user")
    DREMIO_PASSWORD: str = os.getenv("DREMIO_PASSWORD", "pass")
    DREMIO_DATABASE: str = os.getenv("DREMIO_DATABASE", "db")

    # Security (not needed for local testing but FastAPI expects them)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-for-local-testing")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # Dremio configuration
    DREMIO_SERVER: str = os.getenv("DREMIO_SERVER", "http://localhost:9047")
    DREMIO_TOKEN: str = os.getenv("DREMIO_TOKEN", "")
    DREMIO_TABLE_PATH: str = os.getenv(
        "DREMIO_TABLE_PATH",
        '"Global Development"."Business Applications"."Medical Affairs"."GFMI".p_med_affairs_crm_survey_details',
    )
    AIR_API_BASE_URL: str = os.getenv("AIR_API_BASE_URL", "http://localhost:8080")
    # Local testing flag
    USE_LOCAL_DATA: bool = os.getenv("USE_LOCAL_DATA", "true").lower() == "true"
    LOCAL_DATA_PATH: str = os.getenv("LOCAL_DATA_PATH", "data/survey_data.csv")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
