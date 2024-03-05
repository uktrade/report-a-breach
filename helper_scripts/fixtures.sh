#!/bin/bash
# Load all fixtures in one go

echo "Loading all fixture data"

pipenv run python manage.py loaddata report_a_breach/fixtures/*.json

echo "Fixtures loaded"
