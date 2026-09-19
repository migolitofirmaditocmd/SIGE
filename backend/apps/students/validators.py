import re
from django.core.exceptions import ValidationError

CURP_REGEX = re.compile(r'^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$')
PHONE_REGEX = re.compile(r'^\d{10}$')
ENROLLMENT_REGEX = re.compile(r'^[A-Za-z0-9\-_]{4,20}$')

def validate_curp(value: str):
    """
    Valida que la CURP cumpla con el estándar oficial de 18 caracteres de la RENAPO:
    - 4 letras (iniciales de nombres y apellidos)
    - 6 dígitos (año, mes, día de nacimiento: AAMMDD)
    - 1 letra de sexo (H o M)
    - 5 letras (entidad federativa de nacimiento y consonantes internas)
    - 1 caracter alfanumérico diferenciador de siglo
    - 1 dígito verificador
    """
    if not value:
        raise ValidationError("La CURP no puede estar vacía.")
    
    clean_val = value.strip().upper()
    if len(clean_val) != 18:
        raise ValidationError(f"La CURP debe tener exactamente 18 caracteres (longitud actual: {len(clean_val)}).")
    
    if not CURP_REGEX.match(clean_val):
        raise ValidationError(
            f"La CURP '{clean_val}' no cumple con la estructura oficial mexicana de la RENAPO."
        )

def validate_phone_number(value: str):
    """
    Valida un número telefónico celular a 10 dígitos numéricos (formato nacional mexicano).
    """
    if not value:
        raise ValidationError("El número telefónico no puede estar vacío.")
    
    clean_val = re.sub(r'[\s\-\(\)]', '', value)
    if not PHONE_REGEX.match(clean_val):
        raise ValidationError(
            f"El número telefónico debe contener exactamente 10 dígitos numéricos (recibido: '{value}')."
        )

def validate_enrollment_id(value: str):
    """
    Valida la matrícula o código de estudiante escolar.
    """
    if not value:
        raise ValidationError("La matrícula institucional es obligatoria.")
    clean_val = value.strip()
    if not ENROLLMENT_REGEX.match(clean_val):
        raise ValidationError(
            f"La matrícula '{value}' contiene caracteres inválidos. Solo se permiten letras, números, guiones y guiones bajos (4 a 20 caracteres)."
        )
