from django.http import HttpResponsePermanentRedirect


class WWWRedirectMiddleware:
    """
    This middleware will redirect any requests to www to the bare domain
    """
    def process_request(self, request):
        if request.META.get('HTTP_HOST', '').startswith('www.'):
            url = request.build_absolute_uri()
            return HttpResponsePermanentRedirect(url.replace('www.', '', 1))
