import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
from db_config import DB_CONFIG, create_connection, fetch_all

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Load data from MySQL
print("Loading data from MySQL database...")
conn = create_connection()

if conn:
    # Fetch all data from MySQL
    products_df = pd.DataFrame(fetch_all(conn, "SELECT * FROM products"))
    warehouses_df = pd.DataFrame(fetch_all(conn, "SELECT * FROM warehouses"))
    inventory_df = pd.DataFrame(fetch_all(conn, "SELECT * FROM inventory"))
    orders_df = pd.DataFrame(fetch_all(conn, "SELECT * FROM orders"))
    suppliers_df = pd.DataFrame(fetch_all(conn, "SELECT * FROM suppliers"))
    demand_forecast_df = pd.DataFrame(fetch_all(conn, "SELECT * FROM demand_forecast"))
    costs_df = pd.DataFrame(fetch_all(conn, "SELECT * FROM costs"))
    
    conn.close()
    print("✓ Data loaded from MySQL successfully")
else:
    # Fallback to CSV if MySQL is not available
    print("MySQL connection failed. Falling back to CSV files...")
    products_df = pd.read_csv('products.csv')
    warehouses_df = pd.read_csv('warehouses.csv')
    inventory_df = pd.read_csv('inventory.csv')
    orders_df = pd.read_csv('orders.csv')
    suppliers_df = pd.read_csv('suppliers.csv')
    demand_forecast_df = pd.read_csv('demand_forecast.csv')
    costs_df = pd.read_csv('costs.csv')

# Load ML predictions if available
try:
    demand_pred_df = pd.read_csv('../Phase3/demand_predictions.csv')
except FileNotFoundError:
    demand_pred_df = pd.DataFrame({'Month': ['Month 1', 'Month 2', 'Month 3'], 'Predicted_Demand': [100, 120, 110]})

# Merge data for analysis
inventory_merged = inventory_df.merge(products_df, on='product_id').merge(warehouses_df, on='warehouse_id')
orders_merged = orders_df.merge(products_df, on='product_id').merge(warehouses_df, on='warehouse_id')

# Calculate KPIs
total_inventory_value = (inventory_merged['current_stock'] * inventory_merged['unit_cost']).sum()
stockout_rate = (orders_df['status'] == 'Delayed').sum() / len(orders_df) * 100
inventory_turnover = 12  # Simplified calculation
fill_rate = (orders_df['status'] == 'Fulfilled').sum() / len(orders_df) * 100
warehouse_utilization = (inventory_merged['current_stock'].sum() / warehouses_df['capacity'].sum()) * 100
demand_accuracy = 85  # Placeholder

# App
app = dash.Dash(__name__, suppress_callback_exceptions=True, assets_folder='assets')

app.layout = html.Div([
    html.Div([
        html.H1('🏭 SCM Centralized Monitoring Dashboard'),
        html.P('Real-time Supply Chain Analytics & Insights', style={'margin': '10px 0', 'opacity': '0.8'})
    ], className='header'),
    dcc.Tabs(id='tabs', value='executive', className='tabs', children=[
        dcc.Tab(label='📊 Executive Dashboard', value='executive', className='tab'),
        dcc.Tab(label='📦 Inventory Monitoring', value='inventory', className='tab'),
        dcc.Tab(label='🏭 Warehouse Monitoring', value='warehouse', className='tab'),
        dcc.Tab(label='📈 Demand Forecasting', value='demand', className='tab'),
        dcc.Tab(label='💰 Cost Monitoring', value='cost', className='tab'),
        dcc.Tab(label='🚚 Order Monitoring', value='order', className='tab'),
    ]),
    html.Div(id='tab-content'),
    html.Div([
        html.P('© 2026 SCM Project | Built with Dash & Python'),
    ], className='footer')
])

@app.callback(Output('tab-content', 'children'), Input('tabs', 'value'))
def render_content(tab):
    if tab == 'executive':
        return html.Div([
            html.H2('📊 Executive Dashboard'),
            html.Div([
                html.Div([
                    html.H3(f'${total_inventory_value:,.0f}'),
                    html.P('Total Inventory Value')
                ], className='kpi-card'),
                html.Div([
                    html.H3(f'{stockout_rate:.1f}%'),
                    html.P('Stockout Rate')
                ], className='kpi-card'),
                html.Div([
                    html.H3(f'{inventory_turnover}'),
                    html.P('Inventory Turnover')
                ], className='kpi-card'),
                html.Div([
                    html.H3(f'{fill_rate:.1f}%'),
                    html.P('Fill Rate')
                ], className='kpi-card'),
                html.Div([
                    html.H3(f'{warehouse_utilization:.1f}%'),
                    html.P('Warehouse Utilization')
                ], className='kpi-card'),
                html.Div([
                    html.H3(f'{demand_accuracy}%'),
                    html.P('Demand Forecast Accuracy')
                ], className='kpi-card'),
            ], className='kpi-container'),
            html.Div([
                dcc.Graph(
                    figure=px.bar(inventory_merged.groupby('category')['current_stock'].sum().reset_index(),
                                 x='category', y='current_stock', title='Inventory by Category',
                                 color='category', color_discrete_sequence=px.colors.qualitative.Set3)
                )
            ], className='chart-container')
        ])
    elif tab == 'inventory':
        return html.Div([
            html.H2('📦 Inventory Monitoring'),
            html.Div([
                dcc.Dropdown(id='warehouse-filter', options=[{'label': w, 'value': w} for w in warehouses_df['name']], value=warehouses_df['name'].iloc[0], className='dropdown'),
                dcc.Dropdown(id='category-filter', options=[{'label': c, 'value': c} for c in products_df['category'].unique()], value=products_df['category'].unique()[0], className='dropdown'),
            ], className='filter-container'),
            html.Div([
                dcc.Graph(id='inventory-chart')
            ], className='chart-container'),
            html.Div([
                html.Table([
                    html.Thead(html.Tr([html.Th('Product'), html.Th('Current Stock'), html.Th('Safety Stock'), html.Th('Status')])),
                    html.Tbody([
                        html.Tr([
                            html.Td(row['name_x']),
                            html.Td(row['current_stock']),
                            html.Td(row['safety_stock']),
                            html.Td('Low Stock', className='status-low') if row['current_stock'] < row['safety_stock'] else html.Td('OK', className='status-ok')
                        ])
                        for _, row in inventory_merged.head(10).iterrows()
                    ])
                ])
            ], className='table-container')
        ])
    elif tab == 'warehouse':
        return html.Div([
            html.H2('🏭 Warehouse Monitoring'),
            html.Div([
                dcc.Graph(
                    figure=px.bar(warehouses_df, x='name', y='capacity', title='Warehouse Capacities',
                                 color='name', color_discrete_sequence=px.colors.qualitative.Pastel)
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.pie(orders_df, names='status', title='Order Status Distribution',
                                 color='status', color_discrete_map={'Fulfilled':'#28a745', 'Pending':'#ffc107', 'Delayed':'#dc3545'})
                )
            ], className='chart-container')
        ])
    elif tab == 'demand':
        # Merge demand forecast with products to get categories and names
        demand_with_products = demand_forecast_df.merge(products_df, on='product_id')
        
        return html.Div([
            html.H2('📈 Demand Forecasting'),
            
            # Demand by Category - Separate graphs with better spacing
            html.Div([
                dcc.Graph(
                    figure=px.line(demand_with_products, x='forecast_date', y='predicted_demand', 
                                  facet_col='category', facet_col_wrap=1,
                                  title='Demand Forecast by Category',
                                  markers=True, color_discrete_sequence=px.colors.qualitative.Set3,
                                  height=900, facet_row_spacing=0.05)
                )
            ], className='chart-container'),
            
            # Demand by Product - Separate graphs with better spacing
            html.Div([
                dcc.Graph(
                    figure=px.line(demand_with_products, x='forecast_date', y='predicted_demand',
                                  facet_col='name', facet_col_wrap=3,
                                  title='Demand Forecasting of Products',
                                  markers=True, color_discrete_sequence=px.colors.qualitative.Set3,
                                  height=3500, facet_row_spacing=0.02)
                )
            ], className='chart-container'),
            
            # ML Predictions
            html.Div([
                dcc.Graph(
                    figure=px.bar(demand_pred_df, x='Month', y='Predicted_Demand', title='ML Predicted Demand for Next 3 Months',
                                 color='Predicted_Demand', color_continuous_scale='Blues')
                )
            ], className='chart-container')
        ])
    elif tab == 'cost':
        return html.Div([
            html.H2('💰 Cost Monitoring'),
            html.Div([
                dcc.Graph(
                    figure=px.pie(costs_df, names='cost_type', values='amount', title='Cost Breakdown',
                                 color='cost_type', color_discrete_sequence=px.colors.qualitative.Set1)
                )
            ], className='chart-container'),
            html.Div([
                dcc.Graph(
                    figure=px.bar(costs_df.groupby('cost_type')['amount'].sum().reset_index(),
                                 x='cost_type', y='amount', title='Total Costs by Type',
                                 color='cost_type', color_discrete_sequence=px.colors.qualitative.Set1)
                )
            ], className='chart-container')
        ])
    elif tab == 'order':
        return html.Div([
            html.H2('🚚 Order Monitoring'),
            html.Div([
                dcc.Graph(
                    figure=px.histogram(orders_df, x='order_date', title='Orders Over Time',
                                       color_discrete_sequence=['#007bff'])
                )
            ], className='chart-container'),
            html.Div([
                html.Table([
                    html.Thead(html.Tr([html.Th('Order ID'), html.Th('Product'), html.Th('Warehouse'), html.Th('Status')])),
                    html.Tbody([
                        html.Tr([
                            html.Td(row['order_id']),
                            html.Td(products_df.loc[products_df['product_id'] == row['product_id'], 'name'].iloc[0]),
                            html.Td(warehouses_df.loc[warehouses_df['warehouse_id'] == row['warehouse_id'], 'name'].iloc[0]),
                            html.Td(row['status'], className='status-ok' if row['status'] == 'Fulfilled' else 'status-low' if row['status'] == 'Delayed' else '')
                        ])
                        for _, row in orders_df.head(10).iterrows()
                    ])
                ])
            ], className='table-container')
        ])

@app.callback(Output('inventory-chart', 'figure'), Input('warehouse-filter', 'value'), Input('category-filter', 'value'))
def update_inventory_chart(warehouse, category):
    df = inventory_merged[(inventory_merged['name_y'] == warehouse) & (inventory_merged['category'] == category)]
    return px.bar(df, x='name_x', y='current_stock', title=f'Inventory in {warehouse} for {category}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
