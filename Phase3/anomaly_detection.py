import pandas as pd

# Load inventory data
inventory_df = pd.read_csv('../Phase2/inventory.csv')

# Assume storage capacity is safety_stock * 3 (arbitrary)
inventory_df['Capacity'] = inventory_df['Safety_Stock'] * 3

# Excess inventory if current_stock > 1.2 * capacity
inventory_df['Excess_Percentage'] = ((inventory_df['Current_Stock'] - inventory_df['Capacity']) / inventory_df['Capacity']) * 100
inventory_df['Excess_Flag'] = inventory_df['Excess_Percentage'] > 20

# Filter anomalies
anomalies = inventory_df[inventory_df['Excess_Flag']]
print("Warehouses with excess inventory >20%:")
print(anomalies[['Warehouse_ID', 'SKU_ID', 'Current_Stock', 'Capacity', 'Excess_Percentage']])

# Save to CSV
anomalies.to_csv('anomalies.csv', index=False)