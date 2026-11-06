"""Servicio de reloj inyectable y sustituible para SIGE.

Cumple con el requisito RNF-MAN-03 (Testabilidad) y el principio 5 de la
Estrategia de Procesos Programados v2: toda lógica del sistema que dependa
de la fecha u hora debe obtenerla a través de este servicio, permitiendo
congelar o manipular el tiempo en entornos de prueba y ejecuciones manuales
sin alterar el reloj del sistema operativo.
"""

from contextlib import contextmanager
from datetime import date, datetime, time
from typing import Generator
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils import timezone


class ClockService:
    """Proveedor centralizado de fecha y hora para el sistema SIGE.

    Permite obtener la hora actual de forma consciente de la zona horaria
    (timezone-aware) y provee métodos para congelar el tiempo durante pruebas
    unitarias o simulaciones de cortes operativos.
    """

    _frozen_datetime: datetime | None = None

    @classmethod
    def now(cls) -> datetime:
        """Obtiene la fecha y hora actual consciente de la zona horaria.

        Si el reloj se encuentra congelado (por ejemplo, en pruebas), retorna
        el valor previamente fijado asegurando que tenga zona horaria.

        Returns:
            datetime: Fecha y hora actual consciente de la zona horaria.
        """
        if cls._frozen_datetime is not None:
            return cls._frozen_datetime
        return timezone.now()

    @classmethod
    def today(cls) -> date:
        """Obtiene la fecha actual en la zona horaria institucional.

        Returns:
            date: Fecha actual correspondiente a TIME_ZONE del sistema.
        """
        current_dt = cls.now()
        target_tz = timezone.get_current_timezone()
        return current_dt.astimezone(target_tz).date()

    @classmethod
    def time(cls) -> time:
        """Obtiene la hora actual en la zona horaria institucional.

        Returns:
            time: Hora actual correspondiente a TIME_ZONE del sistema.
        """
        current_dt = cls.now()
        target_tz = timezone.get_current_timezone()
        return current_dt.astimezone(target_tz).time()

    @classmethod
    def is_frozen(cls) -> bool:
        """Indica si el reloj se encuentra actualmente congelado.

        Returns:
            bool: True si el reloj está fijado a un tiempo específico, False si no.
        """
        return cls._frozen_datetime is not None

    @classmethod
    def freeze(cls, target: datetime | date | str) -> datetime:
        """Fija el reloj del sistema a una fecha u hora específica.

        Args:
            target (datetime | date | str): Momento al que se desea congelar el reloj.
                Puede ser un objeto datetime, un objeto date (asumiendo inicio del día),
                o una cadena en formato ISO 8601 (ej. '2026-10-27T10:00:00').

        Returns:
            datetime: Objeto datetime consciente de zona horaria al que quedó congelado.

        Raises:
            ValueError: Si la cadena provista no tiene un formato ISO válido.
        """
        target_tz = timezone.get_current_timezone()

        if isinstance(target, str):
            parsed = datetime.fromisoformat(target)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=target_tz)
            cls._frozen_datetime = parsed
        elif isinstance(target, datetime):
            if target.tzinfo is None:
                target = target.replace(tzinfo=target_tz)
            cls._frozen_datetime = target
        elif isinstance(target, date):
            naive_dt = datetime.combine(target, time.min)
            cls._frozen_datetime = naive_dt.replace(tzinfo=target_tz)
        else:
            raise ValueError(f"Tipo no soportado para congelar reloj: {type(target)}")

        return cls._frozen_datetime

    @classmethod
    def unfreeze(cls) -> None:
        """Restaura el reloj del sistema a su comportamiento en tiempo real."""
        cls._frozen_datetime = None

    @classmethod
    @contextmanager
    def freeze_time(
        cls, target: datetime | date | str
    ) -> Generator[datetime, None, None]:
        """Context manager para congelar temporalmente el reloj en bloques 'with'.

        Args:
            target (datetime | date | str): Momento al cual fijar el reloj.

        Yields:
            datetime: La fecha y hora fijadas durante el contexto.

        Examples:
            >>> with ClockService.freeze_time('2026-10-27T10:00:00'):
            ...     assert ClockService.today() == date(2026, 10, 27)
        """
        previous_frozen = cls._frozen_datetime
        try:
            frozen_dt = cls.freeze(target)
            yield frozen_dt
        finally:
            cls._frozen_datetime = previous_frozen

