import os
import sys
from pathlib import Path

from django.core.asgi import get_asgi_application

# from opentelemetry.instrumentation.wsgi import OpenTelemetryMiddleware

# Add the project to the python path so the settings module can be imported
sys.path.append(Path(__file__).resolve().parent.parent.__str__())
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.deploy.production")

application = get_asgi_application()

# if "COPILOT_ENVIRONMENT_NAME" in os.environ:
#     application = OpenTelemetryMiddleware(application)
