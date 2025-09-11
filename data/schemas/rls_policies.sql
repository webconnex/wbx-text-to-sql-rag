-- Row-Level Security (RLS) Configuration for Webconnex
-- Ensures multi-tenant data isolation at database level

-- =====================================================
-- ENABLE ROW LEVEL SECURITY ON TABLES
-- =====================================================

-- Enable RLS on main tables
ALTER TABLE account ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice ENABLE ROW LEVEL SECURITY;
ALTER TABLE customer ENABLE ROW LEVEL SECURITY;
ALTER TABLE registration ENABLE ROW LEVEL SECURITY;
ALTER TABLE form ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- CREATE RLS POLICIES
-- =====================================================

-- Policy for account table (users can only see their own account)
CREATE RLS POLICY account_isolation_policy 
AS (id = current_setting('app_context.account_id')::integer);

-- Policy for invoice table
CREATE RLS POLICY invoice_isolation_policy 
AS (account_id = current_setting('app_context.account_id')::integer);

-- Policy for customer table
CREATE RLS POLICY customer_isolation_policy 
AS (account_id = current_setting('app_context.account_id')::integer);

-- Policy for registration table
CREATE RLS POLICY registration_isolation_policy 
AS (account_id = current_setting('app_context.account_id')::integer);

-- Policy for form table
CREATE RLS POLICY form_isolation_policy 
AS (account_id = current_setting('app_context.account_id')::integer);

-- =====================================================
-- ATTACH POLICIES TO TABLES
-- =====================================================

ALTER TABLE account ATTACH RLS POLICY account_isolation_policy;
ALTER TABLE invoice ATTACH RLS POLICY invoice_isolation_policy;
ALTER TABLE customer ATTACH RLS POLICY customer_isolation_policy;
ALTER TABLE registration ATTACH RLS POLICY registration_isolation_policy;
ALTER TABLE form ATTACH RLS POLICY form_isolation_policy;

-- =====================================================
-- CREATE CONTEXT MANAGEMENT FUNCTIONS
-- =====================================================

-- Function to set account context for current session
CREATE OR REPLACE FUNCTION set_account_context(p_account_id INTEGER)
RETURNS VOID AS $$
BEGIN
    -- Validate account exists
    IF NOT EXISTS (SELECT 1 FROM account WHERE id = p_account_id) THEN
        RAISE EXCEPTION 'Invalid account ID: %', p_account_id;
    END IF;
    
    -- Set the account context
    PERFORM set_config('app_context.account_id', p_account_id::text, false);
    
    -- Log the context change (optional)
    RAISE NOTICE 'Account context set to: %', p_account_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get current account context
CREATE OR REPLACE FUNCTION get_account_context()
RETURNS INTEGER AS $$
BEGIN
    RETURN current_setting('app_context.account_id', true)::integer;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clear account context
CREATE OR REPLACE FUNCTION clear_account_context()
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app_context.account_id', '', false);
    RAISE NOTICE 'Account context cleared';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- CREATE SECURE VIEWS WITH RLS
-- =====================================================

-- Secure view for account data
CREATE OR REPLACE VIEW v_secure_account AS
SELECT 
    id,
    name,
    email,
    contact,
    date_created,
    organization_id
FROM account
WHERE id = get_account_context();

-- Secure view for invoices
CREATE OR REPLACE VIEW v_secure_invoices AS
SELECT 
    i.*
FROM invoice i
WHERE i.account_id = get_account_context();

-- Secure view for customers
CREATE OR REPLACE VIEW v_secure_customers AS
SELECT 
    c.*
FROM customer c
WHERE c.account_id = get_account_context()
    AND c.date_deleted IS NULL;

-- Secure view for registrations
CREATE OR REPLACE VIEW v_secure_registrations AS
SELECT 
    r.*
FROM registration r
WHERE r.account_id = get_account_context();

-- =====================================================
-- CREATE ROLE FOR TEXT-TO-SQL APPLICATION
-- =====================================================

-- Create role for the application
CREATE ROLE text_to_sql_readonly;

-- Grant schema usage
GRANT USAGE ON SCHEMA public TO text_to_sql_readonly;

-- Grant SELECT on tables
GRANT SELECT ON account, invoice, customer, registration, form TO text_to_sql_readonly;

-- Grant SELECT on views
GRANT SELECT ON ALL TABLES IN SCHEMA public TO text_to_sql_readonly;

-- Grant EXECUTE on context functions
GRANT EXECUTE ON FUNCTION set_account_context(INTEGER) TO text_to_sql_readonly;
GRANT EXECUTE ON FUNCTION get_account_context() TO text_to_sql_readonly;
GRANT EXECUTE ON FUNCTION clear_account_context() TO text_to_sql_readonly;

-- =====================================================
-- AUDIT LOGGING FOR RLS
-- =====================================================

-- Create audit table for tracking context changes
CREATE TABLE IF NOT EXISTS rls_audit_log (
    id              BIGINT IDENTITY(1,1) PRIMARY KEY,
    session_id      VARCHAR(100),
    account_id      INTEGER,
    user_name       VARCHAR(100),
    action          VARCHAR(50),
    timestamp       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    query_text      VARCHAR(4000)
);

-- Function to log RLS context changes
CREATE OR REPLACE FUNCTION log_rls_context_change()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO rls_audit_log (
        session_id,
        account_id,
        user_name,
        action,
        query_text
    ) VALUES (
        pg_backend_pid()::VARCHAR,
        NEW.account_id,
        current_user,
        TG_OP,
        current_query()
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- TESTING RLS POLICIES
-- =====================================================

-- Test procedure to verify RLS is working
CREATE OR REPLACE PROCEDURE test_rls_policies(p_account_id INTEGER)
AS $$
DECLARE
    v_count INTEGER;
BEGIN
    -- Set context
    PERFORM set_account_context(p_account_id);
    
    -- Test account access
    SELECT COUNT(*) INTO v_count FROM account;
    RAISE NOTICE 'Account records visible: %', v_count;
    
    -- Test invoice access
    SELECT COUNT(*) INTO v_count FROM invoice;
    RAISE NOTICE 'Invoice records visible: %', v_count;
    
    -- Test customer access
    SELECT COUNT(*) INTO v_count FROM customer;
    RAISE NOTICE 'Customer records visible: %', v_count;
    
    -- Test registration access
    SELECT COUNT(*) INTO v_count FROM registration;
    RAISE NOTICE 'Registration records visible: %', v_count;
    
    -- Clear context
    PERFORM clear_account_context();
    
    RAISE NOTICE 'RLS test completed for account %', p_account_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MAINTENANCE PROCEDURES
-- =====================================================

-- Procedure to refresh RLS policies
CREATE OR REPLACE PROCEDURE refresh_rls_policies()
AS $$
BEGIN
    -- Detach existing policies
    ALTER TABLE account DETACH RLS POLICY account_isolation_policy;
    ALTER TABLE invoice DETACH RLS POLICY invoice_isolation_policy;
    ALTER TABLE customer DETACH RLS POLICY customer_isolation_policy;
    ALTER TABLE registration DETACH RLS POLICY registration_isolation_policy;
    ALTER TABLE form DETACH RLS POLICY form_isolation_policy;
    
    -- Re-attach policies
    ALTER TABLE account ATTACH RLS POLICY account_isolation_policy;
    ALTER TABLE invoice ATTACH RLS POLICY invoice_isolation_policy;
    ALTER TABLE customer ATTACH RLS POLICY customer_isolation_policy;
    ALTER TABLE registration ATTACH RLS POLICY registration_isolation_policy;
    ALTER TABLE form ATTACH RLS POLICY form_isolation_policy;
    
    RAISE NOTICE 'RLS policies refreshed successfully';
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- GRANT PERMISSIONS
-- =====================================================

-- Grant execute permissions on procedures
GRANT EXECUTE ON PROCEDURE test_rls_policies(INTEGER) TO text_to_sql_readonly;
GRANT EXECUTE ON PROCEDURE refresh_rls_policies() TO text_to_sql_readonly;