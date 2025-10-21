import logging
import os
import json
from typing import Dict, Any, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

class YouTubeUploader:
    def __init__(self, config):
        self.config = config
        self.youtube = None
        
        try:
            self._initialize_youtube_client()
            logger.info("✅ YouTubeUploader initialized")
        except Exception as e:
            logger.warning(f"⚠️ YouTubeUploader initialization failed: {str(e)}")
    
    def _initialize_youtube_client(self):
        """
        Initialize YouTube API client with OAuth2 credentials.
        """
        # Try to get credentials from environment variables
        client_id = os.getenv('YOUTUBE_CLIENT_ID')
        client_secret = os.getenv('YOUTUBE_CLIENT_SECRET')
        refresh_token = os.getenv('YOUTUBE_REFRESH_TOKEN')
        
        if not all([client_id, client_secret, refresh_token]):
            logger.warning("⚠️ YouTube credentials not configured")
            logger.info("Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_REFRESH_TOKEN")
            return
        
        try:
            # Create credentials from refresh token
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri='https://oauth2.googleapis.com/token',
                client_id=client_id,
                client_secret=client_secret,
                scopes=SCOPES
            )
            
            # Refresh the access token
            credentials.refresh(Request())
            
            # Build YouTube API client
            self.youtube = build('youtube', 'v3', credentials=credentials)
            logger.info("✅ YouTube API client initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize YouTube client: {str(e)}")
            raise
    
    def upload_video(self, video_path: str, metadata: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Upload a video to YouTube.
        
        Args:
            video_path: Path to the video file
            metadata: Dict with 'title', 'description', 'tags', 'category'
        
        Returns:
            Dict with 'video_id' and 'url' if successful, None if failed
        """
        if not self.youtube:
            logger.error("❌ YouTube client not initialized")
            return {
                'video_id': 'not_configured',
                'url': 'https://youtube.com/watch?v=not_configured',
                'status': 'YouTube API not configured'
            }
        
        try:
            logger.info(f"📤 Uploading video to YouTube: {video_path}")
            
            # Prepare video metadata
            title = metadata.get('title', 'Interesting Fact')
            description = metadata.get('description', metadata.get('content', ''))
            tags = metadata.get('tags', ['facts', 'education', 'interesting'])
            category_id = metadata.get('category_id', '27')  # Education category
            
            # Add hashtags to description
            hashtags = "\n\n#facts #didyouknow #education #learning"
            full_description = f"{description}{hashtags}"
            
            # Request body for the API
            body = {
                'snippet': {
                    'title': title[:100],  # YouTube title limit is 100 chars
                    'description': full_description[:5000],  # Description limit is 5000 chars
                    'tags': tags[:500],  # Max 500 tags
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': 'public',  # 'public', 'private', or 'unlisted'
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Check if file exists
            if not os.path.exists(video_path):
                logger.error(f"❌ Video file not found: {video_path}")
                return None
            
            # Create media upload
            media = MediaFileUpload(
                video_path,
                mimetype='video/mp4',
                resumable=True,
                chunksize=1024*1024  # 1MB chunks
            )
            
            # Execute upload
            logger.info("⬆️ Starting YouTube upload...")
            request = self.youtube.videos().insert(
                part='snippet,status',
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"⬆️ Upload progress: {progress}%")
            
            video_id = response['id']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            logger.info(f"✅ Video uploaded successfully: {video_url}")
            
            return {
                'video_id': video_id,
                'url': video_url,
                'status': 'uploaded'
            }
            
        except Exception as e:
            logger.error(f"❌ YouTube upload failed: {str(e)}")
            return {
                'video_id': 'error',
                'url': 'error',
                'status': f'Upload failed: {str(e)}'
            }
    
    def download_from_s3_and_upload(self, s3_url: str, metadata: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Download a video from S3 and upload it to YouTube.
        
        Args:
            s3_url: S3 URL of the video
            metadata: Video metadata
        
        Returns:
            Dict with upload results
        """
        try:
            # Parse S3 URL
            # Format: https://bucket.s3.amazonaws.com/key or s3://bucket/key
            if s3_url.startswith('s3://'):
                parts = s3_url.replace('s3://', '').split('/', 1)
                bucket = parts[0]
                key = parts[1]
            else:
                # HTTPS URL
                parts = s3_url.replace('https://', '').split('/', 1)
                bucket = parts[0].split('.')[0]
                key = parts[1]
            
            logger.info(f"📥 Downloading from S3: s3://{bucket}/{key}")
            
            # Download from S3
            s3_client = boto3.client('s3')
            local_path = f"/tmp/youtube_upload_{os.getpid()}.mp4"
            s3_client.download_file(bucket, key, local_path)
            
            logger.info(f"✅ Downloaded to: {local_path}")
            
            # Upload to YouTube
            result = self.upload_video(local_path, metadata)
            
            # Clean up local file
            try:
                os.remove(local_path)
                logger.info("🗑️ Cleaned up temporary file")
            except:
                pass
            
            return result
            
        except Exception as e:
            logger.error(f"❌ S3 download and YouTube upload failed: {str(e)}")
            return {
                'video_id': 'error',
                'url': 'error',
                'status': f'Failed: {str(e)}'
            }


def get_oauth_refresh_token():
    """
    Helper function to get OAuth refresh token.
    Run this locally (not in Lambda) to get the refresh token.
    
    Instructions:
    1. Go to https://console.cloud.google.com/apis/credentials
    2. Create OAuth 2.0 Client ID (Desktop app)
    3. Download the JSON file
    4. Run this function with the JSON file path
    5. It will open a browser for authentication
    6. Copy the refresh_token from the output
    """
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python youtube_uploader.py <path_to_client_secrets.json>")
        sys.exit(1)
    
    client_secrets_file = sys.argv[1]
    
    flow = InstalledAppFlow.from_client_secrets_file(
        client_secrets_file,
        SCOPES
    )
    
    credentials = flow.run_local_server(port=0)
    
    print("\n" + "="*50)
    print("SAVE THESE CREDENTIALS:")
    print("="*50)
    print(f"YOUTUBE_CLIENT_ID={credentials.client_id}")
    print(f"YOUTUBE_CLIENT_SECRET={credentials.client_secret}")
    print(f"YOUTUBE_REFRESH_TOKEN={credentials.refresh_token}")
    print("="*50)
    
    return credentials


if __name__ == "__main__":
    # Run this locally to get OAuth tokens
    get_oauth_refresh_token()
