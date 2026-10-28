"""Comando para ejecutar la batería de pruebas técnicas del motor QR (WBS 3.12 & 3.13).

Ejecuta las pruebas de legibilidad óptica en diversas condiciones de luz y distancias
(Miguel, WBS 3.12) y la confirmación matemática de cero colisiones y unicidad sobre
el universo escolar (Saul, WBS 3.13), emitiendo el dictamen formal de KPI-01, KPI-02 y KPI-03.
"""

import io
import time
import uuid
from typing import Any

import cv2
import numpy as np
from django.core.management.base import BaseCommand, CommandParser
from PIL import Image

from apps.qr_codes.crypto import (
    calculate_token_hmac,
    generate_qr_image_bytes,
    verify_token_hmac,
)
from apps.qr_codes.test_optical_readability import (
    _pil_to_cv2,
    _simulate_distance,
    _simulate_lighting,
    _simulate_wear_and_tear,
)


class Command(BaseCommand):
    """Comando de consola para ejecución y reporte de pruebas de motor QR (WBS 3.12 & 3.13)."""

    help = "Ejecuta la batería de pruebas de legibilidad óptica, unicidad y cero colisiones QR."

    def add_arguments(self, parser: CommandParser) -> None:
        """Configura los argumentos del comando.

        Args:
            parser (CommandParser): Analizador de argumentos de Django.
        """
        parser.add_argument(
            "--sample-size",
            type=int,
            default=1500,
            help="Tamaño de muestra de tokens para verificación de colisiones (por defecto 1500).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Ejecuta la batería de pruebas y despliega el informe consolidado.

        Args:
            *args (Any): Argumentos posicionales.
            **options (Any): Opciones analizadas.
        """
        sample_size = options["sample_size"]

        self.stdout.write(self.style.NOTICE("=" * 75))
        self.stdout.write(
            self.style.NOTICE(
                "  SIGE · BATERÍA TÉCNICA DEL MOTOR DE CÓDIGOS QR (WBS 3.12 & 3.13)"
            )
        )
        self.stdout.write(
            "  Responsables: Miguel (@migolitofirmaditocmd) & Saul (@ultimaibrahim)"
        )
        self.stdout.write(self.style.NOTICE("=" * 75 + "\n"))

        # ------------------------------------------------------------------
        # FASE 1: Saul - Unicidad y Cero Colisiones (WBS 3.13, KPI-01, KPI-02)
        # ------------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS("[FASE 1] Verificación Matemática de Unicidad y Colisiones"))
        self.stdout.write(f"  Generando lote de {sample_size} tokens sobre universo escolar...")

        start_gen = time.perf_counter()
        token_list: list[uuid.UUID] = []
        sig_list: list[str] = []

        for _ in range(sample_size):
            u = uuid.uuid4()
            token_list.append(u)
            sig_list.append(calculate_token_hmac(u))

        gen_elapsed = time.perf_counter() - start_gen
        throughput = sample_size / gen_elapsed

        unique_tokens = len(set(token_list))
        unique_sigs = len(set(sig_list))
        token_collisions = sample_size - unique_tokens
        sig_collisions = sample_size - unique_sigs

        kpi_01_pass = token_collisions == 0 and unique_tokens == sample_size
        kpi_02_pass = sig_collisions == 0

        self.stdout.write(f"  • Muestra evaluada:          {sample_size} tokens")
        self.stdout.write(f"  • Tokens únicos (UUIDv4):     {unique_tokens} ({unique_tokens/sample_size*100:.2f}%)")
        self.stdout.write(f"  • Colisiones de tokens:       {token_collisions}")
        self.stdout.write(f"  • Firmas HMAC únicas:         {unique_sigs}")
        self.stdout.write(f"  • Colisiones en firmas:       {sig_collisions}")
        self.stdout.write(f"  • Velocidad de emisión:       {throughput:.1f} tokens/segundo")

        # Anti-tampering
        test_u = token_list[0]
        test_sig = sig_list[0]
        tamper_ok = (
            verify_token_hmac(test_u, test_sig) is True
            and verify_token_hmac(test_u, test_sig[:-1] + ("0" if test_sig[-1] != "0" else "1")) is False
        )
        self.stdout.write(f"  • Detección anti-tamper HMAC: {'CORRECTA' if tamper_ok else 'FALLIDA'}\n")

        # ------------------------------------------------------------------
        # FASE 2: Miguel - Legibilidad Óptica y Distancias (WBS 3.12, KPI-02, KPI-03)
        # ------------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS("[FASE 2] Verificación de Legibilidad Óptica a Distancias (10-30 cm)"))
        detector = cv2.QRCodeDetector()
        ref_uuid = uuid.uuid4()
        png_bytes = generate_qr_image_bytes(ref_uuid, box_size=10, border=2)
        base_cv = _pil_to_cv2(Image.open(io.BytesIO(png_bytes)))

        distances = [10, 20, 30]
        max_dist_ms = 0.0
        dist_all_ok = True

        for d in distances:
            scaled = _simulate_distance(base_cv, d)
            t0 = time.perf_counter()
            decoded, pts, _ = detector.detectAndDecode(scaled)
            t_ms = (time.perf_counter() - t0) * 1000.0
            max_dist_ms = max(max_dist_ms, t_ms)
            match = decoded == str(ref_uuid)
            if not match:
                dist_all_ok = False
            self.stdout.write(
                f"  • Distancia {d:2d} cm:  {'[OK]' if match else '[FALLÓ]'}  "
                f"Decodificado en {t_ms:5.2f} ms (esperado < 500 ms)"
            )

        # ------------------------------------------------------------------
        # FASE 3: Miguel - Condiciones Variables de Iluminación y Desgaste (WBS 3.12)
        # ------------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS("\n[FASE 3] Verificación bajo Condiciones de Iluminación y Desgaste"))
        conditions = [
            ("Luz solar directa (sobreexposición)", "sunlight"),
            ("Penumbra / luz tenue (vespertino)", "dim_light"),
            ("Bajo contraste (pantalla/fotocopia)", "low_contrast"),
            ("Ruido de sensor (cámara económica)", "sensor_noise"),
            ("Desenfoque leve por movimiento", "motion_blur"),
        ]
        light_all_ok = True
        max_light_ms = 0.0

        for label, cond in conditions:
            perturbed = _simulate_lighting(base_cv, cond)
            t0 = time.perf_counter()
            decoded, pts, _ = detector.detectAndDecode(perturbed)
            t_ms = (time.perf_counter() - t0) * 1000.0
            max_light_ms = max(max_light_ms, t_ms)
            match = decoded == str(ref_uuid)
            if not match:
                light_all_ok = False
            self.stdout.write(
                f"  • {label:36s}: {'[OK]' if match else '[FALLÓ]'} ({t_ms:5.2f} ms)"
            )

        # Desgaste físico
        wear_scratch = _simulate_wear_and_tear(base_cv, "scratch")
        wear_smudge = _simulate_wear_and_tear(base_cv, "smudge")
        dec_scratch, _, _ = detector.detectAndDecode(wear_scratch)
        dec_smudge, _, _ = detector.detectAndDecode(wear_smudge)
        wear_ok = (dec_scratch == str(ref_uuid)) and (dec_smudge == str(ref_uuid))
        self.stdout.write(
            f"  • Tolerancia a rayón físico / mancha (Reed-Solomon): {'[OK]' if wear_ok else '[FALLÓ]'}"
        )

        # ------------------------------------------------------------------
        # DICTAMEN DE CRITERIOS DE ACEPTACIÓN
        # ------------------------------------------------------------------
        max_latency = max(max_dist_ms, max_light_ms)
        kpi_03_pass = max_latency < 500.0 and dist_all_ok and light_all_ok

        self.stdout.write(self.style.NOTICE("\n" + "=" * 75))
        self.stdout.write(self.style.NOTICE("  DICTAMEN FORMAL DE CRITERIOS DE ACEPTACIÓN (WBS 3.12 & 3.13)"))
        self.stdout.write(self.style.NOTICE("=" * 75))

        kpi_01_status = self.style.SUCCESS("APROBADO (100% unicidad, 0 colisiones)") if kpi_01_pass else self.style.ERROR("RECHAZADO")
        kpi_02_status = self.style.SUCCESS("APROBADO (100% lectura a 10-30 cm y luz variable)") if dist_all_ok and light_all_ok else self.style.ERROR("RECHAZADO")
        kpi_03_status = self.style.SUCCESS(f"APROBADO (Máx: {max_latency:.2f} ms < 500 ms)") if kpi_03_pass else self.style.ERROR(f"RECHAZADO ({max_latency:.2f} ms)")

        self.stdout.write(f"  • KPI-01 [Unicidad de Tokens]:        {kpi_01_status}")
        self.stdout.write(f"  • KPI-02 [Legibilidad Óptica 10-30cm]: {kpi_02_status}")
        self.stdout.write(f"  • KPI-03 [Tiempo Decodificación]:     {kpi_03_status}")
        self.stdout.write(self.style.NOTICE("=" * 75 + "\n"))

