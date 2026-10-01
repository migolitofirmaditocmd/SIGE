# SIGE — Documento de Seguridad y Autenticación
**Sistema Integral de Gestión Escolar**

**Versión:** 2.0 | **Estado:** Para revisión del equipo
**Derivado de:** Acta v10 · RF/RNF v3 · RN v3 · HU v2 · CA v2 · Modelo de Datos v3.0


Este documento detalla los mecanismos de seguridad, políticas de control de acceso y estrategias de autenticación implementadas en SIGE para garantizar la confidencialidad, integridad y disponibilidad de la información de la comunidad escolar.

---
## 1. Estrategia de Autenticación: JWT de acceso + sesión revocable
SIGE usa un token de acceso JWT de vida corta y un token de renovación **con estado** persistido en `USER_SESSION` (RF-AUT-01). Solo el token de acceso es sin estado.

*   **Access Token (15 minutos).** JWT firmado enviado en `Authorization: Bearer <token>`. Claims: `sub` (id de usuario), `sid` (id de `USER_SESSION`), `iat`, `exp`. **El backend no autoriza con ningún rol contenido en el token:** en cada petición carga de la BD `USER.role`, `USER.is_active` y verifica que `USER_SESSION.revoked_at IS NULL` (RN-API-01). Así la desactivación de una cuenta o un cambio de rol tienen efecto inmediato, no a los 15 minutos (US-004). El token vencido se rechaza con 401 aunque el refresh siga vigente (RN-AUT-04).
*   **Refresh Token (opaco, con estado).** Cadena aleatoria criptográfica (`secrets.token_urlsafe(48)`), **no JWT**. En BD solo se guarda su hash (`USER_SESSION.refresh_token_hash`, UNIQUE).
*   **Vigencia (D-08):** expiración deslizante de 24 horas con tope absoluto de 7 días desde el inicio de sesión (`USER_SESSION.absolute_expires_at`, ver §7 I-05). Superado el tope, se exige iniciar sesión de nuevo.
*   **Rotación y detección de reutilización:** cada llamada a `POST /api/v1/auth/refresh/` revoca la sesión usada (`revoked_reason='ROTATED'`) y emite una nueva con el mismo tope absoluto. Si llega un refresh ya rotado, se asume robo: se revocan todas las sesiones vigentes del usuario (`revoked_reason='REUSE_DETECTED'`) y se audita.
*   **Almacenamiento:** el refresh vive **únicamente** en una cookie `HttpOnly; Secure; SameSite=Strict; Path=/api/v1/auth/`. Nunca en el cuerpo de la respuesta, `localStorage` ni `IndexedDB`. El access token vive solo en memoria de la aplicación. El frontend y la API se sirven bajo el mismo origen mediante el proxy inverso (§5), por lo que no hay CORS en producción.
*   **Invalidación:** cierre de sesión, desactivación de cuenta (todas las sesiones, US-004), restablecimiento de contraseña completado (CA-005-05), cambio de rol por Administrador y detección de reutilización marcan `revoked_at` y `revoked_reason`.
---

## 2. Política de Bloqueo de Seguridad (RN-AUT-03)
Para prevenir ataques de fuerza bruta sobre las cuentas del personal:

1.  **Umbral:** `OPERATIONAL_PARAMETER['ACCOUNT_LOCKOUT_MAX_ATTEMPTS']` (5 por defecto, configurable) intentos fallidos consecutivos.
2.  **Mecanismo:** cada fallo incrementa `USER.failed_login_attempts`. Al alcanzar el umbral se estampa `USER.locked_until = ahora + ACCOUNT_LOCKOUT_DURATION_MINUTES` (15 por defecto, configurable) y se registra en `AUDIT_LOG`.
3.  **Durante el bloqueo** se rechaza el acceso aunque la contraseña sea correcta y se informa el tiempo restante.
4.  **Reinicio del contador:** un inicio de sesión exitoso, el vencimiento de `locked_until` y el desbloqueo manual ponen `failed_login_attempts = 0`.
5.  **Desbloqueo manual:** solo el Administrador (endpoint `POST /api/v1/users/{id}/unlock/`), con registro en `AUDIT_LOG`.
6.  **Anti-enumeración:** el conteo de intentos y el bloqueo se aplican **por nombre de usuario recibido, exista o no** (contador en caché/BD indexado por `username`), de modo que un usuario inexistente produce exactamente la misma secuencia de respuestas (mismo mensaje, mismo código y mismo tiempo de espera) que uno real.
7.  **Límite por origen:** además, rate limiting por IP en `/auth/*` (DRF throttling) que responde 429 con `Retry-After`.
8.  **Administrador bloqueado:** existe un procedimiento documentado de desbloqueo por consola del servidor (`manage.py`) para el caso en que el Administrador sea quien quedó bloqueado, ya que el desbloqueo por la aplicación solo lo realiza un Administrador.

---

## 3. Matriz RBAC (espejo de RN-AUT-06)
La fuente única de verdad es **RN-AUT-06**. Esta tabla la refleja con mayor granularidad; si difieren, prevalece RN-AUT-06 y este documento debe corregirse. Toda fila se aplica en el backend (RN-API-01, RN-AUT-02), nunca solo en la interfaz.

| Módulo / Capacidad | Administrador | Prefecto | Docente | P. Administrativo | Solo Lectura |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **AUT:** Cuentas (alta, desactivar, reasignar rol), resetear claves, desbloquear | ✅ | ❌ | ❌ | ❌ | ❌ |
| **ADM:** Parámetros operativos, catálogos editables (grupos, grados, ciclos), asignaciones prefecto–grupo y docente–grupo | ✅ | ❌ | ❌ | ❌ | ❌ |
| **ADM:** Tipos/gravedad/opciones de reporte (`REPORT_*`) | ❌ (catálogo fijo, RN-ADM-03) | ❌ | ❌ | ❌ | ❌ |
| **ADM:** Bitácora de auditoría · respaldo y restauración | ✅ | ❌ | ❌ | ❌ | ❌ |
| **EST:** Alta, edición y cambio de estatus (`BAJA`/`EGRESADO`) de estudiantes, tutores y consentimiento | ✅ | ❌ | ❌ | ✅ | ❌ |
| **EST:** Reingreso (`BAJA → ACTIVO`) y corrección de `EGRESADO` | ✅ | ❌ | ❌ | ❌ | ❌ |
| **EST:** Consultar expediente (datos generales) | ✅ | ✅ | ❌ | ✅ | ❌ |
| **EST:** Datos de salud (tipo de sangre, alergias) | ✅ | ✅ | ❌ | ✅ | ❌ |
| **EST:** Adeudo de pago / materias pendientes | ✅ | ❌ | ❌ | ✅ | ❌ |
| **IMP:** Importación masiva (incluye plantilla y reporte) | ✅ | ❌ | ❌ | ✅ | ❌ |
| **QR:** Emitir QR (alta inicial, estudiante o docente) | ✅ | ❌ | ❌ | ✅ | ❌ |
| **QR:** Revocar y regenerar QR | ✅ | ❌ | ❌ | ❌ | ❌ |
| **CRE:** Exportar credenciales / stickers | ✅ | ❌ | ❌ | ✅ | ❌ |
| **AST:** Escanear asistencia estudiantil | ❌ | ✅ | ❌ | ✅ | ❌ |
| **AST:** Consultar asistencia detallada (grupo / estudiante) | ✅ | ✅ | ❌ | ✅ | ❌ |
| **AST:** Justificar / modificar asistencia (estudiantil y docente) | ✅ | ❌ | ❌ | ✅ | ❌ |
| **AST:** Alta, edición y desactivación de docentes · programación · fichas e historial docente | ✅ | ❌ | ❌ | ✅ | ❌ |
| **AST:** Reactivar docente · vincular docente con cuenta | ✅ | ❌ | ❌ | ❌ | ❌ |
| **AST:** Registrar entrada/salida de docente | ❌ | ❌ | ❌ | ✅ | ❌ |
| **REP:** Registrar un reporte nuevo | ❌ | ❌ | ✅ (solo grupos asignados, con ficha de docente `ACTIVO` vinculada) | ❌ | ❌ |
| **REP:** Consultar reportes | ✅ (todos) | ✅ (sus grupos asignados) | ✅ (solo los que registró) | ✅ (todos) | ❌ |
| **REP:** Revisar / canalizar (etapa Prefecto) | ❌ | ✅ | ❌ | ❌ | ❌ |
| **REP:** Revisión administrativa, autorizar y enviar comunicación a familia | ❌ | ❌ | ❌ | ✅ | ❌ |
| **COM:** Reintentar envío de correo fallido | ❌ *(D-06)* | ❌ | ❌ | ✅ | ❌ |
| **Información consolidada de asistencia** | ✅ | ❌ | ❌ | ✅ | ✅ |
| **Panel de indicadores (RF-ADM-03)** | ✅ | ❌ | ❌ | ❌ | ✅ |
---

## 4. Checklist de controles de seguridad (referencia OWASP ASVS Nivel 1–2)
**Estado:** `[ ]` planificado · `[~]` implementado sin prueba · `[x]` implementado **y** verificado por una prueba automatizada o manual documentada. Ningún control se marca `[x]` antes de su prueba. **Versión de ASVS de referencia:** definir (p. ej. 4.0.3) y **verificar cada identificador** contra el texto oficial antes de citarlo; mientras no se verifique se cita solo el capítulo (V2 Autenticación, V3 Sesión, V4 Control de acceso, V5 Validación, V6 Criptografía, V8 Protección de datos, V9 Comunicaciones, V11 Lógica de negocio).

### 4.1 Endpoints de autenticación (`/auth/*`) — ASVS V2, V3
- [ ] Contraseñas con hash fuerte y sal (PBKDF2 o Argon2 de Django) · RNF-SEG-03.
- [ ] Mensajes y tiempos de respuesta uniformes ante usuario inexistente, contraseña errónea y cuenta bloqueada (anti-enumeración, SG-02 punto 6) · CA-001, CA-005-02.
- [ ] Bloqueo temporal y rate limiting · RN-AUT-03, CA-002.
- [ ] Refresh con rotación, detección de reutilización e invalidación al cerrar sesión/desactivar/restablecer · RF-AUT-01, CA-001-06, CA-004-01, CA-005-05.
- [ ] Tokens fuera de la URL; refresh solo en cookie HttpOnly · SG-01.

### 4.2 Endpoints de asistencia estudiantil (`/attendance/students/*`) — ASVS V4, V11
- [ ] Autorización por rol en cada operación (escanear: PRE/PAD; justificar/modificar: ADM/PAD) · RN-AST-04, CA-027-07.
- [ ] Hora efectiva calculada por el backend (servidor si es en línea; captura corregida si es offline), rechazo de horas futuras, límite de antigüedad de eventos offline y desfase razonable del reloj · RN-TRX-04, RNF-FIA-04, SG-09.
- [ ] Un registro oficial por estudiante y día (restricción única) · Modelo §4.

### 4.3 Endpoints de reportes y comunicaciones (`/reports/*`, `/communications/*`) — ASVS V4, V8
- [ ] Un Docente solo registra reportes de estudiantes `ACTIVO` en grupos de `TEACHER_GROUP_ASSIGNMENT` y desde una cuenta vinculada a un docente `ACTIVO` · RN-REP-09, RN-AST-30.
- [ ] Un Prefecto solo ve y opera reportes de grupos de `PREFECT_GROUP_ASSIGNMENT`; un Docente solo los suyos; un recurso no visible responde **404**, no 403 (no revelar su existencia) · RN-REP-05.
- [ ] Transiciones de estado validadas por rol y estado en el servidor · RN-REP-03/04.
- [ ] Ningún correo sale sin autorización de PAD ni hacia un tutor con consentimiento `REVOCADO` o sin correo · RN-REP-04, RN-COM-01/04.

### 4.4 Endpoints de estudiantes y datos de menores (`/students/*` y todo endpoint que anide datos del estudiante) — ASVS V4, V8
- [ ] **Acceso al endpoint:** `GET /students/{id}/` y el listado solo para ADM, PRE y PAD; Docente y Solo lectura reciben 403 (US-011, RN-AUT-06).
- [ ] **Filtrado por rol en un serializador central único** (RN-EST-12): `blood_type` y `allergies` visibles para ADM, PRE y PAD; `has_payment_debt` y `pending_subjects` solo para ADM y PAD (se **omiten** del JSON para PRE). No existe campo de monto de adeudo (RN-EST-12, RN-TRX-01).
- [ ] **El mismo filtrado aplica a todo lugar donde viajen esos datos:** objetos de estudiante anidados en reportes, asistencia y comunicaciones; archivos exportados (credenciales, consolidados, reportes de importación); y visualización de `AUDIT_LOG`, cuyo contenido `previous_value`/`new_value` solo ve el Administrador.
- [ ] **Tutores (RN-TRX-06):** los datos del tutor (`GUARDIAN`, `STUDENT_GUARDIAN`) heredan las mismas restricciones de acceso del expediente.
- [ ] **Fotografías:** no se sirven como URL pública; se entregan por un endpoint autenticado que valida rol (RN-TRX-02).
- [ ] **Trazas y errores:** los registros de aplicación y los mensajes de error no incluyen datos de salud, adeudos ni datos de contacto.

### 4.5 Endpoints de credenciales QR (`/credentials/*`) — ASVS V6
- [ ] Token UUIDv4 generado con el CSPRNG del sistema operativo, único contra vigentes y revocados · RN-QR-02/03, CA-022-04.
- [ ] Un QR revocado se rechaza al escanear · RN-QR-04. *(Esto no protege contra la copia de un QR vigente; ver SG-06.)*
- **Limitación aceptada:** el QR es un identificador estático; su copia no puede detectarse criptográficamente. Mitigaciones: (1) la API devuelve nombre, grupo y fotografía del estudiante al operador para verificación visual en la entrada (US-027, UX); (2) la ventana de rebote evita escaneos repetidos (RN-AST-02); (3) revocación inmediata ante pérdida o robo (RN-QR-04). No se firma el token: la validez se resuelve únicamente consultando la BD (RN-QR-02, RNF-SEG-02).

## 5. Seguridad de transporte y red local (RNF-SEG-01)
*   **Terminación TLS en el proxy inverso** (Nginx o Caddy) con TLS 1.2 como mínimo. Es el único puerto expuesto a la red local (443); HTTP (80) solo redirige. Django corre con `SECURE_PROXY_SSL_HEADER`, `SESSION/CSRF cookies Secure` y `SECURE_HSTS_SECONDS` activo una vez validado el certificado.
*   **Certificado (D-09):** Let's Encrypt no es viable sin Internet ni dominio público. Se usa una **CA interna del proyecto** (por ejemplo, `mkcert` o `step-ca`) que emite el certificado del servidor para un nombre local fijo (p. ej. `sige.<escuela>.local`) y una dirección IP reservada en el router. El certificado raíz de la CA se instala y marca como confiable en cada dispositivo (PCs y celulares).
*   **Riesgo operativo:** instalar y confiar una CA en iOS y Android tiene pasos específicos y es el principal obstáculo para que la PWA funcione. Debe incluirse en las pruebas de RNF-COM-02 (dispositivos soportados) y en la guía de despliegue (RNF-POR-01), junto con el calendario de renovación del certificado.
*   **Servicios internos:** PostgreSQL, Redis (si aplica) y el servidor de aplicación escuchan solo en `127.0.0.1` o socket Unix. El firewall del servidor permite únicamente 443 desde la LAN. No hay acceso remoto desde Internet en esta fase (Acta, sección Infraestructura).

## 6. Contraseñas y recuperación de acceso (RNF-SEG-03, RF-AUT-04)
### 6.1 Política de contraseñas
*   Longitud mínima y complejidad **configurables** (`PASSWORD_MIN_LENGTH`, 10 por defecto, y reglas de complejidad en `OPERATIONAL_PARAMETER`; ver §7 I-01), validadas en el servidor con los validadores de contraseña de Django.
*   Hash con Argon2 (o PBKDF2 de Django); nunca se registran ni devuelven contraseñas.

### 6.2 Restablecimiento mediante enlace
1.  El usuario solicita el enlace con su correo institucional. La respuesta es **idéntica exista o no la cuenta** y no se envía correo si no existe (CA-005-02).
2.  Se genera un token aleatorio (`secrets.token_urlsafe(32)`); en BD solo se guarda su hash en `PASSWORD_RESET_TOKEN`. Vigencia: `OPERATIONAL_PARAMETER['PASSWORD_RESET_EXPIRY_MINUTES']` (30 por defecto).
3.  Al emitir uno nuevo, todo enlace previo vigente del mismo usuario se invalida (`invalidated_at`) en la misma operación (RN-AUT-07, CA-005-07/08).
4.  El enlace se acepta solo si `used_at IS NULL AND invalidated_at IS NULL AND expires_at > ahora` (CA-005-03/04).
5.  Al completarse, se marca `used_at` y se revocan todas las `USER_SESSION` del usuario (`revoked_reason='PASSWORD_RESET'`, CA-005-05).
6.  **Sin Internet** el correo no sale (RN-INF-02): la interfaz informa que el servicio de correo no está disponible y que puede pedir apoyo al Administrador (CA-005-06), quien restablece la contraseña desde la gestión de cuentas.

## 7. Buffer offline y confianza en la hora del dispositivo (RN-MOV-02, RN-TRX-04)
*   **Contenido permitido del buffer (IndexedDB de la PWA):** únicamente `client_event_id` (UUID generado en el dispositivo), `qr_token`, `captured_at`, `clock_offset_ms`, `event_type` y el `user_id` del operador que capturó. **Ningún dato personal** del estudiante (RN-MOV-02). Máximo 1,000 eventos; con el buffer lleno se rechaza el nuevo y se alerta (RN-MOV-03).
*   **`clock_offset_ms`:** desfase entre el reloj del dispositivo y la hora del servidor medido en la última conexión (el servidor entrega su hora en `GET /api/v1/system/status/`, C4-09). La hora efectiva es `captured_at` corregida con ese desfase (RN-TRX-04, RNF-FIA-04).
*   **Validaciones del backend al sincronizar:** (1) se rechaza un evento con hora efectiva posterior al reloj del servidor más una tolerancia pequeña (RN-TRX-04); (2) se descartan con motivo los eventos con antigüedad mayor a `OFFLINE_MAX_AGE_HOURS` (72 por defecto, D-11); (3) se marcan para revisión los eventos con `|clock_offset_ms|` mayor a 5 minutos; (4) el `scanned_by` es el operador que capturó (`user_id` del buffer), validando que conserve rol PRE/PAD y cuenta activa al sincronizar.
*   **Ciclo de vida del buffer:** un evento solo se elimina del dispositivo cuando el servidor confirma su procesamiento (aceptado o descartado con motivo). Cerrar sesión con eventos pendientes advierte al operador y no los borra. Si el refresh venció durante la desconexión, el operador debe iniciar sesión de nuevo antes de sincronizar y los eventos se conservan.

## 8. Servidor, secretos y auditoría
*   **Secretos** (`SECRET_KEY`, credenciales de BD y SMTP, llave de firma JWT) fuera del repositorio Git (RNF-MAN-01), en un archivo de entorno con permisos `0600` propiedad del usuario de servicio. `DEBUG=False` en producción. Cada despliegue documenta cómo regenerar secretos (RNF-POR-01).
*   **Cuentas y acceso al servidor:** usuario del sistema dedicado para SIGE sin privilegios de administrador; acceso físico y de consola restringido al equipo técnico y al Administrador (Acta, "control de acceso al servidor"); actualizaciones de seguridad del sistema operativo programadas.
*   **Base de datos:** el rol de PostgreSQL de la aplicación no tiene `DELETE` sobre `AUDIT_LOG`, `ATTENDANCE_*`, `INCIDENT_REPORT` ni `REPORT_TRANSITION_LOG`, y solo `INSERT` sobre `AUDIT_LOG` (Modelo §3.13 y §4; RN-TRX-03).
*   **Bitácora (RF-AUT-05):** se registran inicios de sesión exitosos y fallidos (con IP y agente de usuario en el valor nuevo), bloqueos y desbloqueos, cambios de rol, restablecimientos de contraseña, modificaciones de asistencia, de reportes, de parámetros y de estatus de estudiante o docente, y las corridas de los procesos programados (`user_id = NULL`, PP-01).
*   **Respaldos:** contienen datos de menores; ver PP-04 (permisos `0600`, copia externa cifrada y solo con autorización institucional).

