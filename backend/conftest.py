"""Configuración global de pytest para el proyecto SIGE.

Sobreescribe DATABASES para usar SQLite en memoria durante los tests,
evitando dependencia de red a Supabase y acelerando la suite de pruebas.
"""
import django
from django.conf import settings


def pytest_configure(config: "pytest.Config") -> None:
    """Fuerza SQLite en memoria para todos los tests unitarios.

    Esto garantiza que los tests sean rápidos, reproducibles y sin
    dependencia de conectividad a la base de datos de producción (Supabase).

    Args:
        config (pytest.Config): Objeto de configuración de pytest.
    """
    settings.DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }

