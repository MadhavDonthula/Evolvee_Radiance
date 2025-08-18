import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage

class Command(BaseCommand):
    help = 'Copy media files to static files directory for production deployment'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        static_root = settings.STATIC_ROOT
        
        if not os.path.exists(static_root):
            os.makedirs(static_root)
        
        # Create media directory in static files
        static_media_dir = os.path.join(static_root, 'media')
        if not os.path.exists(static_media_dir):
            os.makedirs(static_media_dir)
        
        # Copy all media files to static files
        if os.path.exists(media_root):
            for root, dirs, files in os.walk(media_root):
                # Calculate relative path
                rel_path = os.path.relpath(root, media_root)
                if rel_path == '.':
                    rel_path = ''
                
                # Create corresponding directory in static files
                static_dir = os.path.join(static_media_dir, rel_path)
                if not os.path.exists(static_dir):
                    os.makedirs(static_dir)
                
                # Copy files
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(static_dir, file)
                    shutil.copy2(src_file, dst_file)
                    self.stdout.write(f'Copied: {src_file} -> {dst_file}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully copied media files to static directory')
        ) 