# SIGE — Especificación de API REST
**Definición de Endpoints y Mapeo de Reglas de Negocio**

**Versión:** 2.0 | **Estado:** Para revisión del equipo
**Derivado de:** Acta v10 · RF/RNF v3 · RN v3 · HU v2 · CA v2 · Modelo de Datos v3.0


Este documento provee la especificación funcional de la API REST del Sistema Integral de Gestión Escolar (SIGE). Se definen los contratos principales (request/response), los códigos de error unificados (RF-API-04) y el mapeo explícito de las Reglas de Negocio (RN) que el backend debe validar en cada endpoint.

---

## 1. Convenciones globales

### 1.1 Documentación y versionado
La API se publica con OpenAPI 3 generado desde el código (por ejemplo `drf-spectacular`) en `/api/v1/schema/` y `/api/v1/docs/` (RF-API-01). Este documento es la especificación funcional; el esquema OpenAPI es el contrato técnico y debe coincidir con él.

### 1.2 Formato de error uniforme (RF-API-04)
```json
{
  "error_code": "QR_REVOKED",
  "message": "QR revocado: verifique la identidad manualmente",
  "details": { "campo": ["motivo"] },
  "rn_reference": "RN-QR-04",
  "trace_id": "d3b07384-d9a0-4c9b-8f6e-0a1b2c3d4e5f"
}
```
`trace_id` es el identificador de correlación que también se escribe en los registros del servidor, para rastrear el error (RF-API-04).

### 1.3 Mapeo de códigos HTTP
*   `400 Bad Request`: error de formato o validación básica.
*   `401 Unauthorized`: credenciales inválidas en el login, o token ausente, inválido o vencido (`TOKEN_EXPIRED`, RN-AUT-04).
*   `403 Forbidden`: el rol no tiene permiso, o la cuenta está desactivada (evaluado solo con credenciales correctas, para no revelar cuentas).
*   `404 Not Found`: el recurso no existe **o el rol no tiene permiso de verlo** (p. ej. un reporte ajeno, RN-REP-05): no se revela su existencia.
*   `422 Unprocessable Entity`: violación de una regla de negocio.
*   `429 Too Many Requests`: bloqueo de cuenta por intentos fallidos o rate limiting; siempre con `Retry-After`.
*   **Resultados no erróneos que se comunican en el cuerpo (200):** un escaneo ignorado por rebote, un evento adicional o una reclasificación **no son errores**; ver 2.2.

### 1.4 Catálogo de `error_code` (inicial)
`INVALID_CREDENTIALS`, `ACCOUNT_LOCKED`, `ACCOUNT_DISABLED`, `TOKEN_EXPIRED`, `PERMISSION_DENIED`, `NOT_FOUND`, `VALIDATION_ERROR`, `BUSINESS_RULE_VIOLATION`, `QR_NOT_RECOGNIZED`, `QR_REVOKED`, `STUDENT_NOT_ACTIVE`, `TEACHER_NOT_ACTIVE`, `EVENT_IN_FUTURE`, `EVENT_TOO_OLD`, `DUPLICATE_ENROLLMENT`, `DUPLICATE_RECORD`, `GUARDIAN_MATCH_FOUND`, `INVALID_TRANSITION`, `IMPORT_INVALID_STRUCTURE`, `RATE_LIMITED`. Cada uno lleva su `rn_reference`.

### 1.5 Listados
Todo listado es paginado: parámetros `page` y `page_size` (máx. 100), respuesta `{ "count": n, "next": url|null, "previous": url|null, "results": [...] }`. El orden por defecto de personas es apellido paterno, apellido materno, nombre(s) (RN-TRX-10). Todo objeto de persona incluye `display_name` y `sort_name` calculados (RN-TRX-10); nunca un `full_name` almacenado.

### 1.6 Fechas y horas
ISO 8601 con zona horaria. El servidor almacena en UTC y la interfaz muestra la zona horaria institucional. Las horas efectivas las calcula el backend (RN-TRX-04); ningún cliente impone la hora efectiva de un evento en línea.

### 1.7 Permisos por endpoint
Cada endpoint declara su matriz de roles y se aplica en el backend (RN-API-01, RN-AUT-06). Un rol sin permiso recibe 403; un recurso fuera del alcance del rol (p. ej. reporte de otro grupo) recibe 404.
---

## 2. Endpoints por Módulo

### 2.1 Autenticación (Módulo AUT)

#### POST `/api/v1/auth/login/`
*   **Capacidad:** iniciar sesión.
*   **Request:** `{ "username": "...", "password": "..." }`
*   **Response (200 OK):** `{ "access": "jwt...", "expires_in": 900, "user": { "id": "uuid", "display_name": "...", "role": "DOCENTE", "teacher_id": "uuid|null" } }`. El refresh token **no** viaja en el cuerpo: se entrega en cookie `HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth/` (SG-01).
*   **Errores:**
    *   `401 INVALID_CREDENTIALS`: usuario o contraseña incorrectos, **o usuario inexistente**, con idéntica respuesta (anti-enumeración).
    *   `429 ACCOUNT_LOCKED` (con `Retry-After`): cuenta bloqueada o con intentos agotados (RN-AUT-03). Se aplica por nombre de usuario recibido exista o no (SG-02).
    *   `403 ACCOUNT_DISABLED`: cuenta desactivada; solo se devuelve cuando la contraseña es correcta.
*   **Reglas:** RN-AUT-01 (la cuenta tiene exactamente un rol y está activa, `USER.is_active`), RN-AUT-03 (contador, bloqueo y reinicio), RN-AUT-05 (el inicio de sesión, exitoso o fallido, queda en `AUDIT_LOG`).

#### POST `/api/v1/auth/refresh/`
*   **Capacidad:** renovar el access token con la cookie de refresh.
*   **Response (200 OK):** `{ "access": "jwt...", "expires_in": 900 }` y nueva cookie de refresh (rotación).
*   **Errores:** `401 TOKEN_EXPIRED` si el refresh está vencido, revocado o fue reutilizado (esto último revoca todas las sesiones del usuario). **Reglas:** RN-AUT-04, RF-AUT-01.

#### POST `/api/v1/auth/logout/`
*   **Capacidad:** cerrar la sesión; marca `USER_SESSION.revoked_at` con `LOGOUT` y borra la cookie. **Reglas:** RF-AUT-01, CA-001-06.

#### POST `/api/v1/auth/password-reset/` y POST `/api/v1/auth/password-reset/confirm/`
*   **Capacidad:** solicitar el enlace de restablecimiento y definir la nueva contraseña. La solicitud responde igual exista o no la cuenta. **Reglas:** RF-AUT-04, RN-AUT-07, RN-INF-02, CA-005-01..08 (detalle en SG-08).

---

### 2.2 Asistencia Estudiantil (Módulo AST)

#### POST `/api/v1/attendance/students/scan/`
*   **Capacidad:** procesar el escaneo de un QR de estudiante, en línea.
*   **Roles:** `PRE`, `PAD`. Otros roles reciben 403 (CA-027-07).
*   **Request:** `{ "qr_token": "uuid", "client_event_id": "uuid" }`. En línea, la hora efectiva es la del **servidor** al recibir la solicitud (RN-TRX-04); el cliente no envía hora.
*   **Respuestas (el servidor decide el resultado; todas llevan `result`):**
    *   `201 Created` — `{ "result": "REGISTRADO", "attendance_id": "uuid", "status": "ASISTIO|LLEGO_TARDE", "effective_datetime": "...", "student": { "display_name": "...", "group": "...", "photo_url": "..." } }`. La foto y el nombre permiten la verificación visual del operador (SG-06).
    *   `200 OK` — `{ "result": "EVENTO_ADICIONAL", "status": "<estado ya determinado>" }`: escaneo fuera de la ventana de rebote con estado ya determinado; se guarda en `ATTENDANCE_STUDENT_EVENT` sin cambiar el estado (RN-AST-07).
    *   `200 OK` — `{ "result": "RECLASIFICADO", "previous_status": "FALTO", "status": "ASISTIO|LLEGO_TARDE", "effective_datetime": "..." }`: el estudiante tenía `FALTO` de origen `AUTOMATICO`; se reclasifica por hora efectiva contra `cutoff_time` (RN-AST-09). Un `FALTA_JUSTIFICADA` o un estado modificado manualmente nunca se reclasifica (cae en `EVENTO_ADICIONAL`).
    *   `200 OK` — `{ "result": "DUPLICADO_IGNORADO", "message": "Registro duplicado", "window_minutes": 5 }`: escaneo dentro de la ventana de rebote, contada desde el último escaneo **procesado** (RN-AST-02/03). No crea registro ni evento y **el operador es notificado mediante este cuerpo**.
*   **Errores (422):**
    *   `QR_NOT_RECOGNIZED` — el token no existe, tiene formato inválido o pertenece a otro tipo de entidad, p. ej. un QR de docente (RN-QR-02, RN-QR-05). Sin registro.
    *   `QR_REVOKED` — el token está `REVOCADO`; incluye alerta para verificar identidad manualmente (RN-QR-04).
    *   `STUDENT_NOT_ACTIVE` — el estudiante está en `BAJA` o `EGRESADO`; el QR no se revoca (RN-EST-05, RN-EST-04).
    *   `EVENT_IN_FUTURE` — la hora efectiva queda en el futuro (RN-TRX-04).
*   **Reglas:** RN-QR-04, RN-EST-05, RN-AST-01 (`ASISTIO` si la hora efectiva es ≤ `cutoff_time` del grupo y jornada; si no, `LLEGO_TARDE`), RN-AST-02/03/07/09, RN-TRX-04, RN-API-01. La respuesta debe resolverse en menos de 250 ms (RNF-DES-01): la ruta crítica no envía correos ni hace trabajo pesado.

#### POST `/api/v1/attendance/students/sync/`
*   **Capacidad:** sincronizar los eventos capturados offline (RN-MOV-02, US-033).
*   **Roles:** `PRE`, `PAD`.
*   **Request:** `{ "events": [ { "client_event_id": "uuid", "qr_token": "uuid", "captured_at": "ISO8601", "clock_offset_ms": 1200, "captured_by": "uuid" } ] }` (máximo 1,000, el tamaño del buffer).
*   **Procesamiento:** en orden de `captured_at`. Cada evento es independiente: uno inválido no aborta el lote. La hora efectiva es `captured_at` corregida con `clock_offset_ms` (RN-TRX-04, RNF-FIA-04). Cada evento pasa por las mismas validaciones y resultados que el escaneo en línea (RN-MOV-01, RN-API-01). Los eventos se reintentan con seguridad: un `client_event_id` ya procesado devuelve su resultado previo sin reprocesarse (idempotencia; ver §7 I-08).
*   **Response (200 OK):** `{ "accepted": [ { "client_event_id": "...", "result": "REGISTRADO|EVENTO_ADICIONAL|RECLASIFICADO|DUPLICADO_IGNORADO" } ], "discarded": [ { "client_event_id": "...", "error_code": "QR_REVOKED|STUDENT_NOT_ACTIVE|QR_NOT_RECOGNIZED|EVENT_IN_FUTURE|EVENT_TOO_OLD", "rn_reference": "RN-QR-04" } ], "summary": { "accepted": 12, "discarded": 1 } }`. Los descartados se notifican al operador con su motivo (US-033).
*   **Validaciones adicionales offline:** antigüedad máxima `OFFLINE_MAX_AGE_HOURS` (D-11), desfase razonable del reloj y vigencia del rol/cuenta del operador (SG-09).

#### POST `/api/v1/attendance/students/{attendance_id}/justify/`
*   **Capacidad:** cambiar un registro `FALTO` a `FALTA_JUSTIFICADA`. `{attendance_id}` es el id de `ATTENDANCE_STUDENT`.
*   **Roles:** `ADM`, `PAD`. El Prefecto recibe 403 (RN-AST-04).
*   **Request:** `{ "justification_reason": "Motivo..." }`
*   **Response (200 OK):** `{ "attendance_id": "uuid", "status": "FALTA_JUSTIFICADA", "origin": "MANUAL" }`
*   **Reglas (403 / 422):** RN-AST-04 (solo ADM/PAD); RN-AST-05 (motivo obligatorio; se conservan valor anterior, valor nuevo, usuario y fecha/hora en `AUDIT_LOG`); RN-AST-06 (no se elimina el registro, se actualiza su estado); RN-AST-22 (solo un registro en estado `FALTO` puede justificarse; si el estado actual es otro, 422 `INVALID_TRANSITION`).

#### PATCH `/api/v1/attendance/students/{attendance_id}/`
*   **Capacidad:** modificar manualmente el estado de un registro ya determinado.
*   **Roles:** `ADM`, `PAD`. **Request:** `{ "status": "...", "reason": "..." }`. El resultado queda con `origin='MANUAL'` y el estado manual prevalece sobre cualquier reclasificación por escaneo (RN-AST-09).
*   **Reglas:** RN-AST-04, RN-AST-05, RN-AST-06, RN-TRX-07. **Pendiente de definir con la institución:** el conjunto de transiciones permitidas (propuesta: cualquier estado a `ASISTIO`, `LLEGO_TARDE` o `FALTO` con motivo; `FALTA_JUSTIFICADA` únicamente desde `FALTO`).

#### POST `/api/v1/attendance/teachers/{attendance_id}/justify/` y PATCH `/api/v1/attendance/teachers/{attendance_id}/`
*   Equivalentes para asistencia docente. **Roles:** `ADM`, `PAD`. **Reglas:** RN-AST-17, RN-AST-22 (solo `FALTO` puede justificarse), RN-AST-21 (no se elimina), RN-TRX-07.

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
*   **Capacidad:** obtener el expediente del estudiante.
*   **Roles:** `ADM`, `PRE`, `PAD`; `DOC` y `SL` reciben 403 (US-011).
*   **Response (200 OK):** datos del estudiante con `display_name`, `sort_name`, `status`, `completeness`, `missing_fields` (RN-EST-10), `group` (grado, grupo, ciclo, turno), `guardians[]` (con `relationship`, `is_primary_contact`, `is_valid_contact`, `consent_status`) y `consent_warning` (verdadero si algún tutor está `PENDIENTE` o `REVOCADO`, RN-EST-08).
*   **Filtrado condicional (RN-EST-12), por serializador central:** `blood_type` y `allergies` para `ADM`, `PRE`, `PAD`. `has_payment_debt` (booleano, **sin monto**) y `pending_subjects` solo para `ADM` y `PAD`; se omiten del JSON para `PRE`. **No existe `payment_debt_amount`.**
*   **`photo_url`:** ruta interna de la API (`/api/v1/students/{id}/photo/`), no una URL pública (RN-TRX-02).

#### GET `/api/v1/students/`
*   **Capacidad:** listado con búsqueda y filtros por nombre (sin acentos ni mayúsculas, RN-TRX-10), matrícula, grupo, grado y estatus; paginado (RF-EST-04). **Roles:** `ADM`, `PRE`, `PAD`. Aplica el mismo filtrado de campos que el detalle.

#### POST `/api/v1/students/`
*   **Capacidad:** crear un estudiante manualmente. **Roles:** `ADM`, `PAD`.
*   **Request:**
```json
{
  "enrollment_id": "...", "group_id": "uuid",
  "first_name": "...", "last_name_father": "...", "last_name_mother": null,
  "birth_date": null, "curp": null, "sex": null, "address": null,
  "blood_type": null, "allergies": null, "has_payment_debt": null, "pending_subjects": [],
  "guardians": [{
    "existing_guardian_id": null, "decline_match_reason": null,
    "first_name": "...", "last_name_father": "...", "last_name_mother": null,
    "email": "...", "phone_number": "...", "relationship": "MADRE", "is_primary_contact": true
  }]
}
```
*   **Response (201 Created):** el expediente creado (misma forma que el GET).
*   **Reglas (422):**
    *   **RN-EST-02:** `enrollment_id` único globalmente e inmutable (`DUPLICATE_ENROLLMENT`).
    *   **RN-EST-03 / RN-EST-11:** al menos un tutor con `is_valid_contact=true`; si no, no se guarda nada.
    *   **RN-EST-10:** si `birth_date` o la fotografía faltan, `completeness="INCOMPLETO"` con la lista de campos faltantes; si falta cualquier dato mínimo, no se guarda nada.
    *   **RN-EST-13:** si un tutor del arreglo coincide fuertemente (nombre completo y correo o teléfono) con un `GUARDIAN` existente y la solicitud no trae ni `existing_guardian_id` ni `decline_match_reason`, responde `422 GUARDIAN_MATCH_FOUND` con `details.candidates` para que la interfaz ofrezca reutilizar o declinar con motivo.
    *   **RN-TRX-08 / RN-TRX-09:** nombre en tres campos, longitud 2–60, caracteres permitidos, sin valores sustitutos.
    *   **RN-AUT-06:** `has_payment_debt` y `pending_subjects` solo los captura ADM/PAD.

#### POST `/api/v1/students/{id}/photo/` y GET `/api/v1/students/{id}/photo/`
*   Carga (multipart; `image/jpeg` o `image/png`; tamaño máximo configurable; se valida el tipo real por contenido y se eliminan metadatos EXIF) y descarga autenticada. Los archivos viven en el almacén privado (C4-04). **Roles:** carga `ADM`, `PAD`; lectura `ADM`, `PRE`, `PAD`. **Reglas:** RN-EST-10, RN-TRX-02.

---

### 2.5 Reportes de Incidencias (Módulo REP)

#### POST `/api/v1/reports/`
*   **Capacidad:** levantar un reporte. **Roles:** solo `DOC`.
*   **Request:** `{ "student_id": "uuid", "report_type_id": "uuid", "severity_id": "uuid", "preset_option_ids": ["uuid"], "observation": "...", "replaces_report_id": null }`
*   **Response (201 Created):** `{ "report_id": "uuid", "status": "REGISTRADO" }`
*   **Reglas (403 / 422):**
    *   **RN-REP-01:** `observation` de 50 a 100 caracteres inclusive (se cuenta después de recortar espacios).
    *   **RN-REP-09:** el alumno pertenece a un grupo en `TEACHER_GROUP_ASSIGNMENT` del docente.
    *   **RN-AST-30:** la cuenta está vinculada a un docente `ACTIVO`; si no, 422.
    *   **RN-EST-05:** el estudiante está `ACTIVO`.
    *   **RN-REP-02:** el tipo y la gravedad no se modifican después de enviarse; `preset_option_ids` deben corresponder al `report_type_id` y `severity_id`.
    *   **RN-REP-08:** `replaces_report_id` solo es válido si apunta a un reporte `RECHAZADO` del mismo docente y estudiante.
    *   **Ruteo (RN-REP-09):** el reporte llega a los prefectos asignados al grupo del estudiante (`PREFECT_GROUP_ASSIGNMENT`); si el grupo no tiene prefecto, queda en la bandeja de PAD y ADM con alerta.

#### GET `/api/v1/reports/`, GET `/api/v1/reports/{id}/`, GET `/api/v1/reports/{id}/history/`
*   Bandeja filtrable por tipo, gravedad, grupo, estudiante y estado; detalle; y trazabilidad (`REPORT_TRANSITION_LOG`). **Alcance por rol (RN-REP-05):** `ADM` y `PAD` todos; `PRE` los de sus grupos asignados; `DOC` solo los que registró; `SL` ninguno. Un reporte fuera del alcance responde **404**.

#### POST `/api/v1/reports/{id}/transitions/`
*   **Capacidad:** ejecutar una acción del flujo. **Sustituye al `PATCH /reports/{id}/` genérico**, que se elimina (RN-REP-02: no se edita un reporte ya enviado; la corrección es un reporte nuevo).
*   **Request:** `{ "action": "...", "reason": "...", "no_communication_reason": "..." }`
*   **Acciones y reglas (RN-REP-03/04/07/08); cualquier combinación no listada responde `422 INVALID_TRANSITION` sin importar lo que el cliente haya mostrado:**

| `action` | Desde → Hasta | Rol | Notas |
|---|---|---|---|
| `REVIEW` | `REGISTRADO → REVISADO_PREFECTO` | `PRE` (grupo asignado) | |
| `REJECT` | `REGISTRADO → RECHAZADO` | `PRE` (grupo asignado) | `reason` obligatorio. **Fin del flujo del original**; la corrección exige `POST /reports/` con `replaces_report_id`. Se notifica al docente autor (RN-REP-08). |
| `CHANNEL` | `REVISADO_PREFECTO → CANALIZADO` | `PRE` (grupo asignado) | |
| `ADMIN_REVIEW` | `CANALIZADO → REVISADO_ADMINISTRATIVO` | `PAD` | |
| `ADMIN_RETURN` | `CANALIZADO → REVISADO_PREFECTO` | `PAD` | `reason` obligatorio (rechazo administrativo: regresa al prefecto, no cierra, RN-REP-03). |
| `COMMUNICATE` | `REVISADO_ADMINISTRATIVO` o `AUTORIZADO` → (envío) | `PAD` | Valida contacto con correo y consentimiento (PP-05). Sin contacto válido con correo → `AUTORIZADO` (RN-REP-07). Con contacto: crea el `COMMUNICATION_LOG` y el worker lleva el reporte a `COMUNICADO` y `RESUELTO` al enviarse con éxito. |
| `RESOLVE_NO_COMMUNICATION` | `REVISADO_ADMINISTRATIVO → RESUELTO` | `PAD` | `no_communication_reason` obligatorio (RN-REP-07b). |

*   **Transiciones del sistema:** `COMUNICADO` y `RESUELTO` por envío `ENVIADO` (RN-REP-07a) las ejecuta el worker con `REPORT_TRANSITION_LOG.changed_by = NULL` (§7 I-04).
*   **RN-REP-06:** toda transición aceptada escribe un renglón en `REPORT_TRANSITION_LOG`. **RN-REP-04:** nunca `PRE` ni `DOC` pueden autorizar ni comunicar. **D-10:** si el grupo no tiene prefecto asignado, la etapa de prefecto no puede ejecutarla nadie hasta definirlo con la institución.

#### POST `/api/v1/reports/{id}/communications/`
*   **Capacidad:** comunicar a la familia (equivale a la acción `COMMUNICATE`). **Roles:** `PAD`. Incluye vista previa del contenido exacto antes del envío (`GET .../communications/preview/`, US-052). **Reglas:** RN-REP-04, RN-COM-01..04, RN-INF-02. Ver PP-05.

---

### 2.6 Importaciones Masivas (Módulo IMP)

#### POST `/api/v1/imports/upload/`
*   **Capacidad:** Subir archivo Excel para carga de alumnos.
*   **Request:** FormData con un archivo `.csv` o `.xlsx` y `group_id`.
*   **Response (200 OK):** `{ "batch_id": "uuid", "status": "VISTA_PREVIA", "total_rows": 45, "valid_rows": 40, "incomplete_rows": 3, "error_rows": 2, "warning_rows": 1 }`
*   **Reglas Validadas:**
    *   **RN-IMP-01 & RN-IMP-03:** Corre las validaciones de negocio en memoria, detecta repetidos (RN-EST-02) y genera filas en `IMPORT_ROW_ERROR`. No inserta en la base de datos de producción (RN-IMP-04).
    *   **RN-IMP-08:** Obliga a asignar el grupo, turno y ciclo a todo el bloque desde este momento.
    *   **RN-IMP-05:** solo ADM y PAD pueden llamar este endpoint (403 para los demás roles).
    *   **RN-IMP-06:** las filas con datos mínimos pero sin fecha de nacimiento o fotografía se cuentan aparte en la respuesta.
    *   **RN-IMP-01:** si la estructura del archivo no corresponde al diccionario, se rechaza completo con `422 IMPORT_INVALID_STRUCTURE`
    antes de procesar filas. **RN-IMP-09:** nombres en columnas separadas. **Seguridad:** se valida la extensión y el tipo real del contenido y un tamaño máximo; el archivo se guarda en el almacén privado y **no se interpreta como formulas ni macros**.

#### POST `/api/v1/imports/{batch_id}/confirm/`
*   **Capacidad:** Inyecta la vista previa a la base de datos real.
*   **Reglas Validadas:**
    *   **RN-IMP-04:** Verifica que el batch siga en estatus `VISTA_PREVIA` y realiza la inserción de las filas marcadas como limpias, omitiendo los errores irresolubles. Muta el estado a `CONFIRMADO`.
    *   **RN-IMP-07:** si al confirmar, la matrícula de una fila ya fue creada por otro proceso desde que se generó la vista previa, esa fila (y solo esa) se rechaza y se agrega a IMPORT_ROW_ERROR; el resto del lote se inserta con normalidad.
    *   **Mecanismo de staging:** al subir, el archivo se conserva en el almacén privado (con su SHA-256) asociado al lote. En `confirm` el servidor **vuelve a leer y a validar** el archivo (así detecta duplicados nuevos, RN-IMP-07) y solo entonces inserta. **Concurrencia:** `confirm` toma un bloqueo de fila del lote y cambia su estado `VISTA_PREVIA → CONFIRMADO` de forma atómica; una segunda llamada recibe 422. Inserción por fila, una fila fallida no detiene al resto (RF-IMP-01).
*   **Endpoints**: `GET /imports/template/` (plantilla, RF-IMP-02), `GET /imports/{batch_id}/` (estado y conteos), `GET /imports/{batch_id}/report/` (reporte descargable con totales y error por fila: columna y motivo, RF-IMP-01) y `POST /imports/{batch_id}/cancel/` (`VISTA_PREVIA → CANCELADO`, elimina el archivo temporal). **Roles de todos:** `ADM`, `PAD` (RN-IMP-05).


## 3. Contratos que faltaban

### 3.1 Asistencia del personal docente (Módulo AST)

#### POST `/api/v1/attendance/teachers/scan/`
*   **Capacidad:** registrar `ENTRADA` o `SALIDA` de un docente escaneando su QR (RF-AST-08).
*   **Roles:** solo `PAD` (RN-AST-10). Cualquier otro rol, incluido `ADM`, recibe 403.
*   **Request:** `{ "qr_token": "uuid", "record_type": "ENTRADA|SALIDA", "client_event_id": "uuid" }`. El PAD elige el tipo manualmente (RN-AST-12). La hora efectiva es la del servidor (RN-TRX-04).
*   **Respuestas:**
    *   `201 Created` — `{ "result": "REGISTRADO", "attendance_id": "...", "record_type": "ENTRADA", "status": "ASISTIO|LLEGO_TARDE", "effective_datetime": "...", "anomaly_flag": "NINGUNA" }`. Para `ENTRADA`, el estado se calcula con el límite del día: `expected_entry_time + tolerancia` (RN-AST-14/19). Para `SALIDA`, `status` es nulo y se conserva la hora efectiva (RN-AST-20).
    *   `201 Created` con `anomaly_flag: "SALIDA_SIN_ENTRADA"` si se registra una `SALIDA` sin `ENTRADA` válida ese día (RN-AST-25); se asigna en este mismo momento (PP-03). Un `FALTÓ` automático no cuenta como `ENTRADA`.
    *   `200 OK` — `{ "result": "RECLASIFICADO", "previous_status": "FALTO", "status": "ASISTIO|LLEGO_TARDE" }`: si el docente tenía `FALTÓ` automático ese día, la `ENTRADA` **actualiza ese mismo renglón** y no cuenta como segunda entrada (RN-AST-13/24). Un `FALTÓ` justificado manualmente no se reclasifica.
*   **Errores (422):** `QR_NOT_RECOGNIZED` (inexistente, revocado o de otro tipo de entidad, RN-AST-11, RN-QR-06); `QR_REVOKED`; `TEACHER_NOT_ACTIVE` (docente `INACTIVO`; el QR **no** se marca revocado, RN-AST-23/29, CA-060-04); `DUPLICATE_RECORD` (segunda `ENTRADA` o segunda `SALIDA` del mismo día, RN-AST-13/16).
*   **Pendiente (D-13):** `ENTRADA` en un día sin asistencia programada.

### 3.2 Docentes (Módulo AST / `teachers`)

| Método y ruta | Roles | Reglas |
|---|---|---|
| `GET /teachers/` (búsqueda por nombre, identificador y estatus, paginado) | ADM, PAD | RF-AST-12, RN-TRX-10 |
| `POST /teachers/` | ADM, PAD | RF-AST-11, RN-AST-26/27, RN-TRX-08/09 (identificador único incluso frente a inactivos, inmutable) |
| `GET /teachers/{id}/` (ficha, estado del QR, programación, acceso a historial) | ADM, PAD | RF-AST-12 |
| `PATCH /teachers/{id}/` | ADM, PAD | RN-AST-26 (identificador inmutable), RN-AUT-05 |
| `POST /teachers/{id}/deactivate/` (motivo obligatorio) | ADM, PAD | RN-AST-28/29 |
| `POST /teachers/{id}/reactivate/` (motivo obligatorio) | ADM | RN-AST-28 |
| `PUT /teachers/{id}/schedule/` | ADM, PAD | RF-AST-09, RN-AST-14/18/19 |
| `POST /users/{user_id}/link-teacher/` | ADM | RN-AST-30 (1 a 1) |
| `GET /teachers/{id}/attendance/?from=&to=` | ADM, PAD | RF-AST-10, RN-AST-21 |

### 3.3 Asistencia estudiantil: consulta e información consolidada

| Método y ruta | Roles | Reglas |
|---|---|---|
| `GET /attendance/students/?group_id=&date=` | ADM, PRE, PAD | RF-AST-04 |
| `GET /attendance/students/history/?student_id=` | ADM, PRE, PAD | RF-AST-05 |
| `GET /attendance/summary/` (por estudiante, grupo y periodo; exportable) | ADM, PAD, SL | RF-AST-07, US-037 |
| `POST /attendance/students/sync/` | PRE, PAD | API-01 |

### 3.4 Estudiantes y tutores

| Método y ruta | Roles | Reglas |
|---|---|---|
| `PATCH /students/{id}/` | ADM, PAD | RN-EST-02 (matrícula inmutable; corrección excepcional con motivo), RN-EST-14 |
| `POST /students/{id}/status/` (`BAJA`, `EGRESADO`) | ADM, PAD | RF-EST-02, RN-EST-04/09 |
| `POST /students/{id}/reinstate/` (`BAJA → ACTIVO`) | ADM | RN-EST-06, RN-EST-09 (`EGRESADO` es final) |
| `POST /students/{id}/guardians/` | ADM, PAD | RN-EST-03/11/13 |
| `PATCH /guardians/{id}/` (si el tutor es compartido, la primera llamada devuelve la lista de estudiantes afectados y requiere reenviar con `confirm=true`) | ADM, PAD | RN-EST-14, Modelo §3.5 |
| `POST /guardians/{id}/split/` | ADM, PAD | RF-EST-07, RN-EST-13 |
| `POST /student-guardians/{id}/invalidate-contact/` (motivo) | ADM, PAD | RN-EST-11 |
| `PATCH /student-guardians/{id}/consent/` | ADM, PAD | RN-EST-07, `GUARDIAN_CONSENT_LOG` |

### 3.5 Comunicaciones (Módulo COM)

| Método y ruta | Roles | Reglas |
|---|---|---|
| `POST /reports/{id}/communications/` | PAD | API-06, PP-05 |
| `GET /communications/?status=&report_id=` | ADM, PAD | RN-COM-03 |
| `POST /communications/{id}/retry/` | PAD (ADM según D-06) | RN-COM-03, CA-053-02/03 |

### 3.6 Administración y operación (Módulo ADM / `ops`)

| Método y ruta | Roles | Reglas |
|---|---|---|
| `GET /settings/parameters/` y `PATCH /settings/parameters/{key}/` | ADM | RN-ADM-02, RF-ADM-02 (valida la restricción de horas en ambos sentidos, no retroactivo, auditado) |
| `GET/POST/PATCH /catalogs/groups/` y `/catalogs/cycles/` (se desactivan, no se eliminan) | ADM | RN-ADM-01, RN-TRX-03 |
| `GET/POST /assignments/prefect-groups/` y `/assignments/teacher-groups/` | ADM | RN-ADM-01, RN-REP-09, Modelo §3.6 |
| `GET /reports/presets/?report_type_id=&severity_id=` (solo lectura) | DOC | RN-ADM-03: `REPORT_*` no tienen escritura para ningún rol |
| `GET /audit-log/` | ADM | RF-AUT-05 |
| `GET /ops/backups/` (último respaldo: fecha, resultado, tamaño, alertas) | ADM | RN-API-03, US-057 |
| `GET /dashboard/` | ADM, SL | RF-ADM-03, CA-056-03 |
| `GET /system/status/` | cualquier usuario autenticado | C4-09: `server_time`, `database`, `internet`, `smtp`, `last_backup` |

### 3.7 Cuentas (Módulo AUT)

| Método y ruta | Roles | Reglas |
|---|---|---|
| `GET/POST /users/`, `PATCH /users/{id}/` (nombre, rol) | ADM | RF-AUT-03, RN-AUT-01, RN-TRX-08 |
| `POST /users/{id}/deactivate/` (invalida todas sus sesiones) | ADM | US-004, CA-004-01 |
| `POST /users/{id}/unlock/` | ADM | RN-AUT-03, CA-002 |