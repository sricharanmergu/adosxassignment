from django.urls import path
from .views import disagreements

urlpatterns = [path("api/disagreements/", disagreements, name="disagreements")]
