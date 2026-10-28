"""Motor de generación de credenciales y stickers escolares en PDF y PNG.

Implementa la generación de documentos para la Escuela Secundaria Mixta 5
conforme al estándar CR-80 (85.6 mm × 53.98 mm) y stickers térmicos
de alta resolución según las especificaciones RF-CRE-01, RF-CRE-02 y RN-CRE-01.
"""

import io
import os
import uuid
from pathlib import Path
from typing import Any

from django.conf import settings
from PIL import Image, ImageColor, ImageDraw, ImageFont
import qrcode
from qrcode.constants import ERROR_CORRECT_M
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------
# Constantes de diseño institucional (Escuela Secundaria Mixta 5)
# ----------------------------------------------------------------------
CR80_WIDTH_MM: float = 85.60
CR80_HEIGHT_MM: float = 53.98
STICKER_WIDTH_MM: float = 50.00
STICKER_HEIGHT_MM: float = 30.00

# Paleta institucional
COLOR_PRIMARY_HEX: str = "#1A365D"  # Azul profundo institucional
COLOR_SECONDARY_HEX: str = "#D69E2E"  # Dorado institucional
COLOR_DARK_TEXT_HEX: str = "#1A202C"  # Gris carbón para máxima legibilidad
COLOR_MUTED_TEXT_HEX: str = "#4A5568"  # Gris medio para etiquetas
COLOR_BG_LIGHT_HEX: str = "#F7FAFC"  # Fondo marfil suave


def _get_pil_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Obtiene una fuente TrueType del sistema o recurre a la fuente por defecto.

    Args:
        size (int): Tamaño de fuente en puntos/píxeles.
        bold (bool, optional): Indica si se prefiere fuente en negrita. Defaults to False.

    Returns:
        ImageFont.ImageFont: Objeto de fuente listo para dibujar en Pillow.
    """
    candidates = (
        ["arialbd.ttf", "segoeuib.ttf", "calibrib.ttf", "DejaVuSans-Bold.ttf"]
        if bold
        else ["arial.ttf", "segoeui.ttf", "calibri.ttf", "DejaVuSans.ttf"]
    )
    for font_name in candidates:
        try:
            return ImageFont.truetype(font_name, size)
        except (OSError, IOError):
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def generate_qr_pil_image(
    token_str: str | uuid.UUID,
    box_size: int = 8,
    border: int = 1,
) -> Image.Image:
    """Genera una imagen Pillow del código QR con contraste óptico para impresión.

    Args:
        token_str (str | uuid.UUID): UUID del token impreso en la credencial.
        box_size (int, optional): Tamaño en píxeles de cada módulo QR. Defaults to 8.
        border (int, optional): Grosor del borde en módulos. Defaults to 1.

    Returns:
        Image.Image: Imagen Pillow en modo RGB con contraste puro (negro/blanco).
    """
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=box_size,
        border=border,
    )
    qr.add_data(str(token_str).strip())
    qr.make(fit=True)
    pil_img = qr.make_image(fill_color="black", back_color="white")
    return pil_img.convert("RGB")


def _draw_student_photo_pil(
    draw: ImageDraw.ImageDraw,
    photo_path: str | None,
    box: tuple[int, int, int, int],
    base_img: Image.Image,
    initials: str = "AL",
) -> None:
    """Dibuja la fotografía del estudiante o una silueta estilizada con iniciales.

    Args:
        draw (ImageDraw.ImageDraw): Contexto de dibujo Pillow.
        photo_path (str | None): Ruta relativa o absoluta a la fotografía.
        box (tuple[int, int, int, int]): Coordenadas (x0, y0, x1, y1).
        base_img (Image.Image): Imagen base donde incrustar la foto.
        initials (str, optional): Iniciales a mostrar si no hay foto. Defaults to "AL".
    """
    x0, y0, x1, y1 = box
    w = x1 - x0
    h = y1 - y0

    loaded = False
    if photo_path:
        # Intentar ruta absoluta o dentro de MEDIA_ROOT
        full_path = Path(photo_path)
        if not full_path.is_absolute():
            full_path = Path(settings.MEDIA_ROOT) / photo_path

        if full_path.exists() and full_path.is_file():
            try:
                with Image.open(full_path) as photo_raw:
                    photo_resized = photo_raw.convert("RGB").resize(
                        (w, h), Image.Resampling.LANCZOS
                    )
                    base_img.paste(photo_resized, (x0, y0))
                    loaded = True
            except Exception:
                loaded = False

    if not loaded:
        # Dibujar silueta institucional con fondo suave
        draw.rectangle([x0, y0, x1, y1], fill="#E2E8F0", outline="#CBD5E0", width=2)
        font = _get_pil_font(max(14, int(w * 0.28)), bold=True)
        draw.text(
            (x0 + w // 2, y0 + h // 2),
            initials[:2].upper(),
            fill="#718096",
            font=font,
            anchor="mm",
        )
    else:
        # Borde decorativo alrededor de la foto cargada
        draw.rectangle([x0, y0, x1, y1], outline="#A0AEC0", width=2)


def generate_credential_png(
    student_data: dict[str, Any],
    mode: str = "CREDENCIAL",
) -> bytes:
    """Genera una imagen PNG de alta resolución de la credencial o sticker escolar.

    Renderizado a 300 DPI estándar para previsualización nítida e impresión fotográfica.

    Args:
        student_data (dict[str, Any]): Diccionario con los datos del estudiante:
            - display_name (str): Nombre completo del alumno.
            - enrollment_id (str): Matrícula institucional.
            - academic_group (str): Grado, grupo y turno (ej. "1°A Matutino").
            - curp (str, opcional): CURP del alumno.
            - token (str | uuid.UUID): UUID del token QR activo.
            - photo_url (str, opcional): Ruta a la foto del alumno.
        mode (str, optional): 'CREDENCIAL' o 'STICKER'. Defaults to 'CREDENCIAL'.

    Returns:
        bytes: Flujo binario PNG listo para ser transmitido o guardado.
    """
    scale = 300 / 25.4  # píxeles por milímetro a 300 DPI (~11.81 px/mm)

    if mode == "STICKER":
        w_px = int(STICKER_WIDTH_MM * scale)
        h_px = int(STICKER_HEIGHT_MM * scale)
        img = Image.new("RGB", (w_px, h_px), "white")
        draw = ImageDraw.Draw(img)

        # Marco del sticker
        draw.rectangle([0, 0, w_px - 1, h_px - 1], outline="#CBD5E0", width=2)

        # Cabecera
        font_header = _get_pil_font(22, bold=True)
        draw.rectangle([0, 0, w_px, 45], fill=COLOR_PRIMARY_HEX)
        draw.text(
            (w_px // 2, 22),
            "ESC. SEC. MIXTA 5 · STICKER QR",
            fill="white",
            font=font_header,
            anchor="mm",
        )

        # Código QR a la izquierda
        qr_size = h_px - 60
        token_val = (
            student_data.get("token")
            or student_data.get("qr_token")
            or student_data.get("active_qr_token")
            or ""
        )
        if not str(token_val).strip():
            raise ValueError(
                f"Token QR ausente o vacío para el estudiante {student_data.get('display_name', 'Desconocido')}"
            )
        qr_img = generate_qr_pil_image(str(token_val).strip(), box_size=6, border=1)
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.NEAREST)
        img.paste(qr_img, (15, 52))

        # Texto informativo a la derecha
        info_x = qr_size + 30
        font_name = _get_pil_font(26, bold=True)
        font_data = _get_pil_font(22, bold=False)

        name = student_data.get("display_name", "")
        if len(name) > 24:
            name = name[:22] + "..."
        draw.text((info_x, 65), name, fill=COLOR_DARK_TEXT_HEX, font=font_name)
        draw.text(
            (info_x, 110),
            f"Matrícula: {student_data.get('enrollment_id', '')}",
            fill=COLOR_MUTED_TEXT_HEX,
            font=font_data,
        )
        draw.text(
            (info_x, 150),
            f"Grupo: {student_data.get('academic_group', '')}",
            fill=COLOR_PRIMARY_HEX,
            font=font_data,
        )

        buf = io.BytesIO()
        img.save(buf, format="PNG", dpi=(300, 300))
        return buf.getvalue()

    # ------------------------------------------------------------------
    # Formato CREDENCIAL CR-80 completa (85.6 mm × 53.98 mm)
    # ------------------------------------------------------------------
    w_px = int(CR80_WIDTH_MM * scale)
    h_px = int(CR80_HEIGHT_MM * scale)
    img = Image.new("RGB", (w_px, h_px), COLOR_BG_LIGHT_HEX)
    draw = ImageDraw.Draw(img)

    # Marco exterior suave
    draw.rectangle([0, 0, w_px - 1, h_px - 1], outline="#E2E8F0", width=3)

    # Cabecera institucional
    header_height = int(h_px * 0.22)
    draw.rectangle([0, 0, w_px, header_height], fill=COLOR_PRIMARY_HEX)
    draw.rectangle(
        [0, header_height - 6, w_px, header_height], fill=COLOR_SECONDARY_HEX
    )

    font_sub = _get_pil_font(18, bold=False)
    font_main = _get_pil_font(28, bold=True)
    font_cred = _get_pil_font(20, bold=True)

    draw.text(
        (w_px // 2, int(header_height * 0.22)),
        "SECRETARÍA DE EDUCACIÓN JALISCO",
        fill="#E2E8F0",
        font=font_sub,
        anchor="mm",
    )
    draw.text(
        (w_px // 2, int(header_height * 0.55)),
        "ESCUELA SECUNDARIA MIXTA No. 5",
        fill="white",
        font=font_main,
        anchor="mm",
    )
    draw.text(
        (w_px // 2, int(header_height * 0.85)),
        "CREDENCIAL ESCOLAR · CICLO 2025-2026",
        fill="#FEFCBF",
        font=font_cred,
        anchor="mm",
    )

    # Columna izquierda: Fotografía del estudiante
    photo_w = int(w_px * 0.26)
    photo_h = int(photo_w * 1.30)
    photo_x = int(w_px * 0.04)
    photo_y = header_height + int((h_px - header_height - photo_h) * 0.35)

    name_tokens = student_data.get("display_name", "").split()
    initials = "".join(t[0] for t in name_tokens[:2]) if name_tokens else "AL"

    _draw_student_photo_pil(
        draw=draw,
        photo_path=student_data.get("photo_url"),
        box=(photo_x, photo_y, photo_x + photo_w, photo_y + photo_h),
        base_img=img,
        initials=initials,
    )

    # Columna derecha: Código QR de alta resolución
    qr_side = int(w_px * 0.25)
    qr_x = w_px - qr_side - int(w_px * 0.04)
    qr_y = header_height + int((h_px - header_height - qr_side) * 0.32)

    token_val = (
        student_data.get("token")
        or student_data.get("qr_token")
        or student_data.get("active_qr_token")
        or ""
    )
    if not str(token_val).strip():
        raise ValueError(
            f"Token QR ausente o vacío para el estudiante {student_data.get('display_name', 'Desconocido')}"
        )
    qr_pil = generate_qr_pil_image(
        str(token_val).strip(), box_size=8, border=1
    )
    qr_pil = qr_pil.resize((qr_side, qr_side), Image.Resampling.NEAREST)

    # Borde blanco con sombra sutil para el QR
    draw.rectangle(
        [qr_x - 3, qr_y - 3, qr_x + qr_side + 3, qr_y + qr_side + 3],
        fill="white",
        outline="#CBD5E0",
        width=1,
    )
    img.paste(qr_pil, (qr_x, qr_y))

    # Etiqueta de seguridad bajo el QR
    font_qr_label = _get_pil_font(15, bold=True)
    draw.text(
        (qr_x + qr_side // 2, qr_y + qr_side + 12),
        "CÓDIGO DE ASISTENCIA",
        fill="#718096",
        font=font_qr_label,
        anchor="mm",
    )

    # Columna central: Datos del estudiante
    info_x = photo_x + photo_w + int(w_px * 0.03)
    info_y = header_height + 25

    font_label = _get_pil_font(17, bold=False)
    font_val_bold = _get_pil_font(25, bold=True)
    font_val_med = _get_pil_font(21, bold=True)
    font_val = _get_pil_font(21, bold=False)

    # Alumno
    draw.text((info_x, info_y), "ALUMNO(A):", fill=COLOR_MUTED_TEXT_HEX, font=font_label)
    name = student_data.get("display_name", "ESTUDIANTE")
    if len(name) > 28:
        # Dividir en dos líneas si es muy largo
        split_idx = name[:26].rfind(" ")
        if split_idx == -1:
            split_idx = 24
        line1 = name[:split_idx]
        line2 = name[split_idx:].strip()
        draw.text((info_x, info_y + 22), line1, fill=COLOR_PRIMARY_HEX, font=font_val_bold)
        draw.text((info_x, info_y + 48), line2, fill=COLOR_PRIMARY_HEX, font=font_val_bold)
        info_y += 28
    else:
        draw.text((info_x, info_y + 22), name, fill=COLOR_PRIMARY_HEX, font=font_val_bold)

    # Matrícula
    draw.text((info_x, info_y + 60), "MATRÍCULA:", fill=COLOR_MUTED_TEXT_HEX, font=font_label)
    draw.text(
        (info_x, info_y + 80),
        student_data.get("enrollment_id", "---"),
        fill=COLOR_DARK_TEXT_HEX,
        font=font_val_med,
    )

    # Grado y Turno
    draw.text(
        (info_x, info_y + 115),
        "GRADO Y TURNO:",
        fill=COLOR_MUTED_TEXT_HEX,
        font=font_label,
    )
    draw.text(
        (info_x, info_y + 135),
        student_data.get("academic_group", "---"),
        fill=COLOR_DARK_TEXT_HEX,
        font=font_val,
    )

    # CURP (si está disponible)
    curp = student_data.get("curp")
    if curp:
        draw.text(
            (info_x, info_y + 170),
            "CURP:",
            fill=COLOR_MUTED_TEXT_HEX,
            font=font_label,
        )
        draw.text(
            (info_x, info_y + 190),
            curp,
            fill=COLOR_DARK_TEXT_HEX,
            font=_get_pil_font(18, bold=True),
        )

    # Franja inferior decorativa
    draw.rectangle([0, h_px - 26, w_px, h_px], fill=COLOR_PRIMARY_HEX)
    font_footer = _get_pil_font(16, bold=False)
    draw.text(
        (w_px // 2, h_px - 13),
        "Esta credencial es personal e intransferible · Escuela Secundaria Mixta 5",
        fill="white",
        font=font_footer,
        anchor="mm",
    )

    buf = io.BytesIO()
    img.save(buf, format="PNG", dpi=(300, 300))
    return buf.getvalue()


def generate_credential_pdf(
    students_data: list[dict[str, Any]],
    mode: str = "CREDENCIAL",
) -> bytes:
    """Genera un documento PDF con una o más credenciales o stickers para impresión.

    Cumple con el estándar CR-80 (85.60 mm × 53.98 mm) generando una página
    por cada credencial, permitiendo el envío directo a impresoras de tarjetas
    PVC (Zebra, Fargo, Evolis) o térmicas de stickers.

    Args:
        students_data (list[dict[str, Any]]): Lista de diccionarios con datos de alumnos.
        mode (str, optional): 'CREDENCIAL' o 'STICKER'. Defaults to 'CREDENCIAL'.

    Returns:
        bytes: Archivo PDF generado en memoria.
    """
    buffer = io.BytesIO()

    page_width = (CR80_WIDTH_MM if mode == "CREDENCIAL" else STICKER_WIDTH_MM) * mm
    page_height = (CR80_HEIGHT_MM if mode == "CREDENCIAL" else STICKER_HEIGHT_MM) * mm

    c = canvas.Canvas(buffer, pagesize=(page_width, page_height))
    c.setTitle("Credenciales Escolares - Secundaria Mixta 5")
    c.setAuthor("SIGE - Escuela Secundaria Mixta 5")

    for student in students_data:
        # Generamos la imagen rasterizada a alta resolución (300 DPI) para fidelidad
        # de diseño gráfico y renderizamos dentro del canvas vectorial exacto
        png_bytes = generate_credential_png(student, mode=mode)
        img_buf = io.BytesIO(png_bytes)
        img_reader = canvas.ImageReader(img_buf)

        c.drawImage(
            img_reader,
            0,
            0,
            width=page_width,
            height=page_height,
            preserveAspectRatio=True,
        )
        c.showPage()

    c.save()
    return buffer.getvalue()
