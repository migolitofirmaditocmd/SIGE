# SIGE — Runbook de Recuperación y Restauración

**Archivo:** `docs/runbook_restauracion.md`
**Versión:** 0.1 | **Estado:** Borrador, por validar en la primera prueba de restauración (§8)
**Trazabilidad:** RF-API-03, RF-INF-03, RNF-FIA-02, RNF-FIA-03, RNF-FIA-04, RN-API-03, RN-INF-01, RN-INF-03, US-057, CA-057-03 a CA-057-07, PP §2.3 y §3, KPI-32, KPI-67

---

## 0. Antes de usar este documento

1. **Los comandos son plantillas.** Se redactaron a partir de lo que fijan los documentos de SIGE (PostgreSQL, `pg_dump -Fc`, `pg_restore`, servidor Linux local), pero **todavía no se han ejecutado en el servidor real**. La primera prueba de restauración (§8) es la que valida este documento; los ajustes que salgan de ella se registran en el §10.
2. **Los valores entre ⟦dobles corchetes⟧ se completan al desplegar** (§1). Mientras no estén completos, el runbook no se considera listo para una emergencia.
3. **No restaure si no hace falta.** Si PostgreSQL arranca y los datos están íntegros, una restauración borra todo lo capturado después del último respaldo. Use el árbol de decisión del §3.

---

## 1. Parámetros del entorno (completar al desplegar)

| Parámetro | Valor | Nota |
|---|---|---|
| Directorio de respaldos (`BACKUP_DIR`) | ⟦/ruta/del/volumen-de-respaldos⟧ | Disco o partición **distinta** de la de datos de PostgreSQL (R-14) |
| Nombre de los archivos de respaldo | ⟦sige_AAAAMMDD_HHMMSS.dump⟧ | Convención por confirmar (ver P-R2, §10) |
| Base de datos de producción (`DB_NAME`) | ⟦sige⟧ | |
| Rol propietario de la base (`DB_OWNER`) | ⟦sige_owner⟧ | Ejecuta migraciones y la restauración |
| Rol de la aplicación (`DB_APP_ROLE`) | ⟦sige_app⟧ | Sin `DELETE` sobre `AUDIT_LOG`, `ATTENDANCE_*`, `INCIDENT_REPORT` ni `REPORT_TRANSITION_LOG`, y solo `INSERT` sobre `AUDIT_LOG` (SEG §8) |
| Servicios del sistema (Docker Compose) | `db`, `api`, `worker` (qcluster), `web` y `proxy` | Definidos en `docker-compose.yml` (Plan de Despliegue §5.4). No hay Redis (D-02 = Django-Q2) |
| Usuario de servicio | ⟦sige⟧ | Propietario de los respaldos con permisos `0600` |
| Directorio del despliegue | ⟦/srv/sige⟧ | Donde está `docker-compose.yml`; desde ahí se ejecuta `docker compose` |
| Responsable técnico principal | ⟦nombre y contacto⟧ | |
| Responsable suplente | ⟦nombre y contacto⟧ | |
| Quien autoriza (institución) | ⟦Administrador o Directivo⟧ | Ver §2 |

Nombres físicos de tablas: `accounts_user` está confirmado en el Modelo §3.1. Los demás siguen la convención de Django (`<app>_<modelo>`); confírmenlos con `\dt` en `psql` y anótenlos aquí cuando los usen las consultas del §6.

---

## 2. Alcance, roles y metas de recuperación

**Qué cubre:** restaurar la base de datos de SIGE desde un respaldo local verificado, y recuperar el servicio en el servidor de la institución o en un equipo de reemplazo (RN-INF-03, CA-057-04).

**Qué no cubre:** restaurar la aplicación desde cero (código, certificado, configuración del proxy). Eso corresponde a la documentación de instalación (CA-057-06). El §7 indica qué debe estar listo antes de restaurar en un equipo de reemplazo.

| Rol | Responsabilidad |
|---|---|
| **Administrador / Directivo** | Autoriza la restauración y recibe el aviso final. Es el único usuario de SIGE con acceso a `GET /ops/backups/`. |
| **Operador técnico** (o el Administrador, si tiene los conocimientos) | Ejecuta el procedimiento por consola. **No hay API pública de restauración** (PP §2.3). |

**Metas:**

| Meta | Valor | Origen |
|---|---|---|
| **Pérdida máxima de datos (RPO)** | Hasta `BACKUP_FREQUENCY_HOURS` (24 h por defecto). Se pierde todo lo capturado después del último respaldo verificado. | PP §2.3 |
| **Tiempo máximo de recuperación (RTO)** | **4 horas** dentro de la jornada si el servidor se recupera en el mismo equipo (escenarios A y C); **la siguiente jornada escolar** si hay que usar un equipo de reemplazo (escenario B) | Valor inicial (Plan de Despliegue §7.2, RNF-FIA-02). Se revisa con el primer tiempo real de la prueba de restauración |

---

## 3. ¿Realmente hay que restaurar?

```
¿El servidor responde a GET /api/v1/system/status/ ?
├─ Sí, y `database` está bien ─────────────→ NO restaurar. Revisar la alerta original.
└─ No, o los datos están dañados
   ├─ ¿PostgreSQL arranca?
   │  ├─ Sí → ¿hay corrupción lógica (datos borrados o alterados por error)?
   │  │       ├─ Sí → Escenario A (§6)
   │  │       └─ No → reiniciar los servicios en el orden de §6, paso 9, y comprobar
   │  └─ No arranca (disco, archivos de datos, sistema operativo)
   │          ├─ ¿El mismo equipo se puede reparar en el día? → repararlo y Escenario A
   │          └─ No → Escenario B: equipo de reemplazo (§7)
   └─ Prueba programada antes de un hito → Escenario C (§8)
```

---

## 4. Contingencia mientras el sistema está caído

El documento de requisitos exige un procedimiento de contingencia ante caídas (RNF-FIA-02). Lo que ya está diseñado:

- **Escaneo estudiantil:** la PWA guarda los eventos sin conexión en su buffer (hasta 1,000, RN-MOV-02) y los sincroniza al volver el servidor. Los operadores deben **mantener abierta la aplicación** (en iOS la sincronización la requiere abierta).
- **Asistencia docente, reportes y consultas** no tienen modo sin conexión. Propuesta para la institución: llevar un registro en papel de entradas y salidas docentes y de reportes, y capturarlo al restablecer el servicio. ⟦Confirmar con la institución⟧.
- **Correo:** depende de Internet y de la cola; los envíos quedan `PENDIENTE` y salen al recuperar el servicio (RN-INF-02, PP §2.4).

El responsable técnico avisa al Administrador al inicio de la caída y cada vez que cambie la estimación de recuperación.

---

## 5. Antes del paso 1: materiales

- [ ] Autorización del Administrador o Directivo (por escrito o en la bitácora del §11).
- [ ] Acceso por consola al servidor (usuario con permisos para detener servicios y operar PostgreSQL).
- [ ] Acceso al `BACKUP_DIR` (o a una copia externa si la institución la autorizó, D-05).
- [ ] Este runbook y la plantilla del Anexo A.
- [ ] Espacio libre en disco suficiente para la base restaurada **y** para conservar la base dañada (orientativo: como mínimo el doble del tamaño del respaldo).

---

## 6. Escenario A: restauración en el mismo servidor

Corresponde a los nueve puntos mínimos que fijó PP §2.3. El Anexo C relaciona cada punto con el paso que lo cubre; los pasos 8, 11 y 12 son medidas de seguridad y de reconciliación adicionales al mínimo.

### Paso 1. Autorizar y registrar el inicio

Anote en el Anexo A: fecha y hora de inicio, motivo, quién autoriza y quién ejecuta. Avise a los operadores que el sistema queda fuera de servicio (§4).

### Paso 2. Elegir el respaldo

Si la aplicación responde, el Administrador consulta `GET /api/v1/ops/backups/` y anota el respaldo más reciente con `status = EXITOSO`. Si la base no responde, elija desde el propio volumen:

```bash
ls -lt "$BACKUP_DIR" | head -20
```

Tome **el más reciente que pase el paso 3**. Nunca use uno marcado como `FALLIDO` ni un archivo temporal incompleto. La rotación conserva siempre el último `EXITOSO` verificado (PP §2.3).

Anote el nombre, la fecha y la hora del respaldo elegido: de ahí sale el momento desde el cual se perdieron datos.

### Paso 3. Verificar la integridad antes de tocar nada

```bash
export BACKUP_FILE="$BACKUP_DIR/⟦nombre_del_respaldo.dump⟧"

# 1) Huella: debe coincidir con la guardada al crear el respaldo
sha256sum "$BACKUP_FILE"
cat "$BACKUP_FILE.sha256"            # ⟦confirmar dónde se guarda, ver P-R2⟧

# 2) El archivo debe poder listarse sin errores
pg_restore --list "$BACKUP_FILE" > /dev/null && echo "LISTADO OK"
```

Si alguna de las dos falla, **descarte ese respaldo** y vuelva al paso 2 con el anterior.

### Paso 4. Detener los servicios de SIGE

Detenga en este orden, de cara al usuario hacia adentro, para que nadie escriba durante la restauración. PostgreSQL permanece encendido.

```bash
cd ⟦/srv/sige⟧
docker compose stop proxy worker web api      # PostgreSQL permanece encendido
```

> **Importante:** el worker debe estar detenido antes de seguir. Si el planificador corriera durante la restauración, podría ejecutar jobs vencidos sobre una base incompleta.

### Paso 5. Conservar la base dañada

No la borre hasta validar la recuperada: puede contener datos posteriores al respaldo (paso 12).

```bash
# Cerrar conexiones restantes y renombrar
docker compose exec db psql -U ⟦postgres⟧ -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();"
docker compose exec db psql -U ⟦postgres⟧ -c "ALTER DATABASE $DB_NAME RENAME TO ${DB_NAME}_danada_$(date +%Y%m%d);"
```

Si PostgreSQL no puede abrir la base, omita este paso y anótelo en el Anexo A.

### Paso 6. Restaurar en una base limpia

```bash
docker compose exec db createdb -U ⟦postgres⟧ -O "$DB_OWNER" "$DB_NAME"

# El volumen de respaldos está montado en el contenedor de la base, en /backups
docker compose exec -T db pg_restore \
  -U ⟦postgres⟧ \
  --dbname="$DB_NAME" \
  --role="$DB_OWNER" \
  --no-owner \
  --exit-on-error \
  --verbose \
  "/backups/$(basename "$BACKUP_FILE")" 2>&1 | tee "/tmp/restauracion_$(date +%Y%m%d_%H%M).log"
```

Notas:
- **No use `--no-acl`.** Los permisos de la aplicación (solo `INSERT` en `AUDIT_LOG`, sin `DELETE` en asistencia y reportes) viajan en el respaldo y se comprueban en el paso 7.
- La extensión `unaccent` (migración `0001_extensions`, MIG §3) debe existir antes de usar la base. El respaldo la incluye; si `pg_restore` falla por privilegios, créela con un superusuario (`CREATE EXTENSION IF NOT EXISTS unaccent;`) y repita.
- `pg_restore` debe ser de una versión igual o posterior a la de `pg_dump` que generó el respaldo.
- Si hay errores, **no continúe**: revise el registro, corrija la causa y repita desde `createdb` (borre la base nueva antes con `dropdb "$DB_NAME"`; la dañada sigue conservada con otro nombre).

### Paso 7. Validar la base recuperada (CA-057-05)

```bash
# a) Estadísticas y conteos de tablas principales
docker compose exec db psql -U ⟦postgres⟧ -d "$DB_NAME" -c "ANALYZE;"
docker compose exec db psql -U ⟦postgres⟧ -d "$DB_NAME" -c "SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY relname;"

# b) El esquema coincide con la versión del código desplegado
docker compose run --rm api python manage.py check
docker compose run --rm api python manage.py migrate --check          # no debe haber migraciones pendientes

# c) Los permisos de la aplicación siguen como en producción
docker compose exec db psql -U ⟦postgres⟧ -d "$DB_NAME" -c "\dp"
```

Revise con el Administrador:

- [ ] `pg_restore` terminó sin errores.
- [ ] Las tablas principales tienen filas: usuarios, estudiantes, tutores, docentes, asistencia, reportes, auditoría, parámetros operativos y ciclo escolar.
- [ ] `python manage.py migrate --check` no reporta migraciones pendientes.
- [ ] El rol `⟦sige_app⟧` **no** tiene `DELETE` sobre `AUDIT_LOG`, `ATTENDANCE_*`, `INCIDENT_REPORT` ni `REPORT_TRANSITION_LOG`, y solo `INSERT` sobre `AUDIT_LOG` (SEG §8).
- [ ] El último renglón de `AUDIT_LOG` es de una hora cercana a la del respaldo (confirme el nombre físico de la tabla con `\dt`).
- [ ] El Administrador puede iniciar sesión (se prueba en el paso 10).

### Paso 8. Invalidar sesiones y enlaces anteriores *(medida de seguridad adicional)*

La base recuperada trae el estado de **cuando se hizo el respaldo**: sesiones que después se cerraron, revocaron o rotaron aparecerían vigentes otra vez, y los enlaces de restablecimiento de contraseña ya usados volverían a estar disponibles. Para cerrar esa puerta:

```sql
-- Cerrar todas las sesiones vigentes: todos los usuarios deberán iniciar sesión de nuevo
UPDATE ⟦accounts_usersession⟧
   SET revoked_at = now(), revoked_reason = 'ADMIN_INVALIDATION'
 WHERE revoked_at IS NULL;

-- Invalidar enlaces de restablecimiento de contraseña pendientes
-- (⟦confirmar el nombre físico y la columna de uso en el Modelo §3.1⟧)
```

Esto se ejecuta con el rol propietario, no con el rol de la aplicación. `REUSE_DETECTED` y `ROTATED` no aplican aquí: `ADMIN_INVALIDATION` es el motivo definido para invalidar por compromiso (Modelo §3.1).

### Paso 9. Arrancar los servicios en el orden indicado

Orden fijado en PP §3: **PostgreSQL, API, worker/planificador y, por último, el proxy**.

```bash
docker compose ps db                        # ya encendido
docker compose up -d api
# ← detenerse aquí: leer la advertencia de abajo antes de encender el worker
docker compose up -d worker web
docker compose up -d proxy
```

> **Advertencia antes de encender el worker.** Si la restauración se hace después de la hora de verificación de ausencias (10:00 matutino, 16:00 vespertino) y el respaldo es anterior al inicio de la jornada, la base no tiene los escaneos de hoy. Al encender el worker:
> - La **guardia de sanidad** (D-03) debe detectar que no hay escaneos en el turno y dejar `JOB_RUN` en `OMITIDO` con una alerta al Administrador, sin insertar faltas. Verifíquelo en el paso 10.
> - Si la jornada ya tenía escaneos registrados **antes** del respaldo, la guardia no se activa y el job evaluará solo a quienes no tengan registro en la base recuperada.
> - **No ejecute manualmente la verificación de ausencias** hasta recapturar la asistencia de hoy: los registros `FALTO` son permanentes (RN-AST-06) y solo se corrigen uno por uno.

Antes de encender el proxy, confirme que la hora del servidor es correcta (`chronyc tracking` o `date`). Los jobs de ausencias **no inician** si el reloj difiere más de 2 minutos (PP §3, punto 4).

### Paso 10. Comprobar la operación

- [ ] `GET /api/v1/system/status/` responde con `database` correcto y una `server_time` coherente.
- [ ] El Administrador inicia sesión y abre el panel de procesos (`JOB_RUN`) y respaldos (`GET /ops/backups/`).
- [ ] Un operador realiza un escaneo de prueba de un QR conocido y la respuesta es la esperada (`REGISTRADO` o `DUPLICADO_IGNORADO`).
- [ ] Un PAD consulta el expediente de un estudiante conocido.
- [ ] El `JOB_RUN` de hoy muestra el comportamiento descrito en la advertencia del paso 9.

### Paso 11. Registrar la restauración

Complete el Anexo A y archívelo **fuera de la base restaurada** (PP §2.3). Además, inserte el renglón de auditoría `ops:restore` (Modelo §3.13, CA-057-07):

```sql
-- Con el rol propietario: INSERT en AUDIT_LOG (nombre físico por confirmar)
-- action = 'ops:restore', origin = 'MANUAL', user_id = NULL
-- new_value = {"respaldo": "...", "responsable": "...", "resultado": "..."}, reason = 'motivo'
```

El respaldo siguiente de SIGE recogerá este renglón; mientras tanto, la bitácora externa es la fuente.

### Paso 12. Reconciliar lo ocurrido después del respaldo *(medida de seguridad adicional)*

Todo cambio posterior al respaldo se perdió, **incluidos los cambios de seguridad y de privacidad**. Si la base dañada es legible, consulte en ella (solo lectura) qué cambió desde la hora del respaldo; si no, el Administrador usa su memoria y los avisos recibidos. Revise y reaplique lo que corresponda (detalle en el Anexo D):

- QR revocados por pérdida o robo (el token volvería a estar `VIGENTE`).
- Cuentas desactivadas, bloqueadas, cambios de rol o contraseñas restablecidas.
- Consentimientos de tutores revocados (RN-COM-04): evitan comunicar a quien ya no autorizó.
- Bajas, egresos y reingresos de estudiantes; altas y desactivaciones de docentes.
- Reportes registrados y transiciones de etapa.
- Escaneos y registros de asistencia de la jornada (los eventos que los dispositivos aún conservan en su buffer se reenvían solos y se procesan por idempotencia, `client_event_id`; los que ya se habían sincronizado antes de la caída se perdieron y hay que recapturarlos).

### Paso 13. Comunicar

Avise al Administrador y a los operadores: hora de restablecimiento, hora del respaldo usado y lista de lo que debe recapturarse. Todos los usuarios tendrán que iniciar sesión de nuevo (paso 8).

---

## 7. Escenario B: equipo de reemplazo

Se usa cuando el servidor no se puede reparar (CA-057-04, CA-057-06). La restauración de la base es la misma del §6; antes hay que dejar el equipo operativo.

**Debe existir antes de restaurar** (según la documentación de instalación):

- [ ] Linux con reloj sincronizado (`chrony`) y la **zona horaria institucional** (RNF-FIA-04). Sin Internet, ajustar la hora manualmente y verificarla.
- [ ] PostgreSQL de versión igual o posterior a la del respaldo, y la extensión `unaccent` disponible.
- [ ] El código de SIGE desplegado en la **misma versión** que el servidor anterior (si no se conoce, la de la última versión estable) y su entorno (`TIME_ZONE`, planificador con la zona institucional, `USE_TZ=True`).
- [ ] Certificado TLS de la CA interna instalado en el proxy y la IP o nombre del servidor igual al anterior, para que los dispositivos no pierdan la confianza (RNF-SEG-01).
- [ ] El usuario de servicio, los roles de PostgreSQL y los permisos `0600` del volumen de respaldos.
- [ ] El volumen de respaldos montado con el último respaldo disponible (o la copia externa cifrada, D-05, con su clave).

Después ejecute del paso 1 al 13 del §6 (el paso 5 no aplica). No ejecute `migrate` hasta validar el estado en el paso 7: si el código es más reciente que el respaldo, `migrate --check` mostrará migraciones pendientes y el Administrador decide si aplicarlas.

---

## 8. Escenario C: prueba de restauración (antes de cada hito de cierre)

RNF-FIA-03 y CA-057-05 exigen una restauración completa **antes de cada hito de cierre**, verificando la integridad de lo recuperado. Se hace **sin tocar producción**: en el mismo servidor con otro nombre de base, o mejor, en otro equipo.

1. Elija el último respaldo `EXITOSO` y verifique su integridad (paso 3).
2. Cree una base de prueba y restaure:

```bash
docker compose exec db createdb -U ⟦postgres⟧ -O "$DB_OWNER" "${DB_NAME}_prueba"
docker compose exec -T db pg_restore -U ⟦postgres⟧ --dbname="${DB_NAME}_prueba" --role="$DB_OWNER" --no-owner --exit-on-error "/backups/$(basename "$BACKUP_FILE")"
```

3. Ejecute las validaciones del paso 7 contra `${DB_NAME}_prueba` (con la configuración de la aplicación apuntada a esa base, en un entorno aislado).
4. Complete el Anexo B y anótelo en la bitácora.
5. Elimine la base de prueba al terminar (`dropdb`), pues contiene datos de menores.

**Criterio de aprobación:** `pg_restore` sin errores, `migrate --check` sin migraciones pendientes, permisos del rol de la aplicación correctos, conteos coherentes con producción al momento del respaldo, inicio de sesión del Administrador y un escaneo de prueba exitosos. Con el 100 % de los respaldos de prueba recuperados (CA-057-03).

**Registre además:** el tiempo total que tomó la restauración. Es el primer dato real para revisar el RTO inicial (§2).

---

## 9. Problemas frecuentes

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| `pg_restore` falla con permisos o propietarios | Roles distintos a los del respaldo | Use `--no-owner --role="$DB_OWNER"` y confirme que el rol existe |
| Error con la extensión `unaccent` | Falta la extensión o privilegios | `CREATE EXTENSION IF NOT EXISTS unaccent;` con superusuario y repetir |
| Errores de versión en `pg_restore` | `pg_restore` más antiguo que el `pg_dump` | Usar la misma versión mayor de PostgreSQL o una posterior |
| `migrate --check` reporta migraciones pendientes | El código es más reciente que el respaldo | No aplicar a ciegas: el Administrador decide; respalde antes (MIG §6) |
| Todo el mundo recibe 401 | Es lo esperado tras el paso 8 | Iniciar sesión de nuevo |
| El `JOB_RUN` queda `OMITIDO` con alerta | La guardia de sanidad no vio escaneos hoy | Es esperable tras una restauración; ver advertencia del paso 9 |
| Los jobs de ausencias no inician | Reloj con más de 2 minutos de diferencia | Corregir la hora y esperar el siguiente tick (cada 5 min) |
| `database` falla en `/system/status/` | La aplicación no alcanza PostgreSQL | Revisar el servicio `db` (`docker compose ps db` y sus registros), el rol de la app y las credenciales del archivo de entorno |
| No hay espacio para restaurar | La base dañada ocupa el disco | Mover la base dañada a otro disco o comprimirla antes de continuar |

---

## 10. Pendientes de este runbook

| # | Pendiente | Quién |
|---|---|---|
| **P-R1** | **Cerrado:** RTO inicial de 4 horas en el mismo equipo y la siguiente jornada con equipo de reemplazo (§2). Se revisa con la primera prueba de restauración | Institución |
| **P-R2** | **Dónde se guarda la huella SHA-256 y el nombre del archivo.** PP §2.3 calcula el SHA-256, pero `BACKUP_LOG` no tiene columna para la ruta ni la huella. Propuesta: que el job escriba `<archivo>.sha256` junto al respaldo y anote el nombre en `BACKUP_LOG.notes`. Es un ajuste a PP §2.3. | Equipo de desarrollo |
| **P-R3** | Completar los parámetros del §1 (rutas, servicios, roles) al desplegar. | Operación |
| **P-R4** | Confirmar la contingencia manual del §4 con la institución. | Institución |
| **P-R5** | Ejecutar la primera prueba de restauración, corregir los comandos que no funcionen y subir este documento a 1.0. | Operación |
| **P-R6** | Confirmar nombres físicos de tablas para las consultas SQL de los pasos 7, 8 y 11. | Desarrollo |

---

## 11. Anexos

### Anexo A. Registro de restauración

```
Fecha y hora de inicio:        ______________________
Fecha y hora de término:       ______________________
Escenario:                     A / B / C (prueba)
Motivo:                        ______________________
Autorizó:                      ______________________
Ejecutó:                       ______________________
Respaldo usado (archivo):      ______________________
Fecha y hora del respaldo:     ______________________
Verificación (SHA-256, list):  OK / FALLÓ
Base dañada conservada como:   ______________________   (o "no aplica")
pg_restore sin errores:        Sí / No
migrate --check:               Sin pendientes / Con pendientes
Permisos del rol de la app:    Correctos / Incorrectos
Sesiones invalidadas (paso 8): Sí / No
Resultado del paso 10:         ______________________
JOB_RUN del día:               ______________________
Reconciliación (paso 12):      ______________________
Tiempo total de restauración:  ______________________
Observaciones:                 ______________________
```

### Anexo B. Checklist de la prueba antes de un hito

- [ ] Respaldo elegido y verificado (SHA-256 y `pg_restore --list`)
- [ ] Restauración en base de prueba sin errores
- [ ] `manage.py check` y `migrate --check` correctos
- [ ] Permisos del rol de la aplicación correctos
- [ ] Conteos de tablas principales coherentes
- [ ] Inicio de sesión del Administrador exitoso
- [ ] Escaneo de prueba exitoso
- [ ] Tiempo total anotado
- [ ] Base de prueba eliminada
- [ ] Anexo A archivado en la bitácora

### Anexo C. Los nueve puntos mínimos de PP §2.3 y dónde se cubren

| Punto mínimo | Paso |
|---|---|
| 1. Cuándo se usa y quién autoriza | §3 y §2, paso 1 |
| 2. Elegir el último respaldo `EXITOSO` verificado | Paso 2 |
| 3. Verificar su integridad antes de tocar nada | Paso 3 |
| 4. Detener API, worker/planificador y proxy; conservar la base dañada | Pasos 4 y 5 |
| 5. Restaurar en una base limpia | Paso 6 |
| 6. Validar la base recuperada | Paso 7 |
| 7. Arrancar en orden y comprobar `GET /system/status/` | Pasos 9 y 10 |
| 8. Registrar fuera de la BD y `ops:restore` en `AUDIT_LOG` | Paso 11 |
| 9. Avisar de la pérdida posterior al respaldo y del reenvío offline | Pasos 12 y 13 |

Los pasos 8 y 12 (invalidar sesiones y reconciliar cambios) **no estaban en el mínimo**: se agregaron por el riesgo de seguridad de reactivar sin querer sesiones, QR revocados y consentimientos revocados.

### Anexo D. Cambios sensibles a reconciliar después de restaurar

| Qué se pudo perder | Riesgo si no se reaplica | Dónde se reaplica |
|---|---|---|
| Revocación de un QR (pérdida, robo, daño) | El QR perdido vuelve a escanear como `VIGENTE` | Reemplazo de QR por el Administrador (diagrama 4.4.2) |
| Desactivación de cuenta o cambio de rol | Un usuario sin permiso recupera acceso | Panel de usuarios (Administrador) |
| Bloqueo de cuenta o restablecimiento de contraseña | Se reutiliza una contraseña ya cambiada | El paso 8 cierra sesiones; revisar contraseñas con el Administrador |
| Consentimiento de un tutor revocado | Se comunica a una familia que retiró su autorización (RN-COM-04) | Expediente del estudiante (PAD o Administrador) |
| Baja, egreso o reingreso de estudiantes | Aparece como `ACTIVO` quien ya no lo es | Expediente del estudiante |
| Desactivación o reactivación de docentes | Se evalúa o se omite a un docente por error | Ficha del docente (diagrama 4.8) |
| Reportes y sus etapas | Se pierde el avance de un reporte | Registro y transiciones desde la bandeja |
| Asistencia de la jornada | `FALTO` automático para quien sí asistió | Recaptura por el operador; justificación o reclasificación por escaneo |

---

*Fin del runbook.*
