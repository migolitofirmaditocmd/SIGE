import uuid
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.students.models import Student
from .models import QRCodeToken
from .crypto import (
    issue_qr_token_for_student,
    generate_qr_image_bytes,
    verify_token_hmac
)

class ValidateQRTokenView(APIView):
    """
    Endpoint de resolución y validación óptica de tokens QR escaneados.
    Utilizado por la PWA móvil y estaciones fijas de prefectura.
    Retorna los datos del alumno solo si el token es válido y está ACTIVO.
    """
    @extend_schema(
        operation_id="qr_validate",
        summary="Validar token QR escaneado",
        description="Resuelve y valida un código QR escaneado por prefectura o docentes.",
        request=inline_serializer("QRValidateRequest", fields={"token": serializers.UUIDField()}),
        responses={200: inline_serializer("QRValidateResponse", fields={
            "valid": serializers.BooleanField(),
            "status": serializers.CharField(),
            "token": serializers.CharField(),
            "issued_at": serializers.DateTimeField(),
            "student": serializers.DictField(),
        })},
        tags=["Códigos QR"],
    )
    def post(self, request):
        token_str = request.data.get('token')
        if not token_str:
            return Response(
                {"error": "El parámetro 'token' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token_uuid = uuid.UUID(str(token_str).strip())
        except ValueError:
            return Response(
                {"error": "El formato del token no es un UUIDv4 válido.", "valid": False},
                status=status.HTTP_400_BAD_REQUEST
            )

        token_obj = (
            QRCodeToken.objects
            .select_related('student')
            .prefetch_related('student__student_guardians__guardian')
            .filter(token=token_uuid)
            .first()
        )

        if not token_obj:
            return Response(
                {"error": "Código QR no registrado en el sistema institucional.", "valid": False},
                status=status.HTTP_404_NOT_FOUND
            )

        if token_obj.status == QRCodeToken.Status.REVOKED:
            return Response(
                {
                    "error": "Esta credencial ha sido REVOCADA por extravío o reposición.",
                    "valid": False,
                    "status": "REVOKED",
                    "revocation_reason": token_obj.revocation_reason
                },
                status=status.HTTP_409_CONFLICT
            )

        if token_obj.status == QRCodeToken.Status.EXPIRED:
            return Response(
                {"error": "Esta credencial ha EXPIRADO.", "valid": False, "status": "EXPIRED"},
                status=status.HTTP_410_GONE
            )

        # Verificación criptográfica opcional de integridad interna
        is_signature_valid = verify_token_hmac(token_obj.token, token_obj.hmac_signature)
        if not is_signature_valid:
            return Response(
                {"error": "Fallo de integridad criptográfica en la credencial.", "valid": False},
                status=status.HTTP_400_BAD_REQUEST
            )

        student = token_obj.student
        primary_sg = (
            student.student_guardians.filter(is_primary_contact=True).first()
            or student.student_guardians.first()
        )
        guardian_info = None
        if primary_sg and primary_sg.guardian:
            guardian_info = {
                "id": str(primary_sg.guardian.id),
                "full_name": primary_sg.guardian.display_name,
                "phone_number": primary_sg.guardian.phone_number,
                "relationship": primary_sg.get_relationship_display(),
            }

        return Response({
            "valid": True,
            "status": "ACTIVE",
            "token": str(token_obj.token),
            "issued_at": token_obj.issued_at,
            "student": {
                "id": str(student.id),
                "enrollment_id": student.enrollment_id,
                "curp": student.curp,
                "full_name": student.full_name,
                "grade": student.grade,
                "group": student.group_letter or "",
                "shift": student.shift,
                "academic_group": student.academic_group,
                "status": student.status,
                "medical_notes": student.medical_notes,
                "guardian": guardian_info,
            }
        }, status=status.HTTP_200_OK)


class RenderQRImageView(APIView):
    """
    Retorna el flujo binario PNG del código QR listo para renderizado
    en plantillas de credenciales o etiquetas térmicas.
    """
    @extend_schema(
        operation_id="qr_render_image",
        summary="Renderizar imagen PNG de código QR",
        description="Retorna el PNG binario del código QR de la credencial.",
        parameters=[
            OpenApiParameter("high_res", bool, description="Generar en alta resolución para credencial impresa"),
        ],
        responses={(200, "image/png"): bytes},
        tags=["Códigos QR"],
    )
    def get(self, request, token):
        token_obj = get_object_or_404(QRCodeToken, token=token)
        high_res = request.query_params.get('high_res', 'false').lower() == 'true'
        box_size = 14 if high_res else 10

        image_bytes = generate_qr_image_bytes(token_obj.token, box_size=box_size)
        return HttpResponse(image_bytes, content_type="image/png")


class IssueQRTokenView(APIView):
    """
    Emite o renueva el código QR de un estudiante, revocando automáticamente el anterior.
    """
    @extend_schema(
        operation_id="qr_issue_token",
        summary="Emitir o renovar credencial QR",
        description="Genera un nuevo token QR firmado con HMAC-SHA256 y revoca el anterior si existía.",
        request=inline_serializer("QRIssueRequest", fields={
            "student_id": serializers.UUIDField(),
            "reason": serializers.CharField(required=False, default="Emisión por sistema"),
        }),
        responses={201: inline_serializer("QRIssueResponse", fields={
            "message": serializers.CharField(),
            "token": serializers.CharField(),
            "status": serializers.CharField(),
            "hmac_signature": serializers.CharField(),
            "issued_at": serializers.DateTimeField(),
            "student_id": serializers.CharField(),
            "enrollment_id": serializers.CharField(),
        })},
        tags=["Códigos QR"],
    )
    def post(self, request):
        student_id = request.data.get('student_id')
        reason = request.data.get('reason', 'Emisión por sistema')

        if not student_id:
            return Response(
                {"error": "El parámetro 'student_id' es obligatorio."},
                status=status.HTTP_400_BAD_REQUEST
            )

        student = get_object_or_404(Student, id=student_id)
        new_token = issue_qr_token_for_student(student, reason=reason)

        return Response({
            "message": "Token QR emitido satisfactoriamente.",
            "token": str(new_token.token),
            "status": new_token.status,
            "hmac_signature": new_token.hmac_signature,
            "issued_at": new_token.issued_at,
            "student_id": str(student.id),
            "enrollment_id": student.enrollment_id
        }, status=status.HTTP_201_CREATED)
