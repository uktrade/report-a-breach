"""
WSGI config for core project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware

# Add the project to the python path so the settings module can be imported
sys.path.append(Path(__file__).resolve().parent.parent.__str__())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.deploy.production")

application = get_wsgi_application()

if "COPILOT_ENVIRONMENT_NAME" in os.environ:
    application = OpenTelemetryMiddleware(application)
