# SIGE — Diagramas de Secuencia por Módulo
### Sistema Integral de Gestión Escolar

**Versión:** 1.1 | **Estado:** Para revisión del equipo
**Derivado de:** Reglas de Negocio v3 · Especificación de Requisitos v3 · Especificación de API REST v2 · Seguridad y Autenticación v2 · Estrategia de Procesos Programados v2 · Arquitectura C4 v2 · Criterios de Aceptación v2 (CA-057) · Estrategia de Migraciones

---

## 0. Cómo leer este documento

Este documento reúne los diagramas de secuencia que faltaban para los 13 flujos principales de SIGE. Cada diagrama está escrito en **Mermaid** (`sequenceDiagram`) y se acompaña de las reglas y contratos que lo gobiernan.

### 0.1 Convenciones

| Convención | Significado |
|---|---|
| **Roles** | `ADM` Administrador/Directivo · `PRE` Prefecto · `DOC` Docente · `PAD` Personal administrativo · `SL` Solo lectura (matriz RN-AUT-06). |
| **Cliente** | "PWA / Web" es la aplicación Next.js. Toda llamada viaja por HTTPS a través del proxy inverso (Nginx o Caddy); el proxy no se dibuja para no saturar los diagramas. |
| **Validación de acceso** | Toda petición autenticada valida el JWT, carga `USER.role` y `USER.is_active` desde la BD y comprueba que `USER_SESSION.revoked_at` sea nulo (Seguridad §1). En los diagramas aparece como un solo paso: *"Valida JWT, sesión y rol"*. |
| **Errores** | Formato uniforme `{error_code, message, details, rn_reference, trace_id}` (RF-API-04). 401 credenciales o token, 403 rol sin permiso, 404 recurso fuera de alcance, 422 regla de negocio, 429 bloqueo o rate limit. |
| **Resultados no erróneos** | Un escaneo ignorado por rebote, un evento adicional y una reclasificación **no son errores**: se responden con 200 y un campo `result`. |
| **Valores de estado** | Se escriben como en la API: `ASISTIO`, `LLEGO_TARDE`, `FALTO`, `FALTA_JUSTIFICADA`; origen `ESCANEO`, `AUTOMATICO` o `MANUAL`. |
| **Auditoría** | `AUDIT_LOG` es de solo inserción (RN-AUT-05). Los jobs escriben con `user_id = NULL`. |

### 0.2 Índice

| # | Diagrama | Módulo | Reglas principales |
|---|---|---|---|
| 4.1 | Autenticación, renovación de token y bloqueo por intentos fallidos | AUT | RN-AUT-03, RN-AUT-04, RN-AUT-05 |
| 4.2 | Importación masiva de estudiantes | IMP / EST | RN-IMP-01 a RN-IMP-10 |
| 4.3 | Alta manual, edición y registro incompleto de estudiante | EST | RN-EST-02, 03, 10, 11, 13, 14 |
| 4.4 | Generación, revocación y exportación de QR (estudiante y docente) | QR / CRE | RN-QR-01 a RN-QR-06, RN-CRE-01 |
| 4.5 | Escaneo de asistencia estudiantil con reclasificación | AST | RN-AST-01 a RN-AST-09 |
| 4.6 | Verificación automática de ausencias (estudiantes y docentes) | AST / jobs | RN-AST-08, 15, 18, 24; RN-ADM-02 |
| 4.7 | Captura y sincronización offline | AST / MOV | RN-MOV-02, RN-MOV-03, RN-TRX-04 |
| 4.8 | Alta, edición, desactivación y reactivación de la ficha docente | AST (`teachers`) | RN-AST-23, 26 a 30 |
| 4.9 | Registro de asistencia docente (entrada y salida) | AST | RN-AST-10 a 25 |
| 4.10 | Flujo completo de un reporte escolar | REP | RN-REP-01 a RN-REP-09 |
| 4.11 | Envío de comunicación por correo con reintento | COM | RN-COM-01 a RN-COM-04, RN-INF-02 |
| 4.12 | Justificación y modificación de asistencia con auditoría | AST | RN-AST-04, 05, 06, 17, 22 |
| 4.13 | Respaldo y restauración de la base de datos | ADM / `ops` | RN-API-03, RN-INF-03, RF-API-03 |

---

## 4.1 Autenticación, renovación de token y bloqueo por intentos fallidos

**Módulo:** AUT · **Endpoints:** `POST /auth/login/`, `POST /auth/refresh/`, `POST /auth/logout/`, `POST /users/{id}/unlock/`
**Idea central:** access token JWT de 15 minutos (sin estado) + refresh token opaco con estado en `USER_SESSION`, rotado en cada renovación. El bloqueo se cuenta **por nombre de usuario recibido, exista o no**, para no revelar qué cuentas existen.

### 4.1.1 Inicio de sesión y bloqueo por intentos fallidos

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    participant W as PWA / Web
    participant A as API · AUT
    participant DB as PostgreSQL

    U->>W: Captura usuario y contraseña
    W->>A: POST /api/v1/auth/login/ {username, password}
    A->>A: Rate limiting por IP en /auth/* (DRF throttling)
    alt La IP excede el límite
        A-->>W: 429 RATE_LIMITED + Retry-After
    else Dentro del límite
        A->>DB: Consulta failed_login_attempts y locked_until por username recibido (exista o no)
        DB-->>A: Contador y locked_until
        alt locked_until es posterior a ahora
            Note over A: Se rechaza aunque la contraseña sea correcta (RN-AUT-03)
            A-->>W: 429 ACCOUNT_LOCKED + Retry-After con el tiempo restante
        else Sin bloqueo vigente
            A->>A: Verifica contraseña (Argon2 o PBKDF2) con tiempo de respuesta uniforme
            alt Contraseña incorrecta o usuario inexistente
                A->>DB: failed_login_attempts + 1 y AUDIT_LOG (login fallido con IP y agente)
                alt Intentos alcanzan ACCOUNT_LOCKOUT_MAX_ATTEMPTS (5)
                    A->>DB: locked_until = ahora + ACCOUNT_LOCKOUT_DURATION_MINUTES (15) y AUDIT_LOG (bloqueo)
                    A-->>W: 429 ACCOUNT_LOCKED + Retry-After
                else Intentos por debajo del umbral
                    A-->>W: 401 INVALID_CREDENTIALS (idéntica exista o no el usuario)
                end
            else Contraseña correcta
                alt USER.is_active es falso
                    A-->>W: 403 ACCOUNT_DISABLED (solo se revela con credenciales correctas)
                else Cuenta activa
                    A->>DB: failed_login_attempts = 0
                    A->>DB: INSERT USER_SESSION (hash del refresh, absolute_expires_at = inicio + 7 días)
                    A->>DB: AUDIT_LOG (login exitoso con IP y agente)
                    A-->>W: 200 {access JWT, expires_in 900, user} + Set-Cookie refresh HttpOnly Secure SameSite=Strict
                    W->>W: Guarda el access solo en memoria (nunca localStorage ni IndexedDB)
                end
            end
        end
    end
```

**Reglas y contratos:** RN-AUT-01, RN-AUT-03, RN-AUT-05, RF-AUT-01, RF-AUT-03, SG-01, SG-02. EEl contador se reinicia con un login exitoso, al vencer `locked_until` o por desbloqueo manual. El intento que alcanza el umbral ya responde `429 ACCOUNT_LOCKED` (CA-002-01); los intentos previos responden `401 INVALID_CREDENTIALS`.

### 4.1.2 Uso del access token, renovación con rotación y detección de reutilización

```mermaid
sequenceDiagram
    autonumber
    participant W as PWA / Web
    participant A as API · AUT
    participant DB as PostgreSQL

    W->>A: Petición con Authorization Bearer access
    A->>A: Valida firma y exp del JWT (claims sub, sid, iat, exp)
    alt Access token vencido
        A-->>W: 401 TOKEN_EXPIRED (RN-AUT-04)
        W->>A: POST /api/v1/auth/refresh/ (cookie refresh)
        A->>DB: Busca USER_SESSION por hash del refresh
        alt Refresh ya rotado (reutilización, se asume robo)
            A->>DB: Revoca todas las sesiones vigentes del usuario (REUSE_DETECTED) y AUDIT_LOG
            A-->>W: 401 TOKEN_EXPIRED y borra la cookie
            W->>W: Redirige al inicio de sesión
        else Refresh vencido (24 h deslizante o tope de 7 días) o revocado
            A-->>W: 401 TOKEN_EXPIRED
            W->>W: Redirige al inicio de sesión (los eventos offline pendientes se conservan)
        else Refresh vigente
            A->>DB: Revoca la sesión usada (ROTATED) e inserta nueva USER_SESSION con el mismo tope absoluto
            A-->>W: 200 {access, expires_in 900} + nueva cookie refresh
            W->>A: Reintenta la petición original con el nuevo access
        end
    else Access token vigente
        A->>DB: Carga USER.role, USER.is_active y USER_SESSION.revoked_at (sid)
        alt Sesión revocada o cuenta desactivada
            A-->>W: 401 SESSION_REVOKED (efecto inmediato, no espera a los 15 minutos)
            W->>W: Descarta el access y redirige al inicio de sesión sin intentar renovar
        else Sesión válida
            A->>A: Autoriza con el rol cargado de la BD, no con el del token (RN-AUT-06)
            A-->>W: Respuesta de la operación
        end
    end
```

**Reglas y contratos:** RN-AUT-04, RF-AUT-01, US-004, CA-004-07, SG-01, D-08. Las sesiones también se revocan por logout, desactivación de cuenta, restablecimiento de contraseña y cambio de rol.

### 4.1.3 Cierre de sesión y desbloqueo manual por el Administrador

```mermaid
sequenceDiagram
    autonumber
    actor U as Usuario
    actor AD as Administrador
    participant W as PWA / Web
    participant A as API · AUT
    participant DB as PostgreSQL

    rect rgba(120,160,220,0.12)
    Note over U,DB: Cierre de sesión
    U->>W: Cierra sesión
    opt Hay eventos offline pendientes en el buffer
        W-->>U: Advierte que quedan eventos sin sincronizar (no se borran)
    end
    W->>A: POST /api/v1/auth/logout/
    A->>DB: USER_SESSION.revoked_at = ahora, revoked_reason = LOGOUT
    A-->>W: 200 y borra la cookie refresh
    end

    rect rgba(220,160,120,0.12)
    Note over AD,DB: Desbloqueo manual de una cuenta bloqueada
    AD->>W: Selecciona la cuenta bloqueada y elige Desbloquear
    W->>A: POST /api/v1/users/{id}/unlock/
    A->>A: Valida JWT, sesión y rol ADM (otros roles reciben 403)
    A->>DB: failed_login_attempts = 0 y locked_until = NULL
    A->>DB: AUDIT_LOG (desbloqueo manual)
    A-->>W: 200 cuenta desbloqueada
    end
```

**Reglas y contratos:** RN-AUT-03 (desbloqueo anticipado solo por ADM), CA-001-06. Si quien queda bloqueado es el propio Administrador, el desbloqueo se hace por consola del servidor con `manage.py` (Seguridad §2, punto 8).

---

## 4.2 Importación masiva de estudiantes (versión corregida)

**Módulo:** IMP (delegando la inserción a EST) · **Endpoints:** `GET /imports/template/`, `POST /imports/upload/`, `GET /imports/{batch_id}/`, `POST /imports/{batch_id}/confirm/`, `POST /imports/{batch_id}/cancel/`, `GET /imports/{batch_id}/report/`
**Corrige el Flujo 1 anterior:** toda importación pasa primero por **vista previa sin persistir** (RN-IMP-04); las filas con faltantes diferidos entran como `INCOMPLETO` y las que no traen datos mínimos se descartan (RN-IMP-06); si una matrícula duplicada aparece entre la vista previa y la confirmación, **solo esa fila** se rechaza (RN-IMP-07).

```mermaid
sequenceDiagram
    autonumber
    actor O as ADM / PAD
    participant W as PWA / Web
    participant I as API · IMP
    participant E as API · EST
    participant F as Almacén privado
    participant DB as PostgreSQL

    rect rgba(120,160,220,0.12)
    Note over O,DB: Fase 1 · Vista previa (dry-run, no se persiste ningún estudiante)
    O->>W: Descarga la plantilla y la llena
    W->>I: GET /imports/template/ (columnas exactas del diccionario)
    O->>W: Selecciona archivo .csv o .xlsx y el grupo del lote (grado, grupo, ciclo y turno)
    W->>I: POST /imports/upload/ (multipart: archivo y group_id)
    I->>I: Valida JWT, sesión y rol ADM o PAD (otros roles 403, RN-IMP-05)
    I->>I: Valida extensión, tipo real del contenido y tamaño máximo (no interpreta fórmulas ni macros)
    I->>F: Guarda el archivo con su SHA-256
    I->>DB: INSERT IMPORT_BATCH (VISTA_PREVIA) con grupo, ciclo y turno únicos del lote (RN-IMP-08)
    I->>I: Valida la estructura contra el diccionario (columnas de nombre separadas, RN-IMP-09)
    alt Estructura inválida
        I-->>W: 422 IMPORT_INVALID_STRUCTURE (archivo rechazado completo, sin procesar filas)
    else Estructura válida
        loop Cada fila, de forma independiente (RN-IMP-02)
            I->>I: Valida nombres (RN-TRX-09) y datos mínimos de RN-EST-10 (nombre(s), apellido paterno, matrícula, tutor con contacto válido)
            alt Faltan datos mínimos o hay formato inválido
                I->>DB: IMPORT_ROW_ERROR (columna y motivo), la fila se descarta (RN-IMP-06)
            else La matrícula ya existe
                I->>DB: IMPORT_ROW_ERROR (duplicada, nunca sobrescribe, RN-IMP-03)
            else Fila válida
                I->>DB: Busca coincidencia fuerte del tutor con un GUARDIAN existente (RN-EST-13)
                opt Hay coincidencia
                    Note over I: Se usará el tutor existente sin modificarlo. Si el contacto difiere, se registra una advertencia y no un error (RN-IMP-10)
                end
                opt Falta fecha de nacimiento o fotografía
                    Note over I: La fila se prepara como INCOMPLETO (RN-IMP-06)
                end
            end
        end
        I-->>W: 200 {batch_id, VISTA_PREVIA, total_rows, valid_rows, incomplete_rows, error_rows, warning_rows}
        W-->>O: Muestra los registros a insertar y los rechazados
    end
    end

    rect rgba(160,200,140,0.14)
    Note over O,DB: Fase 2 · Decisión del usuario
    alt El usuario cancela
        O->>W: Cancelar importación
        W->>I: POST /imports/{batch_id}/cancel/
        I->>DB: IMPORT_BATCH VISTA_PREVIA a CANCELADO
        I->>F: Elimina el archivo temporal
        I-->>W: 200 (no se persistió nada, RN-IMP-04)
    else El usuario no confirma
        Note over I,F: El job de mantenimiento (cada hora) marca CANCELADO y elimina el archivo de lotes en VISTA_PREVIA con más de 24 h
    else El usuario confirma
        O->>W: Confirmar importación
        W->>I: POST /imports/{batch_id}/confirm/
        I->>DB: Bloqueo de fila del lote y cambio atómico VISTA_PREVIA a CONFIRMADO
        alt El lote ya no está en VISTA_PREVIA (segunda llamada)
            I-->>W: 422 (confirmación duplicada)
        else Primera confirmación
            I->>F: Relee el archivo y lo vuelve a validar (detecta duplicados nuevos)
            loop Cada fila válida o incompleta
                I->>E: Delega la inserción de la fila
                E->>DB: Transacción por fila: STUDENT, GUARDIAN nuevo o reutilizado, STUDENT_GUARDIAN con consentimiento PENDIENTE
                alt La matrícula fue creada por otro proceso desde la vista previa
                    E-->>I: Matrícula duplicada
                    I->>DB: IMPORT_ROW_ERROR solo para esa fila (RN-IMP-07)
                else Inserción correcta
                    E-->>I: Fila insertada
                end
            end
            I-->>W: 200 resumen con filas insertadas, con error y advertencias
        end
        O->>W: Descarga el reporte
        W->>I: GET /imports/{batch_id}/report/
        I-->>W: Totales, insertadas, errores por fila (columna y motivo) y advertencias
    end
    end
```

**Reglas y contratos:** RN-IMP-01 a RN-IMP-10, RN-EST-10, RN-EST-13, RN-TRX-09, RF-IMP-01, RF-IMP-02. Una fila fallida nunca detiene al resto del lote. Los archivos contienen datos de menores: viven en el almacén privado y se eliminan según la política de mantenimiento (RN-TRX-01).

---

## 4.3 Alta manual, edición y registro incompleto de estudiante

**Módulo:** EST · **Endpoints:** `POST /students/`, `POST /students/{id}/photo/`, `PATCH /students/{id}/`, `PATCH /guardians/{id}/`
**Idea central:** un estudiante **no se guarda sin un tutor con contacto válido**, pero sí puede guardarse como `INCOMPLETO` si solo faltan la fecha de nacimiento o la fotografía. Los tutores compartidos entre hermanos se reconocen y se actualizan en todos los vínculos con advertencia previa.

### 4.3.1 Alta manual (con reconocimiento de tutor compartido y registro incompleto)

```mermaid
sequenceDiagram
    autonumber
    actor O as ADM / PAD
    participant W as PWA / Web
    participant A as API · EST
    participant DB as PostgreSQL

    O->>W: Captura datos del estudiante y de su(s) tutor(es)
    W->>A: POST /students/ {enrollment_id, group_id, nombre en 3 campos, guardians[]...}
    A->>A: Valida JWT, sesión y rol ADM o PAD (otros roles 403)
    A->>A: Valida nombres (RN-TRX-08 y RN-TRX-09) y formato de correo y teléfono
    Note over A: has_payment_debt y pending_subjects solo los captura ADM o PAD (RN-AUT-06)
    alt Falta un dato mínimo o hay formato inválido
        A-->>W: 422 VALIDATION_ERROR (no se guarda nada, RN-EST-10)
    else Datos mínimos completos
        A->>DB: Consulta si la matrícula ya existe (RN-EST-02)
        alt Matrícula duplicada
            A-->>W: 422 DUPLICATE_ENROLLMENT
        else Matrícula nueva
            A->>DB: Verifica grupo activo y ciclo escolar activo
            loop Cada tutor del arreglo
                A->>DB: Busca coincidencia fuerte (nombre sin acentos ni mayúsculas, y correo o teléfono)
            end
            alt Hay coincidencia y no vienen existing_guardian_id ni decline_match_reason
                A-->>W: 422 GUARDIAN_MATCH_FOUND con details.candidates
                W-->>O: Ofrece reutilizar al tutor existente o declinar con motivo
                O->>W: Elige una opción
                W->>A: POST /students/ de nuevo con existing_guardian_id o decline_match_reason
            end
            A->>A: Evalúa si hay al menos un tutor con contacto válido (RN-EST-03 y RN-EST-11)
            alt Ningún tutor con contacto válido
                A-->>W: 422 (no se guarda nada)
            else Hay tutor válido
                A->>A: Calcula completeness (¿faltan fecha de nacimiento o fotografía?)
                A->>DB: Transacción: STUDENT ACTIVO, GUARDIAN nuevo o vínculo con el existente, STUDENT_GUARDIAN (consentimiento PENDIENTE), AUDIT_LOG
                A-->>W: 201 expediente {completeness, missing_fields, guardians[], consent_warning}
                opt completeness = INCOMPLETO
                    W-->>O: Muestra los campos faltantes. Puede recibir asistencia y reportes y obtener su QR y sticker. La credencial completa exige la fotografía, no la fecha de nacimiento (RN-EST-10, RN-CRE-01)
                end
            end
        end
    end
```

**Reglas y contratos:** RN-EST-02, RN-EST-03, RN-EST-07, RN-EST-10, RN-EST-11, RN-EST-13, RN-TRX-08, RN-TRX-09, RF-EST-01, RF-EST-03. `domicilio`, `sexo` y `CURP` son opcionales y su ausencia no genera la marca `INCOMPLETO`.

### 4.3.2 Completar un registro incompleto

```mermaid
sequenceDiagram
    autonumber
    actor O as ADM / PAD
    participant W as PWA / Web
    participant A as API · EST
    participant F as Almacén privado
    participant DB as PostgreSQL

    O->>W: Abre un expediente marcado INCOMPLETO
    W->>A: GET /students/{id}/
    A-->>W: Expediente con completeness y missing_fields
    rect rgba(120,160,220,0.12)
    Note over O,DB: Carga de la fotografía
    O->>W: Selecciona la fotografía
    W->>A: POST /students/{id}/photo/ (multipart)
    A->>A: Valida rol ADM o PAD, tipo real image/jpeg o image/png y tamaño máximo
    A->>A: Elimina metadatos EXIF
    A->>F: Guarda la imagen (acceso solo por la API autorizada, RN-TRX-02)
    A->>DB: Actualiza la referencia de la fotografía
    A-->>W: 200
    end
    rect rgba(160,200,140,0.14)
    Note over O,DB: Captura de la fecha de nacimiento
    O->>W: Captura la fecha de nacimiento
    W->>A: PATCH /students/{id}/ {birth_date}
    A->>A: Valida rol ADM o PAD
    alt El cambio intenta modificar la matrícula
        A-->>W: 422 (inmutable, RN-EST-02, salvo corrección excepcional con motivo y bitácora)
    else Cambio permitido
        A->>DB: UPDATE STUDENT y AUDIT_LOG
        A->>A: Recalcula completeness
        A-->>W: 200 expediente sin campos faltantes
    end
    end
    W-->>O: El expediente queda sin campos faltantes y la credencial completa ya puede exportarse (RN-CRE-01)
```

**Reglas y contratos:** RN-EST-02, RN-EST-10, RN-CRE-01, RN-TRX-02. La foto no es pública: se sirve por `GET /students/{id}/photo/` con validación de rol.

### 4.3.3 Edición de un tutor compartido entre hermanos

```mermaid
sequenceDiagram
    autonumber
    actor O as ADM / PAD
    participant W as PWA / Web
    participant A as API · EST
    participant DB as PostgreSQL

    O->>W: Edita correo, teléfono o nombre de un tutor
    W->>A: PATCH /guardians/{id}/ {cambios}
    A->>A: Valida JWT, sesión y rol ADM o PAD
    A->>DB: ¿El tutor está vinculado a más de un estudiante?
    alt Tutor compartido y la solicitud no trae confirm=true
        A-->>W: 422 CONFIRMATION_REQUIRED con details.affected_students (cantidad y lista), sin guardar todavía (RN-EST-14)
        W-->>O: "Este cambio afectará a N estudiantes" con la lista
        alt El usuario cancela
            W-->>O: No se modifica nada
        else El usuario confirma
            W->>A: PATCH /guardians/{id}/ {cambios, confirm=true}
        end
    end
    A->>A: Valida formato (RN-TRX-09, correo y teléfono)
    A->>DB: ¿El cambio deja a algún estudiante ACTIVO sin tutor con contacto válido?
    alt Sí
        A-->>W: 422 (RN-EST-03, no se guarda nada)
    else No
        A->>DB: Transacción: UPDATE GUARDIAN una sola vez, aplicado a todos los vínculos
        A->>DB: Retira invalidaciones manuales del dato cambiado y recalcula is_valid_contact
        A->>DB: AUDIT_LOG
        A-->>W: 200 tutor actualizado
        Note over A,DB: Relación, contacto principal y consentimiento son por vínculo STUDENT_GUARDIAN y no se copian entre hermanos (RN-EST-14)
    end
```

**Reglas y contratos:** RN-EST-11, RN-EST-13, RN-EST-14, RF-EST-07, Modelo de Datos §3.5. Si el reconocimiento fue erróneo, `POST /guardians/{id}/split/` separa al tutor en dos registros sin afectar a los demás estudiantes vinculados.

---

## 4.4 Generación y revocación de QR (estudiante y docente)

**Módulo:** QR/CRE · **Endpoints:** `POST /credentials/tokens/` con `{entity_type: STUDENT | TEACHER, entity_id, reason?}`, `POST /credentials/exports/preview/` y `POST /credentials/exports/`
**Idea central:** el mismo endpoint cubre la **alta inicial** (ADM o PAD, sin `reason`) y el **reemplazo con revocación** (solo ADM, con `reason` obligatorio). El token es un UUIDv4 opaco generado con el CSPRNG del sistema operativo, único contra vigentes **y** revocados, y nunca se reutiliza. Estudiantes y docentes usan tokens independientes.

### 4.4.1 Emisión inicial (alta del QR)

```mermaid
sequenceDiagram
    autonumber
    actor O as ADM / PAD
    participant W as PWA / Web
    participant Q as API · QR/CRE
    participant G as Generador QR y PDF
    participant DB as PostgreSQL

    O->>W: Elige a la persona (estudiante o docente) y pulsa Generar QR
    W->>Q: POST /credentials/tokens/ {entity_type, entity_id}
    Q->>Q: Valida JWT, sesión y rol ADM o PAD
    Q->>DB: Carga a la persona y su estatus
    alt Estudiante no ACTIVO (RN-EST-05) o docente no ACTIVO (RN-AST-23)
        Q-->>W: 422 STUDENT_NOT_ACTIVE o TEACHER_NOT_ACTIVE según entity_type
    else Persona ACTIVA
        Q->>DB: ¿Tiene un token VIGENTE para ese tipo de entidad? (RN-QR-01 y RN-QR-05)
        alt Ya tiene token vigente
            Note over Q: Es un reemplazo, ver 4.4.2
        else Sin token vigente
            Q->>Q: Genera UUIDv4 con CSPRNG, opaco y sin datos personales (RN-QR-02)
            Q->>DB: Verifica unicidad contra tokens vigentes y revocados
            Q->>DB: INSERT token VIGENTE asociado a la persona y al tipo, y AUDIT_LOG
            Q->>G: Genera la imagen del código QR a partir del token
            G-->>Q: Imagen QR
            Q-->>W: Token emitido con su imagen QR
            W-->>O: Muestra el QR listo para credencial o sticker
        end
    end
```

### 4.4.2 Revocación y reemplazo (pérdida, robo, daño o duplicidad)

```mermaid
sequenceDiagram
    autonumber
    actor O as Usuario
    participant W as PWA / Web
    participant Q as API · QR/CRE
    participant G as Generador QR y PDF
    participant DB as PostgreSQL

    O->>W: Solicita reemplazar el QR e indica el motivo (PERDIDA, ROBO, DANO, DUPLICIDAD)
    W->>Q: POST /credentials/tokens/ {entity_type, entity_id, reason}
    Q->>Q: Valida JWT y sesión
    Q->>DB: Carga a la persona y su token VIGENTE
    alt La persona no está ACTIVA
        Q-->>W: 422 STUDENT_NOT_ACTIVE o TEACHER_NOT_ACTIVE según entity_type (RN-EST-05 o RN-AST-23)
    else La persona ya tiene token vigente
        alt El solicitante no es ADM
            Q-->>W: 403 PERMISSION_DENIED (solo el Administrador revoca y regenera, RN-QR-06)
        else reason ausente
            Q-->>W: 422 VALIDATION_ERROR (el motivo es obligatorio)
        else ADM con motivo
            Q->>Q: Genera UUIDv4 nuevo con CSPRNG y verifica unicidad contra vigentes y revocados
            Q->>DB: Transacción: token anterior a REVOCADO (conserva la referencia a su reemplazo, no se reutiliza, RN-QR-03)
            Q->>DB: INSERT nuevo token VIGENTE y AUDIT_LOG con el motivo
            Q->>G: Genera la imagen del nuevo QR
            G-->>Q: Imagen QR
            Q-->>W: Nuevo token emitido
            Note over Q,DB: Desde este momento, cualquier escaneo del token anterior se rechaza con QR_REVOKED y alerta de verificación manual (RN-QR-04)
        end
    end
```

**Reglas y contratos:** RN-QR-01 a RN-QR-06, RN-CRE-01, RF-QR-01, RF-QR-03, RF-QR-04, RNF-SEG-02. Una **baja** de estudiante o la **desactivación** de un docente **no revocan** el QR: los escaneos se rechazan por estatus (RN-EST-04, RN-AST-29) y el QR sigue vigente si la persona se reactiva. La exportación de credenciales completas exige fotografía; el sticker no (RN-CRE-01).

### 4.4.3 Exportación de credenciales y stickers (vista previa y descarga)

**Idea central:** la exportación va en **dos pasos sin estado**. La vista previa lista quién entra y quién queda fuera con su motivo (RN-CRE-01), y la descarga devuelve el archivo directamente. El servidor no guarda copia, porque las credenciales llevan fotografías de menores (RN-TRX-01, RN-TRX-02).

```mermaid
sequenceDiagram
    autonumber
    actor O as ADM / PAD
    participant W as PWA / Web
    participant Q as API · QR/CRE
    participant G as Generador QR y PDF
    participant DB as PostgreSQL

    O->>W: Elige el modo (CREDENCIAL o STICKER) y la selección (personas individuales o un grupo)
    W->>Q: POST /credentials/exports/preview/ {mode, entity_type, entity_ids o group_id}
    Q->>Q: Valida JWT, sesión y rol ADM o PAD (otros roles 403)
    alt Se envían ambos o ninguno de entity_ids y group_id, o group_id con TEACHER
        Q-->>W: 422 VALIDATION_ERROR
    else Selección válida
        Q->>DB: Carga a las personas y su QR vigente
        loop Cada persona de la selección
            alt La persona no está ACTIVO
                Q->>Q: Se excluye con motivo NO_ACTIVO
            else No tiene QR VIGENTE
                Q->>Q: Se excluye con motivo SIN_QR_VIGENTE
            else Modo CREDENCIAL y sin fotografía
                Q->>Q: Se excluye con motivo SIN_FOTOGRAFIA
            else Cumple las condiciones
                Q->>Q: Se incluye
            end
        end
        Q-->>W: 200 {included, excluded[] con entity_id, display_name y reason}
        W-->>O: Muestra a los incluidos y lista aparte a los excluidos con su motivo (RN-CRE-01)
        O->>W: Confirma y elige el formato (PDF o PNG)
        W->>Q: POST /credentials/exports/ (mismo cuerpo más format)
        alt Ninguna persona cumple las condiciones
            Q-->>W: 422 BUSINESS_RULE_VIOLATION
        else PNG para más de una persona
            Q-->>W: 422 VALIDATION_ERROR
        else Hay al menos una persona exportable
            Q->>G: Genera las imágenes QR y el PDF o PNG de las personas incluidas
            G-->>Q: Archivo generado
            Q-->>W: 200 archivo (application/pdf o image/png), sin copia en el servidor
        end
    end
```

**Reglas y contratos:** RN-CRE-01, RF-CRE-01, RF-CRE-02, RN-AUT-06 (ADM y PAD), RN-TRX-01, RN-TRX-02. Solo se incluyen personas `ACTIVO` con QR `VIGENTE`. Un estudiante `INCOMPLETO` puede exportar sticker; la credencial completa exige fotografía (RN-EST-10, RN-CRE-01). Para reponer un sticker tras una revocación (RF-QR-03) se usa `mode = STICKER` con el `entity_id` de la persona. Hay un máximo configurable de personas por exportación.

---

## 4.5 Escaneo de asistencia estudiantil con reclasificación tras `FALTÓ` automático

**Módulo:** AST (consulta a QR) · **Endpoint:** `POST /attendance/students/scan/` · **Roles:** `PRE`, `PAD`
**Corrige el Flujo 3 anterior:** el rebote se cuenta desde el **último escaneo procesado** (no desde uno ignorado, RN-AST-02/03); el segundo escaneo con estado ya determinado es un **evento adicional** que no cambia el estado (RN-AST-07); y un `FALTO` automático se **reclasifica** por la hora efectiva del escaneo (RN-AST-09). El cliente no envía hora: la hora efectiva es la del servidor (RN-TRX-04).

```mermaid
sequenceDiagram
    autonumber
    actor O as Operador (PRE / PAD)
    participant W as PWA / Web
    participant A as API · AST
    participant Q as Módulo QR
    participant DB as PostgreSQL

    O->>W: Escanea el QR del estudiante con la cámara
    W->>A: POST /attendance/students/scan/ {qr_token, client_event_id}
    A->>A: Valida JWT, sesión y rol PRE o PAD (otros roles 403)
    A->>A: Hora efectiva = hora del servidor al recibir la solicitud (RN-TRX-04)
    A->>Q: Resuelve el token
    Q->>DB: Busca el token (índice UNIQUE)
    alt Token inexistente, de formato inválido o de otra entidad (p. ej. docente)
        A-->>W: 422 QR_NOT_RECOGNIZED (sin registro)
    else Token REVOCADO
        A-->>W: 422 QR_REVOKED con alerta para verificar identidad manualmente (RN-QR-04)
    else Token VIGENTE
        Q-->>A: student_id
        A->>DB: Carga al estudiante
        alt Estatus BAJA o EGRESADO
            A-->>W: 422 STUDENT_NOT_ACTIVE (el QR no se revoca, RN-EST-04 y RN-EST-05)
        else Estudiante ACTIVO
            A->>DB: Consulta el registro del día (UNIQUE student_id y record_date) y el último escaneo procesado
            alt Escaneo dentro de la ventana de rebote contada desde el último escaneo procesado
                A-->>W: 200 DUPLICADO_IGNORADO {window_minutes} (sin registro ni evento, RN-AST-02)
            else No existe registro del día
                A->>DB: Lee cutoff_time del grupo y jornada
                A->>A: Hora efectiva menor o igual al corte da ASISTIO, si no LLEGO_TARDE (RN-AST-01)
                A->>DB: INSERT ATTENDANCE_STUDENT (origen ESCANEO) y ATTENDANCE_STUDENT_EVENT
                A-->>W: 201 REGISTRADO {status, attendance_id, student: nombre, grupo y foto}
            else El registro es FALTO con origen AUTOMATICO
                A->>A: Compara la hora efectiva con el corte: ASISTIO o LLEGO_TARDE (RN-AST-09)
                A->>DB: UPDATE del mismo registro (sin segundo registro de entrada), conserva la trazabilidad del FALTO previo y fija origen AUTOMATICO
                A->>DB: INSERT ATTENDANCE_STUDENT_EVENT
                A-->>W: 200 RECLASIFICADO {previous_status FALTO, status, effective_datetime}
            else Estado ya determinado (ASISTIO o LLEGO_TARDE), o FALTA_JUSTIFICADA o modificado manualmente
                A->>DB: INSERT ATTENDANCE_STUDENT_EVENT (el estado no cambia, RN-AST-07)
                A-->>W: 200 EVENTO_ADICIONAL {status ya determinado}
            end
        end
    end
    W-->>O: Muestra el resultado, el nombre, el grupo y la foto para verificación visual
```

**Reglas y contratos:** RN-QR-04, RN-EST-05, RN-AST-01, RN-AST-02, RN-AST-03, RN-AST-07, RN-AST-09, RN-TRX-04, RN-TRX-07, RN-API-01. Un `FALTA_JUSTIFICADA` o un estado modificado por un usuario **nunca** se reclasifica por escaneo: el estado manual prevalece. La ruta crítica debe resolverse en menos de 250 ms (RNF-DES-01), por lo que correo, auditoría pesada y cualquier trabajo adicional quedan fuera de ella.

---

## 4.6 Verificación automática de ausencias (job programado)

**Módulo:** AST + worker y planificador · **Documento base:** Estrategia de Procesos Programados §1, §2.1, §2.2 y §3
**Idea central:** un **dispatcher** corre cada 5 minutos y encola solo los jobs vencidos y sin corrida registrada hoy. Así sigue los parámetros editables en caliente y recupera corridas perdidas si el servidor estuvo apagado. Todo job es idempotente: marcador `JOB_RUN`, filtro de elegibles y restricción única en la BD.

### 4.6.1 Estudiantes (una vez por turno y día)

```mermaid
sequenceDiagram
    autonumber
    participant D as Dispatcher (cada 5 min)
    participant J as Job check_student_absences
    participant DB as PostgreSQL
    actor AD as Administrador

    loop Cada 5 minutos
        D->>DB: Para cada turno, ¿hoy es día lectivo con ciclo activo, la hora local alcanzó STUDENT_ABSENCE_CHECK_TIME del turno y no hay JOB_RUN completado?
        alt Se cumplen las tres condiciones
            D->>J: Encola check_student_absences(turno, fecha)
        end
    end
    J->>J: Verifica que el reloj del servidor no difiera más de 2 min de la referencia local
    J->>DB: Adquiere el lock absence_students y registra JOB_RUN EN_CURSO (UNIQUE job_name, run_date y scope)
    alt Otra corrida tiene el lock o ya existe el JOB_RUN
        J-->>D: Termina sin hacer nada (idempotencia)
    else Corrida nueva
        J->>DB: Guardia de ciclo: ACADEMIC_CYCLE activo con start_date menor o igual a hoy y end_date mayor o igual a hoy
        alt Sin ciclo activo vigente
            J->>DB: JOB_RUN = OMITIDO (el job no corre porque falta un ciclo activo vigente)
        else Ciclo activo
            J->>DB: Guardia de sanidad: ¿el turno tiene cero escaneos hoy y cero eventos offline pendientes conocidos?
            alt Turno completo sin ningún escaneo
                J->>DB: JOB_RUN = OMITIDO
                J-->>AD: Alerta visible en el panel (el ADM puede ejecutar la verificación manualmente tras confirmar que fue día lectivo)
            else Hay actividad en el turno
                J->>DB: Selecciona estudiantes ACTIVO del turno sin ningún registro de ATTENDANCE_STUDENT hoy (incluye los INCOMPLETO)
                J->>DB: bulk_create en lotes de 500 con ignore_conflicts: FALTO, origen AUTOMATICO, sync_status ONLINE, group_id vigente, effective_datetime NULL
                Note over J,DB: UNIQUE(student_id, record_date): un escaneo concurrente gana sobre el job
                J->>DB: Un renglón de AUDIT_LOG job:absence_check_students (user_id NULL, evaluados y creados)
                J->>DB: Cierra JOB_RUN con conteos
            end
        end
    end
    Note over J,DB: Ante OperationalError reintenta hasta 3 veces con retroceso exponencial (tope 5 min)
```

**Reglas y contratos:** RN-AST-08, RN-AST-09, RN-ADM-02, RN-TRX-07, RN-AUT-05, CA-030-01 a 07. Los eventos offline aún no sincronizados **no se esperan**: el estudiante queda `FALTO` y se reclasifica al sincronizar según su hora efectiva (ver 4.7). Quien se da de alta o reingresa después de la hora de verificación no recibe `FALTO` ese día. Los cambios de parámetro no son retroactivos.

### 4.6.2 Docentes (umbral individual por docente)

```mermaid
sequenceDiagram
    autonumber
    participant D as Dispatcher (cada 5 min)
    participant J as Job check_teacher_absences
    participant DB as PostgreSQL

    loop Cada 5 minutos
        D->>DB: ¿Existe algún docente elegible pendiente? (programación hoy, sin renglón ENTRADA y umbral individual vencido)
        alt Existe al menos uno
            D->>J: Encola check_teacher_absences(fecha)
        end
    end
    J->>J: Verifica reloj del servidor (diferencia máxima de 2 min)
    J->>DB: Adquiere el lock absence_teachers y crea o actualiza el renglón diario de JOB_RUN (job_name, run_date, scope GLOBAL) en EN_CURSO
    J->>DB: Guardia de ciclo activo vigente
    J->>DB: Guardia de sanidad docente: ¿hay hoy algún escaneo estudiantil, algún registro docente con origen ESCANEO o eventos offline pendientes conocidos?
    alt No hay ninguna actividad
        J->>DB: JOB_RUN = OMITIDO (la guardia se reevalúa en el siguiente tick)
        Note over J,DB: Una sola alerta al Administrador por día. Puede ejecutar la verificación manualmente tras confirmar que fue día lectivo
    else Hay actividad
    J->>DB: Selecciona docentes ACTIVO con TEACHER_SCHEDULE activo y weekday igual al de hoy (RN-AST-18)
    Note over J: Sin programación hoy no hay ausencia, aunque el docente esté ACTIVO
    J->>J: Umbral individual = expected_entry_time + máximo(tolerancia efectiva, 0) + TEACHER_ABSENCE_CHECK_OFFSET_MINUTES (30)
    Note over J: Tolerancia efectiva = la de la programación del docente o, si es nula, TEACHER_DEFAULT_TOLERANCE_MINUTES
    J->>J: Conserva solo a los docentes que ya superaron su umbral hoy
    J->>DB: Excluye a quienes ya tienen cualquier renglón ENTRADA hoy en ATTENDANCE_TEACHER
    J->>DB: bulk_create con ignore_conflicts: record_type ENTRADA, FALTO, origen AUTOMATICO, anomaly_flag NINGUNA, effective_datetime NULL
    Note over J,DB: Se guarda como ENTRADA para que el registro posterior actualice este mismo renglón y no se rechace como duplicado (RN-AST-13 y RN-AST-24, ver 4.9)
    opt La corrida creó al menos un renglón
        J->>DB: AUDIT_LOG job:absence_check_teachers (user_id NULL, evaluados y creados)
    end
    J->>DB: Actualiza el renglón diario de JOB_RUN (conteos acumulados y finished_at) y lo deja COMPLETADO
    end
```

**Reglas y contratos:** RN-AST-13, RN-AST-14, RN-AST-15, RN-AST-18, RN-AST-23, RN-AST-24, RN-AST-29, CA-042-01 a 06. La tolerancia define `LLEGÓ TARDE` al registrar la entrada, **no** interviene en la decisión de `FALTÓ`. Un docente `INACTIVO` no se evalúa. La marca `SALIDA_SIN_ENTRADA` no es responsabilidad de este job: la asigna el endpoint de registro de salida (ver 4.9). El job reutiliza un único renglón diario de `JOB_RUN` (`scope = GLOBAL`) y solo escribe en `AUDIT_LOG` cuando crea al menos un renglón (PP §1 y §2.2, MD §3.16). La guardia de sanidad docente es la de PP §3 (CA-042-08).

---

## 4.7 Captura y sincronización offline

**Módulo:** AST / MOV · **Endpoint:** `POST /attendance/students/sync/` · **Roles:** `PRE`, `PAD`
**Idea central:** sin conexión el dispositivo **no valida nada definitivo**: solo guarda el evento mínimo en un buffer. Todo el criterio de negocio se aplica en el backend al sincronizar, con las mismas reglas que un escaneo en línea (RN-MOV-01, RN-API-01). La hora efectiva sale de la hora de captura corregida con el desfase del reloj, **no** de la hora de sincronización (RN-TRX-04).

### 4.7.1 Captura sin conexión (buffer en el dispositivo)

```mermaid
sequenceDiagram
    autonumber
    actor O as Operador (PRE / PAD)
    participant W as PWA
    participant B as Buffer (IndexedDB)
    participant A as API

    Note over W,A: Con conexión, la PWA consultó GET /system/status/ y calculó clock_offset_ms (reloj del dispositivo contra hora del servidor)
    O->>W: Escanea el QR de un estudiante
    W->>W: Detecta que no alcanza el servidor (pérdida de la LAN)
    W->>B: ¿El buffer tiene menos de 1,000 eventos?
    alt Buffer lleno
        W-->>O: Rechaza el evento y alerta que reintente cuando haya conexión (RN-MOV-03)
    else Hay espacio
        W->>B: Guarda {client_event_id UUID, qr_token, captured_at, clock_offset_ms, event_type, user_id del operador}
        Note over B: Pendiente de validación. Sin nombre, matrícula ni otro dato personal del estudiante (RN-MOV-02)
        W-->>O: "Capturado sin conexión, pendiente de validación"
    end
```

### 4.7.2 Sincronización y validación diferida en el backend

```mermaid
sequenceDiagram
    autonumber
    actor O as Operador (PRE / PAD)
    participant W as PWA
    participant B as Buffer (IndexedDB)
    participant A as API · AST
    participant DB as PostgreSQL

    Note over W,A: Se restablece la conexión (en iOS la sincronización requiere la app abierta, ADR-01)
    opt El refresh venció durante la desconexión
        W-->>O: Pide iniciar sesión de nuevo (los eventos se conservan, ver 4.1.2)
    end
    W->>B: Lee los eventos pendientes (máximo 1,000)
    W->>A: POST /attendance/students/sync/ {events[]}
    A->>A: Valida JWT, sesión y rol PRE o PAD de quien sincroniza
    A->>A: Ordena los eventos por captured_at
    loop Cada evento, de forma independiente (uno inválido no aborta el lote)
        A->>DB: ¿El client_event_id ya fue procesado?
        alt Ya procesado
            A->>A: Devuelve el resultado previo sin reprocesar (idempotencia)
        else Evento nuevo
            A->>DB: ¿captured_by conserva rol PRE o PAD y cuenta activa?
            A->>A: Hora efectiva = captured_at corregida con clock_offset_ms (RN-TRX-04)
            alt Antigüedad mayor a OFFLINE_MAX_AGE_HOURS (72 h)
                A->>A: Descarta con EVENT_TOO_OLD
            else Hora efectiva posterior al reloj del servidor más una tolerancia pequeña
                A->>A: Descarta con EVENT_IN_FUTURE
            else Edad y hora válidas
                opt El valor absoluto de clock_offset_ms supera 5 minutos
                    A->>DB: Marca el evento para revisión
                end
                A->>DB: Valida que el QR exista y no esté revocado, y que el estudiante esté ACTIVO
                alt QR no reconocido, QR revocado o estudiante no activo
                    A->>A: Descarta con QR_NOT_RECOGNIZED, QR_REVOKED o STUDENT_NOT_ACTIVE
                else Evento válido
                    A->>DB: Aplica la lógica del escaneo en línea con la hora efectiva (ver 4.5)
                    Note over A,DB: Rebote desde el último escaneo procesado, ASISTIO o LLEGO_TARDE contra el corte, reclasificación de FALTO AUTOMATICO, o evento adicional
                    A->>A: Acepta con result REGISTRADO, EVENTO_ADICIONAL, RECLASIFICADO o DUPLICADO_IGNORADO
                end
            end
        end
    end
    A-->>W: 200 {accepted[], discarded[] con error_code y rn_reference, summary}
    W->>B: Elimina solo los eventos confirmados por el servidor (aceptados o descartados con motivo)
    W-->>O: Notifica los eventos descartados con su motivo
```

**Reglas y contratos:** RN-MOV-01, RN-MOV-02, RN-MOV-03, RN-TRX-04, RN-AST-02, RN-AST-03, RN-AST-09, RN-API-01, RNF-FIA-01, RNF-FIA-04, SG-09, D-11, US-033. El orden exacto de las validaciones por evento es ilustrativo: los documentos fijan *qué* se valida, no su secuencia interna.
**Caso típico de reclasificación:** un evento capturado a las 07:55 sin conexión y sincronizado a las 11:00, después de que el job de las 10:00 marcó `FALTO`, se acepta como `RECLASIFICADO` con estado `ASISTIO`, porque la hora efectiva (07:55) es anterior al corte (RN-AST-09, RN-TRX-04). Si el registro ya fue `FALTA_JUSTIFICADA` manualmente, el evento solo queda como `EVENTO_ADICIONAL`.

---

## 4.8 Alta, edición, desactivación y reactivación de la ficha docente

**Módulo:** AST (app `teachers`) · **Endpoints:** `POST /teachers/`, `PATCH /teachers/{id}/`, `POST /teachers/{id}/deactivate/`, `POST /teachers/{id}/reactivate/`
**Idea central:** el docente tiene una **ficha propia, independiente de las cuentas de usuario** (RN-AST-23): su asistencia no depende de tener cuenta. Nunca se elimina: solo pasa de `ACTIVO` a `INACTIVO` (ADM o PAD, con motivo) y regresa a `ACTIVO` solo por el Administrador (con motivo).

```mermaid
sequenceDiagram
    autonumber
    actor O as ADM / PAD
    actor AD as Administrador
    participant W as PWA / Web
    participant T as API · Docentes
    participant DB as PostgreSQL

    rect rgba(120,160,220,0.12)
    Note over O,DB: Alta de la ficha
    O->>W: Captura nombre(s), apellido paterno, identificador interno y datos opcionales
    W->>T: POST /teachers/
    T->>T: Valida JWT, sesión y rol ADM o PAD
    T->>T: Valida mínimos (nombre(s), apellido paterno, identificador) y nombres con RN-TRX-09
    T->>DB: ¿El identificador ya existe? (incluye docentes INACTIVO)
    alt Falta un dato mínimo, nombre inválido o identificador duplicado
        T-->>W: 422 DUPLICATE_TEACHER_ID si el identificador ya existe, o VALIDATION_ERROR si falta un mínimo o el nombre es inválido (RN-AST-26 y RN-AST-27)
    else Datos válidos
        T->>DB: INSERT TEACHER (ACTIVO) y AUDIT_LOG
        T-->>W: 201 ficha del docente
    end
    Note over T,DB: Aparte, la programación semanal se define con PUT /teachers/{id}/schedule/ (ADM o PAD) y el vínculo con una cuenta Docente con POST /users/{user_id}/link-teacher/ (solo ADM)
    end

    rect rgba(160,200,140,0.14)
    Note over O,DB: Edición de la ficha
    O->>W: Modifica datos de la ficha
    W->>T: PATCH /teachers/{id}/ {cambios}
    T->>T: Valida rol ADM o PAD y nombres con RN-TRX-09
    alt El cambio intenta modificar el identificador
        T-->>W: 422 BUSINESS_RULE_VIOLATION (inmutable, RN-AST-26, salvo corrección excepcional con motivo y bitácora)
    else Cambio permitido
        T->>DB: UPDATE TEACHER y AUDIT_LOG con valor anterior y nuevo
        T-->>W: 200 ficha actualizada
    end
    end

    rect rgba(220,190,120,0.14)
    Note over O,DB: Desactivación
    O->>W: Desactiva al docente e indica el motivo
    W->>T: POST /teachers/{id}/deactivate/ {reason}
    T->>T: Valida rol ADM o PAD y motivo obligatorio
    alt Sin motivo o el docente ya está INACTIVO
        T-->>W: 422 (RN-AST-28)
    else Transición válida ACTIVO a INACTIVO
        T->>DB: Transacción: status INACTIVO sin tocar TEACHER_SCHEDULE (la programación se conserva y no se evalúa mientras esté INACTIVO)
        T->>DB: El QR vigente NO se revoca y el historial de asistencia sigue consultable (RN-AST-29)
        T->>DB: AUDIT_LOG con reason, como evento distinto del alta original
        T->>DB: ¿Hay una cuenta de usuario vinculada y activa?
        alt Sí
            T-->>W: 200 con advertencia al Administrador (la cuenta no se desactiva sola)
        else No
            T-->>W: 200
        end
        Note over T,DB: Deja de aparecer en la verificación de ausencias y en el registro de ENTRADA y SALIDA. Un escaneo de su QR responde TEACHER_NOT_ACTIVE (ver 4.9)
    end
    end

    rect rgba(220,160,160,0.14)
    Note over AD,DB: Reactivación (solo Administrador)
    AD->>W: Reactiva al docente e indica el motivo
    W->>T: POST /teachers/{id}/reactivate/ {reason}
    alt El rol no es ADM
        T-->>W: 403 PERMISSION_DENIED (RN-AST-28)
    else Sin motivo o el docente no está INACTIVO
        T-->>W: 422
    else Transición válida INACTIVO a ACTIVO
        T->>DB: status ACTIVO (el QR conservado vuelve a aceptarse)
        T->>DB: AUDIT_LOG como evento distinto del alta original
        T-->>W: 200 ficha reactivada con advertencia de revisar la programación conservada
        Note over T,DB: TEACHER_SCHEDULE no se modifica. La misma programación vuelve a aplicar desde hoy, sin evaluar los días en que estuvo INACTIVO (RN-AST-29)
    end
    end
```

**Reglas y contratos:** RN-AST-23, RN-AST-26 a RN-AST-30, RN-TRX-03, RN-TRX-08, RN-TRX-09, RN-AUT-05, RF-AST-11, RF-AST-12. Datos mínimos: nombre(s), apellido paterno, identificador y estatus. Opcionales: apellido materno, fotografía, correo y teléfono; no generan marca de incompleto (RN-AST-27). Un docente nunca se importa de forma masiva: el alta es individual.

---

## 4.9 Registro de asistencia docente (entrada y salida)

**Módulo:** AST · **Endpoint:** `POST /attendance/teachers/scan/` · **Rol:** solo `PAD` (el Administrador y los demás roles reciben 403, RN-AST-10)
**Idea central:** el Personal administrativo escanea el QR del docente y **elige manualmente** si es `ENTRADA` o `SALIDA` (RN-AST-12). Un `FALTO` automático del día se guarda como `ENTRADA`, por eso la entrada real **actualiza ese mismo renglón** en vez de contarse como duplicada.

```mermaid
sequenceDiagram
    autonumber
    actor P as Personal administrativo
    participant W as PWA / Web
    participant A as API · AST
    participant DB as PostgreSQL

    P->>W: Elige ENTRADA o SALIDA y escanea el QR del docente
    W->>A: POST /attendance/teachers/scan/ {qr_token, record_type, client_event_id}
    A->>A: Valida JWT, sesión y rol PAD (cualquier otro rol 403, RN-AST-10)
    A->>A: Hora efectiva = hora del servidor (RN-TRX-04)
    A->>DB: Busca el token QR
    alt Token inexistente o de otro tipo de entidad (p. ej. estudiante)
        A-->>W: 422 QR_NOT_RECOGNIZED
    else Token REVOCADO
        A-->>W: 422 QR_REVOKED
    else Token VIGENTE
        A->>DB: Carga al docente
        alt Docente INACTIVO
            A-->>W: 422 TEACHER_NOT_ACTIVE (el QR no se marca revocado, RN-AST-23 y RN-AST-29)
        else Docente ACTIVO
            A->>DB: Consulta los renglones ATTENDANCE_TEACHER de hoy
            alt record_type = ENTRADA
                alt Existe ENTRADA con FALTO de origen AUTOMATICO
                    A->>DB: Lee expected_entry_time del día y la tolerancia (del docente o institucional)
                    A->>A: Hora efectiva menor o igual a expected_entry_time + tolerancia da ASISTIO, si no LLEGO_TARDE (RN-AST-14 y RN-AST-19)
                    A->>DB: UPDATE del mismo renglón, origen AUTOMATICO, con trazabilidad del FALTO previo (no es una segunda entrada, RN-AST-13 y RN-AST-24)
                    A-->>W: 200 RECLASIFICADO {previous_status FALTO, status}
                else Existe una ENTRADA con estado manual (FALTA_JUSTIFICADA o modificada por un usuario)
                    A-->>W: 422 DUPLICATE_RECORD con details.reason MANUAL_STATE_PREVAILS (RN-AST-24)
                else Existe una ENTRADA válida
                    A-->>W: 422 DUPLICATE_RECORD (RN-AST-13)
                else No existe ENTRADA hoy
                    A->>DB: ¿El docente tiene TEACHER_SCHEDULE activo para el día de la semana de hoy?
                    alt Tiene programación
                        A->>DB: Lee expected_entry_time del día y la tolerancia
                        A->>A: Calcula ASISTIO o LLEGO_TARDE
                        A->>DB: INSERT ATTENDANCE_TEACHER (ENTRADA, origen ESCANEO, is_scheduled true)
                        A-->>W: 201 REGISTRADO {status, effective_datetime, anomaly_flag NINGUNA, scheduled true}
                    else Sin programación hoy
                        A->>DB: INSERT ATTENDANCE_TEACHER (ENTRADA, origen ESCANEO, status nulo, is_scheduled false, RN-AST-32)
                        A-->>W: 201 REGISTRADO {status null, anomaly_flag NINGUNA, scheduled false}
                    end
                end
            else record_type = SALIDA
                alt Ya existe una SALIDA hoy
                    A-->>W: 422 DUPLICATE_RECORD (RN-AST-16)
                else No existe SALIDA hoy
                    A->>DB: ¿Existe una ENTRADA válida hoy? (un FALTO automático no cuenta, RN-AST-13)
                    alt No hay ENTRADA válida
                        A->>DB: INSERT SALIDA con anomaly_flag SALIDA_SIN_ENTRADA (RN-AST-25)
                    else Hay ENTRADA válida
                        A->>DB: INSERT SALIDA con la hora efectiva, status nulo (RN-AST-20)
                    end
                    Note over A,DB: Si hoy el docente no tiene programación, la SALIDA se guarda con is_scheduled false (RN-AST-32). En otro caso, true
                    A-->>W: 201 REGISTRADO {record_type SALIDA, anomaly_flag, scheduled}
                end
            end
        end
    end
    W-->>P: Muestra el resultado
```

**Reglas y contratos:** RN-AST-10 a RN-AST-25, RN-QR-06, RN-TRX-04, RN-TRX-07, RF-AST-08, RF-AST-09, CA-060-04. La corrección posterior de cualquier registro docente solo procede por el flujo de justificación (ver 4.12). La asistencia del personal administrativo está en espera (RN-AST-31, CC-02): este flujo solo aplica a docentes.

---

## 4.10 Flujo completo de un reporte escolar

**Módulo:** REP (con COM) · **Endpoints:** `POST /reports/`, `POST /reports/{id}/transitions/`, `POST /reports/{id}/communications/`, `GET /reports/{id}/history/`
**Idea central:** el reporte avanza en orden `REGISTRADO → REVISADO_PREFECTO → CANALIZADO → REVISADO_ADMINISTRATIVO → COMUNICADO → RESUELTO` y no puede saltarse etapas (RN-REP-03). Hay dos rechazos distintos: el **rechazo del prefecto** termina el flujo del original (se corrige con un reporte nuevo) y el **rechazo administrativo** devuelve el reporte al prefecto. Nunca se comunica a la familia sin revisión del Personal administrativo (RN-REP-04).

```mermaid
sequenceDiagram
    autonumber
    actor D as Docente
    actor PR as Prefecto
    actor PA as Personal administrativo
    participant W as PWA / Web
    participant R as API · REP
    participant DB as PostgreSQL
    participant K as Módulo COM y worker

    rect rgba(120,160,220,0.12)
    Note over D,K: Etapa 1 · Registro por el docente
    D->>W: Registra el reporte (estudiante, tipo, gravedad, opciones y observación)
    W->>R: POST /reports/
    R->>R: Valida JWT, sesión y rol DOC (otros roles 403)
    R->>DB: Verifica cuenta vinculada a docente ACTIVO (RN-AST-30), estudiante ACTIVO (RN-EST-05) de un grupo asignado al docente (RN-REP-09)
    R->>R: Observación de 50 a 100 caracteres tras recortar espacios (RN-REP-01) y opciones acordes al tipo y gravedad
    opt El reporte reemplaza a uno rechazado
        R->>DB: replaces_report_id debe apuntar a un reporte RECHAZADO del mismo docente y estudiante (RN-REP-08)
    end
    alt Alguna validación falla
        R-->>W: 422 (o 403 si el rol o el grupo no corresponden)
    else Validaciones correctas
        R->>DB: INSERT reporte REGISTRADO y renglón en REPORT_TRANSITION_LOG
        R->>DB: ¿El grupo del estudiante tiene prefectos asignados?
        alt Sí
            Note over R,DB: El reporte llega a la bandeja de los prefectos del grupo (PREFECT_GROUP_ASSIGNMENT)
        else No
            Note over R,DB: Queda en la bandeja de PAD y ADM con alerta (RN-REP-09). Nadie ejecuta la etapa de prefecto hasta definir uno (D-10)
        end
        R-->>W: 201 {report_id, REGISTRADO}
    end
    end

    rect rgba(160,200,140,0.14)
    Note over D,K: Etapa 2 · Revisión y canalización por el prefecto
    PR->>W: Abre su bandeja (solo reportes de sus grupos asignados, otros responden 404)
    PR->>W: Decide sobre el reporte
    W->>R: POST /reports/{id}/transitions/ {action}
    R->>R: Valida rol PRE y grupo asignado. Cualquier combinación no listada responde 422 INVALID_TRANSITION
    alt action = REJECT con reason obligatorio
        R->>DB: REGISTRADO a RECHAZADO y renglón en REPORT_TRANSITION_LOG
        R-->>D: Aviso dentro de la aplicación: el reporte aparece como RECHAZADO con su motivo, sin correo (RN-REP-08)
        Note over D,R: Fin del flujo del original. El docente puede registrar un reporte nuevo con replaces_report_id (vuelve a la Etapa 1)
    else action = REVIEW
        R->>DB: REGISTRADO a REVISADO_PREFECTO y renglón en REPORT_TRANSITION_LOG
        PR->>W: Canaliza el reporte
        W->>R: POST /reports/{id}/transitions/ {action = CHANNEL}
        R->>DB: REVISADO_PREFECTO a CANALIZADO y renglón en REPORT_TRANSITION_LOG
    end
    end

    rect rgba(220,190,120,0.14)
    Note over D,K: Etapa 3 · Revisión administrativa
    PA->>W: Revisa el reporte canalizado
    W->>R: POST /reports/{id}/transitions/ {action}
    R->>R: Valida rol PAD
    alt action = ADMIN_RETURN con reason obligatorio
        R->>DB: CANALIZADO a REVISADO_PREFECTO y renglón en REPORT_TRANSITION_LOG
        Note over PR,R: Regresa al prefecto, no se cierra (RN-REP-03). El prefecto vuelve a canalizar
    else action = ADMIN_REVIEW
        R->>DB: CANALIZADO a REVISADO_ADMINISTRATIVO y renglón en REPORT_TRANSITION_LOG
    end
    end

    rect rgba(220,160,160,0.14)
    Note over D,K: Etapa 4 · Cierre del ciclo
    alt El PAD decide no comunicar (RESOLVE_NO_COMMUNICATION)
        PA->>W: Registra el motivo
        W->>R: POST /reports/{id}/transitions/ {action, no_communication_reason}
        R->>DB: REVISADO_ADMINISTRATIVO a RESUELTO con motivo y renglón en REPORT_TRANSITION_LOG (RN-REP-07b)
    else El PAD comunica a la familia (COMMUNICATE)
        PA->>W: Comunicar a la familia
        W->>R: POST /reports/{id}/communications/
        R->>DB: ¿Hay tutor con contacto válido y correo, y consentimiento distinto de REVOCADO? (RN-COM-01 y RN-COM-04)
        alt No hay contacto elegible
            R->>DB: REVISADO_ADMINISTRATIVO a AUTORIZADO (pendiente de contacto válido, RN-REP-07) y renglón en el log
            Note over R,DB: Regresa al flujo de comunicación cuando se registre un contacto válido con correo
        else Hay contacto elegible
            R->>K: Crea COMMUNICATION_LOG y encola el envío (detalle en 4.11)
            K->>DB: Si el envío es ENVIADO, el reporte pasa a COMUNICADO y luego a RESUELTO (changed_by NULL, RN-REP-07a)
        end
    end
    end
```

**Reglas y contratos:** RN-REP-01 a RN-REP-09, RN-AST-30, RN-EST-05, RN-COM-01, RN-COM-04, RN-AUT-06, RF-REP-01 a RF-REP-04. Todo cambio de etapa escribe un renglón en `REPORT_TRANSITION_LOG` (RN-REP-06). El tipo y la gravedad no se modifican después del envío (RN-REP-02): no existe `PATCH /reports/{id}/`. Un reporte fuera del alcance del rol responde **404**, no 403 (RN-REP-05). `PRE` y `DOC` nunca autorizan ni comunican (RN-REP-04).

---

## 4.11 Envío de comunicación por correo con reintento

**Módulo:** COM + worker · **Endpoints:** `GET /reports/{id}/communications/preview/`, `POST /reports/{id}/communications/`, `POST /communications/{id}/retry/`, `GET /communications/`
**Idea central:** el envío **nunca** sale del registro del reporte ni de la revisión del prefecto: solo de la acción explícita del PAD (RN-REP-04). Todo intento deja un renglón de estado `PENDIENTE`, `ENVIADO` o `FALLIDO` (RN-COM-03). Sin Internet el correo no sale, pero eso **no afecta** las funciones internas (RN-INF-02).

### 4.11.1 Autorización, envío asíncrono y reintentos automáticos

```mermaid
sequenceDiagram
    autonumber
    actor PA as Personal administrativo
    participant W as PWA / Web
    participant R as API · REP y COM
    participant DB as PostgreSQL
    participant Q as Cola de tareas
    participant K as Worker
    participant S as Servidor SMTP
    actor T as Tutor

    PA->>W: Abre Comunicar a la familia
    W->>R: GET /reports/{id}/communications/preview/
    R-->>W: Contenido exacto a enviar (solo lo autorizado, nunca el expediente completo, RN-COM-02)
    PA->>W: Autoriza y envía
    W->>R: POST /reports/{id}/communications/
    R->>R: Valida JWT, sesión y rol PAD (RN-REP-04)
    R->>DB: ¿El reporte está en REVISADO_ADMINISTRATIVO o AUTORIZADO?
    alt Estado distinto
        R-->>W: 422 INVALID_TRANSITION
    else Estado válido
        R->>DB: ¿Existe tutor con is_valid_contact y correo? (RN-COM-01)
        alt Ninguno
            R->>DB: Reporte a AUTORIZADO (pendiente de contacto válido) y no se crea COMMUNICATION_LOG
            R-->>W: Respuesta sin envío, con aviso al PAD
        else Hay tutor con correo
            R->>DB: ¿consent_status del tutor es REVOCADO? (RN-COM-04)
            alt REVOCADO
                R-->>W: 422 rechazo y advertencia al PAD (puede usarse otro tutor elegible)
            else Consentimiento no revocado
                R->>DB: Transacción: INSERT COMMUNICATION_LOG (PENDIENTE) con content_snapshot de la vista previa aprobada
                R->>Q: on_commit, send_notification_email(communication_log_id)
                R-->>W: Aceptado, estado PENDIENTE
            end
        end
    end

    Note over Q,S: Fuera de la ruta crítica. Reintentos con retroceso exponencial y jitter (tope 15 min)
    Q->>K: Entrega la tarea
    K->>DB: Relee el renglón de COMMUNICATION_LOG
    alt El renglón ya no está PENDIENTE
        K->>K: Termina (idempotencia)
    else Sigue PENDIENTE
        K->>DB: Relee consent_status del tutor
        alt Ahora es REVOCADO
            K->>DB: Marca FALLIDO permanente y no reintenta
        else No revocado
            alt No hay Internet (RN-INF-02)
                K->>DB: Deja el renglón PENDIENTE sin consumir intentos (la interfaz muestra sin Internet)
            else Hay Internet
                loop Hasta COMMUNICATION_MAX_AUTO_ATTEMPTS (3)
                    K->>S: Envía el content_snapshot exacto sin modificarlo
                    alt Éxito
                        S-->>K: Aceptado
                        K->>DB: Renglón ENVIADO, y en la misma transacción reporte a COMUNICADO y luego RESUELTO (dos renglones con changed_by NULL)
                        S-->>T: Entrega el correo (ENVIADO no significa leído)
                    else SMTPException u OSError
                        K->>DB: Registra el intento fallido (un renglón por intento, RN-COM-03)
                        K->>K: Espera el retroceso y reintenta
                    end
                end
                opt Intentos automáticos agotados
                    K->>DB: Renglón FALLIDO (queda disponible el reintento manual)
                end
            end
        end
    end
```

### 4.11.2 Reintento manual y recolector

```mermaid
sequenceDiagram
    autonumber
    actor PA as Personal administrativo
    participant W as PWA / Web
    participant R as API · COM
    participant DB as PostgreSQL
    participant Q as Cola de tareas
    participant SW as Recolector (cada hora)

    PA->>W: Revisa el estado de los envíos
    W->>R: GET /communications/?status=FALLIDO
    R-->>W: Lista de comunicaciones con su estado
    PA->>W: Pulsa Reintentar en una comunicación FALLIDO
    W->>R: POST /communications/{id}/retry/
    R->>R: Valida JWT, sesión y rol PAD
    R->>DB: INSERT nuevo renglón con retried_by (el renglón fallido se conserva, RN-COM-03)
    R->>Q: Encola send_notification_email (mismo flujo y validaciones que en 4.11.1)
    R-->>W: Aceptado, estado PENDIENTE

    Note over SW,DB: Mantenimiento programado, sin intervención del usuario
    SW->>DB: Toma renglones PENDIENTE con más de 15 min (huérfanos por reinicio del worker)
    SW->>DB: Toma renglones FALLIDO con intentos automáticos restantes (no los permanentes ni los agotados)
    SW->>Q: Reencola esos envíos (sin Internet no consume intentos)
    SW->>DB: Busca reportes AUTORIZADO cuyo tutor ya tenga contacto válido con correo
    SW->>Q: Devuelve esos reportes al flujo de envío (RN-REP-07)
```

**Reglas y contratos:** RN-COM-01 a RN-COM-04, RN-REP-04, RN-REP-07, RN-INF-02, RN-EST-11, US-050, US-052, US-053, CA-052-*, CA-053-*. Un tutor con solo teléfono es contacto válido para guardar al estudiante, pero **no** puede recibir comunicaciones automatizadas (RN-EST-11). El reintento manual es exclusivo del PAD (D-06 cerrada, RN-AUT-06).

---

## 4.12 Justificación y modificación de asistencia con auditoría

**Módulo:** AST · **Endpoints:** `POST /attendance/students/{attendance_id}/justify/`, `PATCH /attendance/students/{attendance_id}/` y sus equivalentes docentes en `/attendance/teachers/{attendance_id}/`
**Idea central:** solo `ADM` y `PAD` pueden cambiar un registro ya determinado, siempre con **motivo** y con trazabilidad inmutable. Un registro **nunca se elimina**. Solo un `FALTO` puede pasar a `FALTA_JUSTIFICADA`, y el resultado queda con origen `MANUAL`, que prevalece sobre cualquier reclasificación automática.

```mermaid
sequenceDiagram
    autonumber
    actor O as Usuario
    participant W as PWA / Web
    participant A as API · AST
    participant DB as PostgreSQL

    rect rgba(120,160,220,0.12)
    Note over O,DB: Justificar una falta
    O->>W: Selecciona un registro FALTO y captura el motivo
    W->>A: POST /attendance/students/{attendance_id}/justify/ {justification_reason}
    A->>A: Valida JWT, sesión y rol ADM o PAD (RN-AST-04)
    alt El rol es PRE, DOC o SL
        A-->>W: 403 PERMISSION_DENIED
    else Rol autorizado
        alt Motivo ausente
            A-->>W: 422 VALIDATION_ERROR (RN-AST-05)
        else Motivo presente
            A->>DB: Carga el registro
            alt El estado actual no es FALTO
                A-->>W: 422 INVALID_TRANSITION (RN-AST-22)
            else El estado es FALTO
                A->>DB: Transacción: estado a FALTA_JUSTIFICADA con origen MANUAL (el registro no se elimina, RN-AST-06)
                A->>DB: AUDIT_LOG con usuario, fecha y hora, valor anterior, valor nuevo y motivo (RN-AST-05 y RN-AUT-05)
                A-->>W: 200 {attendance_id, FALTA_JUSTIFICADA, MANUAL}
            end
        end
    end
    end

    rect rgba(160,200,140,0.14)
    Note over O,DB: Modificar el estado de un registro ya determinado
    O->>W: Elige el nuevo estado y captura el motivo
    W->>A: PATCH /attendance/students/{attendance_id}/ {status, reason}
    A->>A: Valida rol ADM o PAD y motivo obligatorio
    alt Transición no permitida o motivo ausente
        A-->>W: 422 INVALID_TRANSITION o VALIDATION_ERROR
    else Transición permitida
        A->>DB: UPDATE del estado con origen MANUAL
        A->>DB: AUDIT_LOG con valor anterior, valor nuevo, usuario, fecha y hora, y motivo
        A-->>W: 200 registro actualizado
        Note over A,DB: Un escaneo posterior ya no reclasifica este registro: se guarda solo como EVENTO_ADICIONAL (RN-AST-09 y ver 4.5)
    end
    end

    Note over A,DB: No existe operación de borrado. El rol de BD de la aplicación no tiene DELETE sobre ATTENDANCE_* ni AUDIT_LOG (RN-AST-06, RN-AST-21, RN-TRX-03)
```

**Reglas y contratos:** RN-AST-04, RN-AST-05, RN-AST-06, RN-AST-17, RN-AST-21, RN-AST-22, RN-TRX-07, RN-AUT-05. El flujo docente es equivalente (`/attendance/teachers/{id}/justify/` y `PATCH`), con las mismas reglas de rol, motivo y trazabilidad (RN-AST-17). El contenido de `previous_value` y `new_value` en `AUDIT_LOG` solo lo ve el Administrador (Seguridad §4.4). **Pendiente con la institución:** el conjunto exacto de transiciones permitidas en el `PATCH` (propuesta de la API: cualquier estado a `ASISTIO`, `LLEGO_TARDE` o `FALTO` con motivo, y `FALTA_JUSTIFICADA` solo desde `FALTO`).

---

## 4.13 Respaldo y restauración de la base de datos

**Módulo:** ADM / `ops` + worker · **Endpoint de consulta:** `GET /ops/backups/` (solo ADM) · **Documento base:** Procesos Programados §2.3, CA-057-01 a 05
**Idea central:** el respaldo es **automático y local** (no depende de Internet). El resultado oficial (`status`) es el del respaldo local verificado: la copia externa es opcional, está apagada por defecto y **nunca** modifica `status`. La **restauración no es una API pública**: la ejecuta el Administrador u operador técnico por consola, siguiendo el runbook.

### 4.13.1 Respaldo automático

```mermaid
sequenceDiagram
    autonumber
    participant D as Dispatcher (cada 5 min)
    participant J as Job run_backup
    participant DB as PostgreSQL
    participant V as Volumen local de respaldos
    participant X as Copia externa (opcional)
    actor AD as Administrador

    loop Cada 5 minutos
        D->>DB: ¿El último BACKUP_LOG EXITOSO es más antiguo que BACKUP_FREQUENCY_HOURS (24 h, 02:00 por defecto)?
        alt Vencido (incluye recuperar una corrida perdida porque el servidor estuvo apagado)
            D->>J: Encola run_backup
        end
    end
    J->>DB: pg_dump -Fc
    J->>V: Escribe un archivo temporal en una partición distinta de la de datos
    loop Hasta 3 intentos ante OSError o CalledProcessError (retroceso exponencial, tope 10 min)
        J->>V: Verifica integridad: pg_restore --list y SHA-256
    end
    alt Falla el respaldo o la verificación tras los reintentos
        J->>DB: BACKUP_LOG status FALLIDO
        J-->>AD: Alerta visible en el panel (CA-057-02)
        J-->>AD: Correo adicional, mejor esfuerzo, solo si hay Internet (RN-INF-02)
    else Respaldo verificado
        J->>V: Mueve el archivo al destino final con permisos 0600 y propietario el usuario de servicio
        J->>DB: BACKUP_LOG status EXITOSO, size_bytes y offsite_status N_A
        opt Copia externa habilitada (autorizada por escrito, D-05)
            J->>J: Cifra el archivo antes de salir del servidor
            J->>X: Envía la copia si hay conectividad (hasta 3 reintentos exponenciales)
            J->>DB: Actualiza solo offsite_status (EXITOSO o FALLIDO), nunca status
        end
        J->>V: Rotación: conserva al menos 7 respaldos diarios y 4 semanales, sin eliminar jamás el último EXITOSO verificado
    end
    AD->>DB: Consulta GET /ops/backups/ (fecha, resultado, tamaño y alertas)
```

### 4.13.2 Restauración (procedimiento por consola)

```mermaid
sequenceDiagram
    autonumber
    actor AD as Administrador / operador técnico
    participant C as Consola del servidor
    participant V as Volumen local de respaldos
    participant DB as PostgreSQL
    participant S as Servicios SIGE
    participant L as Bitácora de operación (fuera de la BD)

    Note over AD,S: Se ejecuta según docs/runbook_restauracion.md. No existe API pública de restauración
    AD->>AD: Confirma que la restauración está autorizada (RN-INF-03)
    AD->>V: Elige el último respaldo EXITOSO verificado (BACKUP_LOG o, si la base no responde, el propio volumen)
    AD->>C: Verifica su integridad (SHA-256 y pg_restore --list) antes de tocar nada
    AD->>S: Detiene API, worker/planificador y proxy
    AD->>DB: Conserva la base dañada renombrada hasta validar la recuperada
    AD->>C: Restaura el respaldo en una base limpia
    C->>DB: Recupera esquema y datos
    AD->>DB: Valida conteos de tablas clave, claves foráneas, restricciones únicas, último AUDIT_LOG y acceso del Administrador (CA-057-05)
    AD->>S: Arranca los servicios en el orden PostgreSQL, broker, API, worker/planificador y proxy
    S-->>AD: Sistema operando (se confirma con GET /system/status/)
    AD->>DB: INSERT AUDIT_LOG action ops:restore, origin MANUAL, con reason y detalle en new_value (CA-057-07)
    AD->>L: Registra fecha, respaldo usado, responsable y resultado
    Note over AD,L: Se avisa a los operadores que los datos posteriores al respaldo se perdieron
    Note over S,DB: El dispatcher ejecuta en su primer tick los jobs vencidos. Los eventos offline que sigan en dispositivos se reenvían y se procesan por idempotencia (client_event_id)
```

**Reglas y contratos:** RN-API-03, RN-INF-01, RN-INF-03, RF-API-03, RF-INF-03, RNF-FIA-02, RNF-FIA-03, RNF-SEG-04, KPI-32, CA-057-01 a 05 y CA-057-07. Los respaldos contienen datos de menores: permisos `0600` y copia externa solo cifrada y con autorización institucional. La restauración completa debe probarse antes de cada hito de cierre. **Los pasos de 4.13.2 reflejan el contenido mínimo del runbook** (PP §2.3); los comandos exactos viven en `docs/runbook_restauracion.md`.

---

## 5. Registro de observaciones y su resolución

Las 14 observaciones detectadas al construir estos diagramas quedaron resueltas por el paquete de parches PAQ1 (`SIGE_Parches_Observaciones_Diagramas_v1.md`) y por los cambios del Modelo de Datos v3.2. Esta tabla se conserva como registro de trazabilidad.

| # | Observación | Resolución | Dónde |
|---|---|---|---|
| 1 | QR revocado docente: `QR_NOT_RECOGNIZED` frente a `QR_REVOKED` | Se usa `QR_REVOKED` para tokens `REVOCADO` | PO-01 |
| 2 | Quinto intento fallido de login | El intento que alcanza el umbral responde `429 ACCOUNT_LOCKED` | PO-02 |
| 3 | Respuesta con sesión revocada o cuenta desactivada | `401 SESSION_REVOKED`, sin intento de renovación | PO-03, PT-01 |
| 4 | `ENTRADA` docente con `FALTA_JUSTIFICADA` manual | `422 DUPLICATE_RECORD` con `details.reason = MANUAL_STATE_PREVAILS` | PO-04 |
| 5 | `ENTRADA` o `SALIDA` en un día sin programación | Se guarda con `status` nulo e `is_scheduled = false` (RN-AST-32) | PO-05, MD-03 |
| 6 | Programación al reactivar un docente | Se conserva sin tocarse y vuelve a aplicar desde la reactivación | PO-06, MD-04 |
| 7 | `JOB_RUN` y el job docente | Un único renglón diario `GLOBAL` que se actualiza | PO-07, FE-2, MD-06 |
| 8 | Guardia de sanidad docente | Guardia basada en actividad de asistencia, con una alerta por día | PO-08 |
| 9 | Exportación de credenciales | Vista previa y exportación sin estado | PO-09 |
| 10 | Orden de arranque del servidor | PostgreSQL, broker, API, worker/planificador y proxy | PO-10 |
| 11 | Permisos de reintento de correo | Solo PAD (D-06 cerrada) | PO-11 |
| 12 | Canal de la notificación de rechazo | Aviso dentro de la aplicación, sin correo | PO-12 |
| 13 | Códigos de error sin catalogar | `DUPLICATE_TEACHER_ID`, `CONFIRMATION_REQUIRED`, `STUDENT_NOT_ACTIVE` y `TEACHER_NOT_ACTIVE` según `entity_type` | PT-01, PO-13 |
| 14 | Pasos de restauración | Contenido mínimo del runbook en nueve puntos | PO-14 |

---
