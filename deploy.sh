#!/bin/bash

# ==================================================
# Webconnex AI Text-to-SQL - Production Deployment Script
# ==================================================
# Deploys the dockerized application to AWS
# Account: webconnex-ai-dev (049101138630)
# ==================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AWS_REGION="${AWS_REGION:-us-west-2}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-049101138630}"
AWS_PROFILE="${AWS_PROFILE:-049101138630-okta-admin-user}"
ECR_REPOSITORY_BACKEND="webconnex-ai-backend"
ECR_REPOSITORY_FRONTEND="webconnex-ai-frontend"
DEPLOYMENT_ENV="${DEPLOYMENT_ENV:-production}"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     🚀 WEBCONNEX AI TEXT-TO-SQL DEPLOYMENT SCRIPT       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    print_status "AWS CLI found"

    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install it first."
        exit 1
    fi
    print_status "Docker found"

    # Check docker-compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed. Please install it first."
        exit 1
    fi
    print_status "docker-compose found"

    # Check jq (optional but recommended)
    if ! command -v jq &> /dev/null; then
        print_warning "jq is not installed. Some features may not work."
    fi

    echo ""
}

# Verify AWS credentials
verify_aws_credentials() {
    print_info "Verifying AWS credentials..."

    export AWS_PROFILE=$AWS_PROFILE

    if ! aws sts get-caller-identity --profile $AWS_PROFILE > /dev/null 2>&1; then
        print_error "AWS credentials are invalid or expired."
        print_info "Please run: gimme-aws-creds --profile $AWS_PROFILE"
        exit 1
    fi

    ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text)

    if [ "$ACCOUNT_ID" != "$AWS_ACCOUNT_ID" ]; then
        print_warning "Account ID mismatch. Expected: $AWS_ACCOUNT_ID, Got: $ACCOUNT_ID"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi

    print_status "AWS credentials verified for account: $ACCOUNT_ID"
    echo ""
}

# Create ECR repositories if they don't exist
create_ecr_repositories() {
    print_info "Checking ECR repositories..."

    # Backend repository
    if ! aws ecr describe-repositories \
        --repository-names $ECR_REPOSITORY_BACKEND \
        --region $AWS_REGION \
        --profile $AWS_PROFILE > /dev/null 2>&1; then

        print_info "Creating ECR repository: $ECR_REPOSITORY_BACKEND"
        aws ecr create-repository \
            --repository-name $ECR_REPOSITORY_BACKEND \
            --region $AWS_REGION \
            --profile $AWS_PROFILE \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
        print_status "Backend ECR repository created"
    else
        print_status "Backend ECR repository exists"
    fi

    # Frontend repository
    if ! aws ecr describe-repositories \
        --repository-names $ECR_REPOSITORY_FRONTEND \
        --region $AWS_REGION \
        --profile $AWS_PROFILE > /dev/null 2>&1; then

        print_info "Creating ECR repository: $ECR_REPOSITORY_FRONTEND"
        aws ecr create-repository \
            --repository-name $ECR_REPOSITORY_FRONTEND \
            --region $AWS_REGION \
            --profile $AWS_PROFILE \
            --image-scanning-configuration scanOnPush=true \
            --encryption-configuration encryptionType=AES256
        print_status "Frontend ECR repository created"
    else
        print_status "Frontend ECR repository exists"
    fi

    echo ""
}

# Login to ECR
ecr_login() {
    print_info "Logging in to ECR..."

    aws ecr get-login-password \
        --region $AWS_REGION \
        --profile $AWS_PROFILE | \
        docker login \
            --username AWS \
            --password-stdin \
            ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

    print_status "ECR login successful"
    echo ""
}

# Build Docker images
build_images() {
    print_info "Building Docker images..."

    # Build backend
    print_info "Building backend image..."
    docker build \
        -f backend/Dockerfile \
        -t $ECR_REPOSITORY_BACKEND:latest \
        -t $ECR_REPOSITORY_BACKEND:$(date +%Y%m%d-%H%M%S) \
        --build-arg AWS_REGION=$AWS_REGION \
        --build-arg AWS_ACCOUNT_ID=$AWS_ACCOUNT_ID \
        .
    print_status "Backend image built"

    # Build frontend
    print_info "Building frontend image..."
    docker build \
        -f frontend/Dockerfile \
        -t $ECR_REPOSITORY_FRONTEND:latest \
        -t $ECR_REPOSITORY_FRONTEND:$(date +%Y%m%d-%H%M%S) \
        .
    print_status "Frontend image built"

    echo ""
}

# Tag and push images to ECR
push_images() {
    print_info "Pushing images to ECR..."

    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    ECR_URL="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

    # Tag and push backend
    print_info "Pushing backend image..."
    docker tag $ECR_REPOSITORY_BACKEND:latest $ECR_URL/$ECR_REPOSITORY_BACKEND:latest
    docker tag $ECR_REPOSITORY_BACKEND:latest $ECR_URL/$ECR_REPOSITORY_BACKEND:$TIMESTAMP
    docker push $ECR_URL/$ECR_REPOSITORY_BACKEND:latest
    docker push $ECR_URL/$ECR_REPOSITORY_BACKEND:$TIMESTAMP
    print_status "Backend image pushed"

    # Tag and push frontend
    print_info "Pushing frontend image..."
    docker tag $ECR_REPOSITORY_FRONTEND:latest $ECR_URL/$ECR_REPOSITORY_FRONTEND:latest
    docker tag $ECR_REPOSITORY_FRONTEND:latest $ECR_URL/$ECR_REPOSITORY_FRONTEND:$TIMESTAMP
    docker push $ECR_URL/$ECR_REPOSITORY_FRONTEND:latest
    docker push $ECR_URL/$ECR_REPOSITORY_FRONTEND:$TIMESTAMP
    print_status "Frontend image pushed"

    echo ""
    print_status "Images pushed with tags:"
    echo "  • latest"
    echo "  • $TIMESTAMP"
    echo ""
}

# Deploy to ECS (placeholder - customize based on your infrastructure)
deploy_to_ecs() {
    print_info "Deploying to ECS..."
    print_warning "ECS deployment not yet implemented. Manual deployment required."
    print_info "Images are available in ECR at:"
    echo "  • ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$ECR_REPOSITORY_BACKEND:latest"
    echo "  • ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/$ECR_REPOSITORY_FRONTEND:latest"
    echo ""
}

# Run smoke tests
run_smoke_tests() {
    print_info "Running smoke tests..."
    print_warning "Smoke tests not yet implemented."
    echo ""
}

# Main deployment flow
main() {
    print_info "Starting deployment for environment: $DEPLOYMENT_ENV"
    echo ""

    check_prerequisites
    verify_aws_credentials
    create_ecr_repositories
    ecr_login
    build_images
    push_images
    deploy_to_ecs
    run_smoke_tests

    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            ✅ DEPLOYMENT COMPLETED SUCCESSFULLY          ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_info "Next steps:"
    echo "  1. Update ECS task definitions with new image tags"
    echo "  2. Deploy to ECS using AWS Console or CLI"
    echo "  3. Run integration tests"
    echo "  4. Monitor CloudWatch logs and metrics"
    echo ""
}

# Run main function
main
