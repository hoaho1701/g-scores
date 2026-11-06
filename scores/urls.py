from django.urls import path
from . import views

app_name = "scores"

urlpatterns = [
    path("", views.lookup, name="lookup"),
    path("top10/", views.top10, name="top10"),
    path("report/", views.report, name="report"),
]
