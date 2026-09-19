from django.db import models
from django.core.exceptions import ValidationError
from apps.core.models import TimeStampedUUIDModel
from .validators import validate_curp, validate_phone_number, validate_enrollment_id

class Guardian(TimeStampedUUIDModel):
    """
    Representa a la madre, padre o tutor legal responsable del estudiante
    en la Escuela Secundaria Mixta 5. Permite asociar un mismo tutor a múltiples
    alumnos (hermanos) sin duplicar datos de contacto.
    """
    class Relationship(models.TextChoices):
        MADRE = 'MADRE', 'Madre'
        PADRE = 'PADRE', 'Padre'
        TUTOR_LEGAL = 'TUTOR_LEGAL', 'Tutor Legal'
        ABUELO_A = 'ABUELO_A', 'Abuelo / Abuela'
        OTRO = 'OTRO', 'Otro Familiar / Tutor Autorizado'

    full_name = models.CharField(
        max_length=255,
        verbose_name="Nombre completo del tutor"
    )
    phone_number = models.CharField(
        max_length=10,
        validators=[validate_phone_number],
        verbose_name="Teléfono celular (10 dígitos)"
    )
    relationship = models.CharField(
        max_length=25,
        choices=Relationship.choices,
        default=Relationship.TUTOR_LEGAL,
        verbose_name="Parentesco o vínculo"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo electrónico (opcional)"
    )
    notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Observaciones o indicaciones especiales"
    )

    class Meta:
        verbose_name = "Tutor Legal"
        verbose_name_plural = "Tutores Legales"
        ordering = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.get_relationship_display()}) - Tel: {self.phone_number}"

    def clean(self):
        super().clean()
        if self.phone_number:
            self.phone_number = ''.join(c for c in self.phone_number if c.isdigit())
        if self.full_name:
            self.full_name = ' '.join(self.full_name.split())


class Student(TimeStampedUUIDModel):
    """
    Entidad principal de alumnos de la Escuela Secundaria Mixta 5.
    Desacoplada del código QR físico para garantizar la persistencia del
    expediente histórico ante pérdidas de credenciales.
    """
    class Grade(models.IntegerChoices):
        PRIMERO = 1, "1°"
        SEGUNDO = 2, "2°"
        TERCERO = 3, "3°"

    class Shift(models.TextChoices):
        MATUTINO = 'MATUTINO', 'Turno Matutino'
        VESPERTINO = 'VESPERTINO', 'Turno Vespertino'

    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activo'
        INACTIVE = 'INACTIVE', 'Inactivo / Suspensión temporal'
        GRADUATED = 'GRADUATED', 'Egresado'
        EXPELLED = 'EXPELLED', 'Baja definitiva'

    GROUP_CHOICES = [
        ('A', 'A'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('E', 'E'),
        ('F', 'F'),
    ]

    enrollment_id = models.CharField(
        max_length=20,
        unique=True,
        db_index=True,
        validators=[validate_enrollment_id],
        verbose_name="Matrícula / Código escolar"
    )
    curp = models.CharField(
        max_length=18,
        unique=True,
        db_index=True,
        validators=[validate_curp],
        verbose_name="CURP Oficial (RENAPO)"
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name="Nombre(s)"
    )
    last_name_father = models.CharField(
        max_length=100,
        verbose_name="Primer apellido (Paterno)"
    )
    last_name_mother = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Segundo apellido (Materno)"
    )
    grade = models.PositiveSmallIntegerField(
        choices=Grade.choices,
        verbose_name="Grado escolar"
    )
    group = models.CharField(
        max_length=1,
        choices=GROUP_CHOICES,
        verbose_name="Grupo"
    )
    shift = models.CharField(
        max_length=15,
        choices=Shift.choices,
        default=Shift.MATUTINO,
        verbose_name="Turno"
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="Estado escolar"
    )
    medical_notes = models.TextField(
        blank=True,
        default="",
        verbose_name="Alergias o consideraciones médicas relevantes"
    )
    guardian = models.ForeignKey(
        Guardian,
        on_delete=models.PROTECT,
        related_name="students",
        verbose_name="Tutor legal registrado"
    )

    class Meta:
        verbose_name = "Estudiante"
        verbose_name_plural = "Estudiantes"
        ordering = ['grade', 'group', 'last_name_father', 'last_name_mother', 'first_name']
        indexes = [
            models.Index(fields=['grade', 'group', 'shift']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.enrollment_id} - {self.full_name} ({self.academic_group})"

    @property
    def full_name(self) -> str:
        """Devuelve el nombre completo en formato formal: Apellido Paterno Materno Nombre."""
        parts = [self.last_name_father, self.last_name_mother, self.first_name]
        return ' '.join(p for p in parts if p).strip()

    @property
    def academic_group(self) -> str:
        """Devuelve la clave de grado y grupo con turno, ej: 1°A (Matutino)."""
        return f"{self.grade}°{self.group} ({self.get_shift_display()})"

    @property
    def active_qr_token(self):
        """Retorna la instancia activa de QRCodeToken asociada al estudiante, o None."""
        return self.qr_tokens.filter(status='ACTIVE').first()

    def clean(self):
        super().clean()
        if self.curp:
            self.curp = self.curp.strip().upper()
        if self.enrollment_id:
            self.enrollment_id = self.enrollment_id.strip().upper()
        if self.group:
            self.group = self.group.strip().upper()
        if self.first_name:
            self.first_name = ' '.join(self.first_name.split()).title()
        if self.last_name_father:
            self.last_name_father = ' '.join(self.last_name_father.split()).title()
        if self.last_name_mother:
            self.last_name_mother = ' '.join(self.last_name_mother.split()).title()
