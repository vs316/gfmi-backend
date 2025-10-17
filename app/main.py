# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.core.config import settings
# from app.api.v1.api import api_router

# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     version=settings.VERSION,
#     openapi_url=f"{settings.API_V1_STR}/openapi.json",
# )

# # Set up CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=settings.ALLOWED_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(api_router, prefix=settings.API_V1_STR)


# @app.get("/")
# def read_root():
#     return {"message": "GFMI Insight Buddy API", "version": settings.VERSION}


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
import sqlite3
import os

from api.v1.api import api_router
from api.v1.endpoints import health
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# Simple app configuration
app = FastAPI(
    title="GFMI Insight Buddy API",
    version="1.0.0",
    description="Local testing API for GFMI Insight Buddy",
    openapi_url="/api/v1/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[
    #     "http://localhost:3000",
    #     "http://localhost:5173",
    #     "http://127.0.0.1:3000",
    #     "http://localhost:8080",
    #     "http://127.0.0.1:8080",
    # ],
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
DB_FILE = "gfmi_local.db"
app.include_router(api_router, prefix="/api/v1")

# Register health check at root level for Kubernetes
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GFMI Survey API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


def get_db_connection():
    if not os.path.exists(DB_FILE):
        raise HTTPException(
            status_code=500,
            detail=f"Database file not found: {DB_FILE}. Run 'python local_db_setup.py' first.",
        )

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# Root endpoint
@app.get("/")
def read_root():
    return {
        "message": "GFMI Insight Buddy API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "surveys": "/api/v1/surveys/",
            "filters": "/api/v1/filters/options",
        },
    }


# Health check
@app.get("/health")
def health_check():
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM survey_responses")
            result = cursor.fetchone()

            # Safely extract the count
            if result:
                count = int(result[0]) if result[0] is not None else 0
            else:
                count = 0

            print(f"🔍 DEBUG: Health check found {count} records (type: {type(count)})")

            return {
                "status": "healthy",
                "database": "connected",
                "records": count,  # Guaranteed to be an integer
                "database_file": os.path.abspath(DB_FILE),
            }
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return {"status": "error", "message": str(e), "records": 0}


# Get filter options
# @app.get("/api/v1/filters/options")
# def get_filter_options():
#     """Get all available filter options for the sidebar"""
#     try:
#         with get_db_connection() as conn:
#             filters = {}

#             # Define all filter fields based on your CSV structure
#             filter_fields = {
#                 # Teams and Organizations
#                 "msl_names": "msl_name",
#                 "titles": "title",
#                 "departments": "department",
#                 "user_types": "user_type",
#                 # Geographic
#                 "regions": "region",
#                 "countries": "country_geo_id",
#                 "territories": "territory",
#                 # Medical
#                 "tumor_types": "response",
#                 "products": "product",
#                 # Healthcare provider (HCP)
#                 "account_names": "account_name",
#                 "institutions": "company",
#                 "specialties": "usertype",
#                 # Event & Engagement
#                 "channels": "channels",
#                 "assignment_types": "assignment_type",
#                 # Surveys
#                 "survey_names": "survey_name",
#                 "questions": "question",
#             }

#             for filter_name, column_name in filter_fields.items():
#                 try:
#                     cursor = conn.execute(
#                         f"""
#                         SELECT DISTINCT "{column_name}"
#                         FROM survey_responses
#                         WHERE "{column_name}" IS NOT NULL
#                         AND "{column_name}" != ""
#                         ORDER BY "{column_name}"
#                     """
#                     )
#                     values = [row[0] for row in cursor.fetchall()]
#                     filters[filter_name] = values
#                 except Exception as e:
#                     print(f"Warning: Could not get values for {filter_name}: {e}")
#                     filters[filter_name] = []

#             return filters


#     except Exception as e:
#         raise HTTPException(
#             status_code=500, detail=f"Error getting filter options: {str(e)}"
#         )
@app.get("/api/v1/filters/options")
def get_filter_options():
    """Get all available filter options for the sidebar"""
    print("🔍 DEBUG: get_filter_options called")

    try:
        with get_db_connection() as conn:
            # Test connection first
            cursor = conn.execute("SELECT COUNT(*) FROM survey_responses")
            total_records = cursor.fetchone()[0]  # Fixed: Get first element
            print(f"🔍 DEBUG: Total records in DB: {total_records}")

            filters = {}

            # Countries - FIXED to get actual values
            cursor = conn.execute(
                """
                SELECT DISTINCT country_geo_id 
                FROM survey_responses 
                WHERE country_geo_id IS NOT NULL 
                AND country_geo_id != ""
                ORDER BY country_geo_id
            """
            )
            countries = [row[0] for row in cursor.fetchall()]  # Fixed: Access [0]
            print(f"🔍 DEBUG: Countries: {countries}")
            filters["countries"] = countries

            # MSL Names - FIXED
            cursor = conn.execute(
                """
                SELECT DISTINCT msl_name 
                FROM survey_responses 
                WHERE msl_name IS NOT NULL 
                AND msl_name != ""
                ORDER BY msl_name
            """
            )
            msl_names = [row[0] for row in cursor.fetchall()]  # Fixed: Access [0]
            print(f"🔍 DEBUG: MSL Names: {msl_names}")
            filters["msl_names"] = msl_names

            # Survey Names - FIXED
            cursor = conn.execute(
                """
                SELECT DISTINCT survey_name 
                FROM survey_responses 
                WHERE survey_name IS NOT NULL 
                AND survey_name != ""
                ORDER BY survey_name
            """
            )
            survey_names = [row[0] for row in cursor.fetchall()]  # Fixed: Access [0]
            print(f"🔍 DEBUG: Survey Names: {survey_names}")
            filters["survey_names"] = survey_names

            # Tumor Types - FIXED
            cursor = conn.execute(
                'SELECT DISTINCT response FROM survey_responses WHERE response IS NOT NULL AND response != ""'
            )
            tumor_types = [row[0] for row in cursor.fetchall()]
            filters["tumor_types"] = tumor_types

            # Account Names - FIXED
            cursor = conn.execute(
                'SELECT DISTINCT account_name FROM survey_responses WHERE account_name IS NOT NULL AND account_name != ""'
            )
            account_names = [row[0] for row in cursor.fetchall()]
            filters["account_names"] = account_names

            # Titles - FIXED
            cursor = conn.execute(
                'SELECT DISTINCT title FROM survey_responses WHERE title IS NOT NULL AND title != ""'
            )
            titles = [row[0] for row in cursor.fetchall()]
            filters["titles"] = titles

            # Territories - FIXED
            cursor = conn.execute(
                'SELECT DISTINCT territory FROM survey_responses WHERE territory IS NOT NULL AND territory != ""'
            )
            territories = [row[0] for row in cursor.fetchall()]
            filters["territories"] = territories

            # Add survey questions to your existing function
            cursor = conn.execute(
                'SELECT DISTINCT question FROM survey_responses WHERE question IS NOT NULL AND question != "" LIMIT 20'
            )
            questions = [row[0] for row in cursor.fetchall()]
            filters["questions"] = questions
            print(f"🔍 DEBUG: Found {len(questions)} questions")

            # Add empty arrays for missing fields
            filters.update(
                {
                    "departments": [],
                    "user_types": [],
                    "regions": [],
                    "products": [],
                    "institutions": [],
                    "specialties": [],
                    "channels": [],
                    "assignment_types": [],
                    "questions": [],
                }
            )

            print(f"🔍 DEBUG: SUCCESS - Returning real data!")
            return filters

    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Get surveys with filtering and pagination
@app.get("/api/v1/surveys/")
def get_surveys(
    # Teams and Organizations
    msl_name: Optional[str] = Query(None, description="MSL Name"),
    title: Optional[str] = Query(None, description="Title"),
    department: Optional[str] = Query(None, description="Department"),
    user_type: Optional[str] = Query(None, description="User Type"),
    # Geographic
    region: Optional[str] = Query(None, description="Region"),
    country_geo_id: Optional[str] = Query(None, description="Country/Geo ID"),
    territory: Optional[str] = Query(None, description="Territory"),
    # Medical
    response: Optional[str] = Query(None, description="Tumor Type/Response"),
    product: Optional[str] = Query(None, description="Product"),
    # Healthcare provider (HCP)
    account_name: Optional[str] = Query(None, description="Account Name"),
    company: Optional[str] = Query(None, description="Company"),
    name: Optional[str] = Query(None, description="Name"),
    usertype: Optional[str] = Query(None, description="User Type"),
    # Event & Engagement
    channels: Optional[str] = Query(None, description="Channels"),
    assignment_type: Optional[str] = Query(None, description="Assignment Type"),
    # Surveys
    survey_name: Optional[str] = Query(None, description="Survey Name"),
    question: Optional[str] = Query(None, description="Question"),
    # Pagination
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=1000, description="Page size"),
):
    """Get surveys with comprehensive filtering and pagination"""
    try:
        with get_db_connection() as conn:
            # Build WHERE clause dynamically
            where_conditions = []
            params = []

            # Map all possible filters
            filter_mapping = {
                "msl_name": msl_name,
                "title": title,
                "department": department,
                "user_type": user_type,
                "region": region,
                "country_geo_id": country_geo_id,
                "territory": territory,
                "response": response,
                "product": product,
                "account_name": account_name,
                "company": company,
                "name": name,
                "usertype": usertype,
                "channels": channels,
                "assignment_type": assignment_type,
                "survey_name": survey_name,
                "question": question,
            }

            for field, value in filter_mapping.items():
                if value:
                    if field == "question":
                        # Use LIKE for question text search
                        where_conditions.append(f'"{field}" LIKE ?')
                        params.append(f"%{value}%")
                    else:
                        where_conditions.append(f'"{field}" = ?')
                        params.append(value)

            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)

            # Count total records
            count_query = f"SELECT COUNT(*) FROM survey_responses {where_clause}"
            cursor = conn.execute(count_query, params)
            total = cursor.fetchone()[0]

            # Calculate pagination
            offset = (page - 1) * size
            total_pages = (total + size - 1) // size if total > 0 else 0

            # Get paginated results
            query = f"""
                SELECT * FROM survey_responses 
                {where_clause}
                ORDER BY survey_qstn_resp_id
                LIMIT {size} OFFSET {offset}
            """

            cursor = conn.execute(query, params)
            surveys = [dict(row) for row in cursor.fetchall()]

            return {
                "surveys": surveys,
                "total": total,
                "page": page,
                "size": size,
                "total_pages": total_pages,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting surveys: {str(e)}")


# Get specific survey by ID
@app.get("/api/v1/surveys/{survey_id}")
def get_survey(survey_id: str):
    """Get a specific survey by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM survey_responses WHERE survey_qstn_resp_id = ?",
                (survey_id,),
            )
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=404, detail="Survey not found")

            return dict(row)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting survey: {str(e)}")


# Create new survey (for testing CRUD)
@app.post("/api/v1/surveys/")
def create_survey(survey_data: Dict[str, Any]):
    """Create a new survey response"""
    try:
        with get_db_connection() as conn:
            # Get all column names from the table
            cursor = conn.execute("PRAGMA table_info(survey_responses)")
            columns = [row[1] for row in cursor.fetchall()]

            # Prepare data for insertion
            values = []
            placeholders = []
            column_names = []

            for column in columns:
                if column in survey_data:
                    column_names.append(f'"{column}"')
                    placeholders.append("?")
                    values.append(survey_data[column])

            if not column_names:
                raise HTTPException(status_code=400, detail="No valid data provided")

            # Insert the new survey
            insert_query = f"""
                INSERT INTO survey_responses ({", ".join(column_names)})
                VALUES ({", ".join(placeholders)})
            """

            cursor = conn.execute(insert_query, values)
            conn.commit()

            # Return the created survey
            if "survey_qstn_resp_id" in survey_data:
                return get_survey(survey_data["survey_qstn_resp_id"])
            else:
                return {
                    "message": "Survey created successfully",
                    "row_id": cursor.lastrowid,
                }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating survey: {str(e)}")


# Update survey (for testing CRUD)
@app.put("/api/v1/surveys/{survey_id}")
def update_survey(survey_id: str, survey_data: Dict[str, Any]):
    """Update a survey"""
    try:
        with get_db_connection() as conn:
            # Check if survey exists
            cursor = conn.execute(
                "SELECT COUNT(*) FROM survey_responses WHERE survey_qstn_resp_id = ?",
                (survey_id,),
            )
            if cursor.fetchone()[0] == 0:
                raise HTTPException(status_code=404, detail="Survey not found")

            # Build UPDATE query
            set_conditions = []
            params = []

            for field, value in survey_data.items():
                if field != "survey_qstn_resp_id":  # Don't update the ID
                    set_conditions.append(f'"{field}" = ?')
                    params.append(value)

            if not set_conditions:
                raise HTTPException(status_code=400, detail="No valid data to update")

            params.append(survey_id)

            update_query = f"""
                UPDATE survey_responses 
                SET {", ".join(set_conditions)}
                WHERE survey_qstn_resp_id = ?
            """

            conn.execute(update_query, params)
            conn.commit()

            return get_survey(survey_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating survey: {str(e)}")


# Delete survey (for testing CRUD)
@app.delete("/api/v1/surveys/{survey_id}")
def delete_survey(survey_id: str):
    """Delete a survey"""
    try:
        with get_db_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM survey_responses WHERE survey_qstn_resp_id = ?",
                (survey_id,),
            )

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Survey not found")

            conn.commit()
            return {"message": "Survey deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting survey: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
