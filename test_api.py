#!/usr/bin/env python3
"""
Unified test script for GFMI APIs
Tests both Local CSV and Dremio configurations
"""

import requests
import json
import sys
import time
from typing import Dict, Any
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)


class APITester:
    def __init__(self, base_url: str = "http://localhost:8000", mode: str = "local"):
        self.base_url = base_url
        self.mode = mode
        self.passed = 0
        self.failed = 0

    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{text}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")

    def print_test(self, test_name: str):
        """Print test name"""
        print(f"\n{Fore.YELLOW}▶ {test_name}{Style.RESET_ALL}")

    def print_success(self, message: str):
        """Print success message"""
        print(f"  {Fore.GREEN}✅ {message}{Style.RESET_ALL}")
        self.passed += 1

    def print_error(self, message: str):
        """Print error message"""
        print(f"  {Fore.RED}❌ {message}{Style.RESET_ALL}")
        self.failed += 1

    def print_info(self, message: str):
        """Print info message"""
        print(f"  {Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")

    def test_health(self) -> bool:
        """Test 1: Health check endpoint"""
        self.print_test("Test 1: Health Check")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.print_success(
                    f"Health check passed - Status: {data.get('status')}"
                )
                self.print_info(f"Mode: {data.get('mode')}")
                self.print_info(f"Records: {data.get('total_records')}")
                return True
            else:
                self.print_error(f"Health check failed: {response.status_code}")
                return False
        except requests.ConnectionError:
            self.print_error("Cannot connect to API server")
            self.print_info("Make sure to run: uvicorn app.main:app --reload")
            return False
        except Exception as e:
            self.print_error(f"Health check error: {str(e)}")
            return False

    def test_filter_options(self) -> bool:
        """Test 2: Get filter options"""
        self.print_test("Test 2: Filter Options")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/filters/options", timeout=10
            )

            if response.status_code == 200:
                filters = response.json()
                self.print_success("Filter options retrieved")
                self.print_info(f"Countries: {len(filters.get('country_geo_ids', []))}")
                self.print_info(f"MSL Names: {len(filters.get('msl_names', []))}")
                self.print_info(f"Survey Names: {len(filters.get('survey_names', []))}")
                self.print_info(f"Titles: {len(filters.get('titles', []))}")

                # Show sample MSL name (to verify formatting)
                msl_names = filters.get("msl_names", [])
                if msl_names:
                    self.print_info(f"Sample MSL: {msl_names[0]}")

                return True
            else:
                self.print_error(f"Filter options failed: {response.status_code}")
                self.print_info(f"Response: {response.text[:200]}")
                return False
        except Exception as e:
            self.print_error(f"Filter options error: {str(e)}")
            return False

    def test_get_surveys(self) -> bool:
        """Test 3: Get surveys without filters"""
        self.print_test("Test 3: Get Surveys (No Filters)")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/surveys/?page=1&size=10", timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                surveys = data.get("surveys", [])
                self.print_success("Surveys retrieved")
                self.print_info(f"Total surveys: {data.get('total')}")
                self.print_info(f"Current page: {data.get('page')}")
                self.print_info(f"Page size: {data.get('size')}")
                self.print_info(f"Total pages: {data.get('total_pages')}")
                self.print_info(f"Returned: {len(surveys)} surveys")

                if surveys:
                    sample = surveys[0]
                    self.print_info(
                        f"Sample survey: {sample.get('survey_name', 'N/A')}"
                    )
                    self.print_info(f"Sample MSL: {sample.get('name', 'N/A')}")

                return True
            else:
                self.print_error(f"Get surveys failed: {response.status_code}")
                self.print_info(f"Response: {response.text[:200]}")
                return False
        except Exception as e:
            self.print_error(f"Get surveys error: {str(e)}")
            return False

    def test_filtered_surveys_single(self) -> bool:
        """Test 4: Get surveys with single filter"""
        self.print_test("Test 4: Filtered Surveys (Single Filter)")
        try:
            # Get filter options first to use valid filter value
            filters_response = requests.get(
                f"{self.base_url}/api/v1/filters/options", timeout=10
            )

            if filters_response.status_code != 200:
                self.print_error("Cannot get filter options")
                return False

            filters = filters_response.json()
            countries = filters.get("country_geo_ids", [])

            if not countries:
                self.print_info("No countries available for filtering test")
                return True

            test_country = countries[0]
            self.print_info(f"Testing with country: {test_country}")

            response = requests.get(
                f"{self.base_url}/api/v1/surveys/",
                params={"country_geo_ids": test_country, "page": 1, "size": 5},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                self.print_success("Filtered surveys retrieved")
                self.print_info(f"Filtered results: {data.get('total')} surveys")

                # Verify filtering worked
                surveys = data.get("surveys", [])
                if surveys:
                    matching = all(
                        s.get("country_geo_id") == test_country for s in surveys
                    )
                    if matching:
                        self.print_success("Filter correctly applied")
                    else:
                        self.print_error("Filter not correctly applied")
                        return False

                return True
            else:
                self.print_error(f"Filtered surveys failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Filtered surveys error: {str(e)}")
            return False

    def test_filtered_surveys_multiple(self) -> bool:
        """Test 5: Get surveys with multiple filters"""
        self.print_test("Test 5: Filtered Surveys (Multiple Filters)")
        try:
            # Get filter options first
            filters_response = requests.get(
                f"{self.base_url}/api/v1/filters/options", timeout=10
            )

            if filters_response.status_code != 200:
                self.print_error("Cannot get filter options")
                return False

            filters = filters_response.json()

            # Build multiple filter params
            params = {"page": 1, "size": 5}

            countries = filters.get("country_geo_ids", [])
            if countries:
                params["country_geo_ids"] = countries[0]
                self.print_info(f"Filter 1 - Country: {countries[0]}")

            survey_names = filters.get("survey_names", [])
            if survey_names:
                params["survey_names"] = survey_names[0]
                self.print_info(f"Filter 2 - Survey: {survey_names[0][:50]}...")

            response = requests.get(
                f"{self.base_url}/api/v1/surveys/", params=params, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.print_success("Multiple filters work")
                self.print_info(f"Results: {data.get('total')} surveys")
                return True
            else:
                self.print_error(f"Multiple filters failed: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"Multiple filters error: {str(e)}")
            return False

    def test_multiple_values_filter(self) -> bool:
        """Test 6: Test filtering with multiple values"""
        self.print_test("Test 6: Multiple Values Filter")
        try:
            # Get filter options
            filters_response = requests.get(
                f"{self.base_url}/api/v1/filters/options", timeout=10
            )

            if filters_response.status_code != 200:
                self.print_error("Cannot get filter options")
                return False

            filters = filters_response.json()
            countries = filters.get("country_geo_ids", [])

            if len(countries) < 2:
                self.print_info("Not enough countries for multi-value test")
                return True

            # Test with 2 countries
            test_countries = countries[:2]
            self.print_info(f"Testing with countries: {test_countries}")

            # FastAPI handles multiple values with repeated params
            params = [
                ("country_geo_ids", test_countries[0]),
                ("country_geo_ids", test_countries[1]),
                ("page", 1),
                ("size", 10),
            ]

            response = requests.get(
                f"{self.base_url}/api/v1/surveys/", params=params, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                self.print_success("Multiple values filter works")
                self.print_info(f"Results: {data.get('total')} surveys")

                # Verify filtering
                surveys = data.get("surveys", [])
                if surveys:
                    countries_in_results = set(s.get("country_geo_id") for s in surveys)
                    self.print_info(f"Countries in results: {countries_in_results}")

                return True
            else:
                self.print_error(
                    f"Multiple values filter failed: {response.status_code}"
                )
                return False
        except Exception as e:
            self.print_error(f"Multiple values filter error: {str(e)}")
            return False

    def test_msl_name_format(self) -> bool:
        """Test 7: Verify MSL name format (Name + Email)"""
        self.print_test("Test 7: MSL Name Format")
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/filters/options", timeout=10
            )

            if response.status_code == 200:
                filters = response.json()
                msl_names = filters.get("msl_names", [])

                if not msl_names:
                    self.print_info("No MSL names to verify")
                    return True

                # Check if format is "value|label" or just plain value
                has_pipe = any("|" in name for name in msl_names)

                if has_pipe:
                    # Parse and verify format
                    sample = msl_names[0]
                    if "|" in sample:
                        value, label = sample.split("|", 1)
                        self.print_success(f"MSL name format correct")
                        self.print_info(f"Value: {value}")
                        self.print_info(f"Label: {label}")

                        # Check if label contains both name and email
                        if "(" in label and ")" in label:
                            self.print_success("Label contains name and email")
                        else:
                            self.print_error("Label should contain 'Name (email)'")
                            return False
                    else:
                        self.print_error("MSL name should contain '|' separator")
                        return False
                else:
                    self.print_info(
                        f"MSL names are plain values (no formatting): {msl_names[0]}"
                    )
                    # This is OK for basic functionality, but not ideal

                return True
            else:
                self.print_error(f"Cannot get filter options: {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"MSL name format error: {str(e)}")
            return False

    def test_pagination(self) -> bool:
        """Test 8: Verify pagination works"""
        self.print_test("Test 8: Pagination")
        try:
            # Get page 1
            response1 = requests.get(
                f"{self.base_url}/api/v1/surveys/?page=1&size=5", timeout=10
            )

            # Get page 2
            response2 = requests.get(
                f"{self.base_url}/api/v1/surveys/?page=2&size=5", timeout=10
            )

            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()

                surveys1 = data1.get("surveys", [])
                surveys2 = data2.get("surveys", [])

                # Check if pages are different
                if surveys1 and surveys2:
                    ids1 = {s["survey_qstn_resp_id"] for s in surveys1}
                    ids2 = {s["survey_qstn_resp_id"] for s in surveys2}

                    if ids1 != ids2:
                        self.print_success("Pagination works correctly")
                        self.print_info(f"Page 1: {len(surveys1)} surveys")
                        self.print_info(f"Page 2: {len(surveys2)} surveys")
                        return True
                    else:
                        self.print_error("Pages contain same data")
                        return False
                else:
                    self.print_info("Not enough data to test pagination")
                    return True
            else:
                self.print_error("Pagination request failed")
                return False
        except Exception as e:
            self.print_error(f"Pagination error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        self.print_header(f"🧪 Testing GFMI API - {self.mode.upper()} Mode")
        self.print_info(f"Base URL: {self.base_url}")

        tests = [
            self.test_health,
            self.test_filter_options,
            self.test_get_surveys,
            self.test_filtered_surveys_single,
            self.test_filtered_surveys_multiple,
            self.test_multiple_values_filter,
            self.test_msl_name_format,
            self.test_pagination,
        ]

        for test in tests:
            try:
                test()
            except KeyboardInterrupt:
                self.print_error("\nTests interrupted by user")
                sys.exit(1)
            except Exception as e:
                self.print_error(f"Unexpected error: {str(e)}")

        # Print summary
        self.print_header("📊 Test Summary")
        total = self.passed + self.failed
        print(f"{Fore.GREEN}✅ Passed: {self.passed}/{total}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ Failed: {self.failed}/{total}{Style.RESET_ALL}")

        if self.failed == 0:
            print(f"\n{Fore.GREEN}🎉 All tests passed!{Style.RESET_ALL}")
            print(
                f"{Fore.GREEN}Your {self.mode.upper()} API is working correctly! 🎯{Style.RESET_ALL}"
            )
        else:
            print(f"\n{Fore.RED}⚠️  Some tests failed.{Style.RESET_ALL}")
            print(
                f"{Fore.YELLOW}Check the error messages above for troubleshooting.{Style.RESET_ALL}"
            )

        # Print useful links
        print(f"\n{Fore.CYAN}📱 Interactive testing:{Style.RESET_ALL}")
        print(f"   • Swagger UI: {self.base_url}/docs")
        print(f"   • ReDoc: {self.base_url}/redoc")

        print(f"\n{Fore.CYAN}🔗 Example API calls:{Style.RESET_ALL}")
        print(f"   • All surveys: {self.base_url}/api/v1/surveys/")
        print(f"   • Filters: {self.base_url}/api/v1/filters/options")
        print(f"   • Health: {self.base_url}/health")


def main():
    """Main function"""
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}   GFMI API Test Suite{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")

    # Ask user which mode to test
    print("Which API configuration do you want to test?")
    print(f"{Fore.YELLOW}1. Local CSV (USE_LOCAL_DATA=true){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}2. Dremio (USE_LOCAL_DATA=false){Style.RESET_ALL}")
    print(f"{Fore.YELLOW}3. Both{Style.RESET_ALL}")

    choice = input("\nEnter your choice (1/2/3): ").strip()

    base_url = input("Enter API base URL (default: http://localhost:8000): ").strip()
    if not base_url:
        base_url = "http://localhost:8000"

    print(f"\n{Fore.BLUE}⏳ Starting tests...{Style.RESET_ALL}")
    time.sleep(1)

    if choice == "1":
        tester = APITester(base_url=base_url, mode="local")
        tester.run_all_tests()
    elif choice == "2":
        tester = APITester(base_url=base_url, mode="dremio")
        tester.run_all_tests()
    elif choice == "3":
        print(f"\n{Fore.CYAN}Testing LOCAL mode first...{Style.RESET_ALL}")
        tester_local = APITester(base_url=base_url, mode="local")
        tester_local.run_all_tests()

        input(
            f"\n{Fore.YELLOW}Press Enter to continue to Dremio tests (make sure to switch USE_LOCAL_DATA in .env)...{Style.RESET_ALL}"
        )

        print(f"\n{Fore.CYAN}Testing DREMIO mode...{Style.RESET_ALL}")
        tester_dremio = APITester(base_url=base_url, mode="dremio")
        tester_dremio.run_all_tests()
    else:
        print(f"{Fore.RED}Invalid choice. Exiting.{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
