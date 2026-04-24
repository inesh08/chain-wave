import dash
from dash import html, dcc, Input, Output, State, ALL, MATCH, callback_context
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
        html.Img(src=app.get_asset_url('logo.png'), style={'height': '150px', 'display': 'block', 'margin': '0 auto', 'marginBottom': '15px'}),
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
        html.P('© 2026 ChainWave | Supply Chain Management Platform | Built with Dash & Python'),
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
                dcc.Dropdown(id='warehouse-filter', options=[{'label': w, 'value': w} for w in warehouses_df['name']], value=warehouses_df['name'].iloc[0], className='dropdown', style={'flex': '1'}),
                dcc.Dropdown(id='category-filter', options=[{'label': 'All Categories', 'value': 'All'}] + [{'label': c, 'value': c} for c in products_df['category'].unique()], value='All', className='dropdown', style={'flex': '1'}),
                dcc.Dropdown(id='product-search', options=[{'label': p, 'value': p} for p in products_df['name']], placeholder="Search for an item (e.g. Laptop)...", searchable=True, clearable=True, className='dropdown', style={'flex': '2'}),
            ], className='filter-container', style={'display': 'flex', 'gap': '10px', 'marginBottom': '20px'}),
            html.Div([
                dcc.Graph(id='inventory-chart')
            ], className='chart-container'),
            html.Div([
                html.Table([
                    html.Thead(html.Tr([html.Th('Product'), html.Th('Category'), html.Th('Current Stock'), html.Th('Safety Stock'), html.Th('Status')])),
                    html.Tbody(id='inventory-table-body')
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
        
        # Calculate Category-wise Suggestions
        cat_stock = inventory_df.merge(products_df[['product_id', 'category']], on='product_id')
        cat_stock = cat_stock.groupby('category').agg({'current_stock': 'sum', 'safety_stock': 'sum'}).reset_index()
        
        num_months = demand_forecast_df['forecast_date'].nunique() or 1
        cat_demand = demand_forecast_df.merge(products_df[['product_id', 'category']], on='product_id')
        cat_demand = cat_demand.groupby('category')['predicted_demand'].sum().reset_index()
        cat_demand['avg_monthly_demand'] = cat_demand['predicted_demand'] / num_months
        
        suggestions_df = cat_stock.merge(cat_demand, on='category')
        
        recommendation_cards = []
        for _, row in suggestions_df.iterrows():
            stock = row['current_stock']
            safety_stock = row['safety_stock']
            demand = row['avg_monthly_demand']
            category = row['category']
            
            if stock < safety_stock:
                suggestion = "Critical - Below Safety Stock"
                color_class = "status-low"
                icon = "🚨"
            elif stock < 0.8 * demand:
                suggestion = "Low Stock - Restock Soon"
                color_class = "status-low"
                icon = "📦"
            elif stock < 1.1 * demand:
                suggestion = "Plan Restock - Low Buffer"
                color_class = "status-warning"
                icon = "⚠️"
            elif stock > 1.8 * demand:
                suggestion = "Overstocked - Consider Sale"
                color_class = "status-info"
                icon = "💰"
            else:
                suggestion = "Healthy Inventory Level"
                color_class = "status-ok"
                icon = "✅"
                
            recommendation_cards.append(html.Div([
                html.H4(f"{icon} {category}", style={'marginTop': '0'}),
                html.P([html.Strong("Action: "), html.Span(suggestion, className=color_class)]),
                html.Div([
                    html.P(f"Stock: {stock:,.0f}", style={'margin': '5px 0', 'fontSize': '0.9em'}),
                    html.P(f"Demand: {demand:,.0f}", style={'margin': '5px 0', 'fontSize': '0.9em'}),
                ], style={'display': 'flex', 'justifyContent': 'space-between', 'borderTop': '1px solid #eee', 'paddingTop': '10px'}),
                html.P("Click for product details →", style={'fontSize': '0.8em', 'color': '#007bff', 'marginTop': '10px', 'textAlign': 'right'})
            ], 
            id={'type': 'category-card', 'index': category},
            n_clicks=0,
            className='kpi-card', 
            style={'textAlign': 'left', 'minWidth': '280px', 'cursor': 'pointer'}))

        return html.Div([
            html.H2('📈 Demand Forecasting'),
            
            # Inventory Suggestions Section
            html.Div([
                html.H3('Inventory Suggestions', style={'marginBottom': '20px'}),
                html.Div(recommendation_cards, className='kpi-container', style={'justifyContent': 'flex-start'}),
                html.Div(id='product-suggestions-container', style={'marginTop': '20px'})
            ], className='chart-container'),
            
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
                    figure=px.line(
                        demand_with_products[demand_with_products['name'].isin(demand_with_products['name'].unique()[:30])], 
                        x='forecast_date', y='predicted_demand',
                        facet_col='name', facet_col_wrap=3,
                        title='Demand Forecasting of Products (Top 30)',
                        markers=True, color_discrete_sequence=px.colors.qualitative.Set3,
                        height=3500, facet_row_spacing=0.02
                    )
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

@app.callback(
    [Output('inventory-chart', 'figure'), Output('inventory-table-body', 'children')],
    [Input('warehouse-filter', 'value'), Input('category-filter', 'value'), Input('product-search', 'value')]
)
def update_inventory_chart(warehouse, category, product):
    df = inventory_merged[inventory_merged['name_y'] == warehouse]
    
    if product:
        df = df[df['name_x'] == product]
        title = f'Inventory in {warehouse} for {product}'
    else:
        if category != 'All':
            df = df[df['category'] == category]
        title = f'Inventory in {warehouse} for {category if category != "All" else "All Categories"}'
    
    fig = px.bar(df, x='name_x', y='current_stock', title=title)
    
    table_rows = []
    for _, row in df.head(50).iterrows():
        status_class = 'status-low' if row['current_stock'] < row['safety_stock'] else 'status-ok'
        status_text = 'Low Stock' if row['current_stock'] < row['safety_stock'] else 'OK'
        table_rows.append(html.Tr([
            html.Td(row['name_x']),
            html.Td(row['category']),
            html.Td(row['current_stock']),
            html.Td(row['safety_stock']),
            html.Td(status_text, className=status_class)
        ]))
        
    return fig, table_rows

@app.callback(
    Output('product-suggestions-container', 'children'),
    [Input({'type': 'category-card', 'index': ALL}, 'n_clicks')],
    [State({'type': 'category-card', 'index': ALL}, 'id')]
)
def display_product_suggestions(n_clicks, ids):
    ctx = dash.callback_context
    if not ctx.triggered or not any(n_clicks):
        return html.Div("Click on a category card above to see product-level predictions.", style={'color': '#6c757d', 'fontStyle': 'italic', 'textAlign': 'center', 'padding': '20px', 'background': '#f8f9fa', 'borderRadius': '10px', 'border': '1px dashed #ccc'})

    # Get the index of the clicked card
    clicked_prop_id = ctx.triggered[0]['prop_id']
    if 'index' not in clicked_prop_id:
        return dash.no_update
        
    import json
    clicked_id_str = clicked_prop_id.split('.')[0]
    clicked_index = json.loads(clicked_id_str)['index']

    # Filter data for this category
    cat_products = products_df[products_df['category'] == clicked_index]
    cat_inventory = inventory_df[inventory_df['product_id'].isin(cat_products['product_id'])]
    
    num_months = demand_forecast_df['forecast_date'].nunique() or 1
    cat_demand = demand_forecast_df[demand_forecast_df['product_id'].isin(cat_products['product_id'])]
    cat_demand_agg = cat_demand.groupby('product_id')['predicted_demand'].sum().reset_index()
    cat_demand_agg['avg_monthly_demand'] = cat_demand_agg['predicted_demand'] / num_months
    
    # Merge for details
    merged = cat_inventory.merge(cat_products, on='product_id').merge(cat_demand_agg, on='product_id')
    
    rows = []
    for _, row in merged.head(20).iterrows():
        stock = row['current_stock']
        safety_stock = row['safety_stock']
        demand = row['avg_monthly_demand']
        
        if stock < safety_stock:
            suggestion, color_class = "Critical", "status-low"
        elif stock < 0.8 * demand:
            suggestion, color_class = "Restock", "status-low"
        elif stock < 1.1 * demand:
            suggestion, color_class = "Plan Restock", "status-warning"
        elif stock > 1.8 * demand:
            suggestion, color_class = "Overstock", "status-info"
        else:
            suggestion, color_class = "Healthy", "status-ok"
            
        rows.append(html.Tr([
            html.Td(row['name']),
            html.Td(f"{stock:,.0f}"),
            html.Td(f"{demand:,.0f}"),
            html.Td(suggestion, className=color_class)
        ]))

    return html.Div([
        html.H4(f"📦 Product-Level Suggestions: {clicked_index}", style={'marginBottom': '15px', 'color': '#764ba2'}),
        html.Table([
            html.Thead(html.Tr([
                html.Th("Product Name"),
                html.Th("Stock"),
                html.Th("Forecast"),
                html.Th("Action")
            ])),
            html.Tbody(rows)
        ])
    ], className='table-container', style={'marginTop': '20px', 'borderTop': '2px solid #764ba2'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
