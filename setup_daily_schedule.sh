#!/bin/bash

# Setup Daily Automated Video Upload
# Triggers Lambda function once per day at a specified time

FUNCTION_NAME="youtube-fact-generator"
REGION="us-east-1"
RULE_NAME="daily-fact-video-upload"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🕐 Setting up daily automated video uploads..."
echo ""

# Ask user for preferred time (default 12:00 PM UTC)
read -p "Enter daily upload time (HH:MM in UTC, default 12:00): " UPLOAD_TIME
UPLOAD_TIME=${UPLOAD_TIME:-12:00}

# Parse hour and minute
HOUR=$(echo $UPLOAD_TIME | cut -d: -f1)
MINUTE=$(echo $UPLOAD_TIME | cut -d: -f2)

# Validate input
if ! [[ "$HOUR" =~ ^[0-9]{1,2}$ ]] || ! [[ "$MINUTE" =~ ^[0-9]{2}$ ]]; then
    echo "❌ Invalid time format. Using default 12:00 UTC"
    HOUR=12
    MINUTE=00
fi

echo "📅 Schedule Configuration:"
echo "- Frequency: Once per day"
echo "- Time: $HOUR:$MINUTE UTC"
echo "- Action: Generate and upload 1 fact video"
echo ""

# Convert to your local timezone for reference
if command -v date &> /dev/null; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        LOCAL_TIME=$(TZ=UTC date -j -f "%H:%M" "$HOUR:$MINUTE" "+%I:%M %p %Z" 2>/dev/null || echo "Unable to convert")
    else
        # Linux
        LOCAL_TIME=$(TZ=UTC date -d "$HOUR:$MINUTE UTC" "+%I:%M %p %Z" 2>/dev/null || echo "Unable to convert")
    fi
    if [ "$LOCAL_TIME" != "Unable to convert" ]; then
        echo "   (Your local time: $LOCAL_TIME)"
        echo ""
    fi
fi

# Create EventBridge rule with cron expression
# Cron format: minute hour day month day-of-week year
CRON_EXPRESSION="cron($MINUTE $HOUR * * ? *)"

echo "📋 Creating EventBridge rule..."
aws events put-rule \
    --name "$RULE_NAME" \
    --description "Automatically upload 1 fact video per day at $HOUR:$MINUTE UTC" \
    --schedule-expression "$CRON_EXPRESSION" \
    --state ENABLED \
    --region "$REGION"

if [ $? -ne 0 ]; then
    echo "❌ Failed to create EventBridge rule"
    exit 1
fi

echo "✅ EventBridge rule created"
echo ""

# Add Lambda function as target
echo "🎯 Adding Lambda function as target..."
aws events put-targets \
    --rule "$RULE_NAME" \
    --targets '[{"Id":"1","Arn":"arn:aws:lambda:'$REGION':'$ACCOUNT_ID':function:'$FUNCTION_NAME'","Input":"{\"action\":\"full_pipeline\"}"}]' \
    --region "$REGION"

if [ $? -ne 0 ]; then
    echo "❌ Failed to add Lambda target"
    exit 1
fi

echo "✅ Lambda function added as target"
echo ""

# Grant EventBridge permission to invoke Lambda
echo "🔐 Granting EventBridge permission to invoke Lambda..."
aws lambda add-permission \
    --function-name "$FUNCTION_NAME" \
    --statement-id "AllowEventBridgeDailyInvoke" \
    --action "lambda:InvokeFunction" \
    --principal events.amazonaws.com \
    --source-arn "arn:aws:events:$REGION:$ACCOUNT_ID:rule/$RULE_NAME" \
    --region "$REGION" 2>&1 | grep -v "ResourceConflictException" || true

echo "✅ Permission granted"
echo ""

# Verify the setup
echo "🔍 Verifying configuration..."
echo ""

# Check rule status
RULE_STATUS=$(aws events describe-rule --name "$RULE_NAME" --region "$REGION" --query 'State' --output text)
echo "Rule Status: $RULE_STATUS"

# Check targets
TARGET_COUNT=$(aws events list-targets-by-rule --rule "$RULE_NAME" --region "$REGION" --query 'length(Targets)' --output text)
echo "Targets Configured: $TARGET_COUNT"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Daily Upload Schedule is ACTIVE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📅 Your channel will now automatically:"
echo "   • Generate 1 new fact video"
echo "   • Create stunning visuals with DALL-E"
echo "   • Add background music"
echo "   • Upload to YouTube"
echo "   • ALL at $HOUR:$MINUTE UTC daily"
echo ""
echo "💰 Cost per day: ~$0.05 (5 cents)"
echo "💰 Cost per month: ~$1.35 (30 videos)"
echo ""
echo "📺 Your channel: @FactGenerator-k5g"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚙️  Management Commands:"
echo ""
echo "Disable schedule:"
echo "  aws events disable-rule --name $RULE_NAME --region $REGION"
echo ""
echo "Enable schedule:"
echo "  aws events enable-rule --name $RULE_NAME --region $REGION"
echo ""
echo "Check next scheduled time:"
echo "  aws events describe-rule --name $RULE_NAME --region $REGION"
echo ""
echo "Delete schedule:"
echo "  aws events remove-targets --rule $RULE_NAME --ids 1 --region $REGION"
echo "  aws events delete-rule --name $RULE_NAME --region $REGION"
echo ""
echo "🎊 Setup complete! Your automated content creation is live!"

