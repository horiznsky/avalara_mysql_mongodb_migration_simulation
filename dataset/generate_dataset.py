#!/usr/bin/env python3
"""
Generate deterministic, synthetic Avalara-inspired data.

No Avalara customer data or production tax rules are used.
Run:
    python dataset/generate_dataset.py --output dataset/generated --seed 20261123
"""
import argparse
import csv
import json
import random
from pathlib import Path
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

COMPANY_COUNT = 10
CUSTOMER_COUNT = 500
TAX_CODE_COUNT = 30
ITEM_COUNT = 300
TRANSACTION_COUNT = 2000

COMPANY_NAMES = [
    "Northstar Commerce", "Cedar Ridge Supply", "Bluepeak Retail",
    "Harborline Goods", "Summit Trail Outfitters", "Maple & Main",
    "Redwood Market", "Silverfern Electronics", "Brightway Home",
    "Stonebridge Wholesale"
]
FIRST_NAMES = ["Avery", "Jordan", "Taylor", "Morgan", "Riley", "Casey",
               "Jamie", "Cameron", "Drew", "Quinn", "Reese", "Parker"]
LAST_NAMES = ["Miller", "Chen", "Patel", "Garcia", "Brown", "Wilson",
              "Davis", "Martin", "Thompson", "Anderson", "Clark", "Lewis"]
CITIES = [
    ("Seattle", "WA", "98101"), ("Austin", "TX", "78701"),
    ("Denver", "CO", "80202"), ("Miami", "FL", "33101"),
    ("Chicago", "IL", "60601"), ("Boston", "MA", "02108"),
    ("Phoenix", "AZ", "85004"), ("Atlanta", "GA", "30303"),
    ("Portland", "OR", "97201"), ("Dallas", "TX", "75201")
]
PRODUCTS = [
    "Wireless Keyboard", "Office Chair", "USB-C Hub", "Desk Lamp",
    "Notebook Set", "Water Bottle", "Monitor Stand", "Laptop Sleeve",
    "Bluetooth Speaker", "Storage Box", "Web Camera", "Standing Desk Mat",
    "Travel Mug", "HDMI Cable", "LED Light Strip"
]
TAX_CATEGORIES = [
    "General Goods", "Digital Goods", "Apparel", "Food", "Books",
    "Electronics", "Office Supplies", "Home Goods", "Services", "Medical Supplies"
]
TAX_RATES = [Decimal("0.0000"), Decimal("5.0000"), Decimal("7.2500"),
             Decimal("8.0000"), Decimal("8.2500"), Decimal("10.0000")]

def money(value):
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="dataset/generated")
    parser.add_argument("--seed", type=int, default=20261123)
    args = parser.parse_args()
    rng = random.Random(args.seed)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    companies = []
    for i in range(1, COMPANY_COUNT + 1):
        companies.append({
            "company_id": i, "company_code": f"COMP{i:03d}",
            "company_name": COMPANY_NAMES[i-1],
            "country_code": "US", "currency_code": "USD",
            "created_at": "2025-01-01 09:00:00"
        })

    tax_codes = []
    for i in range(1, TAX_CODE_COUNT + 1):
        category = TAX_CATEGORIES[(i-1) % len(TAX_CATEGORIES)]
        tax_codes.append({
            "tax_code_id": i, "tax_code": f"TX-{i:03d}",
            "description": f"Synthetic {category.lower()} tax classification {i:03d}",
            "category": category
        })

    customers = []
    for i in range(1, CUSTOMER_COUNT + 1):
        company_id = ((i - 1) % COMPANY_COUNT) + 1
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        city, state, postal = rng.choice(CITIES)
        customers.append({
            "customer_id": i, "company_id": company_id,
            "customer_code": f"CUST-{company_id:03d}-{i:05d}",
            "customer_name": f"{first} {last} {i}",
            "email": f"customer{i:05d}@example.test",
            "city": city, "state_code": state, "postal_code": postal,
            "country_code": "US", "created_at": "2025-01-01 09:00:00"
        })

    items = []
    for i in range(1, ITEM_COUNT + 1):
        company_id = ((i - 1) % COMPANY_COUNT) + 1
        product = PRODUCTS[(i - 1) % len(PRODUCTS)]
        tax_code_id = ((i - 1) % TAX_CODE_COUNT) + 1
        items.append({
            "item_id": i, "company_id": company_id,
            "item_code": f"ITEM-{company_id:03d}-{i:05d}",
            "item_name": f"{product} Model {i:03d}",
            "tax_code_id": tax_code_id,
            "unit_of_measure": "Each", "active": 1
        })

    customers_by_company = {}
    items_by_company = {}
    for row in customers:
        customers_by_company.setdefault(row["company_id"], []).append(row)
    for row in items:
        items_by_company.setdefault(row["company_id"], []).append(row)

    transactions = []
    lines = []
    start_date = date(2025, 1, 1)
    for tid in range(1, TRANSACTION_COUNT + 1):
        company_id = rng.randint(1, COMPANY_COUNT)
        customer = rng.choice(customers_by_company[company_id])
        tx_date = start_date + timedelta(days=rng.randint(0, 680))
        line_count = rng.randint(2, 4)
        tx_lines = []
        subtotal = Decimal("0.00")
        total_tax = Decimal("0.00")
        selected_items = rng.sample(items_by_company[company_id],
                                    k=min(line_count, len(items_by_company[company_id])))
        for line_no, item in enumerate(selected_items, start=1):
            quantity = Decimal(rng.randint(1, 5))
            unit_price = money(rng.uniform(8, 450))
            line_amount = money(quantity * unit_price)
            rate = rng.choice(TAX_RATES)
            tax_amount = money(line_amount * rate / Decimal("100"))
            jurisdiction = rng.choice(["US-WA-SEA", "US-TX-AUS", "US-CO-DEN",
                                       "US-FL-MIA", "US-IL-CHI", "US-MA-BOS"])
            row = {
                "line_id": len(lines) + len(tx_lines) + 1,
                "company_id": company_id,
                "transaction_id": tid,
                "line_number": line_no,
                "item_id": item["item_id"],
                "quantity": str(quantity.quantize(Decimal("0.001"))),
                "unit_price": str(unit_price),
                "line_amount": str(line_amount),
                "tax_code_snapshot": f"TX-{item['tax_code_id']:03d}",
                "tax_rate": str(rate),
                "tax_amount": str(tax_amount),
                "jurisdiction_code": jurisdiction
            }
            tx_lines.append(row)
            subtotal += line_amount
            total_tax += tax_amount
        transactions.append({
            "transaction_id": tid, "company_id": company_id,
            "customer_id": customer["customer_id"],
            "transaction_code": f"INV-{company_id:03d}-{tid:07d}",
            "transaction_date": tx_date.isoformat(),
            "transaction_type": "SalesInvoice",
            "status": rng.choices(["Committed", "Posted", "Voided"],
                                  weights=[65, 30, 5], k=1)[0],
            "currency_code": "USD",
            "total_amount": str(money(subtotal + total_tax)),
            "total_tax": str(money(total_tax)),
            "created_at": f"{tx_date.isoformat()} 12:00:00"
        })
        lines.extend(tx_lines)

    tables = {
        "companies": (companies, list(companies[0].keys())),
        "customers": (customers, list(customers[0].keys())),
        "tax_codes": (tax_codes, list(tax_codes[0].keys())),
        "items": (items, list(items[0].keys())),
        "transactions": (transactions, list(transactions[0].keys())),
        "transaction_lines": (lines, list(lines[0].keys()))
    }
    for table, (rows, fields) in tables.items():
        write_csv(out / f"{table}.csv", rows, fields)

    manifest = {
        "dataset_name": "Avalara-inspired synthetic transaction dataset",
        "dataset_version": "1.0.0",
        "seed": args.seed,
        "synthetic_only": True,
        "tax_rates_are_illustrative": True,
        "generated_record_counts": {name: len(value[0]) for name, value in tables.items()},
        "notes": [
            "Not supplied by Avalara and not representative of its internal database.",
            "All companies, customers, products, transactions and tax values are synthetic.",
            "Tax rates are illustrative and must not be used for tax compliance."
        ]
    }
    (out / "dataset_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(json.dumps(manifest["generated_record_counts"], indent=2))
    print(f"Dataset written to: {out.resolve()}")

if __name__ == "__main__":
    main()
