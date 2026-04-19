from __future__ import annotations

from django.urls import path

from ui import views


urlpatterns = [
    path("", views.index, name="index"),
    path("api/suggest", views.api_suggest, name="api_suggest"),
    path("api/analyze", views.api_analyze, name="api_analyze"),
]

