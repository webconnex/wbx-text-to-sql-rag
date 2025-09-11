#!/usr/bin/env python3
"""
Direct test of Nova Pro with exact working configuration
"""

import os
import sys
import json
import boto3
from datetime import datetime

print("=" * 80)
print("🔍 NOVA PRO DIRECT ACCESS TEST - DEBUGGING")
print("=" * 80)
print(f"Timestamp: {datetime.now().isoformat()}")

# Test with different configurations
configs = [
    {
        "name": "Config 1: AWS_REGION (current)",
        "region_param": "us-west-2",
        "env_var": "AWS_REGION"
    },
    {
        "name": "Config 2: AWS_REGION_NAME (working project)",
        "region_param": "us-west-2", 
        "env_var": "AWS_REGION_NAME"
    }
]

# Test different model IDs
model_ids = [
    "us.amazon.nova-pro-v1:0",  # With prefix
    "amazon.nova-pro-v1:0",      # Without prefix
]

# Set environment variable for working config
os.environ["AWS_REGION_NAME"] = "us-west-2"
os.environ["AWS_PROFILE"] = "654293192108-okta-admin-user"

for config in configs:
    print(f"\n{'='*60}")
    print(f"Testing: {config['name']}")
    print(f"Region: {config['region_param']}")
    print("-" * 60)
    
    # Create Bedrock client
    try:
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=config['region_param']
        )
        
        # Get caller identity
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f"AWS Account: {identity['Account']}")
        print(f"AWS Profile: {os.environ.get('AWS_PROFILE', 'default')}")
        
    except Exception as e:
        print(f"❌ Failed to create client: {e}")
        continue
    
    # Test each model ID
    for model_id in model_ids:
        print(f"\n  Testing Model ID: {model_id}")
        
        # Test different request formats
        test_formats = [
            {
                "name": "Format 1: Messages with inferenceConfig",
                "body": {
                    "messages": [{
                        "role": "user",
                        "content": [{"text": "Generate SQL: SELECT COUNT(*) FROM customer"}]
                    }],
                    "inferenceConfig": {
                        "maxTokens": 500,
                        "temperature": 0.1
                    }
                }
            },
            {
                "name": "Format 2: Simple messages",
                "body": {
                    "messages": [{
                        "role": "user",
                        "content": "Generate SQL: SELECT COUNT(*) FROM customer"
                    }],
                    "max_tokens": 500,
                    "temperature": 0.1
                }
            },
            {
                "name": "Format 3: Direct prompt",
                "body": {
                    "prompt": "Generate SQL: SELECT COUNT(*) FROM customer",
                    "maxTokens": 500,
                    "temperature": 0.1
                }
            }
        ]
        
        for test_format in test_formats:
            try:
                print(f"    Trying: {test_format['name']}")
                
                response = bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps(test_format['body'])
                )
                
                response_body = json.loads(response['body'].read())
                
                # Extract output based on response structure
                output = None
                if 'output' in response_body:
                    if isinstance(response_body['output'], dict):
                        if 'message' in response_body['output']:
                            content = response_body['output']['message'].get('content', [])
                            if content:
                                output = content[0].get('text', '')
                        else:
                            output = response_body['output'].get('text', '')
                    else:
                        output = str(response_body['output'])
                elif 'completion' in response_body:
                    output = response_body['completion']
                    
                if output:
                    print(f"      ✅ SUCCESS! Got response")
                    print(f"      Output: {output[:100]}...")
                    print(f"      Full response structure: {list(response_body.keys())}")
                    break
                else:
                    print(f"      ⚠️ Got response but couldn't parse output")
                    print(f"      Response keys: {list(response_body.keys())}")
                    
            except Exception as e:
                error_msg = str(e)
                if "AccessDenied" in error_msg:
                    print(f"      ❌ Access denied")
                elif "throughput isn't supported" in error_msg:
                    print(f"      ❌ On-demand throughput not supported")
                elif "ValidationException" in error_msg:
                    print(f"      ❌ Invalid format")
                else:
                    print(f"      ❌ Error: {error_msg[:100]}")

# Also test with inference profile
print("\n" + "="*80)
print("Testing Nova Pro with Inference Profile")
print("="*80)

try:
    bedrock = boto3.client('bedrock', region_name='us-west-2')
    
    # List inference profiles
    print("\nListing available inference profiles...")
    profiles_response = bedrock.list_inference_profiles()
    
    nova_profiles = []
    for profile in profiles_response.get('inferenceProfileSummaries', []):
        if 'nova' in profile.get('inferenceProfileName', '').lower():
            nova_profiles.append(profile)
            print(f"  • {profile.get('inferenceProfileName')}: {profile.get('inferenceProfileId')}")
    
    if not nova_profiles:
        print("  No Nova inference profiles found")
        
        # Try to create one
        print("\nAttempting to create Nova Pro inference profile...")
        try:
            create_response = bedrock.create_inference_profile(
                inferenceProfileName="nova-pro-test",
                description="Test profile for Nova Pro",
                modelSource={
                    "copyFrom": "arn:aws:bedrock:us-west-2::foundation-model/amazon.nova-pro-v1:0"
                }
            )
            print(f"  ✅ Created profile: {create_response.get('inferenceProfileArn')}")
        except Exception as e:
            print(f"  ❌ Could not create profile: {str(e)[:200]}")
            
except Exception as e:
    print(f"❌ Error with inference profiles: {str(e)[:200]}")

print("\n" + "="*80)
print("💡 DIAGNOSIS")
print("="*80)

# Check which models are actually accessible
print("\nTrying to list accessible models...")
try:
    bedrock = boto3.client('bedrock', region_name='us-west-2')
    
    # List foundation models
    models_response = bedrock.list_foundation_models()
    
    accessible_models = []
    for model in models_response.get('modelSummaries', []):
        model_id = model.get('modelId', '')
        if 'nova' in model_id.lower() or 'claude' in model_id.lower():
            accessible_models.append(model_id)
    
    print(f"\nAccessible models in account:")
    for model in accessible_models[:10]:  # Show first 10
        print(f"  • {model}")
        
except Exception as e:
    print(f"Could not list models: {e}")

print("\n" + "="*80)
print("RECOMMENDATION")
print("="*80)
print("\nBased on the tests above, here's what's working:")
print("1. Check which format succeeded (if any)")
print("2. Note the exact model ID that worked")
print("3. Update the configuration accordingly")