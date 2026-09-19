"""
Comando de gestión para sembrar datos piloto de prueba en la Escuela Secundaria Mixta 5.
Genera estudiantes y tutores representativos para los 3 grados escolares y
emite sus correspondientes tokens QR institucionales con firma criptográfica HMAC.
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.students.models import Guardian, Student
from apps.qr_codes.crypto import issue_qr_token_for_student

PILOT_DATA = [
    {
        "guardian": {
            "full_name": "Laura Elena Silva Mendoza",
            "phone_number": "3314567890",
            "relationship": Guardian.Relationship.MADRE,
            "email": "laura.silva@example.com"
        },
        "students": [
            {
                "enrollment_id": "2026-1A-001",
                "curp": "SIML120514MJCXR01",
                "first_name": "Sofía",
                "last_name_father": "Silva",
                "last_name_mother": "Mendoza",
                "grade": 1,
                "group": "A",
                "shift": Student.Shift.MATUTINO,
                "medical_notes": "Alergia a la penicilina"
            }
        ]
    },
    {
        "guardian": {
            "full_name": "Roberto Carlos Gómez Navarro",
            "phone_number": "3323456789",
            "relationship": Guardian.Relationship.PADRE,
            "email": "roberto.gomez@example.com"
        },
        "students": [
            {
                "enrollment_id": "2026-2B-015",
                "curp": "GONR110320HJCXR02",
                "first_name": "Emiliano",
                "last_name_father": "Gómez",
                "last_name_mother": "Navarro",
                "grade": 2,
                "group": "B",
                "shift": Student.Shift.MATUTINO,
                "medical_notes": ""
            }
        ]
    },
    {
        "guardian": {
            "full_name": "Patricia Ochoa Morales",
            "phone_number": "3334567891",
            "relationship": Guardian.Relationship.TUTOR_LEGAL,
            "email": "patricia.ochoa@example.com"
        },
        "students": [
            {
                "enrollment_id": "2026-3A-030",
                "curp": "GOMP100805HJCXR03",
                "first_name": "Santiago",
                "last_name_father": "González",
                "last_name_mother": "Ochoa",
                "grade": 3,
                "group": "A",
                "shift": Student.Shift.MATUTINO,
                "medical_notes": "Uso de inhalador para asma en Educación Física"
            }
        ]
    }
]

class Command(BaseCommand):
    help = "Siembra datos piloto de alumnos, tutores y credenciales QR en la Escuela Secundaria Mixta 5"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Sembrando datos piloto institucionales..."))

        total_guardians = 0
        total_students = 0
        total_qrs = 0

        for item in PILOT_DATA:
            g_data = item["guardian"]
            guardian, g_created = Guardian.objects.get_or_create(
                full_name=g_data["full_name"],
                defaults=g_data
            )
            if g_created:
                total_guardians += 1

            for s_data in item["students"]:
                enrollment = s_data["enrollment_id"]
                student, s_created = Student.objects.get_or_create(
                    enrollment_id=enrollment,
                    defaults={**s_data, "guardian": guardian}
                )
                if s_created:
                    total_students += 1
                
                # Emitir token QR si no tiene activo
                if not student.active_qr_token:
                    qr_token = issue_qr_token_for_student(student, reason="Lote piloto inicial")
                    total_qrs += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  [+] Alumno: {student.full_name} ({student.academic_group}) -> Token QR: {qr_token.token}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSembrado completado con éxito:\n"
                f"  - Tutores registrados: {total_guardians}\n"
                f"  - Estudiantes registrados: {total_students}\n"
                f"  - Credenciales QR emitidas: {total_qrs}\n"
            )
        )
