from django.conf import settings
from django.core.files.storage import FileSystemStorage
from whitenoise.storage import CompressedManifestStaticFilesStorage
import os

class MediaFilesStorage(FileSystemStorage):
    """
    Custom storage for media files that works with WhiteNoise in production
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location = settings.MEDIA_ROOT
        self.base_url = settings.MEDIA_URL

    def url(self, name):
        """
        Return the URL where the contents of the file referenced by name can be
        accessed.
        """
        # Always use the standard media URL pattern
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