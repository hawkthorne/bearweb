import tempfile

from django.core.files.base import ContentFile

import requests
from celery import task

from .bundle import package
from .models import Game


@task
def lovepackage(release_id):
    package(release_id)


@task
def update_icns(game_id):
    game = Game.objects.get(pk=game_id)

    base = "http://iconverticons.com"

    upload_url = base + "/cgi-bin/upload.pl?output=json"
    convert_url = base + "/api/convert.php"
    download_url = base + "/api/download.php"

    if game.icon:
        icon = game.icon
    else:
        handle, path = tempfile.mkstemp('stackmachine')

        with open(path, 'wb') as f:
            image = game.identicon(512)
            image.save(f, 'PNG')

        icon = open(path, 'rb')

    files = {'files[]': ('icon.png', icon)}

    resp = requests.post(upload_url, files=files)
    resp.raise_for_status()

    job = resp.json()

    convert_params = {
        'jobid': job['jobid'],
        'filename': job['upload']['filename'],
        'filesize': job['upload']['filesize'],
        'output': 'json',
        'public': 1,
        'icns': 1,
        'rsrc': 1,
        'hqx': 1,
        'ico': 1,
        'png': 1,
        'favicon': 1,
        'iphone': 1,
        'bpp32': 1,
        'bpp08': 0,
        'bpp04': 0,
        'bpp01': 0,
    }

    resp = requests.get(convert_url, params=convert_params)
    resp.raise_for_status()

    payload = resp.json()

    icon = [i for i in payload['icons'] if i['format'] == 'icns'].pop()

    image_params = {
        'job': job['jobid'],
        'type': 'icns',
        'id': icon['filename'],
    }

    resp = requests.get(download_url, params=image_params, stream=True)
    resp.raise_for_status()

    game.icns.save('icon.icns', ContentFile(resp.content))
