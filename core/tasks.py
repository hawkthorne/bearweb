import base64
import json
import requests
from celery import task
from django.conf import settings


@task
def track(event, **kwargs):
    token = settings.MIXPANEL_API_TOKEN

    if "token" not in kwargs:
        kwargs["token"] = token

    params = {
        "event": event,
        "properties": kwargs
    }

    data = base64.b64encode(json.dumps(params))
    url = "http://api.mixpanel.com/track/?data=" + data
    requests.get(url)
