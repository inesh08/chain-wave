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

# Dynamic Product Generation (150 per category)
NUM_PER_CATEGORY = 150
product_names = []
categories = []

for cat, base_names in [('Electronics', electronics_names), ('Clothing', clothing_names), ('Food', food_names), ('Furniture', furniture_names)]:
    for i in range(NUM_PER_CATEGORY):
        base_name = base_names[i % len(base_names)]
        suffix = f" v{i // len(base_names) + 1}" if i >= len(base_names) else ""
        product_names.append(f"{base_name}{suffix}")
        categories.append(cat)

TOTAL_PRODUCTS = len(product_names)

products = pd.DataFrame({
    'product_id': range(1, TOTAL_PRODUCTS + 1),
    'name': product_names,
    'category': categories,
    'unit_cost': np.random.uniform(10, 100, TOTAL_PRODUCTS).round(2),
    'supplier_id': np.random.randint(1, 11, TOTAL_PRODUCTS)
})

# Warehouses
NUM_WAREHOUSES = 5
warehouses = pd.DataFrame({
    'warehouse_id': range(1, NUM_WAREHOUSES + 1),
    'name': [f'Warehouse {i}' for i in range(1, NUM_WAREHOUSES + 1)],
    'location': ['NY', 'CA', 'TX', 'FL', 'IL'],
    'capacity': np.random.randint(1000, 5000, NUM_WAREHOUSES)
})

# Inventory
NUM_INVENTORY = TOTAL_PRODUCTS * NUM_WAREHOUSES
inventory = pd.DataFrame({
    'inventory_id': range(1, NUM_INVENTORY + 1),
    'product_id': np.tile(range(1, TOTAL_PRODUCTS + 1), NUM_WAREHOUSES),
    'warehouse_id': np.repeat(range(1, NUM_WAREHOUSES + 1), TOTAL_PRODUCTS),
    'current_stock': np.random.randint(10, 200, NUM_INVENTORY),
    'safety_stock': np.random.randint(5, 50, NUM_INVENTORY),
    'last_updated': np.random.choice(pd.date_range('2023-01-01', periods=365, freq='D'), NUM_INVENTORY)
})

# Orders
NUM_ORDERS = 2000
orders = pd.DataFrame({
    'order_id': range(1, NUM_ORDERS + 1),
    'product_id': np.random.randint(1, TOTAL_PRODUCTS + 1, NUM_ORDERS),
    'warehouse_id': np.random.randint(1, NUM_WAREHOUSES + 1, NUM_ORDERS),
    'quantity': np.random.randint(1, 20, NUM_ORDERS),
    'order_date': np.random.choice(pd.date_range('2023-01-01', periods=365, freq='D'), NUM_ORDERS),
    'status': np.random.choice(['Pending', 'Fulfilled', 'Delayed'], NUM_ORDERS)
})

# Suppliers
NUM_SUPPLIERS = 10
suppliers = pd.DataFrame({
    'supplier_id': range(1, NUM_SUPPLIERS + 1),
    'name': [f'Supplier {i}' for i in range(1, NUM_SUPPLIERS + 1)],
    'contact': [f'contact{i}@supplier.com' for i in range(1, NUM_SUPPLIERS + 1)],
    'lead_time_days': np.random.randint(1, 14, NUM_SUPPLIERS)
})

# Demand Forecast
NUM_FORECASTS = TOTAL_PRODUCTS * 3
demand_forecast = pd.DataFrame({
    'forecast_id': range(1, NUM_FORECASTS + 1),
    'product_id': np.tile(range(1, TOTAL_PRODUCTS + 1), 3),
    'forecast_date': np.repeat(pd.date_range('2023-01-01', periods=3, freq='MS'), TOTAL_PRODUCTS),
    'predicted_demand': np.random.randint(50, 200, NUM_FORECASTS),
    'confidence_level': np.random.uniform(0.8, 0.95, NUM_FORECASTS).round(2)
})

# Costs
NUM_COSTS = 1000
costs = pd.DataFrame({
    'cost_id': range(1, NUM_COSTS + 1),
    'product_id': np.random.randint(1, TOTAL_PRODUCTS + 1, NUM_COSTS),
    'cost_type': np.random.choice(['Storage', 'Stockout', 'Transportation'], NUM_COSTS),
    'amount': np.random.uniform(5, 50, NUM_COSTS).round(2),
    'date': np.random.choice(pd.date_range('2023-01-01', periods=365, freq='D'), NUM_COSTS)
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