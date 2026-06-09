"""
Production settings — secure defaults.
"""

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# Auto-detect Render host
RENDER_EXTERNAL_HOSTNAME = env('RENDER_EXTERNAL_HOSTNAME', default='')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

SECRET_KEY = env('SECRET_KEY', default=SECRET_KEY)  # noqa: F405

if env.str('DATABASE_URL', default=''):  # noqa: F405
    DATABASES = {'default': env.db('DATABASE_URL')}  # noqa: F405

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
