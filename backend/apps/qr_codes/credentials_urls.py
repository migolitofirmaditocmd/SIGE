"""Rutas URL para el módulo de credenciales y exportación (CRE).

Mapea los endpoints de exportación y tokens definidos en:
SIGE_Especificacion_API_REST_v2.md §2.3.
"""

from django.urls import path

from .credentials_views import (
    CredentialExportDownloadView,
    CredentialExportPreviewView,
    CredentialTokenView,
)

app_name = "credentials"

urlpatterns = [
    # POST /api/v1/credentials/tokens/             — emisión / renovación
    path("tokens/", CredentialTokenView.as_view(), name="token-issue"),
    # POST /api/v1/credentials/exports/preview/    — vista previa de exportación
    path(
        "exports/preview/",
        CredentialExportPreviewView.as_view(),
        name="export-preview",
    ),
    # POST /api/v1/credentials/exports/            — descarga PDF o PNG
    path(
        "exports/",
        CredentialExportDownloadView.as_view(),
        name="export-download",
    ),
]
