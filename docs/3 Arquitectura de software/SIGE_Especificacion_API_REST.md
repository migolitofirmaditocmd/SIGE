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
    *   **RN-AST-02/RN-AST-03:** Si el escaneo ocurre dentro de la ventana de rebote (configurable, 5 min por defecto) contada desde el último escaneo procesado del mismo estudiante, se **rechaza silenciosamente** (204, sin crear ningún registro) y se notifica al operador.
    *   **RN-AST-07:** Si el escaneo ocurre fuera de la ventana de rebote pero el estudiante ya tiene un estado determinado (`ASISTIO`, `LLEGO_TARDE` o un estado `MANUAL`) para hoy, se guarda en `ATTENDANCE_STUDENT_EVENT` sin alterar el estado ya determinado.
    *   **RN-AST-09:** Si el estudiante ya tiene `FALTO` de origen `AUTOMATICO` para hoy, este escaneo lo **reclasifica** (`ASISTIO`/`LLEGO_TARDE`) comparando la hora efectiva contra `cutoff_time`; un `FALTA_JUSTIFICADA` (origen `MANUAL`) nunca se reclasifica.
    *   **RN-EST-05:** Rechaza (422) si el estudiante no está `ACTIVO
    *   **RN-TRX-04:** Si el scan proviene de un dispositivo offline sincronizado, usa la hora capturada; si es online en vivo, usa la del servidor.

#### POST `/api/v1/attendance/students/{id}/justify/`
*   **Capacidad:** Cambiar el estatus de una inasistencia a `FALTA_JUSTIFICADA`.
*   **Request:** `{ "record_date": "YYYY-MM-DD", "justification_reason": "Motivo..." }`
*   **Response (200 OK):** `{ "status": "FALTA_JUSTIFICADA" }`
*   **Reglas Validadas (403 / 422):**
    *   **RN-AST-06:** No elimina el registro anterior, hace un update de estado.
    *   **RN-AST-04:** Verifica que el usuario que ejecuta (JWT) sea Administrador o Personal Administrativo (el Prefecto NO está autorizado a justificar). **RN-AST-05:** exige `justification_reason` y conserva el valor anterior. **RN-AST-22:** solo puede justificarse un registro en estado `FALTO`; si el estado actual no es `FALTO`, rechazar con 422.`

---

### 2.3 Credenciales QR (Módulo QR)

#### POST `/api/v1/credentials/tokens/`
*   **Capacidad:** Emitir un nuevo QR para un estudiante o docente (por alta o reemplazo).
*   **Request:** `{ "entity_type": "STUDENT" | "TEACHER", "entity_id": "uuid", "reason": "PERDIDA|ROBO|DANO|DUPLICIDAD" }` (`reason` obligatorio solo si la persona ya tiene un token `VIGENTE`)
*   **Reglas Validadas (403 / 422):**
    *   **RN-QR-01/05:** Si la persona **no** tiene token vigente, cualquier `ADM` o `PAD` puede emitir uno nuevo (alta inicial).
    *   **RN-QR-03:** Si la persona **ya** tiene un token vigente, la operación es una revocación + reemplazo y se rechaza (403) si el solicitante no es `ADM`; el campo `reason` es obligatorio en este caso y queda registrado en `AUDIT_LOG`.
    *   **RN-EST-05 / RN-AST-23:** Rechaza si el estudiante no está `ACTIVO` o el docente no está `ACTIVO`.
    *   **RN-QR-02:** El token generado no debe poder derivar datos personales.

---

### 2.4 Estudiantes (Módulo EST)

#### GET `/api/v1/students/{id}/`
*   **Capacidad:** Obtener el expediente del alumno.
*   **Request:** (N/A)
*   **Response (200 OK):** Datos del estudiante anidados con su información de `STUDENT_GUARDIAN`.
*   **Reglas Validadas:**
    *   **Permisos:** Solo `ADM`, `PRE` y `PAD` pueden llamar este endpoint; `DOC` y `SL` reciben 403 (US-011).
    *   **RN-EST-12 (filtrado condicional del payload):**
        *   `blood_type`, `allergies`: visibles para `ADM`, `PAD` y `PRE`.
        *   `has_payment_debt`, `payment_debt_amount`, `pending_subjects`: visibles únicamente para `ADM` y `PAD`; se remueven del JSON para `PRE`.

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
*   **Reglas Validadas (403 / 422):**
    *   **RN-REP-03:** El backend valida que la transición solicitada sea válida desde el estado actual del reporte (`REGISTRADO → REVISADO_PREFECTO → CANALIZADO → REVISADO_ADMINISTRATIVO → AUTORIZADO/COMUNICADO/RESUELTO`); cualquier salto se rechaza con 422, sin importar lo que el cliente haya mostrado.
    *   Transición a `REVISADO_PREFECTO` o `RECHAZADO` (desde `REGISTRADO`): solo `PRE`. Un rechazo aquí **no** admite reintento sobre el mismo reporte (RN-REP-08): se cierra y exige un `POST /reports/` nuevo con `replaces_report_id`.
    *   Transición a `CANALIZADO`: solo `PRE`, y solo desde `REVISADO_PREFECTO`.
    *   Transición a `REVISADO_ADMINISTRATIVO` o `RECHAZADO` (desde `CANALIZADO`): solo `PAD`. Un rechazo aquí regresa el reporte a `REVISADO_PREFECTO` (RN-REP-03), no lo cierra.
    *   Transición a `AUTORIZADO`/`RESUELTO` (comunicar o no comunicar a la familia): **solo `PAD`** (RN-REP-04); nunca `PRE` ni `DOC`, sin excepción.
    *   `rejection_reason` obligatorio en cualquier transición a `RECHAZADO` (RN-REP-08); `no_communication_reason` obligatorio si se marca `RESUELTO` sin pasar por `COMUNICADO`.
    *   **RN-REP-06:** toda transición aceptada crea una fila en `REPORT_TRANSITION_LOG`.

---

### 2.6 Importaciones Masivas (Módulo IMP)

#### POST `/api/v1/imports/upload/`
*   **Capacidad:** Subir archivo Excel para carga de alumnos.
*   **Request:** FormData con el archivo `.xlsx` y `group_id`.
*   **Response (200 OK):** `{ "batch_id": "uuid", "status": "VISTA_PREVIA", "total_rows": 45, "error_rows": 2 }`
*   **Reglas Validadas:**
    *   **RN-IMP-01 & RN-IMP-03:** Corre las validaciones de negocio en memoria, detecta repetidos (RN-EST-02) y genera filas en `IMPORT_ROW_ERROR`. No inserta en la base de datos de producción (RN-IMP-04).
    *   **RN-IMP-08:** Obliga a asignar el grupo, turno y ciclo a todo el bloque desde este momento.
    *   **RN-IMP-05:** solo ADM y PAD pueden llamar este endpoint (403 para los demás roles).
    *   **RN-IMP-06:** las filas con datos mínimos pero sin fecha de nacimiento o fotografía se cuentan aparte en la respuesta.

#### POST `/api/v1/imports/{batch_id}/confirm/`
*   **Capacidad:** Inyecta la vista previa a la base de datos real.
*   **Reglas Validadas:**
    *   **RN-IMP-04:** Verifica que el batch siga en estatus `VISTA_PREVIA` y realiza la inserción de las filas marcadas como limpias, omitiendo los errores irresolubles. Muta el estado a `CONFIRMADO`.
    *   **RN-IMP-07:** si al confirmar, la matrícula de una fila ya fue creada por otro proceso desde que se generó la vista previa, esa fila (y solo esa) se rechaza y se agrega a IMPORT_ROW_ERROR; el resto del lote se inserta con normalidad.
