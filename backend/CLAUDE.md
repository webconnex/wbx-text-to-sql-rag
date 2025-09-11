# 🔧 Backend Development Guide - FastAPI + Agent Architecture

## Specialized Agents for Backend Development

### Primary Agents
- **@api-architect**: FastAPI design patterns, async operations, routing
- **@security-guardian**: 7-layer security implementation, JWT validation
- **@performance-optimizer**: Async optimization, connection pooling, caching
- **@nova-whisperer**: Bedrock integration, prompt optimization
- **@rag-researcher**: Vector storage, embedding operations, S3 integration

## FastAPI Architecture

### Application Structure
```
backend/
├── main.py                 # FastAPI app initialization
├── api/routes/            # API endpoint definitions
├── services/              # Business logic and external integrations
├── auth/                  # Authentication and authorization
├── config/                # Configuration management
└── utils/                 # Shared utilities
```

### Critical FastAPI Patterns

#### Async Route Definitions
```python
@router.post("/query")
async def execute_query(
    request: QueryRequest,
    current_user: User = Depends(get_current_user)
) -> QueryResponse:
    """Execute natural language query with full security validation"""
    
    # 7-layer security validation
    await validate_security_layers(request, current_user)
    
    # Async processing pipeline
    async with get_db_session() as session:
        result = await process_query_async(request, session)
        
    return QueryResponse(**result)
```

#### Dependency Injection
```python
# Database dependency
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Authentication dependency
async def get_current_user(token: str = Depends(get_token)) -> User:
    return await validate_jwt_token(token)
```

#### Error Handling
```python
@app.exception_handler(SecurityException)
async def security_exception_handler(request: Request, exc: SecurityException):
    return JSONResponse(
        status_code=403,
        content={"detail": "Security violation detected", "type": exc.violation_type}
    )
```

## Security Implementation

### 7-Layer Security Architecture
```python
async def validate_security_layers(request: QueryRequest, user: User) -> None:
    """Implement all 7 security layers"""
    
    # Layer 1: Input Sanitization
    sanitized_input = sanitize_input(request.question)
    
    # Layer 2: JWT Authentication (already done via dependency)
    
    # Layer 3: Query Classification
    query_intent = await classify_query_intent(sanitized_input)
    if query_intent != "READ_ONLY":
        raise SecurityException("Malicious query intent detected")
    
    # Layer 4: AI Safety (handled in BedrockVanna)
    
    # Layer 5: SQL Validation (post-generation)
    
    # Layer 6: Account Isolation (enforced in query execution)
    
    # Layer 7: Result Limiting (applied to query results)
```

### JWT Token Management
```python
from jose import JWTError, jwt
from passlib.context import CryptContext

async def validate_jwt_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        account_id: str = payload.get("account_id")
        if account_id is None:
            raise AuthenticationException("Invalid token: missing account_id")
        return payload
    except JWTError:
        raise AuthenticationException("Invalid token")
```

## Database Integration

### Connection Management
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

# Async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    echo=False  # Set to True for SQL logging in development
)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

### Query Execution with RLS
```python
async def execute_secure_query(sql: str, account_id: int, session: AsyncSession) -> List[dict]:
    """Execute query with Row-Level Security"""
    
    # Set account context for RLS
    await session.execute(text(f"SET app.current_account_id = {account_id}"))
    
    # Execute query with automatic account_id filtering
    result = await session.execute(text(sql))
    
    # Convert to list of dictionaries
    return [dict(row) for row in result.fetchall()]
```

## Bedrock Integration

### BedrockVanna Service Usage
```python
from backend.services.bedrock_vanna import BedrockVanna

async def generate_sql_with_context(
    question: str, 
    account_id: int,
    bedrock_vanna: BedrockVanna
) -> str:
    """Generate SQL using BedrockVanna with proper context"""
    
    try:
        # Generate SQL with account context
        sql = await bedrock_vanna.generate_sql_async(question, account_id)
        
        # Validate generated SQL
        if not bedrock_vanna._validate_sql_readonly(sql):
            raise SecurityException("Generated SQL failed security validation")
            
        return sql
        
    except Exception as e:
        logger.error(f"SQL generation failed: {str(e)}")
        raise QueryGenerationException(f"Unable to generate SQL: {str(e)}")
```

## Development Commands

### Server Management
```bash
# Development server with hot reload
uvicorn backend.main:app --reload --port 8000 --host 0.0.0.0

# Production server
uvicorn backend.main:app --workers 4 --port 8000

# Debug mode with detailed logging
uvicorn backend.main:app --reload --port 8000 --log-level debug
```

### Testing
```bash
# Run backend tests
pytest backend/tests/ -v

# Test specific security layers
pytest backend/tests/test_security_layers.py -v

# Test API endpoints
pytest backend/tests/test_api_routes.py -v

# Test async functionality
pytest backend/tests/test_async_operations.py -v
```

### Database Operations
```bash
# Test database connection
python -c "from backend.config.settings import settings; print('DB Config:', settings.DATABASE_URL)"

# Run migrations (if using Alembic)
alembic upgrade head

# Test Redshift connection
python scripts/test_redshift.py
```

## Performance Optimization

### Async Best Practices
```python
# Use connection pooling
async with get_db_session() as session:
    # Database operations
    pass

# Batch operations when possible
async def batch_process_queries(queries: List[str], account_id: int):
    async with get_db_session() as session:
        results = []
        for query in queries:
            result = await execute_secure_query(query, account_id, session)
            results.append(result)
        return results
```

### Caching Strategy
```python
from functools import lru_cache
import asyncio
import aioredis

# Schema caching (rarely changes)
@lru_cache(maxsize=128)
def get_schema_info(account_id: int) -> dict:
    # Cache schema information
    pass

# Query result caching
async def cache_query_result(query_hash: str, result: dict, ttl: int = 1800):
    redis = aioredis.from_url("redis://localhost")
    await redis.setex(query_hash, ttl, json.dumps(result))
```

## Error Handling & Logging

### Custom Exception Classes
```python
class TextToSQLException(Exception):
    """Base exception for Text-to-SQL system"""
    pass

class SecurityException(TextToSQLException):
    """Security violation detected"""
    def __init__(self, message: str, violation_type: str = "unknown"):
        self.violation_type = violation_type
        super().__init__(message)

class QueryGenerationException(TextToSQLException):
    """SQL generation failed"""
    pass

class DatabaseException(TextToSQLException):
    """Database operation failed"""
    pass
```

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

async def log_query_execution(
    question: str, 
    generated_sql: str, 
    account_id: int, 
    execution_time: float,
    result_count: int
):
    logger.info(
        "query_executed",
        question=question[:100],  # Truncate for privacy
        sql_length=len(generated_sql),
        account_id=account_id,
        execution_time_ms=round(execution_time * 1000, 2),
        result_count=result_count,
        timestamp=datetime.utcnow().isoformat()
    )
```

## Common Patterns & Anti-Patterns

### ✅ DO: Use These Patterns
```python
# Proper async context management
async with get_db_session() as session:
    result = await session.execute(query)

# Dependency injection for reusable components
def get_bedrock_vanna() -> BedrockVanna:
    return BedrockVanna()

# Structured error responses
return JSONResponse(
    status_code=400,
    content={
        "error": "validation_failed",
        "detail": "Query contains forbidden operations",
        "timestamp": datetime.utcnow().isoformat()
    }
)
```

### ❌ DON'T: Avoid These Anti-Patterns
```python
# Don't use synchronous database operations
# BAD: session.execute(query)
# GOOD: await session.execute(query)

# Don't hardcode account IDs
# BAD: WHERE account_id = 123
# GOOD: WHERE account_id = {account_id}

# Don't ignore security validation
# BAD: return generate_sql_directly(question)
# GOOD: return await validate_and_generate_sql(question, account_id)
```

## IMPORTANT: Backend Development Rules
1. **ALWAYS** use async/await for database operations
2. **NEVER** skip security layer validation
3. **ALWAYS** validate account_id in queries
4. **NEVER** log sensitive user data or SQL content
5. **ALWAYS** use connection pooling for database access
6. **NEVER** hardcode credentials or configuration

Remember: The backend is the security and performance backbone of the entire system!