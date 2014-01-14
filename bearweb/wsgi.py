"""
WSGI config for stackmachine project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
from os.path import abspath, dirname
from sys import path

import static
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
from django.core.handlers.base import get_path_info
from django.contrib.staticfiles.handlers import StaticFilesHandler
from paste.gzipper import GzipResponse

try:
    from urllib.parse import urlparse
except ImportError:  # Python 2
    from urlparse import urlparse

from django.contrib.staticfiles import utils

SITE_ROOT = dirname(dirname(abspath(__file__)))
path.append(SITE_ROOT)


class Cling(WSGIHandler):
    """
    WSGI middleware that intercepts calls to the static files
    directory, as defined by the STATIC_URL setting, and serves
    those files.
    """

    def __init__(self, application, base_dir=None):
        self.application = application
        if not base_dir:
            base_dir = self.get_base_dir()
        self.base_url = urlparse(self.get_base_url())

        self.cling = static.Cling(base_dir)
        self.debug_cling = StaticFilesHandler(base_dir)

        super(Cling, self).__init__()

    def get_base_dir(self):
        return settings.STATIC_ROOT

    def get_base_url(self):
        utils.check_settings()
        # TODO: Don't hardcode this value
        return '/static/'

    @property
    def debug(self):
        return settings.DEBUG

    def _transpose_environ(self, environ):
        """Translates a given environ to static.Cling's expectations."""
        environ['PATH_INFO'] = environ['PATH_INFO'][len(self.base_url[2]) - 1:]
        return environ

    def _should_handle(self, path):
        """Checks if the path should be handled. Ignores the path if:
        * the host is provided as part of the base_url
        * the request's path isn't under the media path (or equal)
        """
        return path.startswith(self.base_url[2]) and not self.base_url[1]

    def _gzip(self, app, environ, start_response):
        if 'gzip' not in environ.get('HTTP_ACCEPT_ENCODING', ''):
            return app(environ, start_response)

        response = GzipResponse(start_response, 9)
        app_iter = app(environ, response.gzip_start_response)

        if app_iter is not None:
            response.finish_response(app_iter)

        return response.write()

    def __call__(self, environ, start_response):
        # Hand non-static requests to Django
        if not self._should_handle(get_path_info(environ)):
            return self.application(environ, start_response)

        def max_age(status, headers, exc_info=None):
            headers.append(('Cache-Control', "max-age=31536000"))
            return start_response(status, headers, exc_info)

        # Serve static requests from static.Cling
        if not self.debug:
            environ = self._transpose_environ(environ)
            return self._gzip(self.cling, environ, max_age)
        # Serve static requests in debug mode from StaticFilesHandler
        else:
            return self._gzip(self.debug_cling, environ, start_response)

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "jajaja.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "bearweb.settings.production")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application

application = Cling(get_wsgi_application())

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
