from typing import List, Dict, Any
from app.core.database import dremio_client
from app.models.filter import FilterOptions


class FilterService:
    def __init__(self):
        self.table_name = "survey_responses"  # Adjust based on actual Dremio table name

    def get_filter_options(self) -> FilterOptions:
        # Get unique values for each filter category
        filters = {}

        # Teams and Organizations
        filters["msl_names"] = self._get_unique_values("msl_name")
        filters["titles"] = self._get_unique_values("title")
        filters["departments"] = self._get_unique_values("department")
        filters["user_types"] = self._get_unique_values("user_type")

        # Geographic
        filters["regions"] = self._get_unique_values("region")
        filters["countries"] = self._get_unique_values("country_geo_id")
        filters["territories"] = self._get_unique_values("territory")

        # Medical
        filters["tumor_types"] = self._get_unique_values("response")
        filters["products"] = self._get_unique_values("product")

        # Healthcare provider (HCP)
        filters["account_names"] = self._get_unique_values("account_name")
        filters["institutions"] = self._get_unique_values("company")
        filters["specialties"] = self._get_unique_values("usertype")

        # Event & Engagement
        filters["channels"] = self._get_unique_values("channels")
        filters["assignment_types"] = self._get_unique_values("assignment_type")

        # Surveys
        filters["survey_names"] = self._get_unique_values("survey_name")
        filters["questions"] = self._get_unique_values("question")

        return FilterOptions(**filters)

    def _get_unique_values(self, column: str) -> List[str]:
        query = f"""
        SELECT DISTINCT {column}
        FROM {self.table_name}
        WHERE {column} IS NOT NULL AND {column} != ''
        ORDER BY {column}
        """

        try:
            results = dremio_client.execute_query(query)
            return [row[column] for row in results]
        except Exception as e:
            print(f"Error getting unique values for {column}: {e}")
            return []

    def get_related_filters(
        self, base_filter: str, base_value: str
    ) -> Dict[str, List[str]]:
        """Get related filter options based on a base filter selection"""
        related_filters = {}

        # Define relationships between filters
        relationships = {
            "country_geo_id": ["territory", "msl_name", "title"],
            "msl_name": ["country_geo_id", "title", "survey_name"],
            "survey_name": ["question", "msl_name"],
            "account_name": ["country_geo_id", "territory"],
        }

        if base_filter in relationships:
            for related_field in relationships[base_filter]:
                query = f"""
                SELECT DISTINCT {related_field}
                FROM {self.table_name}
                WHERE {base_filter} = ? 
                AND {related_field} IS NOT NULL 
                AND {related_field} != ''
                ORDER BY {related_field}
                """

                try:
                    results = dremio_client.execute_query(query, (base_value,))
                    related_filters[related_field] = [
                        row[related_field] for row in results
                    ]
                except Exception as e:
                    print(f"Error getting related values for {related_field}: {e}")
                    related_filters[related_field] = []

        return related_filters


filter_service = FilterService()
