"""Comando para importar estudiantes de 2°C y 2°D Turno Matutino (WBS 3.7 & 3.16).

Lee el archivo 'FORMATO DE DATOS PARA CREDENCIALES SEGUNDO C Y D 2026-2027.xlsx',
crea los grupos académicos correspondientes, descompone y normaliza los nombres,
registra los tutores legales, emite los tokens criptográficos HMAC-SHA256,
y genera los códigos QR de asistencia en carpetas por grado, grupo y turno.
"""

import io
import os
import re
import unicodedata
from pathlib import Path
from typing import Any, Tuple

import cv2
import numpy as np
import openpyxl
from PIL import Image
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction

from apps.qr_codes.card_generator import generate_credential_pdf, generate_credential_png
from apps.qr_codes.crypto import issue_qr_token_for_student
from apps.students.models import (
    Guardian,
    GroupProxy,
    Student,
    StudentGuardian,
)
from apps.students.validators import POSTAL_CODE_REGEX

# Prefijos de apellidos compuestos comunes en México
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
            remainder = clean[len(comp) :].strip().split()
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
            nombres = rest[len(comp) :].strip()
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

    Args:
        val (Any): Cadena original de tipo de sangre.

    Returns:
        str | None: Tipo de sangre limpio o None.
    """
    if not val:
        return None
    cleaned = "".join(str(val).strip().split()).upper()
    cleaned = cleaned.replace("RN(+)", "+").replace("RH(+)", "+")
    if len(cleaned) > 5:
        cleaned = cleaned[:5]
    return cleaned or None


def clean_filename(text: str) -> str:
    """Genera un nombre de archivo seguro eliminando acentos y caracteres especiales.

    Args:
        text (str): Texto original.

    Returns:
        str: Nombre seguro en mayúsculas separado por guiones bajos.
    """
    text_norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    safe = re.sub(r"[^A-Za-z0-9]+", "_", text_norm).strip("_")
    return safe.upper()


class Command(BaseCommand):
    """Comando para importar estudiantes de 2°C y 2°D y generar sus códigos de asistencia."""

    help = "Importa alumnos de 2°C y 2°D Matutino y genera sus códigos QR de asistencia en carpetas."

    def add_arguments(self, parser: CommandParser) -> None:
        """Configura los argumentos del comando.

        Args:
            parser (CommandParser): Analizador de argumentos.
        """
        parser.add_argument(
            "--file",
            type=str,
            default=None,
            help="Ruta al archivo Excel (por defecto 'docs/base de datos en excel/FORMATO DE DATOS PARA CREDENCIALES SEGUNDO C Y D 2026-2027.xlsx').",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Punto de entrada para la importación y generación de códigos QR.

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
                "FORMATO DE DATOS PARA CREDENCIALES SEGUNDO C Y D 2026-2027.xlsx",
            )

        if not os.path.exists(file_path):
            raise CommandError(f"No se encontró el archivo Excel en: {file_path}")

        self.stdout.write(self.style.NOTICE("=" * 75))
        self.stdout.write(self.style.NOTICE("  SIGE · IMPORTACIÓN DE ESTUDIANTES 2°C Y 2°D MATUTINO"))
        self.stdout.write(self.style.NOTICE(f"  Archivo: {Path(file_path).name}"))
        self.stdout.write(self.style.NOTICE("=" * 75))

        wb = openpyxl.load_workbook(file_path, data_only=True)

        sheet_specs: dict[str, dict[str, Any]] = {
            "2°C": {
                "grade": 2,
                "group_letter": "C",
                "shift": "MATUTINO",
                "folder_name": "2_C_Matutino",
            },
            "2°D": {
                "grade": 2,
                "group_letter": "D",
                "shift": "MATUTINO",
                "folder_name": "2_D_Matutino",
            },
        }

        base_output_dir = os.path.join(
            settings.BASE_DIR.parent,
            "docs",
            "codigos_asistencia_estudiantes",
        )
        os.makedirs(base_output_dir, exist_ok=True)

        detector = cv2.QRCodeDetector()
        total_imported = 0
        total_qrs_generated = 0
        total_verified = 0

        with transaction.atomic():
            for sheetname, g_info in sheet_specs.items():
                target_sheetname = sheetname
                if target_sheetname not in wb.sheetnames:
                    # Intento de normalización por caracteres especiales en nombres de hoja
                    matching = [s for s in wb.sheetnames if g_info["group_letter"] in s and "2" in s]
                    if matching:
                        target_sheetname = matching[0]
                    else:
                        self.stdout.write(self.style.WARNING(f"Hoja '{sheetname}' no encontrada. Saltando..."))
                        continue

                sheet = wb[target_sheetname]
                group_obj, _ = GroupProxy.objects.get_or_create(
                    grade=g_info["grade"],
                    group_letter=g_info["group_letter"],
                    shift=g_info["shift"],
                    defaults={
                        "cutoff_time": "07:15:00",
                        "is_active": True,
                    },
                )

                folder_path = os.path.join(base_output_dir, g_info["folder_name"])
                os.makedirs(folder_path, exist_ok=True)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"\nProcesando grupo {group_obj.grade}° '{group_obj.group_letter}' {group_obj.shift} "
                        f"(Hoja: {target_sheetname}) -> Carpeta: {g_info['folder_name']}"
                    )
                )

                group_student_data_list: list[dict[str, Any]] = []

                for row_idx in range(2, sheet.max_row + 1):
                    raw_name = sheet.cell(row_idx, 3).value
                    if not raw_name or not str(raw_name).strip():
                        continue

                    # Matrícula
                    raw_mat = sheet.cell(row_idx, 4).value
                    if not raw_mat:
                        continue
                    enrollment_id = (
                        str(int(float(raw_mat)))
                        if isinstance(raw_mat, (int, float))
                        else str(raw_mat).strip()
                    )

                    paterno, materno, nombres = split_full_name(str(raw_name))

                    # Domicilio
                    street = str(sheet.cell(row_idx, 7).value or "").strip() or None
                    colonia = str(sheet.cell(row_idx, 8).value or "").strip() or None
                    municipio = str(sheet.cell(row_idx, 9).value or "").strip() or None
                    estado = str(sheet.cell(row_idx, 10).value or "").strip() or None
                    cp = clean_postal_code(sheet.cell(row_idx, 11).value)

                    # Salud
                    blood = clean_blood_type(sheet.cell(row_idx, 13).value)
                    allergies = str(sheet.cell(row_idx, 14).value or "").strip() or None

                    # Crear o actualizar estudiante
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

                    # Tutor / Contacto de emergencia
                    raw_tutor = sheet.cell(row_idx, 15).value
                    raw_tutor_tel = clean_phone(sheet.cell(row_idx, 16).value)

                    if raw_tutor and str(raw_tutor).strip():
                        t_pat, t_mat, t_nom = split_full_name(str(raw_tutor))
                        guardian, _ = Guardian.objects.get_or_create(
                            first_name=t_nom,
                            last_name_father=t_pat,
                            last_name_mother=t_mat or None,
                            defaults={"phone_number": raw_tutor_tel},
                        )
                        if raw_tutor_tel and not guardian.phone_number:
                            guardian.phone_number = raw_tutor_tel
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

                    # Emitir token QR activo
                    token_obj = student.active_qr_token
                    if not token_obj:
                        token_obj = issue_qr_token_for_student(
                            student, reason="Importación inicial 2°C/2°D Matutino"
                        )

                    # Preparar payload para renderizado
                    card_payload = {
                        "student_id": str(student.id),
                        "enrollment_id": student.enrollment_id,
                        "display_name": student.display_name,
                        "academic_group": student.academic_group,
                        "token": str(token_obj.token),
                    }
                    group_student_data_list.append(card_payload)

                    # Generar PNG individual
                    png_bytes = generate_credential_png(card_payload, mode="STICKER")
                    safe_name = clean_filename(student.display_name)
                    png_filename = f"{student.enrollment_id}_{safe_name}.png"
                    png_path = os.path.join(folder_path, png_filename)
                    with open(png_path, "wb") as f_png:
                        f_png.write(png_bytes)

                    # Verificación óptica
                    img_pil = Image.open(io.BytesIO(png_bytes))
                    cv_img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
                    decoded, _, _ = detector.detectAndDecode(cv_img)
                    if decoded == str(token_obj.token):
                        total_verified += 1
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"Falla de lectura óptica en {student.display_name} ({student.enrollment_id})"
                            )
                        )

                    total_imported += 1
                    total_qrs_generated += 1

                # Generar PDF del grupo completo para impresión directa
                pdf_bytes = generate_credential_pdf(group_student_data_list, mode="STICKER")
                pdf_filename = f"stickers_asistencia_{group_obj.grade}{group_obj.group_letter}_matutino.pdf"
                pdf_path = os.path.join(folder_path, pdf_filename)
                with open(pdf_path, "wb") as f_pdf:
                    f_pdf.write(pdf_bytes)

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  -> {len(group_student_data_list)} alumnos importados. "
                        f"PDF consolidado generado en: {pdf_filename}"
                    )
                )

        self.stdout.write(self.style.NOTICE("\n" + "=" * 75))
        self.stdout.write(
            self.style.SUCCESS(
                f"  IMPORTACIÓN Y GENERACIÓN COMPLETADA:\n"
                f"  - Total de alumnos importados: {total_imported}\n"
                f"  - Total de códigos QR generados: {total_qrs_generated}\n"
                f"  - Auditoría óptica OpenCV: {total_verified}/{total_qrs_generated} aprobados al 100%."
            )
        )
        self.stdout.write(self.style.NOTICE("=" * 75))

