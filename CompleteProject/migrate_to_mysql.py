"""
Migrate CSV data to MySQL Database
Run this after init_db.py to populate the database with sample data
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'scm_dashboard'
}

def migrate_csv_to_mysql():
    """Migrate CSV files to MySQL"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # 1. Load and insert products
        print("Loading products...")
        products_df = pd.read_csv('products.csv')
        for _, row in products_df.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO products (product_id, name, category, unit_cost, supplier_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['product_id'], row['name'], row['category'], row['unit_cost'], row['supplier_id']))
        conn.commit()
        print(f"✓ Inserted {len(products_df)} products")

        # 2. Load and insert warehouses
        print("Loading warehouses...")
        warehouses_df = pd.read_csv('warehouses.csv')
        for _, row in warehouses_df.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO warehouses (warehouse_id, name, location, capacity)
                VALUES (%s, %s, %s, %s)
            """, (row['warehouse_id'], row['name'], row['location'], row['capacity']))
        conn.commit()
        print(f"✓ Inserted {len(warehouses_df)} warehouses")

        # 3. Load and insert suppliers
        print("Loading suppliers...")
        suppliers_df = pd.read_csv('suppliers.csv')
        for _, row in suppliers_df.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO suppliers (supplier_id, name, contact, lead_time_days)
                VALUES (%s, %s, %s, %s)
            """, (row['supplier_id'], row['name'], row['contact'], row['lead_time_days']))
        conn.commit()
        print(f"✓ Inserted {len(suppliers_df)} suppliers")

        # 4. Load and insert inventory
        print("Loading inventory...")
        inventory_df = pd.read_csv('inventory.csv')
        for _, row in inventory_df.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO inventory (inventory_id, product_id, warehouse_id, current_stock, safety_stock)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['inventory_id'], row['product_id'], row['warehouse_id'], row['current_stock'], row['safety_stock']))
        conn.commit()
        print(f"✓ Inserted {len(inventory_df)} inventory records")

        # 5. Load and insert orders
        print("Loading orders...")
        orders_df = pd.read_csv('orders.csv')
        for _, row in orders_df.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO orders (order_id, product_id, warehouse_id, quantity, order_date, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row['order_id'], row['product_id'], row['warehouse_id'], row['quantity'], row['order_date'], row['status']))
        conn.commit()
        print(f"✓ Inserted {len(orders_df)} orders")

        # 6. Load and insert demand_forecast
        print("Loading demand forecasts...")
        demand_forecast_df = pd.read_csv('demand_forecast.csv')
        for _, row in demand_forecast_df.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO demand_forecast (forecast_id, product_id, forecast_date, predicted_demand, confidence_level)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['forecast_id'], row['product_id'], row['forecast_date'], row['predicted_demand'], row['confidence_level']))
        conn.commit()
        print(f"✓ Inserted {len(demand_forecast_df)} demand forecasts")

        # 7. Load and insert costs
        print("Loading costs...")
        costs_df = pd.read_csv('costs.csv')
        for _, row in costs_df.iterrows():
            cursor.execute("""
                INSERT IGNORE INTO costs (cost_id, product_id, cost_type, amount, date)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['cost_id'], row['product_id'], row['cost_type'], row['amount'], row['date']))
        conn.commit()
        print(f"✓ Inserted {len(costs_df)} cost records")

        print("\n✓ All data migrated successfully to MySQL!")

    except Error as e:
        print(f"Error during migration: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    migrate_csv_to_mysql()
