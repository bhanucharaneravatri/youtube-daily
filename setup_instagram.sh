#!/bin/bash
# Instagram API Setup Helper Script
# This script helps you get your Instagram credentials

echo "🔧 Instagram API Setup Helper"
echo "================================"
echo ""

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq is not installed. Installing via homebrew..."
    brew install jq
fi

echo "📋 You'll need:"
echo "1. Facebook App ID"
echo "2. Facebook App Secret"
echo "3. Short-lived User Access Token (from Graph API Explorer)"
echo ""

# Get App ID
read -p "Enter your Facebook App ID: " APP_ID
echo ""

# Get App Secret
read -sp "Enter your Facebook App Secret (hidden): " APP_SECRET
echo ""
echo ""

# Get Short-lived token
read -p "Enter your short-lived User Access Token: " SHORT_TOKEN
echo ""

echo "🔄 Exchanging for long-lived token..."
echo ""

# Exchange for long-lived token
RESPONSE=$(curl -s -X GET "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=${APP_ID}&client_secret=${APP_SECRET}&fb_exchange_token=${SHORT_TOKEN}")

# Extract long-lived token
LONG_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
EXPIRES_IN=$(echo $RESPONSE | jq -r '.expires_in')

if [ "$LONG_TOKEN" == "null" ] || [ -z "$LONG_TOKEN" ]; then
    echo "❌ Error getting long-lived token:"
    echo $RESPONSE | jq '.'
    exit 1
fi

echo "✅ Long-lived token obtained!"
echo "⏰ Expires in: $EXPIRES_IN seconds (~60 days)"
echo ""

echo "🔍 Getting your Facebook Pages..."
PAGES_RESPONSE=$(curl -s -X GET "https://graph.facebook.com/v21.0/me/accounts?access_token=${LONG_TOKEN}")

echo "Pages found:"
echo $PAGES_RESPONSE | jq '.data[] | {name: .name, id: .id}'
echo ""

# Get first page ID
PAGE_ID=$(echo $PAGES_RESPONSE | jq -r '.data[0].id')

if [ "$PAGE_ID" == "null" ] || [ -z "$PAGE_ID" ]; then
    echo "❌ No pages found. Make sure you have a Facebook Page linked to your account."
    exit 1
fi

echo "Using first page ID: $PAGE_ID"
echo ""

echo "🔍 Getting Instagram Business Account ID..."
IG_RESPONSE=$(curl -s -X GET "https://graph.facebook.com/v21.0/${PAGE_ID}?fields=instagram_business_account&access_token=${LONG_TOKEN}")

IG_USER_ID=$(echo $IG_RESPONSE | jq -r '.instagram_business_account.id')

if [ "$IG_USER_ID" == "null" ] || [ -z "$IG_USER_ID" ]; then
    echo "❌ No Instagram Business Account found for this page."
    echo "Make sure:"
    echo "1. You have an Instagram Business account"
    echo "2. It's linked to your Facebook Page"
    exit 1
fi

echo "✅ Instagram Business Account ID: $IG_USER_ID"
echo ""

echo "🧪 Testing Instagram API access..."
TEST_RESPONSE=$(curl -s -X GET "https://graph.facebook.com/v21.0/${IG_USER_ID}?fields=id,username&access_token=${LONG_TOKEN}")

IG_USERNAME=$(echo $TEST_RESPONSE | jq -r '.username')

if [ "$IG_USERNAME" == "null" ] || [ -z "$IG_USERNAME" ]; then
    echo "❌ Error accessing Instagram account:"
    echo $TEST_RESPONSE | jq '.'
    exit 1
fi

echo "✅ Instagram username: @$IG_USERNAME"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Setup Complete! Your Instagram credentials:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "INSTAGRAM_USER_ID=$IG_USER_ID"
echo "INSTAGRAM_ACCESS_TOKEN=$LONG_TOKEN"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save to .env file
echo "💾 Saving to .env.instagram file..."
cat > .env.instagram << EOF
# Instagram API Credentials
# Generated on: $(date)
# Expires in: ~60 days

INSTAGRAM_USER_ID=$IG_USER_ID
INSTAGRAM_ACCESS_TOKEN=$LONG_TOKEN

# Instagram Username: @$IG_USERNAME
# Token expires in: $EXPIRES_IN seconds
EOF

echo "✅ Saved to .env.instagram"
echo ""

echo "🚀 Next Steps:"
echo "1. Update Lambda environment variables:"
echo ""
echo "   aws lambda update-function-configuration \\"
echo "     --function-name youtube-fact-generator \\"
echo "     --region us-east-1 \\"
echo "     --environment Variables=\"{ \\
echo "       OPENAI_API_KEY=\$OPENAI_API_KEY, \\
echo "       S3_BUCKET=youtube-fact-generator-videos-094822715906, \\
echo "       GOOGLE_CLOUD_PROJECT=youtube-fact-generator-475820, \\
echo "       YOUTUBE_REFRESH_TOKEN=\$YOUTUBE_REFRESH_TOKEN, \\
echo "       YOUTUBE_CLIENT_ID=\$YOUTUBE_CLIENT_ID, \\
echo "       YOUTUBE_CLIENT_SECRET=\$YOUTUBE_CLIENT_SECRET, \\
echo "       INSTAGRAM_USER_ID=$IG_USER_ID, \\
echo "       INSTAGRAM_ACCESS_TOKEN=$LONG_TOKEN \\
echo "     }\""
echo ""
echo "2. Deploy updated code (see INSTAGRAM_SETUP_GUIDE.md Step 11)"
echo ""
echo "3. Test the full pipeline"
echo ""
echo "📅 Reminder: Set a calendar reminder to refresh your token in 58 days!"
echo ""

