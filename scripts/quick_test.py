#!/usr/bin/env python3
"""
Quick Test Script for Webconnex Text-to-SQL
Run this to quickly test the system end-to-end
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def main():
    """Quick test of the Text-to-SQL system"""
    print("=" * 60)
    print("Webconnex Text-to-SQL Quick Test")
    print("=" * 60)
    
    # Import our service
    from backend.services.bedrock_vanna import BedrockVanna
    
    # Initialize service
    print("\n🚀 Initializing BedrockVanna service...")
    vanna = BedrockVanna()
    print("✅ Service initialized")
    
    # Test questions
    test_cases = [
        {
            "question": "How many accounts are there in total?",
            "account_id": 123,
            "description": "Simple count query"
        },
        {
            "question": "Show me the total number of invoices this month",
            "account_id": 123,
            "description": "Date-based query"
        },
        {
            "question": "How many customers do we have?",
            "account_id": 123,
            "description": "Customer count"
        },
        {
            "question": "What is the total revenue from completed registrations?",
            "account_id": 123,
            "description": "Aggregation query"
        },
        {
            "question": "List the top 5 customers by registration count",
            "account_id": 123,
            "description": "Complex query with JOIN"
        }
    ]
    
    print("\n" + "=" * 60)
    print("TESTING SQL GENERATION")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n📝 Test {i}: {test['description']}")
        print(f"Question: {test['question']}")
        print(f"Account ID: {test['account_id']}")
        
        try:
            # Generate SQL
            sql = vanna.generate_sql(test['question'], test['account_id'])
            
            print(f"\n✅ Generated SQL:")
            print(f"{sql}")
            
            # Validate key requirements
            validations = []
            
            # Check for SELECT
            if 'SELECT' in sql.upper():
                validations.append("✅ Is SELECT query")
            else:
                validations.append("❌ Not a SELECT query")
            
            # Check for schema
            if 'wbx_data.webconnex' in sql.lower():
                validations.append("✅ Uses correct schema")
            else:
                validations.append("⚠️ Missing full schema qualification")
            
            # Check for account_id
            if f"account_id = {test['account_id']}" in sql.lower():
                validations.append("✅ Has account_id filter")
            else:
                validations.append("⚠️ Missing account_id filter")
            
            # Check for LIMIT
            if 'LIMIT' in sql.upper():
                validations.append("✅ Has LIMIT clause")
            else:
                validations.append("⚠️ Missing LIMIT clause")
            
            print("\nValidations:")
            for v in validations:
                print(f"  {v}")
            
            # Try to execute (will fail if no real connection, but tests the flow)
            if input("\n💡 Execute this query? (y/n): ").lower() == 'y':
                try:
                    print("Executing query...")
                    df = vanna.execute_sql(sql, test['account_id'])
                    print(f"✅ Query executed successfully!")
                    print(f"Results shape: {df.shape}")
                    if not df.empty:
                        print(f"First few results:")
                        print(df.head())
                except Exception as e:
                    print(f"⚠️ Execution failed (expected if not connected): {e}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            if input("Show full traceback? (y/n): ").lower() == 'y':
                traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TESTING FORBIDDEN OPERATIONS")
    print("=" * 60)
    
    forbidden_tests = [
        "DELETE all records from account table",
        "DROP the invoice table",
        "UPDATE all customer names to 'test'",
        "INSERT a new account with id 999"
    ]
    
    print("\nThese should all be blocked:")
    for question in forbidden_tests:
        print(f"\n🚫 Testing: {question}")
        try:
            sql = vanna.generate_sql(question, 123)
            print(f"Generated: {sql[:100]}...")
            
            # Try validation
            try:
                vanna._validate_sql_readonly(sql)
                print("❌ SECURITY ISSUE: Query was not blocked!")
            except ValueError as e:
                print(f"✅ Correctly blocked: {e}")
                
        except ValueError as e:
            print(f"✅ Blocked at generation: {e}")
        except Exception as e:
            print(f"✅ Failed safely: {e}")
    
    print("\n" + "=" * 60)
    print("QUICK TEST COMPLETE")
    print("=" * 60)
    print("\n✨ The system is configured for:")
    print(f"  - Model: {os.getenv('BEDROCK_MODEL_ID', 'Not set')}")
    print(f"  - Embeddings: {os.getenv('BEDROCK_MODEL_ID_EMBEDDINGS', 'Not set')}")
    print(f"  - Database: {os.getenv('REDSHIFT_DATABASE', 'Not set')}")
    print(f"  - Schema: wbx_data.webconnex")
    print("\n📚 Next steps:")
    print("  1. Run full test suite: python scripts/test_bedrock.py")
    print("  2. Test Redshift: python scripts/test_redshift.py")
    print("  3. Start the API: cd backend && uvicorn main:app --reload")
    print("  4. Access API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()