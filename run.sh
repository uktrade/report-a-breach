#!/bin/bash -e

python django_app/manage.py migrate --no-input
python django_app/manage.py loaddata django_app/report_a_suspected_breach/fixtures/*.json

# Start webserver
if [ -n "${COPILOT_ENVIRONMENT_NAME}" ]; then
    echo "Running in DBT Platform"
    opentelemetry-instrument gunicorn django_app.config.wsgi --config django_app/config/gunicorn.py
else
    echo "Running in Cloud Foundry"
    python django_app/manage.py collectstatic --no-input
    gunicorn django_app.config.wsgi --bind 0.0.0.0:8080 --capture-output --config django_app/config/gunicorn.py
fi
