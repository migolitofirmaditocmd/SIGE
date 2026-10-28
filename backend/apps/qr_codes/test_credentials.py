"""Tests del módulo de credenciales y exportación (WBS 3.11).

Cubre los criterios de aceptación y especificaciones técnicas:
    - Generación de plantilla institucional oficial (CR-80: 85.6 mm × 53.98 mm).
    - Renderizado de alta resolución del código QR.
    - Generación de documentos PDF multi-página por grupo para impresión masiva.
    - Exportación en formato imagen (PNG) para previsualización.
    - Reglas de negocio RN-CRE-01, RF-CRE-01, RF-CRE-02.
    - Cabeceras de seguridad y no almacenamiento en servidor (RN-TRX-01, RN-TRX-02).
"""

import uuid
import pytest
from rest_framework import status
from rest_framework.test import APIClient

from apps.qr_codes.card_generator import (
    CR80_HEIGHT_MM,
    CR80_WIDTH_MM,
    STICKER_HEIGHT_MM,
    STICKER_WIDTH_MM,
    generate_credential_pdf,
    generate_credential_png,
    generate_qr_pil_image,
)
from apps.qr_codes.crypto import issue_qr_token_for_student
from apps.qr_codes.models import QRCodeToken
from apps.students.models import Guardian, Student, StudentGuardian


@pytest.fixture
def client() -> APIClient:
    """Fixture de cliente de pruebas de DRF."""
    return APIClient()


@pytest.fixture
def sample_guardian() -> Guardian:
    """Fixture de tutor legal de prueba."""
    return Guardian.objects.create(
        first_name="Guadalupe",
        last_name_father="Ramos",
        last_name_mother="Vega",
        phone_number="3312345678",
        email="guadalupe.ramos@example.com",
    )


@pytest.fixture
def active_student_with_photo(sample_guardian: Guardian) -> Student:
    """Fixture de estudiante activo con foto y QR emitido."""
    student = Student.objects.create(
        enrollment_id="2026-1A-001",
        curp="RAGV090815HJCXRN01",
        first_name="Carlos",
        last_name_father="Ramos",
        last_name_mother="Vega",
        grade=1,
        group_letter="A",
        shift="MATUTINO",
        status=Student.Status.ACTIVO,
        photo_url="students/test_photo.jpg",
    )
    StudentGuardian.objects.create(
        student=student,
        guardian=sample_guardian,
        relationship=StudentGuardian.Relationship.PADRE,
        is_primary_contact=True,
    )
    issue_qr_token_for_student(student, reason="Credencial inicial")
    return student


@pytest.fixture
def active_student_without_photo(sample_guardian: Guardian) -> Student:
    """Fixture de estudiante activo con QR pero SIN foto (incompleto)."""
    student = Student.objects.create(
        enrollment_id="2026-1A-002",
        curp="RAGV090815HJCXRN02",
        first_name="Sofía",
        last_name_father="Ramos",
        last_name_mother="Vega",
        grade=1,
        group_letter="A",
        shift="MATUTINO",
        status=Student.Status.ACTIVO,
        photo_url=None,
    )
    StudentGuardian.objects.create(
        student=student,
        guardian=sample_guardian,
        relationship=StudentGuardian.Relationship.MADRE,
        is_primary_contact=True,
    )
    issue_qr_token_for_student(student, reason="Sticker provisional")
    return student


@pytest.fixture
def inactive_student(sample_guardian: Guardian) -> Student:
    """Fixture de estudiante en estatus BAJA."""
    student = Student.objects.create(
        enrollment_id="2026-1A-003",
        curp="RAGV090815HJCXRN03",
        first_name="Mateo",
        last_name_father="Ramos",
        last_name_mother="Vega",
        grade=1,
        group_letter="A",
        shift="MATUTINO",
        status=Student.Status.BAJA,
    )
    StudentGuardian.objects.create(
        student=student,
        guardian=sample_guardian,
        relationship=StudentGuardian.Relationship.TUTOR_LEGAL,
    )
    return student


# ----------------------------------------------------------------------
# 1. Pruebas del motor gráfico de renderizado (card_generator.py)
# ----------------------------------------------------------------------

@pytest.mark.django_db
class TestCredentialCardGenerator:
    """Pruebas unitarias del motor de renderizado de credenciales en PDF y PNG."""

    def test_generate_qr_pil_image_properties(self) -> None:
        """Verifica que el QR generado sea válido y en modo RGB puro."""
        token_uuid = uuid.uuid4()
        img = generate_qr_pil_image(token_uuid, box_size=6, border=1)
        assert img.mode == "RGB"
        assert img.width > 50
        assert img.height > 50

    def test_generate_credential_png_header_and_dimensions(
        self, active_student_with_photo: Student
    ) -> None:
        """La credencial en PNG genera cabecera válida y dimensiones estándar CR-80 a 300 DPI."""
        data = {
            "display_name": active_student_with_photo.display_name,
            "enrollment_id": active_student_with_photo.enrollment_id,
            "academic_group": active_student_with_photo.academic_group,
            "curp": active_student_with_photo.curp,
            "token": str(active_student_with_photo.active_qr_token.token),
            "photo_url": active_student_with_photo.photo_url,
        }
        png_bytes = generate_credential_png(data, mode="CREDENCIAL")
        # Cabecera mágica de PNG
        assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"
        assert len(png_bytes) > 10000

    def test_generate_sticker_png_header(
        self, active_student_without_photo: Student
    ) -> None:
        """El sticker en PNG genera cabecera válida sin requerir fotografía."""
        data = {
            "display_name": active_student_without_photo.display_name,
            "enrollment_id": active_student_without_photo.enrollment_id,
            "academic_group": active_student_without_photo.academic_group,
            "token": str(active_student_without_photo.active_qr_token.token),
        }
        png_bytes = generate_credential_png(data, mode="STICKER")
        assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"
        assert len(png_bytes) > 5000

    def test_generate_credential_pdf_multipage_batch(
        self,
        active_student_with_photo: Student,
        active_student_without_photo: Student,
    ) -> None:
        """La generación de PDF por lote produce un documento con cabecera %PDF- y múltiples páginas."""
        students_data = [
            {
                "display_name": active_student_with_photo.display_name,
                "enrollment_id": active_student_with_photo.enrollment_id,
                "academic_group": active_student_with_photo.academic_group,
                "curp": active_student_with_photo.curp,
                "token": str(active_student_with_photo.active_qr_token.token),
                "photo_url": active_student_with_photo.photo_url,
            },
            {
                "display_name": active_student_without_photo.display_name,
                "enrollment_id": active_student_without_photo.enrollment_id,
                "academic_group": active_student_without_photo.academic_group,
                "curp": active_student_without_photo.curp,
                "token": str(active_student_without_photo.active_qr_token.token),
                "photo_url": None,
            },
        ]
        pdf_bytes = generate_credential_pdf(students_data, mode="CREDENCIAL")
        assert pdf_bytes[:4] == b"%PDF"
        assert len(pdf_bytes) > 20000


# ----------------------------------------------------------------------
# 2. Pruebas de reglas de inclusión y exclusión (CredentialExportService)
# ----------------------------------------------------------------------

@pytest.mark.django_db
class TestCredentialExportService:
    """Pruebas de validación de reglas de negocio para exportación (RN-CRE-01)."""

    def test_credencial_mode_excludes_student_without_photo(
        self,
        active_student_with_photo: Student,
        active_student_without_photo: Student,
    ) -> None:
        """En modo CREDENCIAL, el estudiante sin foto es excluido con SIN_FOTOGRAFIA (RN-CRE-01)."""
        from apps.qr_codes.credentials_service import CredentialExportService

        result = CredentialExportService.evaluate_export_candidates(
            mode="CREDENCIAL",
            entity_ids=[str(active_student_with_photo.id), str(active_student_without_photo.id)],
        )
        assert result["included"] == 1
        assert len(result["excluded"]) == 1
        assert result["excluded"][0]["entity_id"] == str(active_student_without_photo.id)
        assert result["excluded"][0]["reason"] == "SIN_FOTOGRAFIA"

    def test_sticker_mode_includes_student_without_photo(
        self,
        active_student_with_photo: Student,
        active_student_without_photo: Student,
    ) -> None:
        """En modo STICKER, la fotografía no es obligatoria y ambos son incluidos (RN-CRE-01)."""
        from apps.qr_codes.credentials_service import CredentialExportService

        result = CredentialExportService.evaluate_export_candidates(
            mode="STICKER",
            entity_ids=[str(active_student_with_photo.id), str(active_student_without_photo.id)],
        )
        assert result["included"] == 2
        assert len(result["excluded"]) == 0

    def test_inactive_student_is_excluded_with_no_activo(
        self, inactive_student: Student
    ) -> None:
        """Estudiantes en estatus BAJA son excluidos con motivo NO_ACTIVO (RN-CRE-01)."""
        from apps.qr_codes.credentials_service import CredentialExportService

        result = CredentialExportService.evaluate_export_candidates(
            mode="STICKER",
            entity_ids=[str(inactive_student.id)],
        )
        assert result["included"] == 0
        assert len(result["excluded"]) == 1
        assert result["excluded"][0]["reason"] == "NO_ACTIVO"

    def test_student_without_active_qr_is_excluded(
        self, sample_guardian: Guardian
    ) -> None:
        """Estudiante activo sin QR vigente se excluye con SIN_QR_VIGENTE (RN-CRE-01)."""
        from apps.qr_codes.credentials_service import CredentialExportService

        student_no_qr = Student.objects.create(
            enrollment_id="2026-1A-999",
            first_name="Sin",
            last_name_father="QR",
            grade=1,
            group_letter="A",
            status=Student.Status.ACTIVO,
            photo_url="students/photo.jpg",
        )
        result = CredentialExportService.evaluate_export_candidates(
            mode="CREDENCIAL",
            entity_ids=[str(student_no_qr.id)],
        )
        assert result["included"] == 0
        assert len(result["excluded"]) == 1
        assert result["excluded"][0]["reason"] == "SIN_QR_VIGENTE"

    def test_mutual_exclusion_of_entity_ids_and_group_id(self) -> None:
        """Enviar ambos parámetros o ninguno provoca error de validación (HTTP 422)."""
        from apps.core.exceptions import SIGEAPIException
        from apps.qr_codes.credentials_service import CredentialExportService

        # Ambos enviados
        with pytest.raises(SIGEAPIException) as exc:
            CredentialExportService.evaluate_export_candidates(
                mode="CREDENCIAL",
                entity_ids=[str(uuid.uuid4())],
                group_id="A",
            )
        assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Ninguno enviado
        with pytest.raises(SIGEAPIException) as exc2:
            CredentialExportService.evaluate_export_candidates(
                mode="CREDENCIAL",
                entity_ids=None,
                group_id=None,
            )
        assert exc2.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ----------------------------------------------------------------------
# 3. Pruebas de Endpoints de la API REST (credentials_views.py)
# ----------------------------------------------------------------------

@pytest.mark.django_db
class TestCredentialExportEndpoints:
    """Pruebas de integración sobre los endpoints /api/v1/credentials/*."""

    def test_preview_endpoint_returns_counts_and_exclusions(
        self,
        client: APIClient,
        active_student_with_photo: Student,
        active_student_without_photo: Student,
    ) -> None:
        """POST /api/v1/credentials/exports/preview/ devuelve conteo y detalle (§2.3)."""
        payload = {
            "mode": "CREDENCIAL",
            "entity_ids": [str(active_student_with_photo.id), str(active_student_without_photo.id)],
        }
        resp = client.post("/api/v1/credentials/exports/preview/", payload, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp.data["included"] == 1
        assert len(resp.data["excluded"]) == 1
        assert resp.data["excluded"][0]["reason"] == "SIN_FOTOGRAFIA"
        assert resp["Cache-Control"] == "no-store"

    def test_download_pdf_batch_returns_binary_stream(
        self,
        client: APIClient,
        active_student_with_photo: Student,
    ) -> None:
        """POST /api/v1/credentials/exports/ con formato PDF retorna archivo binario con headers seguros."""
        payload = {
            "mode": "CREDENCIAL",
            "format": "PDF",
            "entity_ids": [str(active_student_with_photo.id)],
        }
        resp = client.post("/api/v1/credentials/exports/", payload, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp["Content-Type"] == "application/pdf"
        assert "attachment; filename=" in resp["Content-Disposition"]
        assert resp["Cache-Control"] == "no-store"
        assert resp.content[:4] == b"%PDF"

    def test_download_png_single_returns_image_stream(
        self,
        client: APIClient,
        active_student_with_photo: Student,
    ) -> None:
        """POST /api/v1/credentials/exports/ con formato PNG para una sola persona retorna imagen PNG."""
        payload = {
            "mode": "CREDENCIAL",
            "format": "PNG",
            "entity_ids": [str(active_student_with_photo.id)],
        }
        resp = client.post("/api/v1/credentials/exports/", payload, format="json")
        assert resp.status_code == status.HTTP_200_OK
        assert resp["Content-Type"] == "image/png"
        assert resp["Cache-Control"] == "no-store"
        assert resp.content[:8] == b"\x89PNG\r\n\x1a\n"

    def test_download_png_with_multiple_students_fails_422(
        self,
        client: APIClient,
        active_student_with_photo: Student,
        sample_guardian: Guardian,
    ) -> None:
        """PNG con más de una persona es rechazado con HTTP 422 VALIDATION_ERROR (§2.3)."""
        other_student = Student.objects.create(
            enrollment_id="2026-1A-088",
            first_name="Otro",
            last_name_father="Alumno",
            grade=1,
            group_letter="A",
            status=Student.Status.ACTIVO,
            photo_url="students/other.jpg",
        )
        issue_qr_token_for_student(other_student)

        payload = {
            "mode": "CREDENCIAL",
            "format": "PNG",
            "entity_ids": [str(active_student_with_photo.id), str(other_student.id)],
        }
        resp = client.post("/api/v1/credentials/exports/", payload, format="json")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.data["error_code"] == "VALIDATION_ERROR"

    def test_download_with_zero_included_fails_422(
        self, client: APIClient, inactive_student: Student
    ) -> None:
        """Si ninguna persona cumple los requisitos, devuelve 422 BUSINESS_RULE_VIOLATION (§2.3)."""
        payload = {
            "mode": "CREDENCIAL",
            "format": "PDF",
            "entity_ids": [str(inactive_student.id)],
        }
        resp = client.post("/api/v1/credentials/exports/", payload, format="json")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.data["error_code"] == "BUSINESS_RULE_VIOLATION"


# ----------------------------------------------------------------------
# 4. Pruebas de emisión de tokens QR (POST /api/v1/credentials/tokens/)
# ----------------------------------------------------------------------

@pytest.mark.django_db
class TestCredentialTokenAPI:
    """Pruebas del endpoint de emisión y reposición de credenciales."""

    def test_initial_token_issue_succeeds(
        self, client: APIClient, sample_guardian: Guardian
    ) -> None:
        """Emisión inicial para estudiante sin QR devuelve HTTP 201."""
        student = Student.objects.create(
            enrollment_id="2026-2B-010",
            first_name="Alejandro",
            last_name_father="Gómez",
            grade=2,
            group_letter="B",
            status=Student.Status.ACTIVO,
        )
        payload = {
            "entity_type": "STUDENT",
            "entity_id": str(student.id),
        }
        resp = client.post("/api/v1/credentials/tokens/", payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert "token" in resp.data
        assert resp.data["status"] == "ACTIVE"
        assert resp.data["enrollment_id"] == "2026-2B-010"

    def test_replacement_without_reason_fails_422(
        self, client: APIClient, active_student_with_photo: Student
    ) -> None:
        """Reemplazo de un QR vigente exige motivo obligatorio (RN-QR-03)."""
        payload = {
            "entity_type": "STUDENT",
            "entity_id": str(active_student_with_photo.id),
            "reason": "",  # Vacío
        }
        resp = client.post("/api/v1/credentials/tokens/", payload, format="json")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.data["error_code"] == "VALIDATION_ERROR"

    def test_replacement_with_reason_revokes_previous(
        self, client: APIClient, active_student_with_photo: Student
    ) -> None:
        """Reemplazo con motivo revoca el token anterior y emite uno nuevo (RN-QR-01/03)."""
        old_token = active_student_with_photo.active_qr_token
        payload = {
            "entity_type": "STUDENT",
            "entity_id": str(active_student_with_photo.id),
            "reason": "Credencial extraviada en patio cívico",
        }
        resp = client.post("/api/v1/credentials/tokens/", payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED

        old_token.refresh_from_db()
        assert old_token.status == QRCodeToken.Status.REVOKED
        assert str(resp.data["token"]) != str(old_token.token)

    def test_token_issue_for_inactive_student_fails_422(
        self, client: APIClient, inactive_student: Student
    ) -> None:
        """Estudiante inactivo no puede recibir credencial (RN-EST-05)."""
        payload = {
            "entity_type": "STUDENT",
            "entity_id": str(inactive_student.id),
        }
        resp = client.post("/api/v1/credentials/tokens/", payload, format="json")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.data["error_code"] == "STUDENT_NOT_ACTIVE"
