# 🧪 Testing Framework - Agent-Driven Quality Assurance

## Specialized Agents for Testing

### Primary Agents
- **@test-engineer**: Test strategy, framework design, validation procedures
- **@security-guardian**: Security testing, penetration testing, vulnerability assessment
- **@performance-optimizer**: Load testing, performance validation, benchmarking
- **@rag-researcher**: RAG system testing, retrieval accuracy validation

## Testing Philosophy

### Agent-Driven Testing Strategy
Each agent is responsible for testing within their domain of expertise, ensuring comprehensive coverage across all system components.

### Testing Pyramid
```
                    /\
                   /  \
                  / E2E \     @test-engineer + all domain agents
                 /______\
                /        \
               /Integration\   @test-engineer + domain pairs
              /__________\
             /            \
            /   Unit Tests  \   Each agent tests their domain
           /________________\
```

## Test Categories by Agent

### @test-engineer - Core Testing
```python
test_categories = {
    "unit_tests": [
        "Individual function testing",
        "Class method validation", 
        "Error handling verification",
        "Edge case coverage"
    ],
    "integration_tests": [
        "API endpoint testing",
        "Database integration",
        "Service communication",
        "External API integration"
    ],
    "end_to_end_tests": [
        "Complete user workflows",
        "Multi-component interactions",
        "Real-world scenarios",
        "UI automation testing"
    ]
}
```

### @security-guardian - Security Testing
```python
security_test_suite = {
    "layer_1_input_sanitization": [
        "XSS injection attempts",
        "HTML entity injection",
        "Special character handling",
        "Input length validation"
    ],
    "layer_2_authentication": [
        "JWT token validation",
        "Expired token handling", 
        "Invalid token rejection",
        "Token forgery attempts"
    ],
    "layer_3_query_classification": [
        "Malicious query detection",
        "Intent classification accuracy",
        "False positive rates",
        "Bypass attempt detection"
    ],
    "layer_4_ai_safety": [
        "Prompt injection resistance",
        "Constraint adherence",
        "Model behavior consistency",
        "Safety guardrail effectiveness"
    ],
    "layer_5_sql_validation": [
        "Forbidden operation detection",
        "SQL injection prevention",
        "Regex validation accuracy",
        "False positive minimization"
    ],
    "layer_6_account_isolation": [
        "Cross-tenant access prevention",
        "RLS policy enforcement",
        "Account_id filtering verification",
        "Data leakage prevention"
    ],
    "layer_7_result_limiting": [
        "Row limit enforcement",
        "Large dataset handling",
        "Memory usage protection",
        "Response size validation"
    ]
}
```

### @performance-optimizer - Performance Testing
```python
performance_test_scenarios = {
    "load_testing": [
        "Concurrent user simulation",
        "Query throughput measurement", 
        "System resource utilization",
        "Breaking point identification"
    ],
    "stress_testing": [
        "Peak load handling",
        "Memory pressure testing",
        "Database connection limits",
        "Recovery time measurement"
    ],
    "benchmark_testing": [
        "Response time validation",
        "Query generation speed",
        "Database query performance",
        "End-to-end latency"
    ]
}
```

### @rag-researcher - RAG System Testing
```python
rag_test_scenarios = {
    "retrieval_accuracy": [
        "Semantic similarity validation",
        "Context relevance scoring",
        "Query-result alignment",
        "False positive reduction"
    ],
    "embedding_quality": [
        "Vector similarity consistency",
        "Embedding drift detection",
        "Cross-domain performance",
        "Dimension optimization"
    ],
    "storage_optimization": [
        "S3 access pattern efficiency",
        "Vector search performance",
        "Cache hit rate optimization",
        "Cost per query analysis"
    ]
}
```

## Testing Commands & Workflows

### Agent-Specific Testing
```bash
# Security layer testing
/agent:summon @security-guardian "run comprehensive security test suite"

# Performance validation
/agent:summon @performance-optimizer "execute load testing for 100 concurrent users"

# RAG system validation
/agent:summon @rag-researcher "test retrieval accuracy for business queries"

# End-to-end testing
/agent:summon @test-engineer "run complete user workflow tests"
```

### Multi-Agent Testing Coordination
```bash
# Security + Performance testing
/agent:collaborate @security-guardian @performance-optimizer "test security layer performance impact"

# RAG + Performance testing  
/agent:collaborate @rag-researcher @performance-optimizer "optimize RAG system for speed"

# Comprehensive system testing
/agent:hive-mind "execute full system test suite with all agents"
```

## Test Implementation Patterns

### Security Testing Example
```python
# Layer 1 - Input Sanitization Testing
class TestInputSanitization:
    
    @pytest.mark.security
    async def test_xss_injection_blocked(self):
        """Test XSS injection attempts are blocked"""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ]
        
        for malicious_input in malicious_inputs:
            sanitized = sanitize_input(malicious_input)
            assert '<script>' not in sanitized
            assert 'javascript:' not in sanitized
            assert 'onerror=' not in sanitized
    
    @pytest.mark.security  
    async def test_sql_injection_blocked(self):
        """Test SQL injection attempts are blocked"""
        sql_injections = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM secrets"
        ]
        
        for injection in sql_injections:
            with pytest.raises(SecurityException):
                await classify_query_intent(injection)
```

### Performance Testing Example
```python
# Load Testing Implementation
class TestSystemLoad:
    
    @pytest.mark.performance
    async def test_concurrent_query_performance(self):
        """Test system performance under concurrent load"""
        
        async def simulate_user_query():
            response = await client.post("/api/query", json={
                "question": "How many customers this month?",
                "account_id": 12345
            })
            return response.elapsed.total_seconds()
        
        # Simulate 50 concurrent users
        tasks = [simulate_user_query() for _ in range(50)]
        response_times = await asyncio.gather(*tasks)
        
        # Validate performance targets
        p95_response_time = np.percentile(response_times, 95)
        assert p95_response_time < 2.0  # <2 second P95 target
        
        avg_response_time = np.mean(response_times)
        assert avg_response_time < 1.5  # <1.5 second average
```

### RAG Testing Example
```python
# RAG Accuracy Testing
class TestRAGAccuracy:
    
    @pytest.mark.rag
    async def test_retrieval_accuracy(self):
        """Test RAG retrieval accuracy for business queries"""
        
        test_queries = [
            {
                "query": "monthly revenue trends",
                "expected_context": ["invoice", "billing_date", "amount"],
                "relevance_threshold": 0.8
            },
            {
                "query": "active customer count", 
                "expected_context": ["customer", "date_deleted", "account_id"],
                "relevance_threshold": 0.85
            }
        ]
        
        for test_case in test_queries:
            retrieved_context = await rag_system.retrieve_context(test_case["query"])
            relevance_score = calculate_context_relevance(
                retrieved_context, 
                test_case["expected_context"]
            )
            
            assert relevance_score >= test_case["relevance_threshold"]
```

## Continuous Testing Integration

### Pre-commit Testing
```bash
#!/bin/bash
# Pre-commit hook for agent-driven testing

# Security testing (fast)
/agent:summon @security-guardian "run critical security tests"

# Unit testing
pytest tests/unit/ -v --tb=short

# Performance regression testing (quick)
/agent:summon @performance-optimizer "run performance regression tests"
```

### CI/CD Pipeline Testing
```yaml
# GitHub Actions testing pipeline
name: Agent-Driven Testing
on: [push, pull_request]

jobs:
  security-testing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Security Layer Testing
        run: |
          /agent:summon @security-guardian "run full security test suite"
          
  performance-testing:
    runs-on: ubuntu-latest  
    steps:
      - uses: actions/checkout@v2
      - name: Performance Validation
        run: |
          /agent:summon @performance-optimizer "validate performance benchmarks"
          
  rag-testing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2  
      - name: RAG System Validation
        run: |
          /agent:summon @rag-researcher "test RAG retrieval accuracy"
```

## Testing Quality Metrics

### Success Criteria by Agent
```python
testing_kpis = {
    "@test-engineer": {
        "code_coverage": "> 90%",
        "test_execution_time": "< 5 minutes",
        "test_reliability": "> 99% pass rate",
        "bug_detection_rate": "> 95%"
    },
    "@security-guardian": {
        "security_test_coverage": "100% of 7 layers",
        "attack_detection_rate": "> 99.9%",
        "false_positive_rate": "< 1%",
        "vulnerability_detection": "100% of known issues"
    },
    "@performance-optimizer": {
        "load_test_success": "100 concurrent users",
        "response_time_validation": "< 2s P95",
        "resource_utilization": "< 70% CPU average",
        "throughput_target": "> 25 queries/second"
    },
    "@rag-researcher": {
        "retrieval_accuracy": "> 95%",
        "context_relevance": "> 90%",
        "embedding_consistency": "> 98%",
        "storage_efficiency": "< $20/month cost"
    }
}
```

## IMPORTANT: Testing Best Practices

### For All Agents
1. **Test early and often** - Don't wait for complete features
2. **Write tests that fail first** - TDD approach
3. **Test real-world scenarios** - Not just happy paths
4. **Automate everything possible** - Reduce manual testing overhead
5. **Document test rationale** - Explain why tests exist

### Agent-Specific Guidelines
- **@test-engineer**: Focus on comprehensive coverage and maintainable test suites
- **@security-guardian**: Prioritize attack simulation and vulnerability detection  
- **@performance-optimizer**: Establish clear performance benchmarks and thresholds
- **@rag-researcher**: Validate accuracy and relevance with real business queries

Remember: Testing is not just about finding bugs - it's about ensuring the system meets its promises to users!