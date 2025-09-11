#!/usr/bin/env python3
"""
Test Nova Pro vs Claude 3.5 to determine which model works
"""

import os
import sys
import json
import boto3
from datetime import datetime
import time

print("=" * 80)
print("🔬 NOVA PRO vs CLAUDE 3.5 COMPARISON TEST")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}")
print(f"AWS Account: {boto3.client('sts').get_caller_identity()['Account']}")

bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')

# Test SQL generation prompt
test_prompt = """Generate a READ-ONLY SQL query for: 'How many active customers do we have?'

Requirements:
1. Use schema: wbx_data.webconnex
2. Table: customer
3. Add: WHERE account_id = 12345
4. Add: AND date_deleted IS NULL
5. Add: LIMIT 1000
6. ONLY SELECT statements allowed

Return ONLY the SQL query, no explanations."""

models_to_test = [
    {
        "name": "Amazon Nova Pro",
        "id": "us.amazon.nova-pro-v1:0",
        "format": "nova"
    },
    {
        "name": "Amazon Nova Pro (direct)",
        "id": "amazon.nova-pro-v1:0",
        "format": "nova"
    },
    {
        "name": "Amazon Nova Lite",
        "id": "amazon.nova-lite-v1:0",
        "format": "nova"
    },
    {
        "name": "Claude 3.5 Sonnet",
        "id": "us.anthropic.claude-3-5-sonnet-20240620-v1:0",
        "format": "claude"
    },
    {
        "name": "Claude 3 Haiku",
        "id": "us.anthropic.claude-3-haiku-20240307-v1:0",
        "format": "claude"
    },
    {
        "name": "Claude 3.5 Haiku",
        "id": "us.anthropic.claude-3-5-haiku-20241022-v1:0",
        "format": "claude"
    }
]

results = []

for model in models_to_test:
    print(f"\n{'='*60}")
    print(f"Testing: {model['name']}")
    print(f"Model ID: {model['id']}")
    print("-" * 60)
    
    try:
        start_time = time.time()
        
        if model['format'] == 'nova':
            # Nova format - multiple variations to test
            formats_to_try = [
                # Format 1: Messages array with content array
                {
                    "messages": [{
                        "role": "user",
                        "content": [{"text": test_prompt}]
                    }],
                    "inferenceConfig": {
                        "maxTokens": 500,
                        "temperature": 0.1
                    }
                },
                # Format 2: Simple messages
                {
                    "messages": [{
                        "role": "user",
                        "content": test_prompt
                    }],
                    "max_tokens": 500,
                    "temperature": 0.1
                },
                # Format 3: Direct prompt
                {
                    "prompt": test_prompt,
                    "maxTokens": 500,
                    "temperature": 0.1
                }
            ]
            
            success = False
            for i, body_format in enumerate(formats_to_try, 1):
                try:
                    print(f"  Trying Nova format {i}...")
                    response = bedrock.invoke_model(
                        modelId=model['id'],
                        body=json.dumps(body_format)
                    )
                    
                    response_body = json.loads(response['body'].read())
                    
                    # Try different response parsing methods
                    sql = None
                    if 'output' in response_body:
                        if isinstance(response_body['output'], dict):
                            if 'message' in response_body['output']:
                                sql = response_body['output']['message'].get('content', [{}])[0].get('text', '')
                            else:
                                sql = response_body['output'].get('text', '')
                        else:
                            sql = str(response_body['output'])
                    elif 'completion' in response_body:
                        sql = response_body['completion']
                    elif 'content' in response_body:
                        sql = response_body['content']
                    else:
                        sql = str(response_body)
                    
                    if sql:
                        print(f"  ✅ Format {i} worked!")
                        success = True
                        break
                        
                except Exception as e:
                    continue
            
            if not success:
                raise Exception("All Nova formats failed")
                
        else:  # Claude format
            response = bedrock.invoke_model(
                modelId=model['id'],
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [{
                        "role": "user",
                        "content": test_prompt
                    }],
                    "max_tokens": 500,
                    "temperature": 0.1
                })
            )
            
            response_body = json.loads(response['body'].read())
            sql = response_body.get('content', [{}])[0].get('text', '').strip()
        
        elapsed = time.time() - start_time
        
        # Clean SQL
        sql = sql.replace('```sql', '').replace('```', '').strip()
        
        # Validate SQL
        validations = {
            "SELECT statement": sql.upper().startswith("SELECT"),
            "Schema qualified": "wbx_data.webconnex" in sql.lower(),
            "Account filter": "account_id = 12345" in sql.replace(" ", ""),
            "Active filter": "date_deleted" in sql.lower(),
            "LIMIT clause": "LIMIT" in sql.upper(),
            "No write ops": not any(op in sql.upper() for op in ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER'])
        }
        
        passed_checks = sum(validations.values())
        total_checks = len(validations)
        score = (passed_checks / total_checks) * 100
        
        print(f"\n  📝 Generated SQL:\n  {sql[:200]}...")
        print(f"\n  ✅ Validation Results:")
        for check, passed in validations.items():
            status = "✅" if passed else "❌"
            print(f"    {status} {check}")
        
        print(f"\n  📊 Metrics:")
        print(f"    Score: {score:.1f}%")
        print(f"    Response Time: {elapsed:.3f}s")
        
        results.append({
            "model": model['name'],
            "success": True,
            "score": score,
            "time": elapsed,
            "sql": sql
        })
        
    except Exception as e:
        print(f"  ❌ ERROR: {str(e)[:100]}")
        results.append({
            "model": model['name'],
            "success": False,
            "score": 0,
            "time": 0,
            "error": str(e)
        })

# Summary
print("\n" + "=" * 80)
print("📊 COMPARISON RESULTS")
print("=" * 80)

working_models = [r for r in results if r['success']]
failed_models = [r for r in results if not r['success']]

if working_models:
    print("\n✅ WORKING MODELS:")
    for model in sorted(working_models, key=lambda x: x['score'], reverse=True):
        print(f"  • {model['model']}: Score={model['score']:.1f}%, Time={model['time']:.3f}s")
    
    best_model = max(working_models, key=lambda x: x['score'])
    print(f"\n🏆 BEST MODEL: {best_model['model']} (Score: {best_model['score']:.1f}%)")
else:
    print("\n❌ No models are currently working")

if failed_models:
    print("\n❌ FAILED MODELS:")
    for model in failed_models:
        print(f"  • {model['model']}: {model.get('error', 'Unknown error')[:50]}")

# Recommendations
print("\n" + "=" * 80)
print("💡 RECOMMENDATIONS")
print("=" * 80)

if working_models:
    if any('nova' in m['model'].lower() for m in working_models):
        print("\n✅ Nova Pro IS WORKING!")
        print("  • Keep current configuration with Nova Pro")
        print("  • System is ready for production")
    elif any('claude' in m['model'].lower() for m in working_models):
        print("\n⚠️ Nova Pro not accessible, but Claude is working")
        print("  • Update .env to use Claude 3.5 Sonnet or Haiku")
        print("  • System will work perfectly with Claude")
    
    print(f"\n📝 Recommended model configuration:")
    print(f"  BEDROCK_MODEL_ID={best_model['model'].replace(' ', '-').lower()}")
else:
    print("\n❌ No models are currently accessible")
    print("  1. Go to AWS Console → Bedrock → Model access")
    print("  2. Request access to either Nova Pro or Claude 3.5")
    print("  3. Wait for approval (usually instant)")
    print("  4. Re-run this test")

print("\n" + "=" * 80)