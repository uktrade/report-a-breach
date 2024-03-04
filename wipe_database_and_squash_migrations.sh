#!/bin/bash

docker-compose down
rm -r pgdata
docker-compose up -d
sleep 20
rm report_a_breach/migrations/*.py
pipenv run python manage.py makemigrations
pipenv run python manage.py migrate
