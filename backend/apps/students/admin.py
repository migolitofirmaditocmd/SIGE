from django.contrib import admin
from .models import Guardian, Student

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'relationship', 'phone_number', 'email', 'students_count', 'created_at')
    search_fields = ('full_name', 'phone_number', 'email')
    list_filter = ('relationship', 'created_at')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('full_name',)

    @admin.display(description="Alumnos a cargo")
    def students_count(self, obj):
        return obj.students.count()


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'enrollment_id',
        'full_name',
        'curp',
        'academic_group',
        'status',
        'guardian_contact',
        'has_active_qr',
        'created_at'
    )
    search_fields = (
        'enrollment_id',
        'curp',
        'first_name',
        'last_name_father',
        'last_name_mother',
        'guardian__full_name',
        'guardian__phone_number'
    )
    list_filter = ('grade', 'group', 'shift', 'status')
    readonly_fields = ('id', 'created_at', 'updated_at')
    autocomplete_fields = ('guardian',)
    fieldsets = (
        ("Identificación Escolar", {
            "fields": ("enrollment_id", "curp", "status")
        }),
        ("Datos Personales", {
            "fields": ("first_name", "last_name_father", "last_name_mother")
        }),
        ("Ubicación Académica", {
            "fields": ("grade", "group", "shift")
        }),
        ("Contacto y Tutor Legal", {
            "fields": ("guardian", "medical_notes")
        }),
        ("Auditoría", {
            "fields": ("id", "created_at", "updated_at"),
            "classes": ("collapse",)
        })
    )

    @admin.display(description="Tutor / Teléfono")
    def guardian_contact(self, obj):
        return f"{obj.guardian.full_name} ({obj.guardian.phone_number})"

    @admin.display(boolean=True, description="QR Activo")
    def has_active_qr(self, obj):
        return obj.active_qr_token is not None
