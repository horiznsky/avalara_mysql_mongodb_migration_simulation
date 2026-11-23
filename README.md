# Avalara-inspired MySQL → MongoDB Atlas Migration Simulation

Academic simulation based on publicly documented AvaTax concepts and API models.
This is **not** Avalara's proprietary schema, database, source code, or dataset.

## Scope
Six MySQL tables: companies, customers, tax_codes, items, transactions,
transaction_lines. Synthetic data only; tax rates are illustrative and are
not valid tax-compliance guidance.

## Requirements
- MySQL Server (the project was prepared for MySQL 9.x)
- MySQL Workbench
- Python 3.10+
- MongoDB Atlas account
- MongoDB Relational Migrator
- Optional: MongoDB Compass

## 1. Create the source schema
Open `mysql/schema.sql` in MySQL Workbench and execute it.
Then execute `mysql/indexes.sql`.

## 2. Generate the deterministic dataset
From the repository root:

```bash
python dataset/generate_dataset.py --output dataset/generated --seed 20261123
```

This creates six CSV files and `dataset_manifest.json`.
The generator uses only Python's standard library.

## 3. Load CSV data into MySQL
Install the connector:

```bash
pip install -r requirements.txt
```

Set environment variables (do not commit passwords):

Windows PowerShell:
```powershell
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="YOUR_LOCAL_PASSWORD"
$env:MYSQL_DATABASE="avalara_simulation"
python dataset/load_dataset.py
```

The loader deletes existing rows in child-to-parent order, then inserts
parents before children. It is intended for this disposable demo database.

## 4. Verify
Run:

```sql
USE avalara_simulation;
SELECT 'companies' AS table_name, COUNT(*) AS row_count FROM companies
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'tax_codes', COUNT(*) FROM tax_codes
UNION ALL SELECT 'items', COUNT(*) FROM items
UNION ALL SELECT 'transactions', COUNT(*) FROM transactions
UNION ALL SELECT 'transaction_lines', COUNT(*) FROM transaction_lines;
```

Expected counts are in `dataset/generated/dataset_manifest.json`.

## 5. Migration experiments
- Baseline: map each MySQL table to its own MongoDB collection in Relational Migrator.
- Optimized: map transactions with embedded transaction_lines; retain company,
  customer, and item references plus historical item/tax snapshots.
- Use separate target databases or collection prefixes for the two experiments.

## Reproducibility
The default seed is `20261123`. Use the same seed and generator version to
recreate the same logical dataset.

## Security
Never commit `.env`, database passwords, Atlas connection strings, API keys,
or production data. Use `.env.example` as a template if needed.
