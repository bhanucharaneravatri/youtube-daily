#!/bin/bash
#
# Create ffmpeg Lambda Layer for arm64
#

set -e

echo "🎬 Creating ffmpeg Lambda Layer for arm64..."
echo ""

# Create layer directory structure
mkdir -p ffmpeg-layer/bin

cd ffmpeg-layer

echo "📥 Downloading ffmpeg static build for Linux arm64..."

# Download static ffmpeg build for Linux arm64
# Using johnvansickle's static builds which are well-maintained
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz -o ffmpeg.tar.xz

echo "📦 Extracting..."
tar -xf ffmpeg.tar.xz

# Find the extracted directory (it has a version number in the name)
FFMPEG_DIR=$(ls -d ffmpeg-*-arm64-static | head -n 1)

# Copy ffmpeg binary to layer structure
cp "$FFMPEG_DIR/ffmpeg" bin/
chmod +x bin/ffmpeg

# Clean up
rm -rf "$FFMPEG_DIR" ffmpeg.tar.xz

echo "✅ ffmpeg binary ready: $(./bin/ffmpeg -version | head -n 1)"
echo ""

# Create ZIP file for layer
echo "📦 Creating layer ZIP..."
cd ..
zip -r ffmpeg-layer.zip ffmpeg-layer/ > /dev/null

echo "✅ Layer ZIP created: $(ls -lh ffmpeg-layer.zip | awk '{print $5}')"
echo ""

# Upload to Lambda
echo "⬆️ Publishing Lambda Layer..."
LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name ffmpeg-arm64 \
    --description "FFmpeg static build for arm64 Lambda" \
    --zip-file fileb://ffmpeg-layer.zip \
    --compatible-runtimes python3.12 python3.11 \
    --compatible-architectures arm64 \
    --region us-east-1 \
    --query 'Version' \
    --output text)

echo "✅ Layer published: version $LAYER_VERSION"
echo ""

# Get the layer ARN
LAYER_ARN=$(aws lambda list-layer-versions \
    --layer-name ffmpeg-arm64 \
    --region us-east-1 \
    --query 'LayerVersions[0].LayerVersionArn' \
    --output text)

echo "📋 Layer ARN: $LAYER_ARN"
echo ""

# Add layer to function
echo "🔗 Adding layer to Lambda function..."
aws lambda update-function-configuration \
    --function-name youtube-fact-generator \
    --region us-east-1 \
    --layers \
        arn:aws:lambda:us-east-1:094822715906:layer:youtube-fact-generator-openai:2 \
        $LAYER_ARN \
    --query '{FunctionName:FunctionName,State:State}' \
    --output json

echo ""
echo "✅ ffmpeg layer added to youtube-fact-generator!"
echo ""
echo "Clean up:"
echo "  rm -rf ffmpeg-layer ffmpeg-layer.zip"

