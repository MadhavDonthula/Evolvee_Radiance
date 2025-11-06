# AWS S3 Setup Guide for Evolvée Radiance

This guide will walk you through setting up AWS S3 to store your media files (product images, category images) so they persist after deployment.

## Step 1: Create an S3 Bucket

1. **Log in to AWS Console**
   - Go to https://aws.amazon.com/console/
   - Sign in with your AWS account

2. **Navigate to S3**
   - Search for "S3" in the AWS services search bar
   - Click on "S3" service

3. **Create a New Bucket**
   - Click "Create bucket"
   - **Bucket name**: Choose a unique name (e.g., `evolvee-radiance-media` or `your-company-media-bucket`)
   - **AWS Region**: Choose a region close to your users (e.g., `us-east-1`, `us-west-2`)
   - **Object Ownership**: Select "ACLs enabled" and "Bucket owner preferred"
   - **Block Public Access settings**: **UNCHECK** "Block all public access" (you need public access for images)
     - Check the acknowledgment checkbox
   - **Bucket Versioning**: Disable (unless you need versioning)
   - **Default encryption**: Enable (recommended)
   - Click "Create bucket"

## Step 2: Configure Bucket Permissions

1. **Open your bucket** (click on the bucket name)

2. **Go to Permissions tab**
   - Scroll down to "Bucket policy"
   - Click "Edit"

3. **Add Bucket Policy** (replace `YOUR-BUCKET-NAME` with your actual bucket name):
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
   - Click "Save changes"

4. **CORS Configuration** (if needed for cross-origin requests):
   - In the Permissions tab, scroll to "Cross-origin resource sharing (CORS)"
   - Click "Edit" and add:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
       "AllowedOrigins": ["*"],
       "ExposeHeaders": []
     }
   ]
   ```
   - Click "Save changes"

## Step 3: Create IAM User for S3 Access

1. **Navigate to IAM**
   - Search for "IAM" in AWS services
   - Click on "IAM" service

2. **Create a New User**
   - Click "Users" in the left sidebar
   - Click "Create user"
   - **User name**: `evolvee-radiance-s3-user` (or any name you prefer)
   - Click "Next"

3. **Set Permissions**
   - Select "Attach policies directly"
   - Search for and select: **`AmazonS3FullAccess`** (or create a more restrictive policy)
   - Click "Next"
   - Click "Create user"

4. **Create Access Keys**
   - Click on the user you just created
   - Go to "Security credentials" tab
   - Scroll to "Access keys"
   - Click "Create access key"
   - Select "Application running outside AWS"
   - Click "Next"
   - Add a description (optional): "Django media files storage"
   - Click "Create access key"
   - **IMPORTANT**: Copy both:
     - **Access key ID** (starts with `AKIA...`)
     - **Secret access key** (click "Show" to reveal)
   - **Save these securely** - you won't be able to see the secret key again!

## Step 4: Configure Environment Variables

### For Local Development (.env file)

Create or update your `.env` file in the project root:

```env
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key-id-here
AWS_SECRET_ACCESS_KEY=your-secret-access-key-here
AWS_STORAGE_BUCKET_NAME=your-bucket-name-here
AWS_S3_REGION_NAME=us-east-1
```

**Note**: Make sure `.env` is in your `.gitignore` file to keep credentials secure!

### For Production (Vercel/Render)

Add these as environment variables in your deployment platform:

**For Vercel:**
1. Go to your project settings
2. Navigate to "Environment Variables"
3. Add each variable:
   - `USE_S3` = `True`
   - `AWS_ACCESS_KEY_ID` = `your-access-key-id`
   - `AWS_SECRET_ACCESS_KEY` = `your-secret-access-key`
   - `AWS_STORAGE_BUCKET_NAME` = `your-bucket-name`
   - `AWS_S3_REGION_NAME` = `us-east-1` (or your chosen region)

**For Render:**
1. Go to your service dashboard
2. Navigate to "Environment" tab
3. Add each environment variable (same as above)

## Step 5: Install Dependencies

The required packages are already in `requirements.txt`:
- `django-storages`
- `boto3`

Install them:
```bash
pip install -r requirements.txt
```

## Step 6: Test the Setup

1. **Run migrations** (if needed):
   ```bash
   python manage.py migrate
   ```

2. **Start your development server**:
   ```bash
   python manage.py runserver
   ```

3. **Test image upload**:
   - Go to Django admin
   - Upload a product image or category image
   - Check your S3 bucket - you should see the file in the `media/` folder
   - The image URL should be something like: `https://your-bucket-name.s3.amazonaws.com/media/products/image.png`

## Step 7: Migrate Existing Images (Optional)

If you have existing images in your local `media/` folder that you want to move to S3:

1. **Install django-extensions** (optional, for management command):
   ```bash
   pip install django-extensions
   ```

2. **Or manually upload**:
   - Use AWS Console to upload files
   - Or use a script to sync files to S3

## Troubleshooting

### Images not showing up
- Check that `USE_S3=True` in your environment variables
- Verify AWS credentials are correct
- Check bucket permissions (public read access)
- Verify bucket name matches exactly

### Permission errors
- Ensure IAM user has `AmazonS3FullAccess` or appropriate permissions
- Check bucket policy allows public read access

### CORS errors
- Update CORS configuration in S3 bucket settings
- Ensure your domain is in the allowed origins

## Security Best Practices

1. **Never commit credentials** to git
2. **Use IAM roles** instead of access keys when possible (for EC2/ECS)
3. **Restrict IAM policies** to only necessary S3 operations (read/write to specific bucket)
4. **Enable bucket versioning** if you need to recover deleted files
5. **Set up CloudFront** (optional) for CDN and better performance

## Cost Considerations

- S3 storage is very cheap (~$0.023 per GB/month)
- Data transfer out (serving images) has a free tier (first 1GB/month free)
- For most small-to-medium sites, costs are minimal (< $1/month)

## Next Steps

After setup:
1. Deploy your changes
2. Test image uploads in production
3. Monitor S3 bucket usage in AWS Console
4. Consider setting up CloudFront CDN for better performance (optional)

---

**Need Help?**
- AWS S3 Documentation: https://docs.aws.amazon.com/s3/
- Django Storages Documentation: https://django-storages.readthedocs.io/

