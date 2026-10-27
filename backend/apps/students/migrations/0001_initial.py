"""Migración inicial completa del módulo students (SIGE v3.2).

Sustituye a la migración original para alinear el esquema con el
Modelo de Datos v3.2 §3.3 y §3.5. Incluye:
    - Guardian con nombre estructurado en 3 campos (PersonNameMixin).
    - GroupProxy (placeholder para futura app catalogs).
    - Student con todos los campos del modelo v3.2.
    - StudentGuardian (tabla intermedia con consentimiento).
    - GuardianConsentLog (historial de consentimiento RN-EST-07).
"""

import apps.students.validators
import django.core.validators
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """Migración inicial del módulo students."""

    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ------------------------------------------------------------------
        # GroupProxy
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="GroupProxy",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Identificador único universal (UUIDv4)",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Última actualización"
                    ),
                ),
                (
                    "grade",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "1°"), (2, "2°"), (3, "3°")],
                        verbose_name="Grado",
                    ),
                ),
                (
                    "group_letter",
                    models.CharField(
                        choices=[
                            ("A", "A"), ("B", "B"), ("C", "C"),
                            ("D", "D"), ("E", "E"), ("F", "F"),
                        ],
                        max_length=1,
                        verbose_name="Grupo (letra)",
                    ),
                ),
                (
                    "shift",
                    models.CharField(
                        choices=[
                            ("MATUTINO", "Matutino"), ("VESPERTINO", "Vespertino")
                        ],
                        default="MATUTINO",
                        max_length=15,
                        verbose_name="Turno",
                    ),
                ),
                (
                    "cutoff_time",
                    models.TimeField(
                        blank=True,
                        null=True,
                        verbose_name="Hora de corte de asistencia",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(default=True, verbose_name="Activo"),
                ),
            ],
            options={
                "verbose_name": "Grupo",
                "verbose_name_plural": "Grupos",
                "ordering": ["grade", "group_letter", "shift"],
                "unique_together": {("grade", "group_letter", "shift")},
            },
        ),
        # ------------------------------------------------------------------
        # Guardian
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="Guardian",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Identificador único universal (UUIDv4)",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Última actualización"
                    ),
                ),
                # PersonNameMixin fields (§3.0)
                (
                    "first_name",
                    models.CharField(
                        max_length=60,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name="Nombre(s)",
                    ),
                ),
                (
                    "last_name_father",
                    models.CharField(
                        max_length=60,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name="Apellido paterno",
                    ),
                ),
                (
                    "last_name_mother",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=60,
                        null=True,
                        verbose_name="Apellido materno",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        default=None,
                        max_length=254,
                        null=True,
                        verbose_name="Correo electrónico",
                    ),
                ),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=10,
                        null=True,
                        validators=[apps.students.validators.validate_phone_number],
                        verbose_name="Teléfono celular (10 dígitos)",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tutor Legal",
                "verbose_name_plural": "Tutores Legales",
                "ordering": ["last_name_father", "last_name_mother", "first_name"],
            },
        ),
        # ------------------------------------------------------------------
        # Student
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="Student",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Identificador único universal (UUIDv4)",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Última actualización"
                    ),
                ),
                # PersonNameMixin
                (
                    "first_name",
                    models.CharField(
                        max_length=60,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name="Nombre(s)",
                    ),
                ),
                (
                    "last_name_father",
                    models.CharField(
                        max_length=60,
                        validators=[django.core.validators.MinLengthValidator(2)],
                        verbose_name="Apellido paterno",
                    ),
                ),
                (
                    "last_name_mother",
                    models.CharField(
                        blank=True,
                        default=None,
                        max_length=60,
                        null=True,
                        verbose_name="Apellido materno",
                    ),
                ),
                # Identificación
                (
                    "enrollment_id",
                    models.CharField(
                        db_index=True,
                        max_length=20,
                        unique=True,
                        validators=[apps.students.validators.validate_enrollment_id],
                        verbose_name="Matrícula / Código escolar",
                    ),
                ),
                (
                    "curp",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default=None,
                        max_length=18,
                        null=True,
                        unique=True,
                        validators=[apps.students.validators.validate_curp],
                        verbose_name="CURP Oficial (RENAPO)",
                    ),
                ),
                # Grupo académico (FK opcional mientras no exista catalogs.Group)
                (
                    "group",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="students",
                        to="students.groupproxy",
                        verbose_name="Grupo escolar",
                    ),
                ),
                # Campos de grupo temporales
                (
                    "grade",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        choices=[(1, "1°"), (2, "2°"), (3, "3°")],
                        null=True,
                        verbose_name="Grado escolar",
                    ),
                ),
                (
                    "group_letter",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("A", "A"), ("B", "B"), ("C", "C"),
                            ("D", "D"), ("E", "E"), ("F", "F"),
                        ],
                        default="",
                        max_length=1,
                        verbose_name="Grupo (letra)",
                    ),
                ),
                (
                    "shift",
                    models.CharField(
                        choices=[
                            ("MATUTINO", "Matutino"), ("VESPERTINO", "Vespertino")
                        ],
                        default="MATUTINO",
                        max_length=15,
                        verbose_name="Turno",
                    ),
                ),
                # Estado
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("ACTIVO", "Activo"),
                            ("BAJA", "Baja"),
                            ("EGRESADO", "Egresado"),
                        ],
                        db_index=True,
                        default="ACTIVO",
                        max_length=10,
                        verbose_name="Estado escolar",
                    ),
                ),
                (
                    "completeness",
                    models.CharField(
                        choices=[
                            ("COMPLETO", "Completo"),
                            ("INCOMPLETO", "Incompleto"),
                        ],
                        default="INCOMPLETO",
                        editable=False,
                        max_length=10,
                        verbose_name="Completitud del expediente",
                    ),
                ),
                # Datos personales
                (
                    "birth_date",
                    models.DateField(
                        blank=True, default=None, null=True,
                        verbose_name="Fecha de nacimiento",
                    ),
                ),
                (
                    "sex",
                    models.CharField(
                        blank=True,
                        choices=[("M", "Masculino"), ("F", "Femenino")],
                        default=None,
                        max_length=1,
                        null=True,
                        verbose_name="Sexo",
                    ),
                ),
                (
                    "photo_url",
                    models.CharField(
                        blank=True, default=None, max_length=500,
                        null=True, verbose_name="Ruta interna de fotografía",
                    ),
                ),
                # Domicilio
                (
                    "address_street",
                    models.CharField(
                        blank=True, default=None, max_length=200,
                        null=True, verbose_name="Calle y número",
                    ),
                ),
                (
                    "address_colonia",
                    models.CharField(
                        blank=True, default=None, max_length=100,
                        null=True, verbose_name="Colonia",
                    ),
                ),
                (
                    "address_municipio",
                    models.CharField(
                        blank=True, default=None, max_length=100,
                        null=True, verbose_name="Municipio",
                    ),
                ),
                (
                    "address_estado",
                    models.CharField(
                        blank=True, default=None, max_length=60,
                        null=True, verbose_name="Estado",
                    ),
                ),
                (
                    "address_postal_code",
                    models.CharField(
                        blank=True, default=None, max_length=5,
                        null=True,
                        validators=[apps.students.validators.validate_postal_code],
                        verbose_name="Código postal",
                    ),
                ),
                # Campos restringidos (RN-EST-12)
                (
                    "blood_type",
                    models.CharField(
                        blank=True, default=None, max_length=5,
                        null=True, verbose_name="Tipo de sangre",
                    ),
                ),
                (
                    "allergies",
                    models.TextField(
                        blank=True, default=None, null=True,
                        verbose_name="Alergias o consideraciones médicas",
                    ),
                ),
                (
                    "has_payment_debt",
                    models.BooleanField(
                        blank=True, default=None, null=True,
                        verbose_name="¿Tiene adeudo de pago?",
                    ),
                ),
            ],
            options={
                "verbose_name": "Estudiante",
                "verbose_name_plural": "Estudiantes",
                "ordering": [
                    "grade", "group_letter", "shift",
                    "last_name_father", "last_name_mother", "first_name",
                ],
                "indexes": [
                    models.Index(
                        fields=["grade", "group_letter", "shift"],
                        name="students_st_grade_grp_idx",
                    ),
                    models.Index(fields=["status"], name="students_st_status_idx"),
                    models.Index(
                        fields=["enrollment_id"],
                        name="students_st_enroll_idx",
                    ),
                ],
            },
        ),
        # ------------------------------------------------------------------
        # StudentGuardian
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="StudentGuardian",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Identificador único universal (UUIDv4)",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Última actualización"
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="student_guardians",
                        to="students.student",
                        verbose_name="Estudiante",
                    ),
                ),
                (
                    "guardian",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="student_guardians",
                        to="students.guardian",
                        verbose_name="Tutor legal",
                    ),
                ),
                (
                    "relationship",
                    models.CharField(
                        choices=[
                            ("MADRE", "Madre"), ("PADRE", "Padre"),
                            ("TUTOR_LEGAL", "Tutor Legal"),
                            ("OTRO", "Otro Familiar / Tutor Autorizado"),
                        ],
                        default="TUTOR_LEGAL",
                        max_length=20,
                        verbose_name="Parentesco",
                    ),
                ),
                (
                    "is_primary_contact",
                    models.BooleanField(
                        default=False, verbose_name="¿Es contacto principal?"
                    ),
                ),
                (
                    "is_valid_contact",
                    models.BooleanField(
                        default=True, verbose_name="¿Contacto válido?"
                    ),
                ),
                (
                    "invalid_reason",
                    models.TextField(
                        blank=True, default=None, null=True,
                        verbose_name="Motivo de invalidación",
                    ),
                ),
                (
                    "consent_status",
                    models.CharField(
                        choices=[
                            ("PENDIENTE", "Pendiente"),
                            ("OTORGADO", "Otorgado"),
                            ("REVOCADO", "Revocado"),
                        ],
                        default="PENDIENTE",
                        max_length=15,
                        verbose_name="Estado de consentimiento",
                    ),
                ),
                (
                    "consent_registered_at",
                    models.DateField(
                        blank=True, default=None, null=True,
                        verbose_name="Fecha de registro de consentimiento",
                    ),
                ),
                (
                    "linked_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        verbose_name="Fecha/hora de alta del vínculo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Vínculo Estudiante–Tutor",
                "verbose_name_plural": "Vínculos Estudiante–Tutor",
                "ordering": ["-is_primary_contact", "relationship"],
                "unique_together": {("student", "guardian")},
            },
        ),
        # ------------------------------------------------------------------
        # GuardianConsentLog
        # ------------------------------------------------------------------
        migrations.CreateModel(
            name="GuardianConsentLog",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="Identificador único universal (UUIDv4)",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha de creación"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Última actualización"
                    ),
                ),
                (
                    "student_guardian",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consent_logs",
                        to="students.studentguardian",
                        verbose_name="Vínculo Estudiante–Tutor",
                    ),
                ),
                (
                    "previous_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("PENDIENTE", "Pendiente"),
                            ("OTORGADO", "Otorgado"),
                            ("REVOCADO", "Revocado"),
                        ],
                        default=None,
                        max_length=15,
                        null=True,
                        verbose_name="Estado anterior",
                    ),
                ),
                (
                    "new_status",
                    models.CharField(
                        choices=[
                            ("PENDIENTE", "Pendiente"),
                            ("OTORGADO", "Otorgado"),
                            ("REVOCADO", "Revocado"),
                        ],
                        max_length=15,
                        verbose_name="Nuevo estado",
                    ),
                ),
                (
                    "registered_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="guardian_consent_logs",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Registrado por",
                    ),
                ),
                (
                    "registered_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Fecha/hora de registro"
                    ),
                ),
            ],
            options={
                "verbose_name": "Historial de Consentimiento",
                "verbose_name_plural": "Historial de Consentimientos",
                "ordering": ["-registered_at"],
            },
        ),
    ]
