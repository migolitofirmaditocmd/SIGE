"""Comando para importar SOLO datos de estudiantes de 1°A, 1°B, 1°C y 1°D Matutino.

Lee el archivo 'LISTADO DE CREDENCIALES 2026-2027 PRIMEROS.xlsx', crea los grupos
académicos correspondientes en GroupProxy, descompone y normaliza los nombres
(RN-TRX-08/09/10) y registra a los tutores legales (RN-EST-03/11).

IMPORTANTE: Este comando NO emite tokens QR ni genera credenciales PDF/PNG.
La generación de credenciales se realiza en un paso posterior independiente.
"""

import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Tuple

import openpyxl
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction

from apps.students.models import (
    Guardian,
    GroupProxy,
    Student,
    StudentGuardian,
)
from apps.students.validators import POSTAL_CODE_REGEX

# ---------------------------------------------------------------------------
# Constantes de normalización de apellidos compuestos
# ---------------------------------------------------------------------------
COMPOUND_SURNAMES: tuple[str, ...] = (
    "DE LA CRUZ",
    "DE LA TORRE",
    "DE LA ROSA",
    "DE LA O",
    "DE LOS SANTOS",
    "DEL TORO",
    "DEL RIO",
    "SANCHEZ DE",
)


def split_full_name(raw_name: str) -> Tuple[str, str, str]:
    """Descompone un nombre completo en (apellido_paterno, apellido_materno, nombres).

    Maneja apellidos compuestos comunes y casos de nombre simple o compuesto.

    Args:
        raw_name (str): Cadena con el nombre en formato 'PATERNO MATERNO NOMBRES'.

    Returns:
        Tuple[str, str, str]: Tupla con (paterno, materno, nombres).
    """
    clean = " ".join(raw_name.strip().split())
    clean_upper = clean.upper()
    tokens = clean.split()

    if len(tokens) == 1:
        return tokens[0], "", tokens[0]

    if len(tokens) == 2:
        return tokens[0], "", tokens[1]

    # 1. Comprobar apellido paterno compuesto
    for comp in COMPOUND_SURNAMES:
        if clean_upper.startswith(comp + " "):
            remainder = clean[len(comp):].strip().split()
            materno = remainder[0]
            nombres = " ".join(remainder[1:])
            return comp, materno, nombres

    paterno = tokens[0]
    rest = " ".join(tokens[1:])
    rest_upper = rest.upper()

    # 2. Comprobar apellido materno compuesto
    for comp in COMPOUND_SURNAMES:
        if rest_upper.startswith(comp + " "):
            materno = comp
            nombres = rest[len(comp):].strip()
            return paterno, materno, nombres

    # 3. Formato estándar: [Paterno] [Materno] [Nombre(s)...]
    materno = tokens[1]
    nombres = " ".join(tokens[2:])
    return paterno, materno, nombres


def clean_phone(val: Any) -> str | None:
    """Limpia y valida un número de teléfono a 10 dígitos.

    Args:
        val (Any): Valor original de teléfono.

    Returns:
        str | None: Teléfono de 10 dígitos o None si no cumple el formato.
    """
    if not val:
        return None
    try:
        val_str = str(int(float(val))) if isinstance(val, (int, float)) else str(val)
    except (ValueError, OverflowError):
        val_str = str(val)
    digits = re.sub(r"\D", "", val_str)
    if len(digits) == 10:
        return digits
    if len(digits) > 10:
        return digits[-10:]
    return None


def clean_postal_code(val: Any) -> str | None:
    """Valida y formatea un código postal mexicano de 5 dígitos.

    Args:
        val (Any): Valor original del código postal.

    Returns:
        str | None: Código postal de 5 dígitos o None.
    """
    if not val:
        return None
    try:
        raw = f"{int(float(val)):05d}"
    except (ValueError, OverflowError):
        raw = str(val).strip()
    if POSTAL_CODE_REGEX.match(raw):
        return raw
    return None


def clean_blood_type(val: Any) -> str | None:
    """Normaliza el tipo de sangre a un máximo de 5 caracteres.

    Convierte variantes escritas de forma inconsistente como 'RHO+' u 'ORH+'
    al estándar ABO correcto.

    Args:
        val (Any): Cadena original de tipo de sangre.

    Returns:
        str | None: Tipo de sangre limpio o None.
    """
    if not val:
        return None
    cleaned = "".join(str(val).strip().split()).upper()
    cleaned = cleaned.replace("RHO+", "O+").replace("ORH+", "O+")
    cleaned = cleaned.replace("RN(+)", "+").replace("RH(+)", "+")
    if len(cleaned) > 5:
        cleaned = cleaned[:5]
    return cleaned or None


class Command(BaseCommand):
    """Comando para importar SOLO datos de 1°A, 1°B, 1°C y 1°D Matutino.

    No genera tokens QR ni credenciales. La generación de credenciales
    se realiza en un paso posterior independiente con el comando adecuado.
    """

    help = (
        "Importa SOLO datos de alumnos de 1°A, 1°B, 1°C y 1°D Matutino desde Excel. "
        "NO genera tokens QR ni credenciales PDF/PNG."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        """Configura los argumentos del comando.

        Args:
            parser (CommandParser): Analizador de argumentos.
        """
        parser.add_argument(
            "--file",
            type=str,
            default=None,
            help=(
                "Ruta al archivo Excel "
                "(por defecto 'docs/base de datos en excel/"
                "LISTADO DE CREDENCIALES 2026-2027 PRIMEROS.xlsx')."
            ),
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Punto de entrada para la importación de datos de alumnos de primero.

        Lee el archivo Excel, crea/actualiza grupos académicos, estudiantes y
        tutores legales. No emite tokens QR ni genera archivos de credenciales.

        Args:
            *args (Any): Argumentos posicionales.
            **options (Any): Opciones analizadas.

        Raises:
            CommandError: Si el archivo Excel no existe.
        """
        file_path = options["file"]
        if not file_path:
            file_path = os.path.join(
                settings.BASE_DIR.parent,
                "docs",
                "base de datos en excel",
                "LISTADO DE CREDENCIALES 2026-2027 PRIMEROS.xlsx",
            )

        if not os.path.exists(file_path):
            raise CommandError(f"No se encontró el archivo Excel en: {file_path}")

        self.stdout.write(self.style.NOTICE("=" * 75))
        self.stdout.write(self.style.NOTICE("  SIGE · IMPORTACIÓN DE DATOS: 1°A, 1°B, 1°C Y 1°D MATUTINO"))
        self.stdout.write(self.style.NOTICE(f"  Archivo: {Path(file_path).name}"))
        self.stdout.write(self.style.NOTICE("  NOTA: NO se generarán tokens QR ni credenciales."))
        self.stdout.write(self.style.NOTICE("=" * 75))

        wb = openpyxl.load_workbook(file_path, data_only=True)

        # Especificaciones por grupo (nombre de hoja, grado, grupo, turno)
        # NOTA: La hoja '1°A' tiene un espacio al final en este archivo.
        sheet_specs: dict[str, dict[str, Any]] = {
            "1°A ": {
                "grade": 1,
                "group_letter": "A",
                "shift": "MATUTINO",
                "cutoff_time": "07:15:00",
            },
            "1°B": {
                "grade": 1,
                "group_letter": "B",
                "shift": "MATUTINO",
                "cutoff_time": "07:15:00",
            },
            "1°C": {
                "grade": 1,
                "group_letter": "C",
                "shift": "MATUTINO",
                "cutoff_time": "07:15:00",
            },
            "1°D": {
                "grade": 1,
                "group_letter": "D",
                "shift": "MATUTINO",
                "cutoff_time": "07:15:00",
            },
        }

        total_imported = 0
        total_created = 0
        total_updated = 0

        with transaction.atomic():
            for sheetname, g_info in sheet_specs.items():
                # Buscar la hoja (tolerante a nombres con/sin espacio al final)
                target_sheetname = sheetname
                if target_sheetname not in wb.sheetnames:
                    # Intentar sin espacio o con espacio
                    stripped = sheetname.strip()
                    matching = [
                        s for s in wb.sheetnames
                        if s.strip() == stripped
                    ]
                    if matching:
                        target_sheetname = matching[0]
                    else:
                        # Fallback: buscar por grado y letra
                        matching = [
                            s for s in wb.sheetnames
                            if g_info["group_letter"] in s and "1" in s
                        ]
                        if matching:
                            target_sheetname = matching[0]
                        else:
                            self.stdout.write(
                                self.style.WARNING(
                                    f"Hoja '{sheetname.strip()}' no encontrada. Saltando..."
                                )
                            )
                            continue

                sheet = wb[target_sheetname]

                # Crear o recuperar el grupo académico
                group_obj, group_created = GroupProxy.objects.get_or_create(
                    grade=g_info["grade"],
                    group_letter=g_info["group_letter"],
                    shift=g_info["shift"],
                    defaults={
                        "cutoff_time": g_info["cutoff_time"],
                        "is_active": True,
                    },
                )
                group_label = (
                    "NUEVO" if group_created else "existente"
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nGrupo {group_obj.grade}°{group_obj.group_letter} "
                        f"{group_obj.shift} [{group_label}] "
                        f"(Hoja: '{target_sheetname}')"
                    )
                )

                group_count = 0

                for row_idx in range(2, sheet.max_row + 1):
                    # Estructura de columnas (sin offset):
                    #   Col 1: No. Lista
                    #   Col 2: Nombre completo (PATERNO MATERNO NOMBRES)
                    #   Col 3: Matrícula
                    #   Col 4: Grado
                    #   Col 5: Turno
                    #   Col 6: Dirección (calle)
                    #   Col 7: Colonia
                    #   Col 8: Municipio
                    #   Col 9: Estado
                    #   Col 10: CP
                    #   Col 11: Teléfono del alumno/tutor
                    #   Col 12: Tipo de sangre
                    #   Col 13: Alergias
                    #   Col 14: Contacto de emergencia (nombre del tutor)

                    raw_name = sheet.cell(row_idx, 2).value  # Col B: Nombre
                    if not raw_name or not str(raw_name).strip():
                        continue

                    # Col C: Matrícula
                    raw_mat = sheet.cell(row_idx, 3).value
                    if not raw_mat:
                        continue

                    try:
                        enrollment_id = str(int(float(raw_mat)))
                    except (ValueError, TypeError):
                        enrollment_id = str(raw_mat).strip()

                    # Detectar posible duplicado de matrícula en la fuente
                    existing_student = Student.objects.filter(
                        enrollment_id=enrollment_id
                    ).first()
                    if (
                        existing_student
                        and existing_student.display_name != str(raw_name).strip()
                    ):
                        enrollment_id_alt = f"{enrollment_id}-2"
                        self.stdout.write(
                            self.style.WARNING(
                                f"  Matrícula duplicada en fuente para '{raw_name}': "
                                f"{enrollment_id} -> usando {enrollment_id_alt}"
                            )
                        )
                        enrollment_id = enrollment_id_alt

                    paterno, materno, nombres = split_full_name(str(raw_name))

                    # Domicilio (cols 6–10)
                    street = str(sheet.cell(row_idx, 6).value or "").strip() or None
                    colonia = str(sheet.cell(row_idx, 7).value or "").strip() or None
                    municipio = str(sheet.cell(row_idx, 8).value or "").strip() or None
                    estado = str(sheet.cell(row_idx, 9).value or "").strip() or None
                    cp = clean_postal_code(sheet.cell(row_idx, 10).value)

                    # Teléfono del alumno (col 11) — se reutiliza como tel. del tutor
                    phone_student = clean_phone(sheet.cell(row_idx, 11).value)

                    # Salud (col 12=sangre, col 13=alergias)
                    blood = clean_blood_type(sheet.cell(row_idx, 12).value)
                    allergies = str(sheet.cell(row_idx, 13).value or "").strip() or None

                    # Crear o actualizar el estudiante
                    student, created = Student.objects.update_or_create(
                        enrollment_id=enrollment_id,
                        defaults={
                            "first_name": nombres,
                            "last_name_father": paterno,
                            "last_name_mother": materno or None,
                            "grade": group_obj.grade,
                            "group_letter": group_obj.group_letter,
                            "shift": group_obj.shift,
                            "group": group_obj,
                            "status": Student.Status.ACTIVO,
                            "address_street": street,
                            "address_colonia": colonia,
                            "address_municipio": municipio,
                            "address_estado": estado,
                            "address_postal_code": cp,
                            "blood_type": blood,
                            "allergies": allergies,
                        },
                    )

                    action_label = "CREADO" if created else "ACTUALIZADO"
                    self.stdout.write(
                        f"  [{action_label}] {student.display_name} ({enrollment_id})"
                    )
                    if created:
                        total_created += 1
                    else:
                        total_updated += 1

                    # Tutor / Contacto de emergencia (col 14: nombre del tutor)
                    # El teléfono del tutor no está en este archivo; se usa el
                    # teléfono del alumno (col 11) como número de contacto de emergencia.
                    raw_tutor = sheet.cell(row_idx, 14).value
                    if raw_tutor and str(raw_tutor).strip():
                        t_pat, t_mat, t_nom = split_full_name(str(raw_tutor))
                        guardian, _ = Guardian.objects.get_or_create(
                            first_name=t_nom,
                            last_name_father=t_pat,
                            last_name_mother=t_mat or None,
                            defaults={"phone_number": phone_student},
                        )
                        # Actualizar teléfono si el tutor no tenía uno registrado
                        if phone_student and not guardian.phone_number:
                            guardian.phone_number = phone_student
                            guardian.save()

                        StudentGuardian.objects.update_or_create(
                            student=student,
                            guardian=guardian,
                            defaults={
                                "relationship": StudentGuardian.Relationship.TUTOR_LEGAL,
                                "is_primary_contact": True,
                                "is_valid_contact": bool(guardian.phone_number),
                            },
                        )

                    total_imported += 1
                    group_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  -> {group_count} alumnos procesados en "
                        f"1°{g_info['group_letter']} {g_info['shift']}."
                    )
                )

        # Resumen final
        self.stdout.write(self.style.NOTICE("\n" + "=" * 75))
        self.stdout.write(
            self.style.SUCCESS(
                f"  IMPORTACIÓN COMPLETADA (sin QR ni credenciales):\n"
                f"  - Total procesados  : {total_imported}\n"
                f"  - Nuevos (CREADOS)  : {total_created}\n"
                f"  - Actualizados      : {total_updated}"
            )
        )
        self.stdout.write(self.style.NOTICE("=" * 75))

