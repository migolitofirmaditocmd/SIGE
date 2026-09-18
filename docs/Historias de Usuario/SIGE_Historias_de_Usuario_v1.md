# Historias de Usuario — SIGE
### Sistema Integral de Gestión Escolar
**Documento derivado de:** Acta Constitutiva v9 · Especificación de Requisitos v2 (RF/RNF) · Catálogo de Reglas de Negocio v2 · Diagramas de flujo (asistencia, registro de estudiante, ciclo QR, reportes escolares) · Guía de buenas prácticas de historias de usuario
**Versión:** 1.0 | **Estado:** Para revisión del equipo
**Documento complementario:** `SIGE_Criterios_de_Aceptacion_v1.md` (criterios Dado/Cuando/Entonces por historia, criterios transversales, DoR y DoD)

---

## 1. Introducción

### 1.1 Propósito
Este documento traduce los requisitos (RF/RNF), las reglas de negocio (RN) y los flujos de UX en **historias de usuario detalladas**. Cada historia funciona como un contrato ligero entre negocio, UX/UI, desarrollo y QA: dice **quién** necesita algo, **qué** necesita, **para qué**, bajo **qué reglas**, con **qué permisos y datos**, y cómo se comporta la interfaz. Los criterios de aceptación verificables viven en el documento complementario, con el mismo ID de historia.

### 1.2 Convenciones
- **ID de historia:** `SIGE-US-###` (secuencial global). **ID de criterio:** `CA-###-##` (en el documento de criterios).
- **Prioridad:** MoSCoW heredada del documento de RF (Must / Should / Could). Las historias derivadas que no tienen RF propio se marcan como *Propuesta*.
- **Tipo:** salvo indicación, es una historia de usuario; las marcadas **[Habilitadora]** describen capacidades técnicas que el usuario no ve directamente pero de las que dependen otras historias.
- **⚠ A-##:** remite al **Anexo A** (vacíos, ambigüedades e inconsistencias detectadas en los documentos fuente). En esos puntos se tomó una decisión provisional que conviene validar con el equipo o la institución.
- **Numeración de RF:** se usa la de la *Especificación de Requisitos v2* (RF-AST-08 = registro docente, RF-AST-09 = programación docente, RF-AST-10 = persistencia docente). Ver A-04.
- **Abreviaturas de flujos de UX:**

| Sigla | Diagrama de origen |
|---|---|
| **F-EST** | Flujo de registro de estudiante (incluye importación masiva, alta manual y gestión posterior) |
| **F-AST §n** | Flujo de asistencia, secciones 1–7 (1 escaneo estudiante · 2 ausencias estudiantes · 3 reclasificación · 4 offline · 5 registro docente · 6 ausencias docentes · 7 justificación) |
| **F-QR A/B/T/C** | Flujo del ciclo QR (A alta inicial · B mantenimiento/reemplazo · T subproceso de token · C generación de QR y credencial) |
| **F-REP §n** | Flujo de reportes escolares, secciones 1–6 (1 docente · 2 prefecto · 3 corrección · 4 administrativo · 5 comunicación · 6 consulta) |

### 1.3 Estados de asistencia usados
`ASISTIÓ` · `LLEGÓ TARDE` · `FALTÓ` · `FALTA JUSTIFICADA` (ver A-07). El origen de cada estado se registra como `ESCANEO`, `AUTOMÁTICO` o `MANUAL` (RN-TRX-07).

---

## 2. Actores y roles

| Sigla | Actor | Acceso | Notas |
|---|---|---|---|
| **ADM** | Administrador / Directivo | Web | Control total: usuarios, catálogos, parámetros, auditoría. |
| **PRE** | Prefecto | Web + Móvil | Escaneo de asistencia, expedientes, revisión y canalización de reportes. |
| **DOC** | Docente | Móvil (y web, OE-05) | Registro y consulta de sus propios reportes. No requiere cuenta para que se registre su asistencia. |
| **PAD** | Personal administrativo | Web + Móvil | Escaneo de asistencia estudiantil, asistencia docente, expedientes, revisión de reportes, justificaciones, autorización de comunicación. |
| **SL** | Solo lectura / Auditoría | Web | Estadísticas e información consolidada; nunca escritura (RN-AUT-02). |
| **SIS** | Sistema | — | Procesos programados (verificación de ausencias, respaldos, sincronización). |
| — | Familiar / Tutor | Correo (externo) | Receptor pasivo; sin cuenta en esta fase. |
| — | Estudiante · Docente (como sujeto de asistencia) | QR | Se identifican por QR; no son usuarios del sistema. |

> Regla base: todo usuario tiene **exactamente un rol activo** (RN-AUT-01) y toda regla se valida en el **backend**, sin importar el cliente (RN-API-01, RN-TRX-05).

---

## 3. Mapa de historias (Story Map: Actividad → Paso → Historias)

| Épica | Actividad | Pasos | Historias |
|---|---|---|---|
| **EP-01** | Acceder y controlar el acceso | Autenticarse · Administrar cuentas · Restringir por rol · Auditar | US-001 a US-007 |
| **EP-02** | Gestionar estudiantes | Registrar · Completar · Tutores · Consultar · Modificar · Grupo · Estatus · Consentimiento | US-008 a US-016 |
| **EP-03** | Importar estudiantes masivamente | Plantilla · Cargar/validar · Procesar filas · Vista previa · Reporte | US-017 a US-021 |
| **EP-04** | Identificar con QR y credenciales | Generar · Validar lote · Revocar/reemplazar · Exportar · Reexportar | US-022 a US-026 |
| **EP-05** | Controlar asistencia estudiantil | Escanear/validar · Registrar · Rebote · Ausencias · Reclasificar · Offline · Justificar · Consultar | US-027 a US-037 |
| **EP-06** | Controlar asistencia docente | Alta y QR · Programación · Entrada · Salida · Ausencias · Justificar · Historial | US-038 a US-044 |
| **EP-07** | Gestionar reportes escolares | Registrar · Consultar · Revisar/canalizar · Corregir · Revisión administrativa · Decidir comunicación · Trazabilidad | US-045 a US-051 |
| **EP-08** | Comunicar con familiares | Enviar · Estado y reintento | US-052 a US-053 |
| **EP-09** | Administrar el sistema | Catálogos · Parámetros · Indicadores | US-054 a US-056 |
| **EP-10** | Continuidad y operación local | Respaldo y recuperación · Operación sin Internet | US-057 a US-058 |

---

## 4. Historias de usuario

# EP-01 — Autenticación, usuarios y control de acceso

### SIGE-US-001 — Iniciar y mantener sesión
**Épica:** EP-01 · **Módulo:** AUT · **Actor:** ADM, PRE, DOC, PAD, SL · **Prioridad:** Must · **Hito:** 02
> **Como** usuario de SIGE con cuenta activa, **quiero** iniciar sesión con mi usuario y contraseña desde la web o la app móvil, **para** acceder únicamente a las funciones y datos de mi rol.

- **Contexto:** puerta de entrada común a web y móvil; ambos clientes usan la misma autenticación (RN-API-02, RN-MOV-01).
- **Precondiciones:** cuenta activa con exactamente un rol.
- **Reglas de negocio:** RN-AUT-01 (un rol activo) · RN-AUT-04 (un JWT vencido no permite ninguna operación aunque el refresh siga vigente: 401 + solicitud de renovación) · RN-API-01.
- **Permisos:** todos los roles con cuenta activa.
- **Datos:** *entrada:* usuario (obligatorio), contraseña (obligatoria, oculta). *salida:* token de acceso (vida corta) y token de renovación (vida larga, invalidable).
- **UX/UI y estados:** formulario simple con mostrar/ocultar contraseña; estados: cargando, credenciales inválidas (mensaje genérico que no revela cuál dato falló), cuenta bloqueada (US-002), cuenta desactivada, servidor no disponible. Tras autenticarse, se muestra la pantalla inicial del rol.
- **Flujos alternativos:** token de acceso vencido con refresh vigente → renovación transparente; ambos vencidos → volver a iniciar sesión; **cerrar sesión** invalida el refresh token; cuenta comprometida → el ADM invalida sus sesiones (US-004).
- **Dependencias:** US-003 (cuenta existente).
- **Trazabilidad:** RF-AUT-01 · RNF-SEG-01, RNF-SEG-03 · OE-03 · KPI-08.

### SIGE-US-002 — Bloqueo temporal por intentos fallidos y desbloqueo manual
**Épica:** EP-01 · **Módulo:** AUT · **Actor:** Usuario (bloqueo automático), ADM (desbloqueo) · **Prioridad:** Must · **Hito:** 02
> **Como** administrador, **quiero** que una cuenta se bloquee temporalmente tras varios intentos fallidos consecutivos y poder desbloquearla antes de tiempo, **para** proteger las cuentas sin dejar sin acceso al personal legítimo.

- **Contexto:** mitigación de ataques de fuerza bruta (OWASP ASVS, RNF-SEG-03).
- **Reglas de negocio:** RN-AUT-03 (por defecto 5 intentos, configurable; bloqueo temporal + notificación del tiempo de espera; desbloqueo manual anticipado por ADM) · RN-AUT-05 (queda registro).
- **Permisos:** el bloqueo es automático; el desbloqueo solo lo ejecuta ADM.
- **Datos:** contador de intentos fallidos consecutivos; marca de bloqueo y vencimiento (duración no definida, ver A-17).
- **UX/UI y estados:** al bloquearse, se muestra el tiempo de espera restante; el ADM ve el estado "bloqueada" en la lista de usuarios con acción "Desbloquear".
- **Flujos alternativos:** un inicio de sesión exitoso reinicia el contador; un intento durante el bloqueo se rechaza aunque la contraseña sea correcta.
- **Dependencias:** US-001, US-003.
- **Trazabilidad:** RF-AUT-03 · RN-AUT-03 · RNF-SEG-03 · OE-03.

### SIGE-US-003 — Dar de alta una cuenta de usuario con rol
**Épica:** EP-01 · **Módulo:** AUT · **Actor:** ADM · **Prioridad:** Must · **Hito:** 02
> **Como** administrador, **quiero** crear cuentas de usuario y asignarles un único rol, **para** que cada integrante del personal acceda solo a lo que su función requiere.

- **Precondiciones:** sesión de ADM.
- **Reglas de negocio:** RN-AUT-01 (exactamente un rol activo) · RN-AUT-05 (alta y asignación de rol auditadas) · RNF-SEG-03 (política de contraseñas mínima configurable).
- **Permisos:** solo ADM.
- **Datos:** nombre completo (obl.), usuario único (obl.), correo institucional (obl., formato válido; se usa para recuperación US-005), rol (obl.: ADM, PRE, DOC, PAD, SL), contraseña inicial que cumpla la política (obl.).
- **UX/UI y estados:** formulario con validación en línea; éxito con confirmación; error de usuario/correo duplicado; permisos insuficientes si otro rol intenta acceder (ni por URL).
- **Flujos alternativos:** contraseña que no cumple la política → se rechaza con el detalle de lo que falta.
- **Dependencias:** US-006.
- **Trazabilidad:** RF-AUT-03 · RN-AUT-01 · OE-03 · KPI-08.

### SIGE-US-004 — Desactivar cuentas y reasignar rol
**Épica:** EP-01 · **Módulo:** AUT · **Actor:** ADM · **Prioridad:** Must · **Hito:** 02
> **Como** administrador, **quiero** desactivar una cuenta o cambiar su rol, **para** retirar accesos cuando alguien deja su función o cuando se sospecha que su cuenta fue comprometida.

- **Reglas de negocio:** RN-AUT-01 (nunca dos roles simultáneos; un usuario puede tener roles distintos en momentos distintos) · RN-AUT-05 (todo cambio de rol se audita con valor anterior y nuevo) · RN-TRX-03 (la cuenta se **desactiva**, no se elimina, para conservar la autoría de los registros históricos).
- **Permisos:** solo ADM.
- **Datos:** usuario, nuevo rol o nuevo estado (`ACTIVA`/`DESACTIVADA`), motivo (recomendado).
- **UX/UI y estados:** confirmación explícita antes de desactivar; el efecto sobre sesiones abiertas es inmediato (se invalidan sus refresh tokens).
- **Flujos alternativos:** el ADM no puede dejar al sistema sin ningún ADM activo (protección propuesta).
- **Dependencias:** US-003, US-007.
- **Trazabilidad:** RF-AUT-01, RF-AUT-03, RF-AUT-05 · RN-AUT-01, RN-AUT-05 · OE-03.

### SIGE-US-005 — Recuperar contraseña mediante enlace de un solo uso
**Épica:** EP-01 · **Módulo:** AUT · **Actor:** Usuario con cuenta · **Prioridad:** Should · **Hito:** 02
> **Como** usuario que olvidó su contraseña, **quiero** restablecerla mediante un enlace enviado a mi correo institucional, **para** recuperar el acceso sin depender de un administrador.

- **Reglas de negocio:** RF-AUT-04 (enlace de un solo uso con expiración configurable) · RN-INF-02 (el envío de correo depende de Internet; su ausencia no afecta las funciones internas) · RNF-SEG-03.
- **Datos:** correo/usuario; token de restablecimiento; nueva contraseña (política vigente).
- **UX/UI y estados:** el mensaje tras solicitar el enlace es el mismo exista o no la cuenta (evita enumeración de usuarios, criterio OWASP); estados: enlace enviado, enlace expirado, enlace ya usado, sin Internet (se informa que el servicio de correo no está disponible y que puede pedir apoyo al ADM).
- **Flujos alternativos:** enlace reutilizado o expirado → se rechaza y se ofrece solicitar otro; al completar el cambio se invalidan las sesiones previas.
- **Dependencias:** US-003 · **Trazabilidad:** RF-AUT-04 · OE-03.

### SIGE-US-006 — Restringir funciones y datos según el rol **[Habilitadora]**
**Épica:** EP-01 · **Módulo:** AUT/API · **Actor:** ADM (dueño de la política) · **Prioridad:** Must · **Hito:** 02
> **Como** administrador, **quiero** que cada función y cada dato estén restringidos por el rol del usuario en el backend, **para** que nadie acceda a información o acciones fuera de su rol, ni siquiera manipulando la URL o la API.

- **Reglas de negocio:** RN-AUT-02 (ninguna escritura desde SL, rechazada en API, no solo ocultando botones) · RN-TRX-02 (ningún rol accede "por defecto" a todos los datos de menores) · RN-TRX-05 y RN-API-01 (la regla vive en el backend) · RN-TRX-06 (los datos de tutores heredan las restricciones del expediente).
- **Permisos (resumen de la matriz):**

| Capacidad | ADM | PRE | DOC | PAD | SL |
|---|:-:|:-:|:-:|:-:|:-:|
| Administrar cuentas, catálogos y parámetros | ✓ | — | — | — | — |
| Alta/edición de estudiantes e importación | ✓ | — | — | ✓ | — |
| Consultar expedientes | ✓ | ✓ | — | ✓ | — |
| Escanear asistencia estudiantil | — | ✓ | — | ✓ | — |
| Registrar asistencia docente y programación | — | — | — | ✓ | — |
| Justificar/modificar asistencia | ✓ | — | — | ✓ | — |
| Revocar/regenerar QR | ✓ | — | — | — | — |
| Registrar reportes | — | — | ✓ | — | — |
| Revisar y canalizar reportes | — | ✓ | — | — | — |
| Revisión administrativa y autorizar comunicación | — | — | — | ✓ | — |
| Consultar bitácora | ✓ | — | — | — | — |
| Estadísticas y datos consolidados | ✓ | ✓ | — | ✓ | ✓ |

> La matriz consolida lo que dicen RF, RN y actores; las celdas no definidas de forma explícita (p. ej. ADM en escaneo, SL en indicadores) se marcaron conservadoramente y deben validarse (ver A-21).
- **UX/UI y estados:** elementos no permitidos no se muestran; si se accede por URL/API se devuelve "permiso denegado" con formato de error estándar.
- **Trazabilidad:** RF-AUT-02, RF-API-01, RF-API-02 · RNF-SEG-04 · OE-03 · KPI-08.

### SIGE-US-007 — Consultar la bitácora de auditoría
**Épica:** EP-01 · **Módulo:** AUT · **Actor:** ADM · **Prioridad:** Must · **Hito:** 02
> **Como** administrador, **quiero** consultar quién hizo qué y cuándo en las acciones críticas, **para** detectar usos indebidos y responder ante cualquier aclaración.

- **Reglas de negocio:** RN-AUT-05 (registro inmutable de acciones críticas: cambios de rol, modificaciones de asistencia estudiantil y docente, modificaciones de reportes, cambios de estatus; con usuario, fecha/hora y valor anterior/nuevo) · RN-TRX-07 (distinguir cambios automáticos de manuales) · RN-TRX-03.
- **Permisos:** solo ADM (SL no; ver A-21).
- **Datos:** usuario, fecha/hora, acción, resultado, entidad afectada, valor anterior, valor nuevo, origen (`MANUAL`/`AUTOMÁTICO`). Incluye inicios de sesión (RF-AUT-05).
- **UX/UI y estados:** tabla paginada con filtros por usuario, rango de fechas, tipo de acción y resultado; estados: cargando, sin resultados, error; no ofrece editar ni borrar.
- **Trazabilidad:** RF-AUT-05 · OE-03, OE-08 · KPI-64.

---

# EP-02 — Gestión de estudiantes

### SIGE-US-008 — Registrar un estudiante desde la interfaz web
**Épica:** EP-02 · **Módulo:** EST · **Actor:** PAD (y ADM) · **Prioridad:** Must · **Hito:** 02
> **Como** personal administrativo, **quiero** dar de alta a un estudiante capturando su expediente, **para** que exista una ficha única desde la cual operen asistencia, QR y reportes.

- **Contexto:** vía individual del F-EST (la vía masiva está en EP-03).
- **Precondiciones:** catálogos de grupo/ciclo/grado disponibles (US-054).
- **Reglas de negocio:** RN-EST-01 (un solo estatus: `ACTIVO`, `BAJA`, `EGRESADO`) · RN-EST-02 (matrícula única e inmutable) · RN-EST-03 (al menos un tutor con contacto válido) · RN-TRX-01 (minimización; ver A-22) · RN-API-01.
- **Permisos:** PAD, ADM.
- **Datos:** nombre completo, fecha de nacimiento, fotografía, grado, grupo, ciclo escolar, domicilio, sexo, matrícula, CURP, estatus, tutor(es) (RF-EST-01).
- **UX/UI y estados (F-EST):** captura → validación de campos y formato → verificación de tutor → validación final de consistencia y unicidad de matrícula → creación → asignación de grupo/ciclo → ficha activa. Estados: guardando, éxito, errores por campo, matrícula duplicada, faltan datos.
- **Flujos alternativos:** sin tutor → no se guarda; matrícula existente → se rechaza y se indica el conflicto; faltan otros datos obligatorios pero se cumplen los requisitos mínimos → US-009 (⚠ A-14).
- **Dependencias:** US-010, US-054.
- **Trazabilidad:** RF-EST-01 · RN-EST-01/02/03 · OE-02 · KPI-07, KPI-09 · F-EST.

### SIGE-US-009 — Guardar y completar un registro incompleto
**Épica:** EP-02 · **Módulo:** EST · **Actor:** PAD (y ADM) · **Prioridad:** Must · **Hito:** 02
> **Como** personal administrativo, **quiero** guardar un estudiante cuyos datos aún están incompletos y ver claramente qué campos faltan, **para** completarlos después sin perder lo ya capturado.

- **Contexto:** anotación del F-EST: los datos incompletos sí pueden existir como *registro incompleto* si están presentes los campos mínimos para crearlo.
- **Reglas de negocio:** F-EST (los campos faltantes deben quedar identificados) · RN-EST-03 (el tutor sigue siendo obligatorio) · RN-EST-05 (solo `ACTIVO` recibe asistencia/reportes; ⚠ A-14 sobre el estatus del registro incompleto).
- **Datos:** lista de campos faltantes visible en la ficha; definición de "requisitos mínimos" pendiente (A-14).
- **UX/UI y estados:** indicador "Incompleto" en listas y ficha, con checklist de faltantes; al completar el último campo el indicador desaparece; guardado parcial con confirmación.
- **Flujos alternativos:** si no se cumplen los requisitos mínimos, el registro no se guarda.
- **Dependencias:** US-008 · **Trazabilidad:** RF-EST-01 · OE-02 · F-EST.

### SIGE-US-010 — Asociar y administrar tutores de un estudiante
**Épica:** EP-02 · **Módulo:** EST · **Actor:** PAD (y ADM) · **Prioridad:** Must · **Hito:** 02
> **Como** personal administrativo, **quiero** registrar uno o varios tutores por estudiante y marcar uno como contacto principal, **para** poder notificar a la familia correcta.

- **Reglas de negocio:** RN-EST-03 (al menos un tutor con contacto válido antes de estar `ACTIVO`) · RN-COM-01 (solo se comunica a un contacto marcado como válido) · RN-TRX-06 (herencia de restricciones de acceso) · RN-TRX-01.
- **Datos:** nombre (obl.), relación (`padre`, `madre`, `tutor legal`, `otro`; obl.), teléfono, correo (formato válido; el canal de comunicación es correo), indicador de contacto principal, indicador de contacto válido (definición en A-14).
- **UX/UI y estados:** lista de tutores en la ficha con etiqueta "Principal"; no se puede eliminar al único tutor válido de un estudiante `ACTIVO`.
- **Flujos alternativos:** correo con formato inválido → error en línea.
- **Dependencias:** US-008 · **Trazabilidad:** RF-EST-03 · OE-02 · KPI-07.

### SIGE-US-011 — Consultar y filtrar expedientes
**Épica:** EP-02 · **Módulo:** EST · **Actor:** ADM, PRE, PAD · **Prioridad:** Must · **Hito:** 02
> **Como** prefecto o personal administrativo, **quiero** buscar y filtrar estudiantes por nombre, matrícula, grupo, grado y estatus, **para** encontrar rápido un expediente y consultar su información e historial.

- **Reglas de negocio:** RN-TRX-02 (acceso solo por rol) · RN-EST-04 (los expedientes de `BAJA`/`EGRESADO` siguen consultables por rol autorizado) · RN-EST-07 (advertencia si el consentimiento está `PENDIENTE`).
- **Permisos:** ADM, PRE, PAD. DOC y SL no consultan expedientes.
- **Datos:** filtros: nombre, matrícula, grupo, grado, estatus; resultados paginados; ficha con datos, tutores, asistencia e incidencias asociadas.
- **UX/UI y estados:** buscador + filtros combinables; tabla en escritorio, tarjetas en móvil; estados: cargando, sin resultados, error, permiso denegado.
- **Trazabilidad:** RF-EST-04, RF-EST-05 · OE-02 · KPI-07.

### SIGE-US-012 — Modificar los datos de un estudiante
**Épica:** EP-02 · **Módulo:** EST · **Actor:** PAD (y ADM) · **Prioridad:** Must · **Hito:** 02
> **Como** personal administrativo, **quiero** corregir o actualizar los datos de un estudiante, **para** mantener el expediente vigente sin romper su identidad en el sistema.

- **Reglas de negocio:** RN-EST-02 (la matrícula es inmutable; solo corrección excepcional por PAD/ADM con registro en bitácora) · F-EST (modificación manual solo por personal administrativo con permisos suficientes) · RN-AUT-05 (registro de auditoría).
- **UX/UI y estados:** el campo matrícula aparece bloqueado; una acción separada "Corrección excepcional de matrícula" exige motivo y confirmación.
- **Flujos alternativos:** nueva matrícula ya existente → se rechaza.
- **Dependencias:** US-008 · **Trazabilidad:** RF-EST-01 · RN-EST-02 · OE-02 · F-EST.

### SIGE-US-013 — Cambiar grupo o ciclo conservando el historial
**Épica:** EP-02 · **Módulo:** EST · **Actor:** PAD (y ADM) · **Prioridad:** Must (derivada del F-EST) · **Hito:** 02
> **Como** personal administrativo, **quiero** cambiar a un estudiante de grupo o de ciclo escolar sin perder el historial anterior, **para** que la asistencia y los reportes pasados sigan asociados al grupo al que pertenecía entonces.

- **Reglas de negocio:** F-EST ("Conservar historial anterior") · RN-TRX-03 (archivado lógico) · RF-AST-01 (la asistencia se guarda con el grupo vigente a la fecha).
- **Datos:** grupo/ciclo nuevo (obl.), fecha efectiva.
- **UX/UI y estados:** el historial de grupos se muestra en la ficha con fechas.
- **Trazabilidad:** RF-EST-01 · OE-02 · F-EST.

### SIGE-US-014 — Dar de baja o registrar egreso de un estudiante
**Épica:** EP-02 · **Módulo:** EST · **Actor:** PAD (y ADM) · **Prioridad:** Should · **Hito:** 02
> **Como** personal administrativo, **quiero** cambiar el estatus de un estudiante a `BAJA` o `EGRESADO`, **para** que deje de aparecer en las operaciones diarias pero conserve su historial.

- **Reglas de negocio:** RN-EST-01 · RN-EST-04 (se conserva expediente e historial; deja de aparecer en asistencia y reportes nuevos; archivado lógico, no eliminación física) · RN-EST-05 · RF-EST-02 (transiciones válidas: `ACTIVO→BAJA`, `ACTIVO→EGRESADO`) · RN-AUT-05 (el cambio se audita).
- **UX/UI y estados:** confirmación con resumen del efecto; estados: éxito, transición no permitida.
- **Flujos alternativos:** desde `EGRESADO` no hay transiciones definidas (A-05); el reingreso desde `BAJA` es US-015.
- **Dependencias:** US-030 (el proceso de ausencias omite estudiantes no `ACTIVO`).
- **Trazabilidad:** RF-EST-02 · OE-02 · F-EST.

### SIGE-US-015 — Reingresar a un estudiante dado de baja
**Épica:** EP-02 · **Módulo:** EST · **Actor:** ADM · **Prioridad:** Should · **Hito:** 02
> **Como** administrador, **quiero** autorizar de forma explícita el paso de `BAJA` a `ACTIVO`, **para** reincorporar a un estudiante quedando constancia de que es un reingreso y no el alta original.

- **Reglas de negocio:** RN-EST-06 (requiere autorización explícita del ADM y se registra como evento distinto del alta) · RN-EST-03 (debe conservar al menos un tutor válido) · RN-AUT-05.
- **Permisos:** solo ADM. **Datos:** motivo, fecha.
- **Flujos alternativos:** un PAD que lo intente recibe rechazo. Efecto sobre el QR previo: ver A-05.
- **Trazabilidad:** RF-EST-02 · RN-EST-06 · OE-02.

### SIGE-US-016 — Registrar y consultar el consentimiento del tutor
**Épica:** EP-02 · **Módulo:** EST · **Actor:** PAD (y ADM) · **Prioridad:** Must (regulatorio) · **Hito:** 02
> **Como** personal administrativo, **quiero** registrar el estatus de consentimiento de cada tutor para el tratamiento de los datos del menor, **para** cumplir con la LFPDPPP y saber en qué casos falta regularizarlo.

- **Reglas de negocio:** RN-EST-07 (el consentimiento puede documentarse fuera de SIGE —p. ej. formato físico—, pero debe existir un campo consultable con su estatus vigente; mientras esté `PENDIENTE`, SIGE debería advertir al personal autorizado al consultar el expediente) · RN-TRX-01/02.
- **Datos:** por tutor: estatus (`PENDIENTE`, `OTORGADO`, `REVOCADO`) y fecha de registro.
- **UX/UI y estados:** insignia visible en el expediente ("Consentimiento pendiente") sin bloquear la consulta.
- **Flujos alternativos:** efectos operativos de `REVOCADO` sobre la comunicación no están definidos (A-05, A-19).
- **Trazabilidad:** RF-EST-05 · LFPDPPP · OE-02.

---

# EP-03 — Importación masiva de estudiantes

### SIGE-US-017 — Descargar la plantilla de importación
**Épica:** EP-03 · **Módulo:** IMP · **Actor:** ADM, PAD · **Prioridad:** Should · **Hito:** 02
> **Como** personal administrativo, **quiero** descargar una plantilla CSV/XLSX con las columnas exactas del diccionario de datos y ejemplos válidos, **para** reducir errores al preparar el archivo.

- **Reglas de negocio:** RN-IMP-01 (el archivo debe cumplir exactamente el diccionario vigente).
- **UX/UI y estados:** el botón de plantilla aparece **antes** de seleccionar el archivo (F-EST); descarga inmediata.
- **Trazabilidad:** RF-IMP-02 · OE-02 · F-EST.

### SIGE-US-018 — Cargar un archivo y validar su estructura
**Épica:** EP-03 · **Módulo:** IMP · **Actor:** ADM, PAD (⚠ A-15) · **Prioridad:** Must · **Hito:** 02
> **Como** personal administrativo, **quiero** cargar un archivo Excel/CSV y que SIGE valide primero su estructura de columnas, **para** no procesar archivos que no corresponden al formato definido.

- **Reglas de negocio:** RN-IMP-01 (se rechaza el archivo completo antes de procesar filas si columnas, tipos o formato no corresponden) · fuera de alcance: limpieza/transformación de datos históricos (acta §7).
- **Datos:** archivo `.csv` o `.xlsx`.
- **UX/UI y estados (F-EST):** seleccionar archivo → "SIGE procesa y valida la estructura" → si no coincide, **detener toda la importación** con mensaje que indica qué columnas fallan.
- **Trazabilidad:** RF-IMP-01 · OE-02 · F-EST.

### SIGE-US-019 — Procesar cada fila de forma independiente
**Épica:** EP-03 · **Módulo:** IMP · **Actor:** SIS (iniciado por PAD/ADM) · **Prioridad:** Must · **Hito:** 02
> **Como** personal administrativo, **quiero** que cada fila se valide por separado y que una fila inválida no impida procesar las demás, **para** cargar todo lo correcto y corregir solo lo defectuoso.

- **Reglas de negocio:** RN-IMP-02 (filas independientes; inserción parcial + reporte de errores) · RN-IMP-03 (matrícula existente → fila rechazada como duplicada, nunca sobrescribe) · RN-EST-02, RN-EST-03 (cada fila debe traer al menos un tutor válido) · F-EST (la fila con error se descarta y se pasa a la siguiente; ninguno de sus datos se guarda).
- **Datos del error por fila:** fila afectada, campo, tipo de error, descripción.
- **Flujos alternativos:** el diagrama incluye una salvaguarda ante creación simultánea que termina la importación (A-15).
- **Dependencias:** US-018 · **Trazabilidad:** RF-IMP-01 · OE-02 · F-EST.

### SIGE-US-020 — Revisar la vista previa y confirmar la importación
**Épica:** EP-03 · **Módulo:** IMP · **Actor:** PAD, ADM · **Prioridad:** Must · **Hito:** 02
> **Como** personal administrativo, **quiero** ver una vista previa de qué registros se insertarán y cuáles se rechazarán y confirmarla explícitamente, **para** evitar cargar datos por error.

- **Reglas de negocio:** RN-IMP-04 (toda importación se ejecuta primero en *dry-run*; no se persiste nada hasta la confirmación explícita) · RN-EST-04/05 (los estudiantes importados quedan `ACTIVO`) · F-EST (asignación a grupo/ciclo).
- **UX/UI y estados:** resumen (a insertar / rechazados) + botones "Confirmar importación definitiva" y "Cancelar"; al cancelar, la importación termina sin persistir datos; al confirmar, se generan las fichas activas.
- **Dependencias:** US-019 · **Trazabilidad:** RF-IMP-01 · OE-02 · F-EST.

### SIGE-US-021 — Descargar el reporte de resultados de la importación
**Épica:** EP-03 · **Módulo:** IMP · **Actor:** PAD, ADM · **Prioridad:** Must · **Hito:** 02
> **Como** personal administrativo, **quiero** obtener un reporte descargable con totales y el detalle de cada fila con error, **para** corregir el archivo y volver a cargar únicamente lo pendiente.

- **Datos:** total procesadas, insertadas, con error; por fila con error: columna y motivo (RF-IMP-01). Formato de descarga: CSV/XLSX (propuesta).
- **UX/UI y estados:** al terminar el procesamiento de **todas** las filas se muestra el reporte de filas descartadas y se ofrece la descarga.
- **Trazabilidad:** RF-IMP-01 · OE-02 · F-EST.

---

# EP-04 — Identificación QR y credenciales

### SIGE-US-022 — Generar el QR único de un estudiante
**Épica:** EP-04 · **Módulo:** QR · **Actor:** ADM, PAD (⚠ A-21) · **Prioridad:** Must · **Hito:** 01
> **Como** personal autorizado, **quiero** generar para cada estudiante `ACTIVO` un QR único que no exponga datos personales, **para** identificarlo con seguridad al escanear su credencial.

- **Contexto:** F-QR A (alta inicial) + F-QR T (token) + F-QR C (imagen y asociación).
- **Precondiciones:** estudiante `ACTIVO` sin QR vigente.
- **Reglas de negocio:** RN-QR-01 (máximo un QR vigente) · RN-QR-02 (el payload es un token opaco; sin nombre, matrícula visible ni CURP) · RN-QR-03 (un token revocado nunca se reutiliza) · RN-EST-05 · RN-API-01/TRX-05 (unicidad verificada en backend) · RNF-SEG-02.
- **Datos:** token (UUID v4/CSPRNG), estado (`VIGENTE`), fecha de creación, estudiante, usuario que generó, origen (`alta inicial`/`reemplazo`). Vigencia indefinida hasta revocación.
- **UX/UI y estados (F-QR T):** el sistema genera candidato → valida formato/longitud → verifica que no exista entre vigentes **ni** revocados → si hay colisión reintenta (máximo configurado, 5) → si se excede, alerta al ADM y aborta → si es único, guarda y genera imagen QR que codifica solo el token → asocia con el estudiante.
- **Flujos alternativos:** si el estudiante ya tiene QR vigente (caso anómalo) se trata como reemplazo (US-024).
- **Trazabilidad:** RF-QR-01 · RNF-SEG-02 · OE-01 · KPI-01 a KPI-04.

### SIGE-US-023 — Validar la integridad del lote de QR
**Épica:** EP-04 · **Módulo:** QR · **Actor:** ADM · **Prioridad:** Must · **Hito:** 01
> **Como** administrador, **quiero** ejecutar una validación automática de integridad del lote de códigos (sin duplicados ni huérfanos), **para** habilitarlo con confianza para la producción de credenciales.

- **Reglas de negocio:** RF-QR-02 (antes de habilitar el lote y dentro de las 6 semanas del proyecto) · RN-QR-01/03.
- **Datos:** resultado: total, duplicados, huérfanos (QR sin estudiante o estudiantes `ACTIVO` sin QR), estado del lote (`HABILITADO`/`BLOQUEADO`).
- **UX/UI y estados:** reporte de validación descargable; el lote solo se habilita si el resultado es 0 duplicados y 0 huérfanos.
- **Trazabilidad:** RF-QR-02 · OE-01 · KPI-05.

### SIGE-US-024 — Revocar y reemplazar el QR de un estudiante
**Épica:** EP-04 · **Módulo:** QR · **Actor:** ADM · **Prioridad:** Should · **Hito:** 01 (complementario)
> **Como** administrador, **quiero** revocar el QR de un estudiante y generar uno nuevo cuando su credencial se pierde, se roba, se daña o se duplica, **para** impedir usos indebidos y restituir su identificación.

- **Reglas de negocio:** RN-QR-01/03 (revocar es la única vía para tener otro QR vigente; el token revocado nunca vuelve a vigente ni se reutiliza; el histórico conserva la referencia al revocado y su reemplazo) · RN-QR-04 (todo escaneo posterior con el revocado se rechaza y alerta al operador aunque el estudiante siga `ACTIVO`) · RN-AUT-05, RN-TRX-03 (bitácora).
- **Permisos:** solo ADM.
- **Datos:** motivo (`pérdida`/`robo`/`daño`/`duplicidad`; obl.), estado del QR (`REVOCADO`), fecha de revocación, usuario.
- **UX/UI y estados (F-QR B):** registrar motivo → verificar rol → ¿QR vigente? → revocar → bitácora → subproceso de token (F-QR T) → nuevo QR enlazado al anterior. La UI oculta la acción a roles no ADM; el backend la rechaza en todo caso.
- **Flujos alternativos:** sin QR vigente → se pasa directo a generar; rol distinto de ADM → "Se requiere autorización de rol Administrador".
- **Dependencias:** US-022, US-026.
- **Trazabilidad:** RF-QR-03 · OE-01 · F-QR B.

### SIGE-US-025 — Exportar el QR para la credencial física
**Épica:** EP-04 · **Módulo:** CRE · **Actor:** PAD, ADM · **Prioridad:** Must · **Hito:** 01
> **Como** personal administrativo, **quiero** exportar los códigos QR en alta resolución y con el formato adecuado, **para** incorporarlos en el diseño de credenciales nuevas o imprimirlos como sticker sobre credenciales ya impresas.

- **Reglas de negocio:** RN-CRE-01 (solo estudiantes `ACTIVO` con QR vigente y fotografía cargada; los que no cumplan se excluyen y se listan aparte como pendientes) · fuera de alcance: diseño, impresión y entrega física (acta §7).
- **Datos:** imagen del QR (alta resolución), PDF por lote/estudiante, listado de pendientes.
- **UX/UI y estados (F-QR C):** el sistema entrega el archivo; el personal decide: credencial física no disponible o dañada → agregar QR a credencial nueva; credencial disponible → sticker. La aclaración fotografía/sticker está en A-16.
- **Dependencias:** US-022, US-023. **Trazabilidad:** RF-CRE-01 · OE-01 · KPI-06.

### SIGE-US-026 — Reexportar QR de forma selectiva
**Épica:** EP-04 · **Módulo:** CRE · **Actor:** PAD, ADM · **Prioridad:** Should · **Hito:** 01
> **Como** personal administrativo, **quiero** reexportar el QR de un estudiante o de un grupo, **para** imprimir el sticker de reposición tras una revocación sin regenerar todo el lote.

- **Reglas de negocio:** RN-CRE-01 · RN-QR-01 (solo se exporta el QR vigente, jamás uno revocado).
- **UX/UI y estados:** selector por estudiante o por grupo; vista previa del subconjunto antes de exportar.
- **Dependencias:** US-024, US-025. **Trazabilidad:** RF-CRE-02 · OE-01.

---

# EP-05 — Control de asistencia estudiantil

### SIGE-US-027 — Validar el QR al escanear
**Épica:** EP-05 · **Módulo:** AST/QR · **Actor:** PRE, PAD · **Prioridad:** Must · **Hito:** 03
> **Como** prefecto o personal administrativo, **quiero** que al escanear una credencial el sistema valide el QR y el estatus del estudiante antes de registrar nada, **para** evitar asistencias inválidas o fraudulentas.

- **Contexto:** F-AST §1, pasos E2–E5. Se escanea con la app móvil o, en web, con lector USB tipo teclado (HID) o cámara UVC (RNF-COM-01).
- **Reglas de negocio:** RN-QR-02 (token opaco) · RN-QR-04 (QR revocado → rechazo automático + alerta al operador para verificación manual de identidad) · RN-QR-05 · RN-EST-05 (solo `ACTIVO`) · RN-API-01.
- **Datos:** *entrada:* token leído. *salida:* estudiante identificado (nombre, grupo) o motivo de rechazo.
- **UX/UI y estados:** respuesta en menos de 250 ms en red local (RNF-DES-01); retroalimentación visual **y sonora** inmediata, alto contraste para luz solar, esquinas tipo squircle 12–16 px (RNF-USA-01). Mensajes: "QR no reconocido" (sin registro), "QR revocado — verifique identidad manualmente", "Estudiante no activo".
- **Flujos alternativos:** sin conexión → US-032 (⚠ A-13).
- **Trazabilidad:** RF-AST-01, RF-MOV-01 · RNF-DES-01, RNF-USA-01, RNF-COM-01 · OE-04 · KPI-13, KPI-15.

### SIGE-US-028 — Registrar la asistencia y determinar ASISTIÓ o LLEGÓ TARDE
**Épica:** EP-05 · **Módulo:** AST · **Actor:** PRE, PAD · **Prioridad:** Must · **Hito:** 03
> **Como** prefecto o personal administrativo, **quiero** que cada escaneo válido genere el registro de asistencia con su estado calculado automáticamente, **para** saber al instante si el estudiante llegó a tiempo o tarde.

- **Contexto:** F-AST §1, pasos E8–E11.
- **Reglas de negocio:** RN-AST-01 (se compara la hora del **primer** escaneo válido de entrada contra la hora de corte del grupo y jornada: a más tardar la hora de corte → `ASISTIÓ`; después → `LLEGÓ TARDE`) · RN-EST-05 (precondición) · RN-AST-06 y RN-TRX-03 (conservación permanente) · RN-ADM-02 (la hora de corte la configura el ADM; no es retroactiva).
- **Datos:** estudiante, fecha, hora, grupo, jornada, estado, origen = `ESCANEO`.
- **UX/UI y estados:** confirmación con nombre y estado resultante; si el estudiante ya tiene `ASISTIÓ` o `LLEGÓ TARDE`, el nuevo escaneo se guarda como evento adicional **sin cambiar** el estado; si ya estaba `FALTÓ`, continúa en US-031. Fuente de la hora: ⚠ A-18.
- **Trazabilidad:** RF-AST-01, RF-AST-03 · OE-04 · KPI-13, KPI-15, KPI-18.

### SIGE-US-029 — Ignorar escaneos duplicados (rebote)
**Épica:** EP-05 · **Módulo:** AST · **Actor:** PRE, PAD · **Prioridad:** Must · **Hito:** 03
> **Como** operador de escaneo, **quiero** que un segundo escaneo del mismo estudiante en pocos minutos se ignore y se me avise, **para** no generar registros duplicados por lecturas repetidas.

- **Reglas de negocio:** RN-AST-03 (ventana configurable, 5 min por defecto, entre 1 y 30; se ignora el segundo escaneo) · RN-ADM-02 · A-06 (RF dice "5 minutos mínimo").
- **UX/UI y estados:** aviso "Registro duplicado" al operador; no se crea segundo registro; el escaneo que llega de una sincronización offline pasa por la misma verificación (US-033).
- **Dependencias:** US-027, US-055.
- **Trazabilidad:** RF-AST-02 · OE-04 · KPI-16 · A-03 (RN-AST-02 citada pero no definida).

### SIGE-US-030 — Marcar automáticamente FALTÓ a quien no registró entrada
**Épica:** EP-05 · **Módulo:** AST · **Actor:** SIS (beneficia a PAD, PRE, ADM) · **Prioridad:** Must · **Hito:** 03
> **Como** personal administrativo, **quiero** que a la hora de verificación de ausencias el sistema marque como `FALTÓ` a los estudiantes `ACTIVO` sin registro de entrada, **para** contar con un historial diario completo sin capturar faltas a mano.

- **Contexto:** F-AST §2.
- **Reglas de negocio:** RN-AST-08 (solo se marca `FALTÓ` cuando ya pasó la hora de verificación y no existe registro válido de entrada para la fecha y jornada; antes de esa hora la ausencia no es definitiva; valor inicial 10:00, configurable) · RN-TRX-07 (el cambio se registra como `AUTOMÁTICO`, distinto de una modificación manual) · RN-EST-05.
- **UX/UI y estados:** proceso programado sin interfaz; el resultado aparece en el historial del día; una ejecución repetida no duplica registros.
- **Flujos alternativos:** estudiante con `ASISTIÓ`/`LLEGÓ TARDE` → sin acción; estudiantes no `ACTIVO` → se omiten.
- **Dependencias:** US-055. **Trazabilidad:** RF-AST-03, RF-AST-04 · OE-04 · KPI-60.

### SIGE-US-031 — Reclasificar la asistencia de quien llega después de un FALTÓ automático
**Épica:** EP-05 · **Módulo:** AST · **Actor:** PRE, PAD (escaneo); SIS · **Prioridad:** Must · **Hito:** 03
> **Como** personal administrativo, **quiero** que si un estudiante marcado `FALTÓ` automáticamente llega y escanea después, su estado se actualice según la hora real, **para** reflejar la realidad sin borrar que hubo una ausencia previa.

- **Contexto:** F-AST §3.
- **Reglas de negocio:** RN-AST-09 (se conserva la trazabilidad del estado previo y se actualiza según la hora efectiva del escaneo, sin crear un segundo registro de entrada para la misma fecha y jornada) · RN-TRX-07 (se distingue de una justificación manual) · ⚠ A-01 (RN-AST-09 aparece dos veces con resultado distinto; se sigue el flujo: comparar contra la hora de corte).
- **UX/UI y estados:** el expediente muestra ambos estados con su origen y hora.
- **Trazabilidad:** RF-AST-01, RF-AST-03, RF-AST-06 · OE-04.

### SIGE-US-032 — Capturar asistencia sin conexión al servidor (app móvil)
**Épica:** EP-05 · **Módulo:** MOV/AST · **Actor:** PRE, PAD · **Prioridad:** Must · **Hito:** 04/06
> **Como** operador de escaneo, **quiero** seguir capturando escaneos aunque el dispositivo pierda conexión con el servidor, **para** no detener la entrada de la escuela.

- **Contexto:** F-AST §4 (A). La pérdida de Internet y la pérdida de la red local son escenarios distintos (acta): esta historia trata la pérdida de conexión con el servidor local.
- **Reglas de negocio:** RN-MOV-02 (buffer local de hasta 1,000 registros; el evento queda **pendiente de validación** y no es definitivo) · RNF-FIA-01 · RN-API-02 (el buffer no sustituye la fuente central).
- **Datos:** fecha, hora, tipo de evento, identificador QR leído; marca `PENDIENTE DE VALIDACIÓN`.
- **UX/UI y estados:** indicador persistente "Sin conexión — N eventos pendientes"; con el buffer lleno (1,000) se rechaza el nuevo evento con alerta y se indica reintentar (interpretación operativa, A-13).
- **Trazabilidad:** RF-MOV-01, RF-MOV-03 · RNF-FIA-01 · OE-04, OE-12 · KPI-39.

### SIGE-US-033 — Sincronizar y validar los eventos capturados sin conexión
**Épica:** EP-05 · **Módulo:** MOV/AST/API · **Actor:** SIS (para PRE, PAD) · **Prioridad:** Must · **Hito:** 04/06 **[Habilitadora]**
> **Como** personal administrativo, **quiero** que los eventos guardados sin conexión se envíen solos al recuperarse la conexión y se validen en el servidor, **para** que solo se incorporen al historial los registros válidos.

- **Reglas de negocio:** RN-MOV-02 · RN-API-01 · RN-AST-03 (rebote) · RN-EST-05 · RN-QR-04 (el backend valida identidad, estatus, unicidad y rebote antes de volverlo definitivo) · RN-TRX-07.
- **UX/UI y estados:** el dispositivo reintenta periódicamente; al terminar muestra resumen (aceptados/descartados); los descartados se notifican al operador con motivo (estudiante inactivo, QR revocado, duplicado).
- **Flujos alternativos:** evento válido → continúa en la verificación de rebote (F-AST §1, E7, punto B); si el estudiante ya fue marcado `FALTÓ` por el proceso de las 10:00, aplica US-031. La hora usada para el estado es la de captura (⚠ A-18).
- **Dependencias:** US-032, US-029, US-031.
- **Trazabilidad:** RF-MOV-01 · RNF-FIA-01 · OE-04.

### SIGE-US-034 — Justificar o modificar la asistencia de un estudiante
**Épica:** EP-05 · **Módulo:** AST · **Actor:** PAD, ADM · **Prioridad:** Must · **Hito:** 07
> **Como** personal administrativo, **quiero** justificar una falta o corregir un estado de asistencia con motivo y trazabilidad, **para** reflejar situaciones especiales autorizadas sin perder el registro original.

- **Contexto:** F-AST §7 (compartida con docentes; ver US-043). Disponible en web y móvil (acta §6.10).
- **Reglas de negocio:** RN-AST-04 (solo ADM o PAD) · RN-AST-05 (motivo obligatorio; se conservan valor anterior, nuevo, usuario y fecha/hora) · RN-AST-06 (un registro nunca se elimina) · RN-AUT-05, RN-TRX-07 (marca `MANUAL`).
- **Datos:** registro afectado, nuevo estado (p. ej. `FALTA JUSTIFICADA`), motivo (obl.).
- **UX/UI y estados:** el flujo pide motivo antes de confirmar; roles no autorizados no ven la acción y el backend la rechaza.
- **Trazabilidad:** RF-AST-06 · OE-04 · KPI-63, KPI-64 · A-07.

### SIGE-US-035 — Consultar la asistencia diaria de un grupo
**Épica:** EP-05 · **Módulo:** AST · **Actor:** PRE, PAD, ADM · **Prioridad:** Must · **Hito:** 07
> **Como** prefecto o personal administrativo, **quiero** elegir una fecha y un grupo y ver la lista completa de estudiantes con su estado, **para** dar seguimiento diario a la asistencia.

- **Reglas de negocio:** RN-TRX-02 · RN-TRX-03 · RN-TRX-07 (se distingue el origen del estado) · el historial de fechas anteriores nunca se pierde.
- **Datos:** fecha, grupo; por estudiante: estado, hora del primer escaneo, origen, si fue justificado.
- **UX/UI y estados:** tabla (escritorio) / tarjetas (móvil); filtros por estado; estados: cargando, sin registros (día no lectivo), error.
- **Trazabilidad:** RF-AST-04 · OE-04 · KPI-59.

### SIGE-US-036 — Consultar el historial individual de asistencia
**Épica:** EP-05 · **Módulo:** AST · **Actor:** PRE, PAD, ADM · **Prioridad:** Must · **Hito:** 07
> **Como** personal autorizado, **quiero** ver el historial acumulado de un estudiante durante el ciclo escolar, **para** identificar patrones de faltas o retardos.

- **Datos:** estudiante, periodo; por fecha: estado, hora, origen, justificaciones y sus modificaciones (según permisos).
- **UX/UI y estados:** línea de tiempo/tabla con filtros por periodo y estado; ambas vistas (grupo y estudiante) provienen de la misma información almacenada.
- **Trazabilidad:** RF-AST-05 · OE-04 · KPI-62.

### SIGE-US-037 — Obtener información consolidada de asistencia
**Épica:** EP-05 · **Módulo:** AST · **Actor:** ADM, PAD, SL · **Prioridad:** Should · **Hito:** 07
> **Como** personal autorizado, **quiero** consultar o exportar la asistencia agregada por estudiante, grupo y periodo, **para** apoyar la evaluación académica conforme a las reglas de la institución.

- **Reglas de negocio:** la fórmula de ponderación queda fuera del alcance (RF-AST-07) · RN-TRX-02 (SL solo ve información consolidada).
- **Datos:** conteos por estado, porcentajes, periodo; export CSV/XLSX (propuesta).
- **UX/UI y estados:** cómo acceden los docentes a este insumo no está definido (⚠ A-19).
- **Trazabilidad:** RF-AST-07 · OE-04 · Hito 07.

---

# EP-06 — Control de asistencia del personal docente

### SIGE-US-038 — Registrar a un docente y generar su QR **[Propuesta]**
**Épica:** EP-06 · **Módulo:** AST/QR · **Actor:** PAD, ADM · **Prioridad:** Must (propuesta, ver A-08) · **Hito:** 03
> **Como** personal administrativo, **quiero** dar de alta a un docente y generar su QR individual, **para** poder registrar su asistencia sin que necesite una cuenta de SIGE.

- **Contexto:** RN-QR-05 y RN-AST-11 presuponen docentes con QR, pero no existe un RF que los defina (A-08).
- **Reglas de negocio:** RN-AST-11 (cada docente debe tener un QR vigente asociado inequívocamente a su identidad) · RN-QR-05 (máximo un QR vigente por persona y tipo de registro; estudiantes y docentes tienen identificadores independientes) · RN-QR-02/03 (mismas reglas de token que US-022) · RF-AST-08 (el docente no requiere cuenta).
- **Datos (mínimos, RN-TRX-01):** nombre completo, identificador interno, estado (activo/inactivo), QR.
- **UX/UI y estados:** reutiliza el subproceso de token de F-QR T.
- **Trazabilidad:** RN-AST-11, RN-QR-05 · OE-04 · A-08.

### SIGE-US-039 — Programar días y horarios de asistencia de cada docente
**Épica:** EP-06 · **Módulo:** AST · **Actor:** PAD · **Prioridad:** Must · **Hito:** 03
> **Como** personal administrativo, **quiero** registrar para cada docente sus días de asistencia programada y sus horarios esperados de entrada y salida, **para** que el sistema evalúe puntualidad y ausencias solo cuando corresponde.

- **Reglas de negocio:** RF-AST-09 (docentes distintos pueden tener días y horarios distintos; los cambios conservan trazabilidad) · RN-AST-14/18/19 (la puntualidad y la evaluación de ausencias usan esta programación) · RN-AUT-05.
- **Datos:** docente, días programados, hora esperada de entrada, hora esperada de salida, tolerancia de puntualidad (⚠ A-10).
- **UX/UI y estados:** calendario semanal por docente; historial de cambios de programación; aviso si un docente no tiene programación (no se evaluará ausencia).
- **Trazabilidad:** RF-AST-09 · OE-04 · Hito 03.

### SIGE-US-040 — Registrar la ENTRADA de un docente
**Épica:** EP-06 · **Módulo:** AST · **Actor:** PAD · **Prioridad:** Must · **Hito:** 03
> **Como** personal administrativo, **quiero** escanear el QR de un docente y registrar su entrada, **para** saber si llegó a tiempo según su horario.

- **Contexto:** F-AST §5 (D1–D9).
- **Reglas de negocio:** RN-AST-10 (solo PAD) · RN-AST-11 (QR válido, vigente y de docente) · RN-AST-12 (PAD elige manualmente `ENTRADA`/`SALIDA`) · RN-AST-13 (máximo una `ENTRADA` por fecha) · RN-AST-14 y RN-AST-19 (puntualidad contra el horario específico del docente para ese día) · RF-AST-09 · RN-AST-21 (conservación permanente).
- **Datos:** docente, fecha, hora, estado, origen = `ESCANEO`.
- **UX/UI y estados:** escaneo → selección de tipo → resultado (`ASISTIÓ`/`LLEGÓ TARDE`) o rechazo; si ya hay entrada ese día → "Segunda entrada no permitida"; si el docente **no** tiene asistencia programada ese día → se registra el evento sin evaluar puntualidad ni ausencia.
- **Trazabilidad:** RF-AST-08, RF-AST-09 · OE-04.

### SIGE-US-041 — Registrar la SALIDA de un docente
**Épica:** EP-06 · **Módulo:** AST · **Actor:** PAD · **Prioridad:** Must · **Hito:** 03
> **Como** personal administrativo, **quiero** registrar la salida de un docente con su hora efectiva, **para** conservar su jornada real.

- **Reglas de negocio:** RN-AST-10/11/12 · RN-AST-16 (máximo una `SALIDA` por docente y fecha) · RN-AST-20 (se conserva la hora efectiva del escaneo; el horario esperado no implica que haya salido a esa hora; no se infiere salida automática) · RN-AST-21.
- **UX/UI y estados:** segunda salida → rechazo; ¿se permite `SALIDA` sin `ENTRADA` previa? No está definido (A-10).
- **Trazabilidad:** RF-AST-08 · OE-04.

### SIGE-US-042 — Detectar automáticamente las ausencias de docentes
**Épica:** EP-06 · **Módulo:** AST · **Actor:** SIS (beneficia a PAD, ADM) · **Prioridad:** Must · **Hito:** 03
> **Como** personal administrativo, **quiero** que el sistema marque `FALTÓ` a los docentes con asistencia programada y sin `ENTRADA` a la hora de verificación, **para** contar con un historial confiable de su asistencia.

- **Contexto:** F-AST §6.
- **Reglas de negocio:** RN-AST-15 y RN-AST-18 (solo se evalúa ausencia si hay asistencia programada ese día; docentes sin programación no se marcan) · RN-TRX-07 (`AUTOMÁTICO`) · RF-ADM-02 (hora de verificación docente independiente de la estudiantil).
- **Flujos alternativos:** si después llega una `ENTRADA` válida ese mismo día, el flujo remite a F-AST §5 (D6a); la reclasificación del estado no está definida por regla explícita (⚠ A-09).
- **Dependencias:** US-039, US-055. **Trazabilidad:** RF-AST-08, RF-AST-09 · OE-04.

### SIGE-US-043 — Justificar o modificar la asistencia de un docente
**Épica:** EP-06 · **Módulo:** AST · **Actor:** PAD, ADM · **Prioridad:** Must · **Hito:** 07
> **Como** personal administrativo, **quiero** justificar o corregir un registro de asistencia docente con motivo, **para** reflejar permisos o incidencias autorizadas manteniendo la trazabilidad.

- **Reglas de negocio:** RN-AST-17 (requiere autorización, motivo y trazabilidad inmutable con usuario, fecha/hora, estado anterior, nuevo y motivo) · RN-AST-04 · RN-AST-21 (sin borrado físico) · F-AST §7.
- **Trazabilidad:** RF-AST-06 · OE-04 · KPI-64.

### SIGE-US-044 — Consultar el historial de asistencia docente
**Épica:** EP-06 · **Módulo:** AST · **Actor:** PAD, ADM · **Prioridad:** Must · **Hito:** 03/07
> **Como** personal administrativo, **quiero** consultar las entradas, salidas y estados de un docente por periodo, **para** dar seguimiento a su asistencia igual que con los estudiantes.

- **Reglas de negocio:** RN-AST-21 (registros permanentes) · RN-TRX-03.
- **Datos:** docente, rango de fechas; por día: entrada, salida, estado, origen, justificaciones.
- **Trazabilidad:** RF-AST-08 (punto 7), RF-AST-10 · OE-04 · A-04.

---

# EP-07 — Reportes escolares

### SIGE-US-045 — Registrar un reporte escolar
**Épica:** EP-07 · **Módulo:** REP · **Actor:** DOC · **Prioridad:** Must · **Hito:** 04/07
> **Como** docente, **quiero** registrar un reporte emocional, académico o conductual de un estudiante con su gravedad y opciones del reglamento, **para** que el caso llegue al prefecto con información estructurada.

- **Contexto:** F-REP §1. Disponible en móvil y web con las mismas reglas (RN-MOV-01, RF-REP-05).
- **Reglas de negocio:** RN-AUT-01/05 y RN-EST-05 (rol Docente y estudiante `ACTIVO`) · RN-REP-01 (observación de **50 a 100** caracteres inclusive) · RN-REP-02 (un tipo y un nivel de gravedad, no modificables tras enviarse al prefecto) · RN-TRX-03.
- **Datos:** estudiante (obl.), tipo (`emocional`/`académico`/`conductual`), gravedad, una o más opciones predeterminadas (según tipo/gravedad, del reglamento), observación (50–100), estado inicial `REGISTRADO POR DOCENTE`.
- **UX/UI y estados:** flujo por pasos (tipo → gravedad y opciones → observación); **contador de caracteres visible**; no permite guardar fuera del rango; estados: guardando, éxito, error, rechazo por rol/estatus.
- **Flujos alternativos:** ⚠ A-12 (a qué estudiantes puede reportar un docente y cómo se determina el "prefecto correspondiente").
- **Trazabilidad:** RF-REP-01, RF-REP-05 · OE-05 · KPI-45 a KPI-49.

### SIGE-US-046 — Consultar la bandeja y el estado de los reportes
**Épica:** EP-07 · **Módulo:** REP · **Actor:** DOC, PRE, PAD, ADM · **Prioridad:** Must · **Hito:** 04
> **Como** usuario con acceso a reportes, **quiero** ver la bandeja que corresponde a mi rol y filtrarla, **para** dar seguimiento sin ver información que no me corresponde.

- **Contexto:** F-REP §6.
- **Reglas de negocio:** RN-REP-05 (el DOC solo ve reportes que él registró; ADM y PAD ven todos) · RN-AUT-02 (visible ≠ accionable: ninguna acción de canalización/autorización sin permiso) · RN-TRX-02.
- **Datos:** filtros por tipo, gravedad, grupo, estudiante y estado.
- **UX/UI y estados:** bandeja completa filtrable para PRE/PAD/ADM; lista simple para DOC; vacía, cargando, error. El alcance de la bandeja del PRE (todos vs. asignados) está en A-12.
- **Trazabilidad:** RF-REP-03, RF-REP-05 · OE-05 · KPI-23.

### SIGE-US-047 — Revisar un reporte y canalizarlo o rechazarlo (prefecto)
**Épica:** EP-07 · **Módulo:** REP · **Actor:** PRE · **Prioridad:** Must · **Hito:** 04/07
> **Como** prefecto, **quiero** revisar los reportes recibidos y decidir cuáles canalizo a personal administrativo, **para** filtrar los casos que requieren atención mayor.

- **Contexto:** F-REP §2.
- **Reglas de negocio:** RN-REP-03 (orden estricto sin saltos; rechazo con motivo obligatorio) · RN-REP-06 (cada cambio de etapa genera trazabilidad) · RN-REP-04.
- **Datos:** decisión (aprobar/rechazar), motivo (obl. si rechaza).
- **UX/UI y estados:** aprobar → `REVISADO POR PREFECTO` → acción explícita de canalizar → `CANALIZADO`; rechazar → `RECHAZADO` y notificación al docente autor.
- **Flujos alternativos:** también recibe reportes devueltos por administrativo (US-049) para nueva valoración.
- **Trazabilidad:** RF-REP-02, RF-REP-03, RF-REP-04 · OE-05 · KPI-49, KPI-50.

### SIGE-US-048 — Corregir un reporte rechazado mediante uno nuevo referenciado
**Épica:** EP-07 · **Módulo:** REP · **Actor:** DOC · **Prioridad:** Must · **Hito:** 07
> **Como** docente, **quiero** recibir el motivo de un rechazo y poder registrar un reporte nuevo que haga referencia al original, **para** corregir la clasificación sin alterar lo ya enviado.

- **Contexto:** F-REP §3.
- **Reglas de negocio:** RN-REP-02 (los cambios posteriores requieren un reporte nuevo referenciado al original) · RN-TRX-03 (el original queda archivado y sin modificación) · ⚠ A-11 (contradice el "regreso a etapa anterior" de RN-REP-03).
- **UX/UI y estados:** notificación con motivo; decisión "corregir y reenviar" o dejarlo `RECHAZADO`; el nuevo reporte reentra al flujo desde el registro (F-REP §1).
- **Trazabilidad:** RF-REP-01, RF-REP-04 · OE-05.

### SIGE-US-049 — Revisar reportes canalizados y aprobarlos o devolverlos (administrativo)
**Épica:** EP-07 · **Módulo:** REP · **Actor:** PAD · **Prioridad:** Must · **Hito:** 07
> **Como** personal administrativo, **quiero** revisar los reportes canalizados y aprobarlos o rechazarlos con motivo, **para** asegurar que solo los casos pertinentes avancen.

- **Contexto:** F-REP §4.
- **Reglas de negocio:** RN-REP-03 (rechazo con motivo obligatorio y regreso a una etapa anterior; se modela hacia el prefecto, A-11) · RN-REP-06.
- **UX/UI y estados:** aprobar → `REVISADO POR ADMINISTRATIVO`; rechazar → `RECHAZADO` y regresa a la bandeja del prefecto.
- **Trazabilidad:** RF-REP-02, RF-REP-04 · OE-05 · KPI-51.

### SIGE-US-050 — Decidir si un reporte se comunica a la familia o se resuelve internamente
**Épica:** EP-07 · **Módulo:** REP/COM · **Actor:** PAD · **Prioridad:** Must · **Hito:** 07
> **Como** personal administrativo, **quiero** decidir si un reporte revisado debe comunicarse a la familia y, si no, dejar constancia del motivo, **para** que solo se notifique lo que la institución considere pertinente.

- **Reglas de negocio:** RN-REP-04 (solo tras revisión y autorización de PAD; nunca desde el docente ni el prefecto) · RN-COM-01 (debe existir un contacto válido; si no lo hay, el reporte queda `AUTORIZADO` pendiente de contacto) · RN-EST-07 (advertencia de consentimiento).
- **UX/UI y estados:** decisión Sí/No; No → motivo obligatorio y estado `RESUELTO`; Sí → verificación del contacto → US-052. El criterio de decisión es del PAD (no está en las reglas de origen) y la activación del estado `RESUELTO` es una inferencia (A-11).
- **Trazabilidad:** RF-REP-02, RF-REP-04 · OE-05, OE-06 · KPI-51, KPI-52.

### SIGE-US-051 — Consultar la trazabilidad completa de un reporte
**Épica:** EP-07 · **Módulo:** REP · **Actor:** DOC (los suyos), PRE, PAD, ADM · **Prioridad:** Must · **Hito:** 07
> **Como** usuario autorizado, **quiero** ver el historial de estados de un reporte con quién y cuándo hizo cada cambio, **para** saber en qué punto está y quién lo movió.

- **Reglas de negocio:** RN-REP-06 (cada cambio de etapa genera una entrada automática, visible según rol) · RN-TRX-03 (ningún reporte se elimina) · RN-AUT-02.
- **Datos:** estado (`registrado`, `revisado`, `canalizado`, `rechazado`, `comunicado`, `resuelto`), usuario, fecha/hora, motivo (si aplica).
- **Trazabilidad:** RF-REP-04 · OE-05 · KPI-53.

---

# EP-08 — Comunicación con familiares

### SIGE-US-052 — Enviar por correo la comunicación autorizada a la familia
**Épica:** EP-08 · **Módulo:** COM · **Actor:** PAD (SIS ejecuta el envío) · **Prioridad:** Should (minimización: Must) · **Hito:** 07
> **Como** personal administrativo, **quiero** enviar por correo al contacto familiar la información autorizada de un reporte, **para** mantener informada a la familia sin exponer datos innecesarios del menor.

- **Contexto:** F-REP §5.
- **Reglas de negocio:** RN-COM-01 (solo a un contacto válido del expediente) · RN-COM-02 y RF-COM-03 (contenido limitado a lo explícitamente autorizado; nunca el expediente completo) · RN-REP-04 (previa autorización de PAD) · RN-INF-02 (requiere Internet).
- **Datos:** destinatario (contacto principal/válido), asunto, contenido autorizado.
- **UX/UI y estados:** vista previa del contenido exacto que saldrá; estados: enviando, enviado, fallido, sin Internet.
- **Flujos alternativos:** al envío exitoso → `COMUNICADO A FAMILIA` → `RESUELTO`. Efecto del consentimiento `REVOCADO` sin definir (A-05).
- **Dependencias:** US-050, US-053.
- **Trazabilidad:** RF-COM-01, RF-COM-03 · OE-07 · Riesgo R-02.

### SIGE-US-053 — Registrar el estado de cada envío y reintentarlo
**Épica:** EP-08 · **Módulo:** COM · **Actor:** PAD, SIS · **Prioridad:** Should · **Hito:** 07
> **Como** personal administrativo, **quiero** ver si cada correo quedó pendiente, enviado o fallido y poder reintentar los fallidos, **para** asegurar que la comunicación llegó a procesarse.

- **Reglas de negocio:** RN-COM-03 (todo intento registra fecha, hora y estado `PENDIENTE`/`ENVIADO`/`FALLIDO`; la confirmación de entrega o lectura no puede garantizarse) · RF-COM-02.
- **UX/UI y estados:** los fallidos muestran "Reintentar"; el estado `ENVIADO` nunca se presenta como "leído".
- **Trazabilidad:** RF-COM-02 · OE-07 · Riesgo R-02.

---

# EP-09 — Panel administrativo

### SIGE-US-054 — Administrar catálogos institucionales
**Épica:** EP-09 · **Módulo:** ADM · **Actor:** ADM · **Prioridad:** Must · **Hito:** 02
> **Como** administrador, **quiero** gestionar los catálogos de grupos, grados, ciclos escolares, tipos y niveles de gravedad de reporte, **para** que el resto del sistema opere con datos consistentes.

- **Reglas de negocio:** RN-ADM-01 (solo ADM modifica catálogos) · RN-TRX-03 (los elementos ya usados en historial se **desactivan**, no se eliminan).
- **UX/UI y estados:** listas con alta, edición y desactivación; advertencia de uso antes de desactivar.
- **Trazabilidad:** RF-ADM-01 · OE-10 · KPI-07.

### SIGE-US-055 — Configurar los parámetros operativos de asistencia
**Épica:** EP-09 · **Módulo:** ADM · **Actor:** ADM · **Prioridad:** Should · **Hito:** 02/07
> **Como** administrador, **quiero** configurar la ventana de rebote, la hora de corte y las horas de verificación de ausencias de estudiantes y docentes, **para** adaptar las reglas a la jornada de la institución.

- **Reglas de negocio:** RN-ADM-02 (solo ADM; todo cambio auditado; los cambios no alteran retroactivamente registros ya determinados; A-02) · RN-AST-03 (rebote 1–30 min, 5 por defecto) · RN-AST-08 (verificación estudiantil inicial 10:00) · RF-ADM-02 (parámetros estudiantiles y docentes independientes; opciones del reglamento por tipo/gravedad).
- **Datos:** ventana de rebote (min), hora de corte por grupo/jornada, hora de verificación estudiantil, hora de verificación docente, opciones del reglamento.
- **UX/UI y estados:** validación de rangos; muestra desde cuándo aplica el nuevo valor.
- **Trazabilidad:** RF-ADM-02 · OE-10 · KPI-16.

### SIGE-US-056 — Ver el panel de indicadores operativos
**Épica:** EP-09 · **Módulo:** ADM · **Actor:** ADM (SL por confirmar) · **Prioridad:** Could · **Hito:** 02/07
> **Como** administrador, **quiero** ver indicadores clave —asistencia del día, reportes abiertos, credenciales pendientes—, **para** tomar decisiones con información al momento.

- **Reglas de negocio:** RN-TRX-02 (datos consolidados, sin datos individuales innecesarios).
- **UX/UI y estados:** tarjetas de resumen con actualización manual o periódica; estados: cargando, sin datos, error.
- **Trazabilidad:** RF-ADM-03 · OE-10.

---

# EP-10 — Continuidad y operación local

### SIGE-US-057 — Respaldar y restaurar la base de datos **[Habilitadora]**
**Épica:** EP-10 · **Módulo:** API/INF · **Actor:** SIS; ADM (restauración) · **Prioridad:** Must · **Hito:** 05
> **Como** administrador, **quiero** que existan respaldos automáticos y un procedimiento probado de restauración, **para** recuperarme de una falla del servidor local sin perder información.

- **Reglas de negocio:** RN-API-03 (respaldo automático según la periodicidad configurada, mínimo diaria, sin acción manual; se registra éxito o fallo) · RN-INF-03 (ante interrupción se sigue el procedimiento documentado desde el último respaldo válido) · RNF-FIA-03 (restauración completa probada antes de cada hito de cierre) · RNF-POR-01 (instalación reproducible en un equipo de reemplazo).
- **UX/UI y estados:** el ADM ve fecha, resultado y tamaño del último respaldo; alerta si falla.
- **Trazabilidad:** RF-API-03, RF-INF-03 · OE-08, OE-12 · KPI-32, KPI-33.

### SIGE-US-058 — Operar las funciones internas sin Internet
**Épica:** EP-10 · **Módulo:** INF · **Actor:** Todos los roles operativos · **Prioridad:** Must · **Hito:** 05 **[Habilitadora]**
> **Como** personal escolar, **quiero** seguir registrando asistencia, reportes y consultas aunque no haya Internet, **para** que la operación diaria no se detenga por fallas del proveedor.

- **Reglas de negocio:** RN-INF-01 (asistencia, reportes y consulta operan en la red local) · RN-INF-02 (correo y acceso remoto dependen de Internet; su caída no afecta lo interno) · RF-INF-02 · RF-MOV-03 · acta: pérdida de Internet ≠ pérdida de la red local.
- **UX/UI y estados:** mensajes distintos para "sin Internet" (solo se deshabilita el correo) y "sin conexión al servidor" (activa el modo offline, US-032).
- **Trazabilidad:** RF-INF-01, RF-INF-02, RF-MOV-03 · OE-12 · KPI-31, KPI-43.

---

## Anexo A — Vacíos, ambigüedades e inconsistencias detectados

| # | Hallazgo en los documentos fuente | Decisión provisional en las historias | Propuesta |
|---|---|---|---|
| A-01 | **RN-AST-09 aparece dos veces** con consecuencia distinta: una actualiza "según la hora efectiva"; la otra fija `LLEGÓ TARDE`. El flujo (F-AST §3) evalúa contra la hora de corte. | Se sigue el flujo (US-031). | Conservar una sola redacción; si la hora de verificación es posterior a la de corte, el resultado será casi siempre `LLEGÓ TARDE`. |
| A-02 | **RN-ADM-02 está duplicada** (§2.5 y §2.8) con redacciones distintas. | Se usa la de §2.5 (incluye hora de verificación y no retroactividad). | Eliminar la duplicada. |
| A-03 | Se citan reglas **inexistentes**: RN-AST-02 (en RN-AST-03 y RN-MOV-02), RN-AST-07 (en RN-TRX-07 y matriz §4) y no existe RN-TRX-04. | Se cubrió el comportamiento por la vía de RN-AST-03/01. | Definir (o retirar) RN-AST-02 y RN-AST-07; revisar la numeración TRX. |
| A-04 | **Desfase RF↔RN↔flujo:** las RN-AST-10 a 21 citan RF-AST-09/10 para registro y programación docente; el RF v2 los define como RF-AST-08/09/10; el flujo cita RF-AST-08. | Se usa la numeración del RF v2. | Reetiquetar las RN. |
| A-05 | **RN-EST-07** tiene disparador y consecuencia copiados de RN-EST-06; no se define el efecto de `REVOCADO` ni qué pasa con el QR en un reingreso; no hay transiciones desde `EGRESADO`. | No se bloquea ninguna operación por consentimiento; `EGRESADO` es estado final. | Definir efectos operativos del consentimiento y política de QR en reingreso. |
| A-06 | RF-AST-02 dice "5 minutos **mínimo**"; RN-AST-03 dice 5 por defecto, configurable de 1 a 30. | Se usa RN-AST-03. | Corregir el RF. |
| A-07 | `FALTA JUSTIFICADA` está en el acta (OE-04, KPI-61) pero las RN no la definen como estado. | Es el resultado de justificar una `FALTÓ` (US-034). | Añadir RN de definición del estado. |
| A-08 | **No hay RF** para alta de docentes ni para generar su QR, aunque RN-QR-05 y RN-AST-11 lo presuponen. | Se propone US-038. | Agregar RF (p. ej. RF-AST-11 / RF-QR-04). |
| A-09 | Un docente marcado `FALTÓ` que luego registra `ENTRADA` no tiene regla equivalente a RN-AST-09 (solo inferido en la nota del flujo, conector D). | Se documenta como pendiente en US-042. | Definir regla explícita. |
| A-10 | "Límite establecido" de puntualidad docente sin definir; no se dice si se permite `SALIDA` sin `ENTRADA`. | Tolerancia como dato de la programación. | Definir tolerancia (global o por docente) y la regla de salida sin entrada. |
| A-11 | **Reportes:** RN-REP-03 dice que un rechazo regresa a una etapa anterior; RN-REP-02 y F-REP §3 dicen que tras rechazo del prefecto se corrige con un reporte **nuevo**. El estado `RESUELTO` no tiene criterio de activación; el retorno del rechazo administrativo al prefecto es interpretación. | Se modeló según los diagramas. | Ratificar el criterio con la institución. |
| A-12 | No se define cómo se asigna el "prefecto correspondiente", a qué estudiantes puede reportar un docente ni si la bandeja del prefecto es total o de reportes asignados (acta §6.5 B vs F-REP §6). | Se documenta la incertidumbre en US-045/046. | Definir asignación por grupo/grado. |
| A-13 | En F-AST §1 la validación en BD (E2–E5) ocurre **antes** de evaluar la conexión (E6); sin conexión esas validaciones no pueden ejecutarse. El rechazo por buffer lleno es interpretación de RNF-FIA-01. | Offline: se guarda solo el token leído y todo se valida al sincronizar (US-032/033). | Reordenar el diagrama. |
| A-14 | **Registro incompleto:** no se define "requisitos mínimos", ni si un incompleto es `ACTIVO`, ni la definición de "contacto válido"; RN-EST-03 dice que se bloquea hasta tener tutor. Las aristas "Sí" de F-EST para "¿Faltan datos obligatorios?" son ambiguas. | Tutor siempre obligatorio; el incompleto no genera credencial (RN-CRE-01). | Definir mínimos, estatus y "contacto válido". |
| A-15 | **Importación:** el flujo coloca la vista previa después de crear/asignar grupo (se interpretó como *staging*); una salvaguarda de duplicado termina **toda** la importación, mientras RN-IMP-03 rechaza solo la fila; el rol que importa no está definido. | Filas independientes; ADM y PAD importan. | Aclarar la salvaguarda y el rol. |
| A-16 | RN-CRE-01 exige fotografía y habla de PDF; RF-CRE-01 solo menciona la imagen del QR (incluido el sticker). | La foto se exige en la exportación de credencial completa; para sticker no está definido. | Aclarar. |
| A-17 | No se define la **duración** del bloqueo por intentos fallidos. | Parámetro configurable. | Definir valor por defecto. |
| A-18 | No se define la **fuente de la hora** (servidor vs dispositivo) para determinar puntualidad, sobre todo en eventos offline. | Se usa la hora de captura; la validación es del backend. | Fijar sincronización horaria del servidor y política para offline. |
| A-19 | El acta dice que los docentes usarán la información consolidada de asistencia, pero el rol DOC no la tiene en RF/actores. | Acceso ADM/PAD/SL; los docentes la reciben vía PAD. | Definir acceso de docentes. |
| A-20 | **Numeración de OE/KPI inconsistente:** el RF v2 cita OE-13 (el acta v9 llega a OE-12) y el acta §13 cita KPIs con numeración distinta a su matriz. | Se citan OE/KPI tal como aparecen en el RF v2. | Reconciliar acta, RF y RN. |
| A-21 | Roles no definidos: ADM como operador de escaneo/generación de QR; SL en indicadores y bitácora. | Ver matriz de US-006 (conservadora). | Confirmar la matriz de permisos. |
| A-22 | RF-EST-01 recolecta domicilio, sexo y CURP; RN-TRX-01 exige minimización. | Se conservan por el RF. | Justificar cada campo o marcarlos opcionales. |

---

## Anexo B — Cobertura de reglas de negocio

| Módulo | Reglas | Historias |
|---|---|---|
| EST | RN-EST-01 a 07 | US-008 a US-016 |
| IMP | RN-IMP-01 a 04 | US-017 a US-021 |
| QR / CRE | RN-QR-01 a 05 · RN-CRE-01 | US-022 a US-027 · US-038 |
| AUT | RN-AUT-01 a 05 | US-001 a US-007 |
| AST (estudiantes) | RN-AST-01 y 03 a 09 | US-027 a US-036 · US-055 |
| AST (docentes) | RN-AST-10 a 21 | US-038 a US-044 |
| REP | RN-REP-01 a 06 | US-045 a US-051 |
| COM | RN-COM-01 a 03 | US-050 · US-052 · US-053 |
| ADM | RN-ADM-01 y 02 | US-054 · US-055 |
| API / MOV / INF | RN-API-01 a 03 · RN-MOV-01 y 02 · RN-INF-01 a 03 | US-006 · US-032 · US-033 · US-057 · US-058 |
| TRX | RN-TRX-01 a 03, 05 a 07 | Transversales (criterios CT en el documento de aceptación) |
