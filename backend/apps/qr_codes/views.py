import uuid
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
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

        token_obj = QRCodeToken.objects.select_related('student', 'student__guardian').filter(token=token_uuid).first()

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
                "group": student.group,
                "shift": student.shift,
                "academic_group": student.academic_group,
                "status": student.status,
                "medical_notes": student.medical_notes,
                "guardian": {
                    "id": str(student.guardian.id),
                    "full_name": student.guardian.full_name,
                    "phone_number": student.guardian.phone_number,
                    "relationship": student.guardian.get_relationship_display(),
                }
            }
        }, status=status.HTTP_200_OK)


class RenderQRImageView(APIView):
    """
    Retorna el flujo binario PNG del código QR listo para renderizado
    en plantillas de credenciales o etiquetas térmicas.
    """
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
