from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class SSLifyMiddleware(object):
    """Force all requests to use HTTPs. If we get an HTTP request, we'll just
    force a redirect to HTTPs.

    .. note::
    This will only take effect if ``settings.DEBUG`` is False.

    .. note::
    You can also disable this middleware when testing by setting
    ``settings.SSLIFY_DISABLE`` to True
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        # disabled for test mode?
        if getattr(settings, 'SSLIFY_DISABLE', False):
            return None

        if getattr(view_func, 'ssl_exempt', False):
            return None

        # proceed as normal
        if not any((settings.DEBUG, request.is_secure())):
            url = request.build_absolute_uri(request.get_full_path())
            secure_url = url.replace('http://', 'https://')
            return HttpResponsePermanentRedirect(secure_url)
