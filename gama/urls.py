from django.urls import path

from . import views

app_name = "gama"
urlpatterns = [
    path("", views.index, name="index"),
    path("analysis_run", views.analysis_run, name="analysis_run"),
    path("analysis/", views.analysis_show, name="analysis_show"),
    path('analysis_bulk/', views.analysis_bulk, name='analysis_bulk'),
    path("error/<str:errtype>/", views.error, name="error"),
    path("export_results/", views.export_results, name="export_results"),
    path('clear/', views.clear_session, name='clear_session'),
    path("about/", views.about, name="about"),
]