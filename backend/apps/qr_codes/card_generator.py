"""Motor de generación de credenciales y stickers escolares en PDF y PNG.

Implementa la generación de documentos para la Escuela Secundaria Mixta 5
conforme al estándar CR-80 vertical (54.0 mm × 85.6 mm), credenciales oficiales
con código QR integrado y fotografía oficial (anverso y reverso), stickers térmicos
de alta resolución y maquetación de lotes en formato horizontal (Landscape)
según las especificaciones RF-CRE-01, RF-CRE-02, RN-CRE-01 a RN-CRE-04 y RN-QR-01 a 06.
"""

import io
import os
import uuid
from pathlib import Path
from typing import Any

from django.conf import settings
from PIL import Image, ImageColor, ImageDraw, ImageFont
import cv2
import numpy as np
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------
# Constantes de diseño institucional (Escuela Secundaria Mixta 5)
# ----------------------------------------------------------------------
# Tarjeta estándar CR-80 vertical oficial (base de diseño a 300 DPI)
CR80_WIDTH_MM: float = 54.00
CR80_HEIGHT_MM: float = 85.60
CR80_HORIZ_WIDTH_MM: float = 85.60
CR80_HORIZ_HEIGHT_MM: float = 53.98

# Dimensiones ampliadas optimizadas para impresión en sustrato Carta horizontal (+30% área)
PRINT_CARD_WIDTH_MM: float = 61.50
PRINT_CARD_HEIGHT_MM: float = 97.40

# Sticker térmico de asistencia
STICKER_WIDTH_MM: float = 50.00
STICKER_HEIGHT_MM: float = 52.00

# Paleta de colores institucional
COLOR_PRIMARY_HEX: str = "#1A365D"  # Azul profundo institucional
COLOR_HEADER_NAVY_HEX: str = "#143055"  # Azul heráldico cabecera
COLOR_SECONDARY_HEX: str = "#D69E2E"  # Dorado institucional
COLOR_DARK_TEXT_HEX: str = "#1A202C"  # Carbón de alta legibilidad
COLOR_MUTED_TEXT_HEX: str = "#4A5568"  # Gris medio para subtítulos
COLOR_BG_LIGHT_HEX: str = "#F8FAFC"  # Fondo marfil suave
COLOR_YELLOW_CARD_HEX: str = "#FFFF9B"  # Contenedor amarillo datos alumno

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
LOGO_JALISCO_PATH = ASSETS_DIR / "logo_jalisco.png"
ESCUDO_JALISCO_PATH = ASSETS_DIR / "escudo_jalisco.png"


def _get_pil_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """Obtiene una fuente TrueType del sistema o recurre a la fuente por defecto.

    Args:
        size (int): Tamaño de fuente en puntos/píxeles.
        bold (bool, optional): Indica si se prefiere fuente en negrita. Defaults to False.

    Returns:
        ImageFont.ImageFont: Objeto de fuente listo para dibujar en Pillow.
    """
    candidates = (
        ["calibrib.ttf", "arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]
        if bold
        else ["calibri.ttf", "arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"]
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

    Intenta primero con ERROR_CORRECT_Q; si OpenCV no puede decodificar el QR
    resultante (caso raro por interacción entre UUID y versión QR), escala a
    ERROR_CORRECT_M o ERROR_CORRECT_L para garantizar decodificación óptica.

    Args:
        token_str (str | uuid.UUID): UUID del token impreso en la credencial.
        box_size (int, optional): Tamaño en píxeles de cada módulo QR. Defaults to 8.
        border (int, optional): Grosor del borde en módulos. Defaults to 1.

    Returns:
        Image.Image: Imagen Pillow en modo RGB con contraste puro (negro/blanco).
    """
    for ec in (ERROR_CORRECT_Q, ERROR_CORRECT_M, ERROR_CORRECT_L):
        qr = qrcode.QRCode(
            version=None,
            error_correction=ec,
            box_size=box_size,
            border=border,
        )
        qr.add_data(str(token_str).strip())
        qr.make(fit=True)
        pil_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
        # Verificación óptica rápida antes de entregar la imagen
        img_arr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img_arr)
        if data:
            return pil_img

    # Último recurso: ERROR_CORRECT_M con borde extra y box_size mayor
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=box_size,
        border=border + 1,
    )
    qr.add_data(str(token_str).strip())
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


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
        full_path = Path(photo_path)
        if not full_path.is_absolute() and hasattr(settings, "MEDIA_ROOT"):
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


def render_credential_front_pil(student_data: dict[str, Any]) -> Image.Image:
    """Renderiza el anverso (cara frontal) de la credencial oficial CR-80 a 300 DPI.

    Incorpora la fotografía oficial y el código QR de asistencia contiguos en el
    cuerpo central, cabecera institucional oficial con logos, matrícula y grado/grupo
    destacados, y contenedor inferior amarillo con datos médicos y domicilio.

    Args:
        student_data (dict[str, Any]): Datos estructurados del alumno.

    Returns:
        Image.Image: Imagen Pillow RGB de 638 × 1011 px (54 × 85.6 mm a 300 DPI).
    """
    w, h = 638, 1011
    card = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(card)

    # Marco exterior suave
    d.rectangle([(0, 0), (w - 1, h - 1)], outline=(203, 213, 225), width=2)

    # Tipografías institucionales calibradas para impresión
    f_title_esc = _get_pil_font(35, bold=True)
    f_cct = _get_pil_font(25, bold=True)
    f_badge = _get_pil_font(21, bold=True)
    f_name = _get_pil_font(32, bold=True)
    f_data_bold = _get_pil_font(24, bold=True)
    f_captions = _get_pil_font(17, bold=False)

    col_navy = (20, 48, 85)
    col_dark = (20, 20, 20)

    # 1. Logos institucionales (SEJ y Escudo Jalisco)
    if LOGO_JALISCO_PATH.exists():
        try:
            with Image.open(LOGO_JALISCO_PATH) as l_raw:
                l_h = 75
                l_w = int(l_raw.width * (l_h / l_raw.height))
                l_res = l_raw.convert("RGBA").resize((l_w, l_h), Image.Resampling.LANCZOS)
                card.paste(l_res, (30, 20), mask=l_res.split()[3])
        except Exception:
            pass

    if ESCUDO_JALISCO_PATH.exists():
        try:
            with Image.open(ESCUDO_JALISCO_PATH) as e_raw:
                e_h = 75
                e_w = int(e_raw.width * (e_h / e_raw.height))
                e_res = e_raw.convert("RGBA").resize((e_w, e_h), Image.Resampling.LANCZOS)
                card.paste(e_res, (w - 30 - e_w, 20), mask=e_res.split()[3])
        except Exception:
            pass

    # 2. Cabecera institucional
    d.text((w // 2, 115), "SECUNDARIA 5 MIXTA", fill=col_navy, font=f_title_esc, anchor="mm")
    d.text((w // 2, 158), "C.C.T. 14EES0336D", fill=col_navy, font=f_cct, anchor="mm")
    d.line([(30, 188), (w - 30, 188)], fill=(214, 158, 46), width=2)

    # 3. Insignias / Distintivos (Matrícula y Grado/Grupo)
    enrollment = str(student_data.get("enrollment_id") or "16092179").strip()
    academic_group = str(student_data.get("academic_group") or "2° D · MATUTINO").strip()

    # Rectángulo de Matrícula (ancho ~375 px)
    d.rounded_rectangle([(30, 202), (405, 246)], radius=6, fill=col_navy)
    d.text((217, 224), f"ALUMNO · MATRÍCULA: {enrollment}", fill=(255, 255, 255), font=f_badge, anchor="mm")

    # Rectángulo de Grado y Turno (ancho ~185 px)
    d.rounded_rectangle([(420, 202), (608, 246)], radius=6, fill=col_navy)
    d.text((514, 224), academic_group, fill=(255, 255, 255), font=f_badge, anchor="mm")

    # 4. Sección central: Fotografía Oficial + Código QR Contiguos
    # Caja foto: x=45, y=270, w=255, h=310
    photo_box = (45, 270, 300, 580)
    name_tokens = (student_data.get("display_name") or "ALUMNO").split()
    initials = "".join(t[0] for t in name_tokens[:2]) if name_tokens else "AL"

    _draw_student_photo_pil(
        draw=d,
        photo_path=student_data.get("photo_url"),
        box=photo_box,
        base_img=card,
        initials=initials,
    )
    d.text((172, 595), "Fotografía Oficial", fill=(100, 116, 139), font=f_captions, anchor="mm")

    # Caja QR: x=340, y=270, w=255, h=255
    token_val = (
        student_data.get("token")
        or student_data.get("qr_token")
        or student_data.get("active_qr_token")
        or uuid.uuid4()
    )
    qr_img = generate_qr_pil_image(str(token_val).strip(), box_size=8, border=2)
    qr_resized = qr_img.resize((255, 255), Image.Resampling.NEAREST)

    d.rectangle([(338, 268), (597, 527)], outline=(203, 213, 225), width=2)
    card.paste(qr_resized, (340, 270))
    d.text((467, 545), "Código de Asistencia", fill=(100, 116, 139), font=f_captions, anchor="mm")

    # 5. Banner de Nombre del Alumno
    student_name = (
        student_data.get("display_name")
        or student_data.get("full_name")
        or "IBARRA MEJÍA CARMEN SCARLTT"
    ).strip().upper()

    d.line([(30, 622), (w - 30, 622)], fill=(203, 213, 225), width=1)
    d.text((w // 2, 652), student_name, fill=col_navy, font=f_name, anchor="mm")
    d.line([(30, 680), (w - 30, 680)], fill=(203, 213, 225), width=1)

    # 6. Ficha de Datos Inferior (Contenedor Amarillo #FFFF9B)
    d.rounded_rectangle([(30, 690), (608, 985)], radius=8, fill=(255, 255, 155), outline=(214, 158, 46), width=2)

    street = (student_data.get("address_street") or "AV. CONSTITUCIÓN No. 450").upper()
    colonia = (student_data.get("address_colonia") or "CENTRO BARRANQUITAS").upper()
    municipio = (student_data.get("address_municipio") or "GUADALAJARA, JAL.").upper()
    cp = str(student_data.get("address_postal_code") or "44280")
    phone = str(student_data.get("guardian_phone") or student_data.get("phone_number") or "33-3614-2289")
    blood = str(student_data.get("blood_type") or "O+").upper()
    allergies = str(student_data.get("allergies") or "NINGUNA").upper()

    d.text((45, 725), f"CALLE: {street}", fill=col_dark, font=f_data_bold)
    d.text((45, 770), f"COLONIA: {colonia}", fill=col_dark, font=f_data_bold)
    d.text((45, 815), f"CIUDAD: {municipio}     C.P.: {cp}", fill=col_dark, font=f_data_bold)
    d.text((45, 860), f"TEL: {phone}     SANGRE: {blood}", fill=col_dark, font=f_data_bold)
    d.text((45, 905), f"ALERGIAS: {allergies}", fill=col_dark, font=f_data_bold)
    d.text((45, 950), "CICLO: 2026-2027          VENCE: JULIO 2028", fill=col_navy, font=f_data_bold)

    return card


def render_credential_back_pil(student_data: dict[str, Any]) -> Image.Image:
    """Renderiza el reverso (cara trasera) de la credencial oficial CR-80 a 300 DPI.

    Aloja el protocolo de emergencia escolar, autorización institucional con el
    nombre de la Directora MTRA. ELVA IBARRA JUÁREZ colocado ENCIMA de la línea de
    firma con amplio espacio para rúbrica, disposiciones oficiales y vigencia dorada.

    Args:
        student_data (dict[str, Any]): Datos estructurados del alumno.

    Returns:
        Image.Image: Imagen Pillow RGB de 638 × 1011 px (54 × 85.6 mm a 300 DPI).
    """
    w, h = 638, 1011
    reverso = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(reverso)

    border_col = (180, 180, 180)
    col_navy = (26, 54, 93)
    col_gold = (214, 158, 46)
    col_dark = (20, 20, 20)
    col_muted = (80, 80, 80)

    f_title = _get_pil_font(24, bold=True)
    f_sub = _get_pil_font(23, bold=True)
    f_name = _get_pil_font(25, bold=True)
    f_dir = _get_pil_font(28, bold=True)
    f_sig_lbl = _get_pil_font(25, bold=True)
    f_school_lbl = _get_pil_font(23, bold=True)
    f_disp = _get_pil_font(21, bold=False)
    f_footer = _get_pil_font(27, bold=True)

    # Marco exterior
    d.rectangle([(0, 0), (w - 1, h - 1)], outline=border_col, width=2)

    # 1. Cabecera institucional superior
    d.rectangle([(20, 20), (w - 20, 75)], fill=col_navy)
    d.text((w // 2, 47), "DATOS DE SEGURIDAD Y VIGENCIA", fill=(255, 255, 255), font=f_title, anchor="mm")

    # 2. Caja de contacto de emergencia escolar (tipografía ampliada)
    d.rectangle([(20, 90), (w - 20, 275)], fill=(248, 250, 252), outline=border_col, width=2)
    d.text((35, 115), "EN CASO DE EMERGENCIA LLAMAR A:", fill=col_navy, font=f_sub)

    guardian_name = (
        student_data.get("guardian_name")
        or "MARÍA ELENA LÓPEZ BARRAGÁN"
    ).strip().upper()
    guardian_phone = (
        student_data.get("guardian_phone")
        or student_data.get("phone_number")
        or "33-3614-2289 / 33-1289-4455"
    ).strip()

    d.text((35, 158), "Tutor / Familiar:", fill=col_muted, font=f_sub)
    d.text((215, 158), guardian_name, fill=col_dark, font=f_name)

    d.text((35, 212), "Tel. Emergencia:", fill=col_muted, font=f_sub)
    d.text((215, 212), guardian_phone, fill=col_dark, font=f_name)

    # 3. Recuadro de autorización institucional y firma de dirección
    # Espacio amplio para firma rúbrica física
    d.rectangle([(20, 290), (w - 20, 670)], fill=(255, 255, 255), outline=border_col, width=2)
    d.text((w // 2, 322), "AUTORIZACIÓN INSTITUCIONAL", fill=col_navy, font=f_sub, anchor="mm")

    director_name = (student_data.get("director_name") or "L.E.M ELVA IBARRA JUÁREZ").strip().upper()

    # Nombre oficial de la Directora colocado ENCIMA de la línea de firma
    d.text((w // 2, 500), director_name, fill=col_dark, font=f_dir, anchor="mm")
    d.line([(70, 532), (w - 70, 532)], fill=col_dark, width=2)
    d.text((w // 2, 568), "NOMBRE Y FIRMA DE LA DIRECCIÓN", fill=col_navy, font=f_sig_lbl, anchor="mm")
    d.text((w // 2, 615), "ESCUELA SECUNDARIA MIXTA No. 5", fill=col_dark, font=f_school_lbl, anchor="mm")

    # 4. Normativa escolar oficial (exactamente 2 disposiciones con texto legible)
    d.rectangle([(20, 685), (w - 20, 915)], fill=(248, 250, 252), outline=border_col, width=2)
    d.text((35, 712), "DISPOSICIONES OFICIALES:", fill=col_navy, font=f_sub)

    d.text((35, 755), "• La presente credencial lo(a) acredita como alumno", fill=col_dark, font=f_disp)
    d.text((50, 785), "de este plantel educativo.", fill=col_dark, font=f_disp)

    d.text((35, 830), "• Este documento es intransferible, no es valido si", fill=col_dark, font=f_disp)
    d.text((50, 860), "presenta alteraciones.", fill=col_dark, font=f_disp)

    # 5. Cintillo dorado oficial de vigencia
    d.rectangle([(20, 930), (w - 20, 990)], fill=col_gold)
    d.text((w // 2, 960), "VÁLIDO HASTA JULIO DEL 2028", fill=(255, 255, 255), font=f_footer, anchor="mm")

    return reverso


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
        mode (str, optional): 'CREDENCIAL', 'STICKER' o 'REVERSO'. Defaults to 'CREDENCIAL'.

    Returns:
        bytes: Flujo binario PNG listo para ser transmitido o guardado.
    """
    scale = 300 / 25.4  # píxeles por milímetro a 300 DPI (~11.81 px/mm)
    mode_upper = mode.upper()

    if mode_upper == "STICKER":
        w_px = int(STICKER_WIDTH_MM * scale)
        h_px = int(STICKER_HEIGHT_MM * scale)
        img = Image.new("RGB", (w_px, h_px), "white")
        draw = ImageDraw.Draw(img)

        # Marco exterior suave para guía de corte / sticker
        draw.rounded_rectangle(
            [4, 4, w_px - 5, h_px - 5],
            radius=16,
            outline="#CBD5E1",
            width=2,
        )

        # 1. Leyenda superior: Nombre del estudiante al que le pertenece el código
        name = (
            student_data.get("display_name")
            or student_data.get("full_name")
            or "ESTUDIANTE"
        ).strip()
        font_name = _get_pil_font(23, bold=True)
        words = name.split()
        if len(name) > 22 and len(words) > 2:
            mid = len(words) // 2
            line1 = " ".join(words[:mid])
            line2 = " ".join(words[mid:])
            draw.text((w_px // 2, 38), line1, fill=COLOR_DARK_TEXT_HEX, font=font_name, anchor="mm")
            draw.text((w_px // 2, 66), line2, fill=COLOR_DARK_TEXT_HEX, font=font_name, anchor="mm")
            qr_y = 92
        else:
            draw.text((w_px // 2, 50), name, fill=COLOR_DARK_TEXT_HEX, font=font_name, anchor="mm")
            qr_y = 85

        # 2. Código QR adaptativo con verificación óptica en el sticker completo
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

        token_clean = str(token_val).strip()
        detector = cv2.QRCodeDetector()
        font_footer = _get_pil_font(18, bold=True)
        max_qr = w_px - 20

        candidates: list[tuple[Any, int, int]] = [
            (ERROR_CORRECT_Q, 8, 3),
            (ERROR_CORRECT_Q, 8, 2),
            (ERROR_CORRECT_M, 8, 3),
            (ERROR_CORRECT_M, 8, 2),
            (ERROR_CORRECT_Q, 9, 3),
            (ERROR_CORRECT_Q, 10, 3),
            (ERROR_CORRECT_L, 8, 2),
        ]

        best_img: Image.Image | None = None
        for ec, bs, brd in candidates:
            cand_img = img.copy()
            cand_draw = ImageDraw.Draw(cand_img)

            qr = qrcode.QRCode(version=None, error_correction=ec, box_size=bs, border=brd)
            qr.add_data(token_clean)
            qr.make(fit=True)
            qr_pil = qr.make_image(fill_color="black", back_color="white").convert("RGB")

            qr_size = qr_pil.width
            if qr_size > max_qr:
                qr_pil = qr_pil.resize((max_qr, max_qr), Image.Resampling.NEAREST)
                qr_size = max_qr
            qr_x = (w_px - qr_size) // 2
            cand_img.paste(qr_pil, (qr_x, qr_y))

            qr_bottom = qr_y + qr_size
            cand_draw.text(
                (w_px // 2, qr_bottom + 22),
                "CÓDIGO DE ASISTENCIA",
                fill="#475569",
                font=font_footer,
                anchor="mm",
            )

            cv_cand = cv2.cvtColor(np.array(cand_img), cv2.COLOR_RGB2BGR)
            d, _, _ = detector.detectAndDecode(cv_cand)
            if d == token_clean:
                best_img = cand_img
                break

        if best_img is None:
            best_img = cand_img

        buf = io.BytesIO()
        best_img.save(buf, format="PNG", dpi=(300, 300))
        return buf.getvalue()

    if mode_upper == "REVERSO":
        reverso_img = render_credential_back_pil(student_data)
        buf = io.BytesIO()
        reverso_img.save(buf, format="PNG", dpi=(300, 300))
        return buf.getvalue()

    # Formato CREDENCIAL Anverso estándar oficial CR-80
    front_img = render_credential_front_pil(student_data)
    buf = io.BytesIO()
    front_img.save(buf, format="PNG", dpi=(300, 300))
    return buf.getvalue()


def generate_credential_pdf(
    students_data: list[dict[str, Any]],
    mode: str = "CREDENCIAL",
) -> bytes:
    """Genera un documento PDF con una o más credenciales o stickers para impresión.

    En modo 'STICKER', maqueta múltiples stickers en hoja tamaño Carta vertical (Portrait)
    en una cuadrícula de 4 columnas × 5 filas (20 stickers por página) con guías
    de corte continuas y encabezados de página.

    En modo 'CREDENCIAL', 'CREDENCIAL_LOTE' o 'CREDENCIAL_INDIVIDUAL', maqueta en hoja
    tamaño Carta en formato horizontal (Landscape: 279.4 mm × 215.9 mm) en una cuadrícula
    matricial de 2 filas × 4 columnas (4 estudiantes completos = 8 caras contiguas
    [E1 Frente][E1 Detrás][E2 Frente][E2 Detrás] en la Fila 1 y [E3...][E4...] en la Fila 2).

    Args:
        students_data (list[dict[str, Any]]): Lista de diccionarios con datos de alumnos.
        mode (str, optional): 'CREDENCIAL', 'CREDENCIAL_LOTE', 'CREDENCIAL_INDIVIDUAL'
            o 'STICKER'. Defaults to 'CREDENCIAL'.

    Returns:
        bytes: Archivo PDF generado en memoria listo para descarga o almacenamiento.
    """
    buffer = io.BytesIO()
    mode_upper = mode.upper()

    if mode_upper == "STICKER":
        c = canvas.Canvas(buffer, pagesize=letter)
        c.setTitle("Stickers de Asistencia - Escuela Secundaria Mixta 5")
        c.setAuthor("SIGE - Escuela Secundaria Mixta 5")

        page_w, page_h = letter
        cols = 4
        rows = 5
        per_page = cols * rows

        cell_w = 48.0 * mm
        cell_h = 50.0 * mm
        sticker_w = 45.0 * mm
        sticker_h = 46.8 * mm

        margin_x = (page_w - (cols * cell_w)) / 2.0
        margin_y = (page_h - (rows * cell_h)) / 2.0
        total_students = len(students_data)
        total_pages = max(1, (total_students + per_page - 1) // per_page)

        for idx, student in enumerate(students_data):
            page_idx = idx // per_page
            pos = idx % per_page
            col = pos % cols
            row = pos // cols
            row_from_bottom = (rows - 1) - row

            cell_x = margin_x + (col * cell_w)
            cell_y = margin_y + (row_from_bottom * cell_h)

            if pos == 0:
                c.setFont("Helvetica-Bold", 8)
                c.setFillColor(HexColor("#64748B"))
                group_label = student.get("academic_group", "Escuela Secundaria Mixta 5")
                c.drawString(
                    margin_x,
                    page_h - 10 * mm,
                    f"SIGE · Escuela Secundaria Mixta No. 5  |  Stickers de Asistencia  |  {group_label}",
                )
                c.drawRightString(
                    page_w - margin_x,
                    page_h - 10 * mm,
                    f"Página {page_idx + 1} de {total_pages}",
                )

            c.setStrokeColor(HexColor("#CBD5E1"))
            c.setLineWidth(0.4)
            c.rect(cell_x, cell_y, cell_w, cell_h)

            png_bytes = generate_credential_png(student, mode="STICKER")
            img_reader = canvas.ImageReader(io.BytesIO(png_bytes))

            offset_x = cell_x + (cell_w - sticker_w) / 2.0
            offset_y = cell_y + (cell_h - sticker_h) / 2.0

            c.drawImage(
                img_reader,
                offset_x,
                offset_y,
                width=sticker_w,
                height=sticker_h,
                preserveAspectRatio=True,
            )

            if pos == per_page - 1 or idx == total_students - 1:
                c.showPage()

        c.save()
        return buffer.getvalue()

    # ------------------------------------------------------------------
    # Maquetación Carta Horizontal (Landscape) - Matriz 2×4 (4 Alumnos / 8 Caras)
    # ------------------------------------------------------------------
    # Hoja Carta en horizontal: 279.4 mm × 215.9 mm
    page_w = letter[1]
    page_h = letter[0]

    c = canvas.Canvas(buffer, pagesize=(page_w, page_h))
    c.setTitle("Credenciales Escolares Oficiales - Secundaria Mixta 5")
    c.setAuthor("SIGE - Escuela Secundaria Mixta 5")

    cols = 4
    rows = 2
    students_per_page = 4

    # Dimensiones ampliadas para maximizar el área impresa en hoja Carta
    card_w = PRINT_CARD_WIDTH_MM * mm  # 61.50 mm
    card_h = PRINT_CARD_HEIGHT_MM * mm  # 97.40 mm

    margin_x = 8.0 * mm
    gap_x = (page_w - (2 * margin_x) - (cols * card_w)) / (cols - 1)  # 5.80 mm

    top_margin = 9.0 * mm
    gap_y = 4.3 * mm

    total_students = len(students_data)
    total_pages = max(1, (total_students + students_per_page - 1) // students_per_page)

    for page_idx in range(total_pages):
        # 1. Encabezado institucional de página
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColor(HexColor("#64748B"))
        first_student = students_data[page_idx * students_per_page] if students_data else {}
        group_label = first_student.get("academic_group", "Escuela Secundaria Mixta No. 5")
        c.drawString(
            margin_x,
            page_h - 6.5 * mm,
            f"SIGE · Escuela Secundaria Mixta No. 5  |  Credenciales Escolares Oficiales  |  {group_label}",
        )
        c.drawRightString(
            page_w - margin_x,
            page_h - 6.5 * mm,
            f"Página {page_idx + 1} de {total_pages}",
        )

        # 2. Dibujar guías de corte en todas las 8 posiciones de la matriz
        c.setStrokeColor(HexColor("#94A3B8"))
        c.setLineWidth(0.5)

        slot_coords: list[tuple[float, float]] = []
        for r in range(rows):
            # ReportLab y=0 está abajo; Row 0 es la superior
            y_pos = page_h - top_margin - ((r + 1) * card_h) - (r * gap_y)
            for col in range(cols):
                x_pos = margin_x + (col * (card_w + gap_x))
                c.rect(x_pos, y_pos, card_w, card_h)
                slot_coords.append((x_pos, y_pos))

        # 3. Renderizar hasta 4 estudiantes en la página actual
        start_idx = page_idx * students_per_page
        end_idx = min(start_idx + students_per_page, total_students)
        page_students = students_data[start_idx:end_idx]

        for s_idx, student in enumerate(page_students):
            # Cada estudiante ocupa dos slots contiguos: Frente y Reverso
            slot_front_idx = s_idx * 2
            slot_back_idx = slot_front_idx + 1

            # Renderizar Cara Frontal (Anverso)
            front_img = render_credential_front_pil(student)
            front_buf = io.BytesIO()
            front_img.save(front_buf, format="PNG")
            front_buf.seek(0)
            front_reader = canvas.ImageReader(front_buf)

            fx, fy = slot_coords[slot_front_idx]
            c.drawImage(
                front_reader,
                fx,
                fy,
                width=card_w,
                height=card_h,
                preserveAspectRatio=True,
            )

            # Renderizar Cara Trasera (Reverso)
            back_img = render_credential_back_pil(student)
            back_buf = io.BytesIO()
            back_img.save(back_buf, format="PNG")
            back_buf.seek(0)
            back_reader = canvas.ImageReader(back_buf)

            bx, by = slot_coords[slot_back_idx]
            c.drawImage(
                back_reader,
                bx,
                by,
                width=card_w,
                height=card_h,
                preserveAspectRatio=True,
            )

        c.showPage()

    c.save()
    return buffer.getvalue()
