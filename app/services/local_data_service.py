# app/services/local_data_service.py
import pandas as pd
from typing import Dict, Any, List, Optional
from app.models.filter import FilterOptions, SurveyFilter
import logging
import os

logger = logging.getLogger(__name__)


class LocalDataService:
    """Service to read data from CSV file for local testing"""

    def __init__(self, csv_path: str = "data/survey_data.csv"):
        self.csv_path = csv_path
        self.df = None
        self._load_data()

    def _load_data(self):
        """Load CSV data into pandas DataFrame"""
        try:
            if not os.path.exists(self.csv_path):
                raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} rows from {self.csv_path}")

            # Convert NaN to None for JSON serialization
            self.df = self.df.where(pd.notnull(self.df), None)

        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise

    def build_filter_mask(self, filters: Dict[str, List[str]]) -> pd.Series:
        """Build pandas boolean mask from filters"""
        mask = pd.Series([True] * len(self.df))

        for field, values in filters.items():
            if values and len(values) > 0:
                # Create OR condition for multiple values
                field_mask = self.df[field].isin(values)
                mask = mask & field_mask

        return mask

    def get_surveys(self, filters: SurveyFilter) -> Dict[str, Any]:
        """Get surveys with filtering support for multiple values"""
        try:
            # Convert filters to dict, excluding None and empty values
            filter_dict = {}
            for field, values in filters.dict(exclude_unset=True).items():
                if field in ["page", "size"]:
                    continue
                if values is not None and len(values) > 0:
                    filter_dict[field] = values

            logger.info(f"Applied filters: {filter_dict}")

            # Apply filters
            if filter_dict:
                mask = self.build_filter_mask(filter_dict)
                filtered_df = self.df[mask]
            else:
                filtered_df = self.df

            # Calculate pagination
            total_count = len(filtered_df)
            offset = (filters.page - 1) * filters.size

            # Apply pagination
            paginated_df = filtered_df.iloc[offset : offset + filters.size]

            # Convert to list of dicts
            results = paginated_df.to_dict("records")

            return {
                "surveys": results,
                "total": total_count,
                "page": filters.page,
                "size": filters.size,
                "total_pages": (
                    (total_count + filters.size - 1) // filters.size
                    if total_count > 0
                    else 0
                ),
            }

        except Exception as e:
            logger.error(f"Error in get_surveys: {str(e)}")
            raise

    def get_filter_options(
        self, applied_filters: Optional[Dict[str, List[str]]] = None
    ) -> FilterOptions:
        """Get available filter options, optionally filtered by existing selections"""
        try:
            # Apply filters if provided
            if applied_filters:
                mask = self.build_filter_mask(applied_filters)
                filtered_df = self.df[mask]
            else:
                filtered_df = self.df

            # Get unique values for each field
            options = {
                "country_geo_ids": self._get_unique_values(
                    filtered_df, "country_geo_id"
                ),
                "territories": self._get_unique_values(filtered_df, "territory"),
                "regions": self._get_unique_values(filtered_df, "region"),
                "msl_names": self._get_unique_values(filtered_df, "msl_name"),
                "titles": self._get_unique_values(filtered_df, "title"),
                "departments": self._get_unique_values(filtered_df, "department"),
                "user_types": self._get_unique_values(filtered_df, "user_type"),
                "survey_names": self._get_unique_values(filtered_df, "survey_name"),
                "questions": self._get_unique_values(filtered_df, "question"),
                "products": self._get_unique_values(filtered_df, "product"),
                "product_expertise_options": self._get_unique_values(
                    filtered_df, "product_expertise"
                ),
                "responses": self._get_unique_values(filtered_df, "response"),
                "account_names": self._get_unique_values(filtered_df, "account_name"),
                "companies": self._get_unique_values(filtered_df, "company"),
                "channels": self._get_unique_values(filtered_df, "channels"),
                "assignment_types": self._get_unique_values(
                    filtered_df, "assignment_type"
                ),
            }

            return FilterOptions(**options)

        except Exception as e:
            logger.error(f"Error in get_filter_options: {str(e)}")
            raise

    def _get_unique_values(self, df: pd.DataFrame, column: str) -> List[str]:
        """Get sorted unique values from a column, excluding None/NaN"""
        if column not in df.columns:
            return []

        unique_values = df[column].dropna().unique().tolist()
        unique_values = [
            str(v) for v in unique_values if v is not None and str(v) != "nan"
        ]
        return sorted(unique_values)

    def get_progressive_filter_options(
        self, target_filter: str, applied_filters: Dict[str, List[str]]
    ) -> List[str]:
        """Get filter options for a specific field based on other applied filters"""
        try:
            # Remove target filter from applied filters
            filter_dict = {
                k: v for k, v in applied_filters.items() if k != target_filter
            }

            # Apply filters
            if filter_dict:
                mask = self.build_filter_mask(filter_dict)
                filtered_df = self.df[mask]
            else:
                filtered_df = self.df

            # Get unique values for target filter
            return self._get_unique_values(filtered_df, target_filter)

        except Exception as e:
            logger.error(f"Error in get_progressive_filter_options: {str(e)}")
            raise

    def get_survey_by_id(self, survey_id: str) -> Optional[Dict[str, Any]]:
        """Get specific survey by ID"""
        try:
            result = self.df[self.df["survey_qstn_resp_id"] == survey_id]

            if len(result) == 0:
                return None

            return result.iloc.to_dict()

        except Exception as e:
            logger.error(f"Error in get_survey_by_id: {str(e)}")
            raise
