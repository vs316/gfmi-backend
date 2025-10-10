"""
Data Loader Script for GFMI Insight Buddy
Loads CSV data into Dremio database for the survey responses table
"""

import pandas as pd
import pyodbc
import os
import uuid
from datetime import datetime
from typing import Optional


class DremioDataLoader:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    def load_csv_to_dremio(
        self, csv_file_path: str, table_name: str = "survey_responses"
    ):
        """Load CSV data into Dremio table"""
        print(f"Loading data from {csv_file_path} into table {table_name}...")

        # Read CSV file
        try:
            df = pd.read_csv(csv_file_path, encoding="utf-8")
            print(f"✅ Successfully read {len(df)} rows from CSV")
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
            return False

        # Clean and prepare data
        df = self.clean_data(df)

        # Connect to Dremio and load data
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()

                # Create table if it doesn't exist
                self.create_table_if_not_exists(cursor, table_name)

                # Insert data
                self.insert_data(cursor, df, table_name)

                conn.commit()
                print(f"✅ Successfully loaded {len(df)} rows into {table_name}")
                return True

        except Exception as e:
            print(f"❌ Database error: {e}")
            return False

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for insertion"""
        print("🧹 Cleaning data...")

        # Fill NaN values with None
        df = df.where(pd.notnull(df), None)

        # Ensure required fields have values
        if (
            "survey_qstn_resp_id" not in df.columns
            or df["survey_qstn_resp_id"].isnull().any()
        ):
            print("⚠️  Generating missing survey_qstn_resp_id values...")
            df["survey_qstn_resp_id"] = df["survey_qstn_resp_id"].fillna(
                [str(uuid.uuid4()) for _ in range(len(df))]
            )

        # Convert date columns
        date_columns = ["start_date", "end_date"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        # Convert boolean columns
        boolean_columns = ["expired", "is_active"]
        for col in boolean_columns:
            if col in df.columns:
                df[col] = df[col].map(
                    {
                        "No": False,
                        "Yes": True,
                        True: True,
                        False: False,
                        1: True,
                        0: False,
                    }
                )

        print(f"✅ Data cleaning complete. Shape: {df.shape}")
        return df

    def create_table_if_not_exists(self, cursor, table_name: str):
        """Create table if it doesn't exist"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            survey_qstn_resp_id VARCHAR(255) PRIMARY KEY,
            survey_qstn_resp_key VARCHAR(255),
            survey_key VARCHAR(255),
            msl_key VARCHAR(255),
            src_cd VARCHAR(50),
            account_key VARCHAR(255),
            prod_key VARCHAR(255),
            survey_name VARCHAR(500),
            assignment_type VARCHAR(100),
            channels VARCHAR(100),
            expired BOOLEAN,
            language VARCHAR(10),
            product VARCHAR(255),
            region VARCHAR(255),
            segment VARCHAR(255),
            start_date DATE,
            end_date DATE,
            status VARCHAR(50),
            target_type VARCHAR(255),
            territory VARCHAR(255),
            answer_choice TEXT,
            question TEXT,
            survey TEXT,
            decimal DECIMAL(10,2),
            number INTEGER,
            type VARCHAR(100),
            response TEXT,
            account_name VARCHAR(500),
            msl_id VARCHAR(255),
            country_geo_id VARCHAR(100),
            msl_name VARCHAR(500),
            src_cd_1 VARCHAR(50),
            is_active BOOLEAN,
            useremail VARCHAR(255),
            usertype VARCHAR(100),
            department VARCHAR(255),
            product_expertise VARCHAR(255),
            user_type VARCHAR(100),
            title VARCHAR(255),
            company VARCHAR(255),
            name VARCHAR(255)
        )
        """

        try:
            cursor.execute(create_table_sql)
            print(f"✅ Table {table_name} created or verified")
        except Exception as e:
            print(f"⚠️  Note: Table creation failed (may already exist): {e}")

    def insert_data(self, cursor, df: pd.DataFrame, table_name: str):
        """Insert data into the table"""
        print(f"💾 Inserting {len(df)} rows...")

        # Get column names from dataframe
        columns = df.columns.tolist()
        placeholders = ", ".join(["?" for _ in columns])
        column_names = ", ".join(columns)

        insert_sql = f"""
        INSERT INTO {table_name} ({column_names})
        VALUES ({placeholders})
        """

        # Prepare data for insertion
        data_tuples = []
        for _, row in df.iterrows():
            tuple_data = []
            for col in columns:
                value = row[col]
                if pd.isna(value):
                    tuple_data.append(None)
                else:
                    tuple_data.append(value)
            data_tuples.append(tuple(tuple_data))

        # Insert in batches
        batch_size = 1000
        total_batches = (len(data_tuples) + batch_size - 1) // batch_size

        for i in range(0, len(data_tuples), batch_size):
            batch = data_tuples[i : i + batch_size]
            batch_num = (i // batch_size) + 1

            try:
                cursor.executemany(insert_sql, batch)
                print(
                    f"  📦 Batch {batch_num}/{total_batches} inserted ({len(batch)} rows)"
                )
            except Exception as e:
                print(f"❌ Error inserting batch {batch_num}: {e}")
                # Try inserting one by one for this batch
                for j, row_data in enumerate(batch):
                    try:
                        cursor.execute(insert_sql, row_data)
                    except Exception as row_error:
                        print(f"❌ Error inserting row {i+j+1}: {row_error}")

    def verify_data_load(self, table_name: str = "survey_responses"):
        """Verify the data was loaded correctly"""
        print(f"🔍 Verifying data in table {table_name}...")

        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()

                # Count total rows
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                total_rows = cursor.fetchone()[0]
                print(f"📊 Total rows in table: {total_rows}")

                # Get sample of data
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                columns = [column[0] for column in cursor.description]
                sample_rows = cursor.fetchall()

                print("📋 Sample data:")
                for i, row in enumerate(sample_rows):
                    print(
                        f"  Row {i+1}: {dict(zip(columns[:5], row[:5]))}"
                    )  # Show first 5 columns

                # Check unique values for key filter fields
                filter_fields = [
                    "country_geo_id",
                    "msl_name",
                    "survey_name",
                    "response",
                ]
                for field in filter_fields:
                    try:
                        cursor.execute(
                            f"SELECT DISTINCT {field} FROM {table_name} WHERE {field} IS NOT NULL LIMIT 10"
                        )
                        unique_values = [row[0] for row in cursor.fetchall()]
                        print(f"🏷️  Unique {field} values: {unique_values}")
                    except Exception as e:
                        print(f"⚠️  Could not get unique values for {field}: {e}")

                return True

        except Exception as e:
            print(f"❌ Verification error: {e}")
            return False


def main():
    """Main function to run the data loader"""
    print("🚀 GFMI Insight Buddy Data Loader")
    print("=" * 50)

    # Configuration (modify these values)
    DREMIO_HOST = os.getenv("DREMIO_HOST", "localhost")
    DREMIO_PORT = os.getenv("DREMIO_PORT", "31010")
    DREMIO_USERNAME = os.getenv("DREMIO_USERNAME", "your_username")
    DREMIO_PASSWORD = os.getenv("DREMIO_PASSWORD", "your_password")
    DREMIO_DATABASE = os.getenv("DREMIO_DATABASE", "your_database")

    CSV_FILE_PATH = "C:/Users/VachanShetty/Downloads/17198ac2-ff74-5bcd-422b-f465b409db00.csv"  # Update with your CSV path
    TABLE_NAME = "survey_responses"

    # Build connection string
    connection_string = (
        f"DRIVER={{Dremio ODBC Driver 64-bit}};"
        f"HOST={DREMIO_HOST};"
        f"PORT={DREMIO_PORT};"
        f"UID={DREMIO_USERNAME};"
        f"PWD={DREMIO_PASSWORD};"
        f"DATABASE={DREMIO_DATABASE};"
    )

    print(f"📡 Connecting to Dremio at {DREMIO_HOST}:{DREMIO_PORT}")
    print(f"📁 CSV file: {CSV_FILE_PATH}")
    print(f"🗄️  Target table: {TABLE_NAME}")
    print()

    # Check if CSV file exists
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ CSV file not found: {CSV_FILE_PATH}")
        print("Please update the CSV_FILE_PATH variable with the correct path.")
        return

    # Initialize loader and run
    loader = DremioDataLoader(connection_string)

    # Load data
    success = loader.load_csv_to_dremio(CSV_FILE_PATH, TABLE_NAME)

    if success:
        print()
        print("=" * 50)
        print("🎉 Data loading completed successfully!")

        # Verify the load
        print()
        loader.verify_data_load(TABLE_NAME)

        print()
        print("🔥 Next steps:")
        print("1. Start your FastAPI backend: uvicorn app.main:app --reload")
        print("2. Start your React frontend: npm start")
        print("3. Visit http://localhost:8000/docs for API documentation")
        print("4. Test the filters in your React application")
    else:
        print()
        print("❌ Data loading failed. Please check the error messages above.")
        print()
        print("🛠️  Troubleshooting tips:")
        print("1. Verify Dremio is running and accessible")
        print("2. Check your Dremio credentials in environment variables")
        print("3. Ensure the Dremio ODBC driver is installed")
        print("4. Verify the CSV file path is correct")


if __name__ == "__main__":
    main()
