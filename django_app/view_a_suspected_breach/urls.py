from django.urls import path

from . import views

app_name = "view_a_suspected_breach"

urlpatterns = [
    path("", views.ViewABreachView.as_view(), name="landing"),
    path("<str:pk>/", views.ViewASuspectedBreachView.as_view()),
    path("user_admin/", views.ManageUsersView.as_view(), name="user_admin"),
]
