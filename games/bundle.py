import os
import json
import zipfile
import re
import tempfile

from django.conf import settings
from django.template.loader import render_to_string
from django.core.files import File
from django.core.files.base import ContentFile

from .models import Release


def game_config(pk, version):
    base_url = "{}/api/games/{}".format(settings.INSECURE_HOSTNAME, pk)
    return json.dumps({
        "version": version,
        "links": {
            "updates": base_url + "/appcast",
            "metrics": base_url + "/metrics",
            "errors": base_url + "/errors",
        }
    })


# Given a relative path, turn it into a full one
def p(path):
    return os.path.join(settings.SITE_ROOT, "games", path)


def write_symlink(archive, root, path):
    # http://www.mail-archive.com/python-list@python.org/msg34223.html
    zip_info = zipfile.ZipInfo(root)
    zip_info.create_system = 3
    zip_info.external_attr = 2716663808
    archive.writestr(zip_info, os.readlink(path))


def relpath(path, app):
    """Return the correct relative path for the .app"""
    path = path.replace(os.path.join(settings.SITE_ROOT, "games/"), "")
    return path.replace("build/osx/love.app", app)


_version_pattern = r"t\.version\s+=\s+(\"0\.\d\.0\"|'0\.\d\.0')"


def love_version(conf):
    match = re.search(_version_pattern, conf)

    if match is None:
        return match

    return match.group(1).replace('"', '').replace("'", '')


def package_osx(lovefile, name, slug, version):
    """Given a path to a .love file, create OS X version for
    download. Returns path to create zipfile
    """
    _, output_name = tempfile.mkstemp("love")

    app_name = "{}.app".format(name)
    zip_name = "{}-osx-{}.zip".format(slug, version)

    archive = zipfile.ZipFile(output_name, "w")

    for root, directories, files in os.walk(p("build/osx/love.app")):

        for directory in directories:
            fullpath = os.path.join(root, directory)
            archive_root = relpath(fullpath, app_name)

            if os.path.islink(fullpath):
                write_symlink(archive, archive_root, fullpath)

        for filename in files:
            fullpath = os.path.join(root, filename)
            archive_root = relpath(fullpath, app_name)

            if os.path.islink(fullpath):
                write_symlink(archive, archive_root, fullpath)
            else:
                archive.write(fullpath, archive_root, zipfile.ZIP_DEFLATED)

    lovepath = os.path.join(app_name, "Contents", "Resources", 'game.love')
    archive.write(lovefile, lovepath, zipfile.ZIP_DEFLATED)

    archive.close()

    return output_name, zip_name


def blobify(func, lovefile, name, slug, version):
    output_name, zip_name = func(lovefile, name, slug, version)
    blob = File(open(output_name))
    blob.name = zip_name
    return blob


def package_windows(lovefile, name, slug, version):
    """Given a path to a .love file, create a Windows version for
    download. Returns path to created zipfile
    """
    _, output_name = tempfile.mkstemp("love")

    zip_name = "{}-win-{}.zip".format(slug, version)

    archive = zipfile.ZipFile(output_name, "w")

    for filename in os.listdir(p("build/windows")):
        if not filename.endswith(".dll"):
            continue
        archive.write(p(os.path.join("build/windows", filename)),
                      os.path.join(name, filename), zipfile.ZIP_DEFLATED)

    love_exe = open(p("build/windows/love.exe"), "rb").read()
    love_archive = open(lovefile, "rb").read()

    archive.writestr(os.path.join(name, slug + ".exe"),
                     love_exe + love_archive, zipfile.ZIP_DEFLATED)

    archive.close()

    return output_name, zip_name


def package_exe(lovefile, name, slug, version):
    love_exe = open(p("build/windows/love.exe"), "rb").read()
    love_archive = open(lovefile, "rb").read()

    blob = ContentFile(love_exe + love_archive)
    blob.name = slug + ".exe"
    return blob


def inject_code(lovefile, config):
    _, output_name = tempfile.mkstemp("love")

    archive = zipfile.ZipFile(output_name, 'w')

    # Populate with existing code
    with zipfile.ZipFile(lovefile) as old_archive:
        for zipinfo in old_archive.infolist():
            filename = zipinfo.filename

            if zipinfo.filename == 'main.lua':
                zipinfo.filename = 'oldmain.lua'

            archive.writestr(zipinfo, old_archive.read(filename))

    # Add code
    for script in os.listdir(p("build/sparkle")):
        archive.write(p(os.path.join("build", "sparkle", script)),
                      os.path.join("sparkle", script))

    # Add new main.lua
    archive.writestr("main.lua", render_to_string('games/main.lua'))

    # Add JSON
    archive.writestr("sparkle/config.json", config, zipfile.ZIP_DEFLATED)

    archive.close()

    return output_name


def package(release_id):
    release = Release.objects.get(pk=release_id)
    game = release.game

    config = game_config(game.uuid, release.version)

    # Add new code
    upload = release.get_asset('uploaded')
    love = inject_code(upload.blob, config)

    slug = game.slug
    name = game.name

    # Create binaries
    osx_file = blobify(package_osx, love, name, slug, release.version)
    win_file = blobify(package_windows, love, name, slug, release.version)
    exe_file = package_exe(love, name, slug, release.version)

    # Upload
    release.add_asset(osx_file, tag='osx')
    release.add_asset(win_file, tag='windows')
    release.add_asset(exe_file, tag='exe')
