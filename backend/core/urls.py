"""URL configuration for SIGE backend.

SIGE · Sistema Integral de Gestión Escolar
Escuela Secundaria Mixta 5
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/v1/students/', include('apps.students.urls', namespace='students')),
    path('api/v1/qr/', include('apps.qr_codes.urls')),
    path('api/v1/credentials/', include('apps.qr_codes.credentials_urls', namespace='credentials')),
    # OpenAPI / Swagger (RF-API-01)
    path('api/v1/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
