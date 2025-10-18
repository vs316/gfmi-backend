# app/services/local_data_service.py
import pandas as pd
from typing import Dict, Any, List, Optional
from app.models.filter import FilterOptions, SurveyFilter
import logging
import os

logger = logging.getLogger(__name__)


class LocalDataService:
    """Service to read data from CSV file for local testing"""

    # Map filter parameter names to actual CSV column names
    FILTER_FIELD_MAPPING = {
        "msl_names": "msl_name",  # FIXED: Use msl_name column (contains emails like carl.deluca@regeneron.com.mcrmeu)
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
        "channels": "channels",  # Note: CSV has 'channels' (plural)
        "assignment_types": "assignment_type",
        "specialties": "specialty",
        "practice_settings": "practice_setting",
        "institutions": "company",
    }

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
            logger.info(f"CSV columns: {list(self.df.columns)}")

            # Convert NaN to None for JSON serialization
            self.df = self.df.where(pd.notnull(self.df), None)

        except Exception as e:
            logger.error(f"Error loading CSV: {str(e)}")
            raise

    def build_filter_mask(self, filters: Dict[str, List[str]]) -> pd.Series:
        """Build pandas boolean mask from filters

        Maps filter parameter names to actual CSV column names
        """
        mask = pd.Series([True] * len(self.df))

        for param_name, values in filters.items():
            if not values or len(values) == 0:
                continue

            # Get the actual CSV column name
            csv_column = self.FILTER_FIELD_MAPPING.get(param_name, param_name)

            # Check if column exists in dataframe
            if csv_column not in self.df.columns:
                logger.warning(
                    f"Column '{csv_column}' not found in CSV (from parameter '{param_name}')"
                )
                continue

            # Create OR condition for multiple values (matches any value in the list)
            field_mask = self.df[csv_column].isin(values)
            mask = mask & field_mask

            logger.info(
                f"Filter: {param_name} -> {csv_column} = {values} (matched {field_mask.sum()} rows)"
            )

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
                logger.info(
                    f"After filtering: {len(filtered_df)} rows out of {len(self.df)}"
                )
            else:
                filtered_df = self.df

            # Calculate pagination
            total_count = len(filtered_df)
            offset = (filters.page - 1) * filters.size

            # Apply pagination
            paginated_df = filtered_df.iloc[offset : offset + filters.size]

            # Convert to list of dicts
            results = paginated_df.to_dict("records")

            total_pages = (
                (total_count + filters.size - 1) // filters.size
                if total_count > 0
                else 0
            )

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
            logger.error(f"Error in get_surveys: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            raise

    # def get_filter_options(
    #     self, applied_filters: Optional[Dict[str, List[str]]] = None
    # ) -> FilterOptions:
    #     """Get available filter options, optionally filtered by existing selections"""
    #     try:
    #         # Apply filters if provided
    #         if applied_filters:
    #             mask = self.build_filter_mask(applied_filters)
    #             filtered_df = self.df[mask]
    #         else:
    #             filtered_df = self.df

    #         # Get unique values for each field using actual CSV column names
    #         options = {
    #             "country_geo_ids": self._get_unique_values(
    #                 filtered_df, "country_geo_id"
    #             ),
    #             "territories": self._get_unique_values(filtered_df, "territory"),
    #             "regions": self._get_unique_values(filtered_df, "region"),
    #             "msl_names": self._get_unique_values(
    #                 filtered_df, "msl_name"
    #             ),  # FIXED: Use msl_name column
    #             "titles": self._get_unique_values(filtered_df, "title"),
    #             "departments": self._get_unique_values(filtered_df, "department"),
    #             "user_types": self._get_unique_values(filtered_df, "user_type"),
    #             "survey_names": self._get_unique_values(filtered_df, "survey_name"),
    #             "questions": self._get_unique_values(filtered_df, "question"),
    #             "products": self._get_unique_values(filtered_df, "product"),
    #             "product_expertise_options": self._get_unique_values(
    #                 filtered_df, "product_expertise"
    #             ),
    #             "responses": self._get_unique_values(filtered_df, "response"),
    #             "account_names": self._get_unique_values(filtered_df, "account_name"),
    #             "companies": self._get_unique_values(filtered_df, "company"),
    #             "channels": self._get_unique_values(
    #                 filtered_df, "channels"
    #             ),  # Note: plural in CSV
    #             "assignment_types": self._get_unique_values(
    #                 filtered_df, "assignment_type"
    #             ),
    #         }

    #         logger.info(
    #             f"Generated filter options: {len(options['msl_names'])} MSL names, {len(options['titles'])} titles"
    #         )

    #         return FilterOptions(**options)

    #     except Exception as e:
    #         logger.error(f"Error in get_filter_options: {str(e)}")
    #         import traceback

    #         logger.error(traceback.format_exc())
    #         raise
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

            # Get unique values for each field using actual CSV column names
            options = {
                "country_geo_ids": self._get_unique_values(
                    filtered_df, "country_geo_id"
                ),
                "territories": self._get_unique_values(filtered_df, "territory"),
                "regions": self._get_unique_values(filtered_df, "region"),
                "msl_names": self._get_msl_names_with_display(
                    filtered_df
                ),  # NEW: Special handling
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

            logger.info(
                f"Generated filter options: {len(options['msl_names'])} MSL names, {len(options['titles'])} titles"
            )

            return FilterOptions(**options)

        except Exception as e:
            logger.error(f"Error in get_filter_options: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            raise

    def _get_unique_values(self, df: pd.DataFrame, column: str) -> List[str]:
        """Get sorted unique values from a column, excluding None/NaN"""
        if column not in df.columns:
            logger.warning(f"Column '{column}' not found in CSV")
            return []

        unique_values = df[column].dropna().unique().tolist()
        unique_values = [
            str(v) for v in unique_values if v is not None and str(v) != "nan"
        ]
        return sorted(unique_values)

    def _get_msl_names_with_display(self, df: pd.DataFrame) -> List[str]:
        """Get MSL names in format 'msl_name|Name (msl_name)'

        Returns list of strings in format: 'value|label'
        Frontend will parse this to create {value, label} pairs
        """
        logger.info(f"DEBUG: Processing {len(df)} rows for MSL names")
        logger.info(
            f"DEBUG: Sample row - name: {df['name'].iloc[0]}, msl_name: {df['msl_name'].iloc[0]}"
        )

        if "name" not in df.columns or "msl_name" not in df.columns:
            logger.warning("Required columns 'name' or 'msl_name' not found")
            # Fallback to just msl_name if name is not available
            if "msl_name" in df.columns:
                return self._get_unique_values(df, "msl_name")
            return []

        # Get unique combinations of name and msl_name
        # Don't use .dropna() here as it might drop valid rows
        unique_msls = df[["name", "msl_name"]].drop_duplicates()

        # Format as "value|label" where:
        # - value is msl_name (for filtering)
        # - label is "Name (msl_name)"
        result = []
        for _, row in unique_msls.iterrows():
            msl_name_val = row["msl_name"]
            name_val = row["name"]

            # Convert to string and check for valid values
            msl_name = str(msl_name_val) if pd.notna(msl_name_val) else None
            name = str(name_val) if pd.notna(name_val) else None

            # Only include if both values are valid
            if msl_name and msl_name != "nan" and name and name != "nan":
                # Format: value|label
                result.append(f"{msl_name}|{name} ({msl_name})")
                logger.debug(f"Formatted MSL: {msl_name} -> {name} ({msl_name})")
            elif msl_name and msl_name != "nan":
                # If we have email but no name, just use email
                logger.warning(f"MSL {msl_name} has no name, using email only")
                result.append(msl_name)

        logger.info(f"Generated {len(result)} MSL name options with display names")
        if result:
            logger.info(f"Sample formatted MSL: {result[0]}")

        return sorted(result)

    def get_progressive_filter_options(
        self, target_filter: str, applied_filters: Dict[str, List[str]]
    ) -> List[str]:
        """Get filter options for a specific field based on other applied filters"""
        try:
            # Get the actual CSV column name
            csv_column = self.FILTER_FIELD_MAPPING.get(target_filter, target_filter)

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

            # Get unique values for target filter using the CSV column name
            # Use special handling for MSL names
            if target_filter == "msl_names":
                return self._get_msl_names_with_display(filtered_df)
            else:
                return self._get_unique_values(filtered_df, csv_column)

        except Exception as e:
            logger.error(f"Error in get_progressive_filter_options: {str(e)}")
            import traceback

            logger.error(traceback.format_exc())
            raise

    def get_survey_by_id(self, survey_id: str) -> Optional[Dict[str, Any]]:
        """Get specific survey by ID"""
        try:
            result = self.df[self.df["survey_qstn_resp_id"] == survey_id]

            if len(result) == 0:
                return None

            return result.iloc[0].to_dict()

        except Exception as e:
            logger.error(f"Error in get_survey_by_id: {str(e)}")
            raise
