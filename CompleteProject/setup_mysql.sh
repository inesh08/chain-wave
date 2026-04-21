#!/bin/bash
# MySQL Setup Script for SCM Dashboard
# Run this script to set up MySQL database and initialize the schema

echo "============================================"
echo "SCM Dashboard - MySQL Setup"
echo "============================================"
echo ""

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL is not installed"
    echo "Please install MySQL first:"
    echo "  macOS: brew install mysql"
    echo "  Linux: sudo apt-get install mysql-server"
    echo "  Windows: Download from mysql.com"
    exit 1
fi

echo "✓ MySQL found"

# Check if MySQL is running
if ! mysql -e "SELECT 1" &> /dev/null; then
    echo "❌ MySQL is not running"
    echo "Please start MySQL:"
    echo "  macOS: brew services start mysql"
    echo "  Linux: sudo systemctl start mysql"
    echo "  Windows: net start MySQL80"
    exit 1
fi

echo "✓ MySQL is running"
echo ""

# Install Python packages
echo "Installing Python dependencies..."
pip install mysql-connector-python pandas plotly dash numpy

echo ""
echo "Initializing database schema..."
python init_db.py

echo ""
echo "Loading sample data..."
python sample_data.py

echo ""
echo "Migrating data to MySQL..."
python migrate_to_mysql.py

echo ""
echo "============================================"
echo "✓ Setup Complete!"
echo "============================================"
echo ""
echo "To start the dashboard, run:"
echo "  python dashboard.py"
echo ""
echo "Then open: http://localhost:8050"
