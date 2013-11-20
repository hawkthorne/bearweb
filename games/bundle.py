import os
import json
import zipfile
import tempfile

from django.conf import settings
from django.template.loader import render_to_string

from .models import Release


def game_config(name, version):
    # FIXME: Use Django Settings for correct urls
    base_url = "http://api.example.com/{}".format(name)
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


def package_osx(lovefile, name, version):
    """Given a path to a .love file, create OS X version for
    download. Returns path to create zipfile
    """
    _, output_name = tempfile.mkstemp("love")

    app_name = "{}.app".format(name)
    zip_name = "{}-osx-{}.zip".format(name.lower().replace(" ", "-"), version)

    archive = zipfile.ZipFile(output_name, "w")

    for root, directories, files in os.walk(p("build/osx/love.app")):

        for directory in directories:
            fullpath = os.path.join(root, directory)
            archive_root = fullpath.replace("build/osx/love.app", app_name)

            if os.path.islink(fullpath):
                write_symlink(archive, archive_root, fullpath)

        for filename in files:
            fullpath = os.path.join(root, filename)
            archive_root = fullpath.replace("build/osx/love.app", app_name)

            if os.path.islink(fullpath):
                write_symlink(archive, archive_root, fullpath)
            else:
                archive.write(fullpath, archive_root, zipfile.ZIP_DEFLATED)

    lovepath = os.path.join(app_name, "Contents", "Resources", 'game.love')
    archive.write(lovefile, lovepath, zipfile.ZIP_DEFLATED)

    archive.close()

    return output_name, zip_name


def package_windows(lovefile, name, version):
    """Given a path to a .love file, create a Windows version for
    download. Returns path to created zipfile
    """
    _, output_name = tempfile.mkstemp("love")

    safe_name = name.lower().replace(" ", "-")
    zip_name = "{}-win-{}.zip".format(safe_name, version)

    archive = zipfile.ZipFile(output_name, "w")

    for filename in os.listdir(p("build/windows")):
        if not filename.endswith(".dll"):
            continue
        archive.write(p(os.path.join("build/windows", filename)),
                      os.path.join(name, filename), zipfile.ZIP_DEFLATED)

    love_exe = open(p("build/windows/love.exe"), "rb").read()
    love_archive = open(lovefile, "rb").read()

    archive.writestr(os.path.join(name, safe_name + ".exe"),
                     love_exe + love_archive, zipfile.ZIP_DEFLATED)

    archive.close()

    return output_name, zip_name


def inject_code(lovefile, config):
    _, output_name = tempfile.mkstemp("love")

    archive = zipfile.ZipFile(output_name, 'w')

    # Populate with existing code
    with zipfile.ZipFile(lovefile) as old_archive:
        for zipinfo in old_archive.infolist():
            if zipinfo.filename == 'main.lua':
                name = 'oldmain.lua'
            else:
                name = zipinfo.filename
            archive.writestr(name, old_archive.read(zipinfo.filename))

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

    config = game_config(game.slug, release.version)

    # Add new code
    lovefile = inject_code(release.original_file, config)

    # Create binaries
    osx_zip, _ = package_osx(lovefile, game.name, release.version)
    win_zip, _ = package_windows(lovefile, game.name, release.version)

    # Upload
    # shutil.move(osx_zip, "output/demo-osx-0.1.0.zip")
    # shutil.move(win_zip, "output/demo-win-0.1.0.zip")
    # shutil.move(lovefile, 'output/demo.love')
