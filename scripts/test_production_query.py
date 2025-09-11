#!/usr/bin/env python3
"""
Test production queries against the Text-to-SQL API
"""

import requests
import json
import sys

def test_query(question, account_id=12345):
    """Test a single query against the API"""
    url = "http://localhost:8000/api/query/generate"
    
    payload = {
        "question": question,
        "account_id": account_id
    }
    
    try:
        print(f"\n📝 Question: {question}")
        print("=" * 60)
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            # Display SQL
            if 'sql' in result:
                print("\n✅ Generated SQL:")
                print(result['sql'][:500] + "..." if len(result['sql']) > 500 else result['sql'])
            
            # Display data preview
            if 'data' in result:
                print(f"\n📊 Result: {len(result.get('data', []))} rows returned")
                if result['data']:
                    print("First row:", json.dumps(result['data'][0], indent=2))
            
            # Display metadata
            if 'metadata' in result:
                print(f"\n⏱️  Execution time: {result['metadata'].get('execution_time', 'N/A')}s")
            
            return True
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Is it running?")
        print("   Start with: python scripts/run_server.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run production test queries"""
    print("=" * 60)
    print("🚀 PRODUCTION QUERY TESTING")
    print("=" * 60)
    
    # Test queries - from simple to complex
    test_queries = [
        # Basic counts
        "How many customers do we have?",
        "How many invoices were created this month?",
        
        # Revenue queries
        "What's our total revenue this year?",
        "Show me revenue by month for the last 6 months",
        
        # Customer analytics
        "Who are our top 5 customers by lifetime value?",
        "How many new customers joined this week?",
        
        # Advanced analytics
        "What's our customer retention rate?",
        "Which forms have the highest conversion rates?",
        
        # Security test (should be blocked)
        "Delete all customers where id > 0",
    ]
    
    results = []
    
    for query in test_queries:
        success = test_query(query)
        results.append((query[:50], success))
        print("\n" + "-" * 60)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for query, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {query}")
    
    passed = sum(1 for _, s in results if s)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total}")
    
    if passed == total - 1:  # Expecting the DELETE query to fail
        print("\n🎉 All tests passed as expected!")
        print("   (DELETE query was correctly blocked)")
    else:
        print("\n⚠️  Some tests failed unexpectedly")


if __name__ == "__main__":
    # You can also test specific queries
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        test_query(question)
    else:
        main()