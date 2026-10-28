"""Servicio de validación y partición para exportación de credenciales (RN-CRE-01).

Implementa las reglas de negocio de inclusión y exclusión de estudiantes y docentes
para la emisión de credenciales físicas y stickers térmicos en la Secundaria Mixta 5.
"""

from typing import Any
import uuid

from django.db.models import QuerySet
from rest_framework import status

from apps.core.exceptions import SIGEAPIException
from apps.students.models import GroupProxy, Student


class CredentialExportService:
    """Servicio que aplica las reglas de exportación de credenciales (RN-CRE-01).

    Reglas aplicadas:
        - Solo personas en estatus ACTIVO pueden incluirse (RN-CRE-01).
        - Deben contar con un token QR en estatus ACTIVE (RN-CRE-01, RN-QR-01).
        - Si mode == 'CREDENCIAL', se exige obligatoriamente fotografía (photo_url).
        - Si mode == 'STICKER', la fotografía no es requerida (RN-CRE-01).
        - Los excluidos nunca se omiten en silencio; se reportan con su motivo.
    """

    REASON_NO_PHOTO = "SIN_FOTOGRAFIA"
    REASON_NOT_ACTIVE = "NO_ACTIVO"
    REASON_NO_ACTIVE_QR = "SIN_QR_VIGENTE"

    @classmethod
    def evaluate_export_candidates(
        cls,
        mode: str,
        entity_type: str = "STUDENT",
        entity_ids: list[str] | None = None,
        group_id: str | None = None,
    ) -> dict[str, Any]:
        """Evalúa y particiona los candidatos a exportación entre incluidos y excluidos.

        Args:
            mode (str): Modalidad de exportación ('CREDENCIAL' o 'STICKER').
            entity_type (str, optional): 'STUDENT' o 'TEACHER'. Defaults to 'STUDENT'.
            entity_ids (list[str] | None, optional): Lista de UUIDs específicos. Defaults to None.
            group_id (str | None, optional): UUID o identificador de grupo escolar. Defaults to None.

        Returns:
            dict[str, Any]: Diccionario con:
                - included (int): Cantidad de alumnos que cumplen todos los requisitos.
                - included_students (list[dict]): Datos estructurados para renderizado.
                - excluded (list[dict]): Candidatos rechazados con entity_id, display_name y reason.

        Raises:
            SIGEAPIException: Si los parámetros son inválidos o mutuamente excluyentes (HTTP 422).
        """
        # Validar selección de candidatos: exactamente uno de entity_ids o group_id
        has_entities = bool(entity_ids and len(entity_ids) > 0)
        has_group = bool(group_id and str(group_id).strip())

        if (has_entities and has_group) or (not has_entities and not has_group):
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message=(
                    "Debe proporcionar exactamente uno de 'entity_ids' o "
                    "'group_id' para la exportación."
                ),
                details={
                    "export_target": [
                        "Especifique una lista de IDs de alumnos o un grupo escolar."
                    ]
                },
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        if entity_type.upper() != "STUDENT":
            raise SIGEAPIException(
                error_code="VALIDATION_ERROR",
                message=f"Tipo de entidad '{entity_type}' no soportado actualmente.",
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Construir queryset base
        qs: QuerySet[Student] = Student.objects.prefetch_related(
            "qr_tokens", "student_guardians__guardian"
        )

        if has_entities:
            try:
                uuids = [uuid.UUID(str(eid).strip()) for eid in entity_ids]  # type: ignore
            except ValueError:
                raise SIGEAPIException(
                    error_code="VALIDATION_ERROR",
                    message="Uno o más 'entity_ids' no tienen formato UUIDv4 válido.",
                    http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            qs = qs.filter(id__in=uuids)
        elif has_group:
            # Buscar si group_id coincide con GroupProxy o con clave grado/letra
            group_str = str(group_id).strip()
            group_qs = qs.filter(group__id=group_str) if _is_uuid(group_str) else qs.none()
            if group_qs.exists():
                qs = group_qs
            else:
                # Fallback: buscar por group_letter o combinación
                qs = qs.filter(group_letter__iexact=group_str)

        candidates = list(qs.order_by("grade", "group_letter", "last_name_father", "first_name"))

        if not candidates and has_entities:
            # IDs especificados no encontrados
            raise SIGEAPIException(
                error_code="NOT_FOUND",
                message="No se encontraron estudiantes con los identificadores indicados.",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        included_list: list[dict[str, Any]] = []
        excluded_list: list[dict[str, Any]] = []

        mode_upper = mode.upper()
        for student in candidates:
            # 1. Regla: Solo personas en estatus ACTIVO (RN-CRE-01)
            if student.status != Student.Status.ACTIVO:
                excluded_list.append(
                    {
                        "entity_id": str(student.id),
                        "display_name": student.display_name,
                        "reason": cls.REASON_NOT_ACTIVE,
                    }
                )
                continue

            # 2. Regla: Debe contar con QR vigente en estatus ACTIVE (RN-CRE-01)
            active_token = student.active_qr_token
            if not active_token:
                excluded_list.append(
                    {
                        "entity_id": str(student.id),
                        "display_name": student.display_name,
                        "reason": cls.REASON_NO_ACTIVE_QR,
                    }
                )
                continue

            # 3. Regla: Credencial completa exige fotografía; sticker no (RN-CRE-01)
            if mode_upper == "CREDENCIAL" and not student.photo_url:
                excluded_list.append(
                    {
                        "entity_id": str(student.id),
                        "display_name": student.display_name,
                        "reason": cls.REASON_NO_PHOTO,
                    }
                )
                continue

            # Cumple todos los requisitos
            included_list.append(
                {
                    "id": str(student.id),
                    "display_name": student.display_name,
                    "enrollment_id": student.enrollment_id,
                    "curp": student.curp or "",
                    "academic_group": student.academic_group,
                    "grade": student.grade,
                    "group_letter": student.group_letter,
                    "shift": student.shift,
                    "token": str(active_token.token),
                    "photo_url": student.photo_url,
                }
            )

        return {
            "included": len(included_list),
            "included_students": included_list,
            "excluded": excluded_list,
        }


def _is_uuid(value: str) -> bool:
    """Verifica si una cadena representa un UUID válido."""
    try:
        uuid.UUID(str(value).strip())
        return True
    except (ValueError, AttributeError):
        return False
