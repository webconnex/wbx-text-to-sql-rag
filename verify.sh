#!/bin/bash

# 🔍 Webconnex AI Text-to-SQL System Verification Script
# This script verifies that the entire Docker stack is running correctly

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║   🔍 Webconnex AI Text-to-SQL Verification Script       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is running
echo -e "${BLUE}1️⃣ Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Check if containers are running
echo -e "${BLUE}2️⃣ Checking containers...${NC}"
CONTAINERS=$(docker compose ps --format json 2>/dev/null || echo "[]")

if [ -z "$CONTAINERS" ] || [ "$CONTAINERS" = "[]" ]; then
    echo -e "${YELLOW}⚠️  No containers are running${NC}"
    echo -e "${YELLOW}   Run: docker compose up -d${NC}"
    exit 1
fi

# Parse and check each container
BACKEND_STATUS=$(docker compose ps backend --format json 2>/dev/null | jq -r '.Health // "unknown"' 2>/dev/null || echo "not_running")
FRONTEND_STATUS=$(docker compose ps frontend --format json 2>/dev/null | jq -r '.Health // "unknown"' 2>/dev/null || echo "not_running")
REDIS_STATUS=$(docker compose ps redis --format json 2>/dev/null | jq -r '.Health // "unknown"' 2>/dev/null || echo "not_running")

# Check backend
if [ "$BACKEND_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ Backend container: healthy${NC}"
elif [ "$BACKEND_STATUS" = "not_running" ]; then
    echo -e "${RED}❌ Backend container: not running${NC}"
else
    echo -e "${YELLOW}⚠️  Backend container: $BACKEND_STATUS${NC}"
fi

# Check frontend
if [ "$FRONTEND_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ Frontend container: healthy${NC}"
elif [ "$FRONTEND_STATUS" = "not_running" ]; then
    echo -e "${RED}❌ Frontend container: not running${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend container: $FRONTEND_STATUS${NC}"
fi

# Check redis
if [ "$REDIS_STATUS" = "healthy" ]; then
    echo -e "${GREEN}✅ Redis container: healthy${NC}"
elif [ "$REDIS_STATUS" = "not_running" ]; then
    echo -e "${RED}❌ Redis container: not running${NC}"
else
    echo -e "${YELLOW}⚠️  Redis container: $REDIS_STATUS${NC}"
fi
echo ""

# Check backend health endpoint
echo -e "${BLUE}3️⃣ Checking backend API...${NC}"
BACKEND_HEALTH=$(curl -s http://localhost:8000/api/health 2>/dev/null || echo "failed")
if [ "$BACKEND_HEALTH" = '{"status":"healthy"}' ] || [ "$BACKEND_HEALTH" = "ok" ] || [ ! -z "$BACKEND_HEALTH" ]; then
    echo -e "${GREEN}✅ Backend API responding at http://localhost:8000${NC}"
else
    echo -e "${RED}❌ Backend API not responding${NC}"
fi
echo ""

# Check frontend health endpoint
echo -e "${BLUE}4️⃣ Checking frontend UI...${NC}"
FRONTEND_HEALTH=$(curl -s http://localhost:8501/_stcore/health 2>/dev/null || echo "failed")
if [ "$FRONTEND_HEALTH" = "ok" ]; then
    echo -e "${GREEN}✅ Frontend UI responding at http://localhost:8501${NC}"
else
    echo -e "${RED}❌ Frontend UI not responding${NC}"
fi
echo ""

# Check AWS credentials
echo -e "${BLUE}5️⃣ Checking AWS credentials...${NC}"
if docker compose exec -T backend aws sts get-caller-identity > /dev/null 2>&1; then
    AWS_ACCOUNT=$(docker compose exec -T backend aws sts get-caller-identity 2>/dev/null | grep -o '"Account": "[^"]*"' | cut -d'"' -f4 || echo "unknown")
    if [ "$AWS_ACCOUNT" = "049101138630" ]; then
        echo -e "${GREEN}✅ AWS credentials valid (Account: $AWS_ACCOUNT)${NC}"
    else
        echo -e "${YELLOW}⚠️  AWS credentials valid but unexpected account: $AWS_ACCOUNT${NC}"
    fi
else
    echo -e "${RED}❌ AWS credentials not configured or expired${NC}"
    echo -e "${YELLOW}   Run: gimme-aws-creds --profile 049101138630-okta-admin-user${NC}"
fi
echo ""

# Check Bedrock access
echo -e "${BLUE}6️⃣ Checking Bedrock access...${NC}"
if docker compose exec -T backend python3 -c "
import sys
sys.path.insert(0, '/app')
from backend.config.settings import settings
from backend.auth.aws_auth import aws_auth
try:
    bedrock = aws_auth.get_bedrock_client()
    print('✅ Bedrock client initialized')
except Exception as e:
    print(f'❌ Bedrock error: {str(e)}')
    sys.exit(1)
" 2>/dev/null; then
    echo -e "${GREEN}✅ Amazon Bedrock accessible${NC}"
else
    echo -e "${RED}❌ Amazon Bedrock not accessible${NC}"
fi
echo ""

# Check S3 access
echo -e "${BLUE}7️⃣ Checking S3 buckets...${NC}"
if docker compose exec -T backend aws s3 ls s3://webconnex-ai-dev-vectors > /dev/null 2>&1; then
    echo -e "${GREEN}✅ S3 vectors bucket accessible${NC}"
else
    echo -e "${RED}❌ S3 vectors bucket not accessible${NC}"
fi

if docker compose exec -T backend aws s3 ls s3://webconnex-ai-dev-training > /dev/null 2>&1; then
    echo -e "${GREEN}✅ S3 training bucket accessible${NC}"
else
    echo -e "${RED}❌ S3 training bucket not accessible${NC}"
fi
echo ""

# Final summary
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                 Verification Summary                     ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo -e "${BLUE}Access Points:${NC}"
echo -e "  🌐 Frontend UI:  ${GREEN}http://localhost:8501${NC}"
echo -e "  🔧 Backend API:  ${GREEN}http://localhost:8000${NC}"
echo -e "  📚 API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
echo ""

# Check if all critical checks passed
CRITICAL_CHECKS_PASSED=true

if [ "$BACKEND_STATUS" != "healthy" ]; then CRITICAL_CHECKS_PASSED=false; fi
if [ "$FRONTEND_STATUS" != "healthy" ]; then CRITICAL_CHECKS_PASSED=false; fi
if [ "$REDIS_STATUS" != "healthy" ]; then CRITICAL_CHECKS_PASSED=false; fi

if [ "$CRITICAL_CHECKS_PASSED" = true ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          ✅ All checks passed! System ready.             ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║      ❌ Some checks failed. See details above.           ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo -e "  1. Check logs: ${BLUE}docker compose logs -f${NC}"
    echo -e "  2. Restart services: ${BLUE}docker compose restart${NC}"
    echo -e "  3. Rebuild: ${BLUE}docker compose build && docker compose up -d${NC}"
    exit 1
fi
