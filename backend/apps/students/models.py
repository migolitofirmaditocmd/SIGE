"""Modelos del módulo de estudiantes y tutores.

Implementa las entidades STUDENT, GUARDIAN, STUDENT_GUARDIAN y
GUARDIAN_CONSENT_LOG según el Modelo de Datos SIGE v3.2 §3.3 y §3.5.

Reglas principales:
    - RN-EST-01: estados ACTIVO / BAJA / EGRESADO.
    - RN-EST-02: enrollment_id único e inmutable.
    - RN-EST-03: al menos un tutor con is_valid_contact=True.
    - RN-EST-04: EGRESADO es estado final.
    - RN-EST-07: historial de consentimiento en GUARDIAN_CONSENT_LOG.
    - RN-EST-10: completeness=INCOMPLETO si falta birth_date o photo_url.
    - RN-EST-12: campos de salud y deuda restringidos por rol.
    - RN-EST-13: reutilización de GUARDIAN existente por coincidencia fuerte.
    - RN-EST-14: edición de GUARDIAN compartido requiere confirmación.
    - RN-TRX-08/09/10: nombre estructurado en tres campos, sin full_name.
"""

from django.core.validators import MinLengthValidator
from django.db import models

from apps.core.models import PersonNameMixin, TimeStampedUUIDModel
from .validators import (
    validate_curp,
    validate_enrollment_id,
    validate_person_name,
    validate_phone_number,
    validate_postal_code,
)


# ------------------------------------------------------------------
# GUARDIAN (§3.5)
# ------------------------------------------------------------------

class Guardian(PersonNameMixin, TimeStampedUUIDModel):
    """Tutor legal independiente asociable a múltiples estudiantes.

    Permite que un mismo tutor (padre/madre) quede asociado a hermanos
    sin duplicar sus datos de contacto (RN-EST-13).
    El nombre usa los tres campos del mixin (RN-TRX-08).
    Al menos uno de email o phone_number debe existir por relación
    STUDENT_GUARDIAN para que is_valid_contact sea True (RN-EST-11).

    Attributes:
        first_name (CharField): Nombre(s) del tutor.
        last_name_father (CharField): Apellido paterno.
        last_name_mother (CharField): Apellido materno (opcional).
        email (EmailField): Correo electrónico (opcional a nivel modelo).
        phone_number (CharField): Teléfono 10 dígitos (opcional).
        created_at (DateTimeField): Marca de tiempo de alta.
        updated_at (DateTimeField): Marca de tiempo de última modificación.
    """

    email = models.EmailField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Correo electrónico",
    )
    phone_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        default=None,
        validators=[validate_phone_number],
        verbose_name="Teléfono celular (10 dígitos)",
    )

    class Meta:
        verbose_name = "Tutor Legal"
        verbose_name_plural = "Tutores Legales"
        ordering = ["last_name_father", "last_name_mother", "first_name"]

    def __str__(self) -> str:
        contact = self.email or self.phone_number or "sin contacto"
        return f"{self.display_name} ({contact})"

    def clean(self) -> None:
        """Normaliza nombre y convierte apellido materno vacío a NULL."""
        super().clean()
        self._normalize_name_fields()
        for fn in ("first_name", "last_name_father"):
            validate_person_name(getattr(self, fn, ""), fn)
        if self.last_name_mother:
            validate_person_name(self.last_name_mother, "last_name_mother")


# ------------------------------------------------------------------
# STUDENT (§3.3)
# ------------------------------------------------------------------

class Student(PersonNameMixin, TimeStampedUUIDModel):
    """Entidad principal de alumnos de la Escuela Secundaria Mixta 5.

    El expediente del alumno desacopla la identidad institucional
    del código QR físico, para garantizar la persistencia histórica
    ante pérdidas o revocaciones de credenciales (RN-QR-01).

    Attributes:
        enrollment_id (CharField): Matrícula única e inmutable (RN-EST-02).
        group (ForeignKey): Grupo al que pertenece (grado, turno, ciclo).
        first_name (CharField): Nombre(s) (via PersonNameMixin).
        last_name_father (CharField): Apellido paterno (via PersonNameMixin).
        last_name_mother (CharField): Apellido materno (via PersonNameMixin).
        status (CharField): Estado escolar (RN-EST-01).
        completeness (CharField): Indicador de expediente completo (RN-EST-10).
        birth_date (DateField): Fecha de nacimiento (opcional).
        curp (CharField): CURP RENAPO (opcional, RF-EST-01 v2.1).
        sex (CharField): Sexo del alumno (opcional).
        address_street (CharField): Calle y número (opcional).
        address_colonia (CharField): Colonia (opcional).
        address_municipio (CharField): Municipio (opcional).
        address_estado (CharField): Estado (opcional).
        address_postal_code (CharField): Código postal 5 dígitos (opcional).
        photo_url (CharField): Ruta interna de la fotografía (opcional).
        blood_type (CharField): Tipo de sangre; acceso restringido (RN-EST-12).
        allergies (TextField): Alergias; acceso restringido (RN-EST-12).
        has_payment_debt (BooleanField): Indicador adeudo pago (RN-EST-12).
        guardians (ManyToManyField): Tutores asociados via StudentGuardian.
    """

    class Status(models.TextChoices):
        ACTIVO = "ACTIVO", "Activo"
        BAJA = "BAJA", "Baja"
        EGRESADO = "EGRESADO", "Egresado"

    class Completeness(models.TextChoices):
        COMPLETO = "COMPLETO", "Completo"
        INCOMPLETO = "INCOMPLETO", "Incompleto"

    class SexChoices(models.TextChoices):
        MASCULINO = "M", "Masculino"
        FEMENINO = "F", "Femenino"

    # Identificación
    enrollment_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        validators=[validate_enrollment_id],
        verbose_name="Matrícula / Código escolar",
    )
    curp = models.CharField(
        max_length=18,
        unique=True,
        blank=True,
        null=True,
        default=None,
        validators=[validate_curp],
        verbose_name="CURP Oficial (RENAPO)",
    )

    # Grupo académico (FK → GROUP en app catalogs; usamos CharField simple
    # mientras el modelo Group no esté migrado para evitar dep. circular)
    # TODO: convertir a FK a catalogs.Group cuando exista esa app.
    group = models.ForeignKey(
        "students.GroupProxy",
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="Grupo escolar",
        null=True,
        blank=True,
    )
    # Campos temporales hasta que exista la app catalogs.Group:
    grade = models.PositiveSmallIntegerField(
        choices=[(1, "1°"), (2, "2°"), (3, "3°")],
        verbose_name="Grado escolar",
        null=True,
        blank=True,
    )
    group_letter = models.CharField(
        max_length=1,
        choices=[("A", "A"), ("B", "B"), ("C", "C"),
                 ("D", "D"), ("E", "E"), ("F", "F")],
        blank=True,
        default="",
        verbose_name="Grupo (letra)",
    )
    shift = models.CharField(
        max_length=15,
        choices=[("MATUTINO", "Matutino"), ("VESPERTINO", "Vespertino")],
        default="MATUTINO",
        verbose_name="Turno",
    )

    # Estado y expediente
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVO,
        db_index=True,
        verbose_name="Estado escolar",
    )
    completeness = models.CharField(
        max_length=10,
        choices=Completeness.choices,
        default=Completeness.INCOMPLETO,
        editable=False,
        verbose_name="Completitud del expediente",
        help_text="Calculado automáticamente. INCOMPLETO si falta birth_date o photo_url.",
    )

    # Datos personales opcionales
    birth_date = models.DateField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Fecha de nacimiento",
    )
    sex = models.CharField(
        max_length=1,
        choices=SexChoices.choices,
        blank=True,
        null=True,
        default=None,
        verbose_name="Sexo",
    )
    photo_url = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        default=None,
        verbose_name="Ruta interna de fotografía",
        help_text="Ruta privada; nunca una URL pública (RN-TRX-02).",
    )

    # Domicilio desglosado (opcional, RF-EST-01)
    address_street = models.CharField(
        max_length=200, blank=True, null=True, default=None,
        verbose_name="Calle y número",
    )
    address_colonia = models.CharField(
        max_length=100, blank=True, null=True, default=None,
        verbose_name="Colonia",
    )
    address_municipio = models.CharField(
        max_length=100, blank=True, null=True, default=None,
        verbose_name="Municipio",
    )
    address_estado = models.CharField(
        max_length=60, blank=True, null=True, default=None,
        verbose_name="Estado",
    )
    address_postal_code = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        default=None,
        validators=[validate_postal_code],
        verbose_name="Código postal",
    )

    # Campos de acceso restringido por rol (RN-EST-12)
    blood_type = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        default=None,
        verbose_name="Tipo de sangre",
        help_text="Restringido a ADM, PRE, PAD (RN-EST-12).",
    )
    allergies = models.TextField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Alergias o consideraciones médicas",
        help_text="Restringido a ADM, PRE, PAD (RN-EST-12).",
    )
    has_payment_debt = models.BooleanField(
        blank=True,
        null=True,
        default=None,
        verbose_name="¿Tiene adeudo de pago?",
        help_text="Solo visible a ADM y PAD (RN-EST-12). Sin monto.",
    )

    # Tutores (via tabla intermedia StudentGuardian)
    guardians = models.ManyToManyField(
        Guardian,
        through="StudentGuardian",
        related_name="students",
        verbose_name="Tutores legales",
    )

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = [
            "grade", "group_letter", "shift",
            "last_name_father", "last_name_mother", "first_name",
        ]
        indexes = [
            models.Index(fields=["grade", "group_letter", "shift"]),
            models.Index(fields=["status"]),
            models.Index(fields=["enrollment_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.enrollment_id} - {self.display_name}"

    @property
    def academic_group(self) -> str:
        """Clave legible de grado, grupo y turno. Ej: 1°A (Matutino)."""
        shift_label = dict(
            MATUTINO="Matutino", VESPERTINO="Vespertino"
        ).get(self.shift, self.shift)
        return f"{self.grade}°{self.group_letter} ({shift_label})"

    @property
    def active_qr_token(self):
        """Instancia de QRToken vigente o None."""
        return self.qr_tokens.filter(status="ACTIVE").first()

    @property
    def full_name(self) -> str:
        """Nombre completo en orden Apellido paterno, materno y nombre(s)."""
        parts = [self.last_name_father, self.last_name_mother, self.first_name]
        return " ".join(p for p in parts if p)

    @property
    def medical_notes(self) -> str:
        """Alias de compatibilidad para alergias y notas médicas."""
        return self.allergies or ""

    def _recalculate_completeness(self) -> None:
        """Recalcula el campo completeness (RN-EST-10).

        INCOMPLETO si falta birth_date O photo_url.
        """
        if self.birth_date and self.photo_url:
            self.completeness = self.Completeness.COMPLETO
        else:
            self.completeness = self.Completeness.INCOMPLETO

    def clean(self) -> None:
        """Normaliza y valida campos antes de guardar."""
        super().clean()
        self._normalize_name_fields()
        if self.enrollment_id:
            self.enrollment_id = self.enrollment_id.strip().upper()
        if self.curp:
            self.curp = self.curp.strip().upper()
        if self.group_letter:
            self.group_letter = self.group_letter.strip().upper()

    def save(self, *args, **kwargs) -> None:
        """Recalcula completeness antes de cada guardado."""
        self._recalculate_completeness()
        super().save(*args, **kwargs)


# ------------------------------------------------------------------
# GroupProxy — placeholder hasta que exista app catalogs
# ------------------------------------------------------------------

class GroupProxy(TimeStampedUUIDModel):
    """Representación mínima de un grupo académico.

    Sustituye temporalmente al modelo Group de la futura app
    ``catalogs`` (§3.2 del Modelo de Datos v3.2). Cuando esa app
    esté disponible, esta tabla se migrará y la FK de Student se
    actualizará.

    Attributes:
        grade (PositiveSmallIntegerField): Grado (1, 2 o 3).
        group_letter (CharField): Letra de grupo (A–F).
        shift (CharField): Turno MATUTINO/VESPERTINO.
        cutoff_time (TimeField): Hora de corte para asistencia (RN-AST-01).
        is_active (BooleanField): Indica si el grupo está activo.
    """

    SHIFT_CHOICES = [("MATUTINO", "Matutino"), ("VESPERTINO", "Vespertino")]

    grade = models.PositiveSmallIntegerField(
        choices=[(1, "1°"), (2, "2°"), (3, "3°")],
        verbose_name="Grado",
    )
    group_letter = models.CharField(
        max_length=1,
        choices=[("A", "A"), ("B", "B"), ("C", "C"),
                 ("D", "D"), ("E", "E"), ("F", "F")],
        verbose_name="Grupo (letra)",
    )
    shift = models.CharField(
        max_length=15,
        choices=SHIFT_CHOICES,
        default="MATUTINO",
        verbose_name="Turno",
    )
    cutoff_time = models.TimeField(
        verbose_name="Hora de corte de asistencia",
        help_text="RN-AST-01: hora límite para marcar ASISTIÓ.",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Grupo"
        verbose_name_plural = "Grupos"
        unique_together = [("grade", "group_letter", "shift")]
        ordering = ["grade", "group_letter", "shift"]

    def __str__(self) -> str:
        shift_label = dict(MATUTINO="Mat", VESPERTINO="Ves").get(
            self.shift, self.shift
        )
        return f"{self.grade}°{self.group_letter} {shift_label}"


# ------------------------------------------------------------------
# STUDENT_GUARDIAN (§3.5) — tabla intermedia
# ------------------------------------------------------------------

class StudentGuardian(TimeStampedUUIDModel):
    """Relación intermedia entre Student y Guardian (§3.5).

    Almacena el parentesco, si es contacto principal, si el contacto
    es válido y el estado de consentimiento informado (RN-EST-07).

    Attributes:
        student (ForeignKey): Estudiante.
        guardian (ForeignKey): Tutor legal.
        relationship (CharField): Parentesco (RN-EST-03).
        is_primary_contact (BooleanField): Contacto principal del alumno.
        is_valid_contact (BooleanField): Contacto válido (RN-EST-11).
        invalid_reason (TextField): Motivo de invalidación.
        consent_status (CharField): Estado de consentimiento (RN-EST-07).
        consent_registered_at (DateField): Fecha de registro de consentimiento.
        linked_at (DateTimeField): Fecha/hora de alta del vínculo (C-3).
    """

    class Relationship(models.TextChoices):
        MADRE = "MADRE", "Madre"
        PADRE = "PADRE", "Padre"
        TUTOR_LEGAL = "TUTOR_LEGAL", "Tutor Legal"
        OTRO = "OTRO", "Otro Familiar / Tutor Autorizado"

    class ConsentStatus(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        OTORGADO = "OTORGADO", "Otorgado"
        REVOCADO = "REVOCADO", "Revocado"

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="student_guardians",
        verbose_name="Estudiante",
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.PROTECT,
        related_name="student_guardians",
        verbose_name="Tutor legal",
    )
    relationship = models.CharField(
        max_length=20,
        choices=Relationship.choices,
        default=Relationship.TUTOR_LEGAL,
        verbose_name="Parentesco",
    )
    is_primary_contact = models.BooleanField(
        default=False,
        verbose_name="¿Es contacto principal?",
    )
    is_valid_contact = models.BooleanField(
        default=True,
        verbose_name="¿Contacto válido?",
        help_text="False si el email/teléfono fue invalidado manualmente (RN-EST-11).",
    )
    invalid_reason = models.TextField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Motivo de invalidación",
    )
    consent_status = models.CharField(
        max_length=15,
        choices=ConsentStatus.choices,
        default=ConsentStatus.PENDIENTE,
        verbose_name="Estado de consentimiento",
        help_text="RN-EST-07. Default PENDIENTE al crear.",
    )
    consent_registered_at = models.DateField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Fecha de registro de consentimiento",
    )
    linked_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha/hora de alta del vínculo",
        help_text="Hallazgo C-3 (v3.2): base del primer renglón de GuardianConsentLog.",
    )

    class Meta:
        verbose_name = "Vínculo Estudiante–Tutor"
        verbose_name_plural = "Vínculos Estudiante–Tutor"
        unique_together = [("student", "guardian")]
        ordering = ["-is_primary_contact", "relationship"]

    def __str__(self) -> str:
        return (
            f"{self.guardian.display_name} → "
            f"{self.student.display_name} ({self.get_relationship_display()})"
        )


# ------------------------------------------------------------------
# GUARDIAN_CONSENT_LOG (§3.5) — historial de consentimiento
# ------------------------------------------------------------------

class GuardianConsentLog(TimeStampedUUIDModel):
    """Historial completo de cambios de consentimiento (RN-EST-07).

    Hallazgo B-3 (v3.2): el modelo anterior solo guardaba el estado
    vigente; este modelo conserva el historial completo para poder
    reconstruir la secuencia de cambios.

    Attributes:
        student_guardian (ForeignKey): Vínculo al que pertenece.
        previous_status (CharField): Estado anterior (NULL en primer renglón).
        new_status (CharField): Nuevo estado.
        registered_by (ForeignKey): Usuario que registró el cambio (NULL si automático).
        registered_at (DateTimeField): Marca de tiempo del cambio.
    """

    class ConsentStatus(models.TextChoices):
        PENDIENTE = "PENDIENTE", "Pendiente"
        OTORGADO = "OTORGADO", "Otorgado"
        REVOCADO = "REVOCADO", "Revocado"

    student_guardian = models.ForeignKey(
        StudentGuardian,
        on_delete=models.CASCADE,
        related_name="consent_logs",
        verbose_name="Vínculo Estudiante–Tutor",
    )
    previous_status = models.CharField(
        max_length=15,
        choices=ConsentStatus.choices,
        blank=True,
        null=True,
        default=None,
        verbose_name="Estado anterior",
        help_text="NULL en el primer renglón (alta inicial en PENDIENTE).",
    )
    new_status = models.CharField(
        max_length=15,
        choices=ConsentStatus.choices,
        verbose_name="Nuevo estado",
    )
    registered_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="guardian_consent_logs",
        verbose_name="Registrado por",
        help_text="NULL cuando el renglón inicial es automático (alta).",
    )
    registered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha/hora de registro",
    )

    class Meta:
        verbose_name = "Historial de Consentimiento"
        verbose_name_plural = "Historial de Consentimientos"
        ordering = ["-registered_at"]

    def __str__(self) -> str:
        prev = self.previous_status or "—"
        return (
            f"{self.student_guardian} | "
            f"{prev} → {self.new_status} ({self.registered_at:%Y-%m-%d})"
        )
