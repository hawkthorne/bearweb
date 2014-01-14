web: python manage.py collectstatic --noinput -v 0; newrelic-admin run-program gunicorn --access-logfile - -k gevent -w 6 -b 0.0.0.0:$PORT bearweb.wsgi
worker: python manage.py celery worker --loglevel=info
