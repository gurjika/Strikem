"""
Django settings for poolhub project.

Generated by 'django-admin startproject' using Django 5.0.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from datetime import timedelta
import os
from pathlib import Path
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['134.122.88.48', 'strikem.site', '127.0.0.1', 'localhost', 'strikem.vercel.app']


# Application definition

INSTALLED_APPS = [
    'daphne',
    # "debug_toolbar",
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'channels',
    'core',
    'poolstore',
    'poolstore_api',
    'django_htmx',
    'django_extensions',
    'django_filters',
    'drf_yasg',
    "corsheaders",
    'django_celery_beat'
]

MIDDLEWARE = [
    
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True


ROOT_URLCONF = 'poolhub.urls'

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

WSGI_APPLICATION = 'poolhub.wsgi.application'

# DB_PASSWORD = os.environ.get('DB_PASSWORD')
# DB_HOST = os.environ.get('DB_HOST', '127.0.0.1')


REMOTE_DB_HOST = os.environ.get('REMOTE_DB_HOST')
REMOTE_DB_PORT = os.environ.get('REMOTE_DB_PORT')
REMOTE_DB_PASSWORD = os.environ.get('REMOTE_DB_PASSWORD')
REMOTE_DB_NAME = os.environ.get('REMOTE_DB_NAME')
REMOTE_DB_USER = os.environ.get('REMOTE_DB_USER')

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'strikem',
        'USER': 'admin',
        'PASSWORD': 'mysqlpassword',
        'HOST': 'database-1.chw2ywc68gw1.eu-west-1.rds.amazonaws.com',   
        'PORT': 3306
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'poolhub',
#         'USER': 'root',
#         'PASSWORD': DB_PASSWORD,
#         'HOST': 'mysql',   
#     }
# }


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

TIME_ZONE = 'Asia/Tbilisi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/


# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'






# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'core.user'


ASGI_APPLICATION = 'poolhub.asgi.application'


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("elasticache-strikem.mkl1yv.ng.0001.euw1.cache.amazonaws.com", 6379)],
        },
    },
}

# INTERNAL_IPS = [
#     # ...
#     "127.0.0.1",
#     # ...
# ]


# DEBUG_TOOLBAR_CONFIG = {
#     'SHOW_TOOLBAR_CALLBACK': lambda request:True,
# }

LOGIN_URL = 'login'


from django.contrib.messages import constants as messages
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}


CSRF_TRUSTED_ORIGINS = [
    "https://strikem.site",
]

TIME_ZONE = 'Asia/Tbilisi'

CELERY_BROKER_URL = 'redis://redis:6379/1'


REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

}

SIMPLE_JWT = {
   'AUTH_HEADER_TYPES': ('JWT',),
   'ACCESS_TOKEN_LIFETIME': timedelta(days=1)
}







DJOSER = {
    'SERIALIZERS': {
        'user_create': 'core.serializers.UserCreateSerializer',
        'current_user': 'core.serializers.UserSerializer'
    },

    'ACTIVATION_URL': 'activate/{uid}/{token}/',
    'SEND_ACTIVATION_EMAIL': True,
    'EMAIL': {
        'activation': 'poolstore.email.CustomActivationEmail',
    }

    
}







EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'luka.gurjidze04@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'noreply@poolhub.com'









# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://elasticache-strikem.mkl1yv.ng.0001.euw1.cache.amazonaws.com:6379/2', 
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}


STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')



STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')


AWS_S3_CUSTOM_DOMAIN = 'd2fa3ckosxh4zl.cloudfront.net'
CELERY_RESULT_BACKEND = 'redis://elasticache-strikem.mkl1yv.ng.0001.euw1.cache.amazonaws.com:6379/1'

# AWS_CLOUDFRONT_KEY_ID = os.environ.get('AWS_CLOUDFRONT_KEY_ID')
# AWS_CLOUDFRONT_KEY = os.environ.get('AWS_CLOUDFRONT_KEY').encode('ascii').strip()

# print(AWS_CLOUDFRONT_KEY)


# CELERY_BEAT_SCHEDULE = {
#     'delete_outdated_notifications': {
#         'task': 'poolstore.tasks.delete_outdated_notifications',
#         'schedule': crontab(hour=0, minute=0)
#     }
# }


GOOGLE_OAUTH2_CLIENT_ID=os.environ.get('GOOGLE_OAUTH2_CLIENT_ID')
GOOGLE_OAUTH2_CLIENT_SECRET=os.environ.get('GOOGLE_OAUTH2_CLIENT_SECRET')
GOOGLE_OAUTH2_PROJECT_ID=os.environ.get('GOOGLE_OAUTH2_PROJECT_ID')
GOOGLE_OAUTH2_CLIENT_ID_F=os.environ.get('GOOGLE_OAUTH2_CLIENT_ID_F')


BASE_BACKEND_URL = 'https://strikem.site'


