"""Configuración del panel de administración Django para el módulo de estudiantes.

Registra los modelos Guardian, Student, GroupProxy, StudentGuardian
y GuardianConsentLog con interfaces usables para el equipo de soporte.
"""

from django.contrib import admin

from .models import Guardian, GuardianConsentLog, GroupProxy, Student, StudentGuardian


# ------------------------------------------------------------------
# Guardian
# ------------------------------------------------------------------

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    """Administración de tutores legales.

    Attributes:
        list_display: Columnas visibles en el listado.
        search_fields: Campos de búsqueda rápida.
        list_filter: Filtros laterales.
        readonly_fields: Campos solo de lectura.
    """

    list_display = (
        "display_name_col",
        "email",
        "phone_number",
        "students_count",
        "created_at",
    )
    search_fields = (
        "first_name",
        "last_name_father",
        "last_name_mother",
        "phone_number",
        "email",
    )
    list_filter = ("created_at",)
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("last_name_father", "last_name_mother", "first_name")
    fieldsets = (
        ("Nombre", {"fields": ("first_name", "last_name_father", "last_name_mother")}),
        ("Contacto", {"fields": ("email", "phone_number")}),
        ("Auditoría", {"fields": ("id", "created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Nombre")
    def display_name_col(self, obj: Guardian) -> str:
        """Retorna el display_name calculado del tutor.

        Args:
            obj: Instancia de Guardian.

        Returns:
            str: Nombre completo calculado.
        """
        return obj.display_name

    @admin.display(description="Alumnos a cargo")
    def students_count(self, obj: Guardian) -> int:
        """Cuenta los estudiantes asociados al tutor.

        Args:
            obj: Instancia de Guardian.

        Returns:
            int: Número de estudiantes.
        """
        return obj.student_guardians.count()


# ------------------------------------------------------------------
# StudentGuardian (inline)
# ------------------------------------------------------------------

class StudentGuardianInline(admin.TabularInline):
    """Inline de vínculos tutor–estudiante dentro de la ficha del alumno."""

    model = StudentGuardian
    extra = 0
    readonly_fields = ("linked_at", "consent_status")
    fields = (
        "guardian",
        "relationship",
        "is_primary_contact",
        "is_valid_contact",
        "consent_status",
        "linked_at",
    )


# ------------------------------------------------------------------
# Student
# ------------------------------------------------------------------

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Administración de estudiantes de la Escuela Secundaria Mixta 5.

    Attributes:
        list_display: Columnas visibles en el listado.
        search_fields: Campos de búsqueda rápida.
        list_filter: Filtros laterales.
        readonly_fields: Campos solo de lectura.
        inlines: Vínculos de tutores inline.
    """

    list_display = (
        "enrollment_id",
        "display_name_col",
        "curp",
        "academic_group",
        "status",
        "completeness",
        "has_active_qr",
        "created_at",
    )
    search_fields = (
        "enrollment_id",
        "curp",
        "first_name",
        "last_name_father",
        "last_name_mother",
    )
    list_filter = ("grade", "group_letter", "shift", "status", "completeness")
    readonly_fields = ("id", "completeness", "created_at", "updated_at")
    inlines = [StudentGuardianInline]
    fieldsets = (
        ("Identificación Escolar", {
            "fields": ("enrollment_id", "curp", "status", "completeness"),
        }),
        ("Datos Personales", {
            "fields": (
                "first_name", "last_name_father", "last_name_mother",
                "birth_date", "sex",
            ),
        }),
        ("Ubicación Académica", {
            "fields": ("grade", "group_letter", "shift"),
        }),
        ("Domicilio", {
            "fields": (
                "address_street", "address_colonia",
                "address_municipio", "address_estado", "address_postal_code",
            ),
            "classes": ("collapse",),
        }),
        ("Salud y Administrativo", {
            "fields": ("blood_type", "allergies", "has_payment_debt"),
            "classes": ("collapse",),
        }),
        ("Fotografía", {
            "fields": ("photo_url",),
        }),
        ("Auditoría", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Nombre")
    def display_name_col(self, obj: Student) -> str:
        """Retorna el display_name calculado del estudiante.

        Args:
            obj: Instancia de Student.

        Returns:
            str: Nombre completo calculado.
        """
        return obj.display_name

    @admin.display(boolean=True, description="QR Activo")
    def has_active_qr(self, obj: Student) -> bool:
        """Indica si el estudiante tiene un QR vigente.

        Args:
            obj: Instancia de Student.

        Returns:
            bool: True si tiene QR activo.
        """
        return obj.active_qr_token is not None


# ------------------------------------------------------------------
# GroupProxy
# ------------------------------------------------------------------

@admin.register(GroupProxy)
class GroupProxyAdmin(admin.ModelAdmin):
    """Administración de grupos académicos (placeholder)."""

    list_display = ("__str__", "grade", "group_letter", "shift", "cutoff_time", "is_active")
    list_filter = ("grade", "shift", "is_active")
    search_fields = ("grade", "group_letter")


# ------------------------------------------------------------------
# GuardianConsentLog
# ------------------------------------------------------------------

@admin.register(GuardianConsentLog)
class GuardianConsentLogAdmin(admin.ModelAdmin):
    """Historial de consentimientos (solo lectura)."""

    list_display = (
        "student_guardian",
        "previous_status",
        "new_status",
        "registered_by",
        "registered_at",
    )
    list_filter = ("new_status", "previous_status")
    readonly_fields = ("id", "registered_at")

    def has_add_permission(self, request) -> bool:
        """Desactiva la creación manual desde el admin."""
        return False

    def has_change_permission(self, request, obj=None) -> bool:
        """Desactiva la edición desde el admin."""
        return False
