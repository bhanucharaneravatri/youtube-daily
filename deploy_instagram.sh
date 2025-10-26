#!/bin/bash
# Deploy Instagram Support to AWS Lambda
# This script builds and deploys the updated Lambda function with Instagram support

set -e  # Exit on error

echo "🚀 Deploying Instagram Support to Lambda"
echo "========================================"
echo ""

# Set AWS credentials (configure via aws configure or environment variables)
# export AWS_ACCESS_KEY_ID=your_access_key
# export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Configuration
ECR_REGISTRY="094822715906.dkr.ecr.us-east-1.amazonaws.com"
IMAGE_NAME="youtube-fact-generator"
TAG="instagram"
FUNCTION_NAME="youtube-fact-generator"

echo "📦 Configuration:"
echo "  Registry: $ECR_REGISTRY"
echo "  Image: $IMAGE_NAME:$TAG"
echo "  Function: $FUNCTION_NAME"
echo ""

# Step 1: Build Docker image
echo "🔨 Step 1: Building Docker image..."
docker build -f Dockerfile -t $IMAGE_NAME:$TAG .
echo "✅ Docker image built successfully"
echo ""

# Step 2: Tag for ECR
echo "🏷️  Step 2: Tagging image for ECR..."
docker tag $IMAGE_NAME:$TAG $ECR_REGISTRY/$IMAGE_NAME:$TAG
echo "✅ Image tagged"
echo ""

# Step 3: Login to ECR
echo "🔐 Step 3: Logging in to ECR..."
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin $ECR_REGISTRY
echo "✅ Logged in to ECR"
echo ""

# Step 4: Push to ECR
echo "⬆️  Step 4: Pushing image to ECR..."
docker push $ECR_REGISTRY/$IMAGE_NAME:$TAG
echo "✅ Image pushed successfully"
echo ""

# Step 5: Update Lambda function
echo "🔄 Step 5: Updating Lambda function..."
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --image-uri $ECR_REGISTRY/$IMAGE_NAME:$TAG \
  --region us-east-1 \
  --output json > /tmp/lambda-update.json

echo "✅ Lambda function updated"
echo ""

# Step 6: Wait for update to complete
echo "⏳ Step 6: Waiting for update to complete..."
aws lambda wait function-updated --function-name $FUNCTION_NAME --region us-east-1
echo "✅ Function update complete"
echo ""

# Step 7: Verify deployment
echo "🔍 Step 7: Verifying deployment..."
FUNCTION_INFO=$(aws lambda get-function-configuration \
  --function-name $FUNCTION_NAME \
  --region us-east-1 \
  --output json)

echo "Function Details:"
echo $FUNCTION_INFO | jq '{
  FunctionName: .FunctionName,
  State: .State,
  LastUpdateStatus: .LastUpdateStatus,
  CodeSize: .CodeSize,
  MemorySize: .MemorySize,
  Timeout: .Timeout,
  ImageUri: .ImageUri
}'

echo ""
echo "Environment Variables:"
echo $FUNCTION_INFO | jq '.Environment.Variables | keys'
echo ""

# Check if Instagram variables are set
HAS_IG_USER=$(echo $FUNCTION_INFO | jq -r '.Environment.Variables.INSTAGRAM_USER_ID // "NOT_SET"')
HAS_IG_TOKEN=$(echo $FUNCTION_INFO | jq -r 'if .Environment.Variables.INSTAGRAM_ACCESS_TOKEN then "SET" else "NOT_SET" end')

echo "Instagram Configuration:"
echo "  User ID: $HAS_IG_USER"
echo "  Access Token: $HAS_IG_TOKEN"
echo ""

if [ "$HAS_IG_USER" == "NOT_SET" ] || [ "$HAS_IG_TOKEN" == "NOT_SET" ]; then
    echo "⚠️  Instagram credentials not configured yet"
    echo ""
    echo "To enable Instagram uploads:"
    echo "  1. Run: ./setup_instagram.sh"
    echo "  2. Follow the prompts to get your credentials"
    echo "  3. Update Lambda environment variables with the output"
    echo ""
    echo "For now, the function will skip Instagram uploads (YouTube still works)"
else
    echo "✅ Instagram credentials configured!"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Your Lambda function now supports Instagram uploads!"
echo ""
echo "Next steps:"
echo "1. If you haven't already, run: ./setup_instagram.sh"
echo "2. Test the function: aws lambda invoke --function-name $FUNCTION_NAME --payload '{\"action\":\"full_pipeline\"}' response.json"
echo "3. Check logs: aws logs tail /aws/lambda/$FUNCTION_NAME --follow"
echo ""

