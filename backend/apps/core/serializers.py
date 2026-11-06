"""Serializadores del módulo core y operaciones del sistema SIGE.

Implementa los esquemas de validación y respuesta para la ejecución manual
de procesos programados (§3.6 de la Especificación de API REST v2).
"""

from typing import Any

from rest_framework import serializers

from apps.core.models import JobRun


class JobRunSerializer(serializers.ModelSerializer):
    """Serializador para el modelo JobRun (§3.16).

    Expone los resultados de la ejecución de procesos recurrentes y de fondo.
    """

    class Meta:
        model = JobRun
        fields = [
            "id",
            "job_name",
            "run_date",
            "scope",
            "status",
            "started_at",
            "finished_at",
            "evaluated_count",
            "created_count",
            "error",
        ]
        read_only_fields = fields


class RunJobRequestSerializer(serializers.Serializer):
    """Serializador para la solicitud de ejecución manual de un job programado (§3.6).

    Attributes:
        date (DateField): Fecha de negocio a procesar (por defecto la fecha actual).
        shift (ChoiceField): Turno a evaluar ('MATUTINO' o 'VESPERTINO').
        confirm_school_day (BooleanField): Confirmación de día lectivo para levantar guardias.
    """

    date = serializers.DateField(
        required=False,
        allow_null=True,
        help_text="Fecha de negocio en formato YYYY-MM-DD. Opcional (por defecto hoy).",
    )
    shift = serializers.ChoiceField(
        choices=[("MATUTINO", "Matutino"), ("VESPERTINO", "Vespertino")],
        default="MATUTINO",
        required=False,
        help_text="Turno escolar. Relevante únicamente para check_student_absences.",
    )
    confirm_school_day = serializers.BooleanField(
        required=True,
        help_text="Confirmación explícita del Administrador de que la fecha fue día lectivo (D-03).",
    )
