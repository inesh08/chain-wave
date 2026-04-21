"""
MySQL Database Configuration for SCM Dashboard
"""

import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MyNewPass123!',
    'database': 'scm_dashboard',
    'raise_on_warnings': True
}

def create_connection():
    """Create a database connection to MySQL"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            print("Successfully connected to MySQL database")
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return conn

def close_connection(conn):
    """Close the database connection"""
    if conn.is_connected():
        conn.close()
        print("MySQL connection closed")

def execute_query(conn, query, params=None):
    """Execute a single query"""
    cursor = conn.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        return cursor
    except Error as e:
        print(f"Query execution failed: {e}")
        conn.rollback()
        return None

def fetch_all(conn, query, params=None):
    """Fetch all results from a query"""
    cursor = conn.cursor(dictionary=True)
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"Query failed: {e}")
        return []
