#!/bin/bash -e

python manage.py migrate --no-input
python manage.py collectstatic --no-input

# Start webserver
if [ -n "${COPILOT_ENVIRONMENT_NAME}" ]; then
    echo "Running in DBT Platform"
    opentelemetry-instrument gunicorn config.wsgi --config config/gunicorn.py
else
    echo "Running in Cloud Foundry"
    gunicorn config.wsgi --bind 0.0.0.0:8080 --capture-output --config config/gunicorn.py
fi
