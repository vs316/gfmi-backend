from typing import List, Optional, Dict, Any
from app.core.database import dremio_client
from models.survey import Survey, SurveyCreate, SurveyUpdate, SurveyListResponse
from models.filter import SurveyFilter
import uuid


class SurveyService:
    def __init__(self):
        self.table_name = "survey_responses"

    def create_survey(self, survey: SurveyCreate) -> Survey:
        survey_qstn_resp_id = str(uuid.uuid4())
        survey_qstn_resp_key = (
            f"{survey.survey_key}-{survey.msl_key}-{survey_qstn_resp_id}"
        )

        query = f"""
        INSERT INTO {self.table_name} (
            survey_qstn_resp_id, survey_qstn_resp_key, survey_key, msl_key, src_cd,
            account_key, survey_name, assignment_type, channels, expired, language,
            status, question, response, msl_name, account_name, country_geo_id,
            territory, title, department
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        params = (
            survey_qstn_resp_id,
            survey_qstn_resp_key,
            survey.survey_key,
            survey.msl_key,
            survey.src_cd,
            survey.account_key,
            survey.survey_name,
            survey.assignment_type,
            survey.channels,
            survey.expired,
            survey.language,
            survey.status,
            survey.question,
            survey.response,
            survey.msl_name,
            survey.account_name,
            survey.country_geo_id,
            survey.territory,
            survey.title,
            survey.department,
        )

        dremio_client.execute_query(query, params)
        return self.get_survey(survey_qstn_resp_id)

    def get_survey(self, survey_id: str) -> Optional[Survey]:
        query = f"SELECT * FROM {self.table_name} WHERE survey_qstn_resp_id = ?"
        results = dremio_client.execute_query(query, (survey_id,))

        if results:
            return Survey(**results[0])
        return None

    def get_surveys(self, filters: SurveyFilter) -> SurveyListResponse:
        # Build WHERE clause dynamically based on filters
        where_conditions = []
        params = []

        # Helper function to handle list filters with IN clause
        def add_list_filter(field_name: str, field_values: Optional[List[str]]):
            if field_values and len(field_values) > 0:
                # Create placeholders for IN clause: (?, ?, ?)
                placeholders = ", ".join(["?" for _ in field_values])
                where_conditions.append(f"{field_name} IN ({placeholders})")
                params.extend(field_values)

        # Apply filters - using IN clause for lists
        add_list_filter("msl_name", filters.msl_name)
        add_list_filter("title", filters.title)
        add_list_filter("department", filters.department)
        add_list_filter("user_type", filters.user_type)
        add_list_filter("country_geo_id", filters.country_geo_id)
        add_list_filter("region", filters.region)
        add_list_filter("territory", filters.territory)
        add_list_filter("response", filters.response)
        add_list_filter("product", filters.product)
        add_list_filter("account_name", filters.account_name)
        add_list_filter("company", filters.company)
        add_list_filter("name", filters.name)
        add_list_filter("usertype", filters.usertype)
        add_list_filter("channels", filters.channels)
        add_list_filter("assignment_type", filters.assignment_type)
        add_list_filter("survey_name", filters.survey_name)

        # Question uses LIKE (keep as single value)
        if filters.question:
            where_conditions.append("question LIKE ?")
            params.append(f"%{filters.question}%")

        # Build the query
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        # Count total records
        count_query = f"SELECT COUNT(*) as total FROM {self.table_name} {where_clause}"
        count_result = dremio_client.execute_query(count_query, tuple(params))
        total = count_result[0]["total"] if count_result else 0

        # Calculate pagination
        offset = (filters.page - 1) * filters.size
        total_pages = (total + filters.size - 1) // filters.size

        # Get paginated results
        query = f"""
        SELECT * FROM {self.table_name} 
        {where_clause}
        ORDER BY survey_qstn_resp_id
        LIMIT {filters.size} OFFSET {offset}
        """

        results = dremio_client.execute_query(query, tuple(params))
        surveys = [Survey(**row) for row in results]

        return SurveyListResponse(
            surveys=surveys,
            total=total,
            page=filters.page,
            size=filters.size,
            total_pages=total_pages,
        )

    def update_survey(
        self, survey_id: str, survey_update: SurveyUpdate
    ) -> Optional[Survey]:
        # Build SET clause dynamically
        set_conditions = []
        params = []

        update_data = survey_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                set_conditions.append(f"{field} = ?")
                params.append(value)

        if not set_conditions:
            return self.get_survey(survey_id)

        params.append(survey_id)
        query = f"""
        UPDATE {self.table_name}
        SET {', '.join(set_conditions)}
        WHERE survey_qstn_resp_id = ?
        """

        dremio_client.execute_query(query, tuple(params))
        return self.get_survey(survey_id)

    def delete_survey(self, survey_id: str) -> bool:
        query = f"DELETE FROM {self.table_name} WHERE survey_qstn_resp_id = ?"
        rows_affected = dremio_client.execute_query(query, (survey_id,))
        return rows_affected > 0


survey_service = SurveyService()
