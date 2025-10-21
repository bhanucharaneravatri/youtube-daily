#!/bin/bash
# Try known working public ffmpeg layers for arm64

echo "🔍 Testing public ffmpeg layers..."

# Known public layers (these change over time, so we'll try a few)
LAYERS=(
  "arn:aws:lambda:us-east-1:145266761615:layer:ffmpeg:9"
  "arn:aws:lambda:us-east-1:145266761615:layer:ffmpeg-python-38:1"
  "arn:aws:lambda:us-east-1:901912771163:layer:ffmpeg-python-layer:1"
)

for LAYER in "${LAYERS[@]}"; do
  echo ""
  echo "Trying: $LAYER"
  
  aws lambda update-function-configuration \
    --function-name youtube-fact-generator \
    --region us-east-1 \
    --layers \
      arn:aws:lambda:us-east-1:094822715906:layer:youtube-fact-generator-openai:2 \
      $LAYER \
    --query 'State' \
    --output text 2>&1
    
  if [ $? -eq 0 ]; then
    echo "✅ Layer added successfully!"
    exit 0
  else
    echo "❌ Failed, trying next..."
  fi
done

echo ""
echo "⚠️ No public layers worked. Creating our own optimized build..."
