import logging
import os
import tempfile
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import openai

logger = logging.getLogger(__name__)

class VideoCreator:
    def __init__(self, config):
        self.config = config
        
        if config.openai_api_key:
            self.client = openai.OpenAI(api_key=config.openai_api_key)
            logger.info("✅ VideoCreator initialized with OpenAI DALL-E")
        else:
            self.client = None
            logger.warning("⚠️ VideoCreator initialized without OpenAI")
    
    def create_video(self, fact_data: dict) -> str:
        """
        Create a video from fact data using DALL-E for background image.
        Returns path to the created video file.
        
        Args:
            fact_data: Dict with 'title', 'content', 'category'
        
        Returns:
            str: Path to the created video/image file
        """
        try:
            logger.info(f"🎨 Creating video for fact: {fact_data.get('title', 'Unknown')}")
            
            # Step 1: Generate background image with DALL-E
            background_image = self._generate_background_image(fact_data)
            
            # Step 2: Add text overlay
            final_image = self._add_text_overlay(background_image, fact_data)
            
            # Step 3: Save image to temporary file
            image_path = os.path.join(tempfile.gettempdir(), f"fact_image_{os.getpid()}.jpg")
            final_image.save(image_path, 'JPEG', quality=95)
            logger.info(f"✅ Image created: {image_path}")
            
            # Step 4: Convert to MP4 video
            video_path = self._convert_to_video(image_path)
            
            logger.info(f"✅ Video created successfully: {video_path}")
            return video_path
            
        except Exception as e:
            logger.error(f"❌ Error creating video: {str(e)}")
            # Return a fallback static image path
            return self._create_fallback_image(fact_data)
    
    def _generate_background_image(self, fact_data: dict) -> Image.Image:
        """
        Generate a background image using DALL-E based on the fact.
        """
        if not self.client:
            logger.warning("⚠️ No OpenAI client, creating colored background")
            return self._create_colored_background()
        
        try:
            title = fact_data.get('title', 'Interesting Fact')
            category = fact_data.get('category', 'General')
            
            # Create a prompt for DALL-E optimized for facts
            prompt = f"Create a visually stunning, professional background image for a fact video about: {title}. Style: cinematic, high-quality, {category.lower()} themed, vibrant colors, suitable as a backdrop for text overlay. No text in the image."
            
            logger.info(f"🎨 Generating DALL-E image with prompt: {prompt[:100]}...")
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1792x1024",  # Landscape format for video
                quality="standard",  # or "hd" for higher quality but more expensive
                n=1
            )
            
            image_url = response.data[0].url
            logger.info(f"✅ DALL-E image generated: {image_url[:50]}...")
            
            # Download the image
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            
            image = Image.open(BytesIO(image_response.content))
            logger.info(f"✅ Image downloaded: {image.size}")
            
            return image
            
        except Exception as e:
            logger.error(f"❌ Error generating DALL-E image: {str(e)}")
            return self._create_colored_background()
    
    def _create_colored_background(self) -> Image.Image:
        """
        Create a simple colored gradient background as fallback.
        """
        logger.info("🎨 Creating colored gradient background")
        
        # Create a gradient background
        width, height = 1920, 1080
        image = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(image)
        
        # Create a gradient from blue to purple
        for i in range(height):
            ratio = i / height
            r = int(75 + (140 - 75) * ratio)
            g = int(0 + (100 - 0) * ratio)
            b = int(130 + (200 - 130) * ratio)
            draw.line([(0, i), (width, i)], fill=(r, g, b))
        
        return image
    
    def _add_text_overlay(self, background: Image.Image, fact_data: dict) -> Image.Image:
        """
        Add text overlay with the fact title and content on the background image.
        """
        logger.info("✍️ Adding text overlay")
        
        # Resize background to standard 1920x1080 if needed
        if background.size != (1920, 1080):
            background = background.resize((1920, 1080), Image.Resampling.LANCZOS)
        
        # Create a semi-transparent overlay for better text readability
        overlay = Image.new('RGBA', background.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Add dark semi-transparent rectangles for text areas
        # Title area
        draw.rectangle([(100, 200), (1820, 400)], fill=(0, 0, 0, 180))
        # Content area
        draw.rectangle([(100, 450), (1820, 850)], fill=(0, 0, 0, 150))
        
        # Composite the overlay onto the background
        background = background.convert('RGBA')
        background = Image.alpha_composite(background, overlay)
        background = background.convert('RGB')
        
        # Now add text
        draw = ImageDraw.Draw(background)
        
        title = fact_data.get('title', 'Interesting Fact')
        content = fact_data.get('content', '')
        category = fact_data.get('category', 'General')
        
        # Try to load a nice font, fall back to default if not available
        # Perfect balance - clearly readable without overwhelming
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 85)
            content_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 52)
            category_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 38)
        except:
            logger.warning("⚠️ Custom fonts not found, using default")
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
            category_font = ImageFont.load_default()
        
        # Draw category tag
        draw.text((120, 220), f"📚 {category}", font=category_font, fill=(255, 200, 100))
        
        # Draw title (with word wrap)
        title_lines = self._wrap_text(title, title_font, 1700, draw)
        y_offset = 320
        for line in title_lines:
            draw.text((120, y_offset), line, font=title_font, fill=(255, 255, 255))
            y_offset += 140
        
        # Draw content (with word wrap)
        content_lines = self._wrap_text(content, content_font, 1700, draw)
        y_offset = 520
        for line in content_lines:
            draw.text((120, y_offset), line, font=content_font, fill=(240, 240, 240))
            y_offset += 90
        
        logger.info("✅ Text overlay added successfully")
        return background
    
    def _wrap_text(self, text: str, font, max_width: int, draw) -> list:
        """
        Wrap text to fit within a maximum width.
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _convert_to_video(self, image_path: str, duration: int = 15) -> str:
        """
        Convert a static image to MP4 video using OpenCV.
        Falls back to returning the image if OpenCV is not available.
        
        Args:
            image_path: Path to the input image
            duration: Video duration in seconds
        
        Returns:
            Path to the created MP4 video
        """
        try:
            import cv2
            import numpy as np
        except ImportError:
            logger.warning("⚠️ OpenCV not available, returning image instead of video")
            return image_path
        
        output_path = image_path.replace('.jpg', '.mp4')
        
        try:
            logger.info(f"🎬 Converting image to {duration}s video using OpenCV")
            
            # Read the image
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"❌ Could not read image: {image_path}")
                return image_path
            
            height, width, _ = img.shape
            logger.info(f"Image dimensions: {width}x{height}")
            
            # Define codec and create VideoWriter
            # Use mp4v codec for MP4 format
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 30  # frames per second
            
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                logger.error("❌ Could not open VideoWriter")
                return image_path
            
            # Write the same frame multiple times to create duration
            total_frames = fps * duration
            logger.info(f"Writing {total_frames} frames at {fps} FPS...")
            
            for i in range(total_frames):
                out.write(img)
                if i % 100 == 0:
                    logger.info(f"Progress: {i}/{total_frames} frames")
            
            # Release everything
            out.release()
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                logger.info(f"✅ Video created: {output_path} ({file_size:.2f} MB)")
                
                # Add background music
                output_path = self._add_background_music(output_path, duration)
                
                # Clean up the source image
                try:
                    os.remove(image_path)
                except:
                    pass
                
                return output_path
            else:
                logger.error("❌ Video file was not created")
                return image_path
                
        except Exception as e:
            logger.error(f"❌ Video conversion error: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return image_path
    
    def _add_background_music(self, video_path: str, duration: int) -> str:
        """
        Add background music to the video using ffmpeg directly.
        
        Args:
            video_path: Path to the video file
            duration: Video duration in seconds
        
        Returns:
            Path to the video with audio
        """
        import subprocess
        import traceback
        
        try:
            logger.info("🎵 Adding background music...")
            
            # Check if background music file exists
            music_path = "/var/task/background_music.mp3"
            if not os.path.exists(music_path):
                logger.warning(f"⚠️ Background music not found at {music_path}, skipping")
                return video_path
            
            # Try to find ffmpeg (from imageio-ffmpeg)
            ffmpeg_path = None
            try:
                import imageio_ffmpeg
                ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
                logger.info(f"✅ Found ffmpeg at: {ffmpeg_path}")
            except Exception as e:
                logger.warning(f"⚠️ imageio_ffmpeg not available: {str(e)}")
                # Try system ffmpeg
                import shutil
                ffmpeg_path = shutil.which('ffmpeg')
                if not ffmpeg_path:
                    logger.warning("⚠️ ffmpeg not found, skipping background music")
                    return video_path
            
            # Create output path
            output_path = video_path.replace('.mp4', '_with_music.mp4')
            
            # Use ffmpeg to add audio
            # -stream_loop -1: loop audio indefinitely
            # -t duration: cut to video duration
            # -filter:a "volume=0.3": reduce audio volume to 30%
            logger.info(f"🎬 Merging video with background music using ffmpeg...")
            cmd = [
                ffmpeg_path,
                '-i', video_path,  # Input video
                '-stream_loop', '-1',  # Loop audio
                '-i', music_path,  # Input audio
                '-t', str(duration),  # Duration
                '-c:v', 'copy',  # Copy video codec (no re-encoding)
                '-filter:a', 'volume=0.3',  # Reduce audio volume
                '-c:a', 'aac',  # Audio codec
                '-shortest',  # End when shortest input ends
                '-y',  # Overwrite output
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"✅ Background music added successfully: {output_path}")
                
                # Remove original video without music
                try:
                    os.remove(video_path)
                except:
                    pass
                
                return output_path
            else:
                logger.error(f"❌ ffmpeg failed (exit code {result.returncode})")
                if result.stderr:
                    logger.error(f"ffmpeg stderr: {result.stderr[:500]}")
                return video_path
            
        except subprocess.TimeoutExpired:
            logger.error("❌ ffmpeg timeout while adding music")
            return video_path
        except Exception as e:
            logger.error(f"❌ Error adding background music: {str(e)}")
            logger.error(traceback.format_exc())
            return video_path
    
    def _create_fallback_image(self, fact_data: dict) -> str:
        """
        Create a simple fallback image if all else fails.
        """
        logger.info("🎨 Creating fallback image")
        
        try:
            background = self._create_colored_background()
            final_image = self._add_text_overlay(background, fact_data)
            
            output_path = os.path.join(tempfile.gettempdir(), f"fact_fallback_{os.getpid()}.jpg")
            final_image.save(output_path, 'JPEG', quality=95)
            
            return output_path
        except Exception as e:
            logger.error(f"❌ Even fallback failed: {str(e)}")
            return "/tmp/placeholder_video.jpg"
