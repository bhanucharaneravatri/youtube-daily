#!/bin/bash

# Setup S3 Lifecycle Policy for Auto-Cleanup
# This keeps storage costs minimal and within AWS free tier

BUCKET_NAME="youtube-fact-generator-videos-094822715906"
REGION="us-east-1"

echo "🗑️ Setting up S3 auto-cleanup lifecycle policy..."
echo ""

# Create lifecycle policy JSON
cat > /tmp/s3-lifecycle-policy.json << 'EOF'
{
  "Rules": [
    {
      "ID": "DeleteOldVideosAfter30Days",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "videos/"
      },
      "Expiration": {
        "Days": 30
      }
    }
  ]
}
EOF

echo "📋 Lifecycle Policy:"
echo "- Auto-delete videos older than 30 days"
echo "- Applies to: videos/ folder only"
echo "- Keeps storage under 5 GB (free tier)"
echo ""

# Apply lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket "$BUCKET_NAME" \
  --lifecycle-configuration file:///tmp/s3-lifecycle-policy.json \
  --region "$REGION"

if [ $? -eq 0 ]; then
  echo "✅ Lifecycle policy applied successfully!"
  echo ""
  echo "📊 What this means:"
  echo "- Videos are deleted 30 days after upload"
  echo "- YouTube keeps your videos forever"
  echo "- S3 storage stays under 5 GB (FREE)"
  echo "- AWS cost: ~$0.11/month (just Lambda + ECR)"
  echo ""
  
  # Verify the policy
  echo "🔍 Verifying policy..."
  aws s3api get-bucket-lifecycle-configuration \
    --bucket "$BUCKET_NAME" \
    --region "$REGION" \
    --query 'Rules[0].[Id,Status,Expiration.Days]' \
    --output table
    
else
  echo "❌ Failed to apply lifecycle policy"
  exit 1
fi

# Clean up
rm /tmp/s3-lifecycle-policy.json

echo ""
echo "🎉 Done! Your S3 bucket will now auto-cleanup old videos."

