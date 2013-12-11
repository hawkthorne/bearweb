web: newrelic-admin gunicorn --access-logfile - -k gevent -w 6 -b 0.0.0.0:$PORT bearweb.wsgi
worker: python manage.py celery worker --loglevel=info
