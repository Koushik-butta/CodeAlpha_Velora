"""
Shared Django settings for Velora.
"""

from pathlib import Path

import environ

# Project root (parent of velora package)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env
environ.Env.read_env(BASE_DIR / '.env', overwrite=True)

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, []),
    OTP_EXPIRY_MINUTES=(int, 10),
    OTP_MAX_ATTEMPTS=(int, 5),
)

SECRET_KEY = env('SECRET_KEY', default='django-insecure-dev-only-change-in-env')

DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.humanize',  # ADD THIS

    'cloudinary_storage',
    'cloudinary',
    'users',
    'shop',
    'cart',
    'swap',
    'notifications',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'velora.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'velora' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'shop.context_processors.velora_global_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'velora.wsgi.application'

AUTH_USER_MODEL = 'users.User'

# PostgreSQL via DATABASE_URL or discrete PG* variables
if env.str('DATABASE_URL', default=''):
    DATABASES = {'default': env.db('DATABASE_URL')}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': env('PGHOST', default='localhost'),
            'PORT': env('PGPORT', default='5432'),
            'NAME': env('PGDATABASE', default='velora_db'),
            'USER': env('PGUSER', default='velora_user'),
            'PASSWORD': env('PGPASSWORD', default=''),
        }
    }

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'

STORAGES = {
    'default': {
        'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': env('CLOUDINARY_CLOUD_NAME', default=''),
    'API_KEY': str(env('CLOUDINARY_API_KEY', default='')),
    'API_SECRET': env('CLOUDINARY_API_SECRET', default=''),
}

# Brevo (email / OTP)
BREVO_API_KEY = env('BREVO_API_KEY', default='')
BREVO_SENDER_EMAIL = env('BREVO_SENDER_EMAIL', default='noreply@example.com')
BREVO_SENDER_NAME = env('BREVO_SENDER_NAME', default='Velora')

OTP_EXPIRY_MINUTES = env.int('OTP_EXPIRY_MINUTES')
OTP_MAX_ATTEMPTS = env.int('OTP_MAX_ATTEMPTS')

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
