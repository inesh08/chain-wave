import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Load data
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
        return html.Div([
            html.H2('📈 Demand Forecasting'),
            html.Div([
                dcc.Graph(
                    figure=px.line(demand_forecast_df.head(20), x='forecast_date', y='predicted_demand',
                                  title='Demand Forecast for Sample Products', markers=True)
                )
            ], className='chart-container'),
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

app.layout = html.Div([
    # Sidebar
    html.Div([
        html.Div([
            html.Button('☰', id='sidebar-toggle', className='sidebar-toggle'),
        ], className='sidebar-header'),
        html.Div([
            html.Div([
                html.Span(item['icon'], className='nav-icon'),
                html.Span(item['label'], className='nav-label')
            ], id=f'nav-{item["id"]}', className='nav-item', **{'data-page': item['id']})
            for item in nav_items
        ])
    ], id='sidebar', className='sidebar'),

    # Header
    html.Div([
        html.H1('Centralized Supply Chain Monitoring', className='header-title'),
        html.Div([
            dcc.DatePickerRange(
                id='date-filter',
                start_date=datetime.now().date(),
                end_date=datetime.now().date(),
                className='date-filter'
            ),
            dcc.Dropdown(
                id='warehouse-filter',
                options=[{'label': w, 'value': w} for w in warehouses_df['name']],
                value=warehouses_df['name'].iloc[0],
                className='warehouse-filter'
            ),
            html.Button('🔔', className='notifications'),
            html.Button('👤', className='profile'),
        ], className='header-controls')
    ], className='header'),

    # Main Content
    html.Div(id='page-content', className='main-content')
])

# Callback for sidebar toggle
@app.callback(
    [Output('sidebar', 'className'), Output('page-content', 'className')],
    Input('sidebar-toggle', 'n_clicks'),
    State('sidebar', 'className')
)
def toggle_sidebar(n_clicks, current_class):
    if n_clicks and n_clicks % 2 == 1:
        return 'sidebar collapsed', 'main-content'
    return 'sidebar', 'main-content'

# Callback for navigation
@app.callback(
    Output('page-content', 'children'),
    [Input(f'nav-{item["id"]}', 'n_clicks') for item in nav_items],
    [State('date-filter', 'start_date'), State('date-filter', 'end_date'), State('warehouse-filter', 'value')]
)
def display_page(*args):
    ctx = dash.callback_context
    if not ctx.triggered:
        return render_executive_page(None, None, None)

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    page = button_id.replace('nav-', '') if button_id.startswith('nav-') else 'executive'

    start_date, end_date, warehouse = args[-3:]

    if page == 'executive':
        return render_executive_page(start_date, end_date, warehouse)
    elif page == 'inventory':
        return render_inventory_page(start_date, end_date, warehouse)
    elif page == 'warehouse':
        return render_warehouse_page(start_date, end_date, warehouse)
    elif page == 'demand':
        return render_demand_page(start_date, end_date, warehouse)
    elif page == 'orders':
        return render_orders_page(start_date, end_date, warehouse)
    elif page == 'cost':
        return render_cost_page(start_date, end_date, warehouse)
    elif page == 'alerts':
        return render_alerts_page(start_date, end_date, warehouse)
    else:
        return render_executive_page(start_date, end_date, warehouse)

def render_executive_page(start_date, end_date, warehouse):
    # KPI Gauges
    kpi_gauges = [
        create_gauge('Total Inventory Value', f'${total_inventory_value:,.0f}', total_inventory_value / 1000000 * 100),
        create_gauge('Stockout Rate', f'{stockout_rate:.1f}%', stockout_rate),
        create_gauge('Warehouse Utilization', f'{warehouse_utilization:.1f}%', warehouse_utilization),
        create_gauge('Demand Forecast Accuracy', f'{demand_accuracy}%', demand_accuracy),
        create_gauge('Revenue at Risk', f'${revenue_at_risk:,.0f}', revenue_at_risk / total_inventory_value * 100),
    ]

    return html.Div([
        # KPI Cards
        html.Div(kpi_gauges, className='kpi-container'),

        # Charts
        html.Div([
            html.Div([
                dcc.Graph(figure=create_inventory_bar_chart())
            ], className='chart-section'),
            html.Div([
                dcc.Graph(figure=create_stock_pie_chart())
            ], className='chart-section'),
            html.Div([
                dcc.Graph(figure=create_inventory_trend_chart())
            ], className='chart-section'),
        ], className='chart-grid'),

        # Demand Section
        html.Div([
            html.H3('Demand Analytics', className='chart-title'),
            html.Div([
                dcc.Graph(figure=create_demand_forecast_chart())
            ], className='chart-section'),
            html.Div([
                dcc.Graph(figure=create_demand_supply_area_chart())
            ], className='chart-section'),
        ]),

        # Alerts
        html.Div([
            html.H3('Active Alerts', className='chart-title'),
            html.Div([
                html.Div([
                    html.Span('⚠️', className='alert-icon'),
                    html.Div([
                        html.H4('Low Stock Alert'),
                        html.P('5 products below safety stock levels')
                    ], className='alert-text')
                ], className='alert-card'),
                html.Div([
                    html.Span('📉', className='alert-icon'),
                    html.Div([
                        html.H4('Excess Inventory'),
                        html.P('Warehouse A has 15% overcapacity')
                    ], className='alert-text')
                ], className='alert-card'),
                html.Div([
                    html.Span('📈', className='alert-icon'),
                    html.Div([
                        html.H4('Demand Spike'),
                        html.P('Product X demand increased 40% this week')
                    ], className='alert-text')
                ], className='alert-card'),
            ])
        ], className='alerts-section'),

        # Bottom Charts
        html.Div([
            html.Div([
                dcc.Graph(figure=create_performance_chart())
            ], className='chart-section'),
            html.Div([
                dcc.Graph(figure=create_forecast_trend_chart())
            ], className='chart-section'),
            html.Div([
                dcc.Graph(figure=create_cost_monitoring_chart())
            ], className='chart-section'),
        ], className='bottom-charts')
    ])

def create_gauge(title, value, percentage):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=percentage,
        title={'text': title, 'font': {'size': 14, 'color': '#B0B3B8'}},
        number={'font': {'size': 24, 'color': '#FFFFFF'}},
        gauge={
            'axis': {'range': [None, 100], 'tickcolor': '#B0B3B8'},
            'bar': {'color': '#FF3B3B'},
            'bgcolor': '#1A1F2E',
            'borderwidth': 2,
            'bordercolor': '#FF3B3B',
            'steps': [
                {'range': [0, 50], 'color': '#1A1F2E'},
                {'range': [50, 80], 'color': '#2A2F3E'},
                {'range': [80, 100], 'color': '#3A3F4E'}
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return dcc.Graph(figure=fig, className='kpi-gauge')

def create_inventory_bar_chart():
    fig = px.bar(
        inventory_merged.groupby('name_y')['current_stock'].sum().reset_index(),
        x='name_y', y='current_stock',
        title='Inventory by Warehouse',
        color='name_y',
        color_discrete_sequence=['#FF3B3B', '#FF6B6B', '#FFB3B3']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        title_font={'color': '#FFFFFF'}
    )
    return fig

def create_stock_pie_chart():
    stock_status = pd.DataFrame({
        'Status': ['In Stock', 'Low Stock', 'Out of Stock'],
        'Count': [85, 10, 5]
    })
    fig = px.pie(
        stock_status, names='Status', values='Count',
        title='Stock Status Distribution',
        color_discrete_sequence=['#FF3B3B', '#FF6B6B', '#FFB3B3']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        title_font={'color': '#FFFFFF'}
    )
    return fig

def create_inventory_trend_chart():
    # Sample trend data
    trend_data = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
        'Inventory_Level': [1000 + i*10 + (i%7)*50 for i in range(30)]
    })
    fig = px.line(
        trend_data, x='Date', y='Inventory_Level',
        title='Inventory Trend Over Time',
        color_discrete_sequence=['#FF3B3B']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        title_font={'color': '#FFFFFF'}
    )
    return fig

def create_demand_forecast_chart():
    fig = px.line(
        demand_forecast_df.head(20), x='forecast_date', y='predicted_demand',
        title='Demand Forecast',
        markers=True,
        color_discrete_sequence=['#FF3B3B']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        title_font={'color': '#FFFFFF'}
    )
    return fig

def create_demand_supply_area_chart():
    # Sample demand vs supply data
    ds_data = pd.DataFrame({
        'Date': pd.date_range(start='2023-01-01', periods=30, freq='D'),
        'Demand': [100 + i*2 for i in range(30)],
        'Supply': [95 + i*2 + (i%5)*10 for i in range(30)]
    })
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=ds_data['Date'], y=ds_data['Demand'], fill='tozeroy', name='Demand', line_color='#FF3B3B'))
    fig.add_trace(go.Scatter(x=ds_data['Date'], y=ds_data['Supply'], fill='tonexty', name='Supply', line_color='#FF6B6B'))
    fig.update_layout(
        title='Demand vs Supply',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        title_font={'color': '#FFFFFF'}
    )
    return fig

def create_performance_chart():
    perf_data = pd.DataFrame({
        'Metric': ['On-Time Delivery', 'Order Accuracy', 'Inventory Turnover', 'Cost Efficiency'],
        'Value': [92, 96, 8.5, 88]
    })
    fig = px.bar(
        perf_data, x='Metric', y='Value',
        title='Supply Chain Performance Metrics',
        color='Metric',
        color_discrete_sequence=['#FF3B3B', '#FF6B6B', '#FFB3B3', '#FF8B8B']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        title_font={'color': '#FFFFFF'}
    )
    return fig

def create_forecast_trend_chart():
    fig = px.line(
        demand_pred_df, x='Month', y='Predicted_Demand',
        title='Forecast Trend',
        markers=True,
        color_discrete_sequence=['#FF3B3B']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        title_font={'color': '#FFFFFF'}
    )
    return fig

def create_cost_monitoring_chart():
    fig = px.bar(
        costs_df.groupby('cost_type')['amount'].sum().reset_index(),
        x='cost_type', y='amount',
        title='Cost Monitoring by Type',
        color='cost_type',
        color_discrete_sequence=['#FF3B3B', '#FF6B6B', '#FFB3B3']
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': '#FFFFFF'},
        title_font={'color': '#FFFFFF'}
    )
    return fig

# Placeholder functions for other pages
def render_inventory_page(start_date, end_date, warehouse):
    return html.Div([
        html.H2('📦 Inventory Monitoring'),
        html.P('Detailed inventory analytics and management tools.')
    ])

def render_warehouse_page(start_date, end_date, warehouse):
    return html.Div([
        html.H2('🏭 Warehouse Monitoring'),
        html.P('Warehouse performance and utilization metrics.')
    ])

def render_demand_page(start_date, end_date, warehouse):
    return html.Div([
        html.H2('📈 Demand Forecasting'),
        html.P('Advanced demand prediction and analytics.')
    ])

def render_orders_page(start_date, end_date, warehouse):
    return html.Div([
        html.H2('💰 Orders Dashboard'),
        html.P('Order management and fulfillment tracking.')
    ])

def render_cost_page(start_date, end_date, warehouse):
    return html.Div([
        html.H2('📊 Cost Monitoring'),
        html.P('Cost analysis and optimization insights.')
    ])

def render_alerts_page(start_date, end_date, warehouse):
    return html.Div([
        html.H2('🚨 Alerts & Notifications'),
        html.P('System alerts and notification management.')
    ])

if __name__ == '__main__':
    app.run(debug=True)
