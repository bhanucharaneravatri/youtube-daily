# YouTube API Setup Guide

## 🎯 Overview

This guide will walk you through setting up YouTube API access for automated video uploads.

---

## 📋 Prerequisites

- Google Account
- Access to Google Cloud Console
- YouTube Channel

---

## 🚀 Step-by-Step Setup

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Create Project"**
3. Name it: `youtube-fact-generator`
4. Click **"Create"**

### Step 2: Enable YouTube Data API v3

1. In your project, go to **"APIs & Services" → "Library"**
2. Search for **"YouTube Data API v3"**
3. Click on it and press **"Enable"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services" → "OAuth consent screen"**
2. Choose **"External"** (unless you have Google Workspace)
3. Fill in the form:
   - **App name**: `YouTube Fact Generator`
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Click **"Save and Continue"**
5. **Scopes**: Click **"Add or Remove Scopes"**
   - Search for: `https://www.googleapis.com/auth/youtube.upload`
   - Select it and click **"Update"**
6. Click **"Save and Continue"**
7. **Test users**: Add your Gmail address
8. Click **"Save and Continue"**

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" → "Credentials"**
2. Click **"Create Credentials" → "OAuth 2.0 Client ID"**
3. Application type: **"Desktop app"**
4. Name: `YouTube Uploader`
5. Click **"Create"**
6. **Download** the JSON file (save as `client_secrets.json`)

---

## 🔑 Step 5: Get Refresh Token (Run Locally)

You need to run this once locally to get the refresh token:

### Option A: Using Python Script

1. **Save the YouTube uploader script**:
```bash
cd /Users/bhanueravatri/youtube-fact-generator/deployed_backup
cp youtube_uploader.py ~/youtube_auth.py
cd ~
```

2. **Install dependencies locally**:
```bash
pip3 install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
```

3. **Run the authentication script**:
```bash
python3 youtube_auth.py /path/to/client_secrets.json
```

4. **Follow the prompts**:
   - Browser will open automatically
   - Sign in with your Google account
   - Grant permissions
   - Close browser when done

5. **Copy the output**:
```
==================================================
SAVE THESE CREDENTIALS:
==================================================
YOUTUBE_CLIENT_ID=xxx...xxx.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-xxx...xxx
YOUTUBE_REFRESH_TOKEN=1//xxx...xxx
==================================================
```

### Option B: Using Google OAuth Playground (Alternative)

1. Go to [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
2. Click the settings gear icon (top right)
3. Check **"Use your own OAuth credentials"**
4. Enter your **Client ID** and **Client Secret**
5. In the left panel, scroll to **"YouTube Data API v3"**
6. Select: `https://www.googleapis.com/auth/youtube.upload`
7. Click **"Authorize APIs"**
8. Sign in and grant permissions
9. Click **"Exchange authorization code for tokens"**
10. Copy the **"Refresh token"**

---

## ⚙️ Step 6: Configure Lambda Environment Variables

Add the credentials to your Lambda function:

```bash
aws lambda update-function-configuration \
  --function-name youtube-fact-generator \
  --region us-east-1 \
  --environment "Variables={
    OPENAI_API_KEY=sk-proj-...,
    S3_BUCKET=youtube-fact-generator-videos-094822715906,
    GOOGLE_CLOUD_PROJECT=test-project,
    YOUTUBE_CLIENT_ID=xxx...xxx.apps.googleusercontent.com,
    YOUTUBE_CLIENT_SECRET=GOCSPX-xxx...xxx,
    YOUTUBE_REFRESH_TOKEN=1//xxx...xxx
  }"
```

**⚠️ Important**: Replace the values with your actual credentials!

---

## ✅ Step 7: Test the Integration

Test the full pipeline:

```bash
echo '{"action":"full_pipeline"}' > test-full.json

aws lambda invoke \
  --function-name youtube-fact-generator \
  --region us-east-1 \
  --cli-binary-format raw-in-base64-out \
  --payload file://test-full.json \
  response.json

cat response.json | python3 -m json.tool
```

Expected output:
```json
{
  "statusCode": 200,
  "message": "Full pipeline completed! 🎉",
  "fact": {...},
  "video_path": "/tmp/fact_video_xxx.jpg",
  "s3_url": "https://...",
  "youtube_url": "https://www.youtube.com/watch?v=..."
}
```

---

## 🔒 Security Best Practices

### Option 1: Environment Variables (Current)
✅ Simple  
✅ Good for testing  
⚠️ Visible in Lambda console  

### Option 2: AWS Secrets Manager (Recommended for Production)
✅ Encrypted storage  
✅ Automatic rotation  
✅ Audit logging  

To use Secrets Manager:

1. **Store credentials**:
```bash
aws secretsmanager create-secret \
  --name youtube-api-credentials \
  --secret-string '{
    "client_id": "xxx...xxx.apps.googleusercontent.com",
    "client_secret": "GOCSPX-xxx...xxx",
    "refresh_token": "1//xxx...xxx"
  }'
```

2. **Update Lambda IAM role** to allow `secretsmanager:GetSecretValue`

3. **Modify `youtube_uploader.py`** to fetch from Secrets Manager:
```python
import boto3
import json

def get_youtube_credentials():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='youtube-api-credentials')
    return json.loads(response['SecretString'])
```

---

## 🎬 Video Upload Settings

### Privacy Status Options
- `public` - Anyone can see
- `unlisted` - Only people with link can see
- `private` - Only you can see

Modify in `youtube_uploader.py`:
```python
'privacyStatus': 'public'  # Change as needed
```

### Category IDs
- `27` - Education
- `28` - Science & Technology
- `22` - People & Blogs
- `24` - Entertainment

### Default Video Metadata
Edit in `lambda_function.py` (line ~145):
```python
{
    'title': fact_data['title'],
    'description': fact_data['content'],
    'tags': ['facts', 'education', 'interesting'],
    'category_id': '27'
}
```

---

## 🐛 Troubleshooting

### Error: "The request cannot be completed because you have exceeded your quota"

**Solution**: 
1. Go to [Google Cloud Console → APIs & Services → Quotas](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas)
2. Check your daily quota (default: 10,000 units per day)
3. One upload = ~1600 units (you can upload ~6 videos/day)
4. Request quota increase if needed

### Error: "Access Not Configured"

**Solution**: Make sure YouTube Data API v3 is enabled in your project

### Error: "invalid_grant"

**Solution**: Refresh token expired. Re-run Step 5 to get a new refresh token

### Error: "The OAuth client was deleted"

**Solution**: Recreate OAuth credentials (Step 4)

---

## 📊 Current Pipeline Flow

```
┌─────────────────────┐
│  Generate Fact      │  ← OpenAI GPT-3.5
│  (AI-powered)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generate Image     │  ← OpenAI DALL-E 3
│  with Text Overlay  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Upload to S3       │  ← AWS S3 (private)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Upload to YouTube  │  ← YouTube Data API v3
└──────────┬──────────┘
           │
           ▼
      🎉 Done!
```

---

## 💰 Cost Estimation

### Per Video:
- **OpenAI (fact)**: ~$0.002 (GPT-3.5)
- **OpenAI (image)**: ~$0.04 (DALL-E 3 standard)
- **S3 storage**: ~$0.000023/GB/month
- **Lambda execution**: ~$0.0001 (30 sec @ 1024 MB)
- **YouTube upload**: FREE
- **Total**: ~$0.04-0.05 per video

### Daily Limits:
- **YouTube API**: ~6 videos/day (quota limit)
- **OpenAI**: Depends on your tier
- **Lambda**: No practical limit

---

## 🎯 Next Steps

1. ✅ Complete YouTube OAuth setup (Steps 1-6)
2. ✅ Test with `full_pipeline` action
3. ✅ Monitor CloudWatch logs for errors
4. 🔄 Set up EventBridge for scheduled automation
5. 📊 Add monitoring dashboards
6. 🎨 Customize video templates

---

## 📚 Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [OAuth 2.0 for TV and Device Apps](https://developers.google.com/identity/protocols/oauth2/limited-input-device)
- [Google Cloud Console](https://console.cloud.google.com/)
- [YouTube API Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)

---

## ✨ Your Lambda is Now Complete!

You have a fully automated pipeline that:
- ✅ Generates AI-powered facts
- ✅ Creates beautiful images with DALL-E
- ✅ Stores videos in S3
- ✅ Uploads to YouTube automatically

**All you need now is YouTube OAuth credentials!** 🎉

