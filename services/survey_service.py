from typing import List, Optional, Dict, Any
from app.core.database import dremio_client
from app.models.survey import Survey, SurveyCreate, SurveyUpdate, SurveyListResponse
from app.models.filter import SurveyFilter
import uuid


class SurveyService:
    def __init__(self):
        self.table_name = "survey_responses"  # Adjust based on actual Dremio table name

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

        if filters.msl_name:
            where_conditions.append("msl_name = ?")
            params.append(filters.msl_name)

        if filters.title:
            where_conditions.append("title = ?")
            params.append(filters.title)

        if filters.department:
            where_conditions.append("department = ?")
            params.append(filters.department)

        if filters.country_geo_id:
            where_conditions.append("country_geo_id = ?")
            params.append(filters.country_geo_id)

        if filters.territory:
            where_conditions.append("territory = ?")
            params.append(filters.territory)

        if filters.response:
            where_conditions.append("response = ?")
            params.append(filters.response)

        if filters.account_name:
            where_conditions.append("account_name = ?")
            params.append(filters.account_name)

        if filters.survey_name:
            where_conditions.append("survey_name = ?")
            params.append(filters.survey_name)

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
