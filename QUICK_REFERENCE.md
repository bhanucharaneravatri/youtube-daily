# Quick Reference - YouTube Fact Generator

## 🎯 Current State
**Status:** Placeholder Implementation (No Real Functionality)

## 📞 How to Invoke

### Test Basic Function
```bash
aws lambda invoke \
  --function-name youtube-fact-generator \
  --region us-east-1 \
  --payload '{}' \
  response.json
```

### Generate Fact (Placeholder)
```bash
aws lambda invoke \
  --function-name youtube-fact-generator \
  --region us-east-1 \
  --payload '{"action":"generate_fact"}' \
  response.json
```

## 📁 File Structure

```
deployed_backup/
├── lambda_function.py       # Main handler (action routing)
├── config.py                # Configuration (env vars)
├── fact_generator.py        # Hardcoded facts (needs OpenAI)
├── video_creator.py         # Placeholder (needs implementation)
├── youtube_uploader.py      # Placeholder (needs implementation)
└── [dependencies]/          # boto3, openai, requests, etc.
```

## 🔑 What Each Module Does

| Module | Current | Needed |
|--------|---------|--------|
| **lambda_function** | ✅ Routes actions | Nothing |
| **config** | ✅ Loads env vars | Add API keys |
| **fact_generator** | ❌ Returns test data | OpenAI integration |
| **video_creator** | ❌ Returns fake path | Video rendering |
| **youtube_uploader** | ❌ Returns fake ID | Google API integration |

## 🛠️ To Make It Work

### 1. Add OpenAI Integration (2-4 hours)
```python
# In fact_generator.py
import openai

class FactGenerator:
    def __init__(self, config):
        self.client = openai.OpenAI(api_key=config.openai_api_key)
    
    def generate_fact(self):
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a fact generator..."},
                {"role": "user", "content": "Generate an interesting fact"}
            ]
        )
        return response.choices[0].message.content
```

### 2. Add Environment Variables
```bash
aws lambda update-function-configuration \
  --function-name youtube-fact-generator \
  --environment Variables={OPENAI_API_KEY=sk-...}
```

### 3. Test Again
```bash
aws lambda invoke \
  --function-name youtube-fact-generator \
  --payload '{"action":"generate_fact"}' \
  response.json && cat response.json
```

## 📊 Dependencies Already Installed

✅ **Ready to Use:**
- boto3 (AWS SDK)
- openai (OpenAI SDK)
- requests (HTTP)
- pydantic (Validation)

❌ **Not Installed (Needed Later):**
- moviepy (Video creation)
- google-api-python-client (YouTube)
- pillow (Image processing)
- ffmpeg (Video encoding - needs Lambda layer)

## 💡 Quick Wins

1. **Enable OpenAI** - Just add API key and modify `fact_generator.py`
2. **Add CloudWatch Dashboard** - Monitor invocations
3. **Add Error Alerts** - SNS topic for failures
4. **Cost Tracking** - Tag resources

## 🔍 Debugging

### View Logs
```bash
aws logs tail /aws/lambda/youtube-fact-generator --follow
```

### Check Configuration
```bash
aws lambda get-function-configuration \
  --function-name youtube-fact-generator \
  --region us-east-1
```

### Download Latest Code
```bash
URL=$(aws lambda get-function --function-name youtube-fact-generator \
  --region us-east-1 --query 'Code.Location' --output text)
curl -o latest.zip "$URL"
```

## 🎬 Next Steps (Priority Order)

1. ✅ **Analyze deployed code** ← You are here
2. 🔄 Add OpenAI API key to Lambda environment
3. 🔄 Implement actual fact generation with OpenAI
4. 🔄 Test fact generation
5. ⏳ Decide on video creation approach
6. ⏳ Implement video creation
7. ⏳ Implement YouTube upload
8. ⏳ Add monitoring & alerts

## 📞 Support Commands

### Update Lambda Code
```bash
zip -r function.zip .
aws lambda update-function-code \
  --function-name youtube-fact-generator \
  --zip-file fileb://function.zip
```

### Increase Timeout (for video processing later)
```bash
aws lambda update-function-configuration \
  --function-name youtube-fact-generator \
  --timeout 900  # 15 minutes
```

### Increase Memory (for video processing later)
```bash
aws lambda update-function-configuration \
  --function-name youtube-fact-generator \
  --memory-size 3008  # MB (max: 10240)
```

