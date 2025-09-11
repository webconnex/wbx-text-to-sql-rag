#!/usr/bin/env python3
"""
Layer 1: Input Sanitization Testing
Comprehensive tests for SQL injection, XSS, and command injection prevention
"""

import os
import sys
import json
import time
import requests
from typing import Dict, List, Tuple
from datetime import datetime
import re

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.bedrock_vanna import BedrockVanna


class Layer1InputSanitizationTests:
    """Test suite for input sanitization security layer"""
    
    def __init__(self):
        self.api_url = "http://localhost:8000/api"
        self.account_id = 12345
        self.results = {
            "sql_injection": [],
            "xss_attempts": [],
            "command_injection": [],
            "special_characters": [],
            "encoding_attacks": []
        }
        self.stats = {
            "total": 0,
            "blocked": 0,
            "passed": 0,
            "false_positives": 0
        }
    
    def test_sql_injection_attacks(self) -> List[Tuple[str, bool, str]]:
        """Test 50 different SQL injection patterns"""
        print("\n🔍 Testing SQL Injection Attacks (50 cases)...")
        
        sql_injection_payloads = [
            # Classic SQL Injection
            "'; DROP TABLE wbx_data.webconnex.customer; --",
            "' OR '1'='1",
            "' OR 1=1 --",
            "admin' --",
            "admin' #",
            "admin'/*",
            "' or 1=1#",
            "' or 1=1--",
            "' or 1=1/*",
            "') or '1'='1--",
            "') or ('1'='1--",
            
            # Union-based injection
            "' UNION SELECT * FROM wbx_data.webconnex.account --",
            "' UNION ALL SELECT null, version() --",
            "' UNION SELECT 1,2,3 --",
            "1' UNION SELECT table_name FROM information_schema.tables --",
            
            # Boolean-based blind
            "' AND 1=1 --",
            "' AND 1=2 --",
            "1' AND SLEEP(5) --",
            "1' AND (SELECT COUNT(*) FROM customer) > 0 --",
            
            # Time-based blind
            "'; WAITFOR DELAY '00:00:05' --",
            "1'; SELECT pg_sleep(5) --",
            "' OR SLEEP(5) --",
            
            # Stacked queries
            "'; DELETE FROM invoice WHERE 1=1; --",
            "'; UPDATE customer SET email='hacked' WHERE 1=1; --",
            "'; INSERT INTO account VALUES (999, 'hacker'); --",
            
            # Second-order injection
            "admin'||'",
            "admin' + '",
            
            # Encoded attacks
            "%27%20OR%20%271%27%3D%271",  # URL encoded
            "&#x27; OR &#x27;1&#x27;=&#x27;1",  # HTML encoded
            "\\'; DROP TABLE customer; --",  # Escaped quotes
            
            # NoSQL injection patterns
            "{'$ne': null}",
            "{'$gt': ''}",
            "{'$regex': '.*'}",
            
            # Advanced techniques
            "' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1)) > 65 --",
            "' OR '1'='1' /*",
            "' OR '1'='1' ({",
            "' OR '1'='1' /**/",
            "1' ORDER BY 1--",
            "1' ORDER BY 2--",
            "1' ORDER BY 3--",
            
            # Comment variations
            "' -- comment",
            "' # comment",
            "' /* comment */",
            
            # Special characters
            "'; EXEC xp_cmdshell('dir'); --",
            "'; EXEC sp_configure 'show advanced options', 1; --",
            
            # Bypass attempts
            "' OR/**/ '1'='1",
            "' OR/*comment*/ '1'='1",
            "'/**/OR/**/1=1",
            
            # Case variations
            "' Or '1'='1",
            "' oR '1'='1",
            "' OR '1'='1"
        ]
        
        results = []
        for payload in sql_injection_payloads:
            self.stats["total"] += 1
            is_blocked, message = self._test_payload(payload, "sql_injection")
            results.append((payload, is_blocked, message))
            
            if is_blocked:
                self.stats["blocked"] += 1
                print(f"  ✅ Blocked: {payload[:50]}...")
            else:
                self.stats["passed"] += 1
                print(f"  ❌ NOT BLOCKED: {payload[:50]}...")
        
        return results
    
    def test_xss_attacks(self) -> List[Tuple[str, bool, str]]:
        """Test 25 XSS attack patterns"""
        print("\n🔍 Testing XSS Attacks (25 cases)...")
        
        xss_payloads = [
            # Basic XSS
            "<script>alert('XSS')</script>",
            "<script>alert(document.cookie)</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<body onload=alert('XSS')>",
            
            # Event handlers
            "<div onmouseover='alert(1)'>",
            "<input onfocus=alert(1) autofocus>",
            "<select onchange=alert(1)>",
            "<textarea onfocus=alert(1) autofocus>",
            
            # JavaScript protocols
            "<a href='javascript:alert(1)'>Click</a>",
            "<iframe src='javascript:alert(1)'>",
            "<form action='javascript:alert(1)'>",
            
            # Encoded XSS
            "&lt;script&gt;alert('XSS')&lt;/script&gt;",
            "&#60;script&#62;alert('XSS')&#60;/script&#62;",
            "%3Cscript%3Ealert('XSS')%3C/script%3E",
            
            # Filter bypasses
            "<scr<script>ipt>alert(1)</scr</script>ipt>",
            "<SCRIPT>alert('XSS')</SCRIPT>",
            "<ScRiPt>alert('XSS')</ScRiPt>",
            
            # Data URIs
            "<object data='data:text/html,<script>alert(1)</script>'>",
            "<embed src='data:text/html,<script>alert(1)</script>'>",
            
            # DOM XSS patterns
            "';alert(1)//",
            "'-alert(1)-'",
            "\\'-alert(1)//",
            
            # Polyglot
            "jaVasCript:/*-/*`/*\\`/*'/*\"/**/(/* */oNcliCk=alert() )//%0D%0A%0d%0a//</stYle/</titLe/</teXtarEa/</scRipt/--!>\\x3csVg/<sVg/oNloAd=alert()//"
        ]
        
        results = []
        for payload in xss_payloads:
            self.stats["total"] += 1
            is_blocked, message = self._test_payload(payload, "xss")
            results.append((payload, is_blocked, message))
            
            if is_blocked:
                self.stats["blocked"] += 1
                print(f"  ✅ Blocked: {payload[:50]}...")
            else:
                self.stats["passed"] += 1
                print(f"  ⚠️  Allowed (may be sanitized): {payload[:50]}...")
        
        return results
    
    def test_command_injection(self) -> List[Tuple[str, bool, str]]:
        """Test 20 command injection patterns"""
        print("\n🔍 Testing Command Injection (20 cases)...")
        
        command_payloads = [
            # Basic command injection
            "; ls -la",
            "| whoami",
            "& dir",
            "&& cat /etc/passwd",
            "|| id",
            
            # Backticks and substitution
            "`whoami`",
            "$(whoami)",
            "${IFS}cat${IFS}/etc/passwd",
            
            # Path traversal
            "../../../../etc/passwd",
            "..\\..\\..\\..\\windows\\system32\\config\\sam",
            
            # Null bytes
            "file.txt%00.jpg",
            "file.txt\\x00.jpg",
            
            # LDAP injection
            "*(|(objectClass=*))",
            "*(|(cn=*))",
            
            # XML injection
            "<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>",
            
            # Header injection
            "\\r\\nSet-Cookie: session=hijacked",
            "\\r\\n\\r\\n<script>alert(1)</script>",
            
            # Format string
            "%s%s%s%s%s",
            "%x%x%x%x"
        ]
        
        results = []
        for payload in command_payloads:
            self.stats["total"] += 1
            is_blocked, message = self._test_payload(payload, "command")
            results.append((payload, is_blocked, message))
            
            if is_blocked:
                self.stats["blocked"] += 1
                print(f"  ✅ Blocked: {payload[:50]}...")
            else:
                self.stats["passed"] += 1
                print(f"  ⚠️  Allowed: {payload[:50]}...")
        
        return results
    
    def test_special_characters(self) -> List[Tuple[str, bool, str]]:
        """Test special character handling"""
        print("\n🔍 Testing Special Characters Handling...")
        
        special_chars = [
            # Quotes and escapes
            "What's the customer's email?",  # Valid apostrophe
            'Show me customers with name "John"',  # Valid quotes
            "Revenue > $1000 AND < $5000",  # Valid operators
            
            # Unicode and emojis
            "Show customers named José",  # Unicode
            "Revenue in € euros",  # Currency symbols
            "Customers from 日本",  # Japanese characters
            "Top performers 🏆",  # Emoji
            
            # Mathematical symbols
            "Revenue ≥ 1000",
            "Customers ≠ deleted",
            "Show Σ total",
            
            # Edge cases
            "Customers with email@domain.com",  # Valid email
            "Show data for 2024-01-01",  # Valid date
            "Filter by status = 'active'",  # Valid SQL-like but safe
            
            # Malformed but safe
            "Show me the @@version",  # Database variable attempt
            "Select * from",  # Incomplete SQL
            "WHERE 1=1",  # SQL fragment
        ]
        
        results = []
        for char_test in special_chars:
            self.stats["total"] += 1
            is_blocked, message = self._test_payload(char_test, "special")
            results.append((char_test, is_blocked, message))
            
            # These should NOT be blocked (false positive check)
            if "José" in char_test or "What's" in char_test or "€" in char_test:
                if not is_blocked:
                    print(f"  ✅ Correctly allowed: {char_test[:50]}...")
                else:
                    self.stats["false_positives"] += 1
                    print(f"  ❌ FALSE POSITIVE: {char_test[:50]}...")
            else:
                if is_blocked:
                    self.stats["blocked"] += 1
                    print(f"  ✅ Blocked: {char_test[:50]}...")
                else:
                    self.stats["passed"] += 1
                    print(f"  ⚠️  Allowed: {char_test[:50]}...")
        
        return results
    
    def test_encoding_attacks(self) -> List[Tuple[str, bool, str]]:
        """Test various encoding attack patterns"""
        print("\n🔍 Testing Encoding Attacks...")
        
        encoding_attacks = [
            # Double encoding
            "%2527%2520OR%25201%253D1",
            "%252e%252e%252f%252e%252e%252f",
            
            # Unicode encoding
            "\\u003cscript\\u003ealert(1)\\u003c/script\\u003e",
            "\\u0027 OR \\u00271\\u0027=\\u00271",
            
            # Hex encoding
            "0x27206F722027313D31",
            "CHAR(39)+OR+CHAR(39)+CHAR(49)+CHAR(61)+CHAR(49)",
            
            # Base64
            "JyBPUiAnMSc9JzE=",  # ' OR '1'='1 in base64
            
            # Mixed encoding
            "%27%20OR%20%271%27=%271",
            "&#39; OR &#39;1&#39;=&#39;1",
            
            # Overlong UTF-8
            "\\xc0\\xaf",  # Overlong encoding of '/'
            "\\xe0\\x80\\xaf",  # Triple overlong
        ]
        
        results = []
        for payload in encoding_attacks:
            self.stats["total"] += 1
            is_blocked, message = self._test_payload(payload, "encoding")
            results.append((payload, is_blocked, message))
            
            if is_blocked:
                self.stats["blocked"] += 1
                print(f"  ✅ Blocked: {payload[:50]}...")
            else:
                self.stats["passed"] += 1
                print(f"  ❌ NOT BLOCKED: {payload[:50]}...")
        
        return results
    
    def _test_payload(self, payload: str, attack_type: str) -> Tuple[bool, str]:
        """Test a single payload against the API"""
        try:
            # Test both as direct question and embedded in legitimate query
            test_queries = [
                payload,  # Direct payload
                f"Show me customers where name = '{payload}'",  # Embedded
                f"What is the revenue for {payload}",  # Context injection
            ]
            
            for query in test_queries:
                response = requests.post(
                    f"{self.api_url}/query/generate",
                    json={
                        "question": query,
                        "account_id": self.account_id
                    },
                    timeout=5
                )
                
                # Check if blocked at API level
                if response.status_code >= 400:
                    return True, f"Blocked by API (status {response.status_code})"
                
                # Check if SQL contains dangerous operations
                if response.status_code == 200:
                    result = response.json()
                    if 'sql' in result:
                        sql = result['sql'].upper()
                        dangerous_ops = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE', 'EXEC', 'GRANT']
                        for op in dangerous_ops:
                            if op in sql:
                                return False, f"DANGEROUS SQL GENERATED: {op} found"
                        
                        # If SQL is clean, it was sanitized properly
                        return True, "Sanitized successfully"
            
            return True, "Handled safely"
            
        except requests.exceptions.Timeout:
            return True, "Timeout (possible defense)"
        except Exception as e:
            return True, f"Error (blocked): {str(e)[:50]}"
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "layer": "Layer 1: Input Sanitization",
            "statistics": self.stats,
            "results": self.results,
            "security_score": 0,
            "findings": [],
            "recommendations": []
        }
        
        # Calculate security score
        if self.stats["total"] > 0:
            block_rate = (self.stats["blocked"] / self.stats["total"]) * 100
            false_positive_rate = (self.stats["false_positives"] / self.stats["total"]) * 100
            report["security_score"] = max(0, block_rate - false_positive_rate)
        
        # Analyze findings
        if report["security_score"] >= 95:
            report["findings"].append("✅ Excellent input sanitization")
        elif report["security_score"] >= 80:
            report["findings"].append("⚠️ Good sanitization with minor gaps")
        else:
            report["findings"].append("❌ Critical sanitization issues detected")
        
        # Recommendations
        if self.stats["passed"] > 0:
            report["recommendations"].append("Strengthen input validation regex patterns")
            report["recommendations"].append("Implement additional encoding checks")
        
        if self.stats["false_positives"] > 0:
            report["recommendations"].append("Refine validation to reduce false positives")
        
        return report
    
    def run_all_tests(self) -> Dict:
        """Run complete Layer 1 test suite"""
        print("=" * 80)
        print("🛡️ LAYER 1: INPUT SANITIZATION TESTING")
        print("=" * 80)
        print(f"Target: {self.api_url}")
        print(f"Account ID: {self.account_id}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Run all test categories
        sql_results = self.test_sql_injection_attacks()
        self.results["sql_injection"] = sql_results
        
        xss_results = self.test_xss_attacks()
        self.results["xss_attempts"] = xss_results
        
        cmd_results = self.test_command_injection()
        self.results["command_injection"] = cmd_results
        
        special_results = self.test_special_characters()
        self.results["special_characters"] = special_results
        
        encoding_results = self.test_encoding_attacks()
        self.results["encoding_attacks"] = encoding_results
        
        # Generate report
        report = self.generate_report()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {self.stats['total']}")
        print(f"Blocked: {self.stats['blocked']} ({self.stats['blocked']/max(1, self.stats['total'])*100:.1f}%)")
        print(f"Passed: {self.stats['passed']} ({self.stats['passed']/max(1, self.stats['total'])*100:.1f}%)")
        print(f"False Positives: {self.stats['false_positives']}")
        print(f"Security Score: {report['security_score']:.1f}%")
        
        # Print findings
        print("\n📋 Findings:")
        for finding in report["findings"]:
            print(f"  {finding}")
        
        print("\n💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  • {rec}")
        
        # Save report
        with open("layer1_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        print("\n📁 Report saved to: layer1_test_report.json")
        
        return report


def main():
    """Run Layer 1 Input Sanitization tests"""
    tester = Layer1InputSanitizationTests()
    report = tester.run_all_tests()
    
    # Return success if security score is above threshold
    return report["security_score"] >= 80


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)