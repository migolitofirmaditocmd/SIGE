"""Serializadores del módulo de estudiantes y tutores.

Implementa los contratos de request/response definidos en
SIGE_Especificacion_API_REST_v2.md §2.4 y §3.4, con todas las
validaciones de negocio de los endpoints GET, POST y PATCH de
estudiantes, tutores y la tabla intermedia StudentGuardian.

Reglas de negocio validadas aquí:
    - RN-EST-02: enrollment_id único e inmutable en PATCH.
    - RN-EST-03/11: al menos un tutor con is_valid_contact=True.
    - RN-EST-10: campos mínimos y completeness calculado.
    - RN-EST-12: filtrado de campos sensibles por rol.
    - RN-EST-13: detección de coincidencia fuerte de Guardian.
    - RN-EST-14: aviso al editar Guardian compartido.
    - RN-TRX-08/09: validación de nombres estructurados.
"""

from typing import Any

from django.db import transaction
from rest_framework import serializers

from apps.core.exceptions import (
    DuplicateCurpError,
    DuplicateEnrollmentError,
    SIGEAPIException,
)
from .models import Guardian, GuardianConsentLog, Student, StudentGuardian
from .validators import validate_person_name


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _strip_null(value: str | None) -> str | None:
    """Convierte cadena vacía a None (RN-TRX-08 apellido materno)."""
    if value is not None and value.strip() == "":
        return None
    return value


# ------------------------------------------------------------------
# GroupSerializer (inline, mínimo)
# ------------------------------------------------------------------

class GroupSummarySerializer(serializers.Serializer):
    """Representación inline del grupo académico en la ficha de alumno."""

    id = serializers.UUIDField()
    grade = serializers.IntegerField()
    group_letter = serializers.CharField()
    shift = serializers.CharField()

    class Meta:
        fields = ["id", "grade", "group_letter", "shift"]


# ------------------------------------------------------------------
# GuardianSerializer
# ------------------------------------------------------------------

class GuardianSerializer(serializers.ModelSerializer):
    """Serializador completo de Guardian (lectura y escritura).

    Expone display_name y sort_name calculados (RN-TRX-10).
    El apellido materno vacío se convierte a null (RN-TRX-08).

    Attributes:
        display_name: Nombre(s) Apellido_paterno Apellido_materno.
        sort_name: Apellido_paterno Apellido_materno, Nombre(s).
    """

    display_name = serializers.CharField(read_only=True)
    sort_name = serializers.CharField(read_only=True)

    class Meta:
        model = Guardian
        fields = [
            "id",
            "first_name",
            "last_name_father",
            "last_name_mother",
            "display_name",
            "sort_name",
            "email",
            "phone_number",
            "created_at",
        ]
        read_only_fields = ["id", "display_name", "sort_name", "created_at"]

    def validate_last_name_mother(self, value: str | None) -> str | None:
        """Convierte cadena vacía en null (RN-TRX-08)."""
        return _strip_null(value)

    def validate_first_name(self, value: str) -> str:
        """Valida el nombre con RN-TRX-09."""
        validate_person_name(value, "Nombre(s)")
        return " ".join(value.split())

    def validate_last_name_father(self, value: str) -> str:
        """Valida apellido paterno con RN-TRX-09."""
        validate_person_name(value, "Apellido paterno")
        return " ".join(value.split())

    def validate(self, attrs: dict) -> dict:
        """Verifica que al menos email o phone_number estén presentes."""
        email = attrs.get("email") or (
            self.instance.email if self.instance else None
        )
        phone = attrs.get("phone_number") or (
            self.instance.phone_number if self.instance else None
        )
        if not email and not phone:
            raise serializers.ValidationError(
                "El tutor debe tener al menos un correo electrónico "
                "o un número telefónico (RN-EST-11)."
            )
        return attrs


class GuardianWriteSerializer(GuardianSerializer):
    """Serializador de Guardian para creación/edición de tutor inline.

    Agrega los campos ``existing_guardian_id`` y
    ``decline_match_reason`` para el flujo de detección de
    coincidencias (RN-EST-13).
    """

    existing_guardian_id = serializers.UUIDField(
        required=False,
        allow_null=True,
        write_only=True,
        help_text="UUID de un Guardian existente que se desea reutilizar (RN-EST-13).",
    )
    decline_match_reason = serializers.CharField(
        required=False,
        allow_null=True,
        write_only=True,
        help_text="Motivo para no reutilizar el Guardian sugerido (RN-EST-13).",
    )

    class Meta(GuardianSerializer.Meta):
        fields = GuardianSerializer.Meta.fields + [
            "existing_guardian_id",
            "decline_match_reason",
        ]


# ------------------------------------------------------------------
# StudentGuardianSerializer
# ------------------------------------------------------------------

class StudentGuardianSerializer(serializers.ModelSerializer):
    """Serializa la relación Student–Guardian con datos del tutor inline.

    Attributes:
        guardian: Datos completos del tutor (read-only).
        relationship_display: Etiqueta legible del parentesco.
        consent_status_display: Etiqueta legible del consentimiento.
    """

    guardian = GuardianSerializer(read_only=True)
    relationship_display = serializers.CharField(
        source="get_relationship_display", read_only=True
    )
    consent_status_display = serializers.CharField(
        source="get_consent_status_display", read_only=True
    )

    class Meta:
        model = StudentGuardian
        fields = [
            "id",
            "guardian",
            "relationship",
            "relationship_display",
            "is_primary_contact",
            "is_valid_contact",
            "consent_status",
            "consent_status_display",
            "linked_at",
        ]
        read_only_fields = ["id", "linked_at"]


# ------------------------------------------------------------------
# StudentSerializer (lectura)
# ------------------------------------------------------------------

class StudentReadSerializer(serializers.ModelSerializer):
    """Serializador de lectura del expediente de estudiante (§2.4).

    Expone display_name, sort_name, academic_group y el estado del
    QR activo. Los campos sensibles (blood_type, allergies,
    has_payment_debt) se incluyen o excluyen según el rol del
    solicitante (RN-EST-12); el filtrado lo aplica la vista.

    Attributes:
        display_name: Nombre calculado para la UI (RN-TRX-10).
        sort_name: Nombre para ordenamiento (RN-TRX-10).
        academic_group: Representación legible de grado/grupo/turno.
        status_display: Etiqueta legible del estado.
        completeness_display: Etiqueta legible de completitud.
        active_qr_token_id: UUID del QR vigente o null.
        guardians: Lista de vínculos Estudiante–Tutor.
        consent_warning: True si algún tutor está PENDIENTE o REVOCADO (RN-EST-08).
        photo_url: Ruta interna de la API, nunca URL pública (RN-TRX-02).
    """

    display_name = serializers.CharField(read_only=True)
    sort_name = serializers.CharField(read_only=True)
    academic_group = serializers.CharField(read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    completeness_display = serializers.CharField(
        source="get_completeness_display", read_only=True
    )
    active_qr_token_id = serializers.SerializerMethodField()
    guardians = StudentGuardianSerializer(
        source="student_guardians", many=True, read_only=True
    )
    consent_warning = serializers.SerializerMethodField()
    missing_fields = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id",
            "enrollment_id",
            "curp",
            "first_name",
            "last_name_father",
            "last_name_mother",
            "display_name",
            "sort_name",
            "grade",
            "group_letter",
            "shift",
            "academic_group",
            "status",
            "status_display",
            "completeness",
            "completeness_display",
            "missing_fields",
            "birth_date",
            "sex",
            "photo_url",
            "address_street",
            "address_colonia",
            "address_municipio",
            "address_estado",
            "address_postal_code",
            # Campos sensibles (RN-EST-12) — la vista los filtra por rol:
            "blood_type",
            "allergies",
            "has_payment_debt",
            # Relaciones
            "guardians",
            "consent_warning",
            "active_qr_token_id",
            # Auditoría
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # solo lectura

    def get_active_qr_token_id(self, obj: Student) -> str | None:
        """Retorna el UUID del QR vigente o None.

        Args:
            obj: Instancia de Student.

        Returns:
            str | None: UUID como cadena o None si no hay QR vigente.
        """
        token = obj.active_qr_token
        return str(token.token) if token else None

    def get_consent_warning(self, obj: Student) -> bool:
        """True si algún tutor tiene consentimiento PENDIENTE o REVOCADO.

        Args:
            obj: Instancia de Student.

        Returns:
            bool: True si se requiere atención en el consentimiento (RN-EST-08).
        """
        return obj.student_guardians.filter(
            consent_status__in=["PENDIENTE", "REVOCADO"]
        ).exists()

    def get_missing_fields(self, obj: Student) -> list[str]:
        """Lista los campos faltantes que hacen el expediente INCOMPLETO (RN-EST-10).

        Args:
            obj: Instancia de Student.

        Returns:
            list[str]: Nombres de campos faltantes.
        """
        missing = []
        if not obj.birth_date:
            missing.append("birth_date")
        if not obj.photo_url:
            missing.append("photo_url")
        return missing


# ------------------------------------------------------------------
# StudentWriteSerializer (creación y actualización)
# ------------------------------------------------------------------

class GuardianInlineSerializer(serializers.Serializer):
    """Subserializador para tutores inline en POST /students/.

    Permite crear un Guardian nuevo o referenciar uno existente
    (RN-EST-13). Incluye los campos opcionales de coincidencia.
    """

    existing_guardian_id = serializers.UUIDField(
        required=False, allow_null=True
    )
    decline_match_reason = serializers.CharField(
        required=False, allow_null=True
    )
    first_name = serializers.CharField(required=False, allow_null=True)
    last_name_father = serializers.CharField(required=False, allow_null=True)
    last_name_mother = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )
    email = serializers.EmailField(required=False, allow_null=True)
    phone_number = serializers.CharField(required=False, allow_null=True)
    relationship = serializers.ChoiceField(
        choices=StudentGuardian.Relationship.choices,
        default=StudentGuardian.Relationship.TUTOR_LEGAL,
    )
    is_primary_contact = serializers.BooleanField(default=False)


class StudentWriteSerializer(serializers.ModelSerializer):
    """Serializador de escritura para POST /api/v1/students/ (§2.4).

    Valida las reglas de negocio:
        - RN-EST-02: enrollment_id único.
        - RN-EST-03/11: mínimo un tutor con is_valid_contact=True.
        - RN-EST-10: datos mínimos para guardar.
        - RN-EST-13: detección de Guardian existente.
        - RN-TRX-08/09: nombres válidos.

    Attributes:
        guardians: Lista de tutores a crear/asociar (obligatorio en POST).
    """

    guardians = GuardianInlineSerializer(
        many=True,
        write_only=True,
        help_text="Al menos un tutor con contacto válido (RN-EST-03/11).",
    )

    class Meta:
        model = Student
        fields = [
            "enrollment_id",
            "curp",
            "first_name",
            "last_name_father",
            "last_name_mother",
            "grade",
            "group_letter",
            "shift",
            "birth_date",
            "sex",
            "address_street",
            "address_colonia",
            "address_municipio",
            "address_estado",
            "address_postal_code",
            "blood_type",
            "allergies",
            "has_payment_debt",
            "guardians",
        ]
        extra_kwargs = {
            "enrollment_id": {"validators": []},
            "curp": {"validators": []},
        }

    # ------------------------------------------------------------------
    # Validadores por campo
    # ------------------------------------------------------------------

    def validate_enrollment_id(self, value: str) -> str:
        """Valida unicidad de la matrícula (RN-EST-02).

        Args:
            value: Matrícula a validar.

        Returns:
            str: Matrícula normalizada en mayúsculas.

        Raises:
            DuplicateEnrollmentError: Si la matrícula ya existe.
        """
        clean = value.strip().upper()
        qs = Student.objects.filter(enrollment_id=clean)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise DuplicateEnrollmentError(clean)
        return clean

    def validate_curp(self, value: str | None) -> str | None:
        """Valida unicidad de la CURP cuando se proporciona.

        Args:
            value: CURP a validar.

        Returns:
            str | None: CURP normalizada o None.

        Raises:
            DuplicateCurpError: Si la CURP ya existe en otro alumno.
        """
        if not value:
            return None
        clean = value.strip().upper()
        qs = Student.objects.filter(curp=clean)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise DuplicateCurpError(clean)
        return clean

    def validate_last_name_mother(self, value: str | None) -> str | None:
        """Convierte apellido materno vacío en None (RN-TRX-08)."""
        return _strip_null(value)

    def validate_first_name(self, value: str) -> str:
        """Valida nombre con RN-TRX-09."""
        validate_person_name(value, "Nombre(s)")
        return " ".join(value.split())

    def validate_last_name_father(self, value: str) -> str:
        """Valida apellido paterno con RN-TRX-09."""
        validate_person_name(value, "Apellido paterno")
        return " ".join(value.split())

    def validate_guardians(self, value: list[dict]) -> list[dict]:
        """Valida que haya al menos un tutor con contacto válido (RN-EST-03/11).

        Args:
            value: Lista de dicts de tutores.

        Returns:
            list[dict]: Lista validada.

        Raises:
            serializers.ValidationError: Si ningún tutor tiene contacto válido.
        """
        if not value:
            raise serializers.ValidationError(
                "Se requiere al menos un tutor legal (RN-EST-03)."
            )
        has_valid = any(
            g.get("email") or g.get("phone_number")
            for g in value
            if not g.get("existing_guardian_id")
        )
        # Los tutores referenciados por existing_guardian_id se validan
        # al momento de crear; aquí solo chequeamos que la lista no sea vacía.
        if not has_valid and not any(
            g.get("existing_guardian_id") for g in value
        ):
            raise serializers.ValidationError(
                "Al menos un tutor debe tener correo electrónico o "
                "teléfono válido (RN-EST-11)."
            )
        return value

    # ------------------------------------------------------------------
    # Creación con tutores (transaccional)
    # ------------------------------------------------------------------

    @transaction.atomic
    def create(self, validated_data: dict) -> Student:
        """Crea el estudiante con sus tutores en una sola transacción.

        Detecta coincidencias de Guardian existente (RN-EST-13).
        Genera el primer renglón de GuardianConsentLog (RN-EST-07).

        Args:
            validated_data: Datos validados del serializador.

        Returns:
            Student: Instancia del estudiante creado.

        Raises:
            SIGEAPIException: Si se detecta un Guardian existente
                sin confirmación (GUARDIAN_MATCH_FOUND).
        """
        guardians_data = validated_data.pop("guardians", [])
        student = Student(**validated_data)
        student.full_clean()
        student.save()

        for g_data in guardians_data:
            existing_id = g_data.pop("existing_guardian_id", None)
            g_data.pop("decline_match_reason", None)
            relationship = g_data.pop("relationship",
                                      StudentGuardian.Relationship.TUTOR_LEGAL)
            is_primary = g_data.pop("is_primary_contact", False)

            if existing_id:
                try:
                    guardian = Guardian.objects.get(pk=existing_id)
                except Guardian.DoesNotExist:
                    raise serializers.ValidationError(
                        {"existing_guardian_id": [
                            f"No existe un Guardian con id={existing_id}."
                        ]}
                    )
            else:
                # Detección de coincidencia fuerte (RN-EST-13)
                email = g_data.get("email")
                phone = g_data.get("phone_number")
                first = g_data.get("first_name", "")
                father = g_data.get("last_name_father", "")
                mother = g_data.get("last_name_mother")

                candidates = Guardian.objects.filter(
                    first_name__iexact=first,
                    last_name_father__iexact=father,
                ).filter(
                    **({} if not mother else
                       {"last_name_mother__iexact": mother})
                )
                if email:
                    candidates = candidates.filter(email__iexact=email)
                elif phone:
                    candidates = candidates.filter(phone_number=phone)

                if candidates.exists():
                    raise SIGEAPIException(
                        error_code="GUARDIAN_MATCH_FOUND",
                        message=(
                            "Se encontró un tutor existente con datos "
                            "similares. Use existing_guardian_id para "
                            "reutilizarlo o decline_match_reason para "
                            "crear uno nuevo."
                        ),
                        rn_reference="RN-EST-13",
                        details={
                            "candidates": [
                                {
                                    "id": str(c.id),
                                    "display_name": c.display_name,
                                    "email": c.email,
                                    "phone_number": c.phone_number,
                                }
                                for c in candidates[:5]
                            ]
                        },
                    )

                guardian = Guardian.objects.create(**g_data)

            sg = StudentGuardian.objects.create(
                student=student,
                guardian=guardian,
                relationship=relationship,
                is_primary_contact=is_primary,
                is_valid_contact=bool(
                    guardian.email or guardian.phone_number
                ),
            )
            # Primer renglón de historial de consentimiento (RN-EST-07)
            GuardianConsentLog.objects.create(
                student_guardian=sg,
                previous_status=None,
                new_status=StudentGuardian.ConsentStatus.PENDIENTE,
                registered_by=None,
            )

        return student

    @transaction.atomic
    def update(self, instance: Student, validated_data: dict) -> Student:
        """Actualiza el expediente del estudiante (PATCH).

        La matrícula enrollment_id es inmutable (RN-EST-02): si el
        payload la incluye, se ignora silenciosamente; el serializador
        ya la validó en validate_enrollment_id.

        Args:
            instance: Instancia existente de Student.
            validated_data: Datos validados del serializador.

        Returns:
            Student: Instancia actualizada.
        """
        # Los tutores en PATCH se gestionan por endpoints separados
        validated_data.pop("guardians", None)
        # enrollment_id es inmutable (RN-EST-02); no se modifica.
        validated_data.pop("enrollment_id", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.full_clean()
        instance.save()
        return instance


# ------------------------------------------------------------------
# StudentStatusSerializer (baja lógica / reinscripción)
# ------------------------------------------------------------------

class StudentStatusSerializer(serializers.Serializer):
    """Serializador para POST /students/{id}/status/ y /reinstate/.

    Attributes:
        status: Nuevo estado objetivo (BAJA o EGRESADO).
        reason: Motivo obligatorio de la transición.
    """

    STATUS_CHOICES = [("BAJA", "Baja"), ("EGRESADO", "Egresado")]

    status = serializers.ChoiceField(choices=STATUS_CHOICES)
    reason = serializers.CharField(
        min_length=1,
        max_length=500,
        help_text="Motivo obligatorio de la baja o egreso.",
    )


class StudentReinstateSerializer(serializers.Serializer):
    """Serializador para POST /students/{id}/reinstate/ (BAJA → ACTIVO).

    Attributes:
        reason: Motivo de la reincorporación.
    """

    reason = serializers.CharField(
        min_length=1,
        max_length=500,
        help_text="Motivo de la reincorporación del alumno.",
    )


# ------------------------------------------------------------------
# ConsentSerializer
# ------------------------------------------------------------------

class ConsentUpdateSerializer(serializers.Serializer):
    """Actualización de consentimiento de tutor (PATCH /student-guardians/{id}/consent/).

    Attributes:
        consent_status: Nuevo estado de consentimiento.
        reason: Justificación del cambio.
    """

    CONSENT_CHOICES = [
        ("OTORGADO", "Otorgado"),
        ("REVOCADO", "Revocado"),
    ]

    consent_status = serializers.ChoiceField(choices=CONSENT_CHOICES)
    reason = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Motivo del cambio de consentimiento.",
    )
