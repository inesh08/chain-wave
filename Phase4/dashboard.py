import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data
inventory_df = pd.read_csv('../Phase2/inventory.csv')
orders_df = pd.read_csv('../Phase2/orders.csv')
costs_df = pd.read_csv('../Phase2/costs.csv')
anomalies_df = pd.read_csv('../Phase3/anomalies.csv')

# Compute KPIs
total_inventory_value = (inventory_df['Current_Stock'] * costs_df.set_index('SKU_ID')['Storage_Cost_Per_Unit'].mean()).sum()
revenue_at_risk = anomalies_df['Excess_Percentage'].sum() * 0.01  # Simplified

# App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Centralized SCM Dashboard'),
    
    # Executive Summary
    html.Div([
        html.H2('Executive Summary'),
        html.P(f'Total Inventory Value: ${total_inventory_value:.2f}'),
        html.P(f'Revenue at Risk: ${revenue_at_risk:.2f}')
    ]),
    
    # Interactive Map (simulated with bar chart)
    html.Div([
        html.H2('Warehouse Stock Levels'),
        dcc.Dropdown(
            id='warehouse-dropdown',
            options=[{'label': wh, 'value': wh} for wh in inventory_df['Warehouse_ID'].unique()],
            value=inventory_df['Warehouse_ID'].unique()[0]
        ),
        dcc.Graph(id='stock-chart')
    ]),
    
    # ML Prediction Panel
    html.Div([
        html.H2('Demand Prediction'),
        dcc.Graph(id='demand-chart')
    ]),
    
    # Alert System
    html.Div([
        html.H2('Stockout Alerts'),
        html.Table([
            html.Thead(html.Tr([html.Th(col) for col in anomalies_df.columns])),
            html.Tbody([
                html.Tr([html.Td(anomalies_df.iloc[i][col]) for col in anomalies_df.columns])
                for i in range(len(anomalies_df))
            ])
        ])
    ])
])

@app.callback(
    Output('stock-chart', 'figure'),
    Input('warehouse-dropdown', 'value')
)
def update_stock_chart(warehouse):
    df = inventory_df[inventory_df['Warehouse_ID'] == warehouse]
    fig = px.bar(df, x='SKU_ID', y='Current_Stock', title=f'Stock Levels in {warehouse}')
    return fig

# For demand chart, load from prediction (simplified)
demand_fig = go.Figure()
demand_fig.add_trace(go.Scatter(x=['Month 1', 'Month 2', 'Month 3'], y=[100, 120, 110], mode='lines', name='Predicted'))
demand_fig.update_layout(title='Predicted Demand for SKU001')

@app.callback(
    Output('demand-chart', 'figure'),
    Input('warehouse-dropdown', 'value')  # Dummy
)
def update_demand_chart(_):
    return demand_fig

if __name__ == '__main__':
    app.run_server(debug=True)