# Especificación de Requisitos del Sistema — SIGE
### Sistema Integral de Gestión Escolar
**Documento derivado del Acta Constitutiva del Proyecto v9**
**Versión:** 2.0 — Ampliación de RF/RNF | **Estado:** Para revisión del equipo

---

## 1. Introducción

### 1.1 Propósito
Este documento expande y formaliza la matriz preliminar de Requisitos Funcionales (RF) y No Funcionales (RNF) entregada por el equipo, alineándola con la totalidad de los objetivos específicos (OE-01 a OE-13), el alcance y los hitos definidos en el Acta Constitutiva v8. Sustituye la matriz inicial de 7 RF y 5 RNF por una especificación completa, trazable y priorizada, que sirve de insumo directo para el siguiente documento del plan (Historias de Usuario y Criterios de Aceptación Específicos, sección 15 del acta).

### 1.2 Alcance del documento
Se cubren los módulos correspondientes a **todos** los hitos (01–08), con **prioridad Must-have concentrada en Hito 01 (QR) e Hito 02 (Sistema web integrado)**, tal como pedía la matriz original, pero documentando también los requisitos de asistencia, reportes, comunicación, móvil e infraestructura para que la trazabilidad hacia hitos posteriores quede establecida desde ahora y no se tenga que rehacer el ejercicio de ingeniería de requisitos en cada etapa.

### 1.3 Estándares y marcos de referencia utilizados
- **IEEE 29148:2018** — estructura y redacción de requisitos (identificador único, verbo modal, atomicidad, verificabilidad).
- **ISO/IEC/IEEE 25010** — modelo de calidad de software, usado para clasificar los RNF (adecuación funcional, eficiencia de desempeño, compatibilidad, usabilidad, fiabilidad, seguridad, mantenibilidad, portabilidad).
- **OWASP ASVS (nivel 1–2)** — línea base de seguridad para autenticación, sesión y manejo de datos.
- **LFPDPPP y su Reglamento** — protección de datos personales de menores de edad (transversal a todo el documento).
- **MoSCoW** — priorización de requisitos (Must / Should / Could / Won't, en esta fase).

### 1.4 Convenciones de redacción
- Cada requisito tiene un **ID único** con prefijo por módulo (p. ej. `RF-QR-01`).
- Se usa **DEBE** para requisitos obligatorios (Must), **DEBERÍA** para Should, **PODRÁ** para Could.
- Cada requisito incluye: descripción, reglas de negocio / criterios de aceptación, prioridad, y trazabilidad a Objetivo Específico (OE), Hito y KPI del acta.
- Los RF-01 a RF-07 y RNF-01 a RNF-05 de la versión original se **conservan como base** y se reetiquetan dentro del esquema modular, señalando explícitamente de qué requisito original provienen.

Antes de entrar al detalle técnico, aquí va una explicación en términos simples de qué hace cada módulo y a qué prefijo de requisito corresponde:
 
| Prefijo | Módulo | ¿Qué hace, en simple? |
|---|---|---|
| **EST** | Gestión de Estudiantes | La "ficha" de cada alumno: nombre, grupo, foto, tutor, si sigue activo o ya se dio de baja. Es la base de datos maestra de la que todo lo demás depende. |
| **IMP** | Importación masiva | Para no dar de alta a 500 alumnos a mano: subes un Excel/CSV con el formato correcto y el sistema los carga solo, avisando cuáles filas fallaron y por qué. |
| **QR** | Identificación QR | Le genera a cada alumno un código único (como un "gafete digital") que lo identifica en el sistema sin mostrar sus datos personales a simple vista. |
| **CRE** | Credenciales | Toma esos códigos QR y los entrega al personal administrativo para que los agreguen en la credencial fisica para su impresión o como sticker para ser añadido a credenciales fisicas ya impresas. |
| **AUT** | Autenticación y usuarios | El "login" del sistema: quién puede entrar, con qué contraseña, y qué rol tiene (Admin, Prefecto, Docente, etc.), para que cada quien vea solo lo que le toca. |
| **AST** | Asistencia | El corazón operativo diario: cuando un alumno escanea su QR en la entrada, aquí se decide si llegó a tiempo, tarde, o si faltó, y se guarda el historial. |
| **REP** | Reportes escolares | El flujo de "reportes de conducta/académicos/emocionales": el maestro lo levanta, el prefecto lo revisa, administración decide si se avisa a la familia. |
| **COM** | Comunicación con familiares | La parte que efectivamente manda por correo electrónico los avisos y reportes previamente autorizados al papá/mamá/tutor. |
| **ADM** | Panel administrativo | La "sala de control" para el Administrador: gestionar usuarios, catálogos (grupos, tipos de reporte) y ver indicadores generales. |
| **API** | Backend / API / Base de datos | La maquinaria interna que todos los módulos usan por debajo: donde se guarda todo, se valida la información y se hacen los respaldos. No lo ve el usuario final directamente. |
| **MOV** | Aplicación móvil | La versión para celular de asistencia y reportes, pensada para que el prefecto/docente la use caminando por la escuela, sin necesitar una computadora. |
| **INF** | Infraestructura / Servidor local | Que todo esto corra dentro de una compu de la escuela conectada a su red local, para que siga funcionando aunque se caiga el Internet. |
 

Y para los No Funcionales, la idea detrás de cada categoría:
 
| Categoría RNF | ¿Qué garantiza? |
|---|---|
| **DES** (Desempeño) | Que el sistema responda rápido, sobre todo en la puerta de entrada donde hay fila de alumnos. |
| **SEG** (Seguridad) | Que los datos —sobre todo de menores de edad— estén protegidos, cifrados y solo visibles para quien debe verlos. |
| **FIA** (Fiabilidad) | Que el sistema no se caiga a media jornada, y si algo falla (Internet, servidor), se pueda recuperar sin perder información. |
| **USA** (Usabilidad) | Que sea fácil de usar para un prefecto sin capacitación técnica, incluso con sol pegándole a la pantalla. |
| **COM** (Compatibilidad) | Que funcione con el hardware que ya tiene o vaya a comprar la escuela (lectores QR, cámaras, celulares comunes). |
| **MAN** (Mantenibilidad) | Que el código quede ordenado y documentado, para que el proyecto sobreviva si alguien del equipo se ausenta. |
| **POR** (Portabilidad) | Que si la compu-servidor se descompone, se pueda levantar todo de nuevo en otra sin reinventar el proceso. |
 
---

## 2. Actores del sistema

| Actor | Descripción | Acceso principal |
|---|---|---|
| **Administrador / Directivo** | Control total: usuarios, estudiantes, configuración, reportes, KPIs | Web |
| **Prefecto** | Escaneo de asistencia, consulta de expedientes, recepción y canalización de reportes | Web + Móvil |
| **Docente** | Registro y consulta de sus propios reportes escolares (de los grupos que tiene asignados). No consulta asistencia directamente: recibe la información consolidada mediante exportación entregada por PAD/ADM. Su cuenta se vincula a su ficha de docente (RN-AST-30) | Móvil (y web) |
| **Personal administrativo** | Alta/edición de estudiantes e importación, generación de QR y exportación de credenciales, escaneo de asistencia estudiantil, alta y programación de docentes y registro de su asistencia, consulta de expedientes, revisión de reportes canalizados, autorización y envío de comunicación a familia, justificación/modificación de asistencias, información consolidada de asistencia | Web + Móvil |
| **Solo lectura / Auditoría** | Consulta de estadísticas, información consolidada e indicadores, sin capacidad de modificación; no accede a la bitácora ni a expedientes | Web |
| **Familiar / Tutor** | Receptor pasivo de comunicaciones (Solo correo); no tiene cuenta en el sistema en esta fase | Ninguno (canal externo) |
| **Estudiante** | Sujeto de los datos; se identifica mediante credencial con QR | No aplica (no es usuario del sistema) |

> Nota: La matriz completa de permisos es la RN-AUT-06 del catálogo de reglas de negocio..

---

## 3. Requisitos Funcionales (RF)

### 3.1 Gestión de Estudiantes e Importación — *(OE-02, OE-01 parcial · Hito 01–02)*

**RF-EST-01 — Expediente digital del estudiante** *(reemplaza y expande RF-02)*
El sistema DEBE mantener una ficha centralizada y única por estudiante con los siguientes datos:
> - **Mínimos (obligatorios para guardar):** nombre completo, matrícula, grado, grupo, ciclo escolar, estatus (`ACTIVO`, `BAJA`, `EGRESADO`) y al menos un tutor con contacto válido (RN-EST-03, RN-EST-11).
> - **Obligatorios diferidos (pueden completarse después; su ausencia genera un registro INCOMPLETO, RN-EST-10):** fecha de nacimiento y fotografía.
> - **Opcionales (sujetos a justificación de necesidad, RN-TRX-01):** domicilio, sexo y CURP.
El sistema DEBE mostrar los campos faltantes de un registro incompleto y DEBE documentar, para cada campo recolectado, el módulo que lo requiere. Los campos opcionales que ningún módulo del alcance requiera DEBEN retirarse del modelo de datos.
- *Criterios de aceptación:* 100 % de estudiantes de prueba con expediente completo y estatus consistente (KPI-07, KPI-09).
- *Prioridad:* Must. **Trazabilidad:** OE-02 · Hito 02 · KPI-07, KPI-09.

**RF-EST-02 — Transiciones de estatus del estudiante**
El sistema DEBE restringir las transiciones de estatus a un conjunto válido (`ACTIVO → BAJA`, `ACTIVO → EGRESADO`, `BAJA → ACTIVO` solo con autorización explícita del Administrador). `EGRESADO` es un estatus final. El sistema DEBE impedir el registro de nueva asistencia o reportes para estudiantes en estatus distinto de `ACTIVO`, DEBE conservar el QR vigente del estudiante durante una baja y un reingreso (los escaneos se rechazan por estatus) y DEBE auditar cada cambio.
- *Prioridad:* Should. **Trazabilidad:** OE-02 · Hito 02 · RN-EST-04, RN-EST-06, RN-EST-09.

**RF-EST-03 — Asociación de familiares/tutores**
El sistema DEBE permitir asociar uno o más tutores por estudiante, cada uno con nombre, relación, teléfono y correo, y DEBE permitir marcar un tutor como "contacto principal" para efectos de notificación. Un tutor tiene **contacto válido** cuando cuenta con nombre, relación y correo con formato válido (RN-EST-11); el sistema DEBE marcarlo automáticamente y permitir al Personal administrativo o Administrador invalidarlo con motivo. Un estudiante no puede guardarse sin al menos un tutor con contacto válido.
- *Prioridad:* Must. **Trazabilidad:** OE-02 · Hito 02.

**RF-EST-04 — Consulta y filtrado de expedientes**
El sistema DEBE permitir buscar y filtrar estudiantes por nombre, matrícula, grupo, grado y estatus, con resultados paginados.
- *Prioridad:* Must. **Trazabilidad:** OE-02 · Hito 02.

**RF-EST-05 — Registro de consentimiento del tutor**
El sistema DEBE permitir registrar, para cada tutor/familiar asociado a un estudiante, el estatus de consentimiento para el tratamiento de los datos personales del menor (PENDIENTE, OTORGADO, REVOCADO) junto con la fecha de registro, conforme a la sección "Protección de datos de menores" del acta y a la LFPDPPP. El sistema DEBE advertir al personal autorizado, al consultar el expediente, cuando algún tutor tenga consentimiento `PENDIENTE` o `REVOCADO`, sin bloquear la operación escolar (RN-EST-08), y NO DEBE enviar comunicaciones a un tutor con consentimiento `REVOCADO` (RN-COM-04). El estatus puede documentarse fuera de SIGE (RN-EST-07).
> El sistema DEBE advertir al personal autorizado, al consultar el expediente, cuando algún tutor tenga consentimiento `PENDIENTE` o `REVOCADO`, sin bloquear la operación escolar (RN-EST-08), y NO DEBE enviar comunicaciones a un tutor con consentimiento `REVOCADO` (RN-COM-04). El estatus puede documentarse fuera de SIGE (RN-EST-07).
- *Prioridad:* Must (regulatorio). **Trazabilidad:** OE-02 · Hito 02 · Protección de datos de menores (acta) · KPI-07, KPI-09, KPI-75 (tutores con estatus de consentimiento registrado, 100 %; ver sección 6).

**RF-IMP-01 — Importación masiva de estudiantes (CSV/XLSX)** *(expande RF-01)*
El sistema DEBE permitir cargar archivos CSV y XLSX basados estrictamente en un diccionario de datos publicado por el equipo de desarrollo, ejecutando el proceso en modo transaccional por fila (una fila inválida no bloquea a las demás) y emitiendo, al finalizar, un reporte descargable con: total de filas procesadas, filas insertadas, filas con error y el detalle del error por fila (columna y motivo).
- *Fuera de alcance (heredado del acta):* limpieza o transformación de datos históricos no estructurados — la institución debe entregar los archivos ya conformes al diccionario de datos. Tampoco se contempla la importación masiva de docentes (la matriz de alcance del acta limita la carga masiva a estudiantes); el alta de docentes es individual, por interfaz web.
> - Solo el Administrador y el Personal administrativo PUEDEN importar (RN-IMP-05).
> - Toda importación DEBE pasar por una vista previa (*dry-run*) sin persistencia; solo la confirmación explícita persiste los registros válidos (RN-IMP-04).
> - Las filas sin datos mínimos se descartan; las filas con datos obligatorios diferidos vacíos se insertan como INCOMPLETO (RN-IMP-06).
> - Si al confirmar una matrícula ya fue creada por otro proceso, solo esa fila se rechaza (RN-IMP-07).
- *Prioridad:* Must. **Trazabilidad:** OE-02 · Hito 02 · Fuera de alcance §7.

**RF-IMP-02 — Plantilla de importación descargable**
El sistema DEBERÍA proveer una plantilla CSV/XLSX descargable con las columnas exactas del diccionario de datos y ejemplos de formato válido, para reducir errores de captura por parte de la institución.
- *Prioridad:* Should. **Trazabilidad:** OE-02 · Hito 02.

---

### 3.2 Identificación mediante QR y Credenciales — *(OE-01 · Hito 01)*

**RF-QR-01 — Generación de identificador seguro por estudiante** *(expande RF-03)*
El sistema DEBE generar, para el 100% de los estudiantes registrados, un identificador único e irrepetible que **no exponga datos personales directamente legibles en el payload del código QR** (ver RNF-SEG-02); el identificador DEBE quedar asociado inequívocamente al registro del estudiante en la base de datos.
- *Criterios de aceptación:* 0 identificadores duplicados; 100% de QR legibles y correctamente asociados (KPI-01 a KPI-04).
- *Prioridad:* Must. **Trazabilidad:** OE-01 · Hito 01 · KPI-01, KPI-02, KPI-03, KPI-04.

**RF-QR-02 — Validación de unicidad e integridad**
El sistema DEBE ejecutar una validación automática de integridad (sin duplicados, sin huérfanos) antes de habilitar el lote de códigos para producción de credenciales, dentro del plazo máximo de 6 semanas desde el inicio del proyecto.
- *Prioridad:* Must. **Trazabilidad:** OE-01 · Hito 01 · KPI-05.

**RF-QR-03 — Revocación y regeneración de identificador**
El sistema DEBE permitir, únicamente al rol Administrador, revocar el identificador de un estudiante o de un docente (p. ej. por pérdida o duplicidad de credencial física) y generar uno nuevo, invalidando el anterior para cualquier registro futuro de asistencia y conservando la trazabilidad del cambio.
- *Justificación:* no contemplado explícitamente en la matriz original, pero necesario en operación real (credenciales extraviadas); se agrega como requisito complementario al OE-01.
- *Prioridad:* Should. **Trazabilidad:** OE-01 · Hito 01 (complementario).

**RF-QR-04 — QR del personal docente**
El sistema DEBE generar, para cada docente `ACTIVO`, un identificador único, opaco e irrepetible, con las mismas reglas que RF-QR-01 (sin datos personales legibles; unicidad contra tokens vigentes y revocados). El Personal administrativo y el Administrador PUEDEN generarlo; solo el Administrador PUEDE revocarlo y regenerarlo (mismas reglas que RF-QR-03), y el QR docente es independiente del QR de estudiantes (RN-QR-05, RN-QR-06). Su exportación sigue RF-CRE-01/RF-CRE-02. Al desactivarse un docente su QR vigente no se revoca y se conserva para una eventual reactivación (RN-AST-29). La exportación sigue RN-CRE-01: la credencial completa exige fotografía y el sticker no.
- *Prioridad:* Must. **Trazabilidad:**  OE-01, OE-04 · Hito 03 · KPI-72 · RN-AST-11, RN-QR-05, RN-QR-06.

**RF-CRE-01 — Exportación de credenciales para impresión** *(expande RF-04)*
El sistema DEBE generar, para cada estudiante o docente `ACTIVO` con QR vigente, una imagen de alta resolución del QR individual y un PDF por lote o individual, en dos modalidades: **credencial completa** (requiere fotografía cargada) y **sticker** de QR (no requiere fotografía) para pegarse sobre una credencial ya impresa. Los estudiantes que no cumplan las condiciones DEBEN excluirse y listarse aparte como pendientes con el motivo (RN-CRE-01). El diseño, impresión y entrega física quedan fuera del alcance.
- *Prioridad:* Must. **Trazabilidad:** OE-01 · Hito 01 · KPI-06.

**RF-CRE-02 — Reimpresión selectiva de credenciales**
El sistema DEBERÍA permitir reexportar el código QR (imagen/PDF) de un subconjunto de estudiantes (por grupo o de forma individual) — por ejemplo, para generar el sticker de reposición tras una revocación (RF-QR-03) — sin necesidad de reexportar el lote completo.

---

### 3.3 Autenticación, Usuarios y Control de Acceso (RBAC) — *(OE-03 · Hito 02)*

**RF-AUT-01 — Autenticación basada en JWT** *(expande RF-05)*
El sistema DEBE autenticar usuarios mediante usuario/contraseña y emitir un token de acceso (JWT) de vida corta y un token de renovación (refresh token) de vida más larga, invalidable en caso de cierre de sesión o compromiso de cuenta.
- *Prioridad:* Must. **Trazabilidad:** OE-03 · Hito 02 · KPI-08.

**RF-AUT-02 — Control de acceso basado en roles (RBAC)** *(expande RF-05)*
El sistema DEBE restringir cada función y cada dato mostrado según el rol del usuario autenticado (Administrador/Directivo, Prefecto, Docente, Personal administrativo, Solo lectura), de forma que ningún usuario pueda acceder a información o acciones fuera de su rol, ni siquiera manipulando directamente la URL o la API. Los permisos de cada rol son los de la matriz RN-AUT-06.
- *Criterios de aceptación:* 100% de los roles definidos con permisos funcionales verificados mediante pruebas de autorización negativa (KPI-08).
- *Prioridad:* Must. **Trazabilidad:** OE-03 · Hito 02 · KPI-08.

**RF-AUT-03 — Gestión del ciclo de vida de cuentas**
El sistema DEBE permitir a Administrador dar de alta, desactivar y reasignar el rol de una cuenta de usuario, y DEBE bloquear temporalmente una cuenta tras un número configurable de intentos fallidos consecutivos (5 por defecto) durante un periodo configurable (15 minutos por defecto), con desbloqueo manual anticipado por Administrador. Una cuenta con rol Docente DEBE poder vincularse a la ficha de un docente (RF-AST-11, RN-AST-30).
- *Prioridad:* Must. **Trazabilidad:** OE-03 · Hito 02.

**RF-AUT-04 — Recuperación segura de contraseña**
El sistema DEBE proveer un mecanismo de restablecimiento de contraseña mediante enlace de un solo uso enviado al correo institucional registrado, con expiración configurable.
- *Prioridad:* Should. **Trazabilidad:** OE-03 · Hito 02.

**RF-AUT-05 — Bitácora de auditoría de accesos y acciones críticas**
El sistema DEBE registrar usuario, fecha/hora, acción y resultado para inicios de sesión, cambios de rol, registros y modificaciones de asistencia estudiantil y docente, modificaciones de reportes y cambios de estatus de estudiante y de docente, altas y ediciones de fichas de docentes y correcciones de identificador, de forma consultable por el rol Administrador.
- *Prioridad:* Must. **Trazabilidad:** OE-03, 	OE-07 (Calidad, seguridad y continuidad) · Hito 02 · KPI-64.

---

### 3.4 Control de Asistencia — *(OE-04 · Hito 03)*

**RF-AST-01 — Registro de asistencia por escaneo QR**
El sistema DEBE generar un registro de asistencia al validar el código QR de un estudiante, asociándolo a fecha, hora, grupo y jornada/periodo escolar correspondiente.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03 · KPI-13, KPI-15, KPI-18.

**RF-AST-02 (líneas 169–172):**
El motor de asistencia DEBE ignorar y notificar (sin generar un segundo registro) escaneos del mismo estudiante que ocurran dentro de una ventana de prevención de rebote contada desde el último escaneo procesado, con valor por defecto de 5 minutos, configurable entre 1 y 30 minutos (RN-AST-02, RN-AST-03, RN-ADM-02).
 - *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03 · KPI-16.
 
**RF-AST-03 (líneas 173–183):**
El sistema DEBE determinar automáticamente el estado de asistencia de los estudiantes conforme a la hora efectiva del primer registro válido de entrada (RN-TRX-04) y a los parámetros configurados por la institución.
> - Un registro válido a más tardar a la hora de corte produce `ASISTIÓ`; uno posterior produce `LLEGÓ TARDE`.
> - Los escaneos posteriores con estado ya determinado se conservan como eventos adicionales sin cambiar el estado (RN-AST-07).
> - Un estudiante sin registro válido permanece sin estado definitivo antes de la hora de verificación de ausencias y se marca `FALTÓ` (origen `AUTOMÁTICO`) una vez transcurrida.
> - Un estudiante con `FALTÓ` automático que escanea después se reclasifica según su hora efectiva (RN-AST-09), sin crear un segundo registro de entrada; un estado modificado manualmente no se reclasifica.
> - `FALTA JUSTIFICADA` solo se obtiene al justificar un `FALTÓ` (RN-AST-22).
> - La hora de corte y la hora de verificación DEBEN ser configurables por jornada, y la de verificación DEBE ser posterior a la de corte (RN-ADM-02).
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03..

**RF-AST-04 — Historial diario de asistencia por grupo**
El sistema DEBE permitir consultar, para una fecha y grupo dados, la relación completa de estudiantes y su estado de asistencia correspondiente.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 07 · KPI-59.

**RF-AST-05 — Historial individual de asistencia**
El sistema DEBE permitir consultar el historial acumulado de asistencia de un estudiante específico a lo largo del ciclo escolar.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 07 · KPI-62.

**RF-AST-06 — Justificación y modificación de faltas con trazabilidad**
El sistema DEBE permitir a personal autorizado justificar o modificar registros de asistencia estudiantil y docente, exigiendo un motivo y conservando un registro inmutable de quién realizó el cambio, cuándo se realizó, cuál era el estado anterior y cuál es el nuevo estado. El resultado de justificar una falta es el estado FALTA JUSTIFICADA (RN-AST-22), tanto para estudiantes como para docentes.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 07 · KPI-63, KPI-64..

**RF-AST-07 — Información consolidada de apoyo a evaluación académica**
El sistema DEBE generar información agregada de asistencia (por estudiante, grupo y periodo) exportable o consultable, para ser usada por los docentes conforme a las reglas de evaluación que defina la institución (la fórmula de ponderación queda fuera de este documento). El rol Docente no consulta asistencia directamente; el Personal administrativo o Administrador le entrega la información exportada.
- *Prioridad:* Should. **Trazabilidad:** OE-04 · Hito 07.

**RF-AST-08 — Registro de asistencia del personal docente**
El sistema DEBE permitir al Personal administrativo registrar la asistencia del personal docente mediante el escaneo del código QR individual asociado al docente.
El flujo DEBE permitir:
1. Escanear el código QR del docente.
2. Validar e identificar al docente.
3. Seleccionar manualmente si el registro corresponde a `ENTRADA` o `SALIDA`.
4. Registrar la fecha y hora del evento.
5. Impedir más de un registro de `ENTRADA` y más de un registro de `SALIDA` para el mismo docente en la misma fecha.
6. Determinar el estado de la `ENTRADA` conforme al horario esperado del docente para ese día.
7. Permitir consultar el historial de entradas y salidas del docente.
8. Permitir identificar ausencias únicamente cuando el docente tenga asistencia programada para ese día y no exista una entrada válida después de la hora de verificación correspondiente.
9. Mantener trazabilidad de cualquier modificación o justificación posterior.
10. Permitir registrar una `SALIDA` sin `ENTRADA` previa, marcándola como anomalía visible para revisión (RN-AST-25), y reclasificar un `FALTÓ` automático cuando el docente registra después una `ENTRADA` válida ese día (RN-AST-24).

Los docentes no requieren una cuenta de usuario de SIGE para que el Personal administrativo registre su asistencia.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03 · KPI-73, KPI-74.

**RF-AST-09 — Configuración de jornada y asistencia programada del personal docente**
El sistema DEBE permitir al Personal administrativo autorizado registrar y mantener la programación de cada docente: días de asistencia programada, hora esperada de entrada, hora esperada de salida y tolerancia de puntualidad (si no se define, se usa la tolerancia institucional configurable por el Administrador). Docentes distintos PUEDEN tener días, horarios y tolerancias distintos. El sistema DEBE usar esta programación para decidir si corresponde evaluar la asistencia en una fecha y calcular la puntualidad (RN-AST-14). Los cambios DEBEN conservar trazabilidad y no alterar retroactivamente lo ya determinado.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03 · KPI-73.

**RF-AST-10 — Persistencia y consulta histórica de la asistencia docente**
El sistema DEBE conservar de forma permanente en la base de datos todo registro de asistencia del personal docente (`ENTRADA`, `SALIDA` y su estado derivado), sin eliminación física, y DEBE permitir su consulta histórica por docente y periodo, de forma equivalente al historial de asistencia estudiantil (RF-AST-04, RF-AST-05).
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03/07 · KPI-73, KPI-74 · RN-AST-21

**RF-AST-11 — Expediente y mantenimiento del personal docente**
El sistema DEBE mantener una ficha (expediente) por docente, independiente de las cuentas de usuario, con:
- **Datos mínimos (obligatorios):** nombre completo, identificador interno (clave institucional, única e inmutable, RN-AST-26) y estatus (`ACTIVO` / `INACTIVO`).
- **Datos opcionales:** fotografía, correo electrónico y teléfono (RN-AST-27). No se recolectan otros datos personales.
El sistema DEBE permitir al Personal administrativo y al Administrador registrar y editar la ficha y desactivar al docente con motivo; DEBE permitir **solo al Administrador** reactivarlo con motivo (RN-AST-28). Un docente nunca se elimina y su historial se conserva. Al desactivarlo aplican los efectos de RN-AST-29 (el QR no se revoca, la programación queda suspendida y el historial sigue consultable). El sistema DEBE permitir al Administrador vincular al docente con una cuenta de usuario con rol Docente (RN-AST-30). Todo alta, edición y cambio de estatus DEBE conservar trazabilidad (RN-AUT-05).
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03 · KPI-72 · RN-AST-23, RN-AST-26 a RN-AST-30.

**RF-AST-12 — Consulta y filtrado de docentes**
El sistema DEBE permitir al Personal administrativo y al Administrador buscar y filtrar docentes por nombre, identificador interno y estatus, con resultados paginados, y consultar su ficha con: datos, estatus, estado de su QR (`VIGENTE`, `REVOCADO` o sin QR), programación vigente y acceso a su historial de asistencia (RF-AST-10).
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03 · RN-AUT-06.

### 3.5 Reportes Escolares — *(OE-05/OE-06 · Hito 04/07)*

**RF-REP-01 — Registro de reporte por el docente**
El sistema DEBE permitir al docente registrar un reporte seleccionando tipo (`emocional`, `académico`, `conductual`), nivel de gravedad, una o más opciones predeterminadas según tipo/gravedad (basadas en el reglamento escolar) y una observación adicional de entre 50 y 100 caracteres, con contador de caracteres visible. El docente solo PUEDE registrar reportes de estudiantes ACTIVO de los grupos que tiene asignados; el reporte se envía a los prefectos asignados al grupo del estudiante (RN-REP-09).
- *Prioridad:* Must. **Trazabilidad:** OE-05 (Reportes) · Hito 04/07 · KPI-45 a KPI-48.

**RF-REP-02 — Flujo de canalización del reporte**
El sistema DEBE encaminar cada reporte por el flujo `Registrado por docente → Revisado por prefecto → Canalizado → Revisado por administrativo → Comunicado a familia (o Resuelto sin comunicación)`, permitiendo a cada rol únicamente las acciones que le correspondan (consultar, filtrar, canalizar, autorizar comunicación), sin importar si la etapa se ejecutó desde la app móvil o la plataforma web. El rechazo del prefecto deja el reporte RECHAZADO y exige un reporte nuevo referenciado; el rechazo administrativo regresa el reporte a la revisión del prefecto (RN-REP-03, RN-REP-08).
- *Prioridad:* Must. **Trazabilidad:** OE-05 (Reportes) · Hito 07 · KPI-49 a KPI-52.

**RF-REP-03 — Bandeja y filtrado por rol**
El sistema DEBE proveer, para prefectos y personal administrativo, una bandeja de reportes filtrable por tipo, gravedad, grupo, estudiante y estado.
- *Prioridad:* Must. **Trazabilidad:** OE-05 (Reportes) · Hito 04.

**RF-REP-04 — Trazabilidad completa del reporte**
El sistema DEBE conservar el historial de estados de cada reporte (registrado, revisado por prefecto, canalizado, rechazado, revisado por administrativo, autorizado, comunicado, resuelto) con usuario, fecha/hora y motivo cuando aplique (RN-REP-07).
- *Prioridad:* Must. **Trazabilidad:** OE-05 (Reportes) · Hito 07 · KPI-53.

**RF-REP-05 — Paridad funcional en aplicación móvil**
El sistema DEBE permitir a docentes registrar reportes y a prefectos consultarlos/canalizarlos desde la aplicación móvil, con las mismas reglas de negocio, permisos y datos que la plataforma web.
- *Prioridad:* Must. **Trazabilidad:** 	OE-10 (App móvil) · Hito 04 · KPI-22, KPI-23.

---

### 3.6 Comunicación con Familiares — *(OE-07 · Hito 07)*

**RF-COM-01 — Envío automatizado de comunicaciones por correo**
El sistema DEBE permitir preparar y enviar por correo electrónico la información y los reportes previamente autorizados, utilizando los datos de contacto del expediente del estudiante.
- *Prioridad:* Should. **Trazabilidad:** OE-06 (Comunicación) · Hito 07.

**RF-COM-02 — Registro de estado de envío**
El sistema DEBE registrar, cuando sea técnicamente posible, el estado de cada envío (enviado, fallido, pendiente), sin garantizar confirmación de lectura por parte del tutor.
- *Prioridad:* Should. **Trazabilidad:** OE-06 (Comunicación) · Hito 07 · Riesgo R-02.

**RF-COM-03 — Consentimiento y minimización de datos en el envío**
El sistema DEBE limitar la información enviada a terceros (proveedor de mensajería/correo) a la estrictamente necesaria para la comunicación autorizada, sin exponer el expediente completo del estudiante. El sistema NO DEBE enviar comunicaciones a un tutor con consentimiento REVOCADO (RN-COM-04) y DEBE usar únicamente contactos válidos (RN-EST-11).
- *Prioridad:* Must (regulatorio). **Trazabilidad:** OE-06 (Comunicación), protección de datos de menores.

---

### 3.7 Panel Administrativo — *(OE-09 (Panel administrativo) · Hito 02)*

**RF-ADM-01 — Administración centralizada**
El sistema DEBE proveer una interfaz única para que el rol Administrador gestione usuarios, estudiantes, docentes, catálogos (grupos, grados, ciclos, tipos y niveles de gravedad de reporte), las asignaciones prefecto–grupo y docente–grupo, y módulos habilitados.
- *Prioridad:* Must. **Trazabilidad:** 	OE-09 (Panel administrativo) · Hito 02.

**RF-ADM-02 — Configuración de parámetros operativos**
El sistema DEBE permitir configurar, de forma independiente para estudiantes y docentes, la ventana de prevención de rebote (1–30 min, 5 por defecto), la hora de corte por grupo y jornada, las horas de verificación de ausencias (10:00 inicial para estudiantes) —siempre posteriores a la hora de corte—, la tolerancia institucional de puntualidad docente (0 min inicial), el número y duración de bloqueo de cuentas (5 intentos / 15 min) y las opciones predeterminadas del reglamento por tipo/gravedad de reporte. Todo cambio DEBE auditarse y no ser retroactivo (RN-ADM-02).
- *Prioridad:* Should. **Trazabilidad:** 	OE-09 (Panel administrativo) · Hito 02/07.

**RF-ADM-03 — Panel de indicadores (KPIs)**
El sistema DEBERÍA mostrar al Administrador y al rol Solo Lectura un tablero con los indicadores operativos clave (asistencia del día, reportes abiertos, credenciales pendientes), como apoyo a la toma de decisiones.
- *Prioridad:* Could. **Trazabilidad:** 	OE-09 (Panel administrativo).

---

### 3.8 Backend, API y Base de Datos — *(	OE-08 (Backend, BD y API) · Hito 01/03)*

**RF-API-01 — API documentada como fuente única de verdad**
El sistema DEBE exponer una API REST documentada (OpenAPI/Swagger) que sea consumida de forma exclusiva tanto por la plataforma web como por la aplicación móvil, evitando lógica de negocio duplicada entre clientes.
- *Prioridad:* Must. **Trazabilidad:** 	OE-08 (Backend, BD y API), 	OE-12 (Integración multiplataforma) · Hito 03.

**RF-API-02 — Validación de datos del lado del servidor**
El sistema DEBE validar toda entrada de datos en el backend independientemente de la validación realizada en el cliente (web o móvil).
- *Prioridad:* Must. **Trazabilidad:** 	OE-07 (Calidad, seguridad y continuidad), 	OE-08 (Backend, BD y API).

**RF-API-03 — Respaldo periódico de la base de datos**
El sistema DEBE ejecutar respaldos automáticos de la base de datos con una periodicidad definida (mínimo diaria) y DEBE permitir restaurar un respaldo en un procedimiento documentado y probado.
- *Prioridad:* Must. **Trazabilidad:** 	OE-07 (Calidad, seguridad y continuidad), 	OE-11 (Servidor local) · Hito 05 · KPI-32.

**RF-API-04 — Manejo estructurado de errores**
El sistema DEBE devolver errores en un formato consistente (código, mensaje, referencia de trazabilidad) tanto a la plataforma web como a la aplicación móvil.
- *Prioridad:* Should. **Trazabilidad:** 	OE-07 (Calidad, seguridad y continuidad), 	OE-08 (Backend, BD y API).

---

### 3.9 Aplicación Móvil — *(OE-11 · Hito 04)*

**RF-MOV-01 — Escaneo y validación de QR desde el dispositivo móvil**
La aplicación móvil DEBE permitir escanear el QR de un estudiante y, con conexión al servidor local, validarlo contra el backend en tiempo real. Sin conexión, DEBE almacenar únicamente el evento de captura (fecha, hora de captura, tipo de evento e identificador QR leído) conforme a RNF-FIA-01 y RN-MOV-02, marcarlo como pendiente de validación y no considerarlo registro definitivo; la existencia del token, su vigencia, el estatus del estudiante, la unicidad y el rebote se validan en el backend al sincronizar.
- *Prioridad:* Must. **Trazabilidad:** OE-10 · Hito 04 · KPI-19, KPI-26.

**RF-MOV-02 — Registro y consulta de asistencia y reportes desde móvil**
La aplicación móvil DEBE permitir a los roles correspondientes registrar asistencia, registrar reportes y consultar su estado, utilizando la misma API, autenticación y reglas de negocio que la plataforma web (sin base de datos independiente).
- *Prioridad:* Must. **Trazabilidad:** 	OE-10 (App móvil), OE-12 (Integración multiplataforma) · Hito 04 · KPI-21, KPI-24, KPI-25.

**RF-MOV-03 — Operación dentro de la red institucional**
La aplicación móvil DEBE poder comunicarse con el servidor local a través de la red Wi-Fi institucional para las funciones internas, sin requerir conexión a Internet.
- *Prioridad:* Must. **Trazabilidad:** 	OE-10 (App móvil), 	OE-11 (Servidor local) · Hito 05 · KPI-30.
	
---

### 3.10 Infraestructura y Servidor Local — *(	OE-11 (Servidor local) OE-13 · Hito 05)*

**RF-INF-01 — Despliegue en servidor local institucional**
El sistema DEBE poder desplegarse en una computadora proporcionada por la institución, conectada a la red local, alojando backend, API y base de datos.
- *Prioridad:* Must. **Trazabilidad:** 	OE-11 (Servidor local) · Hito 05 · KPI-28.

**RF-INF-02 — Separación de funciones internas y dependientes de Internet**
El diseño DEBE identificar y separar explícitamente qué funcionalidades operan exclusivamente dentro de la red local (asistencia, reportes, consultas) de aquellas que requieren Internet (envío de correo, acceso remoto).
- *Prioridad:* Must. **Trazabilidad:** 	OE-11 (Servidor local) · Hito 05 · KPI-31.

**RF-INF-03 — Procedimiento de recuperación ante interrupción**
El sistema DEBE contar con un procedimiento documentado y probado de recuperación del servidor local y restauración de respaldo ante una interrupción del servicio.
- *Prioridad:* Must. **Trazabilidad:** 	OE-07 (Calidad, seguridad y continuidad), 	OE-11 (Servidor local) · Hito 05/06 · KPI-32, KPI-44.

---

## 4. Requisitos No Funcionales (RNF)
*(Clasificados según ISO/IEC/IEEE 25010)*

### 4.1 Eficiencia de desempeño

**RNF-DES-01 — Tiempo de respuesta en punto de acceso** *(= RNF-01 original)*
La validación y confirmación visual/auditiva de un código QR DEBE resolverse en menos de 250 ms bajo condiciones normales de red local.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03/06.

**RNF-DES-02 — Capacidad de escaneo en hora pico**
El sistema DEBE soportar, sin degradación perceptible del tiempo de respuesta (RNF-DES-01), al menos [N] escaneos por minuto durante la entrada/salida de la jornada escolar (valor de N a definir con la institución según matrícula real).
- *Prioridad:* Should. **Trazabilidad:** OE-04 · Hito 06 (pruebas piloto).

### 4.2 Seguridad

**RNF-SEG-01 — Cifrado en tránsito**
Toda comunicación entre clientes (web y móvil) y el servidor DEBE viajar cifrada (HTTPS/TLS), incluso cuando la comunicación ocurra dentro de la red local institucional.
- *Prioridad:* Must. **Trazabilidad:** 	OE-07 (Calidad, seguridad y continuidad).

**RNF-SEG-02 — Privacidad del payload del QR** *(= RNF-02 original)*
El payload del código QR físico impreso en la credencial NO DEBE incluir datos personales directamente identificables (nombre, matrícula visible en claro, etc.); DEBE tratarse de un identificador opaco resoluble únicamente dentro del sistema.
- *Prioridad:* Must (regulatorio). **Trazabilidad:** LFPDPPP, OE-01.

**RNF-SEG-03 — Política de contraseñas y bloqueo por intentos fallidos**
El sistema DEBE exigir contraseñas con una longitud y complejidad mínimas configurables y DEBE bloquear temporalmente una cuenta tras un número definido de intentos fallidos consecutivos.
- *Prioridad:* Must. **Trazabilidad:** OE-03, 	OE-07 (Calidad, seguridad y continuidad).

**RNF-SEG-04 — Minimización y control de acceso a datos de menores**
El sistema DEBE limitar los campos de datos personales recolectados a los estrictamente necesarios (principio de minimización) y DEBE restringir el acceso a datos de menores exclusivamente al personal autorizado según su rol.
- *Prioridad:* Must (regulatorio). **Trazabilidad:** LFPDPPP, sección "Protección de datos de menores" del acta.

### 4.3 Fiabilidad / Disponibilidad

**RNF-FIA-01 — Tolerancia a desconexión con buffer local** *(= RNF-03 original)*
El módulo de escaneo DEBE almacenar en el dispositivo hasta 1,000 eventos de captura generados durante una pérdida de conectividad y sincronizarlos automáticamente al restablecerse la conexión. Con el buffer lleno, DEBE rechazar nuevos eventos y alertar al operador (RN-MOV-03). Los eventos almacenados se consideran pendientes de validación y DEBEN ser validados por el backend antes de incorporarse como registros definitivos.
- *Prioridad:* Must. **Trazabilidad:** OE-04, OE-11 · Hito 06 · KPI-43.

**RNF-FIA-02 — Disponibilidad durante jornada escolar**
El sistema DEBE mantener disponibilidad del servidor local durante el horario de operación escolar definido por la institución, con un procedimiento de contingencia documentado ante caídas (ver RF-INF-03).
- *Prioridad:* Must. **Trazabilidad:** 	OE-11 (Servidor local) · Riesgo R-09.

**RNF-FIA-03 — Respaldo y recuperación probados**
El procedimiento de respaldo de base de datos DEBE probarse mediante una restauración completa antes de cada hito de cierre, verificando la integridad de los datos recuperados.
- *Prioridad:* Must. **Trazabilidad:** 	OE-07 (Calidad, seguridad y continuidad) · Hito 05/08 · KPI-32, KPI-67.

**RNF-FIA-04 — Sincronización horaria**
El servidor local DEBE mantener su reloj sincronizado y la zona horaria institucional configurada. Cuando no haya Internet para sincronizar, DEBE existir un procedimiento documentado de verificación y ajuste manual de la hora al inicio de cada jornada. La aplicación móvil DEBE registrar la hora de captura de cada evento offline junto con su desfase respecto de la última hora conocida del servidor (RN-TRX-04).
- *Prioridad:* Must. **Trazabilidad:** OE-04, OE-11 · Riesgo R-11.

### 4.4 Usabilidad

**RNF-USA-01 — Diseño visual y ergonomía en punto de acceso** *(= RNF-04 original)*
La interfaz DEBE implementar curvaturas tipo "squircle" (`border-radius: 12–16px`), contraste tipográfico elevado apto para pantallas expuestas a luz solar directa (zona de puerta/entrada), y retroalimentación visual/sonora inmediata ante un escaneo válido o inválido.
- *Prioridad:* Should. **Trazabilidad:** Hito 06 (validación de usabilidad) · KPI-37.

**RNF-USA-02 — Curva de aprendizaje del personal operativo**
Un prefecto, docente o personal administrativo sin capacitación técnica previa DEBERÍA poder completar las tareas críticas de su rol (registrar asistencia estudiantil, registrar asistencia docente cuando corresponda y registrar reportes escolares) con una guía mínima, alcanzando al menos 90% de tareas completadas correctamente en las pruebas de usabilidad.
- *Prioridad:* Should. **Trazabilidad:** Hito 06 · KPI-36.

### 4.5 Compatibilidad

**RNF-COM-01 — Hardware de captura de QR** *(= RNF-05 original)*
El módulo de captura de QR DEBE aceptar lectores USB emuladores de teclado (HID) y cámaras web estándar (UVC), sin requerir instalación de controladores propietarios.
- *Prioridad:* Could. **Trazabilidad:** Hito 03/06 · Riesgo R-13.

**RNF-COM-02 — Dispositivos y navegadores soportados**
El equipo DEBE definir y documentar, antes del Hito 04, el conjunto mínimo de dispositivos móviles (SO y versión) y navegadores web soportados, y validar la aplicación contra una muestra representativa de dicho conjunto.
- *Prioridad:* Must. **Trazabilidad:** 	OE-10 (App móvil) · Hito 04 · KPI-26 · Riesgo R-13.

### 4.6 Mantenibilidad

**RNF-MAN-01 — Control de versiones y documentación técnica**
Todo el código fuente y las decisiones técnicas relevantes DEBEN versionarse en Git/GitHub desde el inicio del proyecto, y DEBE mantenerse documentación técnica mínima de arquitectura y despliegue.
- *Prioridad:* Must. **Trazabilidad:** Principio de desarrollo "Documentación progresiva" · Riesgo R-05.

**RNF-MAN-02 — Separación de responsabilidades Frontend/Backend**
La división de responsabilidades entre Next.js (frontend) y Django (backend/API) DEBE mantenerse documentada y consistente a lo largo del proyecto, evitando lógica de negocio duplicada en el frontend.
- *Prioridad:* Must. **Trazabilidad:** Riesgo R-07.

### 4.7 Portabilidad

**RNF-POR-01 — Reproducibilidad del entorno de servidor local**
El procedimiento de instalación y configuración del servidor local DEBE quedar documentado de forma que pueda reproducirse en una computadora de reemplazo en caso de falla del equipo original.
- *Prioridad:* Must. **Trazabilidad:** 	OE-11 (Servidor local) · Hito 05 · Riesgo R-14.

---

## 5. Matriz de trazabilidad resumida

| Módulo | Requisitos clave | OE | Hito principal | KPIs asociados |
|---|---|---|---|---|
| Estudiantes / Importación | RF-EST-01..05, RF-IMP-01..02 | OE-02 | Hito 02 | KPI-07, KPI-09, KPI-75 |
| QR / Credenciales | RF-QR-01..04 | OE-01 | Hito 01 | KPI-01 a KPI-06, KPI-72 |
| Autenticación / RBAC | RF-AUT-01..05 | OE-03 | Hito 02 | KPI-08 |
| Asistencia | RF-AST-01..12 | OE-04 | Hito 03 / Hito 07 | KPI-13 a KPI-18, KPI-59 a KPI-64, KPI-72 a KPI-74 |
| Reportes | RF-REP-01..05 | OE-05 (Reportes) | Hito 04 / Hito 07 | KPI-22, KPI-23, KPI-45 a KPI-53 |
| Comunicación | RF-COM-01..03 | 	OE-06 (Comunicación) | Hito 07 | — |
| Panel administrativo | RF-ADM-01..03 | 	OE-09 (Panel administrativo) | Hito 02 | KPI-07, KPI-08 |
| Backend/API/BD | RF-API-01..04 | 		OE-07 (Calidad, seguridad y continuidad) (Backend, BD y API) | Hito 01 / Hito 03 | KPI-28 a KPI-30 |
| App móvil | RF-MOV-01..03 | 	OE-10 (App móvil) | Hito 04 | KPI-19 a KPI-27 |
| Infraestructura local | RF-INF-01..03 | 	OE-11 (Servidor local) 	OE-12 (Integración multiplataforma) | Hito 05 | KPI-28 a KPI-34, KPI-43, KPI-44 |
| RNF transversales | RNF-DES, RNF-SEG, RNF-FIA, RNF-USA, RNF-COM, RNF-MAN, RNF-POR | 	OE-06 (Comunicación) (Calidad, seguridad y continuidad) | Todos | Ver secciones 4.1–4.7 |

---

## 6. Resumen de priorización MoSCoW (fase Hito 01–02)

**Must (bloquean el cierre de Hito 01/02):**
RF-EST-01, RF-EST-03, RF-EST-04, RF-IMP-01, RF-QR-01, RF-QR-02, RF-CRE-01, RF-AUT-01, RF-AUT-02, RF-AUT-03, RF-AUT-05, RF-ADM-01, RNF-SEG-01, RNF-SEG-02, RNF-SEG-03, RNF-SEG-04,RF-QR-04, RF-AST-11, RF-AST-12.

**Should (deseables en Hito 01/02, exigibles a más tardar en Hito 03/04):**
RF-EST-02, RF-IMP-02, RF-QR-03, RF-CRE-02, RF-AUT-04, RF-ADM-02.

**Could (valor agregado, no comprometido en el alcance base):**
RF-ADM-03,RNF-COM-01.

---

## 7. Glosario breve

- **RBAC:** Role-Based Access Control, control de acceso basado en roles.
- **JWT:** JSON Web Token, formato de token de autenticación.
- **CR-80:** estándar de medida de tarjeta/credencial (85.6 × 54 mm).
- **HID / UVC:** estándares de hardware "plug and play" para teclados/lectores (HID) y cámaras (UVC).
- **LFPDPPP:** Ley Federal de Protección de Datos Personales en Posesión de los Particulares.

---

## 8. Próximo paso sugerido

Conforme a la sección 15 del acta, este documento es la base directa para redactar las **Historias de Usuario** y los **Criterios de Aceptación Específicos** de cada requisito (formato Given/When/Then), priorizando primero los requisitos Must de Hito 01–02. Si quieres, puedo continuar con ese documento a partir de esta matriz.
