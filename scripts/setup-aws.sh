#!/bin/bash

# ==================================================
# AWS Infrastructure Setup Script
# ==================================================
# Creates and configures all required AWS resources
# Account: webconnex-ai-dev (049101138630)
# ==================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
AWS_REGION="${AWS_REGION:-us-west-2}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-049101138630}"
AWS_PROFILE="${AWS_PROFILE:-049101138630-okta-admin-user}"

# Resource names
S3_BUCKET_VECTORS="webconnex-ai-dev-vectors"
S3_BUCKET_TRAINING="webconnex-ai-dev-training"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         🔧 AWS INFRASTRUCTURE SETUP SCRIPT               ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Helper functions
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

# Verify AWS credentials
verify_credentials() {
    print_info "Verifying AWS credentials..."

    export AWS_PROFILE=$AWS_PROFILE

    if ! aws sts get-caller-identity --profile $AWS_PROFILE > /dev/null 2>&1; then
        print_error "AWS credentials are invalid or expired."
        print_info "Please run: gimme-aws-creds --profile $AWS_PROFILE"
        exit 1
    fi

    ACCOUNT_ID=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text)
    CURRENT_USER=$(aws sts get-caller-identity --profile $AWS_PROFILE --query Arn --output text)

    print_status "Authenticated as: $CURRENT_USER"
    print_status "Account ID: $ACCOUNT_ID"

    if [ "$ACCOUNT_ID" != "$AWS_ACCOUNT_ID" ]; then
        print_error "Account ID mismatch!"
        print_error "Expected: $AWS_ACCOUNT_ID, Got: $ACCOUNT_ID"
        exit 1
    fi

    echo ""
}

# Create S3 buckets for vector storage
create_s3_buckets() {
    print_info "Setting up S3 buckets..."

    # Vectors bucket
    if aws s3api head-bucket --bucket $S3_BUCKET_VECTORS --profile $AWS_PROFILE 2>/dev/null; then
        print_warning "Bucket $S3_BUCKET_VECTORS already exists"
    else
        print_info "Creating bucket: $S3_BUCKET_VECTORS"

        if [ "$AWS_REGION" == "us-east-1" ]; then
            aws s3api create-bucket \
                --bucket $S3_BUCKET_VECTORS \
                --region $AWS_REGION \
                --profile $AWS_PROFILE
        else
            aws s3api create-bucket \
                --bucket $S3_BUCKET_VECTORS \
                --region $AWS_REGION \
                --profile $AWS_PROFILE \
                --create-bucket-configuration LocationConstraint=$AWS_REGION
        fi

        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket $S3_BUCKET_VECTORS \
            --versioning-configuration Status=Enabled \
            --profile $AWS_PROFILE

        # Enable encryption
        aws s3api put-bucket-encryption \
            --bucket $S3_BUCKET_VECTORS \
            --server-side-encryption-configuration '{
                "Rules": [{
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }]
            }' \
            --profile $AWS_PROFILE

        # Block public access
        aws s3api put-public-access-block \
            --bucket $S3_BUCKET_VECTORS \
            --public-access-block-configuration \
                BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true \
            --profile $AWS_PROFILE

        print_status "Created bucket: $S3_BUCKET_VECTORS"
    fi

    # Training bucket
    if aws s3api head-bucket --bucket $S3_BUCKET_TRAINING --profile $AWS_PROFILE 2>/dev/null; then
        print_warning "Bucket $S3_BUCKET_TRAINING already exists"
    else
        print_info "Creating bucket: $S3_BUCKET_TRAINING"

        if [ "$AWS_REGION" == "us-east-1" ]; then
            aws s3api create-bucket \
                --bucket $S3_BUCKET_TRAINING \
                --region $AWS_REGION \
                --profile $AWS_PROFILE
        else
            aws s3api create-bucket \
                --bucket $S3_BUCKET_TRAINING \
                --region $AWS_REGION \
                --profile $AWS_PROFILE \
                --create-bucket-configuration LocationConstraint=$AWS_REGION
        fi

        # Enable versioning
        aws s3api put-bucket-versioning \
            --bucket $S3_BUCKET_TRAINING \
            --versioning-configuration Status=Enabled \
            --profile $AWS_PROFILE

        # Enable encryption
        aws s3api put-bucket-encryption \
            --bucket $S3_BUCKET_TRAINING \
            --server-side-encryption-configuration '{
                "Rules": [{
                    "ApplyServerSideEncryptionByDefault": {
                        "SSEAlgorithm": "AES256"
                    }
                }]
            }' \
            --profile $AWS_PROFILE

        # Block public access
        aws s3api put-public-access-block \
            --bucket $S3_BUCKET_TRAINING \
            --public-access-block-configuration \
                BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true \
            --profile $AWS_PROFILE

        print_status "Created bucket: $S3_BUCKET_TRAINING"
    fi

    echo ""
}

# Verify Bedrock access
verify_bedrock_access() {
    print_info "Verifying Amazon Bedrock access..."

    # List foundation models
    if aws bedrock list-foundation-models \
        --region $AWS_REGION \
        --profile $AWS_PROFILE > /dev/null 2>&1; then
        print_status "Bedrock access verified"

        # Check Nova Pro availability
        if aws bedrock list-foundation-models \
            --region $AWS_REGION \
            --profile $AWS_PROFILE \
            --query 'modelSummaries[?contains(modelId, `nova-pro`)]' | grep -q "nova-pro"; then
            print_status "Amazon Nova Pro model available"
        else
            print_warning "Amazon Nova Pro model not found in this region"
            print_info "You may need to request access via AWS Console"
        fi

        # Check Titan Embeddings availability
        if aws bedrock list-foundation-models \
            --region $AWS_REGION \
            --profile $AWS_PROFILE \
            --query 'modelSummaries[?contains(modelId, `titan-embed`)]' | grep -q "titan-embed"; then
            print_status "Amazon Titan Embeddings available"
        else
            print_warning "Amazon Titan Embeddings not found"
        fi
    else
        print_error "Unable to access Bedrock. Check permissions."
        print_info "Required permissions:"
        echo "  • bedrock:ListFoundationModels"
        echo "  • bedrock:InvokeModel"
        echo "  • bedrock-runtime:InvokeModel"
    fi

    echo ""
}

# Verify Redshift access
verify_redshift_access() {
    print_info "Verifying Redshift access..."

    # Check if Redshift Data API is accessible
    if aws redshift-data list-statements \
        --region $AWS_REGION \
        --profile $AWS_PROFILE \
        --max-results 1 > /dev/null 2>&1; then
        print_status "Redshift Data API access verified"
    else
        print_warning "Unable to access Redshift Data API"
        print_info "This may be expected if cluster doesn't exist yet"
    fi

    echo ""
}

# Create IAM policy for application (optional)
create_iam_policy() {
    print_info "Checking IAM policies..."

    POLICY_NAME="WebconnexAI-TextToSQL-Policy"

    if aws iam get-policy \
        --policy-arn "arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${POLICY_NAME}" \
        --profile $AWS_PROFILE > /dev/null 2>&1; then
        print_warning "IAM policy $POLICY_NAME already exists"
    else
        print_info "IAM policy creation skipped (manual setup recommended)"
        print_info "Required permissions:"
        echo "  • S3: s3:GetObject, s3:PutObject, s3:ListBucket"
        echo "  • Bedrock: bedrock:InvokeModel"
        echo "  • Redshift: redshift-data:*"
        echo "  • Secrets Manager: secretsmanager:GetSecretValue"
    fi

    echo ""
}

# Summary and next steps
print_summary() {
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ✅ AWS SETUP COMPLETED                      ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    print_info "Resources created/verified:"
    echo "  • S3 Bucket (Vectors): $S3_BUCKET_VECTORS"
    echo "  • S3 Bucket (Training): $S3_BUCKET_TRAINING"
    echo "  • Bedrock Access: Verified"
    echo "  • Region: $AWS_REGION"
    echo "  • Account: $AWS_ACCOUNT_ID"
    echo ""
    print_info "Next steps:"
    echo "  1. Update .env file with these resource names"
    echo "  2. Verify Redshift cluster access"
    echo "  3. Configure Secrets Manager for Redshift credentials"
    echo "  4. Request Bedrock model access if needed"
    echo "  5. Run: docker-compose up -d"
    echo ""
}

# Main execution
main() {
    verify_credentials
    create_s3_buckets
    verify_bedrock_access
    verify_redshift_access
    create_iam_policy
    print_summary
}

# Run main function
main
