# app/services/air_api_service.py
import httpx
import json
from typing import Dict, List, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class AIRAPIService:
    """Service to interact with the AIR-API chat endpoint"""

    def __init__(self):
        self.base_url = settings.AIR_API_BASE_URL
        self.timeout = 60.0  # 60 seconds timeout for AI responses

    def format_query_with_filters(
        self, user_query: str, filters: Optional[Dict[str, List[str]]] = None
    ) -> str:
        """
        Format the user query with selected filters into a single query string

        Args:
            user_query: The natural language query from the user
            filters: Dictionary of selected filters

        Returns:
            Formatted query string combining filters and user query
        """
        if not filters:
            return user_query

        # Build filter context string
        filter_parts = []

        # Map internal filter names to user-friendly names
        filter_name_map = {
            "msl_name": "MSL",
            "country_geo_id": "Country",
            "territory": "State/Territory",
            "region": "Region",
            "survey_name": "Survey",
            "question": "Survey Question",
            "account_name": "HCP Name",
            "company": "Institution",
            "product": "Product/Program",
            "response": "Tumor Type",
            "title": "Title",
            "department": "Department",
            "channels": "Channel",
            "assignment_type": "Engagement Type",
        }

        for filter_key, filter_values in filters.items():
            if filter_values and len(filter_values) > 0:
                friendly_name = filter_name_map.get(filter_key, filter_key)
                if len(filter_values) == 1:
                    filter_parts.append(f"{friendly_name}: {filter_values}")
                else:
                    values_str = ", ".join(filter_values)
                    filter_parts.append(f"{friendly_name}: {values_str}")

        # Combine filters and query
        if filter_parts:
            filter_context = " | ".join(filter_parts)
            formatted_query = (
                f"Context Filters: [{filter_context}] | User Query: {user_query}"
            )
        else:
            formatted_query = user_query

        logger.info(f"Formatted query: {formatted_query}")
        return formatted_query

    async def send_chat_query(
        self, query: str, filters: Optional[Dict[str, List[str]]] = None
    ) -> Dict:
        """
        Send a chat query to the AIR-API service

        Args:
            query: User's natural language query
            filters: Selected filter values

        Returns:
            Response from the AIR-API service
        """
        try:
            # Format the query with filters
            formatted_query = self.format_query_with_filters(query, filters)

            # Prepare the request payload
            payload = {"query": formatted_query}

            # Send request to AIR-API
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                )

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.error("AIR-API request timed out")
            raise Exception("Request to AI service timed out. Please try again.")
        except httpx.HTTPError as e:
            logger.error(f"AIR-API HTTP error: {str(e)}")
            raise Exception(f"Error communicating with AI service: {str(e)}")
        except Exception as e:
            logger.error(f"AIR-API error: {str(e)}")
            raise


# Create singleton instance
air_api_service = AIRAPIService()
