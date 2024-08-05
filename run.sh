#!/bin/bash -e

python django_app/manage.py migrate --no-input
python django_app/manage.py loaddata django_app/report_a_suspected_breach/fixtures/*.json

# Start webserver
echo "Running in DBT Platform"
gunicorn django_app.config.wsgi --config django_app/config/gunicorn.py
