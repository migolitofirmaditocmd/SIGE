import uuid
import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from apps.students.models import Guardian, Student
from apps.qr_codes.models import QRCodeToken
from apps.qr_codes.crypto import (
    calculate_token_hmac,
    verify_token_hmac,
    issue_qr_token_for_student,
    generate_qr_image_bytes
)

class TestQRCryptoEngine(TestCase):
    def setUp(self):
        self.guardian = Guardian.objects.create(
            full_name="Rosa Silva Ramos",
            phone_number="3322114455",
            relationship=Guardian.Relationship.MADRE
        )
        self.student = Student.objects.create(
            enrollment_id="2026-1C-015",
            curp="SIRR091102MJCXRX04",
            first_name="Valeria",
            last_name_father="Silva",
            last_name_mother="Ramos",
            grade=1,
            group="C",
            guardian=self.guardian
        )

    def test_hmac_calculation_and_verification(self):
        sample_uuid = uuid.uuid4()
        sig = calculate_token_hmac(sample_uuid)
        assert len(sig) == 64  # SHA-256 produce 64 caracteres hexadecimales
        assert verify_token_hmac(sample_uuid, sig) is True

        # Firma manipulada o errónea
        tampered_sig = "a" * 64
        assert verify_token_hmac(sample_uuid, tampered_sig) is False

    def test_issue_qr_token_and_uniqueness(self):
        token1 = issue_qr_token_for_student(self.student, reason="Credencial inicial")
        assert token1.status == QRCodeToken.Status.ACTIVE
        assert token1.hmac_signature != ""
        assert verify_token_hmac(token1.token, token1.hmac_signature) is True
        assert self.student.active_qr_token.id == token1.id

        # Re-emisión por extravío
        token2 = issue_qr_token_for_student(self.student, reason="Reposición por extravío")
        token1.refresh_from_db()

        # El anterior debe haber sido revocado atómicamente
        assert token1.status == QRCodeToken.Status.REVOKED
        assert token1.revoked_at is not None
        assert "Reemplazado por nueva emisión" in token1.revocation_reason

        # El nuevo debe ser el único activo
        assert token2.status == QRCodeToken.Status.ACTIVE
        assert self.student.active_qr_token.id == token2.id

    def test_generate_qr_image_png_header(self):
        token = issue_qr_token_for_student(self.student)
        png_bytes = generate_qr_image_bytes(token.token)
        # Cabecera mágica obligatoria de archivos PNG: 89 50 4E 47 0D 0A 1A 0A
        assert png_bytes[:8] == b'\x89PNG\r\n\x1a\n'


class TestQRAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.guardian = Guardian.objects.create(
            full_name="Fernando López Soto",
            phone_number="3399887766",
            relationship=Guardian.Relationship.PADRE
        )
        self.student = Student.objects.create(
            enrollment_id="2026-3C-099",
            curp="LOSF070101HJCXRX08",
            first_name="Diego",
            last_name_father="López",
            last_name_mother="Soto",
            grade=3,
            group="C",
            guardian=self.guardian
        )
        self.active_token = issue_qr_token_for_student(self.student)

    def test_validate_active_qr(self):
        response = self.client.post("/api/v1/qr/validate/", {"token": str(self.active_token.token)}, format="json")
        assert response.status_code == 200
        assert response.data["valid"] is True
        assert response.data["student"]["enrollment_id"] == "2026-3C-099"
        assert response.data["student"]["full_name"] == "López Soto Diego"
        assert response.data["student"]["guardian"]["full_name"] == "Fernando López Soto"

    def test_validate_revoked_qr(self):
        # Revocar el token
        self.active_token.revoke(reason="Credencial reportada como extraviada")
        response = self.client.post("/api/v1/qr/validate/", {"token": str(self.active_token.token)}, format="json")
        assert response.status_code == 409
        assert response.data["valid"] is False
        assert response.data["status"] == "REVOKED"

    def test_validate_nonexistent_qr(self):
        fake_uuid = str(uuid.uuid4())
        response = self.client.post("/api/v1/qr/validate/", {"token": fake_uuid}, format="json")
        assert response.status_code == 404
        assert response.data["valid"] is False

    def test_render_qr_image_endpoint(self):
        url = f"/api/v1/qr/{self.active_token.token}/image/"
        response = self.client.get(url)
        assert response.status_code == 200
        assert response["Content-Type"] == "image/png"
        assert response.content[:8] == b'\x89PNG\r\n\x1a\n'

    def test_issue_qr_endpoint(self):
        response = self.client.post(
            "/api/v1/qr/issue/",
            {"student_id": str(self.student.id), "reason": "Emisión desde prueba"},
            format="json"
        )
        assert response.status_code == 201
        assert response.data["status"] == "ACTIVE"
        assert "token" in response.data
