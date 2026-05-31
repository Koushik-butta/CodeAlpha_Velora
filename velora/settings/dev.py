"""
Development settings — DEBUG on, loads .env from project root.
"""

from .base import *  # noqa: F403

DEBUG = True

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])  # noqa: F405

environ.Env.read_env(BASE_DIR / '.env')  # noqa: F405

# Re-read secrets and DB after .env is loaded
SECRET_KEY = env('SECRET_KEY', default=SECRET_KEY)  # noqa: F405

if env.bool('USE_SQLITE_DEV', default=False):  # noqa: F405
    DATABASES = {  # noqa: F405
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',  # noqa: F405
        }
    }
elif env.str('DATABASE_URL', default=''):  # noqa: F405
    DATABASES = {'default': env.db('DATABASE_URL')}  # noqa: F405
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': env('PGHOST', default='localhost'),  # noqa: F405
            'PORT': env('PGPORT', default='5432'),  # noqa: F405
            'NAME': env('PGDATABASE', default='velora_db'),  # noqa: F405
            'USER': env('PGUSER', default='velora_user'),  # noqa: F405
            'PASSWORD': env('PGPASSWORD', default=''),  # noqa: F405
        }
    }


BREVO_API_KEY = env('BREVO_API_KEY', default='')  # noqa: F405
BREVO_SENDER_EMAIL = env('BREVO_SENDER_EMAIL', default=BREVO_SENDER_EMAIL)  # noqa: F405
BREVO_SENDER_NAME = env('BREVO_SENDER_NAME', default=BREVO_SENDER_NAME)  # noqa: F405

OTP_EXPIRY_MINUTES = env.int('OTP_EXPIRY_MINUTES')  # noqa: F405
OTP_MAX_ATTEMPTS = env.int('OTP_MAX_ATTEMPTS')  # noqa: F405

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
