"""Validadores del módulo de estudiantes y tutores.

Contiene las funciones de validación para CURP (RENAPO), matrícula
institucional, teléfono (10 dígitos, México), nombre de persona
(RN-TRX-08/09) y código postal.
"""

import re

from django.core.exceptions import ValidationError


# ------------------------------------------------------------------
# Expresiones regulares compiladas
# ------------------------------------------------------------------

CURP_REGEX = re.compile(r"^[A-Z]{4}\d{6}[HM][A-Z]{5}[A-Z0-9]\d$")
PHONE_REGEX = re.compile(r"^\d{10}$")
ENROLLMENT_REGEX = re.compile(r"^[A-Za-z0-9\-_]{4,20}$")
POSTAL_CODE_REGEX = re.compile(r"^\d{5}$")

# Caracteres permitidos en nombres (RN-TRX-09): letras (con acentos),
# espacios, apóstrofos, guiones y puntos.
NAME_ALLOWED_REGEX = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s'\-\.]+$")

# Valores sustitutos prohibidos en campos de nombre (RN-TRX-09).
FORBIDDEN_NAME_VALUES = frozenset({
    "n/a", "na", "no aplica", "no disponible", "nd", "ninguno",
    "desconocido", "sin dato", ".", "-", "--", "...", "x", "xx", "xxx",
})


# ------------------------------------------------------------------
# Validadores
# ------------------------------------------------------------------

def validate_curp(value: str) -> None:
    """Valida que la CURP cumpla con el estándar oficial de RENAPO.

    Estructura de 18 caracteres:
    - 4 letras (iniciales de nombres y apellidos)
    - 6 dígitos (AAMMDD)
    - 1 letra de sexo (H o M)
    - 5 letras (entidad + consonantes internas)
    - 1 carácter alfanumérico (diferenciador de siglo)
    - 1 dígito verificador

    Args:
        value: Cadena con la CURP a validar.

    Raises:
        ValidationError: Si la CURP está vacía, tiene longitud
            incorrecta o no cumple la estructura.
    """
    if not value:
        return  # CURP es opcional según RF-EST-01 v2.1
    clean_val = value.strip().upper()
    if len(clean_val) != 18:
        raise ValidationError(
            f"La CURP debe tener exactamente 18 caracteres "
            f"(longitud actual: {len(clean_val)})."
        )
    if not CURP_REGEX.match(clean_val):
        raise ValidationError(
            f"La CURP '{clean_val}' no cumple con la estructura "
            f"oficial mexicana de la RENAPO."
        )


def validate_phone_number(value: str) -> None:
    """Valida un número telefónico celular (10 dígitos, formato México).

    Args:
        value: Cadena con el número telefónico.

    Raises:
        ValidationError: Si el número no contiene exactamente 10 dígitos.
    """
    if not value:
        return  # Teléfono es opcional en tutor (RN-EST-11)
    clean_val = re.sub(r"[\s\-\(\)]", "", value)
    if not PHONE_REGEX.match(clean_val):
        raise ValidationError(
            f"El número telefónico debe contener exactamente "
            f"10 dígitos numéricos (recibido: '{value}')."
        )


def validate_enrollment_id(value: str) -> None:
    """Valida la matrícula o código de estudiante escolar (RN-EST-02).

    Args:
        value: Cadena con la matrícula.

    Raises:
        ValidationError: Si está vacía o contiene caracteres inválidos.
    """
    if not value:
        raise ValidationError("La matrícula institucional es obligatoria.")
    clean_val = value.strip()
    if not ENROLLMENT_REGEX.match(clean_val):
        raise ValidationError(
            f"La matrícula '{value}' contiene caracteres inválidos. "
            f"Solo se permiten letras, números, guiones y guiones bajos "
            f"(4 a 20 caracteres)."
        )


def validate_person_name(value: str, field_label: str = "Nombre") -> None:
    """Valida un campo de nombre de persona (RN-TRX-08 / RN-TRX-09).

    Verifica:
    * Longitud entre 2 y 60 caracteres.
    * Solo caracteres permitidos (letras con acentos, espacios,
      apóstrofos, guiones, puntos).
    * Que no sea un valor sustituto prohibido.

    Args:
        value: Valor del campo de nombre.
        field_label: Etiqueta para mensajes de error.

    Raises:
        ValidationError: Si el valor no cumple las reglas.
    """
    if not value:
        return
    stripped = value.strip()
    if len(stripped) < 2 or len(stripped) > 60:
        raise ValidationError(
            f"{field_label} debe tener entre 2 y 60 caracteres "
            f"(longitud actual: {len(stripped)})."
        )
    if not NAME_ALLOWED_REGEX.match(stripped):
        raise ValidationError(
            f"{field_label} contiene caracteres no permitidos. "
            f"Solo se permiten letras (con acentos), espacios, "
            f"apóstrofos, guiones y puntos."
        )
    if stripped.lower() in FORBIDDEN_NAME_VALUES:
        raise ValidationError(
            f"{field_label} no puede ser un valor sustituto "
            f"como '{stripped}'."
        )


def validate_postal_code(value: str) -> None:
    """Valida un código postal mexicano (5 dígitos).

    Args:
        value: Cadena con el código postal.

    Raises:
        ValidationError: Si no contiene exactamente 5 dígitos.
    """
    if not value:
        return
    if not POSTAL_CODE_REGEX.match(value.strip()):
        raise ValidationError(
            f"El código postal debe contener exactamente 5 dígitos "
            f"(recibido: '{value}')."
        )
