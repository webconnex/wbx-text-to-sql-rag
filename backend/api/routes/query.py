"""
Query API Routes
Handles natural language to SQL query execution
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from backend.auth.middleware import get_current_user
from backend.services.bedrock_vanna import BedrockVanna
from backend.config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Vanna service
vanna_service = BedrockVanna()


class QueryRequest(BaseModel):
    """Query request model"""
    question: str = Field(..., description="Natural language question")
    account_id: int = Field(..., description="Account ID for multi-tenancy")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "How many invoices do I have this month?",
                "account_id": 123
            }
        }


class QueryResponse(BaseModel):
    """Query response model"""
    sql: str = Field(..., description="Generated SQL query")
    results: List[Dict[str, Any]] = Field(..., description="Query results")
    metadata: Dict[str, Any] = Field(..., description="Query metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sql": "SELECT COUNT(*) FROM invoice WHERE account_id = 123",
                "results": [{"count": 42}],
                "metadata": {
                    "row_count": 1,
                    "execution_time": "2024-01-14T10:30:00Z",
                    "account_id": 123
                }
            }
        }


class QueryHistoryItem(BaseModel):
    """Query history item model"""
    id: str
    question: str
    sql: str
    row_count: int
    execution_time: datetime
    account_id: int


@router.post("/", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    current_user: Dict = Depends(get_current_user)
) -> QueryResponse:
    """
    Execute natural language query
    
    Args:
        request: Query request with question and account_id
        current_user: Current authenticated user
        
    Returns:
        Query response with SQL and results
    """
    try:
        # Verify user has access to the account
        user_account_id = current_user.get("account_id")
        if user_account_id != request.account_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account"
            )
        
        logger.info(f"Processing query for account {request.account_id}: {request.question[:50]}...")
        
        # Generate SQL from natural language
        sql_query = vanna_service.generate_sql(
            question=request.question,
            account_id=request.account_id
        )
        
        # Execute SQL query
        df = vanna_service.execute_sql(
            sql=sql_query,
            account_id=request.account_id
        )
        
        # Convert DataFrame to list of dicts
        results = df.to_dict('records') if not df.empty else []
        
        # Prepare response
        response = QueryResponse(
            sql=sql_query,
            results=results,
            metadata={
                "row_count": len(results),
                "execution_time": datetime.utcnow().isoformat(),
                "account_id": request.account_id,
                "truncated": len(df) >= settings.MAX_QUERY_RESULTS if not df.empty else False
            }
        )
        
        logger.info(f"Query executed successfully for account {request.account_id}, returned {len(results)} rows")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute query: {str(e)}"
        )


@router.get("/history", response_model=List[QueryHistoryItem])
async def get_query_history(
    account_id: int,
    limit: int = 100,
    current_user: Dict = Depends(get_current_user)
) -> List[QueryHistoryItem]:
    """
    Get query history for an account
    
    Args:
        account_id: Account ID
        limit: Maximum number of items to return
        current_user: Current authenticated user
        
    Returns:
        List of query history items
    """
    try:
        # Verify user has access to the account
        user_account_id = current_user.get("account_id")
        if user_account_id != account_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account"
            )
        
        # TODO: Implement query history retrieval from database
        # For now, return empty list
        return []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting query history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve query history"
        )


@router.post("/validate")
async def validate_sql(
    sql: str,
    account_id: int,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate SQL query without executing
    
    Args:
        sql: SQL query to validate
        account_id: Account ID
        current_user: Current authenticated user
        
    Returns:
        Validation result
    """
    try:
        # Verify user has access to the account
        user_account_id = current_user.get("account_id")
        if user_account_id != account_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this account"
            )
        
        # Basic validation checks
        sql_upper = sql.upper()
        
        # Check for forbidden operations
        forbidden = ["DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", "CREATE", "ALTER"]
        for operation in forbidden:
            if operation in sql_upper:
                return {
                    "valid": False,
                    "error": f"Operation {operation} is not allowed"
                }
        
        # Check for account_id filter
        if f"account_id = {account_id}" not in sql.lower():
            return {
                "valid": False,
                "error": "Query must include account_id filter"
            }
        
        # TODO: Add more sophisticated SQL validation
        
        return {
            "valid": True,
            "message": "SQL query is valid"
        }
        
    except Exception as e:
        logger.error(f"Error validating SQL: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate SQL"
        )


@router.post("/explain")
async def explain_query(
    sql: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Get natural language explanation of SQL query
    
    Args:
        sql: SQL query to explain
        current_user: Current authenticated user
        
    Returns:
        Explanation of the query
    """
    try:
        # TODO: Use Bedrock to generate explanation
        # For now, return placeholder
        return {
            "sql": sql,
            "explanation": "This query retrieves data from the database based on the specified conditions."
        }
        
    except Exception as e:
        logger.error(f"Error explaining query: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to explain query"
        )