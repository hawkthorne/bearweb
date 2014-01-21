"""Development settings and globals."""
from base import *  # noqa

import os

# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

DEFAULT_FROM_EMAIL = 'support@stackmachine.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@{}'.format(get_env_var('MAILGUN_DOMAIN'))
EMAIL_HOST_PASSWORD = get_env_var('MAILGUN_PASSWORD')
EMAIL_PORT = 587

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG

# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': os.path.join(SITE_ROOT, 'django_cache'),
    }
}

# See: https://github.com/django-debug-toolbar/django-debug-toolbar

# See: https://github.com/django-debug-toolbar/django-debug-toolbar
INTERNAL_IPS = ('127.0.0.1', )

# See: https://github.com/django-debug-toolbar/django-debug-toolbar

# See: https://github.com/django-debug-toolbar/django-debug-toolbar
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TEMPLATE_CONTEXT': True,
}

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = get_env_var('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_env_var('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_OLD = 'uploads.local.bearraid.com'
AWS_STORAGE_BUCKET_NAME = 'stackmachine-local'

BROKER_URL = 'redis://localhost:6379/0'
