"""Comando de gestión para sembrar los datos piloto de la Escuela Secundaria Mixta 5.

Ejecuta la importación del listado oficial de estudiantes desde el archivo Excel
institucional ('docs/base de datos en excel/LISTADO PARA CREDENCIALES.xlsx').
"""

from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Comando de consola para sembrar datos escolares piloto y credenciales QR."""

    help = "Siembra los datos piloto institucionales de la Escuela Secundaria Mixta 5."

    def handle(self, *args: Any, **options: Any) -> None:
        """Invoca la importación del listado escolar oficial."""
        self.stdout.write(self.style.NOTICE("Sembrando datos piloto institucionales..."))
        call_command("import_school_excel")
