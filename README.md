# Avalara-Inspired MySQL to MongoDB Atlas Migration

A database migration demonstration using **MySQL, MongoDB Atlas, and MongoDB Relational Migrator**.

## 1. Project Overview

This project demonstrates the migration of an Avalara-inspired relational database from MySQL to MongoDB Atlas.

The source database represents a simplified tax management system containing companies, customers, tax codes, items, transactions, and transaction lines.

The project demonstrates:
- Relational database schema design in MySQL.
- Synthetic dataset generation and loading.
- Relational-to-document schema mapping.
- Embedding related records in MongoDB.
- Snapshot migration using MongoDB Relational Migrator.
- Migration verification and database backup.

**Important:** This is an academic reconstruction inspired by publicly documented Avalara AvaTax concepts. It uses synthetic data and does not represent Avalara's proprietary internal database schema or production data.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| MySQL 9.7.2 | Source relational database |
| MongoDB Atlas | Target document database |
| MongoDB Relational Migrator | Schema mapping and migration |
| MongoDB Database Tools | Database backup and restoration |
| MySQL Workbench | Database management and SQL export |
| MongoDB Compass | MongoDB database inspection |
| Python 3.14.6 | Dataset generation and loading |
| uv | Python dependency management |

## 3. Source Database: MySQL

The source database is named `avalara_simulation`.

It contains six relational tables:

| Table | Records | Description |
|---|---:|---|
| companies | 10 | Company information |
| customers | 500 | Customer records |
| tax_codes | 30 | Tax classification codes |
| items | 300 | Products and services |
| transactions | 2,000 | Transaction headers |
| transaction_lines | 5,903 | Individual transaction line items |
| **Total** | **8,743** | |

All records are synthetically generated for demonstration purposes.

### Relational Schema

The source schema contains foreign-key relationships between companies, customers, items, tax codes, transactions, and transaction lines.

The `transaction_lines` table references its parent transaction using a composite relationship involving `company_id` and `transaction_id`.

## 4. MongoDB Target Design

The target database in MongoDB Atlas is named `avalara_migration`.

The optimized MongoDB schema contains five top-level collections:

| MongoDB Collection | Source Table |
|---|---|
| companies | companies |
| customers | customers |
| items | items |
| taxCodes | tax_codes |
| transactions | transactions + transaction_lines |

### Embedded Document Mapping

Instead of maintaining transaction lines as a separate collection, the optimized mapping embeds them inside their corresponding transaction document.

Example:

```javascript
{
  _id: ObjectId("..."),
  transactionId: 1001,
  companyId: 1,
  customerId: 25,
  status: "Committed",
  totalAmount: 2500.00,
  totalTax: 300.00,

  lines: [
    {
      lineId: 1,
      lineNumber: 1,
      itemId: 101,
      quantity: 2,
      unitPrice: 1100.00,
      lineAmount: 2200.00,
      taxCodeSnapshot: "TAX001",
      taxRate: 0.13636,
      taxAmount: 300.00,
      jurisdictionCode: "US-CA"
    }
  ]
}
```

This design allows a transaction and its associated line items to be retrieved together.

The original MySQL `transaction_lines` table remains unchanged.

## 5. Migration Process

The migration was performed using MongoDB Relational Migrator.

### Step 1: Source Database Preparation
- Created the MySQL schema.
- Created the required indexes.
- Generated synthetic records.
- Loaded the dataset into MySQL.

### Step 2: Relational Mapping
- Connected the MySQL source database.
- Connected the MongoDB Atlas destination.
- Examined the generated MongoDB schema suggestions.
- Configured the transaction-line relationship as an embedded array.
- Removed the standalone `transactionLines` target mapping.

### Step 3: Migration Configuration

| Setting | Configuration |
|---|---|
| Migration mode | Snapshot |
| Source database | avalara_simulation |
| Destination database | avalara_migration |
| Destination collections | 5 |
| Data verification | Enabled |
| Drop destination collections | Disabled |

### Step 4: Migration Execution

The snapshot migration processed all six source tables and completed successfully.

## 6. Migration Results

The optimized migration produced five top-level MongoDB collections.

| Collection | Documents |
|---|---:|
| companies | 10 |
| customers | 500 |
| items | 300 |
| taxCodes | 30 |
| transactions | 2,000 |
| **Total top-level documents** | **2,840** |

The 5,903 transaction-line records are represented as embedded documents inside the 2,000 transaction documents, rather than as a separate collection.

### Migration Verification

MongoDB Relational Migrator reported:

- Snapshot processing completed for all six source tables.
- Five target collections identified for verification.
- Verification completed successfully.
- No inconsistencies found in the verified collections.

The verification log noted that generated MongoDB `_id` fields were skipped because corresponding fields do not exist in the relational source database.

**Note:** The migration review summary reported 8,565 rows to migrate, while the MySQL source contained 8,743 records. The difference of 178 was not conclusively explained during this demonstration. The successful verification result applies to the collections and source tables reported by Relational Migrator; it should not be interpreted as independent proof that every source row was migrated.

## 7. Database Backup and Restoration

Database backups are included to support reproducibility.

### MySQL Backup

The MySQL database can be exported using MySQL Workbench:

1. Open Server → Data Export.
2. Select `avalara_simulation`.
3. Select all six tables.
4. Choose Dump Structure and Data.
5. Export to a self-contained SQL file.

Expected backup:

```text
mysql/
└── avalara_simulation.sql
```

Restore using:

```bash
mysql -u root -p < mysql/avalara_simulation.sql
```

### MongoDB Backup

MongoDB Atlas was exported using `mongodump`.

Expected backup:

```text
mongodb/
└── backup/
    └── avalara_migration/
        ├── companies.bson
        ├── companies.metadata.json
        ├── customers.bson
        ├── customers.metadata.json
        ├── items.bson
        ├── items.metadata.json
        ├── taxCodes.bson
        ├── taxCodes.metadata.json
        ├── transactions.bson
        └── transactions.metadata.json
```

Restore using MongoDB Database Tools:

```bash
mongorestore \
  --uri="YOUR_MONGODB_CONNECTION_STRING" \
  --nsInclude="avalara_migration.*" \
  mongodb/backup
```

Use an empty destination database or intentionally replace existing collections when restoring.

## 8. Repository Structure

```text
avalara_mysql_mongodb_migration_simulation/
│
├── mysql/
│   ├── schema.sql
│   ├── indexes.sql
│   └── avalara_simulation.sql
│
├── mongodb/
│   └── backup/
│       └── avalara_migration/
│
├── dataset/
│   ├── generate_dataset.py
│   ├── load_dataset.py
│   └── generated/
│       ├── companies.csv
│       ├── customers.csv
│       ├── tax_codes.csv
│       ├── items.csv
│       ├── transactions.csv
│       ├── transaction_lines.csv
│       └── dataset_manifest.json
│
├── migration/
│   ├── baseline.relmig
│   └── optimized.relmig
│
├── docs/
│   ├── screenshots/
│   ├── diagrams/
│   └── project_report.pdf
│
├── README.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
└── .gitignore
```

## 9. Running the Python Dataset Generator

Install uv if it is not already installed:

```bash
pip install uv
```

Install project dependencies:

```bash
uv sync
```

Generate the synthetic dataset:

```bash
uv run python dataset/generate_dataset.py
```

Load the generated data into MySQL:

```bash
uv run python dataset/load_dataset.py
```

Configure database credentials through environment variables in a local `.env` file.

Never commit `.env` or database credentials to GitHub.

## 10. Conclusion

This project demonstrates the migration of a relational tax-management database from MySQL to MongoDB Atlas using MongoDB Relational Migrator.

It covers source schema preparation, synthetic data generation, relational-to-document mapping, embedding related records, snapshot migration, verification, and database backup.

The resulting MongoDB model contains five top-level collections, with transaction line items embedded inside their parent transactions.

The project provides a reproducible demonstration of migrating a relational database into a document-oriented database using MongoDB's migration tooling.

---

**Project Type:** Academic Database Migration Demonstration

**Data:** Synthetic

**Source:** MySQL

**Target:** MongoDB Atlas

**Migration Tool:** MongoDB Relational Migrator