from django.conf import settings


def olark(request):
    return {'OLARK': settings.OLARK}
