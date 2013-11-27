import functools
import json

import keen

from django.http import HttpResponse

from .models import Game
from games import fieldmarshal


# Structs

class Metric(fieldmarshal.Struct):
    event = unicode
    properties = {unicode: unicode}


class MetricContainer(fieldmarshal.Struct):
    metrics = [Metric]


def jsonify(payload, code=200):
    output = json.dumps(payload)
    return HttpResponse(output, status=code, content_type="application/json")


def api_error(msg, code=400):
    return jsonify({"errors": [{"message": msg}]}, code=code)


def allowed(*args):
    methods = args

    def outer(f):
        @functools.wraps(f)
        def inner(request, *args, **kwargs):
            if request.method not in methods:
                msg = 'Method {} not supported'.format(request.method)
                return api_error(msg, code=405)
            resp = f(request, *args, **kwargs)
            return resp
        return inner
    return outer


@allowed('GET', 'POST')
def metrics(request, game_pk):
    try:
        container = fieldmarshal.loads(MetricContainer, request.body)
    except ValueError:
        return api_error('Could not parse JSON body', code=400)

    events = {}

    for metric in container.metrics:
        if metric.event not in events:
            events[metric.event] = []

        events[metric.event].append(metric.properties)

    # Keen to the rescue
    keen.add_events(events)

    return jsonify('', code=204)


@allowed('GET', 'POST')
def errors(request, game_pk):
    # Track with Keen
    return api_error('Internal server error', code=500)


@allowed('GET')
def appcast(request, game_pk):
    try:
        game = Game.objects.get(pk=game_pk)
    except Game.DoesNotExist:
        return api_error('Requested game does not exist', code=404)
    except Game.MultipleObjectsReturned:
        return api_error('Internal server error', code=500)

    return jsonify(game.appcast())
