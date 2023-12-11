FROM python:3.11.4

# Install dependencies
RUN apt-get update && apt-get install wget gcc libpq-dev postgresql-client npm -y

ENV WEB_PORT ${WEB_PORT}

RUN pip3 install --upgrade pip

RUN mkdir /code
RUN mkdir /deps

WORKDIR /code

COPY requirements.txt /code/

RUN pip3 install -r requirements.txt

CMD scripts/entry.sh
