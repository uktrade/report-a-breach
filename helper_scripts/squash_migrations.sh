#!/bin/bash

cd ".." || exit
rm report_a_breach/migrations/*.py
touch report_a_breach/migrations/__init__.py
pipenv run python manage.py makemigrations
