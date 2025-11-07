import logging
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)

class MediaFilesStorage(S3Boto3Storage):
    """
    Custom storage for media files using S3.
    This will be used when USE_S3=True in settings.
    django-storages automatically reads AWS_* settings from Django settings.
    """
    location = 'media'
    file_overwrite = False
    default_acl = 'public-read'
    
    def __init__(self, *args, **kwargs):
        # Explicitly set bucket name and credentials from settings
        if not kwargs.get('bucket_name'):
            kwargs['bucket_name'] = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
        if not kwargs.get('access_key'):
            kwargs['access_key'] = getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        if not kwargs.get('secret_key'):
            kwargs['secret_key'] = getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        if not kwargs.get('region_name'):
            kwargs['region_name'] = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
        
        super().__init__(*args, **kwargs)
        
        # Log initialization for debugging (print for immediate visibility)
        print(f"[STORAGE] S3 Storage initialized - Bucket: {self.bucket_name}, Region: {kwargs.get('region_name', 'default')}")
        logger.info(f"S3 Storage initialized - Bucket: {self.bucket_name}, Region: {kwargs.get('region_name', 'default')}")
    
    def save(self, name, content, max_length=None):
        """
        Save file to S3 with error handling and logging
        """
        try:
            logger.info(f"Attempting to save file to S3: {name}")
            saved_name = super().save(name, content, max_length)
            logger.info(f"Successfully saved file to S3: {saved_name}")
            return saved_name
        except Exception as e:
            logger.error(f"Failed to save file to S3: {name}. Error: {str(e)}", exc_info=True)
            # Re-raise the exception so Django knows the upload failed
            raise
    
    def url(self, name):
        """
        Return the URL for the file
        """
        try:
            url = super().url(name)
            logger.debug(f"Generated URL for {name}: {url}")
            return url
        except Exception as e:
            logger.error(f"Failed to generate URL for {name}: {str(e)}", exc_info=True)
            raise
