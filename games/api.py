import functools
import json

import keen

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Game, CrashReport
from games import fieldmarshal


# Structs

class Metric(fieldmarshal.Struct):
    event = unicode
    properties = {}


class Tag(fieldmarshal.Struct):
    os = unicode
    version = unicode
    distinct_id = unicode


class Report(fieldmarshal.Struct):
    message = unicode
    tags = Tag


class MetricContainer(fieldmarshal.Struct):
    metrics = [Metric]


class ReportContainer(fieldmarshal.Struct):
    errors = [Report]


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
@csrf_exempt
def metrics(request, game_uuid):
    try:
        game = Game.objects.get(uuid=game_uuid)
    except Game.DoesNotExist:
        return api_error('Requested game does not exist', code=404)
    except Game.MultipleObjectsReturned:
        return api_error('Internal server error', code=500)

    try:
        container = fieldmarshal.loads(MetricContainer, request.body)
    except ValueError:
        return api_error('Could not parse JSON body', code=400)

    events = {}

    for metric in container.metrics:
        if metric.event not in events:
            events[metric.event] = []

        metric.properties['game_uuid'] = game.uuid
        events[metric.event].append(metric.properties)

    print events

    # Keen to the rescue
    keen.add_events(events)

    return jsonify('', code=204)


@allowed('GET', 'POST')
@csrf_exempt
def errors(request, game_uuid):
    try:
        game = Game.objects.get(uuid=game_uuid)
    except Game.DoesNotExist:
        return api_error('Requested game does not exist', code=404)
    except Game.MultipleObjectsReturned:
        return api_error('Internal server error', code=500)

    try:
        container = fieldmarshal.loads(ReportContainer, request.body)
    except ValueError:
        return api_error('Could not parse JSON body', code=400)

    crashes = []

    for report in container.errors:
        data = fieldmarshal.dumpd(report.tags)
        data['game_uuid'] = game.uuid
        crashes.append(data)

    keen.add_events({
        'crashes': crashes,
    })

    for report in container.errors:
        c = CrashReport(game=game, traceback=report.message)
        c.distinct_id = report.tags.distinct_id
        c.os = report.tags.os
        c.version = report.tags.version
        c.save()

    return api_error('', code=204)


@allowed('GET')
@csrf_exempt
def appcast(request, game_uuid):
    try:
        game = Game.objects.get(uuid=game_uuid)
    except Game.DoesNotExist:
        return api_error('Requested game does not exist', code=404)
    except Game.MultipleObjectsReturned:
        return api_error('Internal server error', code=500)

    return jsonify(game.appcast())
