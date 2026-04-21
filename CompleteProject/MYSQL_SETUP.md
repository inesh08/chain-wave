# MySQL Setup Instructions for SCM Dashboard

## Prerequisites
- MySQL Server installed and running
- Python 3.7+
- mysql-connector-python package

## Installation Steps

### 1. Install MySQL Connector
```bash
pip install mysql-connector-python
```

### 2. Start MySQL Server
```bash
# macOS (if installed via Homebrew)
brew services start mysql

# Linux
sudo systemctl start mysql

# Windows
net start MySQL80
```

### 3. Initialize the Database
```bash
cd /Users/inesh/Downloads/scm-proj/CompleteProject
python init_db.py
```

This will:
- Create the `scm_dashboard` database
- Create all necessary tables with proper indexes
- Set up foreign key relationships
- Configure data integrity constraints

### 4. Load Initial Data
```bash
python sample_data.py
python migrate_to_mysql.py
```

This will:
- Generate sample data
- Save to CSV files (backup)
- Load data into MySQL database

### 5. Run the Dashboard
```bash
python dashboard.py
```

The dashboard will automatically connect to MySQL. If MySQL is unavailable, it will fallback to CSV files.

## Database Configuration

Edit `db_config.py` if your MySQL credentials differ:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Add password here if needed
    'database': 'scm_dashboard',
}
```

## Troubleshooting

### "Unknown database 'scm_dashboard'"
- Run `python init_db.py` again

### "Access denied for user 'root'@'localhost'"
- Update password in `db_config.py`
- Or reset MySQL root password

### "Can't connect to MySQL server"
- Ensure MySQL is running
- Check if port 3306 is accessible

### Dashboard shows "MySQL connection failed"
- Check MySQL is running
- Verify credentials in `db_config.py`
- Check database exists: `mysql -u root -e "SHOW DATABASES;"`

## Database Benefits

✓ **Persistent Storage** - Data survives application restarts  
✓ **Real-time Updates** - Multiple users can update data simultaneously  
✓ **Data Integrity** - Foreign keys and constraints ensure consistency  
✓ **Scalability** - Handles large datasets efficiently  
✓ **Backup Support** - Easy to backup and restore  
✓ **Concurrent Access** - Support for multiple simultaneous users  

## Database Schema

### Tables Created:
1. **products** - Product catalog (50 records)
2. **warehouses** - Warehouse locations (5 records)
3. **inventory** - Stock levels across warehouses (250 records)
4. **orders** - Order history (1000 records)
5. **suppliers** - Supplier information (10 records)
6. **demand_forecast** - Demand predictions (150 records)
7. **costs** - Cost breakdowns (200 records)

## Backup and Restore

### Backup Database
```bash
mysqldump -u root scm_dashboard > backup.sql
```

### Restore Database
```bash
mysql -u root scm_dashboard < backup.sql
```

## Useful MySQL Commands

```bash
# Connect to MySQL
mysql -u root

# List all databases
SHOW DATABASES;

# Use SCM database
USE scm_dashboard;

# View all tables
SHOW TABLES;

# Check table structure
DESCRIBE products;

# View data
SELECT * FROM products LIMIT 10;

# Check indexes
SHOW INDEX FROM products;

# Check foreign keys
SELECT CONSTRAINT_NAME, TABLE_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE WHERE CONSTRAINT_SCHEMA = 'scm_dashboard';
```

## Performance Tips

1. **Indexes Created**:
   - Primary keys on all tables
   - Foreign key indexes for relationships
   - Category, status, and date indexes for filtering

2. **Query Optimization**:
   - Queries use indexed columns for filtering
   - Joins use foreign key relationships
   - Proper pagination for large result sets

3. **Maintenance**:
   - Run `OPTIMIZE TABLE` periodically
   - Check `SHOW TABLE STATUS` for optimization needs
   - Monitor slow queries: `SET GLOBAL slow_query_log = 'ON';`

## File Structure

```
CompleteProject/
├── dashboard.py              # Main dashboard app (now with MySQL support)
├── db_config.py             # Database configuration
├── init_db.py               # Database schema initialization
├── migrate_to_mysql.py      # CSV to MySQL migration script
├── sample_data.py           # Sample data generator (updated for MySQL)
├── requirements.txt         # Python dependencies
├── products.csv             # CSV backup
├── orders.csv               # CSV backup
└── ... (other CSV files)
```

## Next Steps

1. Add authentication/user management
2. Implement data validation layer
3. Add caching for frequently accessed data
4. Set up automated backups
5. Add data export functionality
6. Implement audit logging
7. Add real-time data sync
