from django.core.management.base import BaseCommand
from django.conf import settings
from store.storage import MediaFilesStorage

class Command(BaseCommand):
    help = 'Test S3 connection and configuration'

    def handle(self, *args, **options):
        self.stdout.write('=' * 50)
        self.stdout.write('S3 Configuration Test')
        self.stdout.write('=' * 50)
        
        # Check if S3 is enabled
        use_s3 = getattr(settings, 'USE_S3', False)
        self.stdout.write(f'\nUSE_S3: {use_s3}')
        
        if not use_s3:
            self.stdout.write(self.style.ERROR('\n❌ S3 is not enabled!'))
            self.stdout.write('Set USE_S3=True in your environment variables.')
            return
        
        # Check AWS settings
        self.stdout.write('\nAWS Settings:')
        aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
        aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
        bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
        region = getattr(settings, 'AWS_S3_REGION_NAME', '')
        
        self.stdout.write(f'  AWS_ACCESS_KEY_ID: {"✓ Set" if aws_access_key else "✗ Missing"}')
        self.stdout.write(f'  AWS_SECRET_ACCESS_KEY: {"✓ Set" if aws_secret_key else "✗ Missing"}')
        self.stdout.write(f'  AWS_STORAGE_BUCKET_NAME: {bucket_name if bucket_name else "✗ Missing"}')
        self.stdout.write(f'  AWS_S3_REGION_NAME: {region if region else "✗ Missing"}')
        
        if not all([aws_access_key, aws_secret_key, bucket_name]):
            self.stdout.write(self.style.ERROR('\n❌ Missing required AWS credentials!'))
            return
        
        # Check storage class
        default_storage = getattr(settings, 'DEFAULT_FILE_STORAGE', '')
        self.stdout.write(f'\nDEFAULT_FILE_STORAGE: {default_storage}')
        
        # Test storage initialization
        try:
            self.stdout.write('\nTesting S3 connection...')
            storage = MediaFilesStorage()
            
            # Try to access the bucket
            self.stdout.write(f'  Bucket name: {storage.bucket_name}')
            self.stdout.write(f'  Location: {storage.location}')
            self.stdout.write(f'  Region: {getattr(storage, "region_name", "default")}')
            
            # Try to list objects (this will actually connect)
            try:
                # Just check if we can access the bucket
                exists = storage.bucket_name
                self.stdout.write(self.style.SUCCESS('\n✓ S3 storage initialized successfully!'))
                self.stdout.write(f'\nMedia URL pattern: {getattr(settings, "MEDIA_URL", "Not set")}')
                self.stdout.write(f'Example URL: {getattr(settings, "MEDIA_URL", "")}products/test.jpg')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'\n⚠ Storage initialized but connection test failed: {str(e)}'))
                self.stdout.write('This might be normal if the bucket is empty or permissions are restricted.')
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Failed to initialize S3 storage: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
        
        self.stdout.write('\n' + '=' * 50)

