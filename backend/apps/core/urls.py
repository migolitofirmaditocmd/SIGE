"""Rutas de API para el módulo de operaciones y administración (ops / core).

Mapea endpoints de operaciones del sistema (§3.6 de Especificación de API REST v2).
"""

from django.urls import path

from apps.core.views import RunJobView

app_name = "ops"

urlpatterns = [
    path("jobs/<str:job_name>/run/", RunJobView.as_view(), name="run-job"),
]

