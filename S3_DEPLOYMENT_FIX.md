# S3 Not Working on Deployment - Diagnostic Steps

## Problem
- S3 works on localhost ✅
- Admin shows S3 URL ✅  
- But file doesn't appear in S3 bucket ❌

This means the configuration is correct, but the actual upload is failing silently.

## What I Just Fixed

1. **Added explicit credential passing** to storage class
2. **Added error logging** to catch upload failures
3. **Added logging configuration** so errors appear in Render logs

## Next Steps

### 1. Deploy the Updated Code

Commit and push these changes, then redeploy on Render.

### 2. Check Render Logs

After deploying, when you upload an image:

1. Go to Render Dashboard → Your Service → Logs
2. Upload an image via admin
3. Look for these log messages:
   - `"S3 Storage initialized - Bucket: ..."`
   - `"Attempting to save file to S3: ..."`
   - `"Successfully saved file to S3: ..."` OR `"Failed to save file to S3: ..."`

### 3. Common Issues to Check

#### Issue: "Access Denied" or "Forbidden" errors
**Cause**: IAM user doesn't have write permissions

**Fix**:
1. Go to AWS IAM Console
2. Find your IAM user
3. Verify it has `AmazonS3FullAccess` or `PutObject` permission
4. Check that the access keys are active (not expired)

#### Issue: "Bucket does not exist" or "NoSuchBucket"
**Cause**: Bucket name mismatch or wrong region

**Fix**:
1. Verify `AWS_STORAGE_BUCKET_NAME` in Render matches exactly (case-sensitive)
2. Verify `AWS_S3_REGION_NAME` matches your bucket's region
3. Check bucket exists in AWS Console

#### Issue: "InvalidAccessKeyId" or "SignatureDoesNotMatch"
**Cause**: Wrong credentials

**Fix**:
1. Double-check `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` in Render
2. Make sure no extra spaces or quotes
3. Verify keys are for the correct IAM user

#### Issue: No errors in logs, but file still doesn't upload
**Cause**: Storage class might not be used, or silent failure

**Fix**:
1. Check `/debug-s3/` endpoint to verify `DEFAULT_FILE_STORAGE` is set correctly
2. Verify the storage class is being imported correctly
3. Check if there are any middleware or signals interfering

### 4. Test Upload with Logging

After deploying, try uploading an image and watch the logs in real-time:

1. Open Render logs in one tab
2. Upload image in admin in another tab
3. Watch for log messages

### 5. Verify IAM Permissions

The IAM user needs these permissions (minimum):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:PutObjectAcl",
                "s3:GetObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME"
        }
    ]
}
```

Or use `AmazonS3FullAccess` for simplicity (less secure but easier).

### 6. Check Bucket Policy

Your bucket needs to allow public read (for displaying images):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
        }
    ]
}
```

But the IAM user needs write permissions (separate from bucket policy).

## Quick Test

After deploying, check the logs for these messages when uploading:

**Good signs:**
```
INFO S3 Storage initialized - Bucket: your-bucket-name, Region: us-east-1
INFO Attempting to save file to S3: products/test.jpg
INFO Successfully saved file to S3: products/test.jpg
```

**Bad signs:**
```
ERROR Failed to save file to S3: products/test.jpg. Error: Access Denied
ERROR Failed to save file to S3: products/test.jpg. Error: InvalidAccessKeyId
```

## Still Not Working?

1. **Share the error message** from Render logs
2. **Check `/debug-s3/` endpoint** - what does it show?
3. **Verify IAM permissions** - does the user have write access?
4. **Test credentials manually** - can you upload to S3 using AWS CLI with the same credentials?


