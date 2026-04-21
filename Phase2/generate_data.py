import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate inventory data
products = [f'SKU{i:03d}' for i in range(1, 101)]
warehouses = ['WH001', 'WH002', 'WH003', 'WH004', 'WH005']

inventory_data = []
for product in products:
    for warehouse in warehouses:
        current_stock = np.random.randint(50, 500)
        safety_stock = np.random.randint(20, 100)
        inventory_data.append({
            'SKU_ID': product,
            'Warehouse_ID': warehouse,
            'Current_Stock': current_stock,
            'Safety_Stock': safety_stock
        })

inventory_df = pd.DataFrame(inventory_data)
inventory_df.to_csv('inventory.csv', index=False)

# Generate orders data (6 months)
start_date = datetime(2023, 10, 1)
end_date = datetime(2024, 4, 1)
dates = pd.date_range(start_date, end_date, freq='D')

orders_data = []
order_id = 1
for date in dates:
    num_orders = np.random.poisson(10)  # Average 10 orders per day
    for _ in range(num_orders):
        sku = random.choice(products)
        warehouse = random.choice(warehouses)
        quantity = np.random.randint(1, 50)
        lead_time = np.random.randint(1, 14)  # 1-14 days
        # Simulate bottlenecks: occasional delays
        if random.random() < 0.05:  # 5% chance
            lead_time += np.random.randint(5, 15)
        fulfillment_status = 'Fulfilled' if random.random() > 0.1 else 'Delayed'  # 10% delayed
        orders_data.append({
            'Order_ID': order_id,
            'Order_Date': date.strftime('%Y-%m-%d'),
            'SKU_ID': sku,
            'Warehouse_ID': warehouse,
            'Quantity': quantity,
            'Lead_Time_Days': lead_time,
            'Fulfillment_Status': fulfillment_status
        })
        order_id += 1

orders_df = pd.DataFrame(orders_data)
orders_df.to_csv('orders.csv', index=False)

# Generate costs data
costs_data = []
for product in products:
    storage_cost_per_unit = round(np.random.uniform(0.5, 5.0), 2)
    stockout_penalty_per_unit = round(np.random.uniform(10, 50), 2)
    costs_data.append({
        'SKU_ID': product,
        'Storage_Cost_Per_Unit': storage_cost_per_unit,
        'Stockout_Penalty_Per_Unit': stockout_penalty_per_unit
    })

costs_df = pd.DataFrame(costs_data)
costs_df.to_csv('costs.csv', index=False)

print("Data generation complete. Files: inventory.csv, orders.csv, costs.csv")