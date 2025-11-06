# S3 Troubleshooting Guide

## Issues Fixed

1. **URLs Configuration**: Fixed `urls.py` to not try serving media files statically when using S3
2. **Storage Class**: Updated storage class to properly initialize with AWS credentials
3. **Environment Variable Parsing**: Made `USE_S3` parsing case-insensitive and more flexible
4. **Validation**: Added validation to ensure all required S3 credentials are present

## Checklist for Render Deployment

### 1. Verify Environment Variables in Render

Go to your Render dashboard → Your Service → Environment tab and ensure these are set:

- ✅ `USE_S3` = `True` (or `true`, `1`, `yes`, `on` - case-insensitive)
- ✅ `AWS_ACCESS_KEY_ID` = Your access key (starts with `AKIA...`)
- ✅ `AWS_SECRET_ACCESS_KEY` = Your secret access key
- ✅ `AWS_STORAGE_BUCKET_NAME` = Your bucket name (e.g., `evolvee-radiance-media`)
- ✅ `AWS_S3_REGION_NAME` = Your bucket region (e.g., `us-east-1`)

**Important**: Make sure there are NO extra spaces or quotes around the values!

### 2. Verify S3 Bucket Configuration

1. **Bucket exists and is accessible**
   - Go to AWS S3 Console
   - Verify your bucket exists
   - Check the bucket name matches exactly (case-sensitive)

2. **Bucket permissions**
   - Go to Permissions tab
   - Verify "Block public access" is OFF
   - Verify bucket policy allows public read access

3. **IAM User permissions**
   - Go to IAM Console
   - Verify your IAM user has `AmazonS3FullAccess` or appropriate permissions
   - Verify the access keys are active

### 3. Test Image Upload

1. **Upload via Admin**
   - Go to your deployed admin panel
   - Upload a product or category image
   - Check the browser console for any errors

2. **Check S3 Bucket**
   - Go to AWS S3 Console
   - Navigate to your bucket
   - Check if files appear in the `media/` folder
   - Click on a file and verify it's publicly accessible

3. **Check Image URL**
   - In Django admin, after uploading, check the image URL
   - It should be: `https://your-bucket-name.s3.amazonaws.com/media/products/filename.png`
   - Try opening that URL directly in a browser

### 4. Common Issues and Solutions

#### Issue: Images upload but don't display
**Solution**: 
- Check bucket permissions (public read access)
- Verify CORS configuration if needed
- Check browser console for CORS errors

#### Issue: "Access Denied" errors
**Solution**:
- Verify IAM user has correct permissions
- Check that access keys are correct in Render environment variables
- Verify bucket policy allows public read

#### Issue: "Bucket does not exist" errors
**Solution**:
- Verify bucket name matches exactly (case-sensitive)
- Check that bucket is in the correct region
- Verify `AWS_S3_REGION_NAME` matches your bucket's region

#### Issue: Environment variables not being read
**Solution**:
- In Render, make sure environment variables are set at the Service level (not just in render.yaml)
- Redeploy after adding/changing environment variables
- Check Render logs for any configuration errors

### 5. Debug Steps

1. **Check Render Logs**
   - Go to Render dashboard → Your Service → Logs
   - Look for any errors related to S3 or storage
   - Check for "ValueError" about missing credentials

2. **Test Locally First**
   - Set up `.env` file with same credentials
   - Test image upload locally
   - If it works locally but not on Render, it's an environment variable issue

3. **Verify Settings Are Loaded**
   - Add temporary logging in `settings.py`:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   if USE_S3:
       logger.info(f"S3 enabled. Bucket: {AWS_STORAGE_BUCKET_NAME}")
   ```
   - Check Render logs to see if this message appears

### 6. Quick Test Script

You can add this to a Django management command to test S3 connection:

```python
from django.core.management.base import BaseCommand
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class Command(BaseCommand):
    def handle(self, *args, **options):
        if not settings.USE_S3:
            self.stdout.write(self.style.ERROR('S3 is not enabled'))
            return
        
        try:
            storage = S3Boto3Storage()
            # Try to list bucket contents
            storage.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            self.stdout.write(self.style.SUCCESS('S3 connection successful!'))
            self.stdout.write(f'Bucket: {settings.AWS_STORAGE_BUCKET_NAME}')
            self.stdout.write(f'Region: {settings.AWS_S3_REGION_NAME}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'S3 connection failed: {str(e)}'))
```

Run with: `python manage.py test_s3`

## Still Having Issues?

1. Double-check all environment variables in Render
2. Verify bucket permissions in AWS Console
3. Check Render deployment logs for errors
4. Test with a simple image upload
5. Verify the image URL format matches: `https://bucket-name.s3.amazonaws.com/media/...`

