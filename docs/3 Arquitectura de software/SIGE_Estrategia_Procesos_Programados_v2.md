# SIGE — Estrategia de Procesos Programados (Cron & Jobs)
**Sistema Integral de Gestión Escolar**

**Versión:** 2.0 | **Estado:** Para revisión del equipo
**Derivado de:** Acta v10 · RF/RNF v3 · RN v3 · HU v2 · CA v2 · Modelo de Datos v3.0

Este documento define la arquitectura y el diseño de los procesos en segundo plano (background jobs) y tareas recurrentes (crons) requeridos por SIGE para automatizar la inserción de faltas masivas, las notificaciones asíncronas y los procesos de mantenimiento.

---

## 1. Motor de Ejecución

Se usa **[Celery + Redis | Django-Q2 con broker ORM]**. *(El equipo debe marcar una opción antes de iniciar el Hito 03; el resto del documento es válido para ambas y señala las diferencias.)*

| Aspecto | Celery + Redis | Django-Q2 (broker ORM) |
|---|---|---|
| Procesos a operar en el servidor local | worker, beat, redis | cluster qcluster |
| Locks de exclusión mutua | Redis lock | `pg_try_advisory_lock` de PostgreSQL |
| Reintentos | `autoretry_for` (§3.1) | `max_attempts` + `retry` de la tarea |
| Planificación | Beat + dispatcher por condición (§2.1) | Schedules + dispatcher por condición (§2.1) |

**Principios comunes**
1. **Planificación por condición, no por reloj fijo.** Los parámetros de hora (`OPERATIONAL_PARAMETER`) son editables en caliente por el Administrador (CA-030-06), por lo que un `crontab` estático no puede seguirlos. Un *dispatcher* corre cada 5 minutos, evalúa qué jobs están vencidos y no tienen corrida registrada hoy, y encola solo esos. Esto además recupera automáticamente corridas perdidas si el servidor estuvo apagado (PP-09).
2. **Registro de corridas (`JOB_RUN`, D-04):** cada ejecución escribe `job_name`, `run_date`, `scope` (p. ej. turno), `status`, `started_at`, `finished_at`, conteos y error. `UNIQUE(job_name, run_date, scope)` es el marcador de idempotencia y la fuente del estado de salud de los procesos que ve el Administrador.
3. **Todo job es idempotente por diseño** (§3.2): marcador de corrida + filtro de elegibles + restricción única en BD.

---

## 2. Jobs Críticos y Reglas de Negocio

### 2.1 Verificación Diaria de Ausencias (Estudiantes)
*   **Trazabilidad:** US-030, US-031, RN-AST-08, RN-AST-09, RN-ADM-02, RN-TRX-07, CA-030-01..07, CA-055-07..10.
*   **Días de ejecución:** días lectivos (lunes a viernes) dentro del ciclo escolar activo (ver §3.3).
*   **Hora de verificación (fuente única):** `OPERATIONAL_PARAMETER['STUDENT_ABSENCE_CHECK_TIME_MATUTINO']` (10:00 inicial) y `OPERATIONAL_PARAMETER['STUDENT_ABSENCE_CHECK_TIME_VESPERTINO']` (16:00 inicial, provisional). La restricción "la verificación debe ser posterior a la hora de corte de todo grupo activo del turno" se valida al guardar el parámetro o el grupo (RN-ADM-02, CA-055-08..10); el job no recalcula cortes ni offsets. *No existen* `STUDENT_ABSENCE_CHECK_TIME` ni `STUDENT_ABSENCE_CHECK_OFFSET_MINUTES`.
*   **Disparo (una vez por turno y día):** el dispatcher (§1) corre cada 5 minutos y, para cada turno, encola `check_student_absences(shift, date)` solo si: (a) hoy es día lectivo con ciclo activo, (b) la hora local es mayor o igual a la hora de verificación del turno, y (c) no existe un `JOB_RUN` completado para `(check_student_absences, hoy, turno)`. No se reevalúa durante el resto del día: una persona dada de alta o reingresada después de la hora de verificación no recibe `FALTÓ` ese día.
*   **Lógica principal:**
    1. Adquirir el lock `absence_students:{date}:{shift}` (§3.2) y registrar `JOB_RUN` en estado `EN_CURSO`.
    2. Seleccionar estudiantes con `status='ACTIVO'`, cuyo `GROUP` (activo) pertenezca al turno y que **no tengan ningún registro** en `ATTENDANCE_STUDENT` con `record_date = hoy` (cualquier estado, no solo `FALTO`).
    3. Insertar con `bulk_create(batch_size=500, ignore_conflicts=True)`: `status='FALTO'`, `origin='AUTOMATICO'`, `sync_status='ONLINE'`, `group_id` = grupo vigente del estudiante (denormalizado), `record_date = hoy`, `effective_datetime = NULL` (no hubo escaneo; se llena si luego se reclasifica por RN-AST-09, D-12). El `UNIQUE(student_id, record_date)` garantiza que un escaneo concurrente gana sobre el job.
    4. Los escaneos capturados offline y aún no sincronizados **no se esperan**: el estudiante queda `FALTO` y se reclasifica al sincronizar según su hora efectiva (RN-AST-09, RN-TRX-04, US-033).
    5. Escribir **un** renglón de `AUDIT_LOG`: `action='job:absence_check_students'`, `user_id=NULL`, `origin='AUTOMATICO'`, `new_value={date, shift, evaluated, created}`. Como `bulk_create` no dispara `save()` ni señales, la auditoría se escribe explícitamente aquí (RN-AUT-05, RN-TRX-07).
    6. Cerrar `JOB_RUN` con conteos.
*   **Idempotencia (triple):** (1) marcador `JOB_RUN`; (2) filtro de estudiantes sin registro hoy; (3) `UNIQUE(student_id, record_date)` + `ignore_conflicts`. Ejecutarlo dos veces el mismo día no genera registros (CA-030-05).
*   **No retroactividad:** un cambio de parámetro rige desde su vigencia; los días anteriores no se recalculan (RN-ADM-02, CA-030-06, CA-055-05).
*   **Exclusiones:** estudiantes en `BAJA` o `EGRESADO` (CA-030-04). Un estudiante con registro incompleto (`completeness='INCOMPLETO'`) sigue siendo `ACTIVO` y sí se evalúa (RN-EST-10).

### 2.2 Verificación Diaria de Ausencias (Docentes)
*   **Trazabilidad:** US-042, RN-AST-13, RN-AST-14, RN-AST-15, RN-AST-18, RN-AST-23, RN-AST-24, RN-AST-29, RF-ADM-02, CA-042-01..06.
*   **Parámetro:** `OPERATIONAL_PARAMETER['TEACHER_ABSENCE_CHECK_OFFSET_MINUTES']` (30 inicial). **No existe una hora global** de verificación docente. El umbral de cada docente es individual: `TEACHER_SCHEDULE.expected_entry_time` del día + `max(tolerancia_efectiva, 0)` + `TEACHER_ABSENCE_CHECK_OFFSET_MINUTES` (D-07). La tolerancia efectiva es `TEACHER_SCHEDULE.punctuality_tolerance_minutes` o, si es nula, `TEACHER_DEFAULT_TOLERANCE_MINUTES`.
*   **Disparo:** el dispatcher (§1) corre cada 5 minutos y encola `check_teacher_absences(date)`; el job solo procesa docentes cuyo umbral individual ya pasó hoy. Es idempotente por la condición de selección (un docente con renglón de `ENTRADA` hoy deja de ser elegible) y por la restricción única.
*   **Lógica principal:**
    1. Seleccionar docentes con `TEACHER.status='ACTIVO'` y un `TEACHER_SCHEDULE` con `is_active=true` y `weekday = día de hoy` (RN-AST-18: sin programación hoy no hay ausencia).
    2. Filtrar los que ya superaron su umbral individual.
    3. Excluir a quienes ya tienen cualquier renglón `ATTENDANCE_TEACHER` con `record_type='ENTRADA'` hoy. La tolerancia **no** interviene aquí: define `LLEGÓ TARDE` al registrar, no `FALTÓ`.
    4. Insertar con `bulk_create(ignore_conflicts=True)`: `record_type='ENTRADA'`, `status='FALTO'`, `origin='AUTOMATICO'`, `anomaly_flag='NINGUNA'`, `effective_datetime=NULL` (D-12). Se guarda como `ENTRADA` para que el `UNIQUE(teacher_id, record_date, record_type)` permita que el registro posterior de la entrada **actualice este mismo renglón** (RN-AST-24, sin contarse como segunda entrada, RN-AST-13) en vez de rechazarse como duplicado.
    5. Escribir un renglón de `AUDIT_LOG` (`action='job:absence_check_teachers'`, `user_id=NULL`, `origin='AUTOMATICO'`, conteos) y cerrar `JOB_RUN`.
*   **Nota sobre `SALIDA_SIN_ENTRADA`:** la marca no es responsabilidad de este job. La asigna el endpoint de registro de `SALIDA` en el mismo instante (RN-AST-25, CA-041-05; ver API-02). Una `SALIDA` posterior a un `FALTÓ` automático también es "sin entrada", porque ese `FALTÓ` no cuenta como `ENTRADA` (RN-AST-13).

### 2.3 Respaldo Automático de Base de Datos (RN-API-03)
*   **Trazabilidad:** US-057, RN-API-03, RN-INF-01, RN-INF-03, RF-API-03, RNF-FIA-03, RNF-SEG-04, CA-057-01..04.
*   **Frecuencia:** diaria como mínimo (RF-API-03), 02:00 por defecto. La periodicidad es configurable (RN-API-03) mediante `OPERATIONAL_PARAMETER['BACKUP_FREQUENCY_HOURS']` (24 por defecto; ver §7, I-01). **Recuperación de corridas perdidas:** el dispatcher (§1) evalúa en cada tick si el último `BACKUP_LOG` con `status='EXITOSO'` es más antiguo que la frecuencia y, de ser así, ejecuta el respaldo de inmediato (la PC servidor puede estar apagada a la hora programada).
*   **Lógica principal:**
    1. Ejecutar por subproceso `pg_dump -Fc` hacia un archivo temporal en el **volumen local de respaldos**, que debe ser un disco o partición **distinto** del de datos de PostgreSQL (R-14). Obligatorio, no depende de Internet (RN-INF-01).
    2. **Verificar integridad:** `pg_restore --list` sobre el archivo y cálculo de SHA-256. Si falla, el respaldo es `FALLIDO`.
    3. Mover el archivo al destino final con permisos `0600` y propietario el usuario de servicio (datos de menores, RNF-SEG-04).
    4. Registrar `BACKUP_LOG`: `status` = resultado **únicamente** del respaldo local verificado; `size_bytes`; `offsite_status='N_A'` si no hay copia externa configurada.
    5. **Copia externa (opcional, apagada por defecto; D-05):** solo si la institución la autorizó por escrito. El archivo se cifra antes de salir del servidor. Si hay conectividad se intenta; ante error de red se reintenta con retroceso exponencial hasta 3 veces. El resultado se registra solo en `offsite_status` (`EXITOSO`/`FALLIDO`); **nunca** modifica `status`.
    6. **Retención:** conservar al menos los últimos 7 respaldos diarios y 4 semanales (ajustable al espacio disponible); la rotación nunca elimina el último respaldo `EXITOSO` verificado.
*   **Manejo de fallos del respaldo local:** reintento hasta 3 veces con retroceso exponencial ante causas transitorias (disco, conexión a la BD). Si todos fallan: `BACKUP_LOG.status='FALLIDO'` y **alerta visible en el panel del Administrador** (CA-057-02, US-057). El correo al Administrador es un canal adicional "mejor esfuerzo" que depende de Internet (RN-INF-02); la alerta en el sistema es la que cuenta.
*   **Restauración (RF-API-03, RNF-FIA-03, RN-INF-03):** procedimiento documentado en el runbook de operación (`docs/runbook_restauracion.md`), ejecutado por el Administrador/operador técnico desde consola, no por API pública. Debe probarse con una restauración completa antes de cada hito de cierre, verificando integridad (KPI-32, KPI-67).

### 2.4 Cola Asíncrona de Correos (RN-COM-03)
*   **Trazabilidad:** US-050, US-052, US-053, RN-REP-04, RN-REP-07, RN-COM-01..04, RN-INF-02, CA-052-*, CA-053-*.
*   **Disparador:** la acción explícita del Personal administrativo "Comunicar a la familia" (`POST /api/v1/reports/{id}/communications/`, ver API-02). **Nunca** el registro del reporte ni su revisión por el prefecto (RN-REP-04).
*   **Validaciones previas al primer envío (síncronas, en la API; si fallan responden 422 y no crean renglón):**
    1. El reporte está en `REVISADO_ADMINISTRATIVO` o `AUTORIZADO` (RN-REP-03/07).
    2. Existe al menos un tutor con `is_valid_contact=true` **y correo electrónico** (RN-COM-01, RN-EST-11). Si no existe, el reporte pasa a `AUTORIZADO` (pendiente de contacto válido, RN-REP-07) y no se envía nada.
    3. El tutor destinatario no tiene `consent_status='REVOCADO'` (RN-COM-04; CA-052-08: se rechaza y se advierte al PAD).
    4. El contenido a enviar es el aprobado en la vista previa (RN-COM-02, US-052) y se guarda como `content_snapshot`.
*   **Encolado:** en una sola transacción se crea el renglón `COMMUNICATION_LOG` (`PENDIENTE`) y, con `transaction.on_commit`, se encola `send_notification_email.delay(communication_log_id)`.
*   **Lógica del job `send_notification_email`:**
    0. Releer el renglón; si no está `PENDIENTE`, terminar (idempotencia). Releer `consent_status`; si es `REVOCADO`, marcar `FALLIDO` permanente y no reintentar.
    1. Enviar por SMTP el `content_snapshot` exacto, sin mutarlo.
    2. Éxito → `ENVIADO`; en la misma transacción el reporte transiciona `COMUNICADO` y luego `RESUELTO` (RN-REP-07a), con dos renglones en `REPORT_TRANSITION_LOG` de origen sistema (`changed_by = NULL`, ver §7 I-04).
    3. Error de red o SMTP → reintento automático con retroceso exponencial hasta `COMMUNICATION_MAX_AUTO_ATTEMPTS` (3 por defecto, ver §7 I-01). Si se agotan: `FALLIDO` y queda disponible el reintento manual del Personal administrativo (CA-053-02).
    4. **Cada intento deja huella** (RN-COM-03, CA-053-03): un renglón por intento; un reintento manual crea un renglón nuevo con `retried_by` y conserva el fallido (ver §7 I-03). El estado `ENVIADO` nunca se presenta como "leído".
*   **Job recolector (sweeper), cada hora:** toma renglones `PENDIENTE` con más de 15 minutos de antigüedad (huérfanos por reinicio del worker) y `FALLIDO` con intentos automáticos restantes. No toma `FALLIDO` permanentes ni agotados. Si no hay Internet (RN-INF-02) no consume intentos: deja el renglón `PENDIENTE` y la interfaz muestra "sin Internet" (US-052). También revisa reportes en `AUTORIZADO` cuyo tutor ya tenga un contacto válido con correo y los devuelve al flujo de envío (RN-REP-07).
### 2.5 Mantenimiento
*   **Sesiones vencidas:** diario, marca como `revoked_reason='EXPIRED'` las `USER_SESSION` vencidas y no revocadas. La validación de la sesión en cada petición no depende de este job; es solo higiene de datos.
*   **Archivos de importación:** cada hora, elimina del almacenamiento privado los archivos de lotes `CANCELADO` o en `VISTA_PREVIA` con más de 24 horas y marca el lote `CANCELADO`. Los archivos contienen datos de menores (minimización, RN-TRX-01); el `IMPORT_BATCH` y sus `IMPORT_ROW_ERROR` se conservan (RN-TRX-03). Ver §7 I-06.
*   **Rotación de respaldos:** parte de §2.3.
---

## 3. Tolerancia a Fallos y Reintentos (Resumen)

1. **Políticas de reintento por job.** Se declaran explícitamente en cada tarea; no hay una política única.

| Job | Excepciones reintentables | Máx. reintentos | Retroceso |
|---|---|---|---|
| `send_notification_email` | `smtplib.SMTPException`, `OSError` (incluye errores de conexión y timeouts) | `COMMUNICATION_MAX_AUTO_ATTEMPTS` (3) | exponencial con *jitter*, tope 15 min |
| `check_student_absences`, `check_teacher_absences` | `django.db.OperationalError` | 3 | exponencial, tope 5 min |
| `run_backup` (copia local) | `OSError`, `subprocess.CalledProcessError` | 3 | exponencial, tope 10 min |
| `run_backup` (copia externa) | `OSError` | 3 | exponencial; su fallo no cambia `status` (§2.3) |

Ejemplo (Celery):

```python
from celery import shared_task
import smtplib

@shared_task(bind=True,
             autoretry_for=(smtplib.SMTPException, OSError),
             retry_backoff=True, retry_backoff_max=900, retry_jitter=True,
             max_retries=3, acks_late=True)
def send_notification_email(self, communication_log_id): ...
```

*Variante Django-Q2:* configurar `max_attempts` y `retry` por tarea y registrar el resultado en `JOB_RUN`.

2. **Mutual Exclusion (Locks):** Se usarán *Redis Locks* para garantizar que un proceso pesado como la inyección masiva de faltas de alumnos no se cruce consigo mismo si la ejecución de las 10:00 se demora más de lo esperado.
3. **Guardias previas a la inserción masiva de faltas.** Antes de §2.1 y §2.2, el job valida:
   *   **Ciclo activo (ya disponible en el modelo):** existe un `ACADEMIC_CYCLE` con `is_active=true` y `start_date ≤ hoy ≤ end_date`. Si no, el job no corre y registra aviso en `JOB_RUN`.
   *   **Guardia de sanidad (D-03):** si a la hora de verificación un turno completo tiene **cero** escaneos registrados hoy y cero eventos offline pendientes de sincronizar conocidos por el servidor, el job **no inserta** faltas, deja `JOB_RUN.status='OMITIDO'` y genera una alerta visible al Administrador, quien puede ejecutar manualmente la verificación tras confirmar que fue un día lectivo. Motivo: los registros de asistencia son permanentes (RN-AST-06, RN-TRX-03) y la única corrección es justificar uno por uno (RN-AST-22).
   *   **Catálogo de días no laborables:** no está en el alcance actual; incorporarlo requiere control de cambios (el job lo consultaría como una tercera guardia).
4. **Reloj, zona horaria y equipo apagado (RNF-FIA-04).**
   *   Django `TIME_ZONE` y el planificador (`CELERY_TIMEZONE` o equivalente) usan la zona horaria institucional, con `USE_TZ=True`. Todas las horas de los parámetros se interpretan en esa zona.
   *   El servidor mantiene su reloj sincronizado (chrony/NTP). Sin Internet existe un procedimiento documentado de verificación y ajuste manual al inicio de cada jornada; los jobs de ausencias no deben iniciar si el reloj difiere más de 2 minutos de la referencia local registrada.
   *   La PC servidor puede estar apagada fuera de horario: como el dispatcher decide por condición (§1), cualquier job vencido se ejecuta en el primer tick tras el arranque (respaldos incluidos, §2.3). Se documenta en el runbook que el arranque del servidor debe iniciar proxy, API, base de datos y worker/planificador en ese orden.
