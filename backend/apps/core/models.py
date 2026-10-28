"""Modelos base, auditoría y operaciones del proyecto SIGE.

Contiene el modelo abstracto con UUID y timestamps, el mixin de nombre estructurado
(§3.0 del Modelo de Datos v3.2), la bitácora de auditoría inmutable (AUDIT_LOG, §3.13),
el registro de ejecuciones programadas (JOB_RUN, §3.16) y los tokens de restablecimiento
de credenciales (PASSWORD_RESET_TOKEN, §3.1).
"""

import uuid
from typing import Any

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone


class TimeStampedUUIDModel(models.Model):
    """Modelo abstracto base con identificador único universal (UUIDv4)
    y marcas de tiempo automáticas para auditoría de cambios.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único universal (UUIDv4)",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización",
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class PersonNameMixin(models.Model):
    """Mixin abstracto para nombre estructurado en tres campos (§3.0).

    Aplica a USER, STUDENT, TEACHER y GUARDIAN.
    Reglas: RN-TRX-08, RN-TRX-09, RN-TRX-10.

    * ``first_name``: obligatorio, 2–60 caracteres.
    * ``last_name_father``: obligatorio, 2–60 caracteres.
    * ``last_name_mother``: opcional (NULL), 2–60 caracteres si se provee.
    * No se almacena ``full_name``; la API expone ``display_name``
      y ``sort_name`` calculados.
    """

    first_name = models.CharField(
        max_length=60,
        validators=[MinLengthValidator(2)],
        verbose_name="Nombre(s)",
    )
    last_name_father = models.CharField(
        max_length=60,
        validators=[MinLengthValidator(2)],
        verbose_name="Apellido paterno",
    )
    last_name_mother = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        default=None,
        verbose_name="Apellido materno",
        help_text="Opcional. Vacío se guarda como NULL (nunca cadena vacía).",
    )

    class Meta:
        abstract = True

    # ------------------------------------------------------------------
    # Propiedades calculadas (RN-TRX-10)
    # ------------------------------------------------------------------

    @property
    def display_name(self) -> str:
        """Nombre(s) Apellido_paterno Apellido_materno (para la interfaz)."""
        parts = [self.first_name, self.last_name_father, self.last_name_mother]
        return " ".join(p for p in parts if p)

    @property
    def sort_name(self) -> str:
        """Apellido_paterno Apellido_materno, Nombre(s) (para ordenamiento)."""
        surnames = " ".join(
            p for p in [self.last_name_father, self.last_name_mother] if p
        )
        return f"{surnames}, {self.first_name}"

    # ------------------------------------------------------------------
    # Normalización (RN-TRX-09)
    # ------------------------------------------------------------------

    def _normalize_name_fields(self) -> None:
        """Normaliza espacios internos en los tres campos de nombre."""
        for field in ("first_name", "last_name_father", "last_name_mother"):
            value = getattr(self, field, None)
            if value:
                setattr(self, field, " ".join(value.split()))
            elif field == "last_name_mother" and value == "":
                # Vacío se guarda como NULL, nunca cadena vacía.
                self.last_name_mother = None


# ----------------------------------------------------------------------
# AUDIT_LOG (§3.13)
# ----------------------------------------------------------------------

class AuditLog(TimeStampedUUIDModel):
    """Bitácora de auditoría inmutable del sistema escolar (§3.13).

    Registra inicios de sesión, cambios de rol, inserción masiva de ausencias,
    modificaciones de asistencia, reportes disciplinarios y operaciones de consola.
    Tabla de solo inserción (INSERT-only).

    Attributes:
        action (CharField): Acción auditada (ej. 'auth:admin_bootstrap', 'ops:restore').
        user (ForeignKey): Usuario actor. Nulo si es proceso automático o acción de consola.
        origin (CharField): Origen del evento ('ESCANEO', 'AUTOMATICO', 'MANUAL').
        reason (TextField): Motivo explícito exigido en acciones sensibles.
        new_value (JSONField): Estado resultante o parámetros de la operación.
        old_value (JSONField): Estado previo si aplica.
        ip_address (GenericIPAddressField): Dirección IP del cliente en peticiones HTTP.
    """

    class Origin(models.TextChoices):
        """Orígenes válidos para eventos de auditoría (RN-TRX-07)."""
        ESCANEO = "ESCANEO", "Escaneo"
        AUTOMATICO = "AUTOMATICO", "Automático"
        MANUAL = "MANUAL", "Manual"

    action = models.CharField(
        max_length=100,
        verbose_name="Acción auditada",
        help_text="Identificador único de la acción (ej. 'auth:admin_bootstrap')",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="Usuario responsable",
    )
    origin = models.CharField(
        max_length=20,
        choices=Origin.choices,
        default=Origin.MANUAL,
        verbose_name="Origen del evento",
    )
    reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="Motivo o justificación",
    )
    new_value = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores posteriores / contexto",
    )
    old_value = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Valores anteriores",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Dirección IP",
    )

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        actor = self.user.get_username() if self.user else "SISTEMA/CONSOLA"
        return f"[{self.created_at:%Y-%m-%d %H:%M:%S}] {self.action} por {actor}"

    def clean(self) -> None:
        """Valida restricciones de negocio para registros de auditoría (§3.13).

        Raises:
            ValidationError: Si una acción manual carece de usuario y no corresponde
                a 'ops:restore' o 'auth:admin_bootstrap'.
        """
        super().clean()
        if self.origin == self.Origin.MANUAL and not self.user:
            allowed_console_actions = ("ops:restore", "auth:admin_bootstrap")
            if (
                self.action not in allowed_console_actions
                and not self.action.startswith("ops:")
                and not self.action.startswith("job:")
            ):
                raise ValidationError(
                    "Las acciones manuales de auditoría requieren un usuario responsable, "
                    f"a excepción de operaciones de consola: {allowed_console_actions}."
                )


# ----------------------------------------------------------------------
# JOB_RUN (§3.16)
# ----------------------------------------------------------------------

class JobRun(TimeStampedUUIDModel):
    """Registro de ejecución de procesos programados y background jobs (§3.16).

    Provee el marcador de idempotencia para la ejecución de tareas recurrentes
    (ej. inserción de ausencias estudiantiles y docentes) y la fuente de estado
    operativo para el panel del Administrador.

    Attributes:
        job_name (CharField): Nombre canónico del job.
        run_date (DateField): Fecha de negocio de la corrida.
        scope (CharField): Ámbito de ejecución ('MATUTINO', 'VESPERTINO', 'GLOBAL').
        status (CharField): Estado actual ('EN_CURSO', 'COMPLETADO', 'FALLIDO', 'OMITIDO').
        started_at (DateTimeField): Momento en que inició la corrida.
        finished_at (DateTimeField): Momento de término.
        evaluated_count (IntegerField): Cantidad de registros evaluados.
        created_count (IntegerField): Cantidad de registros creados o modificados.
        error (TextField): Mensaje de excepción o causa de fallo si ocurrió.
    """

    class Status(models.TextChoices):
        """Estados operativos del job programado."""
        EN_CURSO = "EN_CURSO", "En Curso"
        COMPLETADO = "COMPLETADO", "Completado"
        FALLIDO = "FALLIDO", "Fallido"
        OMITIDO = "OMITIDO", "Omitido"

    job_name = models.CharField(
        max_length=100,
        verbose_name="Nombre del proceso",
        help_text="Ej. 'check_student_absences', 'check_teacher_absences'",
    )
    run_date = models.DateField(
        verbose_name="Fecha de ejecución",
    )
    scope = models.CharField(
        max_length=50,
        default="GLOBAL",
        verbose_name="Alcance / Turno",
        help_text="Turno ('MATUTINO'/'VESPERTINO') o 'GLOBAL'",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.EN_CURSO,
        verbose_name="Estado de ejecución",
    )
    started_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Inicio de corrida",
    )
    finished_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fin de corrida",
    )
    evaluated_count = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Total evaluados",
    )
    created_count = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        verbose_name="Total creados",
    )
    error = models.TextField(
        null=True,
        blank=True,
        verbose_name="Detalle del error",
    )

    class Meta:
        verbose_name = "Ejecución de Job"
        verbose_name_plural = "Ejecuciones de Jobs"
        ordering = ["-started_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["job_name", "run_date", "scope"],
                name="unique_job_run_per_date_scope",
            )
        ]

    def __str__(self) -> str:
        return f"{self.job_name} ({self.run_date} {self.scope}): {self.status}"


# ----------------------------------------------------------------------
# PASSWORD_RESET_TOKEN (§3.1)
# ----------------------------------------------------------------------

class PasswordResetToken(TimeStampedUUIDModel):
    """Token criptográfico de un solo uso para definición o restablecimiento de contraseña (§3.1).

    Almacena únicamente el hash SHA-256 del token para prevenir divulgación
    y garantiza expiración configurable (PASSWORD_RESET_EXPIRY_MINUTES) e invalidación
    al consumirse o al emitirse un nuevo enlace (RN-AUT-07, CA-001-11).

    Attributes:
        user (ForeignKey): Usuario titular de la cuenta.
        token_hash (CharField): Hash SHA-256 del token generado (64 hexchars).
        expires_at (DateTimeField): Momento exacto de vencimiento.
        used_at (DateTimeField): Momento en que fue consumido exitosamente.
        invalidated_at (DateTimeField): Momento en que fue revocado o reemplazado.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens",
        verbose_name="Usuario",
    )
    token_hash = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="Hash SHA-256 del token",
    )
    expires_at = models.DateTimeField(
        verbose_name="Fecha de expiración",
    )
    used_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de uso",
    )
    invalidated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de invalidación",
    )

    class Meta:
        verbose_name = "Token de Restablecimiento de Contraseña"
        verbose_name_plural = "Tokens de Restablecimiento de Contraseña"
        ordering = ["-created_at"]

    @property
    def is_valid(self) -> bool:
        """Determina si el token está activo, sin consumir y sin vencer."""
        return (
            self.used_at is None
            and self.invalidated_at is None
            and self.expires_at > timezone.now()
        )

    def __str__(self) -> str:
        status = "VÁLIDO" if self.is_valid else "INACTIVO/EXPIRADO"
        return f"ResetToken({self.user.get_username()}) - {status}"
