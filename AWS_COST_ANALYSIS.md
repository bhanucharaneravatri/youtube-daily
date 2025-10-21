# 💰 AWS Cost Analysis - Daily Video Uploads

## Scenario: 1 Video Per Day (30 videos/month)

### Assumptions Based on Your Setup:
- **Lambda execution time**: ~45-50 seconds per video
- **Lambda memory**: 2048 MB (2 GB)
- **Lambda architecture**: ARM64
- **Video size**: ~10-15 MB per video
- **Container image size**: ~600-700 MB
- **Region**: us-east-1

---

## 📊 Monthly Cost Breakdown (30 videos)

### 1. AWS Lambda ⚡
**Compute Costs:**
- **Execution time**: 50 seconds per video
- **Memory**: 2 GB
- **Total compute**: 50 sec × 2 GB × 30 videos = **3,000 GB-seconds/month**

**Pricing:**
- ARM64 compute: $0.0000133334 per GB-second
- **Compute cost**: 3,000 × $0.0000133334 = **$0.04/month**

**Request Costs:**
- 30 requests × $0.20 per 1M requests = **$0.000006/month** (negligible)

**Lambda Total: $0.04/month**

---

### 2. Amazon S3 📦
**Storage:**
- Video size: ~12 MB average per video
- 30 videos = 360 MB = 0.36 GB stored
- Assuming cumulative storage (keeping all videos):
  - Month 1: 0.36 GB
  - Month 2: 0.72 GB
  - Month 3: 1.08 GB
  - After 1 year: ~4.3 GB

**Pricing:**
- S3 Standard: $0.023 per GB/month
- **Month 1 storage cost**: 0.36 GB × $0.023 = **$0.008/month**
- **After 1 year**: 4.3 GB × $0.023 = **$0.10/month**

**Data Transfer:**
- Transfer OUT to internet: First 100 GB/month is **FREE**
- 30 videos × 12 MB = 360 MB/month - well within free tier
- **Transfer cost: $0.00/month** (free tier)

**S3 Total (Month 1): $0.008/month**
**S3 Total (After 1 year): $0.10/month**

---

### 3. Amazon ECR (Container Registry) 🐳
**Storage:**
- Container image size: ~650 MB = 0.65 GB

**Pricing:**
- $0.10 per GB/month for storage
- **ECR cost**: 0.65 GB × $0.10 = **$0.065/month**

**ECR Total: $0.07/month** (rounded)

---

### 4. CloudWatch Logs 📝
**Log Storage:**
- Logs per video: ~50-100 KB
- 30 videos = ~3 MB/month

**Pricing:**
- First 5 GB ingestion: **FREE**
- First 5 GB storage: **FREE**
- Your usage: ~3 MB - well within free tier

**CloudWatch Total: $0.00/month** (free tier)

---

## 💵 Total AWS Costs

### Month 1 (30 videos):
| Service | Cost |
|---------|------|
| Lambda | $0.04 |
| S3 | $0.01 |
| ECR | $0.07 |
| CloudWatch | $0.00 |
| **TOTAL** | **$0.12/month** |

### Per Video Cost:
**$0.12 ÷ 30 videos = $0.004 per video**

### Per Day Cost (1 video):
**$0.004/day** (less than half a cent!)

---

## 📈 Cost Projection Over Time

### Monthly Costs:
| Month | Lambda | S3 Storage* | ECR | CloudWatch | **Total** |
|-------|--------|-------------|-----|------------|-----------|
| 1 | $0.04 | $0.01 | $0.07 | $0.00 | **$0.12** |
| 3 | $0.04 | $0.02 | $0.07 | $0.00 | **$0.13** |
| 6 | $0.04 | $0.05 | $0.07 | $0.00 | **$0.16** |
| 12 | $0.04 | $0.10 | $0.07 | $0.00 | **$0.21** |

*S3 grows as you accumulate videos (if you keep them all)

---

## 💡 Cost Optimization Tips

### Option 1: Keep All Videos Forever
- **Year 1**: ~$2.50 total AWS cost
- S3 storage grows: 4.3 GB after 1 year
- Good for building a content library

### Option 2: Delete Videos After Upload
- Add automatic S3 deletion after YouTube upload succeeds
- **Constant cost**: $0.11/month (just Lambda + ECR)
- **Year 1**: ~$1.32 total AWS cost
- Saves ~$1.18/year

### Option 3: S3 Lifecycle Policy
- Auto-delete videos older than 30 days
- Keeps recent videos for backup
- **Constant cost**: $0.12/month
- **Year 1**: ~$1.44 total AWS cost

---

## 🎯 Final Summary

### AWS Cost for 1 Video Per Day:

**Daily**: $0.004 (less than 1 cent!)
**Monthly**: $0.12
**Yearly**: $1.44 - $2.50 (depending on storage retention)

### Total Cost Including OpenAI (for reference):
**Per Video**:
- AWS: $0.004
- OpenAI (GPT-3.5): $0.001
- OpenAI (DALL-E 3): $0.040
- **Total**: $0.045 (~5 cents per video)

**Monthly** (30 videos):
- AWS: $0.12
- OpenAI: $1.23
- **Total**: $1.35

**Yearly** (365 videos):
- AWS: $1.44 - $2.50
- OpenAI: $15.00
- **Total**: $16.44 - $17.50

---

## 🆓 AWS Free Tier Benefits (First 12 Months)

If you're on AWS Free Tier:

### Lambda Free Tier:
- 1 million requests/month FREE
- 400,000 GB-seconds of compute/month FREE
- Your usage: 3,000 GB-seconds/month
- **You're well within free tier!** ✅
- **Lambda cost: $0.00/month for first year**

### S3 Free Tier:
- 5 GB storage FREE
- 20,000 GET requests FREE
- 2,000 PUT requests FREE
- **S3 cost: $0.00/month for first year** ✅

### ECR Free Tier:
- 500 MB storage FREE
- Your usage: 650 MB
- **ECR cost: $0.015/month** (only charged for 150 MB)

**Total cost with Free Tier: ~$0.02/month!** 🎉

---

## 📊 Comparison

| Scenario | Monthly | Yearly |
|----------|---------|--------|
| **AWS Only** (no free tier) | $0.12 | $1.44 |
| **AWS Only** (with free tier) | $0.02 | $0.24* |
| **AWS + OpenAI** (no free tier) | $1.35 | $16.44 |
| **AWS + OpenAI** (with free tier) | $1.25 | $15.24* |

*Free tier only for first 12 months

---

## 🎊 Bottom Line

**AWS cost for 1 video per day: $0.004/day**

That's **less than half a cent per video** for:
- ✅ Serverless compute (Lambda)
- ✅ Video storage (S3)
- ✅ Container hosting (ECR)
- ✅ Logging (CloudWatch)
- ✅ Unlimited scalability
- ✅ Global availability

**With AWS Free Tier: Effectively $0 for the first year!** 🎉

The bulk of your costs (~92%) come from OpenAI (DALL-E), not AWS infrastructure!

