from django import template
from django.core.urlresolvers import reverse


class ActiveNode(template.Node):
    def __init__(self, named_url):
        self.name = named_url

    def render(self, context):
        request = context.get('request')
        if request is None:
            return ""

        url = reverse(self.name)

        if request.path.startswith(url):
            return "active"

        return ""


def do_active(parser, token):
    _, named_url = token.split_contents()
    return ActiveNode(named_url.replace("'", ""))

register = template.Library()
register.tag('active', do_active)
