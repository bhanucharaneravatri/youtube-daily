#!/bin/bash
# Manual Instagram Credential Fetcher
# This is a simpler, more verbose version for debugging

echo "🔍 Manual Instagram Credential Finder"
echo "======================================"
echo ""

# Get input
read -p "Enter your App ID (1343701057484699): " APP_ID
read -sp "Enter your App Secret: " APP_SECRET
echo ""
read -p "Enter your User Access Token (with all permissions): " USER_TOKEN
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Exchange for Long-Lived Token"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

EXCHANGE_URL="https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=${APP_ID}&client_secret=${APP_SECRET}&fb_exchange_token=${USER_TOKEN}"

echo "Calling: $EXCHANGE_URL"
echo ""

LONG_TOKEN_RESPONSE=$(curl -s "$EXCHANGE_URL")
echo "Response:"
echo "$LONG_TOKEN_RESPONSE" | jq '.'
echo ""

LONG_TOKEN=$(echo "$LONG_TOKEN_RESPONSE" | jq -r '.access_token')

if [ "$LONG_TOKEN" == "null" ] || [ -z "$LONG_TOKEN" ]; then
    echo "❌ Failed to get long-lived token"
    echo "Full response: $LONG_TOKEN_RESPONSE"
    exit 1
fi

echo "✅ Long-lived token obtained!"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Get Facebook Pages"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

PAGES_URL="https://graph.facebook.com/v21.0/me/accounts?access_token=${LONG_TOKEN}"
echo "Calling: $PAGES_URL"
echo ""

PAGES_RESPONSE=$(curl -s "$PAGES_URL")
echo "Pages Response:"
echo "$PAGES_RESPONSE" | jq '.'
echo ""

# Count pages
PAGE_COUNT=$(echo "$PAGES_RESPONSE" | jq '.data | length')
echo "Found $PAGE_COUNT page(s)"
echo ""

if [ "$PAGE_COUNT" == "0" ] || [ "$PAGE_COUNT" == "null" ]; then
    echo "❌ No pages found!"
    echo ""
    echo "Possible issues:"
    echo "1. Token doesn't have 'pages_show_list' permission"
    echo "2. Your Facebook account doesn't manage any pages"
    echo "3. You need to grant permissions again"
    echo ""
    echo "Try:"
    echo "- Go to Graph API Explorer"
    echo "- Make sure 'pages_show_list' permission is checked"
    echo "- Generate a NEW token"
    exit 1
fi

# Show all pages
echo "Your Facebook Pages:"
echo "$PAGES_RESPONSE" | jq -r '.data[] | "  - \(.name) (ID: \(.id))"'
echo ""

# Get first page
PAGE_ID=$(echo "$PAGES_RESPONSE" | jq -r '.data[0].id')
PAGE_NAME=$(echo "$PAGES_RESPONSE" | jq -r '.data[0].name')

echo "Using page: $PAGE_NAME (ID: $PAGE_ID)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Get Instagram Business Account"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

IG_URL="https://graph.facebook.com/v21.0/${PAGE_ID}?fields=instagram_business_account&access_token=${LONG_TOKEN}"
echo "Calling: $IG_URL"
echo ""

IG_RESPONSE=$(curl -s "$IG_URL")
echo "Instagram Response:"
echo "$IG_RESPONSE" | jq '.'
echo ""

IG_USER_ID=$(echo "$IG_RESPONSE" | jq -r '.instagram_business_account.id')

if [ "$IG_USER_ID" == "null" ] || [ -z "$IG_USER_ID" ]; then
    echo "❌ No Instagram Business Account found for this page!"
    echo ""
    echo "Make sure:"
    echo "1. Your Instagram account (@ramayana_2025) is a Business account"
    echo "2. It's linked to the Facebook Page '$PAGE_NAME'"
    echo "3. The link is properly configured"
    echo ""
    exit 1
fi

echo "✅ Instagram Business Account ID: $IG_USER_ID"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Verify Instagram Access"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

VERIFY_URL="https://graph.facebook.com/v21.0/${IG_USER_ID}?fields=id,username&access_token=${LONG_TOKEN}"
echo "Calling: $VERIFY_URL"
echo ""

VERIFY_RESPONSE=$(curl -s "$VERIFY_URL")
echo "Verification Response:"
echo "$VERIFY_RESPONSE" | jq '.'
echo ""

IG_USERNAME=$(echo "$VERIFY_RESPONSE" | jq -r '.username')

if [ "$IG_USERNAME" == "null" ] || [ -z "$IG_USERNAME" ]; then
    echo "❌ Could not verify Instagram access!"
    echo "Full response: $VERIFY_RESPONSE"
    exit 1
fi

echo "✅ Verified Instagram: @$IG_USERNAME"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 SUCCESS! Your Instagram Credentials:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "INSTAGRAM_USER_ID=$IG_USER_ID"
echo "INSTAGRAM_ACCESS_TOKEN=$LONG_TOKEN"
echo ""
echo "Instagram Username: @$IG_USERNAME"
echo "Facebook Page: $PAGE_NAME"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💾 Saving to .env.instagram..."
cat > .env.instagram << EOF
# Instagram API Credentials
# Generated on: $(date)
# Expires in: ~60 days

INSTAGRAM_USER_ID=$IG_USER_ID
INSTAGRAM_ACCESS_TOKEN=$LONG_TOKEN

# Instagram Username: @$IG_USERNAME
# Facebook Page: $PAGE_NAME
EOF

echo "✅ Saved to .env.instagram"
echo ""
echo "🚀 Next: Update Lambda with these credentials"
echo ""

