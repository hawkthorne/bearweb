"""Production settings and globals."""
from os import environ
import urlparse

from base import *  # noqa

# Normally you should not import ANYTHING from Django directly
# into your settings, but ImproperlyConfigured is an exception.
from django.core.exceptions import ImproperlyConfigured


def get_env_setting(setting):
    """ Get the environment setting or return exception """
    try:
        return environ[setting]
    except KeyError:
        error_msg = "Set the %s env variable" % setting
        raise ImproperlyConfigured(error_msg)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
DEFAULT_FROM_EMAIL = 'support@stackmachine.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@{}'.format(get_env_var('MAILGUN_DOMAIN'))
EMAIL_HOST_PASSWORD = get_env_var('MAILGUN_PASSWORD')
EMAIL_PORT = 587

# See: https://docs.djangoproject.com/en/dev/ref/settings/#server-email
SERVER_EMAIL = EMAIL_HOST_USER

STATICFILES_STORAGE = (
    'django.contrib.staticfiles.storage.CachedStaticFilesStorage'
)

# Enable for CDN
# STATIC_URL = 'https://d2votg94yd3u26.cloudfront.net/static/'
STATIC_URL = '/static/'

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

RAVEN_CONFIG = {
    'dsn': get_env_var('SENTRY_DSN'),
}

redis_url = urlparse.urlparse(get_env_setting('REDISCLOUD_URL'))

CACHES = {
    'default': {
        'BACKEND': 'redis_cache.RedisCache',
        'LOCATION': '%s:%s' % (redis_url.hostname, redis_url.port),
        'OPTIONS': {'PASSWORD': redis_url.password, 'DB': 0},
    }
}

CONN_MAX_AGE = 600

MIXPANEL_API_TOKEN = get_env_setting('MIXPANEL_API_TOKEN')
BROKER_URL = get_env_setting('REDISCLOUD_URL')

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


MIDDLEWARE_CLASSES = ('core.middleware.SSLifyMiddleware',) + \
    MIDDLEWARE_CLASSES

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = get_env_var('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = get_env_var('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'cloud.stackmachine.com'

# FIXME
SECURE_HOSTNAME = 'https://bearweb.herokuapp.com'
INSECURE_HOSTNAME = 'http://bearweb.herokuapp.com'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = get_env_setting('SECRET_KEY')
OLARK = True
