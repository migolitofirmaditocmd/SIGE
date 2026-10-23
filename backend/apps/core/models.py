"""Modelos base y mixins reutilizables del proyecto SIGE.

Contiene el modelo abstracto con UUID y timestamps, y el mixin
de nombre estructurado (§3.0 del Modelo de Datos v3.2).
"""

import uuid

from django.core.validators import MinLengthValidator
from django.db import models


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
