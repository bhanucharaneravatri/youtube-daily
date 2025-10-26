# Instagram API Setup Guide

This guide will walk you through setting up Instagram Graph API access for automated video uploads.

## Prerequisites

✅ **Instagram Business Account** (required)
✅ **Facebook Page** linked to your Instagram account
✅ **Facebook Developer Account**

---

## Step 1: Convert to Instagram Business Account

1. Open Instagram app on your phone
2. Go to **Settings** → **Account**
3. Select **Switch to Professional Account**
4. Choose **Business** as account type
5. Complete the setup process

---

## Step 2: Create/Link Facebook Page

1. Go to [Facebook Pages](https://www.facebook.com/pages/creation/)
2. Create a new page or use an existing one
3. Link it to your Instagram Business account:
   - Instagram App → **Settings** → **Account** → **Linked Accounts**
   - Select **Facebook** and link your page

---

## Step 3: Register as Facebook Developer

1. Go to [Facebook for Developers](https://developers.facebook.com/)
2. Click **Get Started** (top right)
3. Sign up with your Facebook account
4. Complete the registration

---

## Step 4: Create a Facebook App

1. Go to [My Apps](https://developers.facebook.com/apps/)
2. Click **Create App**
3. Select **Business** as app type
4. Fill in details:
   - **App Name**: `Daily Facts Bot` (or your choice)
   - **App Contact Email**: Your email
5. Click **Create App**

---

## Step 5: Add Instagram Graph API Product

1. In your app dashboard, find **Add Products**
2. Locate **Instagram Graph API**
3. Click **Set Up**

---

## Step 6: Configure App Settings

1. Go to **Settings** → **Basic** in the left sidebar
2. Note down:
   - **App ID** (you'll need this)
   - **App Secret** (click "Show" to reveal)
3. Add **Privacy Policy URL** (required):
   - Can use: `https://www.termsfeed.com/live/privacy-policy-generator`
4. Add **App Domains**: `localhost` (for testing)
5. Save changes

---

## Step 7: Get Instagram Business Account ID

### Method 1: Using Graph API Explorer

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app from the dropdown
3. Click **Generate Access Token**
4. Grant all permissions (especially `instagram_basic`, `pages_show_list`, `instagram_content_publish`)
5. In the query field, enter:
   ```
   me/accounts
   ```
6. Click **Submit**
7. Find your Facebook Page ID in the response
8. Now query:
   ```
   {page-id}?fields=instagram_business_account
   ```
9. The response will contain your Instagram Business Account ID

### Method 2: Using Access Token Debugger

1. Go to [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
2. Use the User Access Token from Method 1
3. Look for the `user_id` - this is your account ID

---

## Step 8: Generate Long-Lived Access Token

Short-lived tokens expire in 1 hour. We need a long-lived token (60 days).

### Get Short-Lived Token

1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Click **Generate Access Token**
4. Grant these permissions:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_show_list`
   - `pages_read_engagement`
5. Copy the access token

### Exchange for Long-Lived Token

Run this command (replace values):

```bash
curl -X GET "https://graph.facebook.com/v21.0/oauth/access_token? \
  grant_type=fb_exchange_token& \
  client_id=YOUR_APP_ID& \
  client_secret=YOUR_APP_SECRET& \
  fb_exchange_token=YOUR_SHORT_LIVED_TOKEN"
```

Or use this URL in your browser:
```
https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_LIVED_TOKEN
```

**Response:**
```json
{
  "access_token": "YOUR_LONG_LIVED_TOKEN",
  "token_type": "bearer",
  "expires_in": 5183944  // 60 days
}
```

**Save the `access_token`!** This is your long-lived token.

---

## Step 9: Test Your Setup

Test your credentials with this curl command:

```bash
curl -X GET "https://graph.facebook.com/v21.0/YOUR_INSTAGRAM_USER_ID?fields=id,username&access_token=YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": "17841408797797620",
  "username": "yourinstagramusername"
}
```

---

## Step 10: Update Lambda Environment Variables

Now update your Lambda function with Instagram credentials:

```bash
aws lambda update-function-configuration \
  --function-name youtube-fact-generator \
  --region us-east-1 \
  --environment "Variables={ \
    OPENAI_API_KEY=your_openai_key, \
    S3_BUCKET=youtube-fact-generator-videos-094822715906, \
    GOOGLE_CLOUD_PROJECT=youtube-fact-generator-475820, \
    YOUTUBE_REFRESH_TOKEN=your_youtube_token, \
    YOUTUBE_CLIENT_ID=your_youtube_client_id, \
    YOUTUBE_CLIENT_SECRET=your_youtube_client_secret, \
    INSTAGRAM_USER_ID=your_instagram_business_account_id, \
    INSTAGRAM_ACCESS_TOKEN=your_long_lived_token \
  }"
```

---

## Step 11: Deploy Updated Code

Build and deploy the Docker image with Instagram support:

```bash
cd /Users/bhanueravatri/youtube-fact-generator

# Build Docker image
docker build -f Dockerfile.lambda -t youtube-fact-generator:instagram .

# Tag for ECR
docker tag youtube-fact-generator:instagram 094822715906.dkr.ecr.us-east-1.amazonaws.com/youtube-fact-generator:instagram

# Push to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin 094822715906.dkr.ecr.us-east-1.amazonaws.com

docker push 094822715906.dkr.ecr.us-east-1.amazonaws.com/youtube-fact-generator:instagram

# Update Lambda function
aws lambda update-function-code \
  --function-name youtube-fact-generator \
  --image-uri 094822715906.dkr.ecr.us-east-1.amazonaws.com/youtube-fact-generator:instagram \
  --region us-east-1
```

---

## Step 12: Test the Integration

Test the full pipeline with Instagram upload:

```bash
aws lambda invoke \
  --function-name youtube-fact-generator \
  --region us-east-1 \
  --cli-binary-format raw-in-base64-out \
  --payload '{"action":"full_pipeline"}' \
  response.json

cat response.json | jq
```

---

## Important Notes

### Access Token Refresh

Long-lived tokens expire after 60 days. You have two options:

1. **Manual Refresh**: Repeat Step 8 every 60 days
2. **Automatic Refresh** (recommended): Implement token refresh in your Lambda function

### Instagram Video Requirements

- **Format**: MP4 (H.264 video codec, AAC audio)
- **Duration**: 3-60 seconds (for Reels)
- **Aspect Ratio**: 9:16 (vertical), 1:1 (square), or 4:5
- **Resolution**: 720p minimum (1080p recommended)
- **File Size**: Maximum 100MB
- **Frame Rate**: 23-60 FPS

Your videos already meet these requirements! ✅

### Rate Limits

Instagram Graph API has rate limits:
- **200 calls per hour per user**
- **100 media container creations per hour**

For 1 video/day, you're well within limits! ✅

### Publishing Delays

Instagram may take 5-15 minutes to process your video before publishing. The code includes automatic status checking.

---

## Troubleshooting

### Error: "Invalid OAuth Access Token"

- **Cause**: Token expired or invalid
- **Solution**: Generate a new long-lived token (Step 8)

### Error: "This endpoint requires the 'pages_show_list' permission"

- **Cause**: Missing permissions
- **Solution**: Regenerate token with all required permissions (Step 8)

### Error: "Instagram account not found"

- **Cause**: Account is not a Business account or not linked to Facebook Page
- **Solution**: Verify Steps 1 & 2

### Error: "Video processing failed"

- **Cause**: Video doesn't meet Instagram requirements
- **Solution**: Check video format, duration, and file size

### Error: "Rate limit exceeded"

- **Cause**: Too many API calls
- **Solution**: Wait 1 hour or upgrade to Instagram API with higher limits

---

## Security Best Practices

1. ✅ **Never commit tokens to Git** (already protected by `.gitignore`)
2. ✅ **Store tokens in Lambda environment variables**
3. ✅ **Rotate tokens every 60 days**
4. ✅ **Monitor token usage in Facebook App Dashboard**
5. ✅ **Use HTTPS URLs for video uploads**

---

## Cost Implications

**Instagram API**: **FREE** ✅

No additional AWS costs for Instagram uploads (uses existing Lambda and S3 infrastructure).

---

## Next Steps

After setup:

1. ✅ Test with a single video
2. ✅ Monitor CloudWatch logs
3. ✅ Check Instagram account for posted video
4. ✅ Set calendar reminder for token renewal (58 days)

---

## Useful Links

- [Instagram Graph API Documentation](https://developers.facebook.com/docs/instagram-api/)
- [Instagram Content Publishing](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)

---

## Support

If you encounter issues:

1. Check CloudWatch logs: `aws logs tail /aws/lambda/youtube-fact-generator --follow`
2. Test API manually using Graph API Explorer
3. Verify all permissions in your Facebook App

---

**Ready to go multi-platform! 🚀📱**

