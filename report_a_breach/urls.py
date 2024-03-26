from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("", include("report_a_breach.core.urls")),
    path("healthcheck", include("healthcheck.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
