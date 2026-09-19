import uuid
from django.db import models

class TimeStampedUUIDModel(models.Model):
    """
    Modelo abstracto base con identificador único universal (UUIDv4)
    y marcas de tiempo automáticas para auditoría de cambios.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Identificador único universal (UUIDv4)"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']
