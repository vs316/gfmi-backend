#!/usr/bin/env python3
"""Test script to verify database content"""

import sqlite3
import os


def test_database():
    db_file = "gfmi_local.db"

    if not os.path.exists(db_file):
        print(f"❌ Database file not found: {db_file}")
        print("Run: python local_db_setup.py")
        return

    print(f"✅ Database file found: {db_file}")

    try:
        with sqlite3.connect(db_file) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Test 1: Count total records
            cursor.execute("SELECT COUNT(*) as count FROM survey_responses")
            total = cursor.fetchone()["count"]
            print(f"📊 Total records: {total}")

            if total == 0:
                print("❌ No data in database!")
                print("Run: python local_db_setup.py")
                return

            # Test 2: Check unique countries
            cursor.execute(
                "SELECT DISTINCT country_geo_id FROM survey_responses WHERE country_geo_id IS NOT NULL"
            )
            countries = [row[0] for row in cursor.fetchall()]
            print(f"🌍 Countries ({len(countries)}): {countries}")

            # Test 3: Check unique MSL names
            cursor.execute(
                "SELECT DISTINCT msl_name FROM survey_responses WHERE msl_name IS NOT NULL LIMIT 5"
            )
            msls = [row[0] for row in cursor.fetchall()]
            print(f"👥 MSL Names ({len(msls)}): {msls}")

            # Test 4: Check unique survey names
            cursor.execute(
                "SELECT DISTINCT survey_name FROM survey_responses WHERE survey_name IS NOT NULL LIMIT 3"
            )
            surveys = [row[0] for row in cursor.fetchall()]
            print(f"📋 Survey Names ({len(surveys)}): {surveys}")

            # Test 5: Sample record
            cursor.execute("SELECT * FROM survey_responses LIMIT 1")
            sample = dict(cursor.fetchone())
            print(f"📄 Sample record keys: {list(sample.keys())[:10]}")

            # Test 6: Check specific columns that should have data
            test_columns = [
                "country_geo_id",
                "msl_name",
                "survey_name",
                "response",
                "account_name",
            ]
            for col in test_columns:
                cursor.execute(
                    f'SELECT COUNT(DISTINCT "{col}") as count FROM survey_responses WHERE "{col}" IS NOT NULL AND "{col}" != ""'
                )
                count = cursor.fetchone()["count"]
                print(f"🔍 {col}: {count} unique values")

    except Exception as e:
        print(f"❌ Database error: {e}")


if __name__ == "__main__":
    test_database()
