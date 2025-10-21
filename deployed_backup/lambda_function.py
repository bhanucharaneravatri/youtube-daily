import logging
import os
import boto3
from datetime import datetime
from typing import Dict, Any

from config import Config
from fact_generator import FactGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upload_to_s3(file_path: str, bucket_name: str) -> str:
    """
    Upload a file to S3 and return the URL.
    
    Args:
        file_path: Local path to the file
        bucket_name: S3 bucket name
    
    Returns:
        str: S3 URL of the uploaded file
    """
    s3_client = boto3.client('s3')
    
    # Generate unique filename
    filename = os.path.basename(file_path)
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    s3_key = f"videos/{timestamp}_{filename}"
    
    # Upload file
    logger.info(f"⬆️ Uploading to S3: s3://{bucket_name}/{s3_key}")
    s3_client.upload_file(file_path, bucket_name, s3_key)
    
    # Generate URL
    s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
    
    return s3_url

def lambda_handler(event, context):
    try:
        logger.info("🚀 YouTube Fact Generator Lambda started")
        logger.info(f"Event received: {event}")
        
        config = Config()
        logger.info("✅ Configuration initialized")
        
        action = event.get('action')
        logger.info(f"Action requested: '{action}'")
        
        if action == 'generate_fact':
            logger.info("🤖 Processing fact generation request...")
            
            fact_gen = FactGenerator(config)
            logger.info("✅ Fact generator initialized")
            
            fact_data = fact_gen.generate_fact()
            logger.info(f"✅ Fact generated: {fact_data}")
            
            result = {
                'statusCode': 200,
                'message': 'Fact generated successfully! 🎉',
                'timestamp': datetime.utcnow().isoformat(),
                'fact': fact_data,
                'openai_used': hasattr(fact_gen, 'openai_client') and fact_gen.openai_client is not None,
                'event_processed': True
            }
            
            logger.info("✅ Fact generation completed successfully")
            return result
        
        elif action == 'create_video':
            logger.info("🎬 Processing video creation request...")
            
            # Get fact data from event or generate new one
            fact_data = event.get('fact_data')
            if not fact_data:
                logger.info("No fact provided, generating new one...")
                fact_gen = FactGenerator(config)
                fact_data = fact_gen.generate_fact()
                logger.info(f"✅ Fact generated: {fact_data}")
            
            # Create video
            video_creator = VideoCreator(config)
            logger.info("✅ Video creator initialized")
            
            video_path = video_creator.create_video(fact_data)
            logger.info(f"✅ Video created: {video_path}")
            
            # Upload to S3 (optional)
            s3_url = None
            if config.s3_bucket:
                try:
                    s3_url = upload_to_s3(video_path, config.s3_bucket)
                    logger.info(f"✅ Video uploaded to S3: {s3_url}")
                except Exception as e:
                    logger.warning(f"⚠️ S3 upload failed: {str(e)}")
            
            result = {
                'statusCode': 200,
                'message': 'Video created successfully! 🎬',
                'timestamp': datetime.utcnow().isoformat(),
                'fact': fact_data,
                'video_path': video_path,
                's3_url': s3_url,
                'event_processed': True
            }
            
            logger.info("✅ Video creation completed successfully")
            return result
        
        elif action == 'full_pipeline':
            logger.info("🚀 Processing full pipeline (fact → video → upload)...")
            
            # Step 1: Generate fact
            fact_gen = FactGenerator(config)
            fact_data = fact_gen.generate_fact()
            logger.info(f"✅ Step 1: Fact generated: {fact_data['title']}")
            
            # Step 2: Create video
            video_creator = VideoCreator(config)
            video_path = video_creator.create_video(fact_data)
            logger.info(f"✅ Step 2: Video created: {video_path}")
            
            # Step 3: Upload to S3
            s3_url = None
            if config.s3_bucket:
                try:
                    s3_url = upload_to_s3(video_path, config.s3_bucket)
                    logger.info(f"✅ Step 3: Uploaded to S3: {s3_url}")
                except Exception as e:
                    logger.error(f"❌ Step 3 failed: {str(e)}")
            
            # Step 4: Upload to YouTube
            youtube_url = None
            youtube_result = None
            try:
                uploader = YouTubeUploader(config)
                if s3_url:
                    youtube_result = uploader.download_from_s3_and_upload(
                        s3_url,
                        {
                            'title': fact_data['title'],
                            'description': fact_data['content'],
                            'tags': ['facts', 'education', fact_data.get('category', 'general').lower()],
                            'category_id': '27'  # Education
                        }
                    )
                    if youtube_result:
                        youtube_url = youtube_result.get('url')
                        logger.info(f"✅ Step 4: Uploaded to YouTube: {youtube_url}")
                else:
                    logger.warning("⚠️ Step 4: No S3 URL, skipping YouTube upload")
            except Exception as e:
                logger.error(f"❌ Step 4 failed: {str(e)}")
            
            result = {
                'statusCode': 200,
                'message': 'Full pipeline completed! 🎉',
                'timestamp': datetime.utcnow().isoformat(),
                'fact': fact_data,
                'video_path': video_path,
                's3_url': s3_url,
                'youtube_url': youtube_url,
                'event_processed': True
            }
            
            logger.info("✅ Full pipeline completed successfully")
            return result
        
        result = {
            'statusCode': 200,
            'message': 'Lambda function is working! 🎉',
            'timestamp': datetime.utcnow().isoformat(),
            'event': event,
            'action_detected': action
        }
        
        logger.info("✅ Lambda completed with default response")
        return result
        
    except Exception as e:
        error_msg = f"❌ Lambda execution failed: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        return {
            'statusCode': 500,
            'error': error_msg,
            'timestamp': datetime.utcnow().isoformat()
        }
