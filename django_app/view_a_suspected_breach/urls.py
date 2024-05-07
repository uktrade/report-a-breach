from django.contrib import admin
from django.urls import path

from . import views

app_name = "view_a_suspected_breach"

urlpatterns = [
    path("", views.ViewABreachView.as_view(), name="landing"),
    path("admin/", admin.site.urls),
]

# admin.site.index_template = "admin/base.html"
# admin.autodiscover()
