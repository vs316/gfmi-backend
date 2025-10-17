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
        self.table_path = (
            settings.DREMIO_TABLE_PATH
        )  # "Global Development"."Business Applications"."Medical Affairs"."GFMI".p_med_affairs_crm_survey_details

    def build_where_clause(self, filters: Dict[str, Any]) -> str:
        """Build WHERE clause from filters, supporting multiple values

        FIXED: Properly formats SQL IN clauses with quoted values
        """
        conditions = []

        for field, values in filters.items():
            if values and len(values) > 0:
                # Escape single quotes in values
                escaped_values = [str(v).replace("'", "''") for v in values]

                # Handle multiple values with IN clause
                if len(values) == 1:
                    conditions.append(f"\"{field}\" = '{escaped_values}'")
                else:
                    # Format as: "field" IN ('value1', 'value2', 'value3')
                    values_str = ", ".join([f"'{v}'" for v in escaped_values])
                    conditions.append(f'"{field}" IN ({values_str})')

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
                    survey_key,
                    msl_key,
                    msl_name,
                    country_geo_id,
                    survey_name,
                    question,
                    response,
                    product,
                    account_name,
                    title,
                    company,
                    useremail,
                    department,
                    user_type,
                    product_expertise,
                    channels,
                    assignment_type,
                    territory,
                    region
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
            total_count = count_result["total_count"] if count_result else 0

            return {
                "data": results,
                "total": total_count,
                "page": filters.page,
                "size": filters.size,
                "pages": (total_count + filters.size - 1) // filters.size,
            }

        except Exception as e:
            logger.error(f"Error in get_surveys: {str(e)}")
            raise

    def get_filter_options(
        self, applied_filters: Optional[Dict[str, List[str]]] = None
    ) -> FilterOptions:
        """Get available filter options, optionally filtered by existing selections

        Progressive filtering: If filters are applied, only show options that
        are available given those constraints
        """
        try:
            # Build WHERE clause based on applied filters
            where_clause = "1=1"
            if applied_filters:
                where_clause = self.build_where_clause(applied_filters)

            # Query to get distinct values for all filter fields
            # This is optimized to get all distinct values in one query
            query = f"""
                SELECT DISTINCT
                    country_geo_id,
                    territory,
                    region,
                    msl_name,
                    title,
                    department,
                    user_type,
                    survey_name,
                    question,
                    product,
                    product_expertise,
                    response,
                    account_name,
                    company,
                    channels,
                    assignment_type
                FROM {self.table_path}
                WHERE {where_clause}
            """

            results = self.api.execute_query(query, limit=10000)

            # Extract unique values for each field
            options = {
                "country_geo_ids": set(),
                "territories": set(),
                "regions": set(),
                "msl_names": set(),
                "titles": set(),
                "departments": set(),
                "user_types": set(),
                "survey_names": set(),
                "questions": set(),
                "products": set(),
                "product_expertise_options": set(),
                "responses": set(),
                "account_names": set(),
                "companies": set(),
                "channels": set(),
                "assignment_types": set(),
            }

            # Map database fields to option keys
            field_mapping = {
                "country_geo_id": "country_geo_ids",
                "territory": "territories",
                "region": "regions",
                "msl_name": "msl_names",
                "title": "titles",
                "department": "departments",
                "user_type": "user_types",
                "survey_name": "survey_names",
                "question": "questions",
                "product": "products",
                "product_expertise": "product_expertise_options",
                "response": "responses",
                "account_name": "account_names",
                "company": "companies",
                "channels": "channels",
                "assignment_type": "assignment_types",
            }

            for row in results:
                for field, key in field_mapping.items():
                    value = row.get(field)
                    if value is not None and value != "":
                        options[key].add(value)

            # Convert sets to sorted lists
            result = {}
            for key, value_set in options.items():
                result[key] = sorted(list(value_set))

            return FilterOptions(**result)

        except Exception as e:
            logger.error(f"Error in get_filter_options: {str(e)}")
            raise

    def get_progressive_filter_options(
        self, target_filter: str, applied_filters: Dict[str, List[str]]
    ) -> List[str]:
        """Get filter options for a specific field based on other applied filters

        This enables progressive/cascading filters where selecting one filter
        updates the available options in other filters

        Args:
            target_filter: The filter field to get options for (e.g., 'country_geo_id')
            applied_filters: Dictionary of already applied filters

        Returns:
            List of available values for the target filter
        """
        try:
            # Build WHERE clause from applied filters (excluding the target filter)
            filter_dict = {
                k: v for k, v in applied_filters.items() if k != target_filter
            }
            where_clause = (
                self.build_where_clause(filter_dict) if filter_dict else "1=1"
            )

            # Query for distinct values of the target filter
            query = f"""
                SELECT DISTINCT "{target_filter}"
                FROM {self.table_path}
                WHERE {where_clause} 
                    AND "{target_filter}" IS NOT NULL
                ORDER BY "{target_filter}"
            """

            results = self.api.execute_query(query, limit=10000)

            # Extract values
            options = [row[target_filter] for row in results if row.get(target_filter)]

            return options

        except Exception as e:
            logger.error(f"Error in get_progressive_filter_options: {str(e)}")
            raise
