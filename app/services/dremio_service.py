import requests
import json
import time
from typing import Dict, Any, List, Optional
from app.core.config import settings
import logging

from app.models.filter import FilterOptions, SurveyFilter

logger = logging.getLogger(__name__)


class DremioAPI:
    def __init__(self, server: str, token: str):
        self.server = server
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "content-type": "application/json",
        }

    def _api_get(self, endpoint: str):
        response = requests.get(
            f"{self.server}/api/v3/{endpoint}", headers=self.headers, timeout=30
        )
        response.raise_for_status()
        return response.json()

    def _api_post(self, endpoint: str, body: Optional[Dict[str, Any]] = None):
        response = requests.post(
            f"{self.server}/api/v3/{endpoint}",
            headers=self.headers,
            data=json.dumps(body) if body else None,
            timeout=30,
        )
        response.raise_for_status()
        return response.json() if response.text else None

    def execute_query(self, sql_query: str, limit: int = 100):
        try:
            logger.info(f"Executing Dremio query: {sql_query}")

            # Submit the SQL query
            response = self._api_post("sql", body={"sql": sql_query})
            job_id = response["id"]
            logger.info(f"Job submitted with ID: {job_id}")

            # Poll for job completion
            response = self._api_get(f"job/{job_id}/")
            job_status = response["jobState"]

            while job_status not in ["COMPLETED", "FAILED", "CANCELED"]:
                time.sleep(1)
                response = self._api_get(f"job/{job_id}/")
                job_status = response["jobState"]
                logger.info(f"Job status: {job_status}")

            if job_status == "FAILED":
                error_msg = response.get("errorMessage", "Unknown error")
                raise Exception(f"SQL Query failed: {error_msg}")

            if job_status == "CANCELED":
                raise Exception("SQL Query was canceled")

            # Get results
            row_count = response["rowCount"]
            results = []
            offset = 0

            while offset < row_count:
                current_limit = min(limit, row_count - offset)
                response = self._api_get(
                    f"job/{job_id}/results?offset={offset}&limit={current_limit}"
                )
                results.extend(response["rows"])
                offset += limit

            logger.info(f"Retrieved {len(results)} rows")
            return results

        except Exception as e:
            logger.error(f"Error executing Dremio query: {str(e)}")
            logger.error(f"Query: {sql_query}")
            raise


class DremioService:
    def __init__(self):
        self.api = DremioAPI(server=settings.DREMIO_SERVER, token=settings.DREMIO_TOKEN)
        self.table_path = settings.DREMIO_TABLE_PATH

    # Map filter parameter names to actual database column names
    FILTER_FIELD_MAPPING = {
        "msl_names": "msl_name",  # Use msl_name column (contains emails with .mcrmeu suffix)
        "titles": "title",
        "departments": "department",
        "user_types": "user_type",
        "regions": "region",
        "country_geo_ids": "country_geo_id",
        "territories": "territory",
        "tumor_types": "response",
        "survey_names": "survey_name",
        "questions": "question",
        "account_names": "account_name",
        "products": "product",
        "product_expertise": "product_expertise",
        "channels": "channels",
        "assignment_types": "assignment_type",
        "specialties": "specialty",
        "practice_settings": "practice_setting",
        "institutions": "company",
    }

    def build_where_clause(self, filters: Dict[str, Any]) -> str:
        """Build WHERE clause from filters, supporting multiple values
        
        Maps filter parameter names to actual database column names
        """
        conditions = []

        for param_name, values in filters.items():
            if not values or len(values) == 0:
                continue

            # Get the actual database column name
            db_column = self.FILTER_FIELD_MAPPING.get(param_name, param_name)
            
            # Escape single quotes in values
            escaped_values = [str(v).replace("'", "''") for v in values]

            # Handle multiple values with IN clause
            if len(escaped_values) == 1:
                conditions.append(f'"{db_column}" = \'{escaped_values[0]}\'')
            else:
                # Format as: "field" IN ('value1', 'value2', 'value3')
                values_str = ", ".join([f"'{v}'" for v in escaped_values])
                conditions.append(f'"{db_column}" IN ({values_str})')

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # Log the WHERE clause for debugging
        logger.info(f"Generated WHERE clause: {where_clause}")

        return where_clause

    def get_surveys(self, filters: SurveyFilter) -> Dict[str, Any]:
        """Get surveys with filtering support for multiple values"""
        try:
            # Convert filters to dict, excluding None values
            filter_dict = {}
            for field, values in filters.dict(exclude_unset=True).items():
                if field in ["page", "size"]:
                    continue
                if values is not None and len(values) > 0:
                    filter_dict[field] = values

            logger.info(f"Applied filters: {filter_dict}")

            # Build WHERE clause
            where_clause = self.build_where_clause(filter_dict)

            # Calculate offset for pagination
            offset = (filters.page - 1) * filters.size

            # Build the complete SQL query
            base_query = f"""
                SELECT 
                    survey_qstn_resp_id,
                    survey_qstn_resp_key,
                    survey_key,
                    msl_key,
                    src_cd,
                    account_key,
                    prod_key,
                    name,
                    country_geo_id,
                    territory,
                    region,
                    msl_name,
                    title,
                    useremail,
                    survey_name,
                    assignment_type,
                    channels,
                    expired,
                    language,
                    product,
                    segment,
                    start_date,
                    end_date,
                    status,
                    target_type,
                    answer_choice,
                    question,
                    survey,
                    decimal,
                    number,
                    type,
                    response,
                    account_name,
                    msl_id,
                    is_active,
                    usertype,
                    department,
                    product_expertise,
                    user_type,
                    company
                FROM {self.table_path}
                WHERE {where_clause}
                ORDER BY survey_qstn_resp_id
                LIMIT {filters.size} OFFSET {offset}
            """

            # Execute query
            results = self.api.execute_query(base_query)

            # Get total count for pagination
            count_query = f"""
                SELECT COUNT(*) as total_count
                FROM {self.table_path}
                WHERE {where_clause}
            """
            count_result = self.api.execute_query(count_query)
            total_count = count_result[0]["total_count"] if count_result else 0

            total_pages = (total_count + filters.size - 1) // filters.size

            logger.info(
                f"Returning page {filters.page}/{total_pages} with {len(results)} surveys out of {total_count} total"
            )

            return {
                "surveys": results,
                "total": total_count,
                "page": filters.page,
                "size": filters.size,
                "total_pages": total_pages,
            }

        except Exception as e:
            logger.error(f"Error in
