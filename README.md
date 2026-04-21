# SCM Centralized Monitoring Project (P5)

This project addresses the need for centralized monitoring in supply chain management to prevent stockouts, excess inventory, and high costs.

## Project Structure
- **Phase1/**: Problem analysis and data architecture
- **Phase2/**: Data generation scripts and CSV files
- **Phase3/**: Machine learning models
- **Phase4/**: Dashboard application
- **Phase5/**: Final report
- **CompleteProject/**: Integrated complete solution

## Technology Used
- **Python**: Core programming language
- **Dash/Plotly**: Interactive web dashboard
- **Pandas**: Data manipulation
- **Scikit-learn**: Machine learning models
- **PostgreSQL**: Database (designed, CSV for demo)
- **Jupyter**: Data analysis (optional)

## How to Run the Project
1. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

2. **Generate Data**:
   ```
   cd Phase2
   python generate_data.py
   ```

3. **Run ML Models**:
   ```
   cd ../Phase3
   python demand_prediction.py
   python anomaly_detection.py
   ```

4. **Launch Dashboard**:
   ```
   cd ../CompleteProject
   python dashboard.py
   ```
   Open http://localhost:8050 in browser

## Dashboard Screenshots
[Insert screenshots of each dashboard tab here]

## Features
- 6 interactive dashboard tabs
- Real-time KPIs and metrics
- ML-powered demand forecasting
- Anomaly detection for excess inventory
- Drill-down filters by warehouse and category
- Responsive design

## Submission
- Report: Compile Phase5/report.md into PDF as SCM22CS_P5_XXX-XXX-XXX.pdf
- Presentation: 10-minute demo of the dashboard

Deadline: April 20, 2026