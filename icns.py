import json
import requests

base = "http://iconverticons-com-hxtzwkxoy3t5.runscope.net"
#base = "http://iconverticons.com"

upload_url = base + "/cgi-bin/upload.pl?output=json"
convert_url = base + "/api/convert.php"
download_url = base + "/api/download.php"



files = {'files[]': ('icon.png', open('icon.png', 'rb'))}

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

icon = [icon for icon in payload['icons'] if icon['format'] == 'icns'].pop()

image_params = {
    'job': job['jobid'],
    'type': 'icns',
    'id': icon['filename'],
}

resp = requests.get(download_url, params=image_params, stream=True)
resp.raise_for_status()

with open('icon.icns', 'wb') as f:
    for chunk in resp.iter_content():
        f.write(chunk)
