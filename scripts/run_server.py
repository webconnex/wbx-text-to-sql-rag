#!/usr/bin/env python3
"""
Run the Webconnex Text-to-SQL API Server
Simple script to start the FastAPI server
"""

import os
import sys
import uvicorn
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def main():
    """Start the FastAPI server"""
    print("=" * 60)
    print("Starting Webconnex Text-to-SQL API Server")
    print("=" * 60)
    
    # Environment info
    print("\n📋 Configuration:")
    print(f"  Host: {os.getenv('API_HOST', '0.0.0.0')}")
    print(f"  Port: {os.getenv('API_PORT', '8000')}")
    print(f"  Workers: {os.getenv('API_WORKERS', '1')}")
    print(f"  Reload: {os.getenv('API_RELOAD', 'true')}")
    print(f"  Environment: {os.getenv('ENVIRONMENT', 'development')}")
    
    print("\n🔧 AWS Configuration:")
    print(f"  Profile: {os.getenv('AWS_PROFILE', 'Not set')}")
    print(f"  Region: {os.getenv('AWS_REGION', 'Not set')}")
    print(f"  Nova Pro: {os.getenv('BEDROCK_MODEL_ID', 'Not set')}")
    print(f"  Titan Embeddings: {os.getenv('BEDROCK_MODEL_ID_EMBEDDINGS', 'Not set')}")
    
    print("\n🗄️ Database Configuration:")
    print(f"  Cluster: {os.getenv('REDSHIFT_CLUSTER_ID', 'Not set')}")
    print(f"  Database: {os.getenv('REDSHIFT_DATABASE', 'Not set')}")
    print(f"  Schema: wbx_data.webconnex")
    
    print("\n" + "=" * 60)
    print("Starting server...")
    print("=" * 60)
    
    print("\n📌 API Endpoints:")
    print("  - Documentation: http://localhost:8000/docs")
    print("  - Health Check: http://localhost:8000/api/health")
    print("  - Query Endpoint: POST http://localhost:8000/api/query")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start the server
    uvicorn.run(
        "backend.main:app",
        host=os.getenv('API_HOST', '0.0.0.0'),
        port=int(os.getenv('API_PORT', '8000')),
        reload=os.getenv('API_RELOAD', 'true').lower() == 'true',
        log_level=os.getenv('API_LOG_LEVEL', 'info').lower(),
        workers=1 if os.getenv('API_RELOAD', 'true').lower() == 'true' else int(os.getenv('API_WORKERS', '1'))
    )


if __name__ == "__main__":
    main()