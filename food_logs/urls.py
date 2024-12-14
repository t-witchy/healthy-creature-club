from django.urls import path

from . import views
from .views import transcribe_and_analyze, view_logs

urlpatterns = [
    path("", views.index, name="index"),
    path("view-logs", views.view_logs, name="view_logs"),
    path("test", views.test, name="test"),
    path("transcribe-and-analyze/", transcribe_and_analyze, name="transcribe_and_analyze"),
]