web: python django_app/manage.py migrate --no-input && gunicorn django_app.config.asgi:application -k django_app.config.uvicorn_worker.CustomUvicornWorker --config django_app/config/gunicorn.py
