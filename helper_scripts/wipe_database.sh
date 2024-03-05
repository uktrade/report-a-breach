#!/bin/bash

docker-compose down
rm -r pgdata
docker-compose up -d
sleep 20
pipenv run python manage.py migrate
