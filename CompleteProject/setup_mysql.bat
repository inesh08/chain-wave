@echo off
REM MySQL Setup Script for SCM Dashboard (Windows)
REM Run this batch file to set up MySQL database and initialize the schema

echo ============================================
echo SCM Dashboard - MySQL Setup (Windows)
echo ============================================
echo.

REM Check if MySQL is installed
mysql -v >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ MySQL is not installed or not in PATH
    echo Please install MySQL first from: https://mysql.com
    pause
    exit /b 1
)

echo ✓ MySQL found
echo.

REM Install Python packages
echo Installing Python dependencies...
pip install mysql-connector-python pandas plotly dash numpy

echo.
echo Initializing database schema...
python init_db.py

echo.
echo Loading sample data...
python sample_data.py

echo.
echo Migrating data to MySQL...
python migrate_to_mysql.py

echo.
echo ============================================
echo ✓ Setup Complete!
echo ============================================
echo.
echo To start the dashboard, run:
echo   python dashboard.py
echo.
echo Then open: http://localhost:8050
echo.
pause
