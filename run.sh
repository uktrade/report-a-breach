#!/bin/bash -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start webserver
gunicorn config.wsgi --bind 0.0.0.0:8080 --capture-output --config config/gunicorn.py
