# SIGE — Estrategia de Procesos Programados (Cron & Jobs)
**Sistema Integral de Gestión Escolar**

Este documento define la arquitectura y el diseño de los procesos en segundo plano (background jobs) y tareas recurrentes (crons) requeridos por SIGE para automatizar la inserción de faltas masivas, las notificaciones asíncronas y los procesos de mantenimiento.

---

## 1. Motor de Ejecución Recomendado
Para el ecosistema basado en Django, se estipula el uso de **Celery** como framework de colas de tareas asíncronas, en conjunto con **Redis** como *message broker* y para el almacenamiento de resultados/locks. 

*   **Celery Worker:** Despachará en paralelo (y en background) tareas intensivas inducidas por eventos de los usuarios (ej. el envío de correos).
*   **Celery Beat:** Actuará como el programador de tareas y leerá las frecuencias temporales definidas para inyectar tareas al worker. Alternativamente, para un despliegue MVP más contenido, se aprueba el uso de *Django-Q*.

---

## 2. Jobs Críticos y Reglas de Negocio

### 2.1 Verificación Diaria de Ausencias (Estudiantes)
*   **Frecuencia:** Diaria (de lunes a viernes).
*   **Hora de Ejecución:** El job corre con una frecuencia corta (cada 15-30 minutos) durante todo el horario escolar, no a una sola hora fija. En cada corrida, evalúa **grupo por grupo**: un grupo entra a evaluación de ausencias solo cuando ya transcurrió su propia `GROUP.cutoff_time` más el margen configurado en `OPERATIONAL_PARAMETER['STUDENT_ABSENCE_CHECK_OFFSET_MINUTES']` (nuevo parámetro; sustituye a `STUDENT_ABSENCE_CHECK_TIME` como hora única). Esto respeta que la hora de verificación debe ser posterior a la hora de corte de cada grupo y jornada (RN-ADM-02), incluso cuando distintos grupos tienen turnos distintos.
*   **Idempotencia reforzada:** al correr cada 15-30 minutos, el `WHERE` de la consulta debe excluir explícitamente a los estudiantes que ya tienen cualquier registro de asistencia hoy (no solo `FALTO`), para no reevaluar grupos ya procesados en la corrida anterior.
*   **Lógica Principal:**
    1. Identifica a todos los alumnos (`status='ACTIVO'`) cuyo `GROUP` coincida con el turno escolar correspondiente.
    2. Compara el censo contra los registros existentes hoy en `ATTENDANCE_STUDENT`.
    3. Para todo aquel alumno sin registro oficial en la fecha, el job realiza una inserción masiva (`bulk_create`) de asistencias con `status='FALTO'` y `origin='AUTOMATICO'`.
*   **Idempotencia:** El script detecta ejecuciones dobles. Si ya existen faltas automáticas para hoy, la inserción es omitida para evitar errores de duplicidad.

### 2.2 Verificación Diaria de Ausencias (Docentes)
*   **Frecuencia:** Diaria (de lunes a viernes).
*   **Hora de Ejecución:** Dictada por `OPERATIONAL_PARAMETER['TEACHER_ABSENCE_CHECK_TIME']` (ej. 08:00 AM).
*   **Lógica Principal:**
    1. A diferencia de los estudiantes (fijos por grupo), aquí se debe unir a la tabla `TEACHER_SCHEDULE` filtrando por el día de la semana para determinar quién debía asistir hoy.
    2. Si el docente debía registrarse (`record_type='ENTRADA'`) y no figura un evento dentro de su tolerancia en `ATTENDANCE_TEACHER`, se le registra automáticamente como `FALTO` de origen automático.
*   **Flags de Anomalía (RN-AST-25):** Una segunda parte de este job (o un job separado al finalizar la tarde) evalúa registros que posean marca de `SALIDA` y levanta una bandera `SALIDA_SIN_ENTRADA` si nunca se escaneó la entrada.

### 2.3 Respaldo Automático de Base de Datos (RN-API-03)
*   **Frecuencia:** Diaria (Típicamente en horas valle, ej. 02:00 AM).
*   **Lógica Principal:**
    1. Ejecuta vía subproceso un *dump* completo (ej. `pg_dump`) de PostgreSQL.
    2. Comprime el volcado y lo guarda primero en un **volumen local** del servidor institucional (obligatorio, no depende de Internet, RN-INF-01). Si hay conectividad disponible, intenta adicionalmente una copia a un destino externo (S3 u otro) como respaldo secundario; el éxito o fallo de esta copia externa **no** determina el `status` del `BACKUP_LOG`, que se marca `EXITOSO` con solo la copia local confirmada.
    3. Genera un registro final de bitácora en la tabla `BACKUP_LOG`.
*   **Manejo de Fallos:** Si falla la exportación al volumen externo por errores de red, la tarea reintenta exponencialmente un máximo de 3 veces. Si todos los reintentos fallan, el `BACKUP_LOG` se graba con `status='FALLIDO'` y se notifica al Administrador.

### 2.4 Cola Asíncrona de Correos (RN-COM-03)
*   **Frecuencia:** Orientada a eventos. Celery delega la función `send_notification_email.delay(report_id)` inmediatamente en cuanto ocurre un registro de incidencia. 
*   **Job Recolector (Sweeper):** Cada hora, un pequeño cron revisa la tabla `COMMUNICATION_LOG` en busca de filas olvidadas en `status='PENDIENTE'` o `status='FALLIDO'` (que aún sean reintentables) e intenta despacharlas.
*   **Lógica Principal:**
    0. Antes de reintentar, verifica que el `STUDENT_GUARDIAN.consent_status` del destinatario no sea `REVOCADO` (RN-COM-04); si lo es, marca la fila como `FALLIDO` de forma permanente (sin más reintentos) y no la vuelve a tomar el sweeper.
    1. Extrae el `content_snapshot` exacto y lo envía por SMTP sin mutar información.
    2. Actualiza exitosamente a `ENVIADO`.

---

## 3. Tolerancia a Fallos y Reintentos (Resumen)

1. **Retry Policies (Políticas de Reintento):** Todos los jobs de Celery deben estar decorados con `@task(autoretry_for=(NetworkError, SMTPException), retry_backoff=True)`. Esto asegura recuperación natural sin programar lógicas repetitivas personalizadas.
2. **Mutual Exclusion (Locks):** Se usarán *Redis Locks* para garantizar que un proceso pesado como la inyección masiva de faltas de alumnos no se cruce consigo mismo si la ejecución de las 10:00 se demora más de lo esperado.
3. **Manejo de Feriados / Suspensión de Labores:** Los trabajos de inyección de asistencia validarán primero una potencial bandera global `IS_HOLIDAY` o lista de días no laborables antes de penalizar a la población entera, si se llegase a agregar este catálogo al alcance en fases futuras.
