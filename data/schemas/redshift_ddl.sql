-- Webconnex Text-to-SQL Database Schema
-- Amazon Redshift DDL for production tables

-- =====================================================
-- ACCOUNT TABLE - Multi-tenant base table
-- =====================================================
CREATE TABLE IF NOT EXISTS account (
    id                  INTEGER ENCODE az64 NOT NULL,
    name                VARCHAR(150) NOT NULL,
    date_created        TIMESTAMP ENCODE az64 DEFAULT CURRENT_TIMESTAMP,
    date_updated        TIMESTAMP ENCODE az64,
    date_deleted        TIMESTAMP ENCODE az64,
    source              VARCHAR(765),
    referral_code       VARCHAR(765),
    contact             VARCHAR(150),
    email               VARCHAR(180),
    phone               VARCHAR(60),
    organization_id     INTEGER ENCODE az64,
    
    PRIMARY KEY (id)
)
DISTSTYLE KEY
DISTKEY (id)
SORTKEY (id, date_created);

COMMENT ON TABLE account IS 'Main account/organization table for multi-tenancy';
COMMENT ON COLUMN account.id IS 'Unique account identifier';
COMMENT ON COLUMN account.name IS 'Organization or account name';
COMMENT ON COLUMN account.email IS 'Primary contact email';
COMMENT ON COLUMN account.date_deleted IS 'Soft delete timestamp';

-- =====================================================
-- INVOICE TABLE - Billing and revenue
-- =====================================================
CREATE TABLE IF NOT EXISTS invoice (
    id                  BIGINT ENCODE az64 NOT NULL,
    billing_id          INTEGER ENCODE az64,
    account_id          INTEGER ENCODE az64 NOT NULL,
    product             VARCHAR(500),
    invoice_number      VARCHAR(100),
    status              VARCHAR(50),
    amount              NUMERIC(18,2),
    remaining_balance   NUMERIC(18,2),
    previous_balance    NUMERIC(18,2),
    date_created        TIMESTAMP ENCODE az64 DEFAULT CURRENT_TIMESTAMP,
    billing_date        TIMESTAMP ENCODE az64,
    start_date          TIMESTAMP ENCODE az64,
    end_date            TIMESTAMP ENCODE az64,
    
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES account(id)
)
DISTSTYLE KEY
DISTKEY (account_id)
SORTKEY (account_id, billing_date);

COMMENT ON TABLE invoice IS 'Invoice and billing records';
COMMENT ON COLUMN invoice.amount IS 'Total invoice amount';
COMMENT ON COLUMN invoice.status IS 'Payment status (completed, pending, failed)';

-- =====================================================
-- CUSTOMER TABLE - Customer records per account
-- =====================================================
CREATE TABLE IF NOT EXISTS customer (
    id                  BIGINT ENCODE az64 NOT NULL,
    account_id          INTEGER ENCODE az64 NOT NULL,
    email               VARCHAR(255),
    mobile_phone        VARCHAR(50),
    first_name          VARCHAR(100),
    last_name           VARCHAR(100),
    date_created        TIMESTAMP ENCODE az64 DEFAULT CURRENT_TIMESTAMP,
    date_updated        TIMESTAMP ENCODE az64,
    date_deleted        TIMESTAMP ENCODE az64,
    date_last_login     TIMESTAMP ENCODE az64,
    
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES account(id)
)
DISTSTYLE KEY
DISTKEY (account_id)
SORTKEY (account_id, date_created);

COMMENT ON TABLE customer IS 'Customer records for each account';
COMMENT ON COLUMN customer.date_deleted IS 'Soft delete timestamp';

-- =====================================================
-- REGISTRATION TABLE - Orders/Events
-- =====================================================
CREATE TABLE IF NOT EXISTS registration (
    id                  BIGINT ENCODE az64 NOT NULL,
    account_id          BIGINT ENCODE az64 NOT NULL,
    customer_id         BIGINT ENCODE az64,
    form_id             BIGINT ENCODE az64,
    status              SMALLINT,
    total               NUMERIC(18,2),
    email               VARCHAR(255),
    order_number        VARCHAR(100),
    date_created        TIMESTAMP ENCODE az64 DEFAULT CURRENT_TIMESTAMP,
    date_completed      TIMESTAMP ENCODE az64,
    event_date          TIMESTAMP ENCODE az64,
    
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES account(id),
    FOREIGN KEY (customer_id) REFERENCES customer(id)
)
DISTSTYLE KEY
DISTKEY (account_id)
SORTKEY (account_id, date_created);

COMMENT ON TABLE registration IS 'Registration/order records';
COMMENT ON COLUMN registration.status IS 'Order status (1=completed, 0=pending)';
COMMENT ON COLUMN registration.total IS 'Total order amount';

-- =====================================================
-- FORM TABLE - Forms/Pages configuration
-- =====================================================
CREATE TABLE IF NOT EXISTS form (
    id                  BIGINT ENCODE az64 NOT NULL,
    account_id          INTEGER ENCODE az64 NOT NULL,
    name                VARCHAR(500),
    type                VARCHAR(100),
    date_created        TIMESTAMP ENCODE az64 DEFAULT CURRENT_TIMESTAMP,
    date_updated        TIMESTAMP ENCODE az64,
    date_deleted        TIMESTAMP ENCODE az64,
    
    PRIMARY KEY (id),
    FOREIGN KEY (account_id) REFERENCES account(id)
)
DISTSTYLE KEY
DISTKEY (account_id)
SORTKEY (account_id, id);

COMMENT ON TABLE form IS 'Form/page configurations';

-- =====================================================
-- INDEXES for performance optimization
-- =====================================================
CREATE INDEX idx_invoice_account_date ON invoice(account_id, billing_date);
CREATE INDEX idx_customer_account_email ON customer(account_id, email);
CREATE INDEX idx_registration_account_status ON registration(account_id, status);
CREATE INDEX idx_registration_customer ON registration(customer_id);
CREATE INDEX idx_form_account ON form(account_id);

-- =====================================================
-- GRANTS for read-only access
-- =====================================================
CREATE USER text_to_sql_reader PASSWORD 'SecurePassword123!';

GRANT USAGE ON SCHEMA public TO text_to_sql_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO text_to_sql_reader;

-- =====================================================
-- VIEWS for common queries
-- =====================================================

-- Monthly revenue by account
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT 
    account_id,
    DATE_TRUNC('month', billing_date) as month,
    SUM(amount) as total_revenue,
    COUNT(*) as invoice_count
FROM invoice
WHERE status = 'completed'
GROUP BY account_id, DATE_TRUNC('month', billing_date);

-- Customer summary by account
CREATE OR REPLACE VIEW v_customer_summary AS
SELECT 
    account_id,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN date_deleted IS NULL THEN 1 END) as active_customers,
    COUNT(CASE WHEN date_last_login >= CURRENT_DATE - INTERVAL '30 days' THEN 1 END) as active_30_days
FROM customer
GROUP BY account_id;

-- Registration summary by account
CREATE OR REPLACE VIEW v_registration_summary AS
SELECT 
    account_id,
    COUNT(*) as total_registrations,
    COUNT(CASE WHEN status = 1 THEN 1 END) as completed_registrations,
    SUM(CASE WHEN status = 1 THEN total ELSE 0 END) as total_revenue
FROM registration
GROUP BY account_id;

-- =====================================================
-- STORED PROCEDURES for common operations
-- =====================================================

-- Get account statistics
CREATE OR REPLACE PROCEDURE sp_get_account_stats(p_account_id INTEGER)
AS $$
BEGIN
    -- Customer stats
    SELECT 
        'customers' as metric,
        COUNT(*) as total,
        COUNT(CASE WHEN date_deleted IS NULL THEN 1 END) as active
    FROM customer
    WHERE account_id = p_account_id;
    
    -- Invoice stats
    SELECT 
        'invoices' as metric,
        COUNT(*) as total,
        SUM(amount) as total_amount
    FROM invoice
    WHERE account_id = p_account_id;
    
    -- Registration stats
    SELECT 
        'registrations' as metric,
        COUNT(*) as total,
        COUNT(CASE WHEN status = 1 THEN 1 END) as completed
    FROM registration
    WHERE account_id = p_account_id;
END;
$$ LANGUAGE plpgsql;