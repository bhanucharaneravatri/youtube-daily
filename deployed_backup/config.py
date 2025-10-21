import os
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration manager with OpenAI support.
    """
    def __init__(self):
        # OpenAI Configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # AWS Configuration
        self.google_cloud_project = os.getenv('GOOGLE_CLOUD_PROJECT', 'test-project')
        self.s3_bucket = os.getenv('S3_BUCKET', 'youtube-fact-generator-videos-094822715906')
        self.aws_region = os.getenv('AWS_REGION', 'us-east-1')
        
        # OpenAI Settings
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.openai_temperature = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
        self.openai_max_tokens = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
        
        logger.info("✅ Config initialized")
        logger.info(f"S3 Bucket: {self.s3_bucket}")
        logger.info(f"AWS Region: {self.aws_region}")
        logger.info(f"Google Project: {self.google_cloud_project}")
        logger.info(f"OpenAI API Key: {'Set ✅' if self.openai_api_key else 'Not Set ❌'}")
