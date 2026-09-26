# SIGE — Especificación de API REST
**Definición de Endpoints y Mapeo de Reglas de Negocio**

Este documento provee la especificación funcional de la API REST del Sistema Integral de Gestión Escolar (SIGE). Se definen los contratos principales (request/response), los códigos de error unificados (RF-API-04) y el mapeo explícito de las Reglas de Negocio (RN) que el backend debe validar en cada endpoint.

---

## 1. Códigos de Error Uniformes (RF-API-04)
Todo endpoint de la API que devuelva un error debe cumplir con esta estructura base JSON, para facilitar la interpretación del frontend:

```json
{
  "error_code": "BUSINESS_RULE_VIOLATION",
  "message": "Mensaje legible para el usuario final",
  "details": { "campo": ["motivo"] },
  "rn_reference": "RN-AST-01" 
}
```

**Mapeo de HTTP Status Codes:**
*   `400 Bad Request`: Error de formato o validación básica (ej. falta un campo requerido).
*   `401 Unauthorized`: Token JWT inválido, ausente o expirado.
*   `403 Forbidden`: El rol del usuario no tiene permisos para la acción solicitada.
*   `404 Not Found`: El recurso no existe.
*   `422 Unprocessable Entity`: Violación de una Regla de Negocio (RN) específica.
*   `429 Too Many Requests`: Exceso de peticiones (ej. demasiados intentos de login).

---

## 2. Endpoints por Módulo

### 2.1 Autenticación (Módulo AUT)

#### POST `/api/v1/auth/login/`
*   **Capacidad:** Iniciar sesión y obtener tokens JWT.
*   **Request:** `{ "username": "...", "password": "..." }`
*   **Response (200 OK):** `{ "access": "jwt...", "refresh": "jwt...", "role": "DOCENTE" }`
*   **Reglas Validadas (422 / 403):**
    *   **RN-AUT-01:** Valida que el usuario tenga un rol activo.
    *   **RN-AUT-03:** Verifica si la cuenta está bloqueada temporalmente (`locked_until`). Incrementa contador de fallos (`failed_login_attempts`) si la clave es incorrecta.

---

### 2.2 Asistencia Estudiantil (Módulo AST)

#### POST `/api/v1/attendance/students/scan/`
*   **Capacidad:** Procesar el escaneo de un código QR de estudiante en la entrada. Soporta sincronización en batch de la PWA.
*   **Request:** `{ "qr_token": "uuidv4", "scan_datetime": "2026-09-25T07:15:00Z" }`
*   **Response (201 Created):** `{ "status": "ASISTIO", "effective_datetime": "..." }`
*   **Reglas Validadas (422):**
    *   **RN-QR-04:** Valida que el token escaneado exista y tenga `status='VIGENTE'`.
    *   **RN-AST-01:** Calcula si la hora del escaneo está dentro de la tolerancia respecto al `cutoff_time` del `GROUP` del alumno. Retorna `LLEGO_TARDE` o `ASISTIO`.
    *   **RN-AST-07:** Si ya existe un registro de asistencia para este alumno hoy, el nuevo escaneo se guarda silenciosamente en `ATTENDANCE_STUDENT_EVENT` sin alterar el estatus original (ventana de rebote).
    *   **RN-TRX-04:** Si el scan proviene de un dispositivo offline sincronizado, usa la hora capturada; si es online en vivo, usa la del servidor.

#### POST `/api/v1/attendance/students/{id}/justify/`
*   **Capacidad:** Cambiar el estatus de una inasistencia a `FALTA_JUSTIFICADA`.
*   **Request:** `{ "record_date": "YYYY-MM-DD", "justification_reason": "Motivo..." }`
*   **Response (200 OK):** `{ "status": "FALTA_JUSTIFICADA" }`
*   **Reglas Validadas (403 / 422):**
    *   **RN-AST-06:** No elimina el registro anterior, hace un update de estado.
    *   **RN-AST-10:** Verifica que el usuario que ejecuta (JWT) sea `Administrador` o `Personal Administrativo`.

---

### 2.3 Credenciales QR (Módulo QR)

#### POST `/api/v1/credentials/tokens/`
*   **Capacidad:** Emitir un nuevo QR para un estudiante o docente (por alta o reemplazo).
*   **Request:** `{ "entity_type": "STUDENT", "entity_id": "uuid", "origin": "REEMPLAZO" }`
*   **Response (201 Created):** `{ "token_id": "uuid", "qr_image_url": "https://..." }`
*   **Reglas Validadas (422):**
    *   **RN-QR-01:** Revoca automáticamente cualquier otro token que estuviese `VIGENTE` para esta misma persona.
    *   **RN-QR-03:** Garantiza mediante UUIDv4 aleatorio que el token nunca haya existido en la tabla (no se reciclan).
    *   **RN-QR-05:** Verifica la restricción de que se asigna o a un alumno o a un docente, pero nunca a ambos.

---

### 2.4 Estudiantes (Módulo EST)

#### GET `/api/v1/students/{id}/`
*   **Capacidad:** Obtener el expediente del alumno.
*   **Request:** (N/A)
*   **Response (200 OK):** Datos del estudiante anidados con su información de `STUDENT_GUARDIAN`.
*   **Reglas Validadas (Payload Condicional):**
    *   **RN-EST-12:** (Control de Privacidad). Si el JWT pertenece a un `DOCENTE` o `PREFECTO`, los campos `blood_type`, `allergies`, `has_payment_debt` y `STUDENT_PENDING_SUBJECT` se remueven completamente del JSON de respuesta.

#### POST `/api/v1/students/`
*   **Capacidad:** Crear un nuevo estudiante manualmente.
*   **Request:** JSON completo con datos obligatorios e información de tutores.
*   **Response (201 Created):** Datos creados.
*   **Reglas Validadas (422):**
    *   **RN-EST-02:** El `enrollment_id` (matrícula) debe ser único globalmente.
    *   **RN-EST-03:** El array de tutores asociado debe contener al menos un contacto que resulte en `is_valid_contact=True` (ya sea por correo o teléfono).
    *   **RN-EST-10:** Si `birth_date` o `photo_url` vienen nulos, se marca automáticamente `completeness="INCOMPLETO"`.

---

### 2.5 Reportes de Incidencias (Módulo REP)

#### POST `/api/v1/reports/`
*   **Capacidad:** Levantar un reporte disciplinario contra un alumno.
*   **Request:** `{ "student_id": "...", "report_type_id": "...", "observation": "...", "severity_id": "..." }`
*   **Response (201 Created):** `{ "report_id": "...", "status": "REGISTRADO" }`
*   **Reglas Validadas (422 / 403):**
    *   **RN-REP-01:** Valida estrictamente que la longitud de `observation` sea entre 50 y 100 caracteres.
    *   **RN-REP-09:** Si lo redacta un DOCENTE, valida que el alumno pertenezca a un grupo al que ese docente da clases (`TEACHER_GROUP_ASSIGNMENT`).

#### PATCH `/api/v1/reports/{id}/`
*   **Capacidad:** Modificar un reporte existente (ej. Prefecto autoriza o rechaza).
*   **Request:** `{ "status": "RECHAZADO", "rejection_reason": "Falta firma..." }`
*   **Reglas Validadas:**
    *   **RN-REP-06:** Crea automáticamente una fila en `REPORT_TRANSITION_LOG` documentando el cambio de estado.
    *   **RN-REP-08:** Si el status es `RECHAZADO`, se exige el campo `rejection_reason`.

---

### 2.6 Importaciones Masivas (Módulo IMP)

#### POST `/api/v1/imports/upload/`
*   **Capacidad:** Subir archivo Excel para carga de alumnos.
*   **Request:** FormData con el archivo `.xlsx` y `group_id`.
*   **Response (200 OK):** `{ "batch_id": "uuid", "status": "VISTA_PREVIA", "total_rows": 45, "error_rows": 2 }`
*   **Reglas Validadas:**
    *   **RN-IMP-01 & RN-IMP-03:** Corre las validaciones de negocio en memoria, detecta repetidos (RN-EST-02) y genera filas en `IMPORT_ROW_ERROR`. No inserta en la base de datos de producción (RN-IMP-04).
    *   **RN-IMP-08:** Obliga a asignar el grupo, turno y ciclo a todo el bloque desde este momento.

#### POST `/api/v1/imports/{batch_id}/confirm/`
*   **Capacidad:** Inyecta la vista previa a la base de datos real.
*   **Reglas Validadas:**
    *   **RN-IMP-04:** Verifica que el batch siga en estatus `VISTA_PREVIA` y realiza la inserción de las filas marcadas como limpias, omitiendo los errores irresolubles. Muta el estado a `CONFIRMADO`.
