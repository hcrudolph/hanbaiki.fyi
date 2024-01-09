"""
Django settings for hanbaiki_fyi project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from django.contrib.messages import constants as messages
from pathlib import Path
import os

SITE_ID = 1

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG') == 'TRUE'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'hanbaiki.fyi',
    'www.hanbaiki.fyi'
]

CSRF_TRUSTED_ORIGINS = [
    'https://*.hanbaiki.fyi',
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'photoroll',
    'accounts',
    'sorl.thumbnail',
    'storages',
    'captcha',
    'anymail',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hanbaiki_fyi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hanbaiki_fyi.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Storage
# Custom domain and bucket name need to be defined globally

AWS_S3_CUSTOM_DOMAIN = os.getenv('AWS_S3_CUSTOM_DOMAIN')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_MEDIA_LOCATION = os.getenv('AWS_S3_MEDIA_LOCATION')
AWS_S3_STATIC_LOCATION = os.getenv('AWS_S3_STATIC_LOCATION')
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_S3_STATIC_LOCATION}/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_S3_MEDIA_LOCATION}/"

# Storage Backends

STORAGES = {
    'default': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
            'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'bucket_name': AWS_STORAGE_BUCKET_NAME,
            'default_acl': None,
            'location': AWS_S3_MEDIA_LOCATION,
            'custom_domain': AWS_S3_CUSTOM_DOMAIN,
            'region_name': os.getenv('AWS_S3_REGION'),
            'object_parameters': {'CacheControl': 'max-age=86400'},
        },
    },
    'staticfiles': {
        'BACKEND': 'storages.backends.s3.S3Storage',
        'OPTIONS': {
            'access_key': os.getenv('AWS_ACCESS_KEY_ID'),
            'secret_key': os.getenv('AWS_SECRET_ACCESS_KEY'),
            'bucket_name': AWS_STORAGE_BUCKET_NAME,
            'default_acl': None,
            'location': AWS_S3_STATIC_LOCATION,
            'custom_domain': AWS_S3_CUSTOM_DOMAIN,
            'region_name': os.getenv('AWS_S3_REGION'),
            'object_parameters': {'CacheControl': 'max-age=86400'},
        },
    },
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# django_resized global config

DJANGORESIZED_DEFAULT_SIZE = [1000, 1000]
DJANGORESIZED_DEFAULT_QUALITY = 90
DJANGORESIZED_DEFAULT_KEEP_META = True
DJANGORESIZED_DEFAULT_FORCE_FORMAT = 'JPEG'
DJANGORESIZED_DEFAULT_FORMAT_EXTENSIONS = {'JPEG': ".jpg"}
DJANGORESIZED_DEFAULT_NORMALIZE_ROTATION = False

# Login / Logout behaviour

LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Captcha

CAPTCHA_LENGTH = 6

# Boto3 config

AWS_CONFIG_FILE = os.getenv('AWS_CONFIG_FILE')
AWS_CREDENTIALS = os.getenv('AWS_CREDENTIALS')

# Mapbox API access

MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')

# Email
# Email backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
#EMAIL_BACKEND = 'anymail.backends.mailgun.EmailBackend'

## Email server config
#DEFAULT_FROM_EMAIL = 'noreply@hanbaiki.fyi'
#SERVER_EMAIL = 'root@hanbaiki.fyi'
#EMAIL_HOST = <hostname>
#EMAIL_HOST_PORT = <port>
#EMAIL_USE_TLS = True
#EMAIL_HOST_USER = <sender@domain.tld>
#EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

#ANYMAIL = {
#    'MAILGUN_API_KEY': os.getenv('MAILGUN_ACCESS_TOKEN'),
#    'MAILGUN_SENDER_DOMAIN': 'mg.hanbaiki.fyi',
#}

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
}