#!/usr/bin/env python3
"""
Layer 2: Authentication & Authorization Testing
Tests for JWT tokens, multi-tenancy, and access control
"""

import os
import sys
import json
import time
import jwt
import requests
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import hashlib
import base64

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Layer2AuthenticationTests:
    """Test suite for authentication and authorization layer"""
    
    def __init__(self):
        self.api_url = "http://localhost:8000/api"
        self.secret_key = "your-jwt-secret-key-change-in-production"  # From .env
        self.algorithm = "HS256"
        self.results = {
            "jwt_validation": [],
            "token_expiration": [],
            "multi_tenancy": [],
            "rate_limiting": [],
            "access_control": []
        }
        self.stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "blocked": 0
        }
    
    def generate_token(self, account_id: int, exp_minutes: int = 60, 
                      custom_claims: Dict = None) -> str:
        """Generate JWT token for testing"""
        payload = {
            "sub": f"user_{account_id}",
            "account_id": account_id,
            "exp": datetime.utcnow() + timedelta(minutes=exp_minutes),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        if custom_claims:
            payload.update(custom_claims)
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def test_jwt_validation(self) -> List[Tuple[str, bool, str]]:
        """Test JWT token validation scenarios"""
        print("\n🔐 Testing JWT Token Validation...")
        
        test_cases = [
            # Valid tokens
            {
                "name": "Valid token",
                "token": self.generate_token(12345),
                "expected": "success"
            },
            {
                "name": "Valid token different account",
                "token": self.generate_token(67890),
                "expected": "success"
            },
            
            # Invalid signatures
            {
                "name": "Wrong signature",
                "token": jwt.encode(
                    {"account_id": 12345, "exp": datetime.utcnow() + timedelta(hours=1)},
                    "wrong-secret",
                    algorithm="HS256"
                ),
                "expected": "fail"
            },
            {
                "name": "No signature",
                "token": "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJhY2NvdW50X2lkIjoxMjM0NX0.",
                "expected": "fail"
            },
            
            # Algorithm confusion
            {
                "name": "Algorithm confusion attack",
                "token": jwt.encode(
                    {"account_id": 12345},
                    key="",
                    algorithm="none"
                ),
                "expected": "fail"
            },
            
            # Malformed tokens
            {
                "name": "Malformed token",
                "token": "not.a.valid.token",
                "expected": "fail"
            },
            {
                "name": "Empty token",
                "token": "",
                "expected": "fail"
            },
            {
                "name": "Only header",
                "token": base64.b64encode(json.dumps({"alg": "HS256"}).encode()).decode(),
                "expected": "fail"
            },
            
            # Missing claims
            {
                "name": "Missing account_id",
                "token": jwt.encode(
                    {"exp": datetime.utcnow() + timedelta(hours=1)},
                    self.secret_key,
                    algorithm="HS256"
                ),
                "expected": "fail"
            },
            {
                "name": "Missing expiration",
                "token": jwt.encode(
                    {"account_id": 12345},
                    self.secret_key,
                    algorithm="HS256"
                ),
                "expected": "fail"
            }
        ]
        
        results = []
        for test in test_cases:
            self.stats["total"] += 1
            success, message = self._test_auth_token(test["token"])
            
            if test["expected"] == "success":
                if success:
                    self.stats["passed"] += 1
                    print(f"  ✅ {test['name']}: Correctly accepted")
                else:
                    self.stats["failed"] += 1
                    print(f"  ❌ {test['name']}: Incorrectly rejected")
            else:  # expected fail
                if not success:
                    self.stats["blocked"] += 1
                    print(f"  ✅ {test['name']}: Correctly rejected")
                else:
                    self.stats["failed"] += 1
                    print(f"  ❌ {test['name']}: SECURITY ISSUE - Should be rejected!")
            
            results.append((test["name"], success, message))
        
        return results
    
    def test_token_expiration(self) -> List[Tuple[str, bool, str]]:
        """Test token expiration handling"""
        print("\n⏰ Testing Token Expiration...")
        
        test_cases = [
            {
                "name": "Fresh token",
                "token": self.generate_token(12345, exp_minutes=60),
                "expected": "success"
            },
            {
                "name": "Expired token",
                "token": self.generate_token(12345, exp_minutes=-1),
                "expected": "fail"
            },
            {
                "name": "About to expire (1 minute)",
                "token": self.generate_token(12345, exp_minutes=1),
                "expected": "success"
            },
            {
                "name": "Far future expiration",
                "token": self.generate_token(12345, exp_minutes=525600),  # 1 year
                "expected": "success"  # May want to limit this
            },
            {
                "name": "Backdated token",
                "token": jwt.encode(
                    {
                        "account_id": 12345,
                        "exp": datetime.utcnow() - timedelta(hours=1),
                        "iat": datetime.utcnow() - timedelta(hours=2)
                    },
                    self.secret_key,
                    algorithm="HS256"
                ),
                "expected": "fail"
            }
        ]
        
        results = []
        for test in test_cases:
            self.stats["total"] += 1
            success, message = self._test_auth_token(test["token"])
            
            if test["expected"] == "success":
                if success:
                    self.stats["passed"] += 1
                    print(f"  ✅ {test['name']}: Accepted")
                else:
                    self.stats["failed"] += 1
                    print(f"  ❌ {test['name']}: Rejected (should accept)")
            else:
                if not success:
                    self.stats["blocked"] += 1
                    print(f"  ✅ {test['name']}: Correctly rejected")
                else:
                    self.stats["failed"] += 1
                    print(f"  ❌ {test['name']}: ACCEPTED EXPIRED TOKEN!")
            
            results.append((test["name"], success, message))
        
        return results
    
    def test_multi_tenancy(self) -> List[Tuple[str, bool, str]]:
        """Test multi-tenant isolation"""
        print("\n🏢 Testing Multi-Tenancy Isolation...")
        
        # Create tokens for different accounts
        account1_token = self.generate_token(11111)
        account2_token = self.generate_token(22222)
        admin_token = self.generate_token(99999, custom_claims={"role": "admin"})
        
        test_cases = [
            {
                "name": "Account 1 queries own data",
                "token": account1_token,
                "account_id": 11111,
                "query": "Show my customers",
                "expected": "success"
            },
            {
                "name": "Account 1 tries to query Account 2 data",
                "token": account1_token,
                "account_id": 22222,  # Different account!
                "query": "Show customers for account 22222",
                "expected": "fail"
            },
            {
                "name": "Account 2 queries own data",
                "token": account2_token,
                "account_id": 22222,
                "query": "Show my invoices",
                "expected": "success"
            },
            {
                "name": "Token/account mismatch",
                "token": account1_token,
                "account_id": 33333,  # Neither token nor requested
                "query": "Show any data",
                "expected": "fail"
            },
            {
                "name": "Admin token (should still be isolated)",
                "token": admin_token,
                "account_id": 99999,
                "query": "Show all accounts",  # Admin shouldn't bypass tenant isolation
                "expected": "success_isolated"
            }
        ]
        
        results = []
        for test in test_cases:
            self.stats["total"] += 1
            success, sql = self._test_tenant_isolation(
                test["token"], 
                test["account_id"], 
                test["query"]
            )
            
            # Check SQL contains proper account_id filter
            has_correct_filter = False
            if sql:
                token_data = jwt.decode(test["token"], self.secret_key, 
                                      algorithms=["HS256"], 
                                      options={"verify_exp": False})
                expected_account = token_data.get("account_id")
                has_correct_filter = f"account_id = {expected_account}" in sql
            
            if test["expected"] == "success" or test["expected"] == "success_isolated":
                if success and has_correct_filter:
                    self.stats["passed"] += 1
                    print(f"  ✅ {test['name']}: Properly isolated")
                else:
                    self.stats["failed"] += 1
                    print(f"  ❌ {test['name']}: Isolation failure!")
            else:
                if not success:
                    self.stats["blocked"] += 1
                    print(f"  ✅ {test['name']}: Cross-tenant access blocked")
                else:
                    self.stats["failed"] += 1
                    print(f"  ❌ {test['name']}: CROSS-TENANT ACCESS ALLOWED!")
            
            results.append((test["name"], success, f"Filter: {has_correct_filter}"))
        
        return results
    
    def test_rate_limiting(self) -> List[Tuple[str, bool, str]]:
        """Test rate limiting per user/account"""
        print("\n🚦 Testing Rate Limiting...")
        
        token = self.generate_token(12345)
        results = []
        
        # Test burst requests
        print("  Testing burst requests...")
        burst_results = []
        for i in range(20):
            start_time = time.time()
            success, status = self._make_request_with_token(token)
            elapsed = time.time() - start_time
            burst_results.append((success, status, elapsed))
            
            if i < 10 and not success and status == 429:
                print(f"    Rate limited at request {i+1}")
                self.stats["blocked"] += 1
                break
        
        # Check if rate limiting kicked in
        rate_limited = any(status == 429 for _, status, _ in burst_results)
        if rate_limited:
            print("  ✅ Rate limiting active")
            self.stats["passed"] += 1
        else:
            print("  ⚠️  No rate limiting detected in burst test")
        
        results.append(("Burst requests", rate_limited, f"{len(burst_results)} requests"))
        
        # Test per-account limiting
        print("  Testing per-account rate limits...")
        account_tokens = [self.generate_token(i) for i in range(10000, 10005)]
        
        for idx, token in enumerate(account_tokens):
            success_count = 0
            for _ in range(5):
                success, _ = self._make_request_with_token(token)
                if success:
                    success_count += 1
            
            results.append((f"Account {10000+idx}", success_count == 5, f"{success_count}/5 succeeded"))
            
            if success_count < 5:
                print(f"    Account {10000+idx} rate limited after {success_count} requests")
            else:
                print(f"    Account {10000+idx} allowed all requests")
        
        return results
    
    def test_access_control(self) -> List[Tuple[str, bool, str]]:
        """Test role-based access control"""
        print("\n🔑 Testing Access Control...")
        
        # Create tokens with different roles
        user_token = self.generate_token(12345, custom_claims={"role": "user"})
        admin_token = self.generate_token(12345, custom_claims={"role": "admin"})
        no_role_token = self.generate_token(12345)
        
        test_cases = [
            {
                "name": "User role - basic query",
                "token": user_token,
                "endpoint": "/query/generate",
                "expected": "success"
            },
            {
                "name": "Admin role - basic query",
                "token": admin_token,
                "endpoint": "/query/generate",
                "expected": "success"
            },
            {
                "name": "User role - training endpoint",
                "token": user_token,
                "endpoint": "/training/add",
                "expected": "fail"  # Users shouldn't add training data
            },
            {
                "name": "Admin role - training endpoint",
                "token": admin_token,
                "endpoint": "/training/add",
                "expected": "success"
            },
            {
                "name": "No role - basic query",
                "token": no_role_token,
                "endpoint": "/query/generate",
                "expected": "success"  # Default allow for queries
            },
            {
                "name": "No role - training endpoint",
                "token": no_role_token,
                "endpoint": "/training/add",
                "expected": "fail"
            }
        ]
        
        results = []
        for test in test_cases:
            self.stats["total"] += 1
            success, message = self._test_endpoint_access(test["token"], test["endpoint"])
            
            if test["expected"] == "success":
                if success:
                    self.stats["passed"] += 1
                    print(f"  ✅ {test['name']}: Access granted")
                else:
                    self.stats["failed"] += 1
                    print(f"  ❌ {test['name']}: Access denied (should allow)")
            else:
                if not success:
                    self.stats["blocked"] += 1
                    print(f"  ✅ {test['name']}: Access correctly denied")
                else:
                    self.stats["failed"] += 1
                    print(f"  ❌ {test['name']}: ACCESS GRANTED (should deny)!")
            
            results.append((test["name"], success, message))
        
        return results
    
    def _test_auth_token(self, token: str) -> Tuple[bool, str]:
        """Test if a token is accepted by the API"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{self.api_url}/query/generate",
                headers=headers,
                json={"question": "Test query", "account_id": 12345},
                timeout=5
            )
            
            if response.status_code == 200:
                return True, "Token accepted"
            elif response.status_code == 401:
                return False, "Unauthorized"
            elif response.status_code == 403:
                return False, "Forbidden"
            else:
                return False, f"Status {response.status_code}"
                
        except Exception as e:
            return False, str(e)
    
    def _test_tenant_isolation(self, token: str, account_id: int, 
                               query: str) -> Tuple[bool, str]:
        """Test tenant isolation with specific token and account"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{self.api_url}/query/generate",
                headers=headers,
                json={"question": query, "account_id": account_id},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                sql = result.get("sql", "")
                return True, sql
            else:
                return False, ""
                
        except Exception as e:
            return False, ""
    
    def _make_request_with_token(self, token: str) -> Tuple[bool, int]:
        """Make a request and return success status and HTTP code"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post(
                f"{self.api_url}/query/generate",
                headers=headers,
                json={"question": "Test", "account_id": 12345},
                timeout=1
            )
            return response.status_code == 200, response.status_code
        except:
            return False, 0
    
    def _test_endpoint_access(self, token: str, endpoint: str) -> Tuple[bool, str]:
        """Test access to specific endpoint"""
        try:
            headers = {"Authorization": f"Bearer {token}"}
            
            if "training" in endpoint:
                response = requests.post(
                    f"{self.api_url}{endpoint}",
                    headers=headers,
                    json={"question": "Test", "sql": "SELECT 1"},
                    timeout=5
                )
            else:
                response = requests.post(
                    f"{self.api_url}{endpoint}",
                    headers=headers,
                    json={"question": "Test", "account_id": 12345},
                    timeout=5
                )
            
            return response.status_code in [200, 201], f"Status {response.status_code}"
            
        except Exception as e:
            return False, str(e)
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "layer": "Layer 2: Authentication & Authorization",
            "statistics": self.stats,
            "results": self.results,
            "security_score": 0,
            "findings": [],
            "recommendations": []
        }
        
        # Calculate security score
        if self.stats["total"] > 0:
            success_rate = ((self.stats["passed"] + self.stats["blocked"]) / 
                          self.stats["total"]) * 100
            report["security_score"] = success_rate
        
        # Findings
        if report["security_score"] >= 95:
            report["findings"].append("✅ Excellent authentication security")
        elif report["security_score"] >= 80:
            report["findings"].append("⚠️ Good authentication with minor issues")
        else:
            report["findings"].append("❌ Critical authentication vulnerabilities")
        
        if self.stats["failed"] > 0:
            report["findings"].append(f"❌ {self.stats['failed']} authentication bypasses detected")
        
        # Recommendations
        if self.stats["failed"] > 0:
            report["recommendations"].append("Review JWT validation logic")
            report["recommendations"].append("Strengthen token expiration checks")
            report["recommendations"].append("Enforce stricter multi-tenant isolation")
        
        return report
    
    def run_all_tests(self) -> Dict:
        """Run complete Layer 2 test suite"""
        print("=" * 80)
        print("🔐 LAYER 2: AUTHENTICATION & AUTHORIZATION TESTING")
        print("=" * 80)
        print(f"Target: {self.api_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run all test categories
        jwt_results = self.test_jwt_validation()
        self.results["jwt_validation"] = jwt_results
        
        exp_results = self.test_token_expiration()
        self.results["token_expiration"] = exp_results
        
        tenant_results = self.test_multi_tenancy()
        self.results["multi_tenancy"] = tenant_results
        
        rate_results = self.test_rate_limiting()
        self.results["rate_limiting"] = rate_results
        
        access_results = self.test_access_control()
        self.results["access_control"] = access_results
        
        # Generate report
        report = self.generate_report()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.stats['total']}")
        print(f"Passed: {self.stats['passed']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Blocked: {self.stats['blocked']}")
        print(f"Security Score: {report['security_score']:.1f}%")
        
        print("\n📋 Findings:")
        for finding in report["findings"]:
            print(f"  {finding}")
        
        if report["recommendations"]:
            print("\n💡 Recommendations:")
            for rec in report["recommendations"]:
                print(f"  • {rec}")
        
        # Save report
        with open("layer2_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        print("\n📁 Report saved to: layer2_test_report.json")
        
        return report


def main():
    """Run Layer 2 Authentication tests"""
    tester = Layer2AuthenticationTests()
    report = tester.run_all_tests()
    
    return report["security_score"] >= 80


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)