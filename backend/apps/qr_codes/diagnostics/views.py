"""Vista de diagnóstico y prueba interactiva del escáner QR.

Módulo de soporte técnico aislado del código de producción, destinado a permitir
la verificación visual y óptica de credenciales físicas mediante cámara web o móvil.
"""

from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from apps.students.models import Student


class QRScannerTestView(View):
    """Interfaz web interactiva para pruebas de escaneo óptico y validación de credenciales.

    Permite a los evaluadores (Miguel y Saul) y al personal técnico:
    1. Escanear credenciales físicas impresas usando la cámara del dispositivo en tiempo real.
    2. Subir capturas o fotos de credenciales para decodificación óptica directa.
    3. Probar la resolución y validación de tokens contra el endpoint REST institucional.
    """

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Renderiza la consola interactiva de diagnóstico del escáner QR.

        Args:
            request (HttpRequest): Solicitud HTTP entrante.
            *args (Any): Argumentos posicionales.
            **kwargs (Any): Argumentos nombrados.

        Returns:
            HttpResponse: Plantilla HTML con la consola de escaneo y ejemplos de prueba.
        """
        # Obtenemos los primeros 5 alumnos de 1°A Vespertino como muestras rápidas
        sample_students = []
        students_qs = (
            Student.objects.filter(status=Student.Status.ACTIVO, grade=1, group_letter="A")
            .select_related("group")
            .prefetch_related("qr_tokens")[:5]
        )

        for s in students_qs:
            token_obj = s.active_qr_token
            if token_obj:
                sample_students.append(
                    {
                        "name": s.display_name,
                        "enrollment_id": s.enrollment_id,
                        "token": str(token_obj.token),
                    }
                )

        context = {
            "sample_students": sample_students,
        }
        return render(request, "diagnostics/qr_scanner.html", context)

