import pandas as pd
import numpy as np
import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'MyNewPass123!',
    'database': 'scm_dashboard'
}

# Product names by category
electronics_names = [
    'Laptop', 'Smartphone', 'Tablet', 'Headphones', 'Smart Watch', 'Wireless Mouse', 'Keyboard', 'Monitor', 'Printer', 'Router',
    'External Hard Drive', 'USB Flash Drive', 'Bluetooth Speaker', 'Webcam', 'Graphics Card', 'Power Bank', 'Phone Case', 'Screen Protector', 'Cable Organizer', 'Gaming Console'
]

clothing_names = [
    'T-Shirt', 'Jeans', 'Jacket', 'Sneakers', 'Dress', 'Sweater', 'Hat', 'Socks', 'Gloves', 'Scarf',
    'Pants', 'Shirt', 'Coat', 'Boots', 'Sandals', 'Belt', 'Tie', 'Underwear', 'Bra', 'Shorts'
]

food_names = [
    'Rice', 'Milk', 'Bread', 'Apples', 'Bananas', 'Chicken', 'Beef', 'Eggs', 'Cheese', 'Yogurt',
    'Pasta', 'Tomatoes', 'Potatoes', 'Onions', 'Carrots', 'Orange Juice', 'Coffee', 'Tea', 'Sugar', 'Salt'
]

furniture_names = [
    'Chair', 'Table', 'Sofa', 'Desk', 'Bookshelf', 'Bed', 'Nightstand', 'Dresser', 'Cabinet', 'Lamp',
    'Ottoman', 'Rug', 'Curtains', 'Mirror', 'Clock', 'Vase', 'Picture Frame', 'Coat Rack', 'Bar Stool', 'Bean Bag'
]

# Create products with proper names
product_names = electronics_names + clothing_names + food_names + furniture_names
categories = (['Electronics'] * len(electronics_names) + 
              ['Clothing'] * len(clothing_names) + 
              ['Food'] * len(food_names) + 
              ['Furniture'] * len(furniture_names))

# Take first 50
product_names = product_names[:50]
categories = categories[:50]

products = pd.DataFrame({
    'product_id': range(1, 51),
    'name': product_names,
    'category': categories,
    'unit_cost': np.random.uniform(10, 100, 50).round(2),
    'supplier_id': np.random.randint(1, 11, 50)
})

# Warehouses
warehouses = pd.DataFrame({
    'warehouse_id': range(1, 6),
    'name': [f'Warehouse {i}' for i in range(1, 6)],
    'location': ['NY', 'CA', 'TX', 'FL', 'IL'],
    'capacity': np.random.randint(1000, 5000, 5)
})

# Inventory
inventory = pd.DataFrame({
    'inventory_id': range(1, 251),
    'product_id': np.tile(range(1, 51), 5),
    'warehouse_id': np.repeat(range(1, 6), 50),
    'current_stock': np.random.randint(10, 200, 250),
    'safety_stock': np.random.randint(5, 50, 250),
    'last_updated': pd.date_range('2023-01-01', periods=250, freq='D')[:250]
})

# Orders
orders = pd.DataFrame({
    'order_id': range(1, 1001),
    'product_id': np.random.randint(1, 51, 1000),
    'warehouse_id': np.random.randint(1, 6, 1000),
    'quantity': np.random.randint(1, 20, 1000),
    'order_date': pd.date_range('2023-01-01', periods=1000, freq='D')[:1000],
    'status': np.random.choice(['Pending', 'Fulfilled', 'Delayed'], 1000)
})

# Suppliers
suppliers = pd.DataFrame({
    'supplier_id': range(1, 11),
    'name': [f'Supplier {i}' for i in range(1, 11)],
    'contact': [f'contact{i}@supplier.com' for i in range(1, 11)],
    'lead_time_days': np.random.randint(1, 14, 10)
})

# Demand Forecast
demand_forecast = pd.DataFrame({
    'forecast_id': range(1, 151),
    'product_id': np.tile(range(1, 51), 3)[:150],
    'forecast_date': pd.date_range('2023-01-01', periods=150, freq='M')[:150],
    'predicted_demand': np.random.randint(50, 200, 150),
    'confidence_level': np.random.uniform(0.8, 0.95, 150).round(2)
})

# Costs
costs = pd.DataFrame({
    'cost_id': range(1, 201),
    'product_id': np.random.randint(1, 51, 200),
    'cost_type': np.random.choice(['Storage', 'Stockout', 'Transportation'], 200),
    'amount': np.random.uniform(5, 50, 200).round(2),
    'date': pd.date_range('2023-01-01', periods=200, freq='D')[:200]
})

# Save to CSV
products.to_csv('products.csv', index=False)
warehouses.to_csv('warehouses.csv', index=False)
inventory.to_csv('inventory.csv', index=False)
orders.to_csv('orders.csv', index=False)
suppliers.to_csv('suppliers.csv', index=False)
demand_forecast.to_csv('demand_forecast.csv', index=False)
costs.to_csv('costs.csv', index=False)

print("Sample data generated and saved as CSV files.")

# Also save to MySQL
def save_to_mysql():
    """Save data to MySQL database"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        print("\nSaving data to MySQL...")

        # Clear existing data
        cursor.execute("DELETE FROM costs")
        cursor.execute("DELETE FROM demand_forecast")
        cursor.execute("DELETE FROM orders")
        cursor.execute("DELETE FROM inventory")
        cursor.execute("DELETE FROM products")
        cursor.execute("DELETE FROM warehouses")
        cursor.execute("DELETE FROM suppliers")
        conn.commit()

        # Insert suppliers first
        for _, row in suppliers.iterrows():
            cursor.execute("""
                INSERT INTO suppliers (supplier_id, name, contact, lead_time_days)
                VALUES (%s, %s, %s, %s)
            """, (row['supplier_id'], row['name'], row['contact'], row['lead_time_days']))

        # Insert warehouses
        for _, row in warehouses.iterrows():
            cursor.execute("""
                INSERT INTO warehouses (warehouse_id, name, location, capacity)
                VALUES (%s, %s, %s, %s)
            """, (row['warehouse_id'], row['name'], row['location'], row['capacity']))

        # Insert products
        for _, row in products.iterrows():
            cursor.execute("""
                INSERT INTO products (product_id, name, category, unit_cost, supplier_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['product_id'], row['name'], row['category'], row['unit_cost'], row['supplier_id']))

        # Insert inventory
        for _, row in inventory.iterrows():
            cursor.execute("""
                INSERT INTO inventory (inventory_id, product_id, warehouse_id, current_stock, safety_stock)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['inventory_id'], row['product_id'], row['warehouse_id'], row['current_stock'], row['safety_stock']))

        # Insert orders
        for _, row in orders.iterrows():
            cursor.execute("""
                INSERT INTO orders (order_id, product_id, warehouse_id, quantity, order_date, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (row['order_id'], row['product_id'], row['warehouse_id'], row['quantity'], row['order_date'], row['status']))

        # Insert demand forecast
        for _, row in demand_forecast.iterrows():
            cursor.execute("""
                INSERT INTO demand_forecast (forecast_id, product_id, forecast_date, predicted_demand, confidence_level)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['forecast_id'], row['product_id'], row['forecast_date'], row['predicted_demand'], row['confidence_level']))

        # Insert costs
        for _, row in costs.iterrows():
            cursor.execute("""
                INSERT INTO costs (cost_id, product_id, cost_type, amount, date)
                VALUES (%s, %s, %s, %s, %s)
            """, (row['cost_id'], row['product_id'], row['cost_type'], row['amount'], row['date']))

        conn.commit()
        print("✓ Data saved to MySQL successfully!")

    except Error as e:
        print(f"Error saving to MySQL: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    try:
        save_to_mysql()
    except Exception as e:
        print(f"MySQL connection failed: {e}")
        print("Note: Make sure MySQL is running and init_db.py has been executed.")