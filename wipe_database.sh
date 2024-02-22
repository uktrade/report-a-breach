#!/bin/bash

docker-compose down
rm -r pgdata
docker-compose up -d
pipenv run python manage.py migrate
