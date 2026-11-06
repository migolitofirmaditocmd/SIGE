"""Vistas y controladores de operaciones administrativas del sistema SIGE.

Implementa los endpoints definidos en el Módulo ADM / ops (§3.6 de la
Especificación de API REST v2), incluyendo la ejecución manual de verificación
de ausencias y procesos programados.
"""

from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import SIGEAPIException
from apps.core.jobs import execute_job
from apps.core.serializers import JobRunSerializer, RunJobRequestSerializer


class RunJobView(APIView):
    """Endpoint REST para la ejecución manual de procesos programados (§3.6).

    Permite al Administrador ejecutar manualmente las verificaciones de ausencias
    ('check_student_absences', 'check_teacher_absences') tras confirmar que fue
    un día lectivo, levantando las guardias de sanidad de forma controlada y auditada.
    """

    permission_classes = [permissions.IsAdminUser]

    @extend_schema(
        summary="Ejecutar manualmente un proceso programado (ADM)",
        description=(
            "Ejecuta de forma manual e idempotente un background job "
            "(check_student_absences o check_teacher_absences). "
            "Requiere confirm_school_day=True; de lo contrario responde 422 VALIDATION_ERROR. "
            "Queda auditado en AUDIT_LOG con origin='MANUAL' y el usuario autenticado."
        ),
        request=RunJobRequestSerializer,
        responses={
            200: OpenApiResponse(response=JobRunSerializer, description="Resultado del JOB_RUN"),
            400: OpenApiResponse(description="Parámetros inválidos o formato erróneo"),
            403: OpenApiResponse(description="Permiso denegado (requiere rol Administrador)"),
            422: OpenApiResponse(description="Violación de regla de negocio o confirm_school_day ausente"),
        },
    )
    def post(self, request: Request, job_name: str, *args: Any, **kwargs: Any) -> Response:
        """Procesa la solicitud de ejecución de un job programado.

        Args:
            request (Request): Solicitud HTTP entrante con el payload JSON.
            job_name (str): Nombre del job provisto en la URL.
            *args (Any): Argumentos posicionales.
            **kwargs (Any): Argumentos nombrados.

        Returns:
            Response: Resultado del modelo JobRun correspondiente a la ejecución.

        Raises:
            SIGEAPIException: Si confirm_school_day no es True o si el job no está permitido.
        """
        allowed_jobs = ("check_student_absences", "check_teacher_absences")
        if job_name not in allowed_jobs:
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message=f"El proceso '{job_name}' no está permitido para ejecución manual por API.",
                rn_reference="PP §3",
                details={"job_name": [f"Jobs permitidos: {', '.join(allowed_jobs)}"]},
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        serializer = RunJobRequestSerializer(data=request.data)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación en los parámetros de la solicitud.",
                rn_reference="RF-API-04",
                details=serializer.errors,
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        validated_data = serializer.validated_data
        confirm_school_day = validated_data.get("confirm_school_day", False)

        if not confirm_school_day:
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="La ejecución manual de verificación de ausencias requiere confirm_school_day=true.",
                rn_reference="PP §3 (D-03)",
                details={
                    "confirm_school_day": [
                        "Debe confirmar explícitamente que la fecha indicada fue un día lectivo."
                    ]
                },
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        run_date = validated_data.get("date")
        shift = validated_data.get("shift", "MATUTINO")

        job_run = execute_job(
            job_name=job_name,
            run_date=run_date,
            shift=shift,
            confirm_school_day=confirm_school_day,
            user=request.user,
        )

        response_serializer = JobRunSerializer(job_run)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

