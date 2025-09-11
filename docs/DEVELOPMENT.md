# Development Guide - Webconnex AI Text-to-SQL System

## 🚀 Quick Start

### One Command Setup
```bash
./start_all.sh
```
That's it! The entire system launches automatically.

## 🛠️ Development Environment Setup

### Prerequisites
- **Python**: 3.10 or higher
- **AWS CLI**: Configured with appropriate credentials
- **AWS Bedrock Access**: Amazon Nova Pro model access required
- **Redshift Access**: Connection to Webconnex data warehouse
- **Git**: For version control

### Initial Setup
```bash
# 1. Clone the repository
git clone [repository-url]
cd "text to sql + Vector"

# 2. Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment configuration
cp .env.example .env
# Edit .env with your actual AWS credentials and configuration

# 5. Configure AWS credentials
export AWS_PROFILE=your-okta-profile-name
gimme-aws-creds --profile your-okta-profile-name

# 6. Launch the system
./start_all.sh
```

### Environment Configuration

Create your `.env` file based on `.env.example`:

```env
# Essential settings
AWS_REGION=us-west-2
AWS_PROFILE=your-okta-profile-name
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
REDSHIFT_DATABASE=wbx_data
REDSHIFT_SCHEMA=webconnex

# Security (change these!)
JWT_SECRET_KEY=your-super-secret-key
OKTA_CLIENT_SECRET=your-okta-secret
```

## 🏗️ Architecture Overview

### System Components
```
Frontend (Streamlit) ←→ Backend (FastAPI) ←→ Amazon Nova Pro ←→ Redshift
        ↓                    ↓                   ↓             ↓
   User Interface        API Server        AI Processing    Data Storage
```

### Directory Structure
```
webconnex-ai-text-to-sql/
├── 🚀 start_all.sh              # Main startup script
├── 📱 frontend_streamlit_v2.py  # Production UI
├── ⚙️ backend/                  # FastAPI application
│   ├── main.py                 # FastAPI app entry point
│   ├── services/
│   │   ├── bedrock_vanna.py    # Nova Pro integration
│   │   └── prompt_templates.py # AI prompts
│   ├── api/routes/             # REST API endpoints
│   │   ├── query.py           # Main query endpoint
│   │   ├── auth.py            # Authentication
│   │   └── health.py          # Health checks
│   └── config/settings.py      # Configuration
├── 🧪 tests/                   # Test suite
├── 📜 scripts/                 # Utility scripts
├── 🗄️ data/schemas/            # Database schemas
└── 📚 docs/                    # Documentation
```

## 🔧 Development Workflow

### Running Individual Components

#### Backend Only
```bash
export AWS_PROFILE=your-profile
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Only
```bash
streamlit run frontend_streamlit_v2.py
```

#### Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_security_layers.py -v
pytest tests/test_nova_integration.py -v

# Run with coverage
pytest --cov=backend tests/
```

### Development Tools

#### API Documentation
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative UI**: http://localhost:8000/redoc
- **OpenAPI Spec**: http://localhost:8000/openapi.json

#### Testing Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Test query
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many customers do we have?", "account_id": 123}'
```

## 🧪 Testing Strategy

### Test Categories
1. **Unit Tests**: Individual function testing
2. **Integration Tests**: Component interaction testing  
3. **Security Tests**: 7-layer security validation
4. **Performance Tests**: Load and stress testing
5. **End-to-End Tests**: Full workflow validation

### Running Tests
```bash
# Quick smoke test
python scripts/test_simple.py

# Full security suite
python tests/test_security_layers.py

# Performance benchmarks
python tests/test_performance.py

# Nova Pro integration
python tests/test_nova_production.py
```

### Test Data
- **Mock Data**: `mock_webconnex_data.json`
- **Schema Files**: `data/schemas/redshift_ddl.sql`
- **Training Data**: Sample Q&A pairs for model training

## 🔒 Security Development Guidelines

### Code Security Best Practices
1. **Never hardcode credentials** - Use environment variables
2. **Validate all inputs** - Sanitize user data
3. **Use parameterized queries** - Prevent SQL injection
4. **Log security events** - Track authentication attempts
5. **Implement rate limiting** - Prevent abuse

### Security Testing
```bash
# Test input sanitization
python tests/test_layer1_input_sanitization.py

# Test authentication
python tests/test_layer2_authentication.py

# Full security suite
python tests/test_all_security_layers.py
```

### Credential Management
```bash
# AWS credentials refresh
gimme-aws-creds --profile your-profile-name

# Check current identity
aws sts get-caller-identity

# Test Bedrock access
aws bedrock list-foundation-models
```

## 🎯 AI Model Integration

### Amazon Nova Pro Configuration
```python
# Model configuration
BEDROCK_MODEL_ID = "us.amazon.nova-pro-v1:0"
BEDROCK_REGION = "us-west-2"
MAX_TOKENS = 1000

# Security constraints in prompts
SECURITY_PROMPT = """
MANDATORY RULES:
1. ONLY SELECT queries allowed
2. MUST include account_id filter
3. MUST include LIMIT clause
"""
```

### Custom Vanna Implementation
```python
from backend.services.bedrock_vanna import BedrockVanna

# Initialize with security
vn = BedrockVanna()
vn.connect_to_redshift(
    database="wbx_data",
    schema="webconnex"
)

# Generate secure SQL
sql = vn.generate_sql(
    question="How many customers?",
    account_id=123
)
```

### Training the Model
```python
# Add training examples
vn.train(
    question="How many active customers?",
    sql="SELECT COUNT(*) FROM customer WHERE account_id = ? AND date_deleted IS NULL"
)

# Training best practices
- Use account_id placeholders
- Include LIMIT clauses
- Follow naming conventions
- Test with various phrasings
```

## 📊 Database Development

### Schema Overview
```sql
-- Main tables in wbx_data.webconnex
account      -- Multi-tenant base table
invoice      -- Billing and revenue data  
customer     -- Customer information
registration -- Orders and events
form         -- Form configurations
```

### Query Patterns
```sql
-- Revenue query pattern
SELECT SUM(amount) as total_revenue
FROM wbx_data.webconnex.invoice
WHERE account_id = ? 
  AND billing_date >= ?
  AND status = 'completed'
LIMIT 1000;

-- Customer analytics pattern  
SELECT COUNT(*) as active_customers
FROM wbx_data.webconnex.customer
WHERE account_id = ?
  AND date_deleted IS NULL
LIMIT 1000;
```

### Row-Level Security (RLS)
```sql
-- Example RLS policy
CREATE POLICY account_isolation ON invoice
FOR ALL TO application_role
USING (account_id = current_setting('app.current_account_id')::int);
```

## 🚀 Deployment Guidelines

### Local Development
```bash
# Development mode with hot reload
./start_all.sh

# Production-like mode
export DEBUG=false
export API_RELOAD=false
./start_all.sh
```

### Docker Deployment
```bash
# Build images
docker build -t webconnex-text-sql-backend ./backend
docker build -t webconnex-text-sql-frontend .

# Run with docker-compose
docker-compose up -d
```

### Environment-Specific Configuration
```env
# Development
DEBUG=true
API_RELOAD=true
LOG_LEVEL=debug

# Staging
DEBUG=false
API_RELOAD=false
LOG_LEVEL=info

# Production
DEBUG=false
API_RELOAD=false
LOG_LEVEL=warning
ENABLE_METRICS=true
```

## 🐛 Debugging & Troubleshooting

### Common Issues

#### AWS Credential Issues
```bash
# Check credentials
aws sts get-caller-identity

# Refresh credentials
gimme-aws-creds --profile your-profile

# Export profile
export AWS_PROFILE=your-profile-name
```

#### Bedrock Access Issues
```bash
# Test Nova Pro access
python scripts/test_bedrock.py

# Check available models
aws bedrock list-foundation-models --region us-west-2
```

#### Database Connection Issues
```bash
# Test Redshift connection
python scripts/test_redshift.py

# Check VPC connectivity
telnet your-redshift-cluster.amazonaws.com 5439
```

### Logging & Monitoring
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check application logs
tail -f logs/app.log
tail -f backend.log
tail -f frontend.log
```

### Performance Profiling
```bash
# Profile API endpoints
python -m cProfile scripts/test_api_performance.py

# Memory usage monitoring
python scripts/monitor_memory.py

# Database query analysis
EXPLAIN ANALYZE SELECT ...
```

## 📝 Code Style & Standards

### Python Code Style
```bash
# Format code
black backend/
black tests/
black scripts/

# Lint code
ruff check backend/
ruff check tests/

# Type checking
mypy backend/
```

### Git Workflow
```bash
# Feature branch workflow
git checkout -b feature/new-query-type
git add .
git commit -m "Add support for trend analysis queries"
git push origin feature/new-query-type

# Create pull request
# After review and approval, merge to main
```

### Commit Message Format
```
type(scope): description

Examples:
feat(api): add new aggregation endpoint
fix(security): resolve SQL injection vulnerability
docs(readme): update setup instructions
test(security): add prompt injection tests
```

## 🔄 Continuous Integration

### Automated Testing
```yaml
# Example CI pipeline
name: Test & Deploy
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run security tests
        run: pytest tests/test_security_layers.py
      - name: Run integration tests  
        run: pytest tests/test_integration.py
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Manual run
pre-commit run --all-files
```

## 📚 Additional Resources

### Documentation
- **API Reference**: `/docs/API_REFERENCE.md`
- **Security Audit**: `/docs/SECURITY_AUDIT.md`
- **Testing Reports**: `/docs/TESTING_REPORTS.md`

### External Resources
- [Vanna AI Documentation](https://vanna.ai/docs/)
- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

### Support Channels
- **Slack**: #text-to-sql-dev
- **Email**: engineering@webconnex.com
- **Wiki**: [Internal Development Wiki]

---

**Last Updated**: January 27, 2025  
**Maintained By**: Webconnex Engineering Team  
**Version**: 2.0.0