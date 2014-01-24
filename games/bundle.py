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


def game_config(uuid, identity, version):
    base_url = "{}/api/games/{}".format(settings.INSECURE_HOSTNAME, uuid)
    return json.dumps({
        "identity": identity,
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


def relpath(prefix, path, app):
    """Return the correct relative path for the .app"""
    path = path.replace(os.path.join(settings.SITE_ROOT, "games/"), "")
    return path.replace(prefix + "/osx/love.app", app)

_version_pattern = r"t\.version\s+=\s+(\"0\.\d\.0\"|'0\.\d\.0')"
_identity_pattern = r"t\.identity\s+=\s+(\".+\"|'.+')"


def love_version(conf):
    match = re.search(_version_pattern, conf)

    if match is None:
        return match

    return match.group(1).replace('"', '').replace("'", '')


def love_identity(conf):
    match = re.search(_identity_pattern, conf)

    if match is None:
        return match

    return match.group(1).replace('"', '').replace("'", '')


def detect_version(lovepath):
    lovefile = zipfile.ZipFile(lovepath)

    try:
        lovefile.getinfo('conf.lua')
    except KeyError:
        return None

    conf = lovefile.read('conf.lua')
    return love_version(conf)


def detect_identity(lovepath):
    lovefile = zipfile.ZipFile(lovepath)

    try:
        lovefile.getinfo('conf.lua')
    except KeyError:
        return None

    conf = lovefile.read('conf.lua')
    return love_identity(conf)


def check_for_main(lovepath):
    try:
        lovefile = zipfile.ZipFile(lovepath)
        lovefile.getinfo('main.lua')
        return True
    except KeyError:
        return False
    except zipfile.BadZipfile:
        return False
    except zipfile.LargeZipfile:
        return False


def package_love(game, lovefile, prefix, name, slug, version):
    return lovefile, u"{}.love".format(slug)


def package_osx(game, lovefile, prefix, name, slug, version):
    """Given a path to a .love file, create OS X version for
    download. Returns path to create zipfile
    """
    _, output_name = tempfile.mkstemp("love")

    app_name = u"{}.app".format(name)
    zip_name = u"{}-osx.zip".format(slug)

    archive = zipfile.ZipFile(output_name, "w")

    for root, directories, files in os.walk(p(prefix + "/osx/love.app")):

        for directory in directories:
            fullpath = os.path.join(root, directory)
            archive_root = relpath(prefix, fullpath, app_name)

            if os.path.islink(fullpath):
                write_symlink(archive, archive_root, fullpath)

        for filename in files:

            fullpath = os.path.join(root, filename)
            archive_root = relpath(prefix, fullpath, app_name)

            if os.path.islink(fullpath):
                write_symlink(archive, archive_root, fullpath)
            elif "Love.icns" in fullpath and game.icns:
                archive.writestr(archive_root, game.icns.read(),
                                 zipfile.ZIP_DEFLATED)
            else:
                archive.write(fullpath, archive_root, zipfile.ZIP_DEFLATED)

    lovepath = os.path.join(app_name, "Contents", "Resources", 'game.love')
    archive.write(lovefile, lovepath, zipfile.ZIP_DEFLATED)

    archive.close()

    return output_name, zip_name


def blobify(func, game, lovefile, prefix, name, slug, version):
    output_name, zip_name = func(game, lovefile, prefix, name, slug, version)
    blob = File(open(output_name))
    blob.name = zip_name
    return blob


def package_windows(game, lovefile, prefix, name, slug, version):
    """Given a path to a .love file, create a Windows version for
    download. Returns path to created zipfile
    """
    _, output_name = tempfile.mkstemp("love")

    zip_name = u"{}-win.zip".format(slug)

    archive = zipfile.ZipFile(output_name, "w")

    for filename in os.listdir(p(prefix + "/windows")):
        if not filename.endswith(".dll"):
            continue
        archive.write(p(os.path.join(prefix + "/windows", filename)),
                      os.path.join(name, filename), zipfile.ZIP_DEFLATED)

    love_exe = open(p(prefix + "/windows/love.exe"), "rb").read()
    love_archive = open(lovefile, "rb").read()

    archive.writestr(os.path.join(name, slug + ".exe"),
                     love_exe + love_archive, zipfile.ZIP_DEFLATED)

    archive.close()

    return output_name, zip_name


def package_exe(game, lovefile, prefix, name, slug, version):
    love_exe = open(p(prefix + "/windows/love.exe"), "rb").read()
    love_archive = open(lovefile, "rb").read()

    blob = ContentFile(love_exe + love_archive)
    blob.name = u"{}.exe".format(slug)
    return blob


def inject_code(game, lovefile, config):
    _, output_name = tempfile.mkstemp("love")

    archive = zipfile.ZipFile(output_name, 'w')

    # Populate with existing code
    with zipfile.ZipFile(lovefile) as old_archive:
        for zipinfo in old_archive.infolist():
            filename = zipinfo.filename

            if zipinfo.filename.startswith("__MACOSX"):
                continue

            if zipinfo.filename.endswith(".DS_Store"):
                continue

            if zipinfo.filename == 'main.lua':
                zipinfo.filename = 'oldmain.lua'

            archive.writestr(zipinfo, old_archive.read(filename))

    # Add code
    for script in os.listdir(p("build/love-sdk")):
        if script.startswith("."):
            continue

        archive.write(p(os.path.join("build", "love-sdk", script)),
                      os.path.join("stackmachine", script))

    if game.splash:
        archive.writestr(os.path.join("stackmachine", "splash.png"),
                         game.splash.read())
    else:
        archive.write(p(os.path.join("static", "img", "splash.png")),
                      os.path.join("stackmachine", script))

    # Add new main.lua
    archive.writestr("main.lua", render_to_string('games/main.lua'))

    # FIXME: Add JSON
    archive.writestr("stackmachine/config.json", config, zipfile.ZIP_DEFLATED)

    archive.close()

    return output_name


def package(release_id):
    release = Release.objects.get(pk=release_id)
    game = release.game

    upload = release.get_asset('uploaded')

    identity = detect_identity(upload.blob) or game.slug
    config = game_config(game.uuid, identity, release.version)

    prefix = "build/love8"

    if release.love_version == "0.9.0":
        prefix = "build/love9"

    # Detect version, fail if not specified
    love = inject_code(game, upload.blob, config)

    slug = game.slug
    name = game.name

    # Create binaries
    love_file = blobify(package_love, game, love, prefix, name, slug,
                        release.version)
    osx_file = blobify(package_osx, game, love, prefix, name, slug,
                       release.version)
    win_file = blobify(package_windows, game, love, prefix,
                       name, slug, release.version)
    exe_file = package_exe(game, love, prefix, name, slug, release.version)

    # Upload
    release.add_asset(love_file, tag='love')
    release.add_asset(osx_file, tag='osx')
    release.add_asset(win_file, tag='windows')
    release.add_asset(exe_file, tag='exe')
