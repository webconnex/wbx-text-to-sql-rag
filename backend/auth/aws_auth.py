"""
AWS Authentication using gimme-aws-creds
Follows existing Webconnex patterns
"""

import os
import boto3
import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class AWSAuth:
    """
    AWS authentication manager using gimme-aws-creds pattern
    """
    
    def __init__(self):
        """Initialize AWS authentication"""
        self.account_id = settings.AWS_ACCOUNT_ID
        self.account_name = settings.AWS_PROFILE
        self.region = settings.AWS_REGION
        self.rs_secret = settings.REDSHIFT_SECRET_ARN
        
        # Set environment for local development
        if settings.RUN_LOCALLY:
            os.environ["RUN_LOCALLY"] = "1"
            logger.info("Running in local mode with gimme-aws-creds")
    
    @lru_cache(maxsize=1)
    def get_session(self) -> boto3.Session:
        """
        Get AWS session using gimme-aws-creds credentials
        
        Returns:
            boto3.Session: AWS session
        """
        try:
            # Use profile if specified
            if settings.AWS_PROFILE:
                session = boto3.Session(
                    profile_name=settings.AWS_PROFILE,
                    region_name=self.region
                )
                logger.info(f"Created AWS session with profile: {settings.AWS_PROFILE}")
            else:
                # Use default credentials
                session = boto3.Session(region_name=self.region)
                logger.info("Created AWS session with default credentials")
            
            # Verify credentials
            sts = session.client('sts')
            identity = sts.get_caller_identity()
            logger.info(f"AWS Identity: {identity['Arn']}")
            
            return session
            
        except Exception as e:
            logger.error(f"Failed to create AWS session: {e}")
            raise
    
    def get_redshift_client(self, session: Optional[boto3.Session] = None):
        """
        Get Redshift Data API client
        
        Args:
            session: Optional boto3 session
            
        Returns:
            Redshift Data API client
        """
        if not session:
            session = self.get_session()
        
        client = session.client(
            'redshift-data',
            region_name=self.region
        )
        
        return client
    
    def get_bedrock_client(self, session: Optional[boto3.Session] = None):
        """
        Get Bedrock Runtime client
        
        Args:
            session: Optional boto3 session
            
        Returns:
            Bedrock Runtime client
        """
        if not session:
            session = self.get_session()
        
        client = session.client(
            'bedrock-runtime',
            region_name=settings.BEDROCK_REGION
        )
        
        return client
    
    def get_s3_client(self, session: Optional[boto3.Session] = None):
        """
        Get S3 client
        
        Args:
            session: Optional boto3 session
            
        Returns:
            S3 client
        """
        if not session:
            session = self.get_session()
        
        client = session.client(
            's3',
            region_name=settings.S3_REGION
        )
        
        return client
    
    def get_secrets_manager_client(self, session: Optional[boto3.Session] = None):
        """
        Get Secrets Manager client
        
        Args:
            session: Optional boto3 session
            
        Returns:
            Secrets Manager client
        """
        if not session:
            session = self.get_session()
        
        client = session.client(
            'secretsmanager',
            region_name=self.region
        )
        
        return client
    
    def get_redshift_credentials(self) -> Dict[str, Any]:
        """
        Get Redshift credentials from Secrets Manager
        
        Returns:
            Dict containing database credentials
        """
        try:
            secrets_client = self.get_secrets_manager_client()
            
            response = secrets_client.get_secret_value(
                SecretId=self.rs_secret
            )
            
            import json
            secret = json.loads(response['SecretString'])
            
            return {
                'username': secret.get('username'),
                'password': secret.get('password'),
                'host': secret.get('host'),
                'port': secret.get('port', 5439),
                'database': settings.REDSHIFT_DATABASE
            }
            
        except Exception as e:
            logger.error(f"Failed to get Redshift credentials: {e}")
            raise
    
    def execute_redshift_query(
        self,
        sql: str,
        database: Optional[str] = None,
        with_event: bool = True
    ) -> str:
        """
        Execute query using Redshift Data API
        
        Args:
            sql: SQL query to execute
            database: Database name (optional)
            with_event: Wait for query completion
            
        Returns:
            Query execution ID
        """
        try:
            client = self.get_redshift_client()
            
            # Execute statement
            response = client.execute_statement(
                ClusterIdentifier=settings.REDSHIFT_CLUSTER_ID,
                Database=database or settings.REDSHIFT_DATABASE,
                Sql=sql,
                SecretArn=self.rs_secret,
                WithEvent=with_event
            )
            
            statement_id = response['Id']
            logger.info(f"Executed Redshift query: {statement_id}")
            
            if with_event:
                # Wait for completion
                waiter = client.get_waiter('statement_finished')
                waiter.wait(
                    Id=statement_id,
                    WaiterConfig={
                        'Delay': 1,
                        'MaxAttempts': settings.QUERY_TIMEOUT_SECONDS
                    }
                )
            
            return statement_id
            
        except Exception as e:
            logger.error(f"Failed to execute Redshift query: {e}")
            raise
    
    def get_query_results(self, statement_id: str) -> Dict[str, Any]:
        """
        Get results from executed query
        
        Args:
            statement_id: Query execution ID
            
        Returns:
            Query results
        """
        try:
            client = self.get_redshift_client()
            
            # Get statement result
            response = client.get_statement_result(Id=statement_id)
            
            # Process results
            columns = [col['label'] for col in response['ColumnMetadata']]
            rows = []
            
            for record in response.get('Records', []):
                row = {}
                for i, col in enumerate(columns):
                    if 'isNull' in record[i] and record[i]['isNull']:
                        row[col] = None
                    else:
                        # Get the actual value based on data type
                        for key in ['stringValue', 'longValue', 'doubleValue', 'booleanValue']:
                            if key in record[i]:
                                row[col] = record[i][key]
                                break
                rows.append(row)
            
            return {
                'columns': columns,
                'rows': rows,
                'row_count': len(rows),
                'statement_id': statement_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get query results: {e}")
            raise


# Create singleton instance
aws_auth = AWSAuth()