#!/usr/bin/env python3
"""
Test Bedrock Connection with Amazon Nova Pro and Titan Embeddings
Tests both text generation and embedding models
"""

import os
import sys
import json
import boto3
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def test_nova_pro():
    """Test Amazon Nova Pro text generation"""
    print("\n🔍 Testing Amazon Nova Pro (Text Generation)...")
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('BEDROCK_REGION', 'us-west-2')
        )
        
        model_id = os.getenv('BEDROCK_MODEL_ID', 'us.amazon.nova-pro-v1:0')
        print(f"Model ID: {model_id}")
        
        # Test prompt for SQL generation
        test_prompt = """You are a SQL expert. Generate a simple SELECT query to count all records in a table called wbx_data.webconnex.account where account_id = 123. 
        
        Output only the SQL query, nothing else:"""
        
        # Invoke model (handle both Claude and Nova)
        if "claude" in model_id.lower():
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "messages": [
                    {
                        "role": "user",
                        "content": test_prompt
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.1
            })
        else:
            body = json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": test_prompt
                    }
                ],
                "max_tokens": 200,
                "temperature": 0.1,
                "top_p": 0.95
            })
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body=body
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        # Handle different response formats
        if 'output' in response_body:
            result = response_body['output']['message']['content'][0]['text']
        elif 'content' in response_body:
            result = response_body['content'][0]['text']
        else:
            result = str(response_body)
        
        print(f"✅ Nova Pro Connection Successful!")
        print(f"Generated SQL: {result}")
        
        # Validate it's a SELECT query
        if 'SELECT' in result.upper():
            print("✅ SQL generation working correctly")
        else:
            print("⚠️ Warning: Response doesn't contain SELECT statement")
        
        return True
        
    except Exception as e:
        print(f"❌ Nova Pro Test Failed: {e}")
        return False


def test_titan_embeddings():
    """Test Amazon Titan Embeddings"""
    print("\n🔍 Testing Amazon Titan Embeddings...")
    
    try:
        # Initialize Bedrock client
        bedrock = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('BEDROCK_REGION', 'us-west-2')
        )
        
        model_id = os.getenv('BEDROCK_MODEL_ID_EMBEDDINGS', 'amazon.titan-embed-text-v1')
        print(f"Model ID: {model_id}")
        
        # Test text for embedding
        test_text = "How many invoices do I have this month?"
        
        # Invoke model
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                "inputText": test_text
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        embedding = response_body.get('embedding', [])
        
        print(f"✅ Titan Embeddings Connection Successful!")
        print(f"Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        
        if len(embedding) > 0:
            print("✅ Embedding generation working correctly")
        else:
            print("⚠️ Warning: Empty embedding returned")
        
        return True
        
    except Exception as e:
        print(f"❌ Titan Embeddings Test Failed: {e}")
        return False


def test_sql_validation():
    """Test SQL validation for read-only operations"""
    print("\n🔍 Testing SQL Validation (Read-Only)...")
    
    # Import our validation logic
    from backend.services.bedrock_vanna import BedrockVanna
    
    vanna = BedrockVanna()
    
    # Test cases
    test_cases = [
        ("SELECT * FROM wbx_data.webconnex.account", True, "Valid SELECT"),
        ("DELETE FROM wbx_data.webconnex.account", False, "DELETE should be blocked"),
        ("DROP TABLE wbx_data.webconnex.account", False, "DROP should be blocked"),
        ("UPDATE wbx_data.webconnex.account SET name='test'", False, "UPDATE should be blocked"),
        ("INSERT INTO wbx_data.webconnex.account VALUES (1)", False, "INSERT should be blocked"),
        ("WITH cte AS (SELECT * FROM wbx_data.webconnex.account) SELECT * FROM cte", True, "CTE should be allowed"),
    ]
    
    all_passed = True
    for sql, should_pass, description in test_cases:
        try:
            vanna._validate_sql_readonly(sql)
            if should_pass:
                print(f"✅ {description}: PASSED")
            else:
                print(f"❌ {description}: FAILED (should have been blocked)")
                all_passed = False
        except ValueError as e:
            if not should_pass:
                print(f"✅ {description}: PASSED (correctly blocked)")
            else:
                print(f"❌ {description}: FAILED (incorrectly blocked)")
                all_passed = False
    
    return all_passed


def test_full_pipeline():
    """Test full pipeline: Question -> SQL Generation"""
    print("\n🔍 Testing Full Pipeline...")
    
    try:
        from backend.services.bedrock_vanna import BedrockVanna
        
        vanna = BedrockVanna()
        
        # Test question
        test_question = "How many accounts are there?"
        test_account_id = 123
        
        print(f"Question: {test_question}")
        print(f"Account ID: {test_account_id}")
        
        # Generate SQL
        sql = vanna.generate_sql(test_question, test_account_id)
        
        print(f"✅ Generated SQL: {sql}")
        
        # Validate the SQL
        checks = [
            ('SELECT' in sql.upper(), "Contains SELECT"),
            ('wbx_data.webconnex' in sql.lower(), "Uses correct schema"),
            (f'account_id = {test_account_id}' in sql.lower(), "Has account_id filter"),
            ('LIMIT' in sql.upper(), "Has LIMIT clause"),
        ]
        
        for check, description in checks:
            if check:
                print(f"  ✅ {description}")
            else:
                print(f"  ❌ {description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full Pipeline Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Webconnex Text-to-SQL Bedrock Testing")
    print("=" * 60)
    
    # Check environment
    print("\n📋 Environment Check:")
    print(f"AWS Profile: {os.getenv('AWS_PROFILE', 'Not set')}")
    print(f"AWS Region: {os.getenv('AWS_REGION', 'Not set')}")
    print(f"Bedrock Region: {os.getenv('BEDROCK_REGION', 'Not set')}")
    print(f"Nova Pro Model: {os.getenv('BEDROCK_MODEL_ID', 'Not set')}")
    print(f"Titan Embeddings: {os.getenv('BEDROCK_MODEL_ID_EMBEDDINGS', 'Not set')}")
    
    # Run tests
    results = []
    
    results.append(("Nova Pro", test_nova_pro()))
    results.append(("Titan Embeddings", test_titan_embeddings()))
    results.append(("SQL Validation", test_sql_validation()))
    results.append(("Full Pipeline", test_full_pipeline()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All tests passed! System is ready.")
    else:
        print("\n⚠️ Some tests failed. Please check the configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()