from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class MediaFilesStorage(S3Boto3Storage):
    """
    Custom storage for media files using S3.
    This will be used when USE_S3=True in settings.
    django-storages automatically reads AWS_* settings from Django settings.
    """
    location = 'media'
    file_overwrite = False
    default_acl = 'public-read'
