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
        if settings.DEBUG:
            return super().url(name)
        else:
            # In production, serve through static files
            return f"/static/media/{name}" 