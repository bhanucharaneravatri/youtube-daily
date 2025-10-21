#!/bin/bash
set -e

echo "🎬 Building minimal ffmpeg for Lambda ARM64..."
echo ""

cd /Users/bhanueravatri/youtube-fact-generator

# Clean up
rm -rf ffmpeg-minimal
mkdir -p ffmpeg-minimal/bin

cd ffmpeg-minimal

# Download a different build - BtbN's builds are known to work well
echo "📥 Downloading BtbN ffmpeg build for Linux ARM64..."
curl -L "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz" -o ffmpeg.tar.xz

echo "📦 Extracting..."
tar -xf ffmpeg.tar.xz

# Find extracted directory
FFMPEG_DIR=$(ls -d ffmpeg-*-linux64-gpl | head -n 1)

# Copy just ffmpeg binary
cp "$FFMPEG_DIR/bin/ffmpeg" bin/
chmod +x bin/ffmpeg

# Test binary
echo "✅ Binary info:"
file bin/ffmpeg

# Clean up
rm -rf "$FFMPEG_DIR" ffmpeg.tar.xz

echo ""
echo "📦 Creating layer..."
cd ..
zip -r ffmpeg-minimal-layer.zip ffmpeg-minimal/bin/ > /dev/null

echo "✅ Layer created: $(ls -lh ffmpeg-minimal-layer.zip | awk '{print $5}')"
echo ""

# Upload
echo "⬆️ Publishing to Lambda..."
aws lambda publish-layer-version \
    --layer-name ffmpeg-minimal-arm64 \
    --description "Minimal ffmpeg for Lambda arm64" \
    --zip-file fileb://ffmpeg-minimal-layer.zip \
    --compatible-runtimes python3.12 \
    --compatible-architectures arm64 \
    --region us-east-1 \
    --query 'LayerVersionArn' \
    --output text

echo ""
echo "✅ Done!"

