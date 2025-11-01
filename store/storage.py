from django.conf import settings
from django.core.files.storage import FileSystemStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage
import os

class MediaFilesStorage(FileSystemStorage):
    """
    Custom storage for media files that works with WhiteNoise in production.
    In production, serves files from /static/media/ instead of /media/
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location = settings.MEDIA_ROOT
        # In production, serve from /static/media/ instead of /media/
        if not settings.DEBUG:
            self.base_url = '/static/media/'
        else:
            self.base_url = settings.MEDIA_URL

    def url(self, name):
        """
        Return the URL where the contents of the file referenced by name can be
        accessed. In production, use /static/media/ path.
        """
        return super().url(name)
            
    def exists(self, name):
        """
        Check if file exists in both media and static directories
        """
        # First check in media directory
        if super().exists(name):
            return True
        
        # Then check in static directory for production
        if not settings.DEBUG:
            static_path = os.path.join(settings.STATIC_ROOT, 'media', name)
            return os.path.exists(static_path)
        
        return False
    
    def save(self, name, content, max_length=None):
        """
        Save the file to the media directory and copy to static for production
        """
        # Read content before saving (since content may be a file-like object that gets consumed)
        if hasattr(content, 'read'):
            content_data = content.read()
            # Reset content pointer if possible
            if hasattr(content, 'seek'):
                content.seek(0)
            # Create a new file-like object with the data
            from io import BytesIO
            content = BytesIO(content_data)
        
        # Save to media directory first
        saved_name = super().save(name, content, max_length)
        
        # In production, also save to static directory
        if not settings.DEBUG:
            static_media_dir = os.path.join(settings.STATIC_ROOT, 'media')
            static_path = os.path.join(static_media_dir, saved_name)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(static_path), exist_ok=True)
            
            # Copy file from media to static directory
            media_path = os.path.join(settings.MEDIA_ROOT, saved_name)
            if os.path.exists(media_path):
                with open(media_path, 'rb') as src:
                    with open(static_path, 'wb') as dst:
                        dst.write(src.read())
        
        return saved_name 