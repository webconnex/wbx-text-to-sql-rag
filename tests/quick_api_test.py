#!/usr/bin/env python3
"""
Quick API test to check available endpoints
"""

import requests
import json

base_url = "http://localhost:8000"

print("Testing API Endpoints...")
print("=" * 60)

# Test root
response = requests.get(f"{base_url}/")
print(f"GET /: {response.status_code}")
if response.status_code == 200:
    print(f"  Response: {response.json()}")

# Test common endpoints
endpoints_to_test = [
    ("GET", "/api/health"),
    ("GET", "/api/docs"),
    ("POST", "/api/query"),
    ("POST", "/query"),
    ("POST", "/generate"),
    ("GET", "/health"),
]

for method, endpoint in endpoints_to_test:
    try:
        if method == "GET":
            response = requests.get(f"{base_url}{endpoint}", timeout=2)
        else:
            # Try with minimal payload
            response = requests.post(
                f"{base_url}{endpoint}",
                json={"question": "test", "account_id": 12345},
                timeout=2
            )
        
        print(f"{method} {endpoint}: {response.status_code}")
        
        if response.status_code == 200:
            if endpoint.endswith("health"):
                print(f"  Health: {response.json()}")
            elif endpoint.endswith("query") or endpoint.endswith("generate"):
                print(f"  ✅ Query endpoint found!")
                
    except Exception as e:
        print(f"{method} {endpoint}: Error - {str(e)[:50]}")

print("\nTrying to find the correct query endpoint...")

# Try different variations
query_endpoints = [
    "/query",
    "/api/query",
    "/generate",
    "/api/generate",
    "/query/generate",
    "/api/query/generate"
]

for endpoint in query_endpoints:
    try:
        response = requests.post(
            f"{base_url}{endpoint}",
            json={
                "question": "How many customers?",
                "account_id": 12345
            },
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            print(f"\n✅ FOUND WORKING ENDPOINT: {endpoint}")
            print(f"  Response: {response.json()}")
            break
        elif response.status_code < 500:
            print(f"  {endpoint}: {response.status_code} (client error)")
        
    except Exception as e:
        continue