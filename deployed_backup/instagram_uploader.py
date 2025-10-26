"""
Instagram uploader using Instagram Graph API.
Uploads videos to Instagram Business accounts.
"""

import logging
import requests
import time
import boto3
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class InstagramUploader:
    """
    Handles video uploads to Instagram using the Graph API.
    """
    
    def __init__(self, config):
        """
        Initialize Instagram uploader with configuration.
        
        Args:
            config: Configuration object with Instagram credentials
        """
        self.config = config
        self.s3_client = boto3.client('s3', region_name=config.aws_region)
        self.graph_api_version = 'v21.0'
        self.base_url = f'https://graph.facebook.com/{self.graph_api_version}'
        
        logger.info("✅ InstagramUploader initialized")
        logger.info(f"Instagram User ID: {'Set ✅' if config.instagram_user_id else 'Not Set ❌'}")
        logger.info(f"Instagram Access Token: {'Set ✅' if config.instagram_access_token else 'Not Set ❌'}")
    
    def _get_public_video_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Generate a presigned URL for the S3 video that Instagram can access.
        
        Args:
            s3_key: S3 key of the video file
            expiration: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL for the video
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.config.s3_bucket,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            logger.info(f"✅ Generated presigned URL for {s3_key}")
            return url
        except Exception as e:
            logger.error(f"❌ Error generating presigned URL: {str(e)}")
            raise
    
    def _create_media_container(self, video_url: str, caption: str) -> Optional[str]:
        """
        Create a media container for the video upload.
        
        Args:
            video_url: Public URL of the video
            caption: Caption for the Instagram post
            
        Returns:
            Creation ID if successful, None otherwise
        """
        try:
            endpoint = f"{self.base_url}/{self.config.instagram_user_id}/media"
            
            params = {
                'media_type': 'REELS',  # Use REELS for better reach
                'video_url': video_url,
                'caption': caption,
                'access_token': self.config.instagram_access_token
            }
            
            logger.info("📤 Creating Instagram media container...")
            response = requests.post(endpoint, params=params)
            response.raise_for_status()
            
            result = response.json()
            creation_id = result.get('id')
            
            if creation_id:
                logger.info(f"✅ Media container created: {creation_id}")
                return creation_id
            else:
                logger.error(f"❌ No creation ID in response: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error creating media container: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
    
    def _check_container_status(self, creation_id: str, max_attempts: int = 30) -> bool:
        """
        Check if the media container is ready for publishing.
        
        Args:
            creation_id: The media container ID
            max_attempts: Maximum number of status checks
            
        Returns:
            True if ready, False otherwise
        """
        endpoint = f"{self.base_url}/{creation_id}"
        
        for attempt in range(max_attempts):
            try:
                params = {
                    'fields': 'status_code',
                    'access_token': self.config.instagram_access_token
                }
                
                response = requests.get(endpoint, params=params)
                response.raise_for_status()
                
                result = response.json()
                status = result.get('status_code')
                
                logger.info(f"📊 Container status (attempt {attempt + 1}/{max_attempts}): {status}")
                
                if status == 'FINISHED':
                    logger.info("✅ Media container is ready!")
                    return True
                elif status == 'ERROR':
                    logger.error("❌ Media container processing failed")
                    return False
                
                # Wait 10 seconds before checking again
                time.sleep(10)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Error checking container status: {str(e)}")
                return False
        
        logger.warning(f"⚠️ Container not ready after {max_attempts} attempts")
        return False
    
    def _publish_media(self, creation_id: str) -> Optional[str]:
        """
        Publish the media container to Instagram.
        
        Args:
            creation_id: The media container ID
            
        Returns:
            Instagram media ID if successful, None otherwise
        """
        try:
            endpoint = f"{self.base_url}/{self.config.instagram_user_id}/media_publish"
            
            params = {
                'creation_id': creation_id,
                'access_token': self.config.instagram_access_token
            }
            
            logger.info("📤 Publishing to Instagram...")
            response = requests.post(endpoint, params=params)
            response.raise_for_status()
            
            result = response.json()
            media_id = result.get('id')
            
            if media_id:
                logger.info(f"✅ Video published successfully! Media ID: {media_id}")
                return media_id
            else:
                logger.error(f"❌ No media ID in response: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error publishing media: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            return None
    
    def upload_video(self, s3_key: str, fact_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Upload a video from S3 to Instagram.
        
        Args:
            s3_key: S3 key of the video file
            fact_data: Dictionary containing fact information (title, content, category)
            
        Returns:
            Dictionary with upload status and details
        """
        try:
            # Check if Instagram is configured
            if not self.config.instagram_user_id or not self.config.instagram_access_token:
                logger.warning("⚠️ Instagram not configured - skipping upload")
                return {
                    'success': False,
                    'error': 'Instagram credentials not configured',
                    'skipped': True
                }
            
            # Create caption from fact data
            caption = f"🧠 {fact_data.get('title', 'Daily Fact')}\n\n"
            caption += f"{fact_data.get('content', '')}\n\n"
            caption += f"#{fact_data.get('category', 'fact').replace(' ', '')} #dailyfacts #didyouknow #interestingfacts #learning"
            
            logger.info("🚀 Starting Instagram upload process...")
            logger.info(f"Video S3 key: {s3_key}")
            
            # Step 1: Generate presigned URL
            video_url = self._get_public_video_url(s3_key)
            
            # Step 2: Create media container
            creation_id = self._create_media_container(video_url, caption)
            if not creation_id:
                return {
                    'success': False,
                    'error': 'Failed to create media container'
                }
            
            # Step 3: Wait for processing
            if not self._check_container_status(creation_id):
                return {
                    'success': False,
                    'error': 'Media container processing failed or timed out'
                }
            
            # Step 4: Publish
            media_id = self._publish_media(creation_id)
            if not media_id:
                return {
                    'success': False,
                    'error': 'Failed to publish media'
                }
            
            logger.info("✅ Instagram upload completed successfully!")
            
            return {
                'success': True,
                'media_id': media_id,
                'creation_id': creation_id,
                'url': f"https://www.instagram.com/p/{media_id}/"
            }
            
        except Exception as e:
            error_msg = f"Unexpected error during Instagram upload: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return {
                'success': False,
                'error': error_msg
            }

