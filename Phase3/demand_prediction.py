import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Load data
orders_df = pd.read_csv('../Phase2/orders.csv')
orders_df['Order_Date'] = pd.to_datetime(orders_df['Order_Date'])

# Aggregate monthly sales per SKU
monthly_sales = orders_df.groupby([pd.Grouper(key='Order_Date', freq='M'), 'SKU_ID'])['Quantity'].sum().reset_index()
monthly_sales.rename(columns={'Order_Date': 'Month', 'Quantity': 'Sales'}, inplace=True)

# Pivot to have SKUs as columns
sales_pivot = monthly_sales.pivot(index='Month', columns='SKU_ID', values='Sales').fillna(0)

# For simplicity, predict for one SKU, say SKU001
sku = 'SKU001'
sales = sales_pivot[sku]

# Create features: lagged sales
def create_features(data, lags=3):
    df = pd.DataFrame(data)
    for lag in range(1, lags+1):
        df[f'lag_{lag}'] = df[sku].shift(lag)
    df.dropna(inplace=True)
    return df

features_df = create_features(sales, lags=3)
X = features_df.drop(columns=[sku])
y = features_df[sku]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f'MSE: {mse}')

# Predict next 3 months (assume last 3 months as input)
last_3 = sales.tail(3).values
future_pred = []
for _ in range(3):
    pred = model.predict([last_3])
    future_pred.append(pred[0])
    last_3 = np.roll(last_3, -1)
    last_3[-1] = pred[0]

print(f'Predicted demand for next 3 months: {future_pred}')

# Save predictions to CSV
predictions_df = pd.DataFrame({
    'Month': ['Month 1', 'Month 2', 'Month 3'],
    'Predicted_Demand': future_pred
})
predictions_df.to_csv('demand_predictions.csv', index=False)

# Plot
plt.figure(figsize=(10, 5))
plt.plot(sales.index, sales.values, label='Actual')
plt.plot(sales.index[-len(y_test):], y_pred, label='Predicted')
plt.legend()
plt.title(f'Demand Prediction for {sku}')
plt.savefig('demand_prediction.png')
plt.show()