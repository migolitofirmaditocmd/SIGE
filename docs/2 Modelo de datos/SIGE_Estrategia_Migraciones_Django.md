# SIGE — Estrategia de Migraciones en Django
### Sistema Integral de Gestión Escolar
**Complemento al Modelo de Datos**

---

## 1. Introducción
Este documento define la estrategia institucional para la gestión, versionado y despliegue de los cambios en el esquema de la base de datos PostgreSQL utilizando el ORM de Django para el proyecto SIGE. El objetivo es mantener una trazabilidad total entre las Reglas de Negocio y las alteraciones de la base de datos, garantizando la reproducibilidad del entorno.

## 2. Versionado de Esquema
1. **Migraciones Automáticas y Manuales:** Las modificaciones estándar a los modelos (`models.py`) se generarán utilizando `python manage.py makemigrations`. Para cambios complejos (índices parciales avanzados, operaciones de llenado o transformaciones complejas), se crearán migraciones vacías (`python manage.py makemigrations --empty <app>`) para inyectar operaciones `RunSQL` o `RunPython`.
2. **Nomenclatura y Trazabilidad:** Django asigna prefijos numéricos a las migraciones (ej. `0002_auto_...`). Para migraciones de datos o ajustes manuales, el nombre deberá reflejar la acción (ej. `0003_seed_operational_parameters`). Adicionalmente, el código de la migración debe incluir un comentario explícito citando la Regla de Negocio que justifica la operación (ej. `# Implementación de RN-AUT-01`).
3. **Inmutabilidad del Historial:** Una vez que un archivo de migración ha sido mezclado (merged) y aplicado en el entorno de pruebas o producción, jamás debe modificarse o eliminarse. Si el esquema necesita cambiar, siempre se debe crear una migración nueva que avance el estado, nunca alterar el pasado.

## 3. Orden de Creación y Dependencias
Para inicializar la base de datos vacía sin conflictos de dependencias (Foreign Keys), la primera ronda de migraciones debe respetar el siguiente orden de resolución:
1. **Catálogos Base (`catalogs`, `settings`, `reports`):** Entidades semilla e independientes, tales como `ACADEMIC_CYCLE`, `GROUP`, `REPORT_TYPE`, `REPORT_SEVERITY` y `OPERATIONAL_PARAMETER`.
2. **Usuarios y Docentes (`accounts`, `teachers`):** Por la dependencia circular indirecta, se recomienda crear primero la tabla `TEACHER` y posteriormente la tabla `USER`, integrando su Foreign Key `teacher_id` (RN-AST-30) en el momento de creación, o resolviéndolo en un paso posterior dentro de la misma migración.
3. **Estudiantes y Tutores (`students`):** Tablas `STUDENT`, `GUARDIAN` y la relación intermedia `STUDENT_GUARDIAN`.
4. **Módulos Operativos:** Tablas de dependencias amplias, en este orden: `attendance`, `reports` (Incidentes), `credentials` (Tokens QR), `imports`, y finalmente las tablas de log `audit` y `ops`.

## 4. Datos Semilla (Seed Data)
El sistema requiere una línea base de información para que los flujos puedan operar. Toda inserción de datos semilla debe existir como una **migración de datos (Data Migration) de Django (`RunPython`)**, de manera que cualquier desarrollador o servidor consiga el mismo estado base al correr `migrate`.
1. **Parámetros Operativos (RN-ADM-02):** La migración de la app `settings` inyectará:
   - `REBOUND_WINDOW_MINUTES`: "5"
   - `STUDENT_ABSENCE_CHECK_TIME`: "10:00"
   - `TEACHER_ABSENCE_CHECK_TIME`: "08:00" (o similar institucional)
   - `TEACHER_DEFAULT_TOLERANCE_MINUTES`: "0"
   - `ACCOUNT_LOCKOUT_MAX_ATTEMPTS`: "5"
   - `ACCOUNT_LOCKOUT_DURATION_MINUTES`: "15"
2. **Ciclo Escolar Activo:** Debe inyectarse un registro de prueba de `ACADEMIC_CYCLE` con la bandera `is_active=True`, dado que ninguna alta estudiantil o docente puede procesarse sin un ciclo vigente.
3. **Roles y Privilegios:** En caso de que se utilicen grupos base para roles (ej. Administrador, Prefecto), se sembrarán en este paso.

## 5. Cambios Restrictivos en Tablas Pobladas
Al evolucionar el sistema, si un campo opcional se convierte en obligatorio (restricción `NOT NULL`), la migración automática de Django fallará en tablas que ya contengan filas nulas. La estrategia es:
1. Crear una migración en 3 pasos:
   - **Paso A:** Se crea el campo o se permite momentáneamente el paso de nulos.
   - **Paso B (RunPython):** Se ejecuta un script iterativo que llena los registros nulos existentes con un valor por defecto o un string de relleno.
   - **Paso C:** Se aplica la restricción definitiva `NOT NULL` o `UNIQUE`.

## 6. Plan de Rollback (Reversibilidad)
Una migración es una transacción que debe poder deshacerse si falla.
1. **Código Reversible:** Toda operación de `RunPython` o `RunSQL` DEBE poseer su parámetro `reverse_code` obligatorio.
   - *Ejemplo:* Si el código de avance inserta datos semilla, el `reverse_code` debe ejecutar una sentencia `.delete()` para esos datos. Así, un `manage.py migrate <app> <version_anterior>` revertirá el estado limpiamente.
2. **Migraciones Irreversibles:** Si una migración destruye datos por diseño (ej. se retira una columna permanentemente), el desarrollador no podrá proveer un `reverse_code` que reviva los datos. En este caso extremo, se debe generar un volcado (`pg_dump`) mandatorio antes del despliegue para respaldar el estado real.
3. **Protección Zero-Downtime:** Para cambios de esquema muy agresivos (como renombrar una tabla vital o partir un campo en dos), la transición se divide en fases a lo largo de varios releases: (1) Crear la nueva columna, (2) Escribir en ambas desde la app, (3) Llenar los datos históricos mediante script de migración, (4) Leer únicamente desde la nueva columna, (5) Eliminar la columna vieja en la siguiente actualización.
