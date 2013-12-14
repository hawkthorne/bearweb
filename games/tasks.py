from celery import task

from .bundle import package


@task
def error():
    raise ValueError("Boop")


@task
def lovepackage(release_id):
    package(release_id)
