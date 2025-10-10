# 🐳 Docker Deployment Guide - Webconnex AI Text-to-SQL

Complete guide for running the Webconnex AI Text-to-SQL system with Docker.

## 📋 Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ ([Install Compose](https://docs.docker.com/compose/install/))
- AWS CLI configured with credentials
- `gimme-aws-creds` for Okta authentication

---

## 🚀 Quick Start (5 minutes)

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd wbx-text-to-sql-rag

# Copy environment template
cp .env.template .env

# Edit .env with your values (or use defaults)
nano .env
```

### 2. Configure AWS Credentials

```bash
# Authenticate with new account
export AWS_PROFILE=049101138630-okta-admin-user
gimme-aws-creds --profile 049101138630-okta-admin-user

# Verify credentials
aws sts get-caller-identity --profile 049101138630-okta-admin-user
```

### 3. Setup AWS Resources

```bash
# Create S3 buckets and verify Bedrock access
chmod +x scripts/setup-aws.sh
./scripts/setup-aws.sh
```

### 4. Launch with Docker Compose

```bash
# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f
```

### 5. Access the Application

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis**: localhost:6379

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Docker Network                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Frontend   │  │   Backend    │  │   Redis   │ │
│  │  (Streamlit) │→ │   (FastAPI)  │→ │  (Cache)  │ │
│  │  Port: 8501  │  │  Port: 8000  │  │Port: 6379 │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
│         ↓                  ↓                         │
└─────────────────────────────────────────────────────┘
              ↓                  ↓
    ┌──────────────────┐  ┌─────────────┐
    │   AWS Bedrock    │  │  Redshift   │
    │  (Nova Pro)      │  │  (wbx_data) │
    └──────────────────┘  └─────────────┘
              ↓
    ┌──────────────────┐
    │   S3 Vectors     │
    │   (Embeddings)   │
    └──────────────────┘
```

---

## 📝 Docker Commands Reference

### Basic Operations

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Check service status
docker-compose ps

# Execute command in container
docker-compose exec backend bash
```

### Build Commands

```bash
# Build images
docker-compose build

# Build without cache
docker-compose build --no-cache

# Build specific service
docker-compose build backend
```

### Troubleshooting

```bash
# View resource usage
docker stats

# Inspect container
docker-compose exec backend env

# Clean everything
docker-compose down -v
docker system prune -a
```

---

## 🔧 Configuration

### Environment Variables

All configuration is done via `.env` file. Key variables:

```bash
# AWS Account (New)
AWS_ACCOUNT_ID=049101138630
AWS_PROFILE=049101138630-okta-admin-user

# S3 Buckets (New)
S3_BUCKET_VECTORS=webconnex-ai-dev-vectors
S3_BUCKET_TRAINING=webconnex-ai-dev-training

# Bedrock Models
BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0
BEDROCK_MODEL_ID_EMBEDDINGS=amazon.titan-embed-text-v1
```

### Volume Mounts

```yaml
volumes:
  - ./backend:/app/backend:ro     # Backend code (read-only)
  - ./logs:/app/logs               # Persistent logs
  - ~/.aws:/home/appuser/.aws:ro   # AWS credentials
```

---

## 🚢 Production Deployment

### Option 1: Deploy to AWS ECR + ECS

```bash
# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

This will:
1. ✅ Build Docker images
2. ✅ Push to AWS ECR
3. ✅ Create ECR repositories if needed
4. ⚠️ Manual: Update ECS task definitions

### Option 2: Manual ECR Push

```bash
# Login to ECR
aws ecr get-login-password --region us-west-2 --profile 049101138630-okta-admin-user | \
  docker login --username AWS --password-stdin \
  049101138630.dkr.ecr.us-west-2.amazonaws.com

# Build and tag
docker build -f backend/Dockerfile -t webconnex-ai-backend:latest .
docker tag webconnex-ai-backend:latest \
  049101138630.dkr.ecr.us-west-2.amazonaws.com/webconnex-ai-backend:latest

# Push
docker push 049101138630.dkr.ecr.us-west-2.amazonaws.com/webconnex-ai-backend:latest
```

---

## 🔍 Monitoring & Debugging

### Health Checks

All services have health checks:

```bash
# Check backend health
curl http://localhost:8000/api/health

# Check frontend health
curl http://localhost:8501/_stcore/health

# Check Redis
docker-compose exec redis redis-cli ping
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service with timestamps
docker-compose logs -f --timestamps backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Performance Monitoring

```bash
# Container stats
docker stats webconnex-ai-backend webconnex-ai-frontend webconnex-ai-redis

# Resource limits (from docker-compose.yml)
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '2'
```

---

## 🔒 Security Best Practices

### 1. Never Commit Credentials

```bash
# .env files are in .gitignore
# Always use .env.template as reference
```

### 2. Use IAM Roles in Production

```yaml
# In ECS, use task roles instead of mounted credentials
task_role_arn: arn:aws:iam::049101138630:role/WebconnexAI-Task-Role
```

### 3. Enable Security Scanning

```bash
# Scan images for vulnerabilities
docker scan webconnex-ai-backend:latest

# ECR auto-scanning (enabled in deploy.sh)
--image-scanning-configuration scanOnPush=true
```

---

## 🛠️ Troubleshooting Guide

### Issue: Container won't start

```bash
# Check logs
docker-compose logs backend

# Common fixes:
1. Verify .env file exists
2. Check AWS credentials: aws sts get-caller-identity
3. Ensure ports 8000, 8501, 6379 are free
```

### Issue: AWS connection errors

```bash
# Refresh credentials
gimme-aws-creds --profile 049101138630-okta-admin-user

# Verify inside container
docker-compose exec backend env | grep AWS
```

### Issue: Bedrock access denied

```bash
# Verify Bedrock access
aws bedrock list-foundation-models --region us-west-2

# Request model access in AWS Console
# Navigate to: Bedrock → Model access → Request access
```

### Issue: S3 bucket not found

```bash
# Run setup script
./scripts/setup-aws.sh

# Or create manually
aws s3 mb s3://webconnex-ai-dev-vectors --region us-west-2
```

---

## 📊 Performance Tuning

### Memory Optimization

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G
```

### Redis Caching

```bash
# Check cache hit rate
docker-compose exec redis redis-cli INFO stats | grep hit

# Clear cache if needed
docker-compose exec redis redis-cli FLUSHALL
```

### Container Resource Limits

```bash
# Monitor resource usage
docker stats

# Adjust limits in docker-compose.yml if needed
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Migrations

```bash
# Run migrations (if applicable)
docker-compose exec backend python -m scripts.migrate_data
```

### Backup Data

```bash
# Backup Redis data
docker-compose exec redis redis-cli SAVE
docker cp webconnex-ai-redis:/data/dump.rdb ./backups/

# Backup S3 (using AWS CLI)
aws s3 sync s3://webconnex-ai-dev-vectors ./backups/vectors/
```

---

## 📞 Support & Resources

- **Documentation**: [README.md](./README.md)
- **Agent Guide**: [CLAUDE.md](./CLAUDE.md)
- **AWS Account**: webconnex-ai-dev (049101138630)
- **Issues**: Create GitHub issue or contact DevOps team

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] AWS credentials configured for new account (049101138630)
- [ ] S3 buckets created and accessible
- [ ] Bedrock models (Nova Pro + Titan Embeddings) enabled
- [ ] Redshift cluster accessible
- [ ] Environment variables set in `.env.production`
- [ ] Health checks passing for all services
- [ ] Security scanning completed
- [ ] Monitoring and logging configured
- [ ] Backup strategy in place
- [ ] Load testing completed

---

**Last Updated**: 2025-01-14
**Docker Version**: 20.10+
**Compose Version**: 2.0+
