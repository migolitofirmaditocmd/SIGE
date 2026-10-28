"""Pruebas unitarias y de integración para el módulo core y operaciones de SIGE.

Cubre:
- RNF-MAN-03: Servicio de reloj inyectable (ClockService).
- P-D5, CA-001-11: Comando de consola create_admin para inicialización de Administrador.
- PP §1, RNF-MAN-03: Comando de consola run_job y servicio execute_job.
- §3.6 API REST v2, CA-030-08, CA-042-09: Endpoint POST /api/v1/ops/jobs/{job_name}/run/.
"""

import hashlib
from datetime import date, datetime, timedelta
from io import StringIO

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.clock import ClockService
from apps.core.jobs import execute_job
from apps.core.models import AuditLog, JobRun, PasswordResetToken

User = get_user_model()


# ======================================================================
# Pruebas de ClockService (RNF-MAN-03)
# ======================================================================

class TestClockService:
    """Verifica el comportamiento del servicio de reloj inyectable."""

    def test_clock_returns_current_time_by_default(self) -> None:
        """Verifica que sin congelar el reloj retorne la fecha de hoy."""
        ClockService.unfreeze()
        assert not ClockService.is_frozen()
        assert isinstance(ClockService.now(), datetime)
        assert isinstance(ClockService.today(), date)

    def test_clock_freeze_with_datetime(self) -> None:
        """Verifica la fijación del reloj con un objeto datetime."""
        target_dt = datetime(2026, 11, 15, 10, 30, 0)
        frozen = ClockService.freeze(target_dt)
        try:
            assert ClockService.is_frozen()
            assert ClockService.now().year == 2026
            assert ClockService.now().month == 11
            assert ClockService.now().day == 15
            assert ClockService.today() == date(2026, 11, 15)
        finally:
            ClockService.unfreeze()
        assert not ClockService.is_frozen()

    def test_clock_freeze_with_iso_string(self) -> None:
        """Verifica la fijación del reloj con una cadena ISO."""
        ClockService.freeze("2026-10-31T08:00:00")
        try:
            assert ClockService.today() == date(2026, 10, 31)
        finally:
            ClockService.unfreeze()

    def test_clock_freeze_context_manager(self) -> None:
        """Verifica el context manager ClockService.freeze_time."""
        original_frozen = ClockService.is_frozen()
        with ClockService.freeze_time("2026-12-25T12:00:00"):
            assert ClockService.is_frozen()
            assert ClockService.today() == date(2026, 12, 25)
        assert ClockService.is_frozen() == original_frozen


# ======================================================================
# Pruebas de create_admin (P-D5, CA-001-11)
# ======================================================================

@pytest.mark.django_db
class TestCreateAdminCommand:
    """Verifica el comando de bootstrap del primer usuario Administrador."""

    def test_create_admin_success(self) -> None:
        """Crea el usuario administrador sin contraseña y emite enlace único."""
        out = StringIO()
        call_command(
            "create_admin",
            username="admin_sec5",
            email="admin@sec5.edu.mx",
            first_name="Carlos",
            last_name_father="Ramírez",
            stdout=out,
        )

        user = User.objects.get(username="admin_sec5")
        assert user.is_staff
        assert user.is_superuser
        assert not user.has_usable_password()

        # Token generado
        reset_token = PasswordResetToken.objects.filter(user=user).first()
        assert reset_token is not None
        assert reset_token.is_valid
        assert len(reset_token.token_hash) == 64

        # Auditoría registrada
        audit = AuditLog.objects.filter(action="auth:admin_bootstrap").first()
        assert audit is not None
        assert audit.origin == AuditLog.Origin.MANUAL
        assert audit.user is None  # Permitido para bootstrapping de consola (§3.13)
        assert "admin_sec5" in audit.new_value["username"]

    def test_create_admin_existing_user_regenerates_token(self) -> None:
        """Si el usuario ya existe, genera un nuevo token e invalida el previo (RN-AUT-07)."""
        call_command("create_admin", username="admin_sec5", email="admin@sec5.edu.mx")
        first_token = PasswordResetToken.objects.get(user__username="admin_sec5")

        # Segunda ejecución
        call_command("create_admin", username="admin_sec5", email="admin@sec5.edu.mx")
        first_token.refresh_from_db()
        assert first_token.invalidated_at is not None  # Invalida el token previo

        latest_token = PasswordResetToken.objects.filter(
            user__username="admin_sec5", invalidated_at__isnull=True
        ).first()
        assert latest_token is not None
        assert latest_token.id != first_token.id

    def test_create_admin_invalid_email_raises_error(self) -> None:
        """Falla si el correo no tiene formato válido."""
        with pytest.raises(CommandError):
            call_command("create_admin", username="bad_admin", email="correo-invalido")


# ======================================================================
# Pruebas de run_job y execute_job (PP §1, RNF-MAN-03)
# ======================================================================

@pytest.mark.django_db
class TestJobExecution:
    """Verifica la ejecución manual y orquestación de jobs programados."""

    def test_execute_job_check_student_absences(self) -> None:
        """Ejecuta check_student_absences con confirmación de día lectivo."""
        job_run = execute_job(
            job_name="check_student_absences",
            run_date=date(2026, 10, 27),
            shift="MATUTINO",
            confirm_school_day=True,
        )
        assert job_run.status == JobRun.Status.COMPLETADO
        assert job_run.job_name == "check_student_absences"
        assert job_run.scope == "MATUTINO"

        # Verificar auditoría
        audit = AuditLog.objects.filter(action__startswith="job:").first()
        assert audit is not None
        assert audit.new_value["job_name"] == "check_student_absences"

    def test_execute_job_idempotency(self) -> None:
        """Verifica que reejecutar el mismo job retorne el JobRun existente."""
        run1 = execute_job("check_student_absences", run_date=date(2026, 10, 27), shift="VESPERTINO")
        run2 = execute_job("check_student_absences", run_date=date(2026, 10, 27), shift="VESPERTINO")
        assert run1.id == run2.id

    def test_run_job_command_success(self) -> None:
        """Ejecuta el comando manage.py run_job en consola."""
        out = StringIO()
        call_command(
            "run_job",
            "check_student_absences",
            "--date=2026-10-28",
            "--shift=MATUTINO",
            "--confirm-school-day",
            stdout=out,
        )
        output = out.getvalue()
        assert "COMPLETADO" in output
        assert JobRun.objects.filter(run_date=date(2026, 10, 28), scope="MATUTINO").exists()


# ======================================================================
# Pruebas del Endpoint REST POST /api/v1/ops/jobs/{job_name}/run/ (§3.6)
# ======================================================================

@pytest.mark.django_db
class TestRunJobAPIView:
    """Verifica el endpoint REST de ejecución manual de jobs (CA-030-08, CA-042-09)."""

    @pytest.fixture(autouse=True)
    def setup_clients(self) -> None:
        """Configura los clientes de prueba con usuarios y credenciales."""
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username="admin_api",
            email="admin_api@sec5.edu.mx",
            password="AdminPassword123!",
        )
        self.regular_user = User.objects.create_user(
            username="docente_api",
            email="docente@sec5.edu.mx",
            password="DocentePassword123!",
        )

    def test_run_job_endpoint_requires_admin(self) -> None:
        """Rechaza con 401/403 si es anónimo o con 403 si es un rol sin privilegios ADM."""
        url = reverse("ops:run-job", kwargs={"job_name": "check_student_absences"})

        # Anónimo
        response = self.client.post(url, {"confirm_school_day": True}, format="json")
        assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)

        # Usuario no administrador
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.post(url, {"confirm_school_day": True}, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_run_job_without_confirm_school_day_returns_422(self) -> None:
        """Retorna 422 VALIDATION_ERROR si confirm_school_day no es True (D-03, §3.6)."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("ops:run-job", kwargs={"job_name": "check_student_absences"})

        response = self.client.post(
            url,
            {"date": "2026-10-27", "shift": "MATUTINO", "confirm_school_day": False},
            format="json",
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["error_code"] == "VALIDATION_ERROR"
        assert "confirm_school_day" in data["details"]

    def test_run_job_successful_execution(self) -> None:
        """Ejecuta exitosamente el job vía REST retornando 200 y registrando auditoría."""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse("ops:run-job", kwargs={"job_name": "check_student_absences"})

        payload = {
            "date": "2026-10-29",
            "shift": "MATUTINO",
            "confirm_school_day": True,
        }
        response = self.client.post(url, payload, format="json")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["job_name"] == "check_student_absences"
        assert data["run_date"] == "2026-10-29"
        assert data["status"] == "COMPLETADO"

        # Verificar registro en AUDIT_LOG con origin='MANUAL' y el usuario solicitante
        audit = AuditLog.objects.filter(
            action="job:check_student_absences",
            user=self.admin_user,
        ).first()
        assert audit is not None
        assert audit.origin == AuditLog.Origin.MANUAL
        assert audit.new_value["confirm_school_day"] is True
