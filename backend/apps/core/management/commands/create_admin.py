"""Comando de gestión para inicializar la primera cuenta de Administrador (P-D5, CA-001-11).

Crea la cuenta de Administrador sin contraseña desde la consola del servidor,
genera un token criptográfico de un solo uso con vigencia acotada y registra
la operación en AUDIT_LOG como acción de consola autorizada (user_id=NULL).
"""

import hashlib
import secrets
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError, CommandParser

from apps.core.clock import ClockService
from apps.core.models import AuditLog, PasswordResetToken

User = get_user_model()


class Command(BaseCommand):
    """Comando de consola para bootstrap del primer usuario Administrador en SIGE.

    Cumple con CA-001-11, RF-AUT-04 y la Decisión P-D5:
    No asigna una contraseña inicial fija ni depende de correo o Internet.
    Entrega un enlace seguro de un solo uso para establecer la clave.
    """

    help = "Crea la cuenta inicial de Administrador y genera un enlace de un solo uso (CA-001-11)."

    def add_arguments(self, parser: CommandParser) -> None:
        """Configura los argumentos requeridos y opcionales por línea de comandos.

        Args:
            parser (CommandParser): Analizador de argumentos de Django.
        """
        parser.add_argument(
            "--username",
            type=str,
            required=True,
            help="Nombre de usuario del Administrador (ej. admin).",
        )
        parser.add_argument(
            "--email",
            type=str,
            required=True,
            help="Correo electrónico institucional del Administrador.",
        )
        parser.add_argument(
            "--first-name",
            type=str,
            default="Administrador",
            help="Nombre de la persona titular.",
        )
        parser.add_argument(
            "--last-name-father",
            type=str,
            default="SIGE",
            help="Apellido paterno del titular.",
        )
        parser.add_argument(
            "--base-url",
            type=str,
            default="http://localhost:3000",
            help="URL base de la interfaz frontend (por defecto http://localhost:3000).",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        """Ejecuta la creación de la cuenta administrativa y el token de un solo uso.

        Args:
            *args (Any): Argumentos posicionales.
            **options (Any): Opciones analizadas por argparse.

        Raises:
            CommandError: Si los datos provistos son inválidos o faltantes.
        """
        username = options["username"].strip()
        email = options["email"].strip().lower()
        first_name = options["first_name"].strip()
        last_name_father = options["last_name_father"].strip()
        base_url = options["base_url"].rstrip("/")

        if not username:
            raise CommandError("El nombre de usuario no puede estar vacío.")
        if "@" not in email:
            raise CommandError("El correo electrónico provisto no tiene un formato válido.")

        # Obtener o crear el usuario administrador
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name_father,
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        now = ClockService.now()

        # Si el usuario ya existía, asegurarse de que tenga permisos de superusuario
        if not created:
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            if email and user.email != email:
                user.email = email
            self.stdout.write(
                self.style.WARNING(
                    f"El usuario '{username}' ya existe. Generando nuevo enlace de un solo uso..."
                )
            )

        # La cuenta no tiene contraseña activa asignada inicialmente
        user.set_unusable_password()
        user.save()

        # Invalidar tokens previos no consumidos del mismo usuario (RN-AUT-07)
        PasswordResetToken.objects.filter(
            user=user,
            used_at__isnull=True,
            invalidated_at__isnull=True,
            expires_at__gt=now,
        ).update(invalidated_at=now)

        # Generar token opaco de alta entropía (32 bytes base64url)
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        expiry_minutes = getattr(settings, "PASSWORD_RESET_EXPIRY_MINUTES", 30)
        expires_at = now + timedelta(minutes=expiry_minutes)

        PasswordResetToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        # Registrar en AUDIT_LOG con origin='MANUAL', user=None (§3.13)
        audit_entry = AuditLog(
            action="auth:admin_bootstrap",
            user=None,
            origin=AuditLog.Origin.MANUAL,
            reason="Creación / inicialización de cuenta de Administrador por consola (CA-001-11)",
            new_value={
                "username": username,
                "email": email,
                "created": created,
                "expires_at": expires_at.isoformat(),
            },
        )
        audit_entry.clean()
        audit_entry.save()

        setup_url = f"{base_url}/auth/definir-password?token={raw_token}"

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 70))
        self.stdout.write(self.style.SUCCESS("  CUENTA DE ADMINISTRADOR CONFIGURADA EXITOSAMENTE (SIGE)"))
        self.stdout.write(self.style.SUCCESS("=" * 70))
        self.stdout.write(f" Usuario:       {username}")
        self.stdout.write(f" Correo:        {email}")
        self.stdout.write(f" Vigencia:      {expiry_minutes} minutos (expira a las {expires_at:%Y-%m-%d %H:%M:%S})")
        self.stdout.write(f" Token hash:    {token_hash[:16]}...")
        self.stdout.write(self.style.WARNING("\n Enlace de un solo uso para definir contraseña (sin correo ni internet):"))
        self.stdout.write(self.style.NOTICE(f" {setup_url}\n"))
        self.stdout.write(self.style.SUCCESS(" Auditoría:     Registrado en AUDIT_LOG (action='auth:admin_bootstrap')"))
        self.stdout.write(self.style.SUCCESS("=" * 70 + "\n"))

