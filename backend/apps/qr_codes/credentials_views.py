"""Vistas REST para el módulo de credenciales y exportación (CRE).

Implementa los contratos definidos en SIGE_Especificacion_API_REST_v2.md §2.3:
    - POST /api/v1/credentials/tokens/
    - POST /api/v1/credentials/exports/preview/
    - POST /api/v1/credentials/exports/
"""

from typing import Any
import uuid

from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import SIGEAPIException, StudentNotActiveError
from apps.students.models import Student
from .card_generator import generate_credential_pdf, generate_credential_png
from .credentials_service import CredentialExportService
from .crypto import issue_qr_token_for_student
from .models import QRCodeToken


# ----------------------------------------------------------------------
# Serializadores de request / response para el módulo CRE
# ----------------------------------------------------------------------

class CredentialTokenIssueSerializer(serializers.Serializer):
    """Serializador para emisión y reemplazo de tokens QR (§2.3)."""

    entity_type = serializers.ChoiceField(
        choices=["STUDENT", "TEACHER"],
        default="STUDENT",
        help_text="Tipo de persona (STUDENT o TEACHER).",
    )
    entity_id = serializers.UUIDField(
        help_text="UUID del estudiante o docente titular.",
    )
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Motivo de la emisión o reemplazo (obligatorio si ya tiene QR vigente).",
    )


class CredentialExportPreviewSerializer(serializers.Serializer):
    """Serializador para solicitud de vista previa de exportación (§2.3)."""

    mode = serializers.ChoiceField(
        choices=["CREDENCIAL", "STICKER"],
        default="CREDENCIAL",
        help_text="Modalidad: CREDENCIAL (requiere foto) o STICKER (solo QR).",
    )
    entity_type = serializers.ChoiceField(
        choices=["STUDENT", "TEACHER"],
        default="STUDENT",
        help_text="Tipo de entidad a exportar.",
    )
    entity_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        default=list,
        help_text="Lista de identificadores para exportación selectiva.",
    )
    group_id = serializers.CharField(
        required=False,
        allow_null=True,
        default=None,
        help_text="Identificador de grupo escolar para exportación masiva.",
    )


class CredentialExportDownloadSerializer(CredentialExportPreviewSerializer):
    """Serializador para descarga de archivos de credenciales (§2.3)."""

    format = serializers.ChoiceField(
        choices=["PDF", "PNG"],
        default="PDF",
        help_text="Formato de exportación: PDF (lote o individual) o PNG (individual).",
    )


# ----------------------------------------------------------------------
# Vistas REST
# ----------------------------------------------------------------------

class CredentialTokenView(APIView):
    """Emite un nuevo código QR para un estudiante o docente (§2.3).

    Si la persona no tiene token vigente, se emite como alta inicial.
    Si ya cuenta con un token vigente, se revoca atómicamente y se
    emite el nuevo (reemplazo por extravío o reposición, RN-QR-01/03).

    Roles permitidos: ADM, PAD.
    """

    @extend_schema(
        operation_id="credentials_issue_token",
        summary="Emitir o renovar código QR de credencial",
        description="Genera un nuevo token criptográfico opaco y revoca el anterior si existía (RN-QR-01, RN-QR-03).",
        request=CredentialTokenIssueSerializer,
        responses={
            201: inline_serializer(
                "CredentialTokenIssueResponse",
                fields={
                    "message": serializers.CharField(),
                    "token": serializers.UUIDField(),
                    "status": serializers.CharField(),
                    "issued_at": serializers.DateTimeField(),
                    "entity_id": serializers.UUIDField(),
                    "enrollment_id": serializers.CharField(),
                },
            )
        },
        tags=["Identificación y Credenciales"],
    )
    def post(self, request: Request) -> Response:
        """Procesa la emisión o reposición del token QR.

        Args:
            request (Request): Objeto de solicitud HTTP.

        Returns:
            Response: Datos del token emitido (HTTP 201).
        """
        serializer = CredentialTokenIssueSerializer(data=request.data)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error en los parámetros de emisión.",
                details=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        entity_id = data["entity_id"]
        entity_type = data["entity_type"]
        reason = data.get("reason", "").strip()

        if entity_type == "STUDENT":
            try:
                student = Student.objects.prefetch_related("qr_tokens").get(pk=entity_id)
            except Student.DoesNotExist:
                raise SIGEAPIException(
                    error_code="NOT_FOUND",
                    message="Estudiante no encontrado.",
                    http_status=status.HTTP_404_NOT_FOUND,
                )

            # Validar que esté activo (RN-EST-05)
            if student.status != Student.Status.ACTIVO:
                raise SIGEAPIException(
                    error_code="STUDENT_NOT_ACTIVE",
                    message="El estudiante no está en estado ACTIVO.",
                    rn_reference="RN-EST-05",
                    http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            has_active = student.active_qr_token is not None
            if has_active and not reason:
                raise SIGEAPIException(
                    error_code="VALIDATION_ERROR",
                    message=(
                        "El estudiante ya cuenta con un código QR activo. "
                        "El campo 'reason' es obligatorio para reposición."
                    ),
                    details={"reason": ["Requerido para reemplazo de credencial."]},
                    http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )

            token_obj = issue_qr_token_for_student(
                student, reason=reason or "Alta inicial de credencial"
            )

            resp_data = {
                "message": "Token QR emitido satisfactoriamente.",
                "token": token_obj.token,
                "status": token_obj.status,
                "issued_at": token_obj.issued_at,
                "entity_id": student.id,
                "enrollment_id": student.enrollment_id,
            }
            resp = Response(resp_data, status=status.HTTP_201_CREATED)
            resp["Cache-Control"] = "no-store"
            return resp

        raise SIGEAPIException(
            error_code="VALIDATION_ERROR",
            message=f"Tipo de entidad '{entity_type}' no soportado.",
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class CredentialExportPreviewView(APIView):
    """Vista previa de una exportación de credenciales o stickers (§2.3).

    Calcula quiénes cumplen todos los requisitos y lista aparte a los
    excluidos con su respectivo motivo de rechazo (RN-CRE-01).

    Roles permitidos: ADM, PAD.
    """

    @extend_schema(
        operation_id="credentials_export_preview",
        summary="Vista previa de exportación de credenciales",
        description="Evalúa los candidatos y lista a los incluidos y excluidos con su motivo (RN-CRE-01).",
        request=CredentialExportPreviewSerializer,
        responses={
            200: inline_serializer(
                "CredentialExportPreviewResponse",
                fields={
                    "included": serializers.IntegerField(),
                    "excluded": serializers.ListField(child=serializers.DictField()),
                },
            )
        },
        tags=["Identificación y Credenciales"],
    )
    def post(self, request: Request) -> Response:
        """Calcula y devuelve la vista previa de inclusión/exclusión.

        Args:
            request (Request): Solicitud con mode, entity_ids o group_id.

        Returns:
            Response: Conteo de incluidos y lista de excluidos (HTTP 200).
        """
        serializer = CredentialExportPreviewSerializer(data=request.data)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación en la solicitud de vista previa.",
                details=serializer.errors,
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        data = serializer.validated_data
        result = CredentialExportService.evaluate_export_candidates(
            mode=data["mode"],
            entity_type=data["entity_type"],
            entity_ids=data.get("entity_ids"),
            group_id=data.get("group_id"),
        )

        resp_data = {
            "included": result["included"],
            "excluded": result["excluded"],
        }
        resp = Response(resp_data, status=status.HTTP_200_OK)
        resp["Cache-Control"] = "no-store"
        return resp


class CredentialExportDownloadView(APIView):
    """Descarga de credenciales o stickers generados en PDF o PNG (§2.3).

    Genera el archivo en memoria bajo demanda y lo entrega en la respuesta.
    No se almacena ninguna copia temporal en el servidor debido a que
    contiene fotografías de menores de edad (RN-TRX-01, RN-TRX-02).

    Roles permitidos: ADM, PAD.
    """

    @extend_schema(
        operation_id="credentials_export_download",
        summary="Descargar credenciales o stickers (PDF/PNG)",
        description="Genera y entrega el documento de credenciales para impresión (RF-CRE-01, RF-CRE-02).",
        request=CredentialExportDownloadSerializer,
        responses={
            (200, "application/pdf"): bytes,
            (200, "image/png"): bytes,
        },
        tags=["Identificación y Credenciales"],
    )
    def post(self, request: Request) -> HttpResponse:
        """Genera el flujo binario del archivo solicitado y lo retorna con headers seguros.

        Args:
            request (Request): Solicitud con parámetros de exportación y formato.

        Returns:
            HttpResponse: Documento PDF o imagen PNG en flujo binario.
        """
        serializer = CredentialExportDownloadSerializer(data=request.data)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación en los parámetros de exportación.",
                details=serializer.errors,
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        data = serializer.validated_data
        mode = data["mode"]
        fmt = data["format"].upper()

        result = CredentialExportService.evaluate_export_candidates(
            mode=mode,
            entity_type=data["entity_type"],
            entity_ids=data.get("entity_ids"),
            group_id=data.get("group_id"),
        )

        included_students = result["included_students"]

        # Si nadie cumplió las condiciones, se rechaza según §2.3
        if len(included_students) == 0:
            raise SIGEAPIException(
                error_code="BUSINESS_RULE_VIOLATION",
                message=(
                    "Ninguna persona cumple los requisitos para la exportación. "
                    "Verifique estatus, vigencia de QR o fotografías faltantes."
                ),
                rn_reference="RN-CRE-01",
                details={"excluded": result["excluded"]},
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Regla §2.3: PNG solo para una sola persona
        if fmt == "PNG" and len(included_students) > 1:
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message=(
                    "El formato PNG solo admite la exportación de una sola persona. "
                    f"Se encontraron {len(included_students)} candidatos incluidos. "
                    "Utilice formato PDF para lotes."
                ),
                details={"included_count": len(included_students)},
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        if fmt == "PNG":
            content = generate_credential_png(included_students[0], mode=mode)
            content_type = "image/png"
            filename = f"credencial_{included_students[0]['enrollment_id']}_{mode.lower()}.png"
        else:
            content = generate_credential_pdf(included_students, mode=mode)
            content_type = "application/pdf"
            filename = f"credenciales_{mode.lower()}_{len(included_students)}.pdf"

        response = HttpResponse(content, content_type=content_type)
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        response["Content-Length"] = str(len(content))
        response["Cache-Control"] = "no-store"
        return response
