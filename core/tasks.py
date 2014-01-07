import base64
import json

from django.conf import settings
from django.contrib.auth.models import User

import requests
from celery import task
from customerio import CustomerIO

cio = CustomerIO(settings.CUSTOMERIO_SITE_ID, settings.CUSTOMERIO_API_KEY)

@task
def identify(pk):
    user = User.objects.get(pk=pk)
    cio.identify(id=user.pk, email=user.email, username=user.username)


@task
def track(pk, event, **kwargs):
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

    cio.track(customer_id=pk, name=event, **kwargs)
