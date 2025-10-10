@echo off
REM Quick script to set up and run GFMI backend locally

echo 🚀 GFMI Local Backend Setup
echo ============================

echo.
echo 1️⃣ Installing requirements...
pip install -r requirements-local.txt

echo.
echo 2️⃣ Setting up local database...
python local_db_setup.py

echo.
echo 3️⃣ Starting API server...
echo Visit: http://localhost:8000/docs
echo.
uvicorn app.main:app --reload
