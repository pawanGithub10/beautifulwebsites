"""
File upload service for avatars and images
"""

import logging
import uuid
from typing import Optional, Tuple
from datetime import datetime
import os
from io import BytesIO

from PIL import Image
import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)


class UploadService:
    """
    Service for handling file uploads to S3 or local storage
    """

    def __init__(self):
        self.use_s3 = bool(
            settings.AWS_ACCESS_KEY_ID and
            settings.AWS_SECRET_ACCESS_KEY and
            settings.AWS_S3_BUCKET
        )

        if self.use_s3:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION
            )
            self.bucket = settings.AWS_S3_BUCKET
            logger.info("S3 upload service initialized")
        else:
            # Use local storage
            self.local_storage_path = "uploads"
            os.makedirs(self.local_storage_path, exist_ok=True)
            logger.warning("Using local file storage (S3 not configured)")

    async def upload_avatar(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        content_type: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload user avatar

        Args:
            file_content: File bytes
            filename: Original filename
            user_id: User ID
            content_type: Content type (e.g., 'image/jpeg')

        Returns:
            Tuple of (success, url, error_message)
        """
        try:
            # Validate file type
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
                return False, None, f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}"

            # Validate file size
            file_size_mb = len(file_content) / (1024 * 1024)
            if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
                return False, None, f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"

            # Process image (resize, optimize)
            processed_content = self._process_image(file_content)

            if not processed_content:
                return False, None, "Failed to process image"

            # Generate unique filename
            unique_filename = f"avatars/{user_id}/{uuid.uuid4()}{file_ext}"

            # Upload to storage
            if self.use_s3:
                url = await self._upload_to_s3(
                    processed_content,
                    unique_filename,
                    content_type
                )
            else:
                url = await self._upload_to_local(
                    processed_content,
                    unique_filename
                )

            if not url:
                return False, None, "Failed to upload file"

            logger.info(f"Avatar uploaded successfully for user {user_id}: {url}")
            return True, url, None

        except Exception as e:
            logger.error(f"Error uploading avatar: {str(e)}")
            return False, None, str(e)

    async def upload_verification_document(
        self,
        file_content: bytes,
        filename: str,
        user_id: str,
        document_type: str,
        content_type: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload verification document

        Args:
            file_content: File bytes
            filename: Original filename
            user_id: User ID
            document_type: Type of document
            content_type: Content type

        Returns:
            Tuple of (success, url, error_message)
        """
        try:
            # Validate file type
            file_ext = os.path.splitext(filename)[1].lower()
            if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
                return False, None, "Invalid file type"

            # Validate file size
            file_size_mb = len(file_content) / (1024 * 1024)
            if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
                return False, None, "File too large"

            # Generate unique filename
            unique_filename = f"verifications/{user_id}/{document_type}/{uuid.uuid4()}{file_ext}"

            # Upload to storage
            if self.use_s3:
                url = await self._upload_to_s3(
                    file_content,
                    unique_filename,
                    content_type
                )
            else:
                url = await self._upload_to_local(
                    file_content,
                    unique_filename
                )

            if not url:
                return False, None, "Failed to upload file"

            logger.info(f"Verification document uploaded for user {user_id}: {url}")
            return True, url, None

        except Exception as e:
            logger.error(f"Error uploading verification document: {str(e)}")
            return False, None, str(e)

    def _process_image(self, image_bytes: bytes) -> Optional[bytes]:
        """
        Process image: resize and optimize

        Args:
            image_bytes: Original image bytes

        Returns:
            Processed image bytes or None
        """
        try:
            # Open image
            image = Image.open(BytesIO(image_bytes))

            # Convert RGBA to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background

            # Resize if too large (max 1000x1000 for avatars)
            max_size = (1000, 1000)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Save optimized image
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)

            return output.read()

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None

    async def _upload_to_s3(
        self,
        file_content: bytes,
        filename: str,
        content_type: str
    ) -> Optional[str]:
        """
        Upload file to S3

        Args:
            file_content: File bytes
            filename: S3 object key
            content_type: Content type

        Returns:
            Public URL or None
        """
        try:
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'
            )

            # Generate public URL
            url = f"https://{self.bucket}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{filename}"
            return url

        except ClientError as e:
            logger.error(f"S3 upload error: {str(e)}")
            return None

    async def _upload_to_local(
        self,
        file_content: bytes,
        filename: str
    ) -> Optional[str]:
        """
        Upload file to local storage

        Args:
            file_content: File bytes
            filename: Local filename

        Returns:
            Local URL or None
        """
        try:
            # Create directory if doesn't exist
            file_path = os.path.join(self.local_storage_path, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)

            # Return relative URL
            url = f"/uploads/{filename}"
            return url

        except Exception as e:
            logger.error(f"Local upload error: {str(e)}")
            return None

    async def delete_file(self, file_url: str) -> bool:
        """
        Delete file from storage

        Args:
            file_url: File URL to delete

        Returns:
            Success status
        """
        try:
            if self.use_s3:
                # Extract key from URL
                key = file_url.split(f"{self.bucket}.s3.{settings.AWS_S3_REGION}.amazonaws.com/")[-1]
                self.s3_client.delete_object(Bucket=self.bucket, Key=key)
            else:
                # Delete local file
                file_path = file_url.replace("/uploads/", self.local_storage_path + "/")
                if os.path.exists(file_path):
                    os.remove(file_path)

            logger.info(f"File deleted: {file_url}")
            return True

        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return False
