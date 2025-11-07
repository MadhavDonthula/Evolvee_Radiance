# Debugging S3 Issues on Render

## Quick Diagnostic Steps

### 1. Check Render Environment Variables

In Render Dashboard → Your Service → Environment tab, verify these EXACT variable names (case-sensitive):

- `USE_S3` (value: `True` or `true`)
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_REGION_NAME`

**Common mistakes:**
- ❌ Extra spaces: `USE_S3 = True` (should be `USE_S3=True`)
- ❌ Quotes around values: `USE_S3="True"` (should be `USE_S3=True`)
- ❌ Wrong variable name: `USE_S3_BUCKET` instead of `AWS_STORAGE_BUCKET_NAME`

### 2. Check Render Logs

After deploying, check the logs for:
- Any errors about missing AWS credentials
- Warnings about S3 falling back to local storage
- Any import errors related to `storages` or `boto3`

Look for lines like:
```
S3 is enabled but required AWS credentials are missing
```

### 3. Test S3 Configuration

Add this to a view temporarily to check settings (remove after debugging):

```python
# In store/views.py, add a debug view
from django.http import JsonResponse
from django.conf import settings

def debug_s3(request):
    data = {
        'USE_S3': getattr(settings, 'USE_S3', False),
        'AWS_ACCESS_KEY_ID': 'Set' if getattr(settings, 'AWS_ACCESS_KEY_ID', '') else 'Missing',
        'AWS_SECRET_ACCESS_KEY': 'Set' if getattr(settings, 'AWS_SECRET_ACCESS_KEY', '') else 'Missing',
        'AWS_STORAGE_BUCKET_NAME': getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Missing'),
        'AWS_S3_REGION_NAME': getattr(settings, 'AWS_S3_REGION_NAME', 'Missing'),
        'DEFAULT_FILE_STORAGE': getattr(settings, 'DEFAULT_FILE_STORAGE', 'Missing'),
        'MEDIA_URL': getattr(settings, 'MEDIA_URL', 'Missing'),
    }
    return JsonResponse(data)
```

Then add to `store/urls.py`:
```python
path('debug-s3/', views.debug_s3, name='debug_s3'),
```

Visit `https://your-site.onrender.com/debug-s3/` to see the configuration.

### 4. Verify S3 Bucket

1. Go to AWS S3 Console
2. Find your bucket
3. Check Permissions tab:
   - Block public access: **OFF**
   - Bucket policy allows public read
4. Try uploading a test file manually to `media/products/test.jpg`
5. Try accessing it: `https://your-bucket.s3.amazonaws.com/media/products/test.jpg`

### 5. Test Image Upload

1. Go to admin panel on deployed site
2. Upload a new product image
3. Check:
   - Does it appear in S3 bucket?
   - What URL does Django show for the image?
   - Can you access that URL directly?

### 6. Common Issues

#### Issue: Images upload but URLs are wrong
**Symptom**: Image appears in S3 but URL is `/media/products/image.jpg` instead of S3 URL

**Solution**: Check that `DEFAULT_FILE_STORAGE` is set to `'store.storage.MediaFilesStorage'` when `USE_S3=True`

#### Issue: "Access Denied" when accessing S3 URLs
**Solution**: 
- Check bucket permissions (public read access)
- Verify bucket policy
- Check IAM user permissions

#### Issue: Environment variables not being read
**Solution**:
- Make sure variables are set at Service level (not just in render.yaml)
- Redeploy after adding variables
- Check for typos in variable names
- Ensure no extra spaces or quotes

#### Issue: Images work locally but not on Render
**Solution**:
- Verify environment variables are set in Render (not just in local .env)
- Check Render logs for errors
- Make sure `USE_S3=True` in Render environment

## Still Not Working?

1. **Run the test command** (if you have shell access):
   ```bash
   python manage.py test_s3
   ```

2. **Check if boto3 is installed**:
   ```bash
   pip list | grep boto3
   pip list | grep django-storages
   ```

3. **Verify the storage class is being used**:
   - Check that uploaded images have S3 URLs (not local paths)
   - Look at the image URL in Django admin after upload

4. **Check AWS credentials**:
   - Verify IAM user has `AmazonS3FullAccess`
   - Check that access keys are active (not expired/revoked)

