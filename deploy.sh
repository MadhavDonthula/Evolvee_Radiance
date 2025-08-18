#!/bin/bash

# Deployment script for Django app
echo "Starting deployment process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Copy media files to static directory
echo "Copying media files to static directory..."
python manage.py copy_media_to_static

echo "Deployment preparation complete!" 