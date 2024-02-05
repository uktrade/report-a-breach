#!/bin/bash -e

python manage.py migrate --no-input
python manage.py collectstatic --no-input

# Start webserver
gunicorn config.wsgi --bind 0.0.0.0:8080 --capture-output --config config/gunicorn.py
