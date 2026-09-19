import hmac
import hashlib
import io
import uuid
from typing import Tuple, Optional
from django.conf import settings
from django.db import transaction
from django.utils import timezone
import qrcode
from qrcode.constants import ERROR_CORRECT_M, ERROR_CORRECT_Q

from .models import QRCodeToken

# Prefijo institucional para la sal de derivación
TOKEN_DOMAIN_SALT = "SIGE-SEC5-MIXTAPREFECTURA"

def calculate_token_hmac(token_val: uuid.UUID | str, secret_key: Optional[str] = None) -> str:
    """
    Calcula la firma digital HMAC-SHA256 para un UUIDv4 de token QR.
    Garantiza que nadie pueda falsificar tokens válidos sin la clave secreta institucional.
    """
    key = (secret_key or settings.SECRET_KEY).encode('utf-8')
    message = f"{TOKEN_DOMAIN_SALT}:{str(token_val)}".encode('utf-8')
    return hmac.new(key, message, hashlib.sha256).hexdigest()

def verify_token_hmac(token_val: uuid.UUID | str, signature: str, secret_key: Optional[str] = None) -> bool:
    """
    Verifica la autenticidad de la firma HMAC utilizando comparación de tiempo constante
    para mitigar vulnerabilidades de canal lateral (timing attacks).
    """
    if not signature or not token_val:
        return False
    expected = calculate_token_hmac(token_val, secret_key)
    return hmac.compare_digest(expected, signature)

@transaction.atomic
def issue_qr_token_for_student(student, reason: str = "Emisión institucional") -> QRCodeToken:
    """
    Emite un nuevo código QR para el estudiante de manera atómica:
    1. Revoca cualquier token activo previo marcándolo como 'REVOKED'.
    2. Genera un nuevo UUIDv4 criptográfico.
    3. Calcula y asocia su firma HMAC-SHA256.
    4. Persiste el registro garantizando la restricción de unicidad activa.
    """
    # Revocar tokens activos previos
    active_tokens = QRCodeToken.objects.select_for_update().filter(
        student=student,
        status=QRCodeToken.Status.ACTIVE
    )
    for old_token in active_tokens:
        old_token.status = QRCodeToken.Status.REVOKED
        old_token.revoked_at = timezone.now()
        old_token.revocation_reason = f"Reemplazado por nueva emisión: {reason}"
        old_token.save(update_fields=['status', 'revoked_at', 'revocation_reason', 'updated_at'])

    # Crear nuevo token
    new_uuid = uuid.uuid4()
    signature = calculate_token_hmac(new_uuid)

    token_instance = QRCodeToken.objects.create(
        token=new_uuid,
        student=student,
        status=QRCodeToken.Status.ACTIVE,
        hmac_signature=signature,
        issued_at=timezone.now()
    )

    return token_instance

def generate_qr_image_bytes(
    token_val: uuid.UUID | str,
    box_size: int = 10,
    border: int = 2,
    high_tolerance: bool = False
) -> bytes:
    """
    Renderiza el código QR en memoria en formato PNG.
    - Utiliza corrección de errores M (15%) o Q (25% en high_tolerance)
      para soportar raspaduras, suciedad o desgaste físico en credenciales escolares.
    - Retorna el flujo de bytes de la imagen PNG optimizada.
    """
    error_correction = ERROR_CORRECT_Q if high_tolerance else ERROR_CORRECT_M
    
    qr = qrcode.QRCode(
        version=None,  # Ajuste automático de versión según longitud
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    # Codificamos el UUID en formato string estándar canónico
    qr.add_data(str(token_val))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
