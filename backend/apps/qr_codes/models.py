import uuid
from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedUUIDModel

class QRCodeToken(TimeStampedUUIDModel):
    """
    Token criptográfico opaco para credenciales físicas de estudiantes.
    Protege los datos personales del menor (LFPDPPP) al no almacenar CURP
    ni nombre en texto plano dentro del código de barras 2D.
    
    Permite rotación ágil ante pérdidas: un token extraviado se marca como REVOKED
    y se emite uno nuevo sin alterar el historial de asistencia ni el expediente del alumno.
    """
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Activo y vigente'
        REVOKED = 'REVOKED', 'Revocado (extravío o reemisión)'
        EXPIRED = 'EXPIRED', 'Expirado (fin de ciclo)'

    token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        db_index=True,
        editable=False,
        verbose_name="Token UUIDv4 impreso en credencial"
    )
    student = models.ForeignKey(
        'students.Student',
        on_delete=models.CASCADE,
        related_name='qr_tokens',
        verbose_name="Estudiante titular"
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="Estado del token"
    )
    hmac_signature = models.CharField(
        max_length=64,
        blank=True,
        editable=False,
        verbose_name="Firma criptográfica HMAC-SHA256"
    )
    issued_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha y hora de emisión"
    )
    revoked_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha y hora de revocación"
    )
    revocation_reason = models.CharField(
        max_length=150,
        blank=True,
        default="",
        verbose_name="Motivo de revocación (ej: extravío, daño, reposición)"
    )

    class Meta:
        verbose_name = "Token de Credencial QR"
        verbose_name_plural = "Tokens de Credenciales QR"
        ordering = ['-issued_at']
        constraints = [
            # Regla de integridad absoluta: Un estudiante solo puede tener UN token con estado ACTIVE simultáneamente
            models.UniqueConstraint(
                fields=['student'],
                condition=models.Q(status='ACTIVE'),
                name='unique_active_qr_token_per_student'
            )
        ]

    def __str__(self):
        return f"QR [{self.status}] -> {self.student.enrollment_id} - {self.student.full_name} ({self.token})"

    def revoke(self, reason: str = "Reemplazo de credencial"):
        """Revoca el token actual de forma explícita."""
        self.status = self.Status.REVOKED
        self.revoked_at = timezone.now()
        self.revocation_reason = reason
        self.save(update_fields=['status', 'revoked_at', 'revocation_reason', 'updated_at'])
