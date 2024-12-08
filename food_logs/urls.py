from django.urls import path

from . import views
from .views import transcribe_and_analyze

urlpatterns = [
    path("", views.index, name="index"),
    path("transcribe-and-analyze/", transcribe_and_analyze, name="transcribe_and_analyze"),
]