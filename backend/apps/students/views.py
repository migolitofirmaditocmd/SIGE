"""Vistas REST del módulo de estudiantes y tutores.

Implementa todos los endpoints definidos en:
    - §2.4: GET /students/{id}/, GET /students/, POST /students/,
      POST /students/{id}/photo/, GET /students/{id}/photo/
    - §3.4: PATCH /students/{id}/, POST /students/{id}/status/,
      POST /students/{id}/reinstate/, POST /students/{id}/guardians/,
      PATCH /guardians/{id}/, POST /guardians/{id}/split/,
      POST /student-guardians/{id}/invalidate-contact/,
      PATCH /student-guardians/{id}/consent/

Reglas aplicadas:
    - RF-API-04: formato de error uniforme via SIGEAPIException.
    - §1.5: paginación estándar (page, page_size ≤ 100).
    - §1.7: permisos por rol (pendiente de integrar JWT; actualmente
      abierto para desarrollo).
    - §1.8: Cache-Control: no-store en respuestas con datos personales.
    - RN-EST-04: EGRESADO es estado final; no se puede reinscribir.
    - RN-EST-09: solo BAJA puede reincorporarse a ACTIVO.
    - RN-EST-14: edición de Guardian compartido requiere confirm=True.
"""

import hashlib
import io
import uuid
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.http import FileResponse
from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from PIL import Image
from rest_framework import filters, serializers, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import (
    InvalidTransitionError,
    SIGEAPIException,
    StudentNotActiveError,
)
from .batch_photos import find_matching_student, process_and_save_photo
from .models import GroupProxy, Guardian, GuardianConsentLog, Student, StudentGuardian
from .serializers import (
    ConsentUpdateSerializer,
    GroupListSerializer,
    GuardianInlineSerializer,
    GuardianSerializer,
    StudentGuardianSerializer,
    StudentReadSerializer,
    StudentReinstateSerializer,
    StudentStatusSerializer,
    StudentWriteSerializer,
)


# ------------------------------------------------------------------
# Paginación estándar (§1.5)
# ------------------------------------------------------------------

class StudentPagination(PageNumberPagination):
    """Paginación configurable con máximo 100 por página (§1.5).

    Returns:
        Respuesta paginada con count, next, previous y results.
    """

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _no_store_response(data: Any, status_code: int) -> Response:
    """Crea una Response con Cache-Control: no-store (§1.8, RN-TRX-01).

    Args:
        data: Datos serializables a incluir en el cuerpo.
        status_code: Código HTTP de la respuesta.

    Returns:
        Response: Objeto Response con la cabecera de caché apropiada.
    """
    resp = Response(data, status=status_code)
    resp["Cache-Control"] = "no-store"
    return resp


def _get_student_or_404(pk: str) -> Student:
    """Obtiene un Student por PK o lanza 404 con formato SIGE.

    Args:
        pk: UUID del estudiante.

    Returns:
        Student: Instancia encontrada.

    Raises:
        SIGEAPIException: HTTP 404 si no existe.
    """
    try:
        return (
            Student.objects
            .select_related()
            .prefetch_related(
                "student_guardians__guardian",
                "student_guardians__consent_logs",
                "qr_tokens",
            )
            .get(pk=pk)
        )
    except (Student.DoesNotExist, ValueError):
        raise SIGEAPIException(
            error_code="NOT_FOUND",
            message="Estudiante no encontrado.",
            rn_reference="",
            http_status=status.HTTP_404_NOT_FOUND,
        )


def _apply_role_field_filter(
    data: dict, request: Request
) -> dict:
    """Elimina campos sensibles según el rol del solicitante (RN-EST-12).

    Para PREFECTO (PRE): elimina has_payment_debt y pending_subjects.
    Para roles sin acceso a salud: elimina blood_type, allergies.

    Args:
        data: Datos serializados del estudiante.
        request: Objeto Request de DRF.

    Returns:
        dict: Datos filtrados por rol.
    """
    # TODO: integrar con el sistema de autenticación JWT.
    # Por ahora, para desarrollo, se devuelven todos los campos.
    return data


# ------------------------------------------------------------------
# GET & POST /api/v1/students/
# ------------------------------------------------------------------

class StudentListCreateView(APIView):
    """Listado paginado y creación de estudiantes (§2.4).

    GET: búsqueda y filtros por nombre, matrícula, grado, grupo y estatus.
    POST: crea un estudiante con su tutor en una sola transacción.

    Roles permitidos:
        GET:  ADM, PRE, PAD.
        POST: ADM, PAD.
    """

    pagination_class = StudentPagination

    def _get_queryset(self, request: Request) -> QuerySet:
        """Construye el queryset filtrado por parámetros de URL.

        Args:
            request: Objeto Request con query_params.

        Returns:
            QuerySet: Estudiantes filtrados y ordenados.
        """
        qs = (
            Student.objects
            .prefetch_related(
                "student_guardians__guardian",
                "qr_tokens",
            )
            .order_by(
                "grade", "group_letter", "shift",
                "last_name_father", "last_name_mother", "first_name",
            )
        )

        params = request.query_params

        # Filtros directos
        grade = params.get("grade")
        group = params.get("group")
        shift = params.get("shift")
        status_param = params.get("status")
        if grade:
            qs = qs.filter(grade=grade)
        if group:
            qs = qs.filter(group_letter=group.upper())
        if shift:
            qs = qs.filter(shift=shift.upper())
        if status_param:
            qs = qs.filter(status=status_param.upper())

        # Búsqueda por texto (nombre o matrícula)
        search = params.get("search", "").strip()
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(enrollment_id__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name_father__icontains=search)
                | Q(last_name_mother__icontains=search)
                | Q(curp__icontains=search)
            )

        return qs

    @extend_schema(
        operation_id="students_list",
        summary="Listado paginado y búsqueda de estudiantes",
        description="Lista estudiantes con filtros de grado, grupo, turno, estatus y búsqueda por texto.",
        parameters=[
            OpenApiParameter("grade", int, description="Grado escolar (1, 2, 3)"),
            OpenApiParameter("group", str, description="Letra de grupo (A–F)"),
            OpenApiParameter("shift", str, description="Turno (MATUTINO, VESPERTINO)"),
            OpenApiParameter("status", str, description="Estatus (ACTIVO, BAJA, EGRESADO)"),
            OpenApiParameter("search", str, description="Búsqueda en nombre, matrícula y CURP"),
            OpenApiParameter("page", int, description="Número de página"),
            OpenApiParameter("page_size", int, description="Tamaño de página (máx. 100)"),
        ],
        responses={200: StudentReadSerializer(many=True)},
        tags=["Estudiantes"],
    )
    def get(self, request: Request) -> Response:
        """Lista estudiantes con paginación y filtros (§2.4, RF-EST-04).

        Args:
            request: Request HTTP GET con query_params opcionales:
                - grade: Filtro por grado (1, 2, 3).
                - group: Filtro por letra de grupo (A–F).
                - shift: Filtro por turno (MATUTINO/VESPERTINO).
                - status: Filtro por estado escolar.
                - search: Búsqueda en nombre, matrícula y CURP.
                - page: Número de página.
                - page_size: Tamaño de página (máx. 100).

        Returns:
            Response: Lista paginada de expedientes.
        """
        qs = self._get_queryset(request)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(qs, request)
        serializer = StudentReadSerializer(page, many=True)
        data = [_apply_role_field_filter(s, request) for s in serializer.data]
        resp = paginator.get_paginated_response(data)
        resp["Cache-Control"] = "no-store"
        return resp

    @extend_schema(
        operation_id="students_create",
        summary="Crear estudiante con tutores",
        description="Crea un expediente de estudiante y sus tutores legales asociados en una sola transacción.",
        request=StudentWriteSerializer,
        responses={201: StudentReadSerializer},
        tags=["Estudiantes"],
    )
    def post(self, request: Request) -> Response:
        """Crea un estudiante con sus tutores (§2.4, RN-EST-02/03/10/13).

        Args:
            request: Request HTTP POST con el payload del estudiante
                y la lista de tutores.

        Returns:
            Response: Expediente creado (HTTP 201) o error (HTTP 400/422).
        """
        serializer = StudentWriteSerializer(data=request.data)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación.",
                details=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        student = serializer.save()
        out = StudentReadSerializer(student)
        return _no_store_response(out.data, status.HTTP_201_CREATED)


# ------------------------------------------------------------------
# GET, PATCH /api/v1/students/{id}/
# ------------------------------------------------------------------

class StudentDetailView(APIView):
    """Detalle y actualización parcial del expediente de un estudiante.

    GET: expediente completo con filtrado de campos por rol (RN-EST-12).
    PATCH: actualización de campos; matrícula inmutable (RN-EST-02).

    Roles permitidos:
        GET:  ADM, PRE, PAD.
        PATCH: ADM, PAD.
    """

    @extend_schema(
        operation_id="students_detail",
        summary="Expediente completo de un estudiante",
        responses={200: StudentReadSerializer},
        tags=["Estudiantes"],
    )
    def get(self, request: Request, pk: str) -> Response:
        """Devuelve el expediente completo del estudiante (§2.4).

        Args:
            request: Request HTTP GET.
            pk: UUID del estudiante.

        Returns:
            Response: Expediente con datos y vínculos de tutores.
        """
        student = _get_student_or_404(pk)
        data = StudentReadSerializer(student).data
        data = _apply_role_field_filter(data, request)
        return _no_store_response(data, status.HTTP_200_OK)

    @extend_schema(
        operation_id="students_update",
        summary="Actualización parcial del expediente",
        description="Actualiza datos del estudiante. La matrícula enrollment_id es inmutable (RN-EST-02).",
        request=StudentWriteSerializer,
        responses={200: StudentReadSerializer},
        tags=["Estudiantes"],
    )
    def patch(self, request: Request, pk: str) -> Response:
        """Actualiza campos del expediente parcialmente (§3.4).

        La matrícula enrollment_id es inmutable (RN-EST-02).

        Args:
            request: Request HTTP PATCH con campos a modificar.
            pk: UUID del estudiante.

        Returns:
            Response: Expediente actualizado.
        """
        student = _get_student_or_404(pk)
        serializer = StudentWriteSerializer(
            student, data=request.data, partial=True
        )
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación.",
                details=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        updated = serializer.save()
        out = StudentReadSerializer(updated)
        return _no_store_response(out.data, status.HTTP_200_OK)


# ------------------------------------------------------------------
# POST /api/v1/students/{id}/status/   (baja lógica)
# ------------------------------------------------------------------

class StudentStatusView(APIView):
    """Cambia el estado escolar del alumno a BAJA o EGRESADO (§3.4).

    Reglas:
        - RN-EST-04: EGRESADO es estado final.
        - RN-EST-09: solo ACTIVO puede pasar a BAJA o EGRESADO.

    Roles permitidos: ADM, PAD.
    """

    # Transiciones permitidas: origen → destinos válidos
    _ALLOWED: dict[str, list[str]] = {
        "ACTIVO": ["BAJA", "EGRESADO"],
        "BAJA": ["EGRESADO"],
    }

    @extend_schema(
        operation_id="students_change_status",
        summary="Baja lógica o egreso de estudiante",
        description="Aplica la transición a BAJA o EGRESADO con motivo obligatorio (RN-EST-04, RN-EST-09).",
        request=StudentStatusSerializer,
        responses={200: inline_serializer("StudentStatusResponse", fields={"id": serializers.UUIDField(), "status": serializers.CharField()})},
        tags=["Estudiantes"],
    )
    def post(self, request: Request, pk: str) -> Response:
        """Aplica la transición de estado solicitada.

        Args:
            request: Request con ``status`` (BAJA|EGRESADO) y ``reason``.
            pk: UUID del estudiante.

        Returns:
            Response: Estado nuevo del estudiante (HTTP 200).
        """
        student = _get_student_or_404(pk)
        serializer = StudentStatusSerializer(data=request.data)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación.",
                details=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        target = serializer.validated_data["status"]
        allowed = self._ALLOWED.get(student.status, [])
        if target not in allowed:
            raise InvalidTransitionError(student.status, target)

        student.status = target
        student.save(update_fields=["status", "updated_at"])
        return _no_store_response(
            {"id": str(student.id), "status": student.status},
            status.HTTP_200_OK,
        )


# ------------------------------------------------------------------
# DELETE /api/v1/students/{id}/delete/   – Eliminación permanente
# ------------------------------------------------------------------

class StudentDeleteView(APIView):
    """Eliminación permanente (hard delete) de un estudiante del sistema.

    Elimina de forma irreversible el registro del estudiante junto con
    sus archivos de fotografía (procesada y original) del disco. Los
    registros asociados (QRCodeToken, StudentGuardian, GuardianConsentLog)
    se eliminan en cascada por las restricciones FK del modelo.

    Roles permitidos: ADM.

    Raises:
        SIGEAPIException: HTTP 404 si el estudiante no existe.
    """

    @extend_schema(
        operation_id="students_delete",
        summary="Eliminar estudiante permanentemente",
        description=(
            "Elimina de forma irreversible el expediente del estudiante, "
            "sus fotografías en disco y todos los registros asociados en cascada. "
            "Esta operación NO puede deshacerse."
        ),
        responses={
            200: inline_serializer(
                "StudentDeleteResponse",
                fields={
                    "message": serializers.CharField(),
                    "deleted_id": serializers.UUIDField(),
                },
            )
        },
        tags=["Estudiantes"],
    )
    @transaction.atomic
    def delete(self, request: Request, pk: str) -> Response:
        """Elimina permanentemente al estudiante y sus archivos.

        Args:
            request: Objeto de solicitud HTTP.
            pk: UUID del estudiante a eliminar.

        Returns:
            Response: Mensaje de confirmación con el ID eliminado (HTTP 200).

        Raises:
            SIGEAPIException: HTTP 404 si el estudiante no existe.
        """
        student = _get_student_or_404(pk)

        student_id_str = str(student.id)
        display_name = student.display_name

        # Eliminar fotografías del disco (procesada y original)
        media_root = Path(settings.MEDIA_ROOT)
        for photo_path in [
            media_root / "students" / f"{student.id}.jpg",
            media_root / "students" / "originals" / f"{student.id}.jpg",
        ]:
            if photo_path.exists():
                try:
                    photo_path.unlink()
                except OSError:
                    pass  # Si no se puede eliminar el archivo, continuar

        # Eliminar el registro — las FK con on_delete=CASCADE
        # eliminan QRCodeToken, StudentGuardian y GuardianConsentLog.
        student.delete()

        return _no_store_response(
            {
                "message": f"Estudiante '{display_name}' eliminado exitosamente.",
                "deleted_id": student_id_str,
            },
            status.HTTP_200_OK,
        )


# ------------------------------------------------------------------
# POST /api/v1/students/{id}/reinstate/   (BAJA → ACTIVO)
# ------------------------------------------------------------------

class StudentReinstateView(APIView):
    """Reincorpora un alumno de BAJA a ACTIVO (§3.4, RN-EST-06/09).

    EGRESADO es estado final y nunca puede reinstaurarse (RN-EST-09).

    Roles permitidos: ADM únicamente.
    """

    @extend_schema(
        operation_id="students_reinstate",
        summary="Reincorporar estudiante (BAJA → ACTIVO)",
        description="Reincorpora un alumno de BAJA a ACTIVO con motivo obligatorio (RN-EST-06, RN-EST-09).",
        request=StudentReinstateSerializer,
        responses={200: inline_serializer("StudentReinstateResponse", fields={"id": serializers.UUIDField(), "status": serializers.CharField()})},
        tags=["Estudiantes"],
    )
    def post(self, request: Request, pk: str) -> Response:
        """Cambia el estado de BAJA a ACTIVO con motivo obligatorio.

        Args:
            request: Request con ``reason`` obligatorio.
            pk: UUID del estudiante.

        Returns:
            Response: Estado actualizado (HTTP 200).
        """
        student = _get_student_or_404(pk)
        if student.status == Student.Status.EGRESADO:
            raise InvalidTransitionError("EGRESADO", "ACTIVO")
        if student.status == Student.Status.ACTIVO:
            raise InvalidTransitionError("ACTIVO", "ACTIVO")

        serializer = StudentReinstateSerializer(data=request.data)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación.",
                details=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        student.status = Student.Status.ACTIVO
        student.save(update_fields=["status", "updated_at"])
        return _no_store_response(
            {"id": str(student.id), "status": student.status},
            status.HTTP_200_OK,
        )


# ------------------------------------------------------------------
# POST /api/v1/students/{id}/guardians/
# ------------------------------------------------------------------

class StudentGuardianAddView(APIView):
    """Agrega un tutor a un estudiante existente (§3.4, RN-EST-03/11/13).

    Roles permitidos: ADM, PAD.
    """

    @extend_schema(
        operation_id="students_add_guardian",
        summary="Vincular tutor legal a estudiante",
        description="Vincula un tutor existente o crea uno nuevo para el alumno (RN-EST-03, RN-EST-13).",
        request=GuardianInlineSerializer,
        responses={201: StudentGuardianSerializer},
        tags=["Tutores"],
    )
    def post(self, request: Request, pk: str) -> Response:
        """Vincula un Guardian nuevo o existente al estudiante.

        Args:
            request: Request con datos del tutor (o existing_guardian_id).
            pk: UUID del estudiante.

        Returns:
            Response: Vínculo StudentGuardian creado (HTTP 201).
        """
        student = _get_student_or_404(pk)

        serializer = GuardianInlineSerializer(data=request.data)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación.",
                details=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        data = serializer.validated_data
        existing_id = data.pop("existing_guardian_id", None)
        data.pop("decline_match_reason", None)
        relationship = data.pop(
            "relationship", StudentGuardian.Relationship.TUTOR_LEGAL
        )
        is_primary = data.pop("is_primary_contact", False)

        with transaction.atomic():
            if existing_id:
                try:
                    guardian = Guardian.objects.get(pk=existing_id)
                except Guardian.DoesNotExist:
                    raise SIGEAPIException(
                        error_code="NOT_FOUND",
                        message=f"No existe un tutor con id={existing_id}.",
                        http_status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                guardian = Guardian.objects.create(**data)

            if StudentGuardian.objects.filter(
                student=student, guardian=guardian
            ).exists():
                raise SIGEAPIException(
                    error_code="DUPLICATE_RECORD",
                    message="Este tutor ya está vinculado al estudiante.",
                    rn_reference="RN-EST-03",
                )

            sg = StudentGuardian.objects.create(
                student=student,
                guardian=guardian,
                relationship=relationship,
                is_primary_contact=is_primary,
                is_valid_contact=bool(
                    guardian.email or guardian.phone_number
                ),
            )
            GuardianConsentLog.objects.create(
                student_guardian=sg,
                previous_status=None,
                new_status=StudentGuardian.ConsentStatus.PENDIENTE,
                registered_by=None,
            )

        out = StudentGuardianSerializer(sg)
        return _no_store_response(out.data, status.HTTP_201_CREATED)


# ------------------------------------------------------------------
# PATCH /api/v1/guardians/{id}/    (con aviso si es compartido)
# ------------------------------------------------------------------

class GuardianDetailView(APIView):
    """Actualiza un Guardian (§3.4, RN-EST-14).

    Si el tutor está vinculado a 2 o más estudiantes y la petición
    no incluye ``confirm=true``, responde 422 CONFIRMATION_REQUIRED
    con la lista de alumnos afectados.

    Roles permitidos: ADM, PAD.
    """

    def _get_guardian_or_404(self, pk: str) -> Guardian:
        """Obtiene Guardian por PK o lanza 404 con formato SIGE."""
        try:
            return Guardian.objects.prefetch_related(
                "student_guardians__student"
            ).get(pk=pk)
        except (Guardian.DoesNotExist, ValueError):
            raise SIGEAPIException(
                error_code="NOT_FOUND",
                message="Tutor no encontrado.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

    @extend_schema(
        operation_id="guardians_update",
        summary="Actualizar datos de tutor legal",
        description="Edita datos del tutor. Si está compartido, requiere confirm=true (RN-EST-14).",
        parameters=[
            OpenApiParameter("confirm", bool, description="Confirmar actualización para tutor compartido"),
        ],
        request=GuardianSerializer,
        responses={200: GuardianSerializer},
        tags=["Tutores"],
    )
    def patch(self, request: Request, pk: str) -> Response:
        """Actualiza parcialmente los datos de un tutor.

        Args:
            request: Request HTTP PATCH. El parámetro ``confirm=true``
                permite modificar un tutor compartido tras mostrar aviso.
            pk: UUID del tutor.

        Returns:
            Response: Tutor actualizado (HTTP 200) o aviso (HTTP 422).
        """
        guardian = self._get_guardian_or_404(pk)

        # RN-EST-14: si es compartido y no hay confirmación, avisa.
        shared_count = guardian.student_guardians.count()
        confirm = str(request.query_params.get("confirm", "")).lower() == "true"

        if shared_count >= 2 and not confirm:
            affected = [
                {
                    "id": str(sg.student.id),
                    "display_name": sg.student.display_name,
                    "grade": sg.student.grade,
                    "group_letter": sg.student.group_letter,
                }
                for sg in guardian.student_guardians.select_related("student")
            ]
            raise SIGEAPIException(
                error_code="CONFIRMATION_REQUIRED",
                message=(
                    f"Este tutor está vinculado a {shared_count} estudiantes. "
                    f"Envíe ?confirm=true para aplicar el cambio a todos."
                ),
                rn_reference="RN-EST-14",
                details={
                    "affected_students": {
                        "count": shared_count,
                        "students": affected,
                    }
                },
            )

        serializer = GuardianSerializer(guardian, data=request.data, partial=True)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación.",
                details=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return _no_store_response(serializer.data, status.HTTP_200_OK)


# ------------------------------------------------------------------
# POST /api/v1/student-guardians/{id}/invalidate-contact/
# ------------------------------------------------------------------

class InvalidateContactView(APIView):
    """Marca un vínculo StudentGuardian como contacto inválido (§3.4, RN-EST-11).

    Roles permitidos: ADM, PAD.
    """

    @extend_schema(
        operation_id="student_guardians_invalidate_contact",
        summary="Invalidar contacto de tutor",
        description="Marca el contacto como inválido con motivo obligatorio (RN-EST-11).",
        request=inline_serializer("InvalidateContactRequest", fields={"reason": serializers.CharField()}),
        responses={200: inline_serializer("InvalidateContactResponse", fields={"id": serializers.UUIDField(), "is_valid_contact": serializers.BooleanField(), "invalid_reason": serializers.CharField()})},
        tags=["Tutores"],
    )
    def post(self, request: Request, pk: str) -> Response:
        """Invalida el contacto del tutor para este estudiante.

        Args:
            request: Request con ``reason`` obligatorio.
            pk: UUID del StudentGuardian.

        Returns:
            Response: Vínculo actualizado (HTTP 200).
        """
        try:
            sg = StudentGuardian.objects.select_related(
                "student", "guardian"
            ).get(pk=pk)
        except (StudentGuardian.DoesNotExist, ValueError):
            raise SIGEAPIException(
                error_code="NOT_FOUND",
                message="Vínculo estudiante–tutor no encontrado.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        reason = request.data.get("reason", "").strip()
        if not reason:
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="El motivo de invalidación es obligatorio (RN-EST-11).",
                details={"reason": ["Este campo es requerido."]},
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        sg.is_valid_contact = False
        sg.invalid_reason = reason
        sg.save(update_fields=["is_valid_contact", "invalid_reason", "updated_at"])
        return _no_store_response(
            {
                "id": str(sg.id),
                "is_valid_contact": sg.is_valid_contact,
                "invalid_reason": sg.invalid_reason,
            },
            status.HTTP_200_OK,
        )


# ------------------------------------------------------------------
# PATCH /api/v1/student-guardians/{id}/consent/
# ------------------------------------------------------------------

class ConsentUpdateView(APIView):
    """Actualiza el estado de consentimiento de un tutor (§3.4, RN-EST-07).

    Genera un renglón en GuardianConsentLog en la misma transacción.

    Roles permitidos: ADM, PAD.
    """

    @extend_schema(
        operation_id="student_guardians_update_consent",
        summary="Actualizar consentimiento de tutor",
        description="Modifica consentimiento y genera renglón de auditoría en GUARDIAN_CONSENT_LOG (RN-EST-07).",
        request=ConsentUpdateSerializer,
        responses={200: inline_serializer("ConsentUpdateResponse", fields={"id": serializers.UUIDField(), "consent_status": serializers.CharField(), "previous_status": serializers.CharField(allow_null=True)})},
        tags=["Tutores"],
    )
    def patch(self, request: Request, pk: str) -> Response:
        """Cambia el estado de consentimiento y registra el historial.

        Args:
            request: Request con ``consent_status`` y ``reason`` opcional.
            pk: UUID del StudentGuardian.

        Returns:
            Response: Vínculo actualizado (HTTP 200).
        """
        try:
            sg = StudentGuardian.objects.get(pk=pk)
        except (StudentGuardian.DoesNotExist, ValueError):
            raise SIGEAPIException(
                error_code="NOT_FOUND",
                message="Vínculo estudiante–tutor no encontrado.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ConsentUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="Error de validación.",
                details=serializer.errors,
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = serializer.validated_data["consent_status"]
        with transaction.atomic():
            GuardianConsentLog.objects.create(
                student_guardian=sg,
                previous_status=sg.consent_status,
                new_status=new_status,
                registered_by=request.user if request.user.is_authenticated else None,
            )
            sg.consent_status = new_status
            sg.save(update_fields=["consent_status", "updated_at"])

        return _no_store_response(
            {
                "id": str(sg.id),
                "consent_status": sg.consent_status,
                "previous_status": GuardianConsentLog.objects.filter(
                    student_guardian=sg
                ).order_by("-registered_at").values_list(
                    "previous_status", flat=True
                ).first(),
            },
            status.HTTP_200_OK,
        )


# ------------------------------------------------------------------
# POST/GET /api/v1/students/{id}/photo/
# ------------------------------------------------------------------

class StudentPhotoView(APIView):
    """Carga y descarga autenticada de la fotografía del alumno (§2.4).

    POST: carga multipart; solo jpeg/png; sin EXIF (RN-TRX-02).
    GET:  descarga autenticada (nunca URL pública).

    Roles:
        POST: ADM, PAD.
        GET:  ADM, PRE, PAD.
    """

    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="students_upload_photo",
        summary="Cargar fotografía del estudiante",
        description="Carga de fotografía (JPEG/PNG) para credencialización y expediente institucional.",
        request=inline_serializer("PhotoUploadRequest", fields={"photo": serializers.FileField()}),
        responses={
            200: inline_serializer(
                "PhotoUploadResponse",
                fields={
                    "photo_url": serializers.CharField(),
                    "completeness": serializers.CharField(),
                    "active_qr_token_id": serializers.UUIDField(allow_null=True),
                },
            )
        },
        tags=["Estudiantes"],
    )
    def post(self, request: Request, pk: str) -> Response:
        """Carga la fotografía del estudiante.

        Args:
            request: Request multipart con el archivo ``photo``.
            pk: UUID del estudiante.

        Returns:
            Response: Confirmación con la URL interna (HTTP 200).
        """
        student = _get_student_or_404(pk)
        photo = request.FILES.get("photo")
        if not photo:
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="El campo 'photo' es obligatorio.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar tipo de contenido real
        allowed_types = {"image/jpeg", "image/png"}
        content_type = photo.content_type or ""
        if content_type not in allowed_types:
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message=(
                    f"Tipo de archivo no permitido: '{content_type}'. "
                    f"Solo se aceptan image/jpeg e image/png (RN-TRX-02)."
                ),
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        # Procesar, sanitizar, recortar con zoom a cabeza/hombros y guardar
        is_manual_crop = request.data.get("is_manual_crop") in (True, "true", "True", "1", 1)
        original_photo = request.FILES.get("original_photo")

        success, msg, sha256_hash = process_and_save_photo(
            student=student,
            file_bytes_or_obj=photo,
            filename=photo.name or f"{student.id}.jpg",
            is_manual_crop=is_manual_crop,
            original_photo_file=original_photo,
        )
        if not success:
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message=msg,
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        active_qr = student.active_qr_token
        active_qr_token_id = str(active_qr.token) if active_qr else None

        return _no_store_response(
            {
                "photo_url": f"/api/v1/students/{pk}/photo/",
                "photo_sha256": student.photo_sha256,
                "completeness": student.completeness,
                "completeness_display": student.get_completeness_display(),
                "active_qr_token_id": active_qr_token_id,
            },
            status.HTTP_200_OK,
        )

    @extend_schema(
        operation_id="students_download_photo",
        summary="Descargar fotografía del estudiante",
        description="Descarga autenticada de la fotografía institucional.",
        responses={200: inline_serializer("PhotoDownloadResponse", fields={"photo_url": serializers.CharField()})},
        tags=["Estudiantes"],
    )
    def get(self, request: Request, pk: str) -> Response:
        """Sirve la fotografía del estudiante (autenticada o renderizable en navegador).

        Args:
            request (Request): Request HTTP GET.
            pk (str): UUID del estudiante.

        Returns:
            Response: Flujo binario de imagen JPEG o 404 si no existe fotografía.
        """
        student = _get_student_or_404(pk)
        if not student.photo_url:
            raise SIGEAPIException(
                error_code="NOT_FOUND",
                message="Este estudiante no tiene fotografía registrada.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        # Si el cliente solicita explícitamente JSON:
        if request.query_params.get("format") == "json":
            return _no_store_response(
                {"photo_url": f"/api/v1/students/{pk}/photo/"},
                status.HTTP_200_OK,
            )

        # Si se solicita la toma original sin recorte (para edición manual de encuadre)
        is_original = request.query_params.get("original") in (
            "true",
            "1",
            True,
        ) or request.query_params.get("raw") in ("true", "1", True)

        # 1. Si se usa almacenamiento remoto en la nube (Supabase Storage / S3)
        if getattr(settings, "USE_SUPABASE_STORAGE", False):
            from django.core.files.storage import default_storage
            from django.http import HttpResponseRedirect
            target_key = f"students/originals/{student.id}.jpg" if is_original else student.photo_url
            try:
                remote_url = default_storage.url(target_key)
                return HttpResponseRedirect(remote_url)
            except Exception:
                pass

        # 2. Servir archivo desde disco local (desarrollo o fallback)
        if is_original and hasattr(settings, "MEDIA_ROOT"):
            orig_path = Path(settings.MEDIA_ROOT) / "students" / "originals" / f"{student.id}.jpg"
            if orig_path.exists() and orig_path.is_file():
                resp = FileResponse(open(orig_path, "rb"), content_type="image/jpeg")
                resp["Cache-Control"] = "no-store"
                return resp

        # Servir el archivo físico binario directamente
        full_path = Path(student.photo_url)
        if not full_path.is_absolute() and hasattr(settings, "MEDIA_ROOT"):
            full_path = Path(settings.MEDIA_ROOT) / student.photo_url

        if full_path.exists() and full_path.is_file():
            resp = FileResponse(open(full_path, "rb"), content_type="image/jpeg")
            resp["Cache-Control"] = "no-store"
            return resp

        raise SIGEAPIException(
            error_code="NOT_FOUND",
            message="El archivo de la fotografía no se encuentra disponible.",
            http_status=status.HTTP_404_NOT_FOUND,
        )

    @extend_schema(
        operation_id="students_delete_photo",
        summary="Eliminar fotografía del estudiante",
        description="Elimina la fotografía del expediente institucional y recalcula completitud (US-064).",
        responses={
            200: inline_serializer(
                "PhotoDeleteResponse",
                fields={
                    "message": serializers.CharField(),
                    "completeness": serializers.CharField(),
                    "completeness_display": serializers.CharField(),
                },
            )
        },
        tags=["Estudiantes"],
    )
    def delete(self, request: Request, pk: str) -> Response:
        """Elimina la fotografía del estudiante y limpia los campos asociados.

        Args:
            request (Request): Request HTTP DELETE.
            pk (str): UUID del estudiante.

        Returns:
            Response: Confirmación de eliminación y nuevo estado de completitud (HTTP 200).
        """
        student = _get_student_or_404(pk)

        if student.photo_url:
            full_path = Path(student.photo_url)
            if not full_path.is_absolute() and hasattr(settings, "MEDIA_ROOT"):
                full_path = Path(settings.MEDIA_ROOT) / student.photo_url
            if full_path.exists() and full_path.is_file():
                try:
                    full_path.unlink()
                except OSError:
                    pass

            # Eliminar también la copia original sin recortar si existe
            if hasattr(settings, "MEDIA_ROOT"):
                orig_path = Path(settings.MEDIA_ROOT) / "students" / "originals" / f"{student.id}.jpg"
                if orig_path.exists() and orig_path.is_file():
                    try:
                        orig_path.unlink()
                    except OSError:
                        pass

        student.photo_url = None
        student.photo_sha256 = None
        student.photo_updated_at = None
        student._recalculate_completeness()
        student.save(
            update_fields=[
                "photo_url",
                "photo_sha256",
                "photo_updated_at",
                "completeness",
                "updated_at",
            ]
        )

        return _no_store_response(
            {
                "message": "Fotografía eliminada exitosamente.",
                "completeness": student.completeness,
                "completeness_display": student.get_completeness_display(),
            },
            status.HTTP_200_OK,
        )


# ------------------------------------------------------------------
# GET /api/v1/students/groups/
# ------------------------------------------------------------------

class GroupListView(APIView):
    """Listado de grupos académicos con conteo de estudiantes matriculados.

    Permite al panel administrativo y a prefectura consultar el catálogo
    activo de grupos para filtrado por grupo en tablas y selectores de UI.
    """

    @extend_schema(
        operation_id="groups_list",
        summary="Listado de grupos académicos",
        description="Retorna la lista de grupos activos con el conteo de estudiantes asignados.",
        responses={200: GroupListSerializer(many=True)},
        tags=["Catálogos"],
    )
    def get(self, request: Request) -> Response:
        """Devuelve todos los grupos académicos ordenados por grado, grupo y turno.

        Args:
            request (Request): Request HTTP GET.

        Returns:
            Response: Lista JSON de grupos con display_name y student_count.
        """
        from django.db.models import Count

        groups = (
            GroupProxy.objects
            .filter(is_active=True)
            .annotate(student_count=Count("students"))
            .order_by("grade", "group_letter", "shift")
        )
        serializer = GroupListSerializer(groups, many=True)
        return _no_store_response(serializer.data, status.HTTP_200_OK)


# ------------------------------------------------------------------
# POST /api/v1/students/batch-photos/
# ------------------------------------------------------------------

class StudentBatchPhotoUploadView(APIView):
    """Carga masiva y vinculación automática de fotografías por lote (SIGE-US-064).

    Recibe múltiples archivos fotográficos (o un archivo ZIP), identifica
    a qué estudiante pertenece cada imagen según su nombre de archivo o matrícula,
    elimina metadatos EXIF por privacidad de menores (RN-TRX-02, RN-EST-16),
    almacena la imagen y actualiza la firma SHA-256 (RN-EST-15).
    """

    parser_classes = [MultiPartParser, FormParser]

    @extend_schema(
        operation_id="students_batch_upload_photos",
        summary="Carga masiva de fotografías de estudiantes",
        description=(
            "Asocia y actualiza automáticamente fotos de estudiantes a partir de "
            "los nombres de archivo de las imágenes recibidas o paquete ZIP (US-064)."
        ),
        request=inline_serializer(
            "BatchPhotoUploadRequest",
            fields={
                "photos": serializers.ListField(
                    child=serializers.FileField(),
                    required=False,
                    help_text="Lista de archivos fotográficos a procesar.",
                ),
                "zip_file": serializers.FileField(
                    required=False,
                    help_text="Paquete ZIP opcional con fotografías.",
                ),
                "grade": serializers.IntegerField(
                    required=False,
                    help_text="Grado escolar para limitar la búsqueda (1, 2 o 3).",
                ),
                "group": serializers.CharField(
                    required=False,
                    help_text="Letra de grupo (A, B, C, etc.).",
                ),
                "shift": serializers.CharField(
                    required=False,
                    help_text="Turno escolar (MATUTINO o VESPERTINO).",
                ),
                "overwrite": serializers.BooleanField(
                    required=False,
                    default=True,
                    help_text="Indica si se deben sobreescribir fotos existentes.",
                ),
            },
        ),
        responses={
            200: inline_serializer(
                "BatchPhotoUploadResponse",
                fields={
                    "total_received": serializers.IntegerField(),
                    "matched_count": serializers.IntegerField(),
                    "updated_count": serializers.IntegerField(),
                    "skipped_count": serializers.IntegerField(),
                    "unmatched_count": serializers.IntegerField(),
                    "results": serializers.ListField(child=serializers.DictField()),
                },
            )
        },
        tags=["Estudiantes"],
    )
    def post(self, request: Request) -> Response:
        """Procesa el lote de fotografías y las vincula a los estudiantes.

        Args:
            request (Request): Petición multipart con lista de archivos o zip_file.

        Returns:
            Response: Reporte detallado de asociación por alumno (HTTP 200).
        """
        import zipfile

        photos = request.FILES.getlist("photos") or request.FILES.getlist("files")
        zip_file = request.FILES.get("zip_file")

        # Extraer elementos a procesar: lista de tuplas (nombre, descriptor/bytes)
        file_items: list[tuple[str, Any]] = []

        for p in photos:
            file_items.append((p.name, p))

        if zip_file:
            try:
                with zipfile.ZipFile(zip_file, "r") as zf:
                    for zip_info in zf.infolist():
                        if zip_info.is_dir():
                            continue
                        name = Path(zip_info.filename).name
                        if name.startswith(".") or name.startswith("__MACOSX"):
                            continue
                        if name.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                            file_items.append((name, zf.read(zip_info)))
            except Exception as exc:
                raise SIGEAPIException(
                    error_code="INVALID_ZIP",
                    message=f"No se pudo descomprimir el archivo ZIP: {str(exc)}",
                    http_status=status.HTTP_400_BAD_REQUEST,
                )

        if not file_items:
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message="No se proporcionaron fotografías ni archivo ZIP válido para procesar.",
                http_status=status.HTTP_400_BAD_REQUEST,
            )

        # Parámetros opcionales de alcance
        grade = request.data.get("grade")
        group_letter = request.data.get("group")
        shift = request.data.get("shift")

        overwrite_raw = request.data.get("overwrite")
        overwrite_flag = True
        if overwrite_raw is not None:
            overwrite_flag = str(overwrite_raw).strip().lower() in (
                "true",
                "1",
                "yes",
                "t",
            )

        # Determinar candidatos prioritarios y de respaldo
        primary_candidates: list[Student]
        fallback_candidates: list[Student] | None = None

        if grade and group_letter and shift:
            primary_candidates = list(
                Student.objects.filter(
                    grade=int(grade),
                    group_letter=str(group_letter).strip().upper(),
                    shift=str(shift).strip().upper(),
                )
            )
            fallback_candidates = list(
                Student.objects.exclude(
                    grade=int(grade),
                    group_letter=str(group_letter).strip().upper(),
                    shift=str(shift).strip().upper(),
                )
            )
        else:
            primary_candidates = list(Student.objects.all())
            fallback_candidates = None

        total_received = len(file_items)
        matched_count = 0
        updated_count = 0
        skipped_count = 0
        unmatched_count = 0
        results: list[dict[str, Any]] = []

        for filename, file_data in file_items:
            matched_student, score, reason = find_matching_student(
                filename, primary_candidates, fallback_candidates
            )

            if not matched_student:
                unmatched_count += 1
                results.append(
                    {
                        "filename": filename,
                        "status": "UNMATCHED",
                        "message": reason,
                        "student_id": None,
                        "student_name": None,
                        "enrollment_id": None,
                        "group": None,
                    }
                )
                continue

            matched_count += 1
            has_photo = bool(matched_student.photo_url)

            # Si ya cuenta con foto y no se solicitó sobreescribir
            if has_photo and not overwrite_flag:
                skipped_count += 1
                results.append(
                    {
                        "filename": filename,
                        "status": "SKIPPED",
                        "message": (
                            "El estudiante ya cuenta con fotografía institucional "
                            "y se especificó conservar la existente."
                        ),
                        "student_id": str(matched_student.id),
                        "student_name": matched_student.display_name,
                        "enrollment_id": matched_student.enrollment_id,
                        "group": f"{matched_student.grade}°{matched_student.group_letter} {matched_student.get_shift_display()}",
                    }
                )
                continue

            success, msg, sha256_val = process_and_save_photo(
                matched_student, file_data, filename
            )

            if success:
                updated_count += 1
                results.append(
                    {
                        "filename": filename,
                        "status": "SUCCESS",
                        "message": f"{msg} · {reason}",
                        "student_id": str(matched_student.id),
                        "student_name": matched_student.display_name,
                        "enrollment_id": matched_student.enrollment_id,
                        "group": f"{matched_student.grade}°{matched_student.group_letter} {matched_student.get_shift_display()}",
                        "active_qr_token_id": (
                            str(matched_student.active_qr_token.token)
                            if matched_student.active_qr_token
                            else None
                        ),
                    }
                )
            else:
                results.append(
                    {
                        "filename": filename,
                        "status": "ERROR",
                        "message": msg,
                        "student_id": str(matched_student.id),
                        "student_name": matched_student.display_name,
                        "enrollment_id": matched_student.enrollment_id,
                        "group": f"{matched_student.grade}°{matched_student.group_letter} {matched_student.get_shift_display()}",
                    }
                )

        response_payload = {
            "total_received": total_received,
            "matched_count": matched_count,
            "updated_count": updated_count,
            "skipped_count": skipped_count,
            "unmatched_count": unmatched_count,
            "results": results,
        }

        return _no_store_response(response_payload, status.HTTP_200_OK)

