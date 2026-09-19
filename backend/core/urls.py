"""URL configuration for SIGE backend.

SIGE · Sistema Integral de Gestión Escolar
Escuela Secundaria Mixta 5
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints
    path('api/v1/students/', include('apps.students.urls')),
    path('api/v1/qr/', include('apps.qr_codes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
