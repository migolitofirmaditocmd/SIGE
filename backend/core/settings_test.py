"""Settings de prueba para pytest — sobreescribe DB a SQLite en memoria."""
from core.settings import *  # noqa: F401, F403

# Forzar SQLite en memoria para tests: sin dependencia de red a Supabase
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

