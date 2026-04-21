# MySQL Setup Guide for SCM Dashboard

## Quick Start

### For macOS:
```bash
bash setup_mysql.sh
```

### For Windows:
```cmd
setup_mysql.bat
```

### For Linux:
```bash
bash setup_mysql.sh
```

---

## Step-by-Step Manual Setup

### Step 1: Install MySQL

**macOS (Homebrew):**
```bash
brew install mysql
brew services start mysql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install mysql-server
sudo systemctl start mysqld
```

**Windows:**
- Download from https://mysql.com/downloads/mysql/
- Run installer and follow setup wizard
- Start MySQL service: `net start MySQL80`

---

### Step 2: Install Python Dependencies

```bash
pip install -r requirements_mysql.txt
```

Or individually:
```bash
pip install mysql-connector-python pandas plotly dash numpy
```

---

### Step 3: Initialize Database Schema

```bash
python init_db.py
```

This will:
- Create `scm_dashboard` database
- Create 7 tables with proper relationships
- Set up indexes and constraints
- Configure foreign keys

Expected output:
```
✓ Database 'scm_dashboard' created/exists
✓ Table 'products' created/exists
✓ Table 'warehouses' created/exists
✓ Table 'inventory' created/exists
✓ Table 'orders' created/exists
✓ Table 'suppliers' created/exists
✓ Table 'demand_forecast' created/exists
✓ Table 'costs' created/exists
✓ Database initialization complete!
```

---

### Step 4: Generate Sample Data

```bash
python sample_data.py
```

This will:
- Generate 50 products across 4 categories
- Create 5 warehouses
- Generate 250 inventory records
- Create 1000 orders
- Create 10 suppliers
- Generate 150 demand forecasts
- Generate 200 cost records
- Save all data to both CSV and MySQL

---

### Step 5: Load Data into MySQL

```bash
python migrate_to_mysql.py
```

This will:
- Clear existing data in MySQL
- Load all CSV data into respective tables
- Verify all data was inserted correctly

Expected output:
```
Loading products...
✓ Inserted 50 products
Loading warehouses...
✓ Inserted 5 warehouses
Loading suppliers...
✓ Inserted 10 suppliers
Loading inventory...
✓ Inserted 250 inventory records
Loading orders...
✓ Inserted 1000 orders
Loading demand_forecast...
✓ Inserted 150 demand forecasts
Loading costs...
✓ Inserted 200 cost records
✓ All data migrated successfully to MySQL!
```

---

### Step 6: Run the Dashboard

```bash
python dashboard.py
```

Expected output:
```
Loading data from MySQL database...
✓ Data loaded from MySQL successfully
Dash is running on http://0.0.0.0:8050
```

Open browser: http://localhost:8050

---

## Configuration

### Change MySQL Password

Edit `db_config.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_new_password',  # Add password here
    'database': 'scm_dashboard',
    'raise_on_warnings': True
}
```

### Change MySQL Host

For remote MySQL server:
```python
DB_CONFIG = {
    'host': '192.168.1.100',  # Remote server IP
    'user': 'root',
    'password': '',
    'database': 'scm_dashboard',
    'raise_on_warnings': True
}
```

---

## Verification

### Check if MySQL is Running

```bash
mysql -u root -e "SELECT 1"
```

Should return:
```
+---+
| 1 |
+---+
| 1 |
+---+
```

### Verify Database Creation

```bash
mysql -u root -e "SHOW DATABASES;" | grep scm_dashboard
```

Should show: `scm_dashboard`

### Check Tables

```bash
mysql -u root -e "USE scm_dashboard; SHOW TABLES;"
```

Should show:
```
+------------------------+
| Tables_in_scm_dashboard |
+------------------------+
| costs                   |
| demand_forecast         |
| inventory               |
| orders                  |
| products                |
| suppliers               |
| warehouses              |
+------------------------+
```

### Verify Data

```bash
mysql -u root -e "USE scm_dashboard; SELECT COUNT(*) as count FROM products;"
```

Should show: 50 products

---

## Troubleshooting

### Error: "Can't connect to MySQL server"
```bash
# Check if MySQL is running
# macOS
brew services list | grep mysql

# Linux
sudo systemctl status mysql

# Start MySQL
brew services start mysql
# or
sudo systemctl start mysql
```

### Error: "Unknown database 'scm_dashboard'"
```bash
# Run initialization again
python init_db.py
```

### Error: "Access denied for user 'root'@'localhost'"
1. Update password in `db_config.py`
2. Or reset MySQL password:
```bash
mysql -u root
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
FLUSH PRIVILEGES;
```

### Error: "Table 'products' doesn't exist"
```bash
# Check which tables exist
mysql -u root scm_dashboard -e "SHOW TABLES;"

# If empty, re-initialize
python init_db.py
```

### Dashboard Shows "MySQL connection failed"
1. Check MySQL is running
2. Verify credentials in `db_config.py`
3. Check database exists: `mysql -u root -e "SHOW DATABASES;"`
4. Check tables: `mysql -u root scm_dashboard -e "SHOW TABLES;"`

---

## Database Backup and Restore

### Backup Database

```bash
mysqldump -u root scm_dashboard > scm_backup_$(date +%Y%m%d_%H%M%S).sql
```

This creates a backup file with timestamp.

### Restore from Backup

```bash
mysql -u root scm_dashboard < scm_backup_20240421_120000.sql
```

### Backup All Databases

```bash
mysqldump -u root --all-databases > full_backup.sql
```

---

## Performance Optimization

### Check Database Size
```bash
mysql -u root -e "
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) as size_mb
FROM information_schema.tables
WHERE table_schema = 'scm_dashboard';
"
```

### Optimize Tables
```bash
mysql -u root -e "USE scm_dashboard; OPTIMIZE TABLE products, warehouses, inventory, orders, suppliers, demand_forecast, costs;"
```

### Check Indexes
```bash
mysql -u root -e "USE scm_dashboard; SHOW INDEX FROM products;"
```

### Check Slow Queries
```bash
mysql -u root -e "SET GLOBAL slow_query_log = 'ON';"
mysql -u root -e "SET GLOBAL long_query_time = 1;"
```

---

## Files Created

| File | Purpose |
|------|---------|
| `db_config.py` | Database connection configuration |
| `init_db.py` | Create database schema |
| `migrate_to_mysql.py` | Migrate CSV data to MySQL |
| `sample_data.py` | Generate sample data (updated) |
| `dashboard.py` | Main dashboard app (updated) |
| `setup_mysql.sh` | Automated setup script (Linux/macOS) |
| `setup_mysql.bat` | Automated setup script (Windows) |
| `requirements_mysql.txt` | Python dependencies |
| `MYSQL_SETUP.md` | Detailed setup documentation |

---

## Next Steps

1. **Security**: Change root password and create dedicated user
2. **Monitoring**: Set up slow query logging
3. **Backup**: Schedule automatic backups
4. **Authentication**: Add dashboard login system
5. **Replication**: Set up MySQL replication for high availability
6. **Caching**: Implement Redis for frequently accessed data

---

## Questions?

Refer to MySQL documentation: https://dev.mysql.com/doc/
