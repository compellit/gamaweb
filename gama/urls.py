from django.urls import path

from . import views

app_name = "gama"
urlpatterns = [
    path("", views.index, name="index"),
    path("analysis", views.analysis, name="analysis"),
]