#!/bin/bash
#
# Script to add ffmpeg Lambda Layer to your function
#

echo "🎬 Adding ffmpeg Layer to Lambda Function..."
echo ""

# For arm64, we'll use a public ffmpeg layer or create one
# Option 1: Use public layer (if available)
# Option 2: Create our own layer

echo "Checking for public ffmpeg layers in us-east-1 (arm64)..."

# Try to add a known working public layer for arm64
# This is a community-maintained layer
LAYER_ARN="arn:aws:lambda:us-east-1:145266761615:layer:ffmpeg-python-38:1"

echo ""
echo "Attempting to add layer: $LAYER_ARN"
echo ""

aws lambda update-function-configuration \
  --function-name youtube-fact-generator \
  --region us-east-1 \
  --layers \
    arn:aws:lambda:us-east-1:094822715906:layer:youtube-fact-generator-openai:2 \
    $LAYER_ARN \
  --query '{FunctionName:FunctionName,Layers:Layers[*].Arn}' \
  --output json

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Layer added successfully!"
else
    echo ""
    echo "⚠️ Public layer not available. Let's create our own..."
    echo ""
    echo "Run: ./create_ffmpeg_layer.sh"
fi

