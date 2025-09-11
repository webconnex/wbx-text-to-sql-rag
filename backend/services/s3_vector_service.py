"""
S3 Vector Store Service
Manages embeddings and vector search using S3
"""

import json
import hashlib
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
import numpy as np

from backend.auth.aws_auth import aws_auth
from backend.config.settings import settings

logger = logging.getLogger(__name__)


class S3VectorService:
    """
    Vector store implementation using S3 and Amazon Titan Embeddings
    Provides embedding storage and similarity search
    """
    
    def __init__(self):
        """Initialize S3 Vector Service with Amazon Titan Embeddings"""
        self.s3_client = aws_auth.get_s3_client()
        self.bedrock_client = aws_auth.get_bedrock_client()
        self.bucket_name = settings.S3_BUCKET_VECTORS
        self.training_bucket = settings.S3_BUCKET_TRAINING
        
        # Use Amazon Titan Embeddings model
        self.embedding_model_id = settings.BEDROCK_MODEL_ID_EMBEDDINGS  # amazon.titan-embed-text-v1
        
        # Ensure buckets exist
        self._ensure_buckets_exist()
        
        logger.info(f"Initialized S3VectorService with bucket: {self.bucket_name}")
    
    def _ensure_buckets_exist(self):
        """Ensure S3 buckets exist"""
        try:
            # Check vectors bucket
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
            except:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': settings.S3_REGION}
                )
                logger.info(f"Created bucket: {self.bucket_name}")
            
            # Check training bucket
            try:
                self.s3_client.head_bucket(Bucket=self.training_bucket)
            except:
                self.s3_client.create_bucket(
                    Bucket=self.training_bucket,
                    CreateBucketConfiguration={'LocationConstraint': settings.S3_REGION}
                )
                logger.info(f"Created bucket: {self.training_bucket}")
                
        except Exception as e:
            logger.error(f"Error ensuring buckets exist: {e}")
    
    def _generate_key(self, content: str, prefix: str = "embeddings") -> str:
        """
        Generate S3 key for content
        
        Args:
            content: Content to hash
            prefix: S3 key prefix
            
        Returns:
            S3 key
        """
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{prefix}/{content_hash}.json"
    
    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding using Amazon Titan Embeddings
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            # Call Amazon Titan Embeddings
            response = self.bedrock_client.invoke_model(
                modelId=self.embedding_model_id,
                body=json.dumps({
                    "inputText": text[:8192]  # Titan has 8K token limit
                })
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            embedding = response_body.get('embedding', [])
            
            return embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            # Return empty embedding on error
            return []
    
    def add_training_pair(
        self,
        question: str,
        sql: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add question-SQL training pair
        
        Args:
            question: Natural language question
            sql: Corresponding SQL query
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            # Generate embedding for question using Titan
            embedding = self._generate_embedding(question)
            
            # Create document
            document = {
                'id': hashlib.md5(f"{question}:{sql}".encode()).hexdigest(),
                'question': question,
                'sql': sql,
                'embedding': embedding,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store in S3
            key = f"training/{document['id']}.json"
            self.s3_client.put_object(
                Bucket=self.training_bucket,
                Key=key,
                Body=json.dumps(document),
                ContentType='application/json'
            )
            
            logger.info(f"Added training pair: {document['id']}")
            return document['id']
            
        except Exception as e:
            logger.error(f"Error adding training pair: {e}")
            raise
    
    def add_document(
        self,
        content: str,
        doc_type: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Add document to vector store
        
        Args:
            content: Document content
            doc_type: Document type (ddl, documentation, etc.)
            metadata: Additional metadata
            
        Returns:
            Document ID
        """
        try:
            # Generate embedding using Titan
            embedding = self._generate_embedding(content)
            
            # Create document
            document = {
                'id': hashlib.md5(content.encode()).hexdigest(),
                'content': content,
                'type': doc_type,
                'embedding': embedding,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Store in S3
            key = f"documents/{doc_type}/{document['id']}.json"
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=json.dumps(document),
                ContentType='application/json'
            )
            
            logger.info(f"Added document: {document['id']} (type: {doc_type})")
            return document['id']
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            raise
    
    def search(
        self,
        query: str,
        account_id: Optional[int] = None,
        top_k: int = 5,
        doc_types: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query
            account_id: Optional account ID filter
            top_k: Number of results to return
            doc_types: Filter by document types
            
        Returns:
            List of similar documents
        """
        try:
            # Generate query embedding using Titan
            query_embedding = np.array(self._generate_embedding(query))
            
            # List all relevant objects
            paginator = self.s3_client.get_paginator('list_objects_v2')
            
            # Search in training bucket
            results = []
            for page in paginator.paginate(Bucket=self.training_bucket, Prefix='training/'):
                for obj in page.get('Contents', []):
                    # Get object
                    response = self.s3_client.get_object(
                        Bucket=self.training_bucket,
                        Key=obj['Key']
                    )
                    document = json.loads(response['Body'].read())
                    
                    # Filter by account_id if specified
                    if account_id and document.get('metadata', {}).get('account_id') != account_id:
                        continue
                    
                    # Calculate similarity
                    doc_embedding = np.array(document['embedding'])
                    similarity = np.dot(query_embedding, doc_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(doc_embedding)
                    )
                    
                    results.append({
                        'document': document,
                        'similarity': float(similarity)
                    })
            
            # Sort by similarity and return top_k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return [r['document'] for r in results[:top_k]]
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_all_training_data(self) -> List[Dict]:
        """
        Get all training data
        
        Returns:
            List of all training documents
        """
        try:
            training_data = []
            
            # List all training objects
            paginator = self.s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.training_bucket, Prefix='training/'):
                for obj in page.get('Contents', []):
                    # Get object
                    response = self.s3_client.get_object(
                        Bucket=self.training_bucket,
                        Key=obj['Key']
                    )
                    document = json.loads(response['Body'].read())
                    training_data.append(document)
            
            return training_data
            
        except Exception as e:
            logger.error(f"Error getting training data: {e}")
            return []
    
    def delete_document(self, doc_id: str):
        """
        Delete document from vector store
        
        Args:
            doc_id: Document ID to delete
        """
        try:
            # Try to delete from both buckets
            keys_to_delete = [
                f"training/{doc_id}.json",
                f"documents/ddl/{doc_id}.json",
                f"documents/documentation/{doc_id}.json"
            ]
            
            for key in keys_to_delete:
                try:
                    self.s3_client.delete_object(
                        Bucket=self.training_bucket if 'training' in key else self.bucket_name,
                        Key=key
                    )
                    logger.info(f"Deleted document: {key}")
                except:
                    pass  # Document might not exist in all locations
                    
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            raise
    
    def create_schema_embeddings(self, account_id: int):
        """
        Create embeddings for Webconnex schema
        
        Args:
            account_id: Account ID for context
        """
        try:
            # Schema contexts for each table
            table_contexts = {
                "account": """
                Table: account
                Purpose: Main account/organization information
                Business context: Each account represents a Webconnex customer
                Key columns: id (PK), name, email, organization_id
                Common queries: "account information", "organization details"
                Examples: "What is my account name?", "When was my account created?"
                """,
                
                "invoice": """
                Table: invoice  
                Purpose: Billing and revenue tracking
                Business context: Monthly/annual billing for Webconnex services
                Key columns: id, amount, status, billing_date, invoice_number
                Relationships: Connected to account via billing_id
                Common queries: "billing", "invoices", "revenue", "payments"
                Examples: "How many invoices this month?", "Total revenue this year?"
                """,
                
                "customer": """
                Table: customer
                Purpose: Customer records per account
                Business context: End users of each account's services
                Key columns: id, account_id, email, date_created
                Relationships: customer.account_id -> account.id
                Common queries: "customers", "users", "contacts"
                Examples: "How many customers?", "New users today?"
                """,
                
                "registration": """
                Table: registration (also called order)
                Purpose: Event registrations and orders
                Business context: Each registration is a purchase or signup
                Key columns: id, account_id, customer_id, total, status, date_completed
                Relationships: Links to account, customer, and form
                Common queries: "registrations", "orders", "sales", "events"
                Examples: "Registrations today?", "Total sales this month?"
                """
            }
            
            # Create embeddings for each table context
            for table_name, context in table_contexts.items():
                self.add_document(
                    content=context,
                    doc_type='schema',
                    metadata={
                        'table': table_name,
                        'account_id': account_id
                    }
                )
            
            # Add common query patterns
            common_queries = [
                {
                    "question": "How many invoices this month?",
                    "sql": "SELECT COUNT(*) FROM invoice WHERE EXTRACT(month FROM billing_date) = EXTRACT(month FROM CURRENT_DATE) AND EXTRACT(year FROM billing_date) = EXTRACT(year FROM CURRENT_DATE) AND account_id = ?",
                },
                {
                    "question": "Total revenue this year?",
                    "sql": "SELECT SUM(amount) FROM invoice WHERE EXTRACT(year FROM billing_date) = EXTRACT(year FROM CURRENT_DATE) AND status = 'completed' AND account_id = ?",
                },
                {
                    "question": "How many customers?",
                    "sql": "SELECT COUNT(*) FROM customer WHERE date_deleted IS NULL AND account_id = ?",
                },
                {
                    "question": "Registrations completed today?",
                    "sql": "SELECT COUNT(*) FROM registration WHERE DATE(date_completed) = CURRENT_DATE AND status = 1 AND account_id = ?",
                }
            ]
            
            for query_pattern in common_queries:
                self.add_training_pair(
                    question=query_pattern["question"],
                    sql=query_pattern["sql"].replace("?", str(account_id)),
                    metadata={
                        'account_id': account_id,
                        'type': 'common_pattern'
                    }
                )
            
            logger.info(f"Created schema embeddings for account {account_id}")
            
        except Exception as e:
            logger.error(f"Error creating schema embeddings: {e}")
            raise