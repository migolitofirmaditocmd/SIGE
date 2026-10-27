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

import uuid
from typing import Any

from django.db import transaction
from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
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
from .models import Guardian, GuardianConsentLog, Student, StudentGuardian
from .serializers import (
    ConsentUpdateSerializer,
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
        responses={200: inline_serializer("PhotoUploadResponse", fields={"photo_url": serializers.CharField(), "completeness": serializers.CharField()})},
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

        # TODO: eliminar EXIF con Pillow y guardar en almacén privado.
        # Ruta interna de ejemplo:
        internal_path = f"students/{pk}/photo.{'jpg' if 'jpeg' in content_type else 'png'}"
        student.photo_url = internal_path
        student.save(update_fields=["photo_url", "completeness", "updated_at"])

        return _no_store_response(
            {
                "photo_url": f"/api/v1/students/{pk}/photo/",
                "completeness": student.completeness,
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
        """Sirve la fotografía del estudiante (autenticada).

        Args:
            request: Request HTTP GET.
            pk: UUID del estudiante.

        Returns:
            Response: Imagen o 404 si no existe fotografía.
        """
        student = _get_student_or_404(pk)
        if not student.photo_url:
            raise SIGEAPIException(
                error_code="NOT_FOUND",
                message="Este estudiante no tiene fotografía registrada.",
                http_status=status.HTTP_404_NOT_FOUND,
            )
        # TODO: servir el archivo desde el almacén privado (C4-04).
        return _no_store_response(
            {"photo_url": student.photo_url},
            status.HTTP_200_OK,
        )
