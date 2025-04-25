web: python django_app/manage.py migrate --no-input && gunicorn django_app.config.asgi:application -k uvicorn.workers.UvicornWorker --config django_app/config/gunicorn.py --lifespan off
