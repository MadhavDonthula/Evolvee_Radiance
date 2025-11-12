# import os
# from pathlib import Path
# import environ

# # Initialize environment variables
# env = environ.Env(
#     DEBUG=(bool, False)
# )
# environ.Env.read_env(os.path.join(Path(__file__).resolve().parent.parent, '.env'))

# BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET_KEY = env('SECRET_KEY')
# DEBUG = env('DEBUG')
# ALLOWED_HOSTS = ['*']

# # Application definition
# INSTALLED_APPS = [
#     "django.contrib.admin",
#     "django.contrib.auth",
#     "django.contrib.contenttypes",
#     "django.contrib.sessions",
#     "django.contrib.messages",
#     "django.contrib.staticfiles",
#     "store",
# ]

# MIDDLEWARE = [
#     "django.middleware.security.SecurityMiddleware",
#     "whitenoise.middleware.WhiteNoiseMiddleware",  # Must be just after SecurityMiddleware
#     "django.contrib.sessions.middleware.SessionMiddleware",
#     "django.middleware.common.CommonMiddleware",
#     "django.middleware.csrf.CsrfViewMiddleware",
#     "django.contrib.auth.middleware.AuthenticationMiddleware",
#     "django.contrib.messages.middleware.MessageMiddleware",
#     "django.middleware.clickjacking.XFrameOptionsMiddleware",
# ]

# ROOT_URLCONF = "lip_products.urls"

# TEMPLATES = [
#     {
#         "BACKEND": "django.template.backends.django.DjangoTemplates",
#         "DIRS": [BASE_DIR / "templates"],
#         "APP_DIRS": True,
#         "OPTIONS": {
#             "context_processors": [
#                 "django.template.context_processors.debug",
#                 "django.template.context_processors.request",
#                 "django.contrib.auth.context_processors.auth",
#                 "django.contrib.messages.context_processors.messages",
#             ],
#         },
#     },
# ]

# WSGI_APPLICATION = "lip_products.wsgi.application"

# # Database
# DATABASES = {
#     "default": env.db(),
# }

# # Password validation
# AUTH_PASSWORD_VALIDATORS = [
#     {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
#     {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
#     {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
#     {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
# ]

# # Internationalization
# LANGUAGE_CODE = "en-us"
# TIME_ZONE = "UTC"
# USE_I18N = True
# USE_TZ = True

# # Static files (CSS, JS, Images)
# STATIC_URL = "/static/"
# STATICFILES_DIRS = [BASE_DIR / "static"]
# STATIC_ROOT = BASE_DIR / "staticfiles"

# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# # Media files
# MEDIA_URL = "/media/"
# MEDIA_ROOT = BASE_DIR / "media"

# # Default primary key field type
# DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"






#### NEWW####

import os
import logging
from pathlib import Path
import environ
import dj_database_url

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Read .env file if it exists (for local development)
env_file = os.path.join(Path(__file__).resolve().parent.parent, '.env')
if os.path.exists(env_file):
    environ.Env.read_env(env_file)

BASE_DIR = Path(__file__).resolve().parent.parent

# Get sensitive data from environment variables with hardcoded fallbacks
SECRET_KEY = env('SECRET_KEY', default='ys-optx20q8kkmq$6z_z2dh6($d7y=@2q7b%_yzv20+fke*i05')
DEBUG = env('DEBUG', default=True)

# Handle ALLOWED_HOSTS for Render deployment
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "storages",  # For S3 storage
    "store",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    'django.middleware.csrf.CsrfViewMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "lip_products.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'store.context_processors.categories',
            ],
        },
    },
]

WSGI_APPLICATION = "lip_products.wsgi.application"

# Database configuration with hardcoded fallback
DATABASE_URL = env('DATABASE_URL', default='postgresql://evolveeradiance_user:3mxBgJwmpONRRt04WU1xJ6dJmyZPcSzG@dpg-ctrkg49opnds73dt1j90-a.virginia-postgres.render.com/evolveeradiance')

# Use dj_database_url to parse the URL properly
DATABASES = {
    'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files configuration for Render
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# Use WhiteNoise for static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files configuration - Use S3 in production, local in development
# Check USE_S3 environment variable (case-insensitive)
USE_S3_STR = env('USE_S3', default='False').strip().lower()
USE_S3 = USE_S3_STR in ('true', '1', 'yes', 'on')

# Log S3 configuration status at startup (print for immediate visibility)
print(f"[SETTINGS] S3 Configuration Check - USE_S3_STR: '{USE_S3_STR}', USE_S3: {USE_S3}")
settings_logger = logging.getLogger(__name__)
settings_logger.info(f"S3 Configuration Check - USE_S3_STR: '{USE_S3_STR}', USE_S3: {USE_S3}")

if USE_S3:
    # AWS S3 settings - read from environment
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='us-east-1')
    
    # Log what we got from environment
    print(f"[SETTINGS] AWS_ACCESS_KEY_ID: {'Set' if AWS_ACCESS_KEY_ID else 'Missing'}")
    print(f"[SETTINGS] AWS_SECRET_ACCESS_KEY: {'Set' if AWS_SECRET_ACCESS_KEY else 'Missing'}")
    print(f"[SETTINGS] AWS_STORAGE_BUCKET_NAME: {AWS_STORAGE_BUCKET_NAME if AWS_STORAGE_BUCKET_NAME else 'Missing'}")
    settings_logger.info(f"AWS_ACCESS_KEY_ID: {'Set' if AWS_ACCESS_KEY_ID else 'Missing'}")
    settings_logger.info(f"AWS_SECRET_ACCESS_KEY: {'Set' if AWS_SECRET_ACCESS_KEY else 'Missing'}")
    settings_logger.info(f"AWS_STORAGE_BUCKET_NAME: {AWS_STORAGE_BUCKET_NAME if AWS_STORAGE_BUCKET_NAME else 'Missing'}")
    
    # Validate that required S3 settings are provided
    if all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME]):
        # All credentials present - configure S3
        print("[SETTINGS] All S3 credentials present - configuring S3 storage")
        settings_logger.info("All S3 credentials present - configuring S3 storage")
        AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
        AWS_S3_OBJECT_PARAMETERS = {
            'CacheControl': 'max-age=86400',
        }
        AWS_DEFAULT_ACL = 'public-read'
        AWS_S3_FILE_OVERWRITE = False
        AWS_QUERYSTRING_AUTH = False
        
        # S3 endpoint URL (for certain regions)
        if AWS_S3_REGION_NAME in ['us-east-1']:
            AWS_S3_ENDPOINT_URL = None  # Use default
        else:
            AWS_S3_ENDPOINT_URL = f'https://s3.{AWS_S3_REGION_NAME}.amazonaws.com'
        
        # S3 static files settings 
        # STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
        
        # S3 media files settings
        DEFAULT_FILE_STORAGE = 'store.storage.MediaFilesStorage'
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
        MEDIA_ROOT = ''
    else:
        # Missing credentials - fall back to local storage
        settings_logger.warning(
            "S3 is enabled but required AWS credentials are missing. "
            "Please set AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_STORAGE_BUCKET_NAME. "
            "Falling back to local storage."
        )
        USE_S3 = False
        # Fall through to local storage configuration below

if not USE_S3:
    # Local media files configuration (for development)
    print("[SETTINGS] Using local file storage (not S3)")
    settings_logger.info("Using local file storage (not S3)")
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / "media"
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

LOGIN_URL = "/login/"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security settings for production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# Email settings for contact form
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'mdonthula98@gmail.com'
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='numk eoez sifm tnnz')  # Use an App Password, not your Gmail password!
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Logging configuration for S3 debugging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'store.storage': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'lip_products.settings': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}

# Partner QR Code Configuration
# This determines the URL used in QR codes
if os.environ.get('RENDER'):
    # Production on Render
    SITE_URL = 'https://evolveeradiance.com'
else:
    # Local development
    SITE_URL = 'http://localhost:8000'