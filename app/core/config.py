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


class Settings:
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


settings = Settings()
