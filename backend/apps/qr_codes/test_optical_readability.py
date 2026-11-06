"""Batería de pruebas de legibilidad óptica y decodificación para el motor QR (WBS 3.12).

Responsable: Miguel (@migolitofirmaditocmd)
Criterios de Aceptación:
    - KPI-02: Lectura exitosa a diferentes distancias (10-30 cm) y condiciones variables
      de iluminación (sol directo, penumbra, bajo contraste, ruido de sensor).
    - KPI-03: Tiempo de decodificación y resolución menor a 500 ms.
    - Resistencia física al desgaste mediante corrección de error Reed-Solomon (M y Q).
"""

import io
import time
import uuid
from typing import Any

import cv2
import numpy as np
import pytest
from PIL import Image

from apps.qr_codes.card_generator import generate_qr_pil_image
from apps.qr_codes.crypto import (
    calculate_token_hmac,
    generate_qr_image_bytes,
    verify_token_hmac,
)


def _pil_to_cv2(pil_img: Image.Image) -> np.ndarray:
    """Convierte una imagen de PIL en formato RGB o L a un arreglo BGR de OpenCV.

    Args:
        pil_img (Image.Image): Imagen original de PIL.

    Returns:
        np.ndarray: Matriz de imagen en formato BGR para OpenCV.
    """
    rgb_img = pil_img.convert("RGB")
    return cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2BGR)


def _simulate_distance(cv_img: np.ndarray, distance_cm: int) -> np.ndarray:
    """Simula la resolución angular proyectada en la cámara según la distancia física.

    A distancias mayores (30 cm), el código QR proyecta menos píxeles sobre el
    sensor que a distancias cortas (10 cm).

    Args:
        cv_img (np.ndarray): Imagen original del código QR.
        distance_cm (int): Distancia física en centímetros (10, 20 o 30 cm).

    Returns:
        np.ndarray: Imagen redimensionada simulando la distancia óptica.
    """
    scale_map = {
        10: 450,  # ~10 cm: alta resolución (~450x450 px)
        20: 280,  # ~20 cm: distancia estándar de mano (~280x280 px)
        30: 160,  # ~30 cm: distancia límite recomendada (~160x160 px)
    }
    target_dim = scale_map.get(distance_cm, 280)
    return cv2.resize(cv_img, (target_dim, target_dim), interpolation=cv2.INTER_AREA)


def _simulate_lighting(cv_img: np.ndarray, condition: str) -> np.ndarray:
    """Aplica transformaciones de luminosidad, contraste y ruido de sensor.

    Args:
        cv_img (np.ndarray): Imagen del código QR.
        condition (str): Condición lumínica ('normal', 'sunlight', 'dim_light',
            'low_contrast', 'sensor_noise', 'motion_blur').

    Returns:
        np.ndarray: Imagen procesada bajo la condición óptica simulada.
    """
    if condition == "normal":
        return cv_img.copy()

    if condition == "sunlight":
        # Luz solar directa: sobreexposición, incremento de brillo y pérdida de contraste
        # g(x) = alpha * f(x) + beta
        bright = cv2.convertScaleAbs(cv_img, alpha=0.9, beta=50)
        return bright

    if condition == "dim_light":
        # Penumbra / baja iluminación: turno vespertino o interiores poco iluminados
        dim = cv2.convertScaleAbs(cv_img, alpha=0.6, beta=-30)
        return dim

    if condition == "low_contrast":
        # Pérdida de contraste óptico (pantallas desgastadas o fotocopias tenues)
        low_c = cv2.convertScaleAbs(cv_img, alpha=0.5, beta=60)
        return low_c

    if condition == "sensor_noise":
        # Ruido de sensor ISO alto en cámaras móviles de gama económica
        noise = np.random.normal(0, 15, cv_img.shape).astype(np.float32)
        noisy = np.clip(cv_img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
        return noisy

    if condition == "motion_blur":
        # Desenfoque leve por movimiento de la mano al presentar la credencial
        kernel = np.ones((3, 3), np.float32) / 9.0
        return cv2.filter2D(cv_img, -1, kernel)

    return cv_img.copy()


def _simulate_wear_and_tear(cv_img: np.ndarray, damage_type: str = "scratch") -> np.ndarray:
    """Simula raspadura física, rayón o mancha superficial en la credencial escolar.

    Args:
        cv_img (np.ndarray): Imagen del código QR.
        damage_type (str, optional): Tipo de daño simulado ('scratch' o 'smudge').
            Defaults to 'scratch'.

    Returns:
        np.ndarray: Imagen con desgaste físico simulado sin alterar los patrones buscadores.
    """
    damaged = cv_img.copy()
    h, w = damaged.shape[:2]

    if damage_type == "scratch":
        # Rayón físico simulado (ej. llave o desgaste en mochila)
        start_pt = (int(w * 0.25), int(h * 0.55))
        end_pt = (int(w * 0.75), int(h * 0.55))
        cv2.line(damaged, start_pt, end_pt, (60, 60, 60), thickness=3)
    elif damage_type == "smudge":
        # Mancha superficial o huella sucia en área de datos
        center = (int(w * 0.5), int(h * 0.6))
        radius = int(w * 0.04)
        cv2.circle(damaged, center, radius, (50, 50, 50), thickness=-1)

    return damaged


class TestOpticalReadabilityAndLatency:
    """Batería técnica de legibilidad óptica sobre el motor QR (WBS 3.12, Miguel)."""

    @pytest.fixture(autouse=True)
    def setup_qr_engine(self) -> None:
        """Inicializa el detector de visión por computadora y tokens de prueba."""
        self.detector = cv2.QRCodeDetector()
        self.sample_token = uuid.uuid4()
        self.signature = calculate_token_hmac(self.sample_token)

    def test_readability_at_distances_10_20_30_cm(self) -> None:
        """Verifica la decodificación óptica a 10 cm, 20 cm y 30 cm (KPI-02, KPI-03).

        Comprueba que a cada distancia:
        1. El detector óptico identifique el código QR sin errores.
        2. El payload decodificado coincida exactamente con el UUIDv4 emitido.
        3. El tiempo de decodificación sea estrictamente menor a 500 ms (KPI-03).
        """
        png_bytes = generate_qr_image_bytes(self.sample_token, box_size=10, border=2)
        pil_img = Image.open(io.BytesIO(png_bytes))
        base_cv = _pil_to_cv2(pil_img)

        distances = [10, 20, 30]
        for dist in distances:
            scaled_img = _simulate_distance(base_cv, dist)

            start_t = time.perf_counter()
            decoded_text, points, _ = self.detector.detectAndDecode(scaled_img)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0

            # Verificación de legibilidad (KPI-02)
            assert points is not None, f"No se detectaron vértices del QR a {dist} cm."
            assert decoded_text == str(self.sample_token), (
                f"Payload incorrecto a {dist} cm: esperado {self.sample_token}, obtenido {decoded_text}"
            )

            # Verificación de latencia (KPI-03 < 500 ms)
            assert elapsed_ms < 500.0, (
                f"Tiempo de decodificación excesivo a {dist} cm: {elapsed_ms:.2f} ms (límite 500 ms)"
            )

    def test_readability_under_variable_lighting_conditions(self) -> None:
        """Verifica la lectura bajo condiciones adversas de iluminación (KPI-02).

        Evalúa el motor óptico ante:
        - Luz solar directa (sobreexposición de credencial a pleno sol, CT-11).
        - Penumbra / luz tenue (turno vespertino en invierno).
        - Bajo contraste (credencial con desgaste superficial).
        - Ruido de sensor (cámara económica en dispositivo móvil de prefectura).
        - Desenfoque por movimiento leve (motion blur al deslizar credencial).
        """
        png_bytes = generate_qr_image_bytes(self.sample_token, box_size=10, border=3)
        pil_img = Image.open(io.BytesIO(png_bytes))
        base_cv = _pil_to_cv2(pil_img)

        conditions = ["normal", "sunlight", "dim_light", "low_contrast", "sensor_noise", "motion_blur"]

        for condition in conditions:
            perturbed_img = _simulate_lighting(base_cv, condition)

            start_t = time.perf_counter()
            decoded_text, points, _ = self.detector.detectAndDecode(perturbed_img)
            elapsed_ms = (time.perf_counter() - start_t) * 1000.0

            assert points is not None, f"Fallo de detección óptica bajo condición: {condition}"
            assert decoded_text == str(self.sample_token), (
                f"Decodificación corrupta bajo {condition}: obtenido '{decoded_text}'"
            )
            assert elapsed_ms < 500.0, (
                f"Latencia excedida bajo {condition}: {elapsed_ms:.2f} ms"
            )

    def test_reed_solomon_physical_wear_resistance(self) -> None:
        """Verifica la tolerancia al daño físico mediante corrección de errores M y Q.

        - Nivel M (15% recuperación): tolera raspaduras de uso cotidiano.
        - Nivel Q (25% recuperación): tolerancia alta para uso rudo escolar.
        """
        for high_tolerance in (False, True):
            png_bytes = generate_qr_image_bytes(
                self.sample_token, box_size=12, border=3, high_tolerance=high_tolerance
            )
            pil_img = Image.open(io.BytesIO(png_bytes))
            base_cv = _pil_to_cv2(pil_img)

            for damage in ("scratch", "smudge"):
                damaged_cv = _simulate_wear_and_tear(base_cv, damage_type=damage)

                decoded_text, points, _ = self.detector.detectAndDecode(damaged_cv)
                assert points is not None, (
                    f"Fallo de detección en QR con daño '{damage}' (high_tolerance={high_tolerance})."
                )
                assert decoded_text == str(self.sample_token), (
                    f"Error en recuperación Reed-Solomon con daño '{damage}' (high_tolerance={high_tolerance})."
                )

    def test_end_to_end_resolution_pipeline_latency(self) -> None:
        """Verifica el tiempo total de decodificación óptica + validación HMAC (KPI-03).

        El pipeline completo incluye:
        1. Decodificación óptica de la imagen del sensor por visión computacional.
        2. Extracción y parseo del UUIDv4.
        3. Comprobación criptográfica de integridad HMAC-SHA256 en tiempo constante.

        El tiempo combinado debe ser significativamente inferior a 500 ms (típicamente < 50 ms).
        """
        png_bytes = generate_qr_image_bytes(self.sample_token, box_size=10, border=2)
        pil_img = Image.open(io.BytesIO(png_bytes))
        cv_img = _pil_to_cv2(pil_img)

        start_pipeline = time.perf_counter()

        # 1. Decodificación óptica
        decoded_text, points, _ = self.detector.detectAndDecode(cv_img)
        assert points is not None
        assert decoded_text != ""

        # 2. Parseo de UUIDv4
        parsed_uuid = uuid.UUID(decoded_text)

        # 3. Validación de firma HMAC-SHA256
        is_valid = verify_token_hmac(parsed_uuid, self.signature)
        assert is_valid is True

        total_elapsed_ms = (time.perf_counter() - start_pipeline) * 1000.0

        # KPI-03: < 500 ms
        assert total_elapsed_ms < 500.0, (
            f"Latencia total del pipeline excedió el KPI-03: {total_elapsed_ms:.2f} ms"
        )
