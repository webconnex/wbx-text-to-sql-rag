#!/usr/bin/env python3
"""
Test Redshift Connection
Verifies connection to Redshift and schema configuration
"""

import os
import sys
import json
import time
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

from backend.auth.aws_auth import aws_auth


def test_redshift_connection():
    """Test basic Redshift connection"""
    print("\n🔍 Testing Redshift Connection...")
    
    try:
        # Get Redshift client
        rs_client = aws_auth.get_redshift_client()
        
        print(f"Cluster: {os.getenv('REDSHIFT_CLUSTER_ID', 'wbx-data')}")
        print(f"Database: {os.getenv('REDSHIFT_DATABASE', 'wbx_data')}")
        
        # Test simple query
        test_sql = "SELECT CURRENT_DATABASE(), CURRENT_USER, VERSION()"
        
        print(f"Executing test query...")
        statement_id = aws_auth.execute_redshift_query(test_sql, with_event=True)
        
        # Get results
        results = aws_auth.get_query_results(statement_id)
        
        print(f"✅ Redshift Connection Successful!")
        print(f"Database: {results['rows'][0]['current_database']}")
        print(f"User: {results['rows'][0]['current_user']}")
        print(f"Version: {results['rows'][0]['version'][:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Redshift Connection Failed: {e}")
        return False


def test_schema_exists():
    """Test if wbx_data.webconnex schema exists"""
    print("\n🔍 Testing Schema Existence...")
    
    try:
        # Check if schema exists
        test_sql = """
        SELECT 
            schema_name,
            schema_owner
        FROM information_schema.schemata 
        WHERE schema_name = 'webconnex'
        """
        
        statement_id = aws_auth.execute_redshift_query(test_sql, with_event=True)
        results = aws_auth.get_query_results(statement_id)
        
        if results['rows']:
            print(f"✅ Schema 'webconnex' exists")
            print(f"Owner: {results['rows'][0]['schema_owner']}")
            return True
        else:
            print(f"⚠️ Schema 'webconnex' not found")
            return False
            
    except Exception as e:
        print(f"❌ Schema Check Failed: {e}")
        return False


def test_tables_exist():
    """Test if required tables exist in wbx_data.webconnex"""
    print("\n🔍 Testing Table Existence...")
    
    required_tables = ['account', 'invoice', 'customer', 'registration', 'form']
    all_exist = True
    
    try:
        # Check tables in webconnex schema
        test_sql = """
        SELECT 
            tablename,
            tableowner,
            schemaname
        FROM pg_tables 
        WHERE schemaname = 'webconnex'
        ORDER BY tablename
        """
        
        statement_id = aws_auth.execute_redshift_query(test_sql, with_event=True)
        results = aws_auth.get_query_results(statement_id)
        
        existing_tables = [row['tablename'] for row in results['rows']]
        
        print(f"Found {len(existing_tables)} tables in webconnex schema:")
        
        for table in required_tables:
            if table in existing_tables:
                print(f"  ✅ {table}")
            else:
                print(f"  ❌ {table} - NOT FOUND")
                all_exist = False
        
        # Show other tables if any
        other_tables = [t for t in existing_tables if t not in required_tables]
        if other_tables:
            print(f"\nOther tables found: {', '.join(other_tables[:10])}")
        
        return all_exist
        
    except Exception as e:
        print(f"❌ Table Check Failed: {e}")
        return False


def test_read_only_query():
    """Test read-only query with full schema qualification"""
    print("\n🔍 Testing Read-Only Query...")
    
    try:
        # Test query with full qualification
        test_sql = """
        SELECT COUNT(*) as count 
        FROM wbx_data.webconnex.account 
        WHERE account_id = 123
        LIMIT 1
        """
        
        print(f"Executing: {test_sql.strip()}")
        
        statement_id = aws_auth.execute_redshift_query(test_sql, with_event=True)
        results = aws_auth.get_query_results(statement_id)
        
        if 'rows' in results:
            print(f"✅ Read-only query executed successfully")
            if results['rows']:
                print(f"Result: {results['rows'][0]}")
            else:
                print("No rows returned (expected for account_id=123)")
            return True
        else:
            print(f"⚠️ Query executed but no results")
            return False
            
    except Exception as e:
        error_str = str(e)
        if 'permission denied' in error_str.lower():
            print(f"❌ Permission denied - check user privileges")
        elif 'does not exist' in error_str.lower():
            print(f"❌ Table not found - check schema path")
        else:
            print(f"❌ Query Failed: {e}")
        return False


def test_write_protection():
    """Test that write operations are blocked"""
    print("\n🔍 Testing Write Protection...")
    
    # These should all fail
    write_operations = [
        ("DELETE FROM wbx_data.webconnex.account WHERE account_id = -999", "DELETE"),
        ("UPDATE wbx_data.webconnex.account SET name = 'test' WHERE account_id = -999", "UPDATE"),
        ("INSERT INTO wbx_data.webconnex.account (id) VALUES (-999)", "INSERT"),
    ]
    
    all_blocked = True
    
    for sql, operation in write_operations:
        try:
            print(f"Testing {operation} (should fail)...")
            statement_id = aws_auth.execute_redshift_query(sql, with_event=True)
            print(f"  ❌ {operation} was NOT blocked - SECURITY ISSUE!")
            all_blocked = False
        except Exception as e:
            error_str = str(e).lower()
            if 'permission' in error_str or 'denied' in error_str or 'read-only' in error_str:
                print(f"  ✅ {operation} correctly blocked")
            else:
                print(f"  ⚠️ {operation} failed but not due to permissions: {e}")
    
    return all_blocked


def test_sample_queries():
    """Test some sample business queries"""
    print("\n🔍 Testing Sample Business Queries...")
    
    sample_queries = [
        {
            "name": "Count all accounts",
            "sql": "SELECT COUNT(*) as total_accounts FROM wbx_data.webconnex.account LIMIT 1"
        },
        {
            "name": "Recent invoices",
            "sql": """
            SELECT COUNT(*) as invoice_count 
            FROM wbx_data.webconnex.invoice 
            WHERE billing_date >= CURRENT_DATE - INTERVAL '30 days'
            LIMIT 1
            """
        },
        {
            "name": "Customer summary",
            "sql": """
            SELECT 
                COUNT(*) as total_customers,
                COUNT(CASE WHEN date_deleted IS NULL THEN 1 END) as active_customers
            FROM wbx_data.webconnex.customer
            LIMIT 1
            """
        }
    ]
    
    all_passed = True
    
    for query in sample_queries:
        try:
            print(f"\nTesting: {query['name']}")
            statement_id = aws_auth.execute_redshift_query(query['sql'], with_event=True)
            results = aws_auth.get_query_results(statement_id)
            
            if results['rows']:
                print(f"  ✅ Query successful")
                print(f"  Result: {results['rows'][0]}")
            else:
                print(f"  ✅ Query successful (no rows)")
                
        except Exception as e:
            print(f"  ❌ Query failed: {e}")
            all_passed = False
    
    return all_passed


def main():
    """Run all Redshift tests"""
    print("=" * 60)
    print("Webconnex Text-to-SQL Redshift Testing")
    print("=" * 60)
    
    # Check environment
    print("\n📋 Environment Check:")
    print(f"AWS Profile: {os.getenv('AWS_PROFILE', 'Not set')}")
    print(f"Redshift Cluster: {os.getenv('REDSHIFT_CLUSTER_ID', 'Not set')}")
    print(f"Database: {os.getenv('REDSHIFT_DATABASE', 'Not set')}")
    print(f"Secret ARN: {os.getenv('REDSHIFT_SECRET_ARN', 'Not set')}")
    
    # Run tests
    results = []
    
    results.append(("Connection", test_redshift_connection()))
    
    if results[-1][1]:  # Only continue if connection works
        results.append(("Schema Exists", test_schema_exists()))
        results.append(("Tables Exist", test_tables_exist()))
        results.append(("Read-Only Query", test_read_only_query()))
        results.append(("Write Protection", test_write_protection()))
        results.append(("Sample Queries", test_sample_queries()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All Redshift tests passed!")
    else:
        print("\n⚠️ Some tests failed. Please check:")
        print("1. AWS credentials are configured correctly")
        print("2. Schema wbx_data.webconnex exists")
        print("3. Required tables exist in the schema")
        print("4. User has read-only permissions")


if __name__ == "__main__":
    main()