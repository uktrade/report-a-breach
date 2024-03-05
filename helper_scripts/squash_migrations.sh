#!/bin/bash

docker-compose up -d
sleep 10
rm report_a_breach/migrations/*.py
pipenv run python manage.py makemigrations
