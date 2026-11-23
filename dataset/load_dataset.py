#!/usr/bin/env python3
"""Load generated CSV files into MySQL in FK-safe order.

Install: pip install mysql-connector-python
Set MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD in environment.
Run after mysql/schema.sql and mysql/indexes.sql.
"""
import csv
import os
from pathlib import Path
import mysql.connector

DATA_DIR = Path(os.getenv("DATA_DIR", "dataset/generated"))
TABLES = [
    ("companies", ["company_id","company_code","company_name","country_code","currency_code","created_at"]),
    ("customers", ["customer_id","company_id","customer_code","customer_name","email","city","state_code","postal_code","country_code","created_at"]),
    ("tax_codes", ["tax_code_id","tax_code","description","category"]),
    ("items", ["item_id","company_id","item_code","item_name","tax_code_id","unit_of_measure","active"]),
    ("transactions", ["transaction_id","company_id","customer_id","transaction_code","transaction_date","transaction_type","status","currency_code","total_amount","total_tax","created_at"]),
    ("transaction_lines", ["line_id","company_id","transaction_id","line_number","item_id","quantity","unit_price","line_amount","tax_code_snapshot","tax_rate","tax_amount","jurisdiction_code"])
]

def main():
    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "avalara_simulation")
    )
    try:
        cur = conn.cursor()
        # Safe for repeatable demo reloads. Deletes child rows before parents.
        for table, _ in reversed(TABLES):
            cur.execute(f"DELETE FROM `{table}`")
        conn.commit()

        for table, fields in TABLES:
            file_path = DATA_DIR / f"{table}.csv"
            placeholders = ", ".join(["%s"] * len(fields))
            columns = ", ".join(f"`{f}`" for f in fields)
            sql = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"
            with file_path.open(newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                batch = []
                for row in reader:
                    batch.append(tuple(row[field] if row[field] != "" else None
                                        for field in fields))
                    if len(batch) >= 500:
                        cur.executemany(sql, batch)
                        batch.clear()
                if batch:
                    cur.executemany(sql, batch)
            conn.commit()
            print(f"Loaded {table}")
        cur.close()
        print("Dataset load completed.")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
