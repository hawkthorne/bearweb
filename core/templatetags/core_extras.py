import re
from django import template
from django.core import urlresolvers


class ActiveNode(template.Node):
    def __init__(self, pattern):
        self.pattern = pattern

    def render(self, context):
        request = context.get('request')

        if request is None:
            return ""

        if re.match(self.pattern, request.path):
            return "active"

        return ""

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context, url_name, return_value=' active', **kwargs):
    matches = current_url_equals(context, url_name, **kwargs)
    return return_value if matches else ''


def current_url_equals(context, url_name, **kwargs):
    namespace = ""

    if ":" in url_name:
        namespace, url_name = url_name.split(":")

    resolved = False

    try:
        resolved = urlresolvers.resolve(context.get('request').path)
    except urlresolvers.Resolver404:
        pass

    matches = resolved and resolved.url_name == url_name and resolved.namespace == namespace

    if matches and kwargs:
        for key in kwargs:
            kwarg = kwargs.get(key)
            resolved_kwarg = resolved.kwargs.get(key)
            if not resolved_kwarg or kwarg != resolved_kwarg:
                return False
    return matches

