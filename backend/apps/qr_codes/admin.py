from django.contrib import admin
from django.utils.html import format_html
from .models import QRCodeToken

@admin.register(QRCodeToken)
class QRCodeTokenAdmin(admin.ModelAdmin):
    list_display = (
        'student_enrollment',
        'student_name',
        'status_badge',
        'token_preview',
        'issued_at',
        'revoked_at'
    )
    search_fields = (
        'student__enrollment_id',
        'student__first_name',
        'student__last_name_father',
        'student__last_name_mother',
        'token'
    )
    list_filter = ('status', 'issued_at')
    readonly_fields = ('id', 'token', 'hmac_signature', 'issued_at', 'revoked_at', 'created_at', 'updated_at')
    ordering = ('-issued_at',)

    @admin.display(description="Matrícula")
    def student_enrollment(self, obj):
        return obj.student.enrollment_id

    @admin.display(description="Estudiante")
    def student_name(self, obj):
        return obj.student.full_name

    @admin.display(description="Token (UUID)")
    def token_preview(self, obj):
        return f"{str(obj.token)[:8]}...{str(obj.token)[-8:]}"

    @admin.display(description="Estado")
    def status_badge(self, obj):
        colors = {
            QRCodeToken.Status.ACTIVE: "#22c55e",
            QRCodeToken.Status.REVOKED: "#ef4444",
            QRCodeToken.Status.EXPIRED: "#6b7280",
        }
        color = colors.get(obj.status, "#3b82f6")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 6px; font-weight: bold; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
