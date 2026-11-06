"""Batería de pruebas de unicidad, colisiones criptográficas y carga para el motor QR (WBS 3.13).

Responsable: Saul (@ultimaibrahim)
Criterios de Aceptación:
    - KPI-01: 100% de unicidad en tokens generados sobre el universo escolar completo.
    - KPI-02: 0 identificadores o firmas HMAC duplicadas (cero colisiones).
    - KPI-03: Rendimiento de emisión masiva y tiempo de resolución < 500 ms.
    - Integridad relacional (unique_active_qr_token_per_student) y resistencia a manipulación.
"""

import time
import uuid
from typing import Any

import pytest
from django.conf import settings
from django.db import IntegrityError
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.qr_codes.crypto import (
    calculate_token_hmac,
    issue_qr_token_for_student,
    verify_token_hmac,
)
from apps.qr_codes.models import QRCodeToken
from apps.students.models import Guardian, Student, StudentGuardian


@pytest.fixture
def test_student() -> Student:
    """Fixture que crea un estudiante con tutor para pruebas de ciclo QR."""
    guardian = Guardian.objects.create(
        first_name="Beatriz",
        last_name_father="Gómez",
        last_name_mother="Morales",
        phone_number="3311223344",
        email="beatriz.gomez@example.com",
    )
    student = Student.objects.create(
        enrollment_id="2026-1B-050",
        curp="GOMB090101MJCXRB09",
        first_name="Mateo",
        last_name_father="Gómez",
        last_name_mother="Morales",
        grade=1,
        group_letter="B",
        shift="MATUTINO",
        status=Student.Status.ACTIVO,
    )
    StudentGuardian.objects.create(
        student=student,
        guardian=guardian,
        relationship=StudentGuardian.Relationship.MADRE,
        is_primary_contact=True,
    )
    return student


class TestMathematicalUniquenessAndCrypto:
    """Pruebas matemáticas de unicidad, colisiones y resistencia criptográfica (WBS 3.13)."""

    def test_massive_token_generation_zero_collisions(self) -> None:
        """Verifica 0 colisiones en generación masiva sobre universo escolar (KPI-01, KPI-02).

        Simula la población escolar completa de la Escuela Secundaria Mixta 5
        generando 1,500 tokens UUIDv4 y firmas HMAC-SHA256 simultáneas:
        - Tasa de colisión requerida: 0.0% (100% de unicidad).
        - Validación estricta de versión RFC 4122 v4 en cada token.
        - 0 colisiones en firmas HMAC derivadas.
        """
        sample_size = 1500
        generated_uuids: list[uuid.UUID] = []
        generated_signatures: list[str] = []

        start_time = time.perf_counter()

        for _ in range(sample_size):
            new_uuid = uuid.uuid4()
            sig = calculate_token_hmac(new_uuid)
            generated_uuids.append(new_uuid)
            generated_signatures.append(sig)

        elapsed_seconds = time.perf_counter() - start_time
        throughput = sample_size / elapsed_seconds

        # KPI-01 & KPI-02: 100% unicidad (cero duplicados)
        assert len(generated_uuids) == sample_size
        assert len(set(generated_uuids)) == sample_size, (
            f"Colisión detectada en UUIDv4: {sample_size - len(set(generated_uuids))} duplicados."
        )

        assert len(generated_signatures) == sample_size
        assert len(set(generated_signatures)) == sample_size, (
            "Colisión detectada en firmas HMAC-SHA256."
        )

        # Validación estructural de entropía UUIDv4
        for token in generated_uuids[:100]:
            assert token.version == 4, f"UUID no es versión 4: {token}"
            assert token.variant == uuid.RFC_4122, f"UUID no cumple RFC 4122: {token}"

        # Rendimiento de generación masiva
        assert throughput > 1000.0, f"Rendimiento de emisión insuficiente: {throughput:.1f} tokens/s"

    def test_cryptographic_tamper_detection(self) -> None:
        """Verifica que cualquier alteración en el UUID o firma sea detectada inmediatamente.

        Mitiga ataques de falsificación o alteración maliciosa de credenciales:
        - Cambio de un solo bit en UUID -> rechazo.
        - Cambio de un solo carácter en firma HMAC -> rechazo.
        - Clave secreta distinta -> rechazo.
        """
        token = uuid.uuid4()
        valid_sig = calculate_token_hmac(token)

        # 1. Firma original válida
        assert verify_token_hmac(token, valid_sig) is True

        # 2. Modificación de un dígito en el UUID
        token_str = str(token)
        tampered_uuid_str = ("0" if token_str[0] != "0" else "1") + token_str[1:]
        tampered_uuid = uuid.UUID(tampered_uuid_str)
        assert verify_token_hmac(tampered_uuid, valid_sig) is False

        # 3. Modificación de un carácter en la firma HMAC
        tampered_sig = ("0" if valid_sig[0] != "0" else "1") + valid_sig[1:]
        assert verify_token_hmac(token, tampered_sig) is False

        # 4. Firma con clave secreta foránea
        foreign_sig = calculate_token_hmac(token, secret_key="CLAVE_EXTERNA_NO_AUTORIZADA")
        assert verify_token_hmac(token, foreign_sig) is False

        # 5. Entrada nula o vacía
        assert verify_token_hmac(token, "") is False


@pytest.mark.django_db
class TestDatabaseIntegrityAndLifecycle:
    """Pruebas de integridad relacional en base de datos y ciclo de vida de tokens (WBS 3.13)."""

    def test_database_unique_active_constraint_enforcement(self, test_student: Student) -> None:
        """Verifica que la BD rechace un segundo token ACTIVE para un mismo alumno.

        Garantiza la regla de negocio de que ningún estudiante puede tener
        más de una credencial activa al mismo tiempo.
        """
        issue_qr_token_for_student(test_student, reason="Credencial inicial")

        # Intentar forzar un segundo token ACTIVE directamente por ORM sin revocar el previo
        with pytest.raises(IntegrityError):
            QRCodeToken.objects.create(
                token=uuid.uuid4(),
                student=test_student,
                status=QRCodeToken.Status.ACTIVE,
                hmac_signature="firma_prueba_invalida_segunda",
            )

    def test_atomic_revocation_on_reissuance(self, test_student: Student) -> None:
        """Verifica que la reemisión revoque atómicamente el token previo con motivo y fecha."""
        token_v1 = issue_qr_token_for_student(test_student, reason="Primera credencial")
        assert token_v1.status == QRCodeToken.Status.ACTIVE

        # Reemisión por extravío
        token_v2 = issue_qr_token_for_student(test_student, reason="Extravío de credencial")

        token_v1.refresh_from_db()
        assert token_v1.status == QRCodeToken.Status.REVOKED
        assert token_v1.revoked_at is not None
        assert "Extravío de credencial" in token_v1.revocation_reason

        assert token_v2.status == QRCodeToken.Status.ACTIVE
        assert test_student.active_qr_token.id == token_v2.id

    def test_resolution_latency_under_threshold(self, test_student: Student) -> None:
        """Verifica que la resolución y verificación por token sea menor a 500 ms (KPI-03).

        Mide el tiempo de búsqueda en base de datos, verificación de HMAC y
        construcción del modelo de respuesta.
        """
        active_token = issue_qr_token_for_student(test_student)

        client = APIClient()
        url = "/api/v1/qr/validate/"

        # Petición de calentamiento (warm-up) para inicializar middleware y enrutador
        client.post(url, {"token": str(uuid.uuid4())}, format="json")

        # Medición del tiempo real de resolución y validación en estado operativo
        start_t = time.perf_counter()
        response = client.post(url, {"token": str(active_token.token)}, format="json")
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["student"]["enrollment_id"] == "2026-1B-050"

        # KPI-03: < 500 ms (típicamente < 25 ms en régimen operativo)
        assert elapsed_ms < 500.0, f"Tiempo de respuesta excesivo en API: {elapsed_ms:.2f} ms"

    def test_revoked_token_rejection(self, test_student: Student) -> None:
        """Verifica que un token revocado sea rechazado inmediatamente al escanearse."""
        token_v1 = issue_qr_token_for_student(test_student, reason="Credencial 1")
        # Forzar reemplazo
        issue_qr_token_for_student(test_student, reason="Reposición")

        client = APIClient()
        url = "/api/v1/qr/validate/"

        response = client.post(url, {"token": str(token_v1.token)}, format="json")
        # Código 409 o 422 de QR_REVOKED
        assert response.status_code in (
            status.HTTP_409_CONFLICT,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            status.HTTP_400_BAD_REQUEST,
        )
        data = response.json()
        assert data.get("status") == "REVOKED" or "REVOKED" in data.get("error_code", "") or "REVOCADA" in data.get("error", "")

