from django.urls import path

from . import views

app_name = "gama"
urlpatterns = [
    path("", views.index, name="index"),
    path("analysis", views.analysis, name="analysis"),
    path("error/<str:errtype>/", views.error, name="error"),
    path("export_results/", views.export_results, name="export_results"),
    path("about/", views.about, name="about"),
    path("results/", views.analysis_results, name="analysis_result"),
    path('clear-session/', views.clear_session, name='clear_session'),
    path('bulk_analysis/', views.bulk_analysis, name='bulk_analysis'),
]