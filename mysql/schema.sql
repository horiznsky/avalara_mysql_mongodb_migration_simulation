-- Avalara-inspired synthetic migration demo
-- Source: MySQL 9.x | Target: MongoDB Atlas
-- This is a reconstructed academic schema, NOT Avalara's proprietary schema.

CREATE DATABASE IF NOT EXISTS avalara_simulation
  CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE avalara_simulation;

CREATE TABLE IF NOT EXISTS companies (
    company_id       INT UNSIGNED NOT NULL AUTO_INCREMENT,
    company_code     VARCHAR(40) NOT NULL,
    company_name     VARCHAR(160) NOT NULL,
    country_code     CHAR(2) NOT NULL DEFAULT 'US',
    currency_code    CHAR(3) NOT NULL DEFAULT 'USD',
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (company_id),
    UNIQUE KEY uq_companies_code (company_code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS customers (
    customer_id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    company_id       INT UNSIGNED NOT NULL,
    customer_code    VARCHAR(40) NOT NULL,
    customer_name    VARCHAR(160) NOT NULL,
    email            VARCHAR(190) NULL,
    city             VARCHAR(100) NULL,
    state_code       CHAR(2) NULL,
    postal_code      VARCHAR(12) NULL,
    country_code     CHAR(2) NOT NULL DEFAULT 'US',
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id),
    UNIQUE KEY uq_customers_company_customer (company_id, customer_id),
    UNIQUE KEY uq_customers_company_code (company_id, customer_code),
    CONSTRAINT fk_customers_company
      FOREIGN KEY (company_id) REFERENCES companies(company_id)
      ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tax_codes (
    tax_code_id      INT UNSIGNED NOT NULL AUTO_INCREMENT,
    tax_code         VARCHAR(40) NOT NULL,
    description      VARCHAR(255) NOT NULL,
    category         VARCHAR(80) NOT NULL,
    PRIMARY KEY (tax_code_id),
    UNIQUE KEY uq_tax_codes_code (tax_code)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS items (
    item_id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
    company_id       INT UNSIGNED NOT NULL,
    item_code        VARCHAR(50) NOT NULL,
    item_name        VARCHAR(160) NOT NULL,
    tax_code_id      INT UNSIGNED NOT NULL,
    unit_of_measure  VARCHAR(20) NOT NULL DEFAULT 'Each',
    active           BOOLEAN NOT NULL DEFAULT TRUE,
    PRIMARY KEY (item_id),
    UNIQUE KEY uq_items_company_item (company_id, item_id),
    UNIQUE KEY uq_items_company_code (company_id, item_code),
    CONSTRAINT fk_items_company
      FOREIGN KEY (company_id) REFERENCES companies(company_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_items_tax_code
      FOREIGN KEY (tax_code_id) REFERENCES tax_codes(tax_code_id)
      ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id    BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    company_id        INT UNSIGNED NOT NULL,
    customer_id       INT UNSIGNED NOT NULL,
    transaction_code  VARCHAR(60) NOT NULL,
    transaction_date  DATE NOT NULL,
    transaction_type  VARCHAR(30) NOT NULL DEFAULT 'SalesInvoice',
    status            VARCHAR(20) NOT NULL DEFAULT 'Committed',
    currency_code     CHAR(3) NOT NULL DEFAULT 'USD',
    total_amount      DECIMAL(15,2) NOT NULL,
    total_tax         DECIMAL(15,2) NOT NULL,
    created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (transaction_id),
    UNIQUE KEY uq_transactions_company_id (company_id, transaction_id),
    UNIQUE KEY uq_transactions_company_code (company_id, transaction_code),
    CONSTRAINT fk_transactions_company
      FOREIGN KEY (company_id) REFERENCES companies(company_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_transactions_customer_same_company
      FOREIGN KEY (company_id, customer_id)
      REFERENCES customers(company_id, customer_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_transactions_amounts
      CHECK (total_amount >= 0 AND total_tax >= 0),
    CONSTRAINT chk_transactions_status
      CHECK (status IN ('Committed', 'Posted', 'Voided'))
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS transaction_lines (
    line_id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    company_id          INT UNSIGNED NOT NULL,
    transaction_id      BIGINT UNSIGNED NOT NULL,
    line_number         SMALLINT UNSIGNED NOT NULL,
    item_id             INT UNSIGNED NOT NULL,
    quantity            DECIMAL(12,3) NOT NULL,
    unit_price          DECIMAL(15,2) NOT NULL,
    line_amount         DECIMAL(15,2) NOT NULL,
    tax_code_snapshot   VARCHAR(40) NOT NULL,
    tax_rate            DECIMAL(8,4) NOT NULL,
    tax_amount          DECIMAL(15,2) NOT NULL,
    jurisdiction_code   VARCHAR(30) NOT NULL,
    PRIMARY KEY (line_id),
    UNIQUE KEY uq_lines_transaction_number (transaction_id, line_number),
    CONSTRAINT fk_lines_transaction_same_company
      FOREIGN KEY (company_id, transaction_id)
      REFERENCES transactions(company_id, transaction_id)
      ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_lines_item_same_company
      FOREIGN KEY (company_id, item_id)
      REFERENCES items(company_id, item_id)
      ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_lines_quantity CHECK (quantity > 0),
    CONSTRAINT chk_lines_amounts CHECK (
      unit_price >= 0 AND line_amount >= 0 AND tax_rate >= 0 AND tax_amount >= 0
    )
) ENGINE=InnoDB;
