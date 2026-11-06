"""Comando de gestión para ejecutar procesos programados manualmente (PP §1 principio 4, RNF-MAN-03).

Permite al operador técnico o evaluador ejecutar cualquier background job
indicando la fecha de negocio y el turno correspondiente, con registro en
JOB_RUN y AUDIT_LOG.
"""

from datetime import date
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from apps.core.clock import ClockService
from apps.core.jobs import execute_job


class Command(BaseCommand):
    """Comando de consola para ejecución manual de tareas recurrentes en SIGE."""

    help = "Ejecuta un proceso programado indicando fecha y turno (PP §1, RNF-MAN-03)."

    def add_arguments(self, parser: CommandParser) -> None:
        """Define los argumentos requeridos y opcionales del comando.

        Args:
            parser (CommandParser): Analizador de argumentos de Django.
        """
        parser.add_argument(
            "job_name",
            type=str,
            help="Nombre del job a ejecutar (ej. check_student_absences, check_teacher_absences).",
        )
        parser.add_argument(
            "--date",
            type=str,
            default=None,
            help="Fecha de negocio en formato YYYY-MM-DD. Por defecto la fecha actual.",
        )
        parser.add_argument(
            "--shift",
            type=str,
            default="MATUTINO",
            choices=["MATUTINO", "VESPERTINO"],
            help="Turno a procesar (solo para check_student_absences).",
        )
        parser.add_argument(
            "--confirm-school-day",
            action="store_true",
            default=False,
            help="Confirma explícitamente que la fecha fue día lectivo (levanta guardia de sanidad).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Ejecuta el job solicitado y reporta el resultado en consola.

        Args:
            *args (Any): Argumentos posicionales.
            **options (Any): Opciones analizadas por argparse.

        Raises:
            CommandError: Si los parámetros provistos no son válidos.
        """
        job_name = options["job_name"]
        shift = options["shift"]
        confirm_school_day = options["confirm_school_day"]

        run_date: date | None = None
        if options["date"]:
            try:
                run_date = date.fromisoformat(options["date"])
            except ValueError:
                raise CommandError(
                    f"Formato de fecha inválido '{options['date']}'. Utilice YYYY-MM-DD."
                )
        else:
            run_date = ClockService.today()

        self.stdout.write(
            self.style.NOTICE(
                f"Iniciando ejecución manual de '{job_name}' para {run_date} ({shift})..."
            )
        )

        try:
            job_run = execute_job(
                job_name=job_name,
                run_date=run_date,
                shift=shift,
                confirm_school_day=confirm_school_day,
                user=None,
            )
        except ValueError as err:
            raise CommandError(str(err)) from err

        color = self.style.SUCCESS if job_run.status == "COMPLETADO" else self.style.WARNING
        self.stdout.write(color(f"\n[JOB_RUN] Resultado: {job_run.status}"))
        self.stdout.write(f"  Proceso:     {job_run.job_name}")
        self.stdout.write(f"  Fecha/Scope: {job_run.run_date} [{job_run.scope}]")
        self.stdout.write(f"  Evaluados:   {job_run.evaluated_count}")
        self.stdout.write(f"  Creados:     {job_run.created_count}")
        if job_run.error:
            self.stdout.write(self.style.ERROR(f"  Error:       {job_run.error}"))

