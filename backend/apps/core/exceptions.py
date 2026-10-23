"""Módulo de respuestas de error estandarizadas (RF-API-04).

Provee excepciones y un handler para devolver siempre el formato::

    {
        "error_code": "...",
        "message": "...",
        "details": {...},
        "rn_reference": "...",
        "trace_id": "..."
    }
"""

import uuid
from typing import Any

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


# ------------------------------------------------------------------
# Excepción base del proyecto
# ------------------------------------------------------------------

class SIGEAPIException(APIException):
    """Excepción base de negocio para SIGE (RF-API-04).

    Args:
        error_code: Código canónico del catálogo (§1.4 API REST v2).
        message: Texto legible para el usuario.
        rn_reference: Regla de negocio que origina el error.
        details: Diccionario con detalles por campo.
        http_status: Código HTTP a devolver.
    """

    def __init__(
        self,
        error_code: str,
        message: str,
        rn_reference: str = "",
        details: dict[str, Any] | None = None,
        http_status: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
    ) -> None:
        self.error_code = error_code
        self.error_message = message
        self.rn_reference = rn_reference
        self.error_details = details or {}
        self.status_code = http_status
        super().__init__(detail=message)


# ------------------------------------------------------------------
# Excepciones específicas frecuentes
# ------------------------------------------------------------------

class DuplicateEnrollmentError(SIGEAPIException):
    """Matrícula ya registrada (RN-EST-02)."""

    def __init__(self, enrollment_id: str) -> None:
        super().__init__(
            error_code="DUPLICATE_ENROLLMENT",
            message=f"La matrícula '{enrollment_id}' ya está registrada.",
            rn_reference="RN-EST-02",
            details={"enrollment_id": [f"Duplicado: {enrollment_id}"]},
        )


class DuplicateCurpError(SIGEAPIException):
    """CURP ya registrada."""

    def __init__(self, curp: str) -> None:
        super().__init__(
            error_code="DUPLICATE_RECORD",
            message=f"La CURP '{curp}' ya está registrada en el sistema.",
            rn_reference="RN-EST-02",
            details={"curp": [f"Duplicado: {curp}"]},
        )


class InvalidTransitionError(SIGEAPIException):
    """Transición de estado no permitida (RN-EST-04 / RN-EST-09)."""

    def __init__(self, current: str, target: str) -> None:
        super().__init__(
            error_code="INVALID_TRANSITION",
            message=(
                f"Transición de '{current}' a '{target}' no permitida."
            ),
            rn_reference="RN-EST-04",
            details={"status": [f"{current} → {target}"]},
        )


class StudentNotActiveError(SIGEAPIException):
    """El estudiante no está en estado ACTIVO (RN-EST-05)."""

    def __init__(self) -> None:
        super().__init__(
            error_code="STUDENT_NOT_ACTIVE",
            message="El estudiante no está en estado ACTIVO.",
            rn_reference="RN-EST-05",
        )


# ------------------------------------------------------------------
# Exception handler personalizado (RF-API-04)
# ------------------------------------------------------------------

def sige_exception_handler(exc: Exception, context: dict) -> Response | None:
    """Handler que envuelve toda excepción en el formato uniforme de SIGE."""
    if isinstance(exc, SIGEAPIException):
        return Response(
            {
                "error_code": exc.error_code,
                "message": exc.error_message,
                "details": exc.error_details,
                "rn_reference": exc.rn_reference,
                "trace_id": str(uuid.uuid4()),
            },
            status=exc.status_code,
        )

    # Delegamos al handler por defecto de DRF para el resto.
    response = drf_exception_handler(exc, context)
    if response is not None:
        response.data = {
            "error_code": "VALIDATION_ERROR",
            "message": "Error de validación.",
            "details": response.data,
            "rn_reference": "",
            "trace_id": str(uuid.uuid4()),
        }
    return response
