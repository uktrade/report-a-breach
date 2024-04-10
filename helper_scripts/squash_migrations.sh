#!/bin/bash

cd ".." || exit
rm report_a_suspected_breach/migrations/*.py
touch report_a_suspected_breach/migrations/__init__.py
pipenv run python manage.py makemigrations
