#!/usr/bin/env bash

# Exit early if something goes wrong
set -e

# Add commands below to run inside the container after all the other buildpacks have been applied
export BUILD_STEP='True'
export COPILOT_ENVIRONMENT_NAME='build'
export DJANGO_SECRET_KEY='dummy_key'
export DEBUG='True'
export DATABASE_CREDENTIALS='{"username": "postgres", "password": "password", "engine": "postgres", "port": 5432, "dbname": "postgres", "host": "db", "dbInstanceIdentifier": "emt-db"}'
export DJANGO_SETTINGS_MODULE='config.settings.deploy.development'

echo "Running django_app/manage.py collectstatic --noinput"
python django_app/manage.py collectstatic --no-input
