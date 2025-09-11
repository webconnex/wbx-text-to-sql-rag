"""
Custom Vanna implementation with AWS Bedrock integration
Provides Text-to-SQL capabilities using Claude on AWS
"""

import json
import logging
from typing import Dict, List, Optional, Any
import pandas as pd

from vanna.base import VannaBase
from backend.auth.aws_auth import aws_auth
from backend.config.settings import settings
from backend.services.s3_vector_service import S3VectorService
from backend.services.prompt_templates import NovaProPrompts, PromptExamples

logger = logging.getLogger(__name__)


class BedrockVanna(VannaBase):
    """
    Vanna implementation using AWS Bedrock (Claude) and S3 Vectors
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize BedrockVanna with configuration
        
        Args:
            config: Optional configuration dictionary
        """
        super().__init__(config=config or {})
        
        # Initialize AWS clients
        self.bedrock_client = aws_auth.get_bedrock_client()
        self.redshift_client = aws_auth.get_redshift_client()
        
        # Initialize vector store
        self.vector_store = S3VectorService()
        
        # Model configuration - Using Amazon Nova Pro
        self.model_id = settings.BEDROCK_MODEL_ID  # us.amazon.nova-pro-v1:0
        self.embedding_model_id = settings.BEDROCK_MODEL_ID_EMBEDDINGS  # amazon.titan-embed-text-v1
        self.max_tokens = settings.BEDROCK_MAX_TOKENS
        
        # FORBIDDEN SQL OPERATIONS - NEVER ALLOW THESE
        self.forbidden_operations = [
            'CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'DELETE', 'UPDATE', 'INSERT',
            'MERGE', 'REPLACE', 'GRANT', 'REVOKE', 'COMMIT', 'ROLLBACK',
            'SET', 'EXEC', 'EXECUTE', 'CALL', 'INTO', 'COPY'
        ]
        
        # Load schema context
        self.schema_context = self._load_schema_context()
        
        logger.info(f"Initialized BedrockVanna with model: {self.model_id}")
    
    def _load_schema_context(self) -> str:
        """
        Load Webconnex schema context for RAG
        
        Returns:
            Schema context string
        """
        return """
        Database: Webconnex Platform (Amazon Redshift)
        Schema: wbx_data.webconnex
        
        IMPORTANT: All tables are in the schema wbx_data.webconnex
        Always use fully qualified table names: wbx_data.webconnex.table_name
        
        TABLES:
        
        1. account (Multi-tenant base table)
           - id: integer (PK) - Account ID
           - name: varchar(150) - Organization name
           - email: varchar(180) - Contact email
           - date_created: timestamp - Creation date
           - organization_id: integer - Parent org ID
           
        2. invoice (Billing and revenue)
           - id: bigint (PK) - Invoice ID
           - billing_id: integer - Billing config ID
           - account_id: integer (FK) - Account reference
           - amount: numeric - Invoice amount
           - status: varchar - Payment status (completed, pending)
           - invoice_number: varchar - Invoice number
           - billing_date: timestamp - Billing date
           - start_date: timestamp - Period start
           - end_date: timestamp - Period end
           
        3. customer (Customer records)
           - id: bigint (PK) - Customer ID
           - account_id: integer (FK) - Account reference
           - email: varchar - Customer email
           - mobile_phone: varchar - Phone number
           - date_created: timestamp - Registration date
           - date_last_login: timestamp - Last login
           - date_deleted: timestamp - Deletion date (soft delete)
           
        4. registration (Orders/Events)
           - id: bigint (PK) - Registration ID
           - account_id: bigint (FK) - Account reference
           - customer_id: bigint (FK) - Customer reference
           - form_id: bigint (FK) - Form reference
           - total: numeric - Order total
           - status: smallint - Order status (1=completed)
           - order_number: varchar - Order number
           - date_created: timestamp - Creation date
           - date_completed: timestamp - Completion date
           - event_date: timestamp - Event date
           
        5. form (Forms/Pages)
           - id: bigint (PK) - Form ID
           - account_id: integer (FK) - Account reference
           - name: varchar - Form name
           
        RELATIONSHIPS:
        - wbx_data.webconnex.customer.account_id -> wbx_data.webconnex.account.id
        - wbx_data.webconnex.registration.account_id -> wbx_data.webconnex.account.id
        - wbx_data.webconnex.registration.customer_id -> wbx_data.webconnex.customer.id
        - wbx_data.webconnex.registration.form_id -> wbx_data.webconnex.form.id
        - wbx_data.webconnex.invoice connects to account via billing configuration
        
        IMPORTANT RULES:
        - Always filter by account_id for multi-tenancy
        - Use date functions: CURRENT_DATE, EXTRACT, DATE_TRUNC
        - Status fields: registration.status (1=completed)
        - Soft deletes: Check date_deleted IS NULL
        """
    
    def _validate_sql_readonly(self, sql: str) -> bool:
        """
        Validate that SQL is read-only and safe
        
        Args:
            sql: SQL query to validate
            
        Returns:
            True if SQL is safe, raises exception otherwise
        """
        sql_upper = sql.upper()
        
        # Remove strings and comments to avoid false positives
        # Remove content within single quotes
        import re
        sql_check = re.sub(r"'[^']*'", '', sql_upper)
        # Remove content within double quotes
        sql_check = re.sub(r'"[^"]*"', '', sql_check)
        # Remove SQL comments
        sql_check = re.sub(r'--.*$', '', sql_check, flags=re.MULTILINE)
        sql_check = re.sub(r'/\*.*?\*/', '', sql_check, flags=re.DOTALL)
        
        # Check for forbidden operations as standalone words (not part of column names)
        for operation in self.forbidden_operations:
            # Check if operation appears as a standalone word
            pattern = r'\b' + operation + r'\b'
            if re.search(pattern, sql_check):
                # Special case: allow 'date_deleted', 'is_deleted' etc.
                if operation == 'DELETE' and 'DATE_DELETE' in sql_upper:
                    continue
                if operation == 'CREATE' and 'DATE_CREATE' in sql_upper:
                    continue
                raise ValueError(f"SECURITY VIOLATION: Operation '{operation}' is strictly forbidden. Only SELECT queries are allowed.")
        
        # Ensure it starts with SELECT (after removing whitespace and comments)
        sql_clean = sql_upper.strip()
        if not sql_clean.startswith('SELECT') and not sql_clean.startswith('WITH'):
            raise ValueError("SECURITY VIOLATION: Only SELECT and WITH (CTE) queries are allowed.")
        
        return True
    
    def generate_sql(self, question: str, account_id: int) -> str:
        """
        Generate SQL from natural language question using Amazon Nova Pro
        
        Args:
            question: Natural language question
            account_id: Account ID for multi-tenancy
            
        Returns:
            Generated SQL query (READ-ONLY)
        """
        try:
            # Get relevant context from vector store
            context_docs = self.vector_store.search(
                question, 
                account_id=account_id,
                top_k=5
            )
            
            # Build enhanced context
            enhanced_context = self.schema_context
            if context_docs:
                enhanced_context += "\n\nRELEVANT EXAMPLES:\n"
                for doc in context_docs:
                    enhanced_context += f"- {doc.get('question', '')}: {doc.get('sql', '')}\n"
            
            # Build prompt optimized for Amazon Nova Pro
            if "nova" in self.model_id.lower():
                # Use optimized Nova Pro prompts
                prompt = NovaProPrompts.get_optimized_prompt(question, account_id)
                
                # Add examples for better context
                if context_docs and len(context_docs) > 0:
                    prompt += PromptExamples.get_examples_for_context(question, account_id, limit=2)
            else:
                # Claude or other models
                prompt = f"""You are an expert SQL developer for Amazon Redshift.
            
DATABASE CONTEXT:
{enhanced_context}

CRITICAL SECURITY RULES - MUST FOLLOW:
1. ONLY generate SELECT queries - NEVER CREATE, DROP, ALTER, DELETE, UPDATE, INSERT, or any modification operations
2. ALWAYS use fully qualified table names: wbx_data.webconnex.table_name
3. ALWAYS include "account_id = {account_id}" in WHERE clause for security
4. Add LIMIT clause (default 1000 unless user specifies otherwise)
5. For dates use 'YYYY-MM-DD' format or date functions like CURRENT_DATE
6. Check for soft deletes with "date_deleted IS NULL" where applicable

USER QUESTION: {question}

Generate ONLY a READ-ONLY SELECT SQL query. Output only the SQL, no explanations:"""
            
            # Call Bedrock model (Claude or Nova)
            if "claude" in self.model_id.lower():
                # Claude format
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "anthropic_version": "bedrock-2023-05-31",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": self.max_tokens,
                        "temperature": 0.1
                    })
                )
            else:
                # Nova format - Use the working format with inferenceConfig
                response = self.bedrock_client.invoke_model(
                    modelId=self.model_id,
                    body=json.dumps({
                        "messages": [{
                            "role": "user",
                            "content": [{"text": prompt}]
                        }],
                        "inferenceConfig": {
                            "maxTokens": self.max_tokens,
                            "temperature": 0.1
                        }
                    })
                )
            
            # Parse response based on model type
            response_body = json.loads(response['body'].read())
            
            # Extract SQL based on response format
            if "nova" in self.model_id.lower() and 'output' in response_body:
                # Nova returns in output.message.content[0].text
                output = response_body['output']
                if isinstance(output, dict) and 'message' in output:
                    sql_query = output['message']['content'][0]['text'].strip()
                else:
                    sql_query = str(output).strip()
            elif 'content' in response_body:
                # Claude format
                sql_query = response_body['content'][0]['text'].strip()
            else:
                # Fallback for different response formats
                sql_query = str(response_body.get('completion', response_body)).strip()
            
            # Clean SQL (remove markdown if present)
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            # CRITICAL: Validate SQL is read-only
            self._validate_sql_readonly(sql_query)
            
            # Ensure we're using the correct schema
            if 'webconnex.' not in sql_query.lower():
                # Replace table names with fully qualified names
                for table in ['account', 'invoice', 'customer', 'registration', 'form']:
                    sql_query = sql_query.replace(f' {table}', f' wbx_data.webconnex.{table}')
                    sql_query = sql_query.replace(f'FROM {table}', f'FROM wbx_data.webconnex.{table}')
                    sql_query = sql_query.replace(f'JOIN {table}', f'JOIN wbx_data.webconnex.{table}')
            
            # Validate SQL contains account_id filter
            if f"account_id = {account_id}" not in sql_query.lower():
                logger.warning(f"Generated SQL missing account_id filter, adding it")
                # Try to add account_id filter
                if "WHERE" in sql_query.upper():
                    sql_query = sql_query.replace(
                        "WHERE", 
                        f"WHERE account_id = {account_id} AND", 
                        1  # Replace only first occurrence
                    )
                else:
                    # Add WHERE clause before ORDER BY, GROUP BY, or LIMIT
                    for keyword in ["ORDER BY", "GROUP BY", "LIMIT"]:
                        if keyword in sql_query.upper():
                            idx = sql_query.upper().find(keyword)
                            sql_query = sql_query[:idx] + f"WHERE account_id = {account_id} " + sql_query[idx:]
                            break
                    else:
                        sql_query += f" WHERE account_id = {account_id}"
            
            # Add LIMIT if not present
            if "LIMIT" not in sql_query.upper():
                sql_query += " LIMIT 1000"
            
            logger.info(f"Generated SQL for account {account_id}: {sql_query[:100]}...")
            
            return sql_query
            
        except Exception as e:
            logger.error(f"Error generating SQL: {e}")
            raise
    
    def execute_sql(self, sql: str, account_id: int) -> pd.DataFrame:
        """
        Execute SQL query with account context
        
        Args:
            sql: SQL query to execute
            account_id: Account ID for context
            
        Returns:
            Query results as DataFrame
        """
        try:
            # Add RLS context setting
            context_sql = f"""
            -- Set account context for Row-Level Security
            SELECT set_account_context({account_id});
            
            -- Set read-only mode for safety
            SET transaction_read_only = on;
            SET statement_timeout = '{settings.QUERY_TIMEOUT_SECONDS}s';
            
            -- User query
            {sql}
            """
            
            # Execute via Redshift Data API
            statement_id = aws_auth.execute_redshift_query(
                context_sql,
                with_event=True
            )
            
            # Get results
            results = aws_auth.get_query_results(statement_id)
            
            # Convert to DataFrame
            df = pd.DataFrame(results['rows'])
            
            # Limit results if needed
            if len(df) > settings.MAX_QUERY_RESULTS:
                logger.warning(f"Truncating results from {len(df)} to {settings.MAX_QUERY_RESULTS}")
                df = df.head(settings.MAX_QUERY_RESULTS)
            
            return df
            
        except Exception as e:
            logger.error(f"Error executing SQL: {e}")
            raise
    
    def train(
        self,
        question: Optional[str] = None,
        sql: Optional[str] = None,
        ddl: Optional[str] = None,
        documentation: Optional[str] = None
    ):
        """
        Add training data to improve SQL generation
        
        Args:
            question: Natural language question
            sql: Corresponding SQL query
            ddl: DDL statements
            documentation: Additional documentation
        """
        try:
            if question and sql:
                # Store question-SQL pair in vector store
                self.vector_store.add_training_pair(
                    question=question,
                    sql=sql,
                    metadata={
                        'type': 'training',
                        'validated': True
                    }
                )
                logger.info(f"Added training pair: {question[:50]}...")
            
            if ddl:
                # Store DDL for schema understanding
                self.vector_store.add_document(
                    content=ddl,
                    doc_type='ddl',
                    metadata={'type': 'schema'}
                )
                logger.info("Added DDL to training data")
            
            if documentation:
                # Store documentation
                self.vector_store.add_document(
                    content=documentation,
                    doc_type='documentation',
                    metadata={'type': 'docs'}
                )
                logger.info("Added documentation to training data")
                
        except Exception as e:
            logger.error(f"Error adding training data: {e}")
            raise
    
    def get_training_data(self) -> List[Dict]:
        """
        Retrieve all training data
        
        Returns:
            List of training examples
        """
        try:
            return self.vector_store.get_all_training_data()
        except Exception as e:
            logger.error(f"Error retrieving training data: {e}")
            raise
    
    def remove_training_data(self, id: str):
        """
        Remove specific training data
        
        Args:
            id: Training data ID
        """
        try:
            self.vector_store.delete_document(id)
            logger.info(f"Removed training data: {id}")
        except Exception as e:
            logger.error(f"Error removing training data: {e}")
            raise
    
    def generate_plotly_code(
        self,
        question: str,
        sql: str,
        df: pd.DataFrame
    ) -> str:
        """
        Generate Plotly visualization code
        
        Args:
            question: Original question
            sql: Generated SQL
            df: Result DataFrame
            
        Returns:
            Plotly code as string
        """
        try:
            # Analyze data structure
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
            text_cols = df.select_dtypes(include=['object']).columns.tolist()
            
            prompt = f"""Generate Plotly Python code to visualize this data.
            
Question: {question}
SQL: {sql}
Data shape: {df.shape}
Numeric columns: {numeric_cols}
Date columns: {date_cols}
Text columns: {text_cols}
First 5 rows: {df.head().to_dict()}

Generate appropriate Plotly visualization code:"""
            
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": 1000,
                    "temperature": 0.1,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                })
            )
            
            response_body = json.loads(response['body'].read())
            plotly_code = response_body['content'][0]['text'].strip()
            
            return plotly_code
            
        except Exception as e:
            logger.error(f"Error generating Plotly code: {e}")
            # Return a default plot
            return """
import plotly.express as px
fig = px.bar(df, title="Query Results")
fig.show()
"""
    
    # Implement required abstract methods from VannaBase
    def add_ddl(self, ddl: str):
        """Add DDL to training data"""
        self.train(ddl=ddl)
    
    def add_documentation(self, doc: str):
        """Add documentation to training data"""
        self.train(documentation=doc)
    
    def add_question_sql(self, question: str, sql: str):
        """Add question-SQL pair to training data"""
        self.train(question=question, sql=sql)
    
    def generate_embedding(self, text: str):
        """Generate embedding for text using Titan"""
        return self.vector_store._generate_embedding(text)
    
    def get_related_ddl(self, question: str, n: int = 5):
        """Get related DDL for a question"""
        docs = self.vector_store.search(question, top_k=n, doc_types=['ddl'])
        return [doc.get('content', '') for doc in docs]
    
    def get_related_documentation(self, question: str, n: int = 5):
        """Get related documentation for a question"""
        docs = self.vector_store.search(question, top_k=n, doc_types=['documentation'])
        return [doc.get('content', '') for doc in docs]
    
    def get_similar_question_sql(self, question: str, n: int = 5):
        """Get similar question-SQL pairs"""
        docs = self.vector_store.search(question, top_k=n, doc_types=['training'])
        return [(doc.get('question', ''), doc.get('sql', '')) for doc in docs]
    
    def submit_prompt(self, prompt: str):
        """Submit prompt to LLM"""
        if "claude" in self.model_id.lower():
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "anthropic_version": "bedrock-2023-05-31",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.max_tokens,
                    "temperature": 0.1
                })
            )
        else:
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": self.max_tokens,
                    "temperature": 0.1
                })
            )
        
        response_body = json.loads(response['body'].read())
        if 'content' in response_body:
            return response_body['content'][0]['text']
        return str(response_body)
    
    def system_message(self, message: str):
        """Return system message format"""
        return {"role": "system", "content": message}
    
    def user_message(self, message: str):
        """Return user message format"""
        return {"role": "user", "content": message}
    
    def assistant_message(self, message: str):
        """Return assistant message format"""
        return {"role": "assistant", "content": message}