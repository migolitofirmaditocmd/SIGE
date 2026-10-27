"""Tests del módulo de estudiantes — WBS 3.7.

Cubre los criterios de aceptación de la especificación API REST v2
§2.4 y §3.4, las Historias de Usuario del módulo EST y las reglas
de negocio RN-EST-01 a RN-EST-14.

Organización:
    - TestValidators: validadores de CURP, matrícula y nombres.
    - TestGuardianModel: modelo Guardian (nombre estructurado).
    - TestStudentModel: modelo Student (completeness, estados, QR).
    - TestStudentListAPI: GET /api/v1/students/ (listado + filtros).
    - TestStudentCreateAPI: POST /api/v1/students/ (creación + reglas).
    - TestStudentDetailAPI: GET y PATCH /api/v1/students/{id}/.
    - TestStudentStatusAPI: POST /status/ y /reinstate/.
    - TestGuardianPatchAPI: PATCH /guardians/{id}/ con aviso compartido.
    - TestConsentAPI: PATCH /student-guardians/{id}/consent/.
    - TestInvalidateContactAPI: POST /invalidate-contact/.
"""

import pytest
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient

from apps.students.models import (
    Guardian,
    GuardianConsentLog,
    Student,
    StudentGuardian,
)
from apps.students.validators import (
    validate_curp,
    validate_enrollment_id,
    validate_person_name,
    validate_phone_number,
)


# ======================================================================
# Fixtures
# ======================================================================

@pytest.fixture
def client() -> APIClient:
    """Cliente API sin autenticación (desarrollo; JWT pendiente)."""
    return APIClient()


@pytest.fixture
def guardian_data() -> dict:
    """Datos mínimos válidos para crear un Guardian."""
    return {
        "first_name": "María Elena",
        "last_name_father": "Ochoa",
        "last_name_mother": "Silva",
        "email": "maria.ochoa@example.com",
        "phone_number": "3319876543",
    }


@pytest.fixture
def guardian(guardian_data) -> Guardian:
    """Instancia de Guardian persistida en base de datos."""
    return Guardian.objects.create(**guardian_data)


@pytest.fixture
def student_payload(guardian) -> dict:
    """Payload válido para POST /api/v1/students/."""
    return {
        "enrollment_id": "2026-1A-001",
        "curp": "GAOS090815HJCXRN02",
        "first_name": "Saúl Ibrahim",
        "last_name_father": "García",
        "last_name_mother": "Ochoa",
        "grade": 1,
        "group_letter": "A",
        "shift": "MATUTINO",
        "guardians": [
            {
                "existing_guardian_id": str(guardian.id),
                "relationship": "MADRE",
                "is_primary_contact": True,
            }
        ],
    }


@pytest.fixture
def student(student_payload) -> Student:
    """Crea un Student completo via API y retorna la instancia."""
    client = APIClient()
    resp = client.post("/api/v1/students/", student_payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED, resp.data
    return Student.objects.get(pk=resp.data["id"])


# ======================================================================
# TestValidators
# ======================================================================

class TestValidators:
    """Tests de los validadores de campos (RN-TRX-08/09, RN-EST-02)."""

    def test_curp_valida_acepta(self) -> None:
        """Una CURP de 18 caracteres con estructura correcta no lanza error."""
        validate_curp("GAOS090815HJCXRN02")

    def test_curp_longitud_incorrecta_falla(self) -> None:
        """Una CURP con menos de 18 caracteres lanza ValidationError."""
        with pytest.raises(ValidationError):
            validate_curp("GAOS090815HJCXR")

    def test_curp_formato_invalido_falla(self) -> None:
        """Dígitos en posiciones de letras iniciales lanza ValidationError."""
        with pytest.raises(ValidationError):
            validate_curp("123456789012345678")

    def test_curp_vacia_se_permite(self) -> None:
        """CURP vacía no lanza error (es opcional, RF-EST-01 v2.1)."""
        validate_curp("")  # debe pasar sin excepción

    def test_matricula_valida_acepta(self) -> None:
        """Matrícula alfanumérica de 4–20 caracteres no lanza error."""
        validate_enrollment_id("2026-1A-001")

    def test_matricula_vacia_falla(self) -> None:
        """Matrícula vacía lanza ValidationError."""
        with pytest.raises(ValidationError):
            validate_enrollment_id("")

    def test_telefono_10_digitos_acepta(self) -> None:
        """Teléfono de 10 dígitos no lanza error."""
        validate_phone_number("3312345678")

    def test_telefono_incorrecto_falla(self) -> None:
        """Teléfono con menos de 10 dígitos lanza ValidationError."""
        with pytest.raises(ValidationError):
            validate_phone_number("331234")

    def test_nombre_valido_acepta(self) -> None:
        """Nombre con acentos y longitud correcta no lanza error."""
        validate_person_name("María Elena", "Nombre")

    def test_nombre_sustituto_falla(self) -> None:
        """Valor sustituto 'N/A' lanza ValidationError (RN-TRX-09)."""
        with pytest.raises(ValidationError):
            validate_person_name("N/A", "Nombre")

    def test_nombre_muy_corto_falla(self) -> None:
        """Nombre de 1 carácter lanza ValidationError (RN-TRX-08)."""
        with pytest.raises(ValidationError):
            validate_person_name("X", "Nombre")


# ======================================================================
# TestGuardianModel
# ======================================================================

@pytest.mark.django_db
class TestGuardianModel:
    """Tests del modelo Guardian con nombre estructurado en 3 campos."""

    def test_display_name_calculado(self, guardian: Guardian) -> None:
        """display_name devuelve 'Nombre Apellido_p Apellido_m' (RN-TRX-10)."""
        assert guardian.display_name == "María Elena Ochoa Silva"

    def test_sort_name_calculado(self, guardian: Guardian) -> None:
        """sort_name devuelve 'Apellido_p Apellido_m, Nombre' (RN-TRX-10)."""
        assert guardian.sort_name == "Ochoa Silva, María Elena"

    def test_apellido_materno_nulo_se_guarda_como_none(self) -> None:
        """Apellido materno en blanco se almacena como NULL (RN-TRX-08)."""
        g = Guardian.objects.create(
            first_name="Pedro",
            last_name_father="López",
            last_name_mother=None,
            email="pedro@example.com",
        )
        assert g.last_name_mother is None

    def test_str_incluye_nombre_y_contacto(self, guardian: Guardian) -> None:
        """__str__ incluye el nombre y el email o teléfono."""
        assert "María Elena Ochoa Silva" in str(guardian)


# ======================================================================
# TestStudentModel
# ======================================================================

@pytest.mark.django_db
class TestStudentModel:
    """Tests del modelo Student: completeness, estados y propiedades."""

    def test_completeness_incompleto_sin_birth_date(
        self, guardian: Guardian
    ) -> None:
        """Sin birth_date, completeness es INCOMPLETO (RN-EST-10)."""
        s = Student.objects.create(
            enrollment_id="TEST-001",
            first_name="Ana",
            last_name_father="Gómez",
            grade=1,
            group_letter="A",
            shift="MATUTINO",
        )
        assert s.completeness == Student.Completeness.INCOMPLETO

    def test_completeness_completo_con_birth_date_y_photo(
        self, guardian: Guardian
    ) -> None:
        """Con birth_date y photo_url, completeness es COMPLETO (RN-EST-10)."""
        from datetime import date
        s = Student.objects.create(
            enrollment_id="TEST-002",
            first_name="Ana",
            last_name_father="Gómez",
            grade=1,
            group_letter="A",
            shift="MATUTINO",
            birth_date=date(2010, 5, 15),
            photo_url="students/uuid/photo.jpg",
        )
        assert s.completeness == Student.Completeness.COMPLETO

    def test_enrollment_id_unico(self, guardian: Guardian) -> None:
        """Dos estudiantes con la misma matrícula lanzan IntegrityError (RN-EST-02)."""
        Student.objects.create(
            enrollment_id="UNICO-001",
            first_name="Luis",
            last_name_father="Pérez",
            grade=2,
            group_letter="B",
        )
        with pytest.raises(Exception):
            Student.objects.create(
                enrollment_id="UNICO-001",  # duplicada
                first_name="Otro",
                last_name_father="Alumno",
                grade=3,
                group_letter="C",
            )

    def test_academic_group_property(self, guardian: Guardian) -> None:
        """academic_group devuelve '1°A (Matutino)'."""
        s = Student.objects.create(
            enrollment_id="TEST-003",
            first_name="Juan",
            last_name_father="Hernández",
            grade=1,
            group_letter="A",
            shift="MATUTINO",
        )
        assert s.academic_group == "1°A (Matutino)"

    def test_display_name_calculado(self, guardian: Guardian) -> None:
        """display_name incluye los tres campos de nombre (RN-TRX-10)."""
        s = Student.objects.create(
            enrollment_id="TEST-004",
            first_name="Carlos",
            last_name_father="Martínez",
            last_name_mother="López",
            grade=2,
            group_letter="B",
        )
        assert s.display_name == "Carlos Martínez López"


# ======================================================================
# TestStudentListAPI
# ======================================================================

@pytest.mark.django_db
class TestStudentListAPI:
    """Tests del endpoint GET /api/v1/students/ (listado, filtros, búsqueda)."""

    def _create_student(self, enrollment_id: str, grade: int,
                        group_letter: str, guardian: Guardian) -> Student:
        s = Student.objects.create(
            enrollment_id=enrollment_id,
            first_name="Test",
            last_name_father="Apellido",
            grade=grade,
            group_letter=group_letter,
            shift="MATUTINO",
        )
        StudentGuardian.objects.create(
            student=s, guardian=guardian,
            relationship=StudentGuardian.Relationship.MADRE,
            is_valid_contact=True,
        )
        return s

    def test_listado_paginado(self, client: APIClient, guardian: Guardian) -> None:
        """El listado responde 200 con estructura paginada (§1.5)."""
        self._create_student("LIST-001", 1, "A", guardian)
        resp = client.get("/api/v1/students/")
        assert resp.status_code == status.HTTP_200_OK
        assert "results" in resp.data
        assert "count" in resp.data

    def test_filtro_por_grado(self, client: APIClient, guardian: Guardian) -> None:
        """El filtro ?grade= devuelve solo alumnos de ese grado."""
        self._create_student("GRADE-001", 1, "A", guardian)
        self._create_student("GRADE-002", 2, "B", guardian)
        resp = client.get("/api/v1/students/?grade=1")
        assert resp.status_code == status.HTTP_200_OK
        ids = [r["enrollment_id"] for r in resp.data["results"]]
        assert "GRADE-001" in ids
        assert "GRADE-002" not in ids

    def test_filtro_por_grupo(self, client: APIClient, guardian: Guardian) -> None:
        """El filtro ?group= devuelve solo alumnos de ese grupo."""
        self._create_student("GROUP-001", 1, "A", guardian)
        self._create_student("GROUP-002", 1, "B", guardian)
        resp = client.get("/api/v1/students/?group=A")
        assert resp.status_code == status.HTTP_200_OK
        ids = [r["enrollment_id"] for r in resp.data["results"]]
        assert "GROUP-001" in ids
        assert "GROUP-002" not in ids

    def test_busqueda_por_nombre(self, client: APIClient, guardian: Guardian) -> None:
        """El parámetro ?search= filtra por nombre o matrícula."""
        s = Student.objects.create(
            enrollment_id="SRCH-001",
            first_name="Xiomara",
            last_name_father="Reyes",
            grade=3,
            group_letter="C",
        )
        resp = client.get("/api/v1/students/?search=Xiomara")
        assert resp.status_code == status.HTTP_200_OK
        ids = [r["enrollment_id"] for r in resp.data["results"]]
        assert "SRCH-001" in ids

    def test_cache_control_no_store(self, client: APIClient) -> None:
        """La respuesta incluye Cache-Control: no-store (§1.8)."""
        resp = client.get("/api/v1/students/")
        assert resp.status_code == status.HTTP_200_OK
        assert "no-store" in resp.get("Cache-Control", "")


# ======================================================================
# TestStudentCreateAPI
# ======================================================================

@pytest.mark.django_db
class TestStudentCreateAPI:
    """Tests de POST /api/v1/students/ (creación con tutores)."""

    def test_crea_estudiante_con_guardian_existente(
        self, client: APIClient, guardian: Guardian
    ) -> None:
        """POST con existing_guardian_id crea alumno y vínculo (RN-EST-03)."""
        payload = {
            "enrollment_id": "2026-1A-100",
            "first_name": "Mateo",
            "last_name_father": "Flores",
            "grade": 1,
            "group_letter": "A",
            "shift": "MATUTINO",
            "guardians": [
                {
                    "existing_guardian_id": str(guardian.id),
                    "relationship": "PADRE",
                    "is_primary_contact": True,
                }
            ],
        }
        resp = client.post("/api/v1/students/", payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        assert resp.data["enrollment_id"] == "2026-1A-100"
        assert resp.data["completeness"] == "INCOMPLETO"

    def test_matricula_duplicada_devuelve_422(
        self, client: APIClient, guardian: Guardian
    ) -> None:
        """Matrícula duplicada devuelve 422 DUPLICATE_ENROLLMENT (RN-EST-02)."""
        Student.objects.create(
            enrollment_id="DUP-001",
            first_name="Primero",
            last_name_father="Apellido",
            grade=1,
            group_letter="A",
        )
        payload = {
            "enrollment_id": "DUP-001",
            "first_name": "Segundo",
            "last_name_father": "Apellido",
            "grade": 1,
            "group_letter": "A",
            "shift": "MATUTINO",
            "guardians": [
                {"existing_guardian_id": str(guardian.id), "relationship": "MADRE"}
            ],
        }
        resp = client.post("/api/v1/students/", payload, format="json")
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        assert resp.data["error_code"] == "DUPLICATE_ENROLLMENT"

    def test_sin_tutores_devuelve_400(self, client: APIClient) -> None:
        """Sin tutores en el payload devuelve error 400 (RN-EST-03)."""
        payload = {
            "enrollment_id": "NO-TUTOR-01",
            "first_name": "Solo",
            "last_name_father": "Alumno",
            "grade": 1,
            "group_letter": "A",
            "shift": "MATUTINO",
            "guardians": [],
        }
        resp = client.post("/api/v1/students/", payload, format="json")
        assert resp.status_code == status.HTTP_400_BAD_REQUEST

    def test_curp_duplicada_devuelve_422(
        self, client: APIClient, guardian: Guardian
    ) -> None:
        """CURP duplicada devuelve 422 DUPLICATE_RECORD."""
        Student.objects.create(
            enrollment_id="CURP-001",
            curp="GAOS090815HJCXRN02",
            first_name="Ya",
            last_name_father="Existe",
            grade=1,
            group_letter="A",
        )
        payload = {
            "enrollment_id": "CURP-002",
            "curp": "GAOS090815HJCXRN02",
            "first_name": "Otro",
            "last_name_father": "Alumno",
            "grade": 1,
            "group_letter": "A",
            "shift": "MATUTINO",
            "guardians": [
                {"existing_guardian_id": str(guardian.id), "relationship": "MADRE"}
            ],
        }
        resp = client.post("/api/v1/students/", payload, format="json")
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        assert resp.data["error_code"] == "DUPLICATE_RECORD"

    def test_crea_historial_consentimiento_inicial(
        self, client: APIClient, guardian: Guardian
    ) -> None:
        """Al crear alumno se genera renglón inicial PENDIENTE en consent log (RN-EST-07)."""
        payload = {
            "enrollment_id": "CONSENT-001",
            "first_name": "Lucia",
            "last_name_father": "Torres",
            "grade": 2,
            "group_letter": "B",
            "shift": "MATUTINO",
            "guardians": [
                {"existing_guardian_id": str(guardian.id), "relationship": "MADRE"}
            ],
        }
        resp = client.post("/api/v1/students/", payload, format="json")
        assert resp.status_code == status.HTTP_201_CREATED
        student = Student.objects.get(pk=resp.data["id"])
        sg = StudentGuardian.objects.get(student=student)
        log_count = GuardianConsentLog.objects.filter(
            student_guardian=sg,
            new_status="PENDIENTE",
            previous_status__isnull=True,
        ).count()
        assert log_count == 1

    def test_deteccion_guardian_existente_devuelve_422(
        self, client: APIClient, guardian: Guardian
    ) -> None:
        """Guardian coincidente sin existing_guardian_id devuelve GUARDIAN_MATCH_FOUND (RN-EST-13)."""
        payload = {
            "enrollment_id": "MATCH-001",
            "first_name": "Pedro",
            "last_name_father": "Ruiz",
            "grade": 1,
            "group_letter": "A",
            "shift": "MATUTINO",
            "guardians": [
                {
                    # Mismo nombre y email que el fixture guardian
                    "first_name": "María Elena",
                    "last_name_father": "Ochoa",
                    "last_name_mother": "Silva",
                    "email": "maria.ochoa@example.com",
                    "phone_number": "3319876543",
                    "relationship": "MADRE",
                }
            ],
        }
        resp = client.post("/api/v1/students/", payload, format="json")
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.data["error_code"] == "GUARDIAN_MATCH_FOUND"
        assert "candidates" in resp.data["details"]


# ======================================================================
# TestStudentDetailAPI
# ======================================================================

@pytest.mark.django_db
class TestStudentDetailAPI:
    """Tests de GET y PATCH /api/v1/students/{id}/."""

    def test_get_devuelve_expediente(
        self, client: APIClient, student: Student
    ) -> None:
        """GET devuelve el expediente con display_name y guardians (§2.4)."""
        resp = client.get(f"/api/v1/students/{student.id}/")
        assert resp.status_code == status.HTTP_200_OK
        assert "display_name" in resp.data
        assert "guardians" in resp.data
        assert "consent_warning" in resp.data
        assert "missing_fields" in resp.data
        assert resp.get("Cache-Control") == "no-store"

    def test_get_inexistente_devuelve_404(self, client: APIClient) -> None:
        """GET de UUID inexistente devuelve 404 NOT_FOUND."""
        import uuid
        resp = client.get(f"/api/v1/students/{uuid.uuid4()}/")
        assert resp.status_code == status.HTTP_404_NOT_FOUND
        assert resp.data["error_code"] == "NOT_FOUND"

    def test_patch_actualiza_campos(
        self, client: APIClient, student: Student
    ) -> None:
        """PATCH actualiza campos opcionales sin tocar la matrícula (RN-EST-02)."""
        original_enrollment = student.enrollment_id
        resp = client.patch(
            f"/api/v1/students/{student.id}/",
            {"blood_type": "O+", "enrollment_id": "IGNORADO"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        student.refresh_from_db()
        assert student.blood_type == "O+"
        assert student.enrollment_id == original_enrollment  # inmutable

    def test_patch_curp_duplicada_devuelve_422(
        self, client: APIClient, student: Student, guardian: Guardian
    ) -> None:
        """PATCH con CURP de otro alumno devuelve DUPLICATE_RECORD."""
        other = Student.objects.create(
            enrollment_id="OTHER-001",
            curp="OISG100512MJCXRX01",
            first_name="Otro",
            last_name_father="Alumno",
            grade=2,
            group_letter="B",
        )
        resp = client.patch(
            f"/api/v1/students/{student.id}/",
            {"curp": "OISG100512MJCXRX01"},
            format="json",
        )
        assert resp.status_code in (
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
        assert resp.data["error_code"] == "DUPLICATE_RECORD"


# ======================================================================
# TestStudentStatusAPI
# ======================================================================

@pytest.mark.django_db
class TestStudentStatusAPI:
    """Tests de POST /students/{id}/status/ y /reinstate/ (RN-EST-04/06/09)."""

    def test_baja_logica_activo_a_baja(
        self, client: APIClient, student: Student
    ) -> None:
        """Un alumno ACTIVO puede pasar a BAJA con motivo."""
        resp = client.post(
            f"/api/v1/students/{student.id}/status/",
            {"status": "BAJA", "reason": "Se muda de ciudad"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        student.refresh_from_db()
        assert student.status == "BAJA"

    def test_egresado_es_final(self, client: APIClient, student: Student) -> None:
        """EGRESADO no puede reiniciarse a ACTIVO (RN-EST-09)."""
        client.post(
            f"/api/v1/students/{student.id}/status/",
            {"status": "EGRESADO", "reason": "Terminó el ciclo"},
            format="json",
        )
        resp = client.post(
            f"/api/v1/students/{student.id}/reinstate/",
            {"reason": "Intento de reinscripción inválido"},
            format="json",
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.data["error_code"] == "INVALID_TRANSITION"

    def test_reinstate_baja_a_activo(
        self, client: APIClient, student: Student
    ) -> None:
        """Un alumno en BAJA puede reincorporarse a ACTIVO (RN-EST-06)."""
        client.post(
            f"/api/v1/students/{student.id}/status/",
            {"status": "BAJA", "reason": "Temporal"},
            format="json",
        )
        resp = client.post(
            f"/api/v1/students/{student.id}/reinstate/",
            {"reason": "Regresó al ciclo escolar"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        student.refresh_from_db()
        assert student.status == "ACTIVO"

    def test_transicion_invalida_activo_a_activo(
        self, client: APIClient, student: Student
    ) -> None:
        """Intentar pasar de ACTIVO a ACTIVO devuelve INVALID_TRANSITION."""
        resp = client.post(
            f"/api/v1/students/{student.id}/reinstate/",
            {"reason": "No aplica"},
            format="json",
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.data["error_code"] == "INVALID_TRANSITION"


# ======================================================================
# TestGuardianPatchAPI
# ======================================================================

@pytest.mark.django_db
class TestGuardianPatchAPI:
    """Tests de PATCH /guardians/{id}/ con aviso de compartido (RN-EST-14)."""

    def test_patch_guardian_no_compartido_actualiza(
        self, client: APIClient, guardian: Guardian, student: Student
    ) -> None:
        """PATCH a Guardian con un solo alumno actualiza sin pedir confirmación."""
        resp = client.patch(
            f"/api/v1/students/guardians/{guardian.id}/",
            {"email": "nuevo@example.com"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        guardian.refresh_from_db()
        assert guardian.email == "nuevo@example.com"

    def test_patch_guardian_compartido_sin_confirm_devuelve_422(
        self, client: APIClient, guardian: Guardian, student: Student
    ) -> None:
        """PATCH a Guardian compartido sin confirm=true devuelve CONFIRMATION_REQUIRED."""
        # Crear segundo alumno con el mismo guardian
        s2 = Student.objects.create(
            enrollment_id="SHARED-002",
            first_name="Segundo",
            last_name_father="Alumno",
            grade=2,
            group_letter="B",
        )
        StudentGuardian.objects.create(
            student=s2,
            guardian=guardian,
            relationship=StudentGuardian.Relationship.MADRE,
            is_valid_contact=True,
        )
        resp = client.patch(
            f"/api/v1/students/guardians/{guardian.id}/",
            {"phone_number": "3391234567"},
            format="json",
        )
        assert resp.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert resp.data["error_code"] == "CONFIRMATION_REQUIRED"
        assert "affected_students" in resp.data["details"]

    def test_patch_guardian_compartido_con_confirm_actualiza(
        self, client: APIClient, guardian: Guardian, student: Student
    ) -> None:
        """PATCH con ?confirm=true actualiza el Guardian compartido (RN-EST-14)."""
        s2 = Student.objects.create(
            enrollment_id="SHARED-003",
            first_name="Tercero",
            last_name_father="Alumno",
            grade=2,
            group_letter="C",
        )
        StudentGuardian.objects.create(
            student=s2,
            guardian=guardian,
            relationship=StudentGuardian.Relationship.PADRE,
            is_valid_contact=True,
        )
        resp = client.patch(
            f"/api/v1/students/guardians/{guardian.id}/?confirm=true",
            {"phone_number": "3391234567"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        guardian.refresh_from_db()
        assert guardian.phone_number == "3391234567"


# ======================================================================
# TestConsentAPI
# ======================================================================

@pytest.mark.django_db
class TestConsentAPI:
    """Tests de PATCH /student-guardians/{id}/consent/ (RN-EST-07)."""

    def test_actualiza_consentimiento_y_genera_log(
        self, client: APIClient, student: Student
    ) -> None:
        """PATCH actualiza consent_status y crea renglón en GuardianConsentLog."""
        sg = student.student_guardians.first()
        assert sg is not None
        resp = client.patch(
            f"/api/v1/students/student-guardians/{sg.id}/consent/",
            {"consent_status": "OTORGADO"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        sg.refresh_from_db()
        assert sg.consent_status == "OTORGADO"
        log = GuardianConsentLog.objects.filter(
            student_guardian=sg, new_status="OTORGADO"
        ).first()
        assert log is not None
        assert log.previous_status == "PENDIENTE"


# ======================================================================
# TestInvalidateContactAPI
# ======================================================================

@pytest.mark.django_db
class TestInvalidateContactAPI:
    """Tests de POST /student-guardians/{id}/invalidate-contact/ (RN-EST-11)."""

    def test_invalida_contacto_con_motivo(
        self, client: APIClient, student: Student
    ) -> None:
        """POST con motivo marca is_valid_contact=False (RN-EST-11)."""
        sg = student.student_guardians.first()
        resp = client.post(
            f"/api/v1/students/student-guardians/{sg.id}/invalidate-contact/",
            {"reason": "El número ya no pertenece al tutor"},
            format="json",
        )
        assert resp.status_code == status.HTTP_200_OK
        sg.refresh_from_db()
        assert sg.is_valid_contact is False

    def test_invalida_contacto_sin_motivo_devuelve_400(
        self, client: APIClient, student: Student
    ) -> None:
        """POST sin motivo devuelve 400 VALIDATION_ERROR."""
        sg = student.student_guardians.first()
        resp = client.post(
            f"/api/v1/students/student-guardians/{sg.id}/invalidate-contact/",
            {},
            format="json",
        )
        assert resp.status_code == status.HTTP_400_BAD_REQUEST
        assert resp.data["error_code"] == "VALIDATION_ERROR"
