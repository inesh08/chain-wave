"""
Initialize MySQL Database Schema for SCM Dashboard
Run this script once to set up the database structure
"""

import mysql.connector
from mysql.connector import Error

# MySQL connection for initial setup
INIT_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MyNewPass123!',
}

def init_database():
    """Create database and tables"""
    conn = None
    try:
        conn = mysql.connector.connect(**INIT_CONFIG)
        cursor = conn.cursor()

        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS scm_dashboard")
        print("✓ Database 'scm_dashboard' created/exists")

        # Use the database
        cursor.execute("USE scm_dashboard")

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                category VARCHAR(50) NOT NULL,
                unit_cost DECIMAL(10, 2) NOT NULL,
                supplier_id INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_product_name (name),
                INDEX idx_category (category),
                INDEX idx_supplier_id (supplier_id)
            )
        """)
        print("✓ Table 'products' created/exists")

        # Create warehouses table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS warehouses (
                warehouse_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                location VARCHAR(50) NOT NULL,
                capacity INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_warehouse_name (name),
                INDEX idx_location (location)
            )
        """)
        print("✓ Table 'warehouses' created/exists")

        # Create inventory table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                inventory_id INT PRIMARY KEY AUTO_INCREMENT,
                product_id INT NOT NULL,
                warehouse_id INT NOT NULL,
                current_stock INT NOT NULL,
                safety_stock INT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
                UNIQUE KEY unique_product_warehouse (product_id, warehouse_id),
                INDEX idx_product_id (product_id),
                INDEX idx_warehouse_id (warehouse_id)
            )
        """)
        print("✓ Table 'inventory' created/exists")

        # Create orders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id INT PRIMARY KEY AUTO_INCREMENT,
                product_id INT NOT NULL,
                warehouse_id INT NOT NULL,
                quantity INT NOT NULL,
                order_date DATE NOT NULL,
                status ENUM('Pending', 'Fulfilled', 'Delayed') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                FOREIGN KEY (warehouse_id) REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
                INDEX idx_product_id (product_id),
                INDEX idx_warehouse_id (warehouse_id),
                INDEX idx_order_date (order_date),
                INDEX idx_status (status)
            )
        """)
        print("✓ Table 'orders' created/exists")

        # Create suppliers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suppliers (
                supplier_id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                contact VARCHAR(100),
                lead_time_days INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_supplier_name (name),
                INDEX idx_lead_time (lead_time_days)
            )
        """)
        print("✓ Table 'suppliers' created/exists")

        # Create demand_forecast table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS demand_forecast (
                forecast_id INT PRIMARY KEY AUTO_INCREMENT,
                product_id INT NOT NULL,
                forecast_date DATE NOT NULL,
                predicted_demand INT NOT NULL,
                confidence_level DECIMAL(3, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                INDEX idx_product_id (product_id),
                INDEX idx_forecast_date (forecast_date)
            )
        """)
        print("✓ Table 'demand_forecast' created/exists")

        # Create costs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS costs (
                cost_id INT PRIMARY KEY AUTO_INCREMENT,
                product_id INT NOT NULL,
                cost_type ENUM('Storage', 'Stockout', 'Transportation') NOT NULL,
                amount DECIMAL(10, 2) NOT NULL,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
                INDEX idx_product_id (product_id),
                INDEX idx_cost_type (cost_type),
                INDEX idx_date (date)
            )
        """)
        print("✓ Table 'costs' created/exists")

        conn.commit()
        print("\n✓ Database initialization complete!")

    except Error as e:
        print(f"Error during database initialization: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    init_database()
