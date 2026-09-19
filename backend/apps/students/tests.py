import pytest
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient
from apps.students.models import Guardian, Student
from apps.students.validators import validate_curp, validate_phone_number

class TestStudentValidators:
    def test_valid_curp(self):
        # CURP válida sintácticamente (18 caracteres)
        valid_curp = "GAOS090815HJCXRN02"
        validate_curp(valid_curp)  # No debe lanzar excepción

    def test_invalid_curp_length(self):
        with pytest.raises(ValidationError):
            validate_curp("GAOS090815HJCXR")  # 15 caracteres

    def test_invalid_curp_format(self):
        with pytest.raises(ValidationError):
            validate_curp("123456789012345678")  # Números en lugar de letras iniciales

    def test_valid_phone(self):
        validate_phone_number("3312345678")

    def test_invalid_phone(self):
        with pytest.raises(ValidationError):
            validate_phone_number("331234")  # Menos de 10 dígitos


class TestStudentModels(TestCase):
    def setUp(self):
        self.guardian = Guardian.objects.create(
            full_name="María Elena Ochoa Silva",
            phone_number="3319876543",
            relationship=Guardian.Relationship.MADRE,
            email="maria.ochoa@example.com"
        )
        self.student = Student.objects.create(
            enrollment_id="2026-1A-001",
            curp="GAOS090815HJCXRN02",
            first_name="Saúl Ibrahim",
            last_name_father="García",
            last_name_mother="Ochoa",
            grade=1,
            group="A",
            shift=Student.Shift.MATUTINO,
            guardian=self.guardian
        )

    def test_student_str_and_properties(self):
        assert self.student.full_name == "García Ochoa Saúl Ibrahim"
        assert self.student.academic_group == "1°A (Turno Matutino)"
        assert "2026-1A-001" in str(self.student)

    def test_guardian_str(self):
        assert "María Elena Ochoa Silva" in str(self.guardian)
        assert "Madre" in str(self.guardian)

    def test_duplicate_enrollment_id_fails(self):
        with pytest.raises(Exception):
            Student.objects.create(
                enrollment_id="2026-1A-001",  # Duplicada
                curp="OISG100512MJCXRX01",
                first_name="Hermano",
                last_name_father="García",
                last_name_mother="Ochoa",
                grade=1,
                group="B",
                guardian=self.guardian
            )


class TestStudentAPI(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.guardian = Guardian.objects.create(
            full_name="Carlos García Pérez",
            phone_number="3331122334",
            relationship=Guardian.Relationship.PADRE
        )

    def test_create_student_via_api(self):
        payload = {
            "enrollment_id": "2026-2B-042",
            "curp": "GAPC080410HJCXRN09",
            "first_name": "Mateo",
            "last_name_father": "García",
            "last_name_mother": "Pérez",
            "grade": 2,
            "group": "B",
            "shift": "MATUTINO",
            "guardian": str(self.guardian.id)
        }
        response = self.client.post("/api/v1/students/", payload, format="json")
        assert response.status_code == 201
        assert response.data["enrollment_id"] == "2026-2B-042"
        assert response.data["academic_group"] == "2°B (Turno Matutino)"

    def test_list_students_and_filtering(self):
        Student.objects.create(
            enrollment_id="2026-3A-010",
            curp="GARC070211HJCXRX03",
            first_name="Luis",
            last_name_father="García",
            grade=3,
            group="A",
            guardian=self.guardian
        )
        response = self.client.get("/api/v1/students/?grade=3")
        assert response.status_code == 200
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["enrollment_id"] == "2026-3A-010"
