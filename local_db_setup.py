"""
Local Database Setup for GFMI Insight Buddy
Creates SQLite database from CSV for local API testing
"""

import pandas as pd
import sqlite3
import os
import uuid
from datetime import datetime


class LocalDatabaseSetup:
    def __init__(self, db_file: str = "gfmi_local.db"):
        self.db_file = db_file

    def setup_from_csv(self, csv_file_path: str, table_name: str = "survey_responses"):
        """Setup SQLite database from CSV file"""
        print(f"🚀 Setting up local database from {csv_file_path}")

        # Read CSV file
        try:
            df = pd.read_csv(csv_file_path, encoding="utf-8")
            print(f"✅ Successfully read {len(df)} rows from CSV")
        except Exception as e:
            print(f"❌ Error reading CSV file: {e}")
            return False

        # Clean and prepare data
        df = self.clean_data(df)

        # Create SQLite database and load data
        try:
            # Remove existing database
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
                print(f"🗑️  Removed existing database: {self.db_file}")

            with sqlite3.connect(self.db_file) as conn:
                # Create table
                self.create_table(conn, table_name)

                # Insert data using pandas to_sql (much easier!)
                df.to_sql(table_name, conn, if_exists="append", index=False)

                print(f"✅ Successfully loaded {len(df)} rows into {table_name}")

                # Verify the load
                self.verify_data(conn, table_name)

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

        # Convert date columns to strings (SQLite compatibility)
        date_columns = ["start_date", "end_date"]
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime(
                    "%Y-%m-%d"
                )
                df[col] = df[col].replace("NaT", None)

        # Convert boolean columns
        boolean_columns = ["expired", "is_active"]
        for col in boolean_columns:
            if col in df.columns:
                df[col] = (
                    df[col]
                    .map(
                        {
                            "No": 0,
                            "Yes": 1,
                            True: 1,
                            False: 0,
                            1: 1,
                            0: 0,
                            "no": 0,
                            "yes": 1,
                            "true": 1,
                            "false": 0,
                        }
                    )
                    .fillna(0)
                )

        print(f"✅ Data cleaning complete. Shape: {df.shape}")
        return df

    def create_table(self, conn, table_name: str):
        """Create table with proper SQLite schema"""
        create_table_sql = f"""CREATE TABLE IF NOT EXISTS {table_name} (
            survey_qstn_resp_id TEXT PRIMARY KEY,
            survey_qstn_resp_key TEXT,
            survey_key TEXT,
            msl_key TEXT,
            src_cd TEXT,
            account_key TEXT,
            prod_key TEXT,
            survey_name TEXT,
            assignment_type TEXT,
            channels TEXT,
            expired INTEGER,
            language TEXT,
            product TEXT,
            region TEXT,
            segment TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            target_type TEXT,
            territory TEXT,
            answer_choice TEXT,
            question TEXT,
            survey TEXT,
            decimal REAL,
            number INTEGER,
            type TEXT,
            response TEXT,
            account_name TEXT,
            msl_id TEXT,
            country_geo_id TEXT,
            msl_name TEXT,
            src_cd_1 TEXT,
            is_active INTEGER,
            useremail TEXT,
            usertype TEXT,
            department TEXT,
            product_expertise TEXT,
            user_type TEXT,
            title TEXT,
            company TEXT,
            name TEXT
        )"""

        conn.execute(create_table_sql)
        print(f"✅ Table {table_name} created")

    def verify_data(self, conn, table_name: str):
        """Verify the data was loaded correctly"""
        print(f"🔍 Verifying data in table {table_name}...")

        # Count total rows
        cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
        total_rows = cursor.fetchone()[0]
        print(f"📊 Total rows in table: {total_rows}")

        # Get sample of data
        cursor = conn.execute(f"SELECT * FROM {table_name} LIMIT 3")
        columns = [description[0] for description in cursor.description]
        sample_rows = cursor.fetchall()

        print("📋 Sample data:")
        for i, row in enumerate(sample_rows):
            print(f"  Row {i+1}:")
            for j, col in enumerate(columns[:8]):  # Show first 8 columns
                value = row[j]
                if isinstance(value, str) and len(str(value)) > 50:
                    value = str(value)[:50] + "..."
                print(f"    {col}: {value}")
            print()

        # Check unique values for key filter fields
        filter_fields = ["country_geo_id", "msl_name", "survey_name", "response"]
        for field in filter_fields:
            try:
                cursor = conn.execute(
                    f'SELECT DISTINCT "{field}" FROM {table_name} WHERE "{field}" IS NOT NULL LIMIT 5'
                )
                unique_values = [row[0] for row in cursor.fetchall()]
                print(f"✨ Sample {field} values: {unique_values}")
            except Exception as e:
                print(f"⚠️  Could not get unique values for {field}: {e}")


def main():
    """Main function to run the local database setup"""
    print("🚀 GFMI Local Database Setup")
    print("=" * 50)

    # Look for CSV files in current directory and Downloads
    csv_paths = [
        "17198ac2-ff74-5bcd-422b-f465b409db00.csv",
        "C:/Users/VachanShetty/Downloads/17198ac2-ff74-5bcd-422b-f465b409db00.csv",
        os.path.join(
            os.path.expanduser("~"),
            "Downloads",
            "17198ac2-ff74-5bcd-422b-f465b409db00.csv",
        ),
    ]

    CSV_FILE_PATH = None
    for path in csv_paths:
        if os.path.exists(path):
            CSV_FILE_PATH = path
            print(f"📄 Found CSV file: {CSV_FILE_PATH}")
            break

    if not CSV_FILE_PATH:
        print("❌ CSV file not found. Tried:")
        for path in csv_paths:
            print(f"  📄 {path}")
        print()
        print("Please copy your CSV file to the current directory.")
        return

    DB_FILE = "gfmi_local.db"
    TABLE_NAME = "survey_responses"

    print(f"🗄️  Database file: {DB_FILE}")
    print(f"📊 Table name: {TABLE_NAME}")
    print()

    # Initialize setup and run
    setup = LocalDatabaseSetup(DB_FILE)

    # Setup database
    success = setup.setup_from_csv(CSV_FILE_PATH, TABLE_NAME)

    if success:
        print()
        print("=" * 50)
        print("🎉 Local database setup completed!")
        print()
        print("🔥 Next steps:")
        print("1. Replace database import in your services")
        print("2. Start your FastAPI backend: uvicorn app.main:app --reload")
        print("3. Visit: http://localhost:8000/docs")
        print("4. Test all API endpoints locally!")
        print(f"5. Database file created: {os.path.abspath(DB_FILE)}")
    else:
        print()
        print("❌ Local database setup failed.")


if __name__ == "__main__":
    main()
