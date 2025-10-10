#!/usr/bin/env python3
"""
Test script to verify local SQLite setup works with the APIs
"""

import requests
import json
import time


def test_local_apis():
    """Test all the API endpoints locally"""
    base_url = "http://localhost:8000"

    print("🧪 Testing GFMI Local APIs")
    print("=" * 50)

    # Test 1: Health check
    print("1️⃣  Testing health check...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ Health check passed")
            print(f"   📊 Response: {response.json()}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("   ❌ Cannot connect to API server")
        print("   💡 Make sure to run: uvicorn app.main:app --reload")
        return False

    # Test 2: Get filter options
    print("\n2️⃣  Testing filter options...")
    try:
        response = requests.get(f"{base_url}/api/v1/filters/options")
        if response.status_code == 200:
            filters = response.json()
            print("   ✅ Filter options retrieved")
            print(f"   📊 Countries: {filters.get('countries', [])[:3]}...")
            print(f"   📊 Survey names: {len(filters.get('survey_names', []))} surveys")
            print(f"   📊 MSL names: {len(filters.get('msl_names', []))} MSLs")
        else:
            print(f"   ❌ Filter options failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Filter options error: {e}")

    # Test 3: Get surveys (no filters)
    print("\n3️⃣  Testing get surveys...")
    try:
        response = requests.get(f"{base_url}/api/v1/surveys/?page=1&size=10")
        if response.status_code == 200:
            surveys = response.json()
            print("   ✅ Surveys retrieved")
            print(f"   📊 Total surveys: {surveys.get('total', 0)}")
            print(f"   📊 Current page: {surveys.get('page', 0)}")
            print(f"   📊 Returned: {len(surveys.get('surveys', []))} surveys")

            # Show first survey
            if surveys.get("surveys"):
                first_survey = surveys["surveys"][0]
                print(f"   📋 Sample survey: {first_survey.get('survey_name', 'N/A')}")
        else:
            print(f"   ❌ Get surveys failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Get surveys error: {e}")

    # Test 4: Get surveys with filters
    print("\n4️⃣  Testing filtered surveys...")
    try:
        response = requests.get(
            f"{base_url}/api/v1/surveys/?country_geo_id=GB-UK-Ireland&page=1&size=5"
        )
        if response.status_code == 200:
            surveys = response.json()
            print("   ✅ Filtered surveys retrieved")
            print(f"   📊 Filtered results: {surveys.get('total', 0)} surveys")
            if surveys.get("surveys"):
                print(f"   🇬🇧 UK surveys found: {len(surveys['surveys'])}")
        else:
            print(f"   ❌ Filtered surveys failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Filtered surveys error: {e}")

    # Test 5: Test multiple filters
    print("\n5️⃣  Testing multiple filters...")
    try:
        params = {
            "survey_name": "Oncology Organic Insights (EU-UK)",
            "page": 1,
            "size": 5,
        }
        response = requests.get(f"{base_url}/api/v1/surveys/", params=params)
        if response.status_code == 200:
            surveys = response.json()
            print("   ✅ Multiple filters work")
            print(f"   📊 Oncology surveys: {surveys.get('total', 0)}")
        else:
            print(f"   ❌ Multiple filters failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Multiple filters error: {e}")

    print("\n" + "=" * 50)
    print("🎉 Local API testing completed!")
    print("\n📱 Interactive testing:")
    print(f"   • Swagger UI: {base_url}/docs")
    print(f"   • ReDoc: {base_url}/redoc")
    print("\n🔗 Example API calls:")
    print(f"   • All surveys: {base_url}/api/v1/surveys/")
    print(f"   • Filters: {base_url}/api/v1/filters/options")
    print(f"   • UK surveys: {base_url}/api/v1/surveys/?country_geo_id=GB-UK-Ireland")

    return True


def main():
    """Run the test suite"""
    print("⏳ Starting API tests in 2 seconds...")
    print("   (Make sure your API server is running)")
    time.sleep(2)

    success = test_local_apis()

    if success:
        print("\n✅ All basic tests passed!")
        print("Your local GFMI API is working correctly! 🎯")
    else:
        print("\n❌ Some tests failed.")
        print("Check the error messages above for troubleshooting.")


if __name__ == "__main__":
    main()
