"""Comando de gestión para cargar fotografías de estudiantes de 2°A Matutino.

Lee las fotografías desde la carpeta oficial de credenciales, elimina metadatos
EXIF por privacidad (RN-TRX-02), normaliza a JPEG, almacena los archivos en
MEDIA_ROOT/students/<id>.jpg, calcula el hash SHA-256 (RN-EST-15) y actualiza
los registros de Student correspondientes.
"""

import hashlib
import io
import os
import re
import unicodedata
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction
from django.utils import timezone
from PIL import Image

from apps.students.models import Student


def normalize_name(text: str) -> str:
    """Normaliza un texto eliminando acentos, caracteres especiales y espacios extra.

    Args:
        text (str): Cadena de texto a normalizar.

    Returns:
        str: Texto en mayúsculas sin acentos con espacios simples.
    """
    if not text:
        return ""
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Z0-9]+", " ", norm.upper()).strip()


# Mapeo manual explícito para variaciones ortográficas documentadas
EXPLICIT_NAME_MAP: dict[str, str] = {
    "COBARRUVIAS EDGAR": "EDGAR BARKLEY COVARRUBIAS LUNA",
    "OROZCO YARELI": "JARELI NICOL OROZCO LANDEROS",
    "ARELIS VALENTINA": "VALENTINA NICOLET ARELIS ARCEO",
    "AUROJO LUCAS": "LUCAS EMILIANO ARAUJO ROSALES",
    "SANCHEZ GINA": "GYNA DANIELA SOTO SANCHEZ",
    "GONZALEZ NICOLAS": "YASSER NICOLAS GONZALEZ OCEGUERA",
}


class Command(BaseCommand):
    """Comando para vincular fotografías de 2°A Matutino con sus estudiantes."""

    help = (
        "Carga fotografías institucionales para los alumnos de 2°A Matutino "
        "desde la carpeta de credenciales, omitiendo a quienes ya tienen foto."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        """Configura los argumentos del comando.

        Args:
            parser (CommandParser): Analizador de argumentos.
        """
        parser.add_argument(
            "--folder",
            type=str,
            default=r"c:\Users\gabri\OneDrive\Documentos\CREDENCIALES 2025-2026\FOTOS 2 A",
            help="Ruta absoluta a la carpeta con las fotografías de 2°A.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Punto de entrada para la carga y vinculación de fotografías.

        Args:
            *args (Any): Argumentos posicionales.
            **options (Any): Opciones analizadas.

        Raises:
            CommandError: Si la carpeta de fotografías no existe.
        """
        folder_path = options["folder"]
        if not os.path.exists(folder_path):
            raise CommandError(f"No se encontró la carpeta en: {folder_path}")

        self.stdout.write(self.style.NOTICE("=" * 75))
        self.stdout.write(self.style.NOTICE("  SIGE · CARGA DE FOTOGRAFÍAS: 2°A MATUTINO"))
        self.stdout.write(self.style.NOTICE(f"  Carpeta origen: {folder_path}"))
        self.stdout.write(self.style.NOTICE("=" * 75))

        # Directorio destino en MEDIA_ROOT
        dest_dir = Path(settings.MEDIA_ROOT) / "students"
        dest_dir.mkdir(parents=True, exist_ok=True)

        # Cargar todos los alumnos de 2°A Matutino
        students_2a = list(
            Student.objects.filter(grade=2, group_letter="A", shift="MATUTINO")
            .order_by("last_name_father", "first_name")
        )

        all_files = sorted(
            [f for f in os.listdir(folder_path) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        )

        loaded_count = 0
        skipped_already_has_photo = 0
        skipped_no_match = 0

        with transaction.atomic():
            for filename in all_files:
                name_no_ext = os.path.splitext(filename)[0]
                norm_file = normalize_name(name_no_ext)

                # Descartar archivos genéricos
                if filename.upper().startswith("IMG_") or norm_file == "VALENZUELA":
                    self.stdout.write(
                        self.style.WARNING(f"  [OMITIDO GENÉRICO/DUPLICADO] {filename}")
                    )
                    skipped_no_match += 1
                    continue

                # 1. Comprobar mapeo explícito
                matched_student: Student | None = None
                if norm_file in EXPLICIT_NAME_MAP:
                    target_name = EXPLICIT_NAME_MAP[norm_file]
                    for s in students_2a:
                        if normalize_name(s.display_name) == normalize_name(target_name):
                            matched_student = s
                            break

                # 2. Búsqueda por coincidencia de tokens
                if not matched_student:
                    file_tokens = set(norm_file.split())
                    best_candidates: list[tuple[Student, int]] = []
                    for s in students_2a:
                        student_norm = normalize_name(
                            f"{s.last_name_father} {s.last_name_mother or ''} {s.first_name}"
                        )
                        student_tokens = set(student_norm.split())
                        common = file_tokens.intersection(student_tokens)
                        if len(common) >= 2 or (len(file_tokens) == 1 and file_tokens.issubset(student_tokens)):
                            best_candidates.append((s, len(common)))

                    if best_candidates:
                        best_candidates.sort(key=lambda x: x[1], reverse=True)
                        matched_student = best_candidates[0][0]

                if not matched_student:
                    self.stdout.write(
                        self.style.WARNING(f"  [SIN EMPAREJAR] Archivo '{filename}' no coincide con 2°A.")
                    )
                    skipped_no_match += 1
                    continue

                # Si el estudiante ya tiene foto cargada, omitir
                if matched_student.photo_url:
                    self.stdout.write(
                        self.style.NOTICE(
                            f"  [YA TIENE FOTO] {matched_student.display_name} "
                            f"({matched_student.enrollment_id}) -> omitido."
                        )
                    )
                    skipped_already_has_photo += 1
                    continue

                # Procesar la imagen con Pillow
                source_file_path = os.path.join(folder_path, filename)
                try:
                    with Image.open(source_file_path) as raw_img:
                        clean_img = Image.new("RGB", raw_img.size, (255, 255, 255))
                        if raw_img.mode in ("RGBA", "LA", "P"):
                            clean_img.paste(
                                raw_img,
                                mask=raw_img.split()[-1] if raw_img.mode == "RGBA" else None,
                            )
                        else:
                            clean_img.paste(raw_img.convert("RGB"))

                        # Guardar sin EXIF en formato JPEG
                        dest_filename = f"{matched_student.id}.jpg"
                        dest_file_path = dest_dir / dest_filename

                        buf = io.BytesIO()
                        clean_img.save(buf, format="JPEG", quality=92, optimize=True)
                        photo_bytes = buf.getvalue()

                        with open(dest_file_path, "wb") as f_dest:
                            f_dest.write(photo_bytes)

                        sha256_hash = hashlib.sha256(photo_bytes).hexdigest()

                        # Actualizar registro del estudiante
                        matched_student.photo_url = f"students/{dest_filename}"
                        matched_student.photo_sha256 = sha256_hash
                        matched_student.photo_updated_at = timezone.now()
                        matched_student._recalculate_completeness()
                        matched_student.save(
                            update_fields=[
                                "photo_url",
                                "photo_sha256",
                                "photo_updated_at",
                                "completeness",
                                "updated_at",
                            ]
                        )

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  [FOTO VINCULADA] {matched_student.display_name} "
                                f"({matched_student.enrollment_id}) <- '{filename}'"
                            )
                        )
                        loaded_count += 1

                except Exception as err:
                    self.stdout.write(
                        self.style.ERROR(
                            f"  [ERROR] Falló procesamiento de '{filename}': {err}"
                        )
                    )

        # Resumen final
        self.stdout.write(self.style.NOTICE("\n" + "=" * 75))
        self.stdout.write(
            self.style.SUCCESS(
                f"  CARGA DE FOTOGRAFÍAS 2°A COMPLETADA:\n"
                f"  - Nuevas fotos vinculadas        : {loaded_count}\n"
                f"  - Omitidos (ya tenían foto)      : {skipped_already_has_photo}\n"
                f"  - Omitidos (sin match/genéricos) : {skipped_no_match}\n"
                f"  - Total archivos procesados      : {len(all_files)}"
            )
        )
        self.stdout.write(self.style.NOTICE("=" * 75))
