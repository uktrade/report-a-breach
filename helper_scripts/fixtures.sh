#!/bin/bash
# Load all fixtures in one go

echo "Loading all fixture data"


cd ".." || exit
cd "django_app" || exit
pipenv run python manage.py loaddata report_a_suspected_breach/fixtures/*.json

echo "Fixtures loaded"
