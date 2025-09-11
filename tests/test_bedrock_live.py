#!/usr/bin/env python3
"""
Live test with Bedrock using updated credentials
"""

import os
import sys
import json
import boto3
from datetime import datetime

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("🚀 TESTING WITH LIVE BEDROCK CONNECTION")
print("=" * 60)

# Test AWS credentials
print("\n1️⃣ Testing AWS Credentials...")
try:
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    print(f"✅ AWS Account: {identity['Account']}")
    print(f"✅ User: {identity['UserId']}")
except Exception as e:
    print(f"❌ AWS Error: {e}")
    sys.exit(1)

# Test Bedrock access
print("\n2️⃣ Testing Bedrock Access...")
try:
    bedrock = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-west-2'
    )
    
    # Test with Claude Haiku
    test_prompt = """You are a SQL expert. Generate a READ-ONLY SQL query for: 
    'How many customers do we have?'
    
    Rules:
    - Use schema: wbx_data.webconnex
    - Add WHERE account_id = 12345
    - Add LIMIT 1000
    - Only SELECT statements allowed"""
    
    response = bedrock.invoke_model(
        modelId='us.anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": test_prompt
                }
            ]
        })
    )
    
    result = json.loads(response['body'].read())
    sql = result.get('content', [{}])[0].get('text', '')
    
    print("✅ Bedrock Connection Successful!")
    print(f"\n📝 Generated SQL:\n{sql}")
    
    # Validate the SQL
    print("\n3️⃣ Validating Generated SQL...")
    validations = {
        "Has SELECT": "SELECT" in sql.upper(),
        "Has schema": "wbx_data.webconnex" in sql.lower(),
        "Has account_id": "account_id = 12345" in sql.replace(" ", ""),
        "Has LIMIT": "LIMIT" in sql.upper(),
        "No dangerous ops": not any(op in sql.upper() for op in ['DROP', 'DELETE', 'UPDATE', 'INSERT'])
    }
    
    for check, passed in validations.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
    
except Exception as e:
    print(f"❌ Bedrock Error: {e}")
    print("\nTrying with correct model format...")
    
    try:
        # Alternative format
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            body=json.dumps({
                "prompt": f"\n\nHuman: {test_prompt}\n\nAssistant:",
                "max_tokens_to_sample": 1000
            })
        )
        
        result = json.loads(response['body'].read())
        sql = result.get('completion', '')
        print(f"✅ Alternative format worked!\n{sql}")
        
    except Exception as e2:
        print(f"❌ Alternative also failed: {e2}")

# Test the full API
print("\n4️⃣ Testing Full API Integration...")
import requests
import jwt
from datetime import timedelta

# Generate token
secret_key = "your-jwt-secret-key-change-in-production"
token_payload = {
    "sub": "user_12345",
    "account_id": 12345,
    "exp": datetime.utcnow() + timedelta(hours=1),
    "iat": datetime.utcnow(),
    "type": "access"
}

token = jwt.encode(token_payload, secret_key, algorithm="HS256")

# Test API
headers = {"Authorization": f"Bearer {token}"}
queries_to_test = [
    "How many customers do we have?",
    "What's our total revenue this month?",
    "Show me top 5 customers",
    "Delete all customers"  # Should be blocked
]

for query in queries_to_test:
    print(f"\n📝 Testing: {query}")
    
    response = requests.post(
        "http://localhost:8000/api/query",
        headers=headers,
        json={
            "question": query,
            "account_id": 12345
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"  ✅ Success!")
        if 'sql' in result:
            print(f"  SQL: {result['sql'][:100]}...")
    else:
        print(f"  Status: {response.status_code}")
        if "delete" in query.lower():
            print(f"  ✅ Correctly blocked dangerous query")
        else:
            print(f"  ❌ Should have succeeded")
            print(f"  Error: {response.text[:200]}")

print("\n" + "=" * 60)
print("🎯 BEDROCK INTEGRATION TEST COMPLETE")
print("=" * 60)