"""
Training Routes
Manage training data for improving SQL generation
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.auth.middleware import get_current_user
from backend.services.bedrock_vanna import BedrockVanna

router = APIRouter()
vanna_service = BedrockVanna()


class TrainingPair(BaseModel):
    """Training pair model"""
    question: str
    sql: str
    metadata: Optional[Dict[str, Any]] = None


class TrainingResponse(BaseModel):
    """Training response model"""
    id: str
    message: str
    timestamp: datetime


@router.post("/add", response_model=TrainingResponse)
async def add_training_data(
    training_pair: TrainingPair,
    current_user: Dict = Depends(get_current_user)
) -> TrainingResponse:
    """
    Add a new training pair (question-SQL)
    """
    try:
        # Add account_id to metadata
        metadata = training_pair.metadata or {}
        metadata["account_id"] = current_user.get("account_id")
        metadata["added_by"] = current_user.get("username")
        
        # Add training data
        vanna_service.train(
            question=training_pair.question,
            sql=training_pair.sql
        )
        
        return TrainingResponse(
            id=f"training_{datetime.utcnow().timestamp()}",
            message="Training data added successfully",
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add training data: {str(e)}"
        )


@router.get("/list")
async def list_training_data(
    limit: int = 100,
    current_user: Dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    List all training data
    """
    try:
        training_data = vanna_service.get_training_data()
        
        # Filter by account_id
        account_id = current_user.get("account_id")
        filtered_data = [
            item for item in training_data
            if item.get("metadata", {}).get("account_id") == account_id
        ]
        
        return filtered_data[:limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve training data: {str(e)}"
        )


@router.delete("/{training_id}")
async def delete_training_data(
    training_id: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Delete specific training data
    """
    try:
        vanna_service.remove_training_data(training_id)
        
        return {
            "message": f"Training data {training_id} deleted successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete training data: {str(e)}"
        )