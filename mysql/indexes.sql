-- Additional workload indexes for the Avalara-inspired demo.
USE avalara_simulation;

CREATE INDEX idx_customers_company_name
    ON customers(company_id, customer_name);

CREATE INDEX idx_items_tax_code
    ON items(tax_code_id);

CREATE INDEX idx_transactions_date_status
    ON transactions(transaction_date, status);

CREATE INDEX idx_transactions_customer_date
    ON transactions(customer_id, transaction_date);

CREATE INDEX idx_lines_item
    ON transaction_lines(item_id);

CREATE INDEX idx_lines_jurisdiction
    ON transaction_lines(jurisdiction_code);
