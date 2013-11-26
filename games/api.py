import functools
import json

from django.http import HttpResponse
#from django.views.decorators.csrf import csrf_exempt

from .models import Game


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
    return api_error('Internal server error', code=500)


@allowed('GET', 'POST')
def errors(request, game_pk):
    return api_error('Internal server error', code=500)


@allowed('GET')
def appcast(request, game_pk):
    try:
        game = Game.objects.get(pk=game_pk)
    except Game.DoesNotExist:
        return api_error('Requested game does not exist', code=404)
    except Game.MultipleObjectsReturned:
        return api_error('Internal server error', code=500)

    print game.name

    return jsonify(game.appcast())
