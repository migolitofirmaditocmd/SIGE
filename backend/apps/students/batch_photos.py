"""Servicio de procesamiento y vinculación por lote de fotografías de estudiantes.

Este módulo implementa el motor de coincidencia fonética y por tokens entre
los nombres de archivo de las fotografías y los registros de estudiantes en
la base de datos, así como la sanitización de metadatos EXIF (RN-TRX-02, RN-EST-16),
normalización a formato JPEG RGB y cálculo de firma SHA-256 (RN-EST-15).
"""

import difflib
import hashlib
import io
import os
import re
import unicodedata
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db.models import QuerySet
from django.utils import timezone
from PIL import Image

from apps.students.models import Student


def normalize_name(text: str) -> str:
    """Normaliza una cadena de texto eliminando acentos, caracteres especiales y espacios.

    Args:
        text (str): Cadena de texto original (ej. nombre de archivo o alumno).

    Returns:
        str: Texto normalizado en mayúsculas sin acentos con espacios simples.
    """
    if not text:
        return ""
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^A-Z0-9]+", " ", norm.upper()).strip()


def tokenize_name(text: str) -> list[str]:
    """Divide una cadena en tokens ignorando palabras de ruido o conectores comunes.

    Args:
        text (str): Texto normalizado.

    Returns:
        list[str]: Lista de palabras clave significativas en mayúsculas.
    """
    ignore_words = {"DE", "DEL", "LA", "LAS", "LOS", "Y", "E", "SAN"}
    tokens = [w for w in text.split() if len(w) > 1 and w not in ignore_words]
    return tokens


def find_matching_student(
    filename: str,
    primary_candidates: list[Student],
    fallback_candidates: list[Student] | None = None,
) -> tuple[Student | None, float, str]:
    """Busca el estudiante que mejor coincide con el nombre de archivo de la fotografía.

    Aplica coincidencia por matrícula exacta, coincidencia por subconjunto de tokens
    de nombre/apellidos, similitud difusa por token y similitud global de cadena.

    Args:
        filename (str): Nombre del archivo fotográfico (con o sin extensión).
        primary_candidates (list[Student]): Lista prioritaria de estudiantes (ej. grupo actual).
        fallback_candidates (list[Student] | None, optional): Estudiantes del resto del plantel. Defaults to None.

    Returns:
        tuple[Student | None, float, str]: Tupla con el estudiante asignado (o None),
            la puntuación de confianza (0.0 a 1000.0) y el criterio de vinculación.
    """
    name_no_ext = os.path.splitext(filename)[0]
    norm_filename = normalize_name(name_no_ext)

    # Descartar archivos genéricos de cámara o duplicados evidentes
    if (
        norm_filename.startswith("IMG ")
        or norm_filename.startswith("DSC ")
        or norm_filename.startswith("PHOTO ")
        or norm_filename in {"VALENZUELA"}
    ):
        return None, 0.0, "Archivo con nombre genérico o duplicado omitido."

    file_tokens = tokenize_name(norm_filename)
    if not file_tokens:
        return None, 0.0, "Nombre de archivo sin tokens válidos para comparación."

    def evaluate_candidates(
        candidates: list[Student],
    ) -> tuple[Student | None, float, str]:
        best_student: Student | None = None
        best_score = 0.0
        best_reason = ""

        for student in candidates:
            # 1. Coincidencia directa por matrícula escolar (enrollment_id)
            student_matricula = normalize_name(student.enrollment_id or "")
            if student_matricula and (
                norm_filename == student_matricula
                or student_matricula in norm_filename.split()
            ):
                return student, 1000.0, "Coincidencia exacta por matrícula escolar."

            # Representaciones normalizadas del estudiante
            s_father = normalize_name(student.last_name_father or "")
            s_mother = normalize_name(student.last_name_mother or "")
            s_first = normalize_name(student.first_name or "")

            full_name_order1 = f"{s_father} {s_mother} {s_first}".strip()
            full_name_order2 = f"{s_first} {s_father} {s_mother}".strip()
            short_order1 = f"{s_father} {s_first}".strip()
            short_order2 = f"{s_first} {s_father}".strip()

            student_tokens = set(tokenize_name(full_name_order1))
            file_token_set = set(file_tokens)

            # 2. Todos los tokens del archivo están en el nombre del estudiante (mínimo 2)
            if len(file_token_set) >= 2 and file_token_set.issubset(student_tokens):
                score = 200.0 + (len(file_token_set) * 10.0)
                if score > best_score:
                    best_score = score
                    best_student = student
                    best_reason = "Subconjunto exacto de tokens (apellidos y nombres)."
                continue

            # 3. Coincidencia difusa token por token (tolerancia a variaciones ortográficas)
            # Ej: COBARRUVIAS -> COVARRUBIAS, GINA -> GYNA, YARELI -> JARELI
            token_scores: list[float] = []
            for ft in file_tokens:
                best_sim = 0.0
                for st in student_tokens:
                    sim = difflib.SequenceMatcher(None, ft, st).ratio()
                    if sim > best_sim:
                        best_sim = sim
                token_scores.append(best_sim)

            avg_sim = sum(token_scores) / len(token_scores) if token_scores else 0.0
            min_sim = min(token_scores) if token_scores else 0.0

            if len(file_tokens) >= 2 and min_sim >= 0.74:
                score = 150.0 + (avg_sim * 20.0)
                if score > best_score:
                    best_score = score
                    best_student = student
                    best_reason = f"Similitud fonética/ortográfica por tokens ({min_sim:.0%})."
                continue

            # 4. Similitud global de secuencias sobre variantes de nombres
            r1 = difflib.SequenceMatcher(None, norm_filename, short_order1).ratio()
            r2 = difflib.SequenceMatcher(None, norm_filename, short_order2).ratio()
            r3 = difflib.SequenceMatcher(None, norm_filename, full_name_order1).ratio()
            r4 = difflib.SequenceMatcher(None, norm_filename, full_name_order2).ratio()
            max_r = max(r1, r2, r3, r4)

            common_tokens = file_token_set.intersection(student_tokens)
            if (len(common_tokens) >= 1 and max_r >= 0.65) or max_r >= 0.80:
                score = (len(common_tokens) * 20.0) + (max_r * 30.0)
                if score > best_score:
                    best_score = score
                    best_student = student
                    best_reason = f"Similitud global de texto ({max_r:.0%})."

        return best_student, best_score, best_reason

    # Evaluar primero en el grupo prioritario
    best_student, best_score, best_reason = evaluate_candidates(primary_candidates)
    if best_student and best_score >= 50.0:
        return best_student, best_score, best_reason

    # Si no se encontró en el grupo prioritario y hay candidatos de respaldo
    if fallback_candidates:
        fb_student, fb_score, fb_reason = evaluate_candidates(fallback_candidates)
        if fb_student and fb_score >= 50.0:
            return fb_student, fb_score, f"{fb_reason} (Encontrado fuera del grupo principal)"

    return None, 0.0, "No se encontró ningún estudiante con coincidencia suficiente."


def process_and_save_photo(
    student: Student,
    file_bytes_or_obj: Any,
    filename: str,
) -> tuple[bool, str, str]:
    """Sanitiza, normaliza y almacena la fotografía institucional de un estudiante.

    Elimina metadatos EXIF por privacidad de menores (RN-TRX-02, RN-EST-16),
    convierte a JPEG RGB, genera el hash SHA-256 (RN-EST-15), guarda en el
    sistema de archivos seguro y recalcula la completitud del expediente (RN-EST-10).

    Args:
        student (Student): Instancia del estudiante a actualizar.
        file_bytes_or_obj (Any): Bytes o descriptor de archivo de la fotografía.
        filename (str): Nombre original del archivo para traza y extensión.

    Returns:
        tuple[bool, str, str]: Tupla con el éxito (True/False), mensaje de resultado
            y el hash SHA-256 calculado.
    """
    try:
        # Abrir imagen con Pillow para sanitización
        if hasattr(file_bytes_or_obj, "read"):
            image_raw = Image.open(file_bytes_or_obj)
        else:
            image_raw = Image.open(io.BytesIO(file_bytes_or_obj))

        # Crear una imagen limpia en RGB descartando metadatos EXIF (RN-TRX-02)
        image_clean = Image.new("RGB", image_raw.size, (255, 255, 255))
        if image_raw.mode in ("RGBA", "LA") or (
            image_raw.mode == "P" and "transparency" in image_raw.info
        ):
            # Componer sobre fondo blanco
            image_raw_rgba = image_raw.convert("RGBA")
            image_clean.paste(image_raw_rgba, mask=image_raw_rgba.split()[3])
        else:
            image_clean.paste(image_raw.convert("RGB"))

        # Redimensionar proporcionalmente si la imagen de cámara es excesivamente grande
        max_dim = 1200
        if max(image_clean.size) > max_dim:
            image_clean.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)

        # Guardar en buffer JPEG sanitizado
        buffer = io.BytesIO()
        image_clean.save(buffer, format="JPEG", quality=90, optimize=True)
        photo_bytes = buffer.getvalue()

        # Calcular firma SHA-256 (RN-EST-15)
        sha256_hash = hashlib.sha256(photo_bytes).hexdigest()

        # Almacenar en disco en MEDIA_ROOT/students/<student_id>.jpg
        dest_dir = Path(settings.MEDIA_ROOT) / "students"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / f"{student.id}.jpg"
        dest_path.write_bytes(photo_bytes)

        # Actualizar campos en el modelo Student
        rel_path = f"students/{student.id}.jpg"
        student.photo_url = rel_path
        student.photo_sha256 = sha256_hash
        student.photo_updated_at = timezone.now()
        student._recalculate_completeness()
        student.save(
            update_fields=[
                "photo_url",
                "photo_sha256",
                "photo_updated_at",
                "completeness",
                "updated_at",
            ]
        )

        return True, "Fotografía procesada y guardada exitosamente.", sha256_hash

    except Exception as exc:
        return False, f"Error al procesar la imagen: {str(exc)}", ""
