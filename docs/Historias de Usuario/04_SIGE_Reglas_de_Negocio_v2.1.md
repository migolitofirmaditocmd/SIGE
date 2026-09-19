# Catálogo de Reglas de Negocio — SIGE
### Sistema Integral de Gestión Escolar
**Documento derivado del Acta Constitutiva v9 y de la Especificación de Requisitos v2**
**Versión:** 2.0 | **Estado:** Para revisión del equipo

---

## 1. Introducción

### 1.1 Propósito
Mientras que el documento de Requisitos Funcionales (RF) y No Funcionales (RNF) describe **qué debe hacer el sistema**, este catálogo describe **las reglas que gobiernan el comportamiento del negocio**, independientemente de cómo se implementen. Una regla de negocio es una afirmación que define o restringe algún aspecto del negocio, y que debe cumplirse sin importar qué módulo, pantalla o API la ejecute. Separarlas de los RF permite:

- Detectar reglas duplicadas o contradictorias entre módulos.
- Facilitar que las reglas se implementen en un solo lugar (backend) y no se dupliquen entre plataforma web y app móvil — requisito explícito del acta (OE-13, RF-API-01).
- Servir de base directa para casos de prueba y para las Historias de Usuario (siguiente documento del plan, sección 15 del acta).

### 1.2 Estándares y marco de referencia utilizados
- **OMG SBVR** (*Semantics of Business Vocabulary and Rules*) — vocabulario y estructura término/hecho/regla.
- **Business Rules Manifesto** (Business Rules Group) — principio de que las reglas son un activo de primer nivel, independiente de los procesos y de la tecnología que las ejecuta.
- **Clasificación de Ronald G. Ross / Barbara von Halle** — tipología de reglas usada en este documento (ver 1.3).
- **IEEE 29148:2018** — atomicidad, verificabilidad y trazabilidad, aplicadas aquí a nivel de regla.

### 1.3 Tipología de reglas utilizada

| Tipo | Sigla | Definición | Ejemplo genérico |
|---|---|---|---|
| **Hecho / Definición estructural** | `DEF` | Establece un término, una relación o una estructura de datos válida. | "Un estudiante tiene exactamente un estatus." |
| **Restricción (Constraint)** | `RES` | Prohíbe o exige una condición; su violación **impide** que la operación se complete. | "La matrícula debe ser única." |
| **Habilitador de acción (Action Enabler)** | `HAB` | Si se cumple una condición, el sistema **debe disparar** una acción o notificación. | "Si el reporte es de gravedad alta, se notifica de inmediato al prefecto." |
| **Cómputo** | `CMP` | Define cómo se calcula o deriva un valor. | "El estado de asistencia se calcula según la hora de escaneo vs. la hora de corte." |
| **Inferencia** | `INF` | Deriva conocimiento nuevo a partir de hechos existentes, sin ser un cálculo aritmético directo. | "Un estudiante en estatus BAJA se considera inactivo para todo registro nuevo." |

### 1.4 Convenciones
- ID: `RN-<MÓDULO>-<NÚM>`, usando los mismos prefijos de módulo del documento de RF (EST, IMP, QR, CRE, AUT, AST, REP, COM, ADM, API, MOV, INF) más `TRX` para reglas transversales.
- Cada regla indica: enunciado, tipo, condición/disparador, consecuencia, excepciones conocidas, y trazabilidad al RF y al OE/Hito de origen.
- Toda regla es **atómica**: si una oración tiene dos condiciones independientes, se separa en dos reglas.
- Toda regla DEBE poder convertirse en al menos un caso de prueba binario (cumple / no cumple).

---

## 2. Reglas de negocio por módulo

### 2.1 Estudiantes (EST)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-EST-01 | DEF | Un estudiante tiene exactamente un estatus: `ACTIVO`, `BAJA` o `EGRESADO`. | — | — | — | RF-EST-01,RF-EST-02, OE-02 |
| RN-EST-02 | RES | La matrícula de un estudiante es única e inmutable una vez asignada | Alta o edición de estudiante | Se rechaza la operación si la matrícula ya existe o si se intenta modificar la de un registro existente. | Corrección manual administrativa excepcional, solo por personal administrativo o administrador, con registro en bitácora. | RF-EST-01 |
| RN-EST-03 | RES | Un estudiante DEBE tener al menos un tutor/familiar asociado con contacto válido (RN-EST-11) para poder guardarse en el sistema, sea como registro completo o incompleto. | Alta o edición de estudiante; intento de eliminar o invalidar el único tutor válido de un estudiante `ACTIVO` | Se rechaza el guardado; no se persiste ningún dato del registro. | — | RF-EST-03, RF-EST-01 |
| RN-EST-04 | HAB | Si un estudiante cambia a estatus `BAJA` o `EGRESADO`, el sistema conserva su expediente e historial, pero deja de aparecer en las operaciones activas del día (asistencia, reportes nuevos, verificación de ausencias). | Cambio de estatus | Archivado lógico, no eliminación física. Sus QR vigentes **no se revocan automáticamente**: los escaneos se rechazan por RN-EST-05. | Consulta histórica por rol autorizado. | RF-EST-02, RN-TRX-03 |
| RN-EST-05 | RES | Solo un estudiante en estatus `ACTIVO` puede ser objeto de nuevos registros de asistencia o reportes escolares. | Intento de registrar asistencia o reporte asociado al estudiante | Se rechaza el registro si el estudiante no está `ACTIVO`. | — | RF-EST-02, RF-AST-01, RF-REP-01 |
| RN-EST-06 | INF | Un cambio de `BAJA` a `ACTIVO` (reingreso) requiere autorización explícita del Administrador y queda registrado como evento distinto del alta original. | Reactivación de estudiante | Se genera un registro de auditoría diferenciado. El QR vigente previo se conserva (salvo que se haya revocado por RN-QR-03) y el estudiante debe conservar al menos un tutor con contacto válido (RN-EST-03). | No aplica a `EGRESADO` (RN-EST-09). | RF-EST-02, RF-AUT-05, RN-QR-03 |
| RN-EST-07 | DEF | El consentimiento del tutor para el tratamiento de los datos del menor se registra **por tutor** con un estatus (`PENDIENTE`, `OTORGADO`, `REVOCADO`) y su fecha de registro. SIGE NO DEBE exigir que el consentimiento se capture dentro del sistema (puede documentarse por el medio que defina la institución, p. ej. formato físico), pero SÍ DEBE existir un campo consultable con el estatus vigente. | Alta de tutor o cambio de consentimiento | Se conserva el estatus vigente y el historial de cambios con fecha. Al crear un tutor, su estatus de consentimiento inicia en PENDIENTE; ningún tutor puede quedar sin estatus. | — | RF-EST-05, LFPDPPP |
| RN-EST-08 | HAB | Si algún tutor de un estudiante tiene consentimiento `PENDIENTE` o `REVOCADO`, SIGE advierte al personal autorizado al consultar el expediente. | Consulta del expediente | Advertencia visible; no bloquea la consulta ni la operación escolar (salvo RN-COM-04). | — | RF-EST-05, RN-EST-07 |
| RN-EST-09 | RES | `EGRESADO` es un estatus final: no admite transiciones (ni a `ACTIVO` ni a `BAJA`). | Intento de cambiar el estatus de un estudiante `EGRESADO` | Se rechaza el cambio. | Corrección de un egreso erróneo solo por el Administrador, con motivo y registro en bitácora. | RF-EST-02, RN-AUT-05 |
| RN-EST-10 | DEF | Un registro de estudiante es **INCOMPLETO** cuando cuenta con todos los datos mínimos (nombre completo, matrícula, grado, grupo, ciclo escolar y un tutor con contacto válido) pero carece de uno o más datos obligatorios diferidos (fecha de nacimiento, fotografía). Un registro incompleto conserva el estatus `ACTIVO`, puede recibir asistencia y reportes, muestra los campos faltantes y no genera credencial (RN-CRE-01) hasta completarse. | Guardado de un registro sin algún dato obligatorio diferido | Se guarda con la marca INCOMPLETO y la lista de campos faltantes. Si falta cualquier dato mínimo, no se guarda nada. | `domicilio`, `sexo` y `CURP` son opcionales (RF-EST-01) y su ausencia no genera la marca. | RF-EST-01, RN-EST-03, RN-EST-05, RN-TRX-01 |
| RN-EST-11 | DEF | Un tutor tiene **contacto válido** cuando cuenta con nombre, relación y un correo electrónico con formato válido, y no está marcado como inválido. SIGE lo marca como válido automáticamente al validar el formato; el Personal administrativo o Administrador puede marcarlo como inválido con motivo (p. ej. correo devuelto de forma reiterada). | Alta o edición de un tutor | Se asigna el indicador de contacto válido/inválido. | Mientras el canal de comunicación sea solo correo, el teléfono no interviene en la validez. | RF-EST-03, RN-EST-03, RN-COM-01 |

### 2.2 Importación masiva (IMP)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-IMP-01 | RES | Un archivo de importación solo se procesa si cumple exactamente el diccionario de datos vigente (columnas, tipos y formato). | Carga de archivo | Se rechaza el archivo completo antes de intentar procesar filas si la estructura no corresponde. | — | RF-IMP-01, OE-02 |
| RN-IMP-02 | CMP | Cada fila del archivo se procesa de forma independiente: una fila inválida no afecta el procesamiento de las demás filas válidas. | Procesamiento del archivo | Inserción parcial + reporte de errores por fila. | — | RF-IMP-01 |
| RN-IMP-03 | RES | Una fila cuya matrícula ya exista en el sistema se rechaza y se reporta como duplicada; nunca sobrescribe el registro existente. | Procesamiento de fila | Registro en el reporte de errores. | — | RF-IMP-01, RN-EST-02 |
| RN-IMP-04 | HAB | Toda importación DEBE ejecutarse primero en modo de vista previa (*dry-run*): las filas se validan y se preparan (incluida su asignación a grupo y ciclo) **sin persistir datos**; la vista previa muestra los registros a insertar y los rechazados. | Inicio de importación | Solo la confirmación explícita del usuario persiste los registros válidos. Si el usuario cancela o no confirma, no se persiste nada y la importación termina. | — | RF-IMP-01 |
| RN-IMP-05 | RES | Solo el Administrador y el Personal administrativo pueden ejecutar importaciones, descargar la plantilla y descargar el reporte de importación. | Cualquier operación del módulo de importación | Rechazo a nivel de API para otros roles. | — | RF-IMP-01, RF-IMP-02, RN-AUT-06 |
| RN-IMP-06 | RES | Cada fila DEBE traer los datos mínimos de RN-EST-10 (incluido un tutor con contacto válido). Los datos obligatorios diferidos pueden venir vacíos: en ese caso la fila crea un registro INCOMPLETO. | Procesamiento de fila | Fila sin datos mínimos: se descarta y se reporta; fila con faltantes diferidos: se inserta como INCOMPLETO. | Las columnas siempre deben existir en el archivo (RN-IMP-01); lo que puede estar vacío es el valor. | RF-IMP-01, RN-EST-03, RN-EST-10 |
| RN-IMP-07 | RES | Si al confirmar la importación la matrícula de una fila ya fue creada por otro proceso desde que se generó la vista previa, **solo esa fila** se rechaza y se reporta como duplicada; nunca sobrescribe y no detiene el resto de la importación. | Confirmación de importación | Fila rechazada + registro en el reporte de errores. | — | RF-IMP-01, RN-IMP-03, RN-EST-02 |

### 2.3 Identificación QR y Credenciales (QR / CRE)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-QR-01 | RES | Un estudiante tiene, en todo momento, cuando mucho un identificador QR **vigente**. | Generación de QR | Se rechaza generar un segundo QR vigente para el mismo estudiante sin revocar el anterior. | — | RF-QR-01, RF-QR-03 |
| RN-QR-02 | RES | El identificador QR no debe contener, en su payload, datos personales directamente legibles del estudiante. | Generación de QR | El valor codificado es un identificador opaco (token) sin nombre, matrícula visible ni CURP. | — | RF-QR-01, RNF-SEG-02, LFPDPPP |
| RN-QR-03 | DEF | Un identificador QR revocado nunca vuelve a estar vigente ni se reutiliza para otro estudiante. | Revocación | El histórico conserva la referencia al identificador revocado y a su reemplazo. | — | RF-QR-03 |
| RN-QR-04 | HAB | Si un identificador QR se revoca, todo escaneo posterior con ese identificador se rechaza automáticamente, aunque el estudiante siga `ACTIVO`. | Escaneo con QR revocado | Rechazo + alerta al operador para verificar identidad manualmente. | — | RF-QR-03, RF-AST-01 |
| RN-QR-05 | DEF | Cada persona que requiera identificación mediante QR dentro de SIGE debe contar con como máximo un QR vigente asociado a su identidad y tipo de registro. | Generación de un QR | El sistema impide mantener simultáneamente más de un QR vigente para la misma persona y tipo. | Estudiantes y personal docente utilizan identificadores QR independientes. | RF-QR-01, RF-QR-04, RF-AST-01, RF-AST-08 |
| RN-QR-06 | RES | El QR de un docente sigue las mismas reglas de token que el de un estudiante (RN-QR-02, RN-QR-03, RN-QR-04); su revocación y regeneración solo puede hacerla el Administrador. | Generación, revocación o escaneo de un QR docente | Se aplican las reglas del ciclo QR con identificadores independientes de los de estudiantes. | — | RF-QR-04, RN-QR-05, RN-AST-11 |
| RN-CRE-01 | RES | Solo se exporta el QR de estudiantes en estatus `ACTIVO` con QR vigente. Para exportar una **credencial completa** se exige además la fotografía cargada; para un **sticker** de QR no se exige. | Solicitud de exportación de credenciales o stickers | Se excluyen de la exportación los estudiantes que no cumplan la condición y se listan aparte como pendientes, con el motivo. | — | RF-CRE-01, RF-CRE-02, RF-EST-01 |

### 2.4 Autenticación y control de acceso (AUT)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-AUT-01 | DEF | Todo usuario del sistema tiene exactamente un rol activo entre: Administrador/Directivo, Prefecto, Docente, Personal administrativo, Solo lectura. | — | — | Un usuario puede tener roles distintos en momentos distintos, pero nunca dos roles simultáneos activos. | RF-AUT-02 |
| RN-AUT-02 | RES | Ninguna acción de escritura (crear, modificar, eliminar) puede ejecutarse desde el rol Solo lectura. | Cualquier operación de escritura | Rechazo a nivel de API, no solo ocultando el botón en la interfaz. | — | RF-AUT-02 |
| RN-AUT-03 | HAB | Tras un número configurable de intentos fallidos consecutivos de inicio de sesión (por defecto 5), la cuenta se bloquea temporalmente durante un periodo configurable (por defecto 15 minutos). | Intento fallido de login | Bloqueo temporal + notificación al usuario del tiempo de espera; durante el bloqueo se rechaza el acceso aunque la contraseña sea correcta. Un inicio de sesión exitoso reinicia el contador. | Desbloqueo manual anticipado por Administrador. | RF-AUT-03, RNF-SEG-03 |
| RN-AUT-04 | RES | Un token de acceso (JWT) vencido no debe permitir ninguna operación, aunque el token de renovación siga vigente. | Solicitud con token vencido | Rechazo 401 + solicitud de renovación. | — | RF-AUT-01 |
| RN-AUT-05 | HAB | Toda acción crítica, incluyendo cambios de rol, modificaciones de asistencia estudiantil o docente, modificaciones de reportes y cambios de estatus de estudiante, genera un registro de auditoría inmutable. | Ejecución de la acción | Registro con usuario, fecha/hora, valor anterior y valor nuevo cuando corresponda. | — | RF-AUT-05 |
| RN-AUT-06 | DEF | Los permisos de cada rol son exactamente los de la matriz siguiente; ningún rol tiene un permiso que no esté listado, y la matriz se aplica en el backend (RN-API-01). | Cualquier solicitud a la API | Se rechaza toda operación fuera de la matriz. | — | RF-AUT-02, RN-AUT-01, RN-AUT-02, RN-TRX-02 |


| Capacidad | ADM | PRE | DOC | PAD | SL |
|---|:-:|:-:|:-:|:-:|:-:|
| Cuentas, roles, desbloqueos, catálogos, asignaciones, parámetros | ✓ | — | — | — | — |
| Bitácora de auditoría · respaldo y restauración | ✓ | — | — | — | — |
| Alta/edición/estatus de estudiantes, tutores y consentimiento | ✓ | — | — | ✓ | — |
| Reingreso de estudiante (RN-EST-06) · revocar/regenerar QR | ✓ | — | — | — | — |
| Importación masiva | ✓ | — | — | ✓ | — |
| Generar QR (estudiantes y docentes) · exportar credenciales | ✓ | — | — | ✓ | — |
| Consultar expedientes | ✓ | ✓ | — | ✓ | — |
| Escanear asistencia estudiantil | — | ✓ | — | ✓ | — |
| Alta y programación de docentes · historial docente | ✓ | — | — | ✓ | — |
| Registrar asistencia docente (RN-AST-10) | — | — | — | ✓ | — |
| Justificar/modificar asistencia | ✓ | — | — | ✓ | — |
| Consultar asistencia detallada (grupo/estudiante) | ✓ | ✓ | — | ✓ | — |
| Información consolidada · indicadores | ✓ | — | — | ✓ (consolidada) | ✓ |
| Registrar reportes | — | — | ✓ | — | — |
| Consultar reportes (RN-REP-05) | ✓ todos | ✓ sus grupos | ✓ propios | ✓ todos | — |
| Revisar y canalizar reportes | — | ✓ | — | — | — |
| Revisión administrativa, autorizar y enviar comunicación | — | — | — | ✓ | — |
 
> Los indicadores del panel (RF-ADM-03) los ve ADM y SL; PAD ve solo la información consolidada de asistencia.

### 2.5 Control de asistencia (AST)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-AST-01 | CMP | El estado de asistencia de un estudiante con al menos un escaneo válido se determina comparando la hora efectiva (RN-TRX-04) del primer escaneo válido de entrada del día contra la hora de corte configurada para su grupo y jornada. | Primer escaneo válido de entrada | Si el escaneo ocurre a más tardar a la hora de corte, el estado es `ASISTIÓ`; si ocurre después de la hora de corte, el estado es `LLEGÓ TARDE`. | — | RF-AST-03 |
| RN-AST-02 | HAB | Si un escaneo válido de un estudiante ocurre dentro de la ventana de prevención de rebote (RN-AST-03), contada desde su **último escaneo procesado** (no desde uno ignorado), el sistema lo ignora, no crea registro ni evento nuevo y notifica "registro duplicado" al operador. | Escaneo dentro de la ventana | Se ignora el segundo escaneo y se notifica al operador. | — | RF-AST-02, RN-AST-03 |
| RN-AST-03 | CMP | Dos escaneos del mismo estudiante se consideran "rebote" si el segundo ocurre dentro de una ventana de tiempo configurable contada desde el último escaneo procesado, con valor por defecto de 5 minutos. | Escaneo dentro de la ventana | Se aplica RN-AST-02. | Configuración institucional entre 1 y 30 minutos (RN-ADM-02). | RF-AST-02 |
| RN-AST-04 | RES | Solo un usuario con rol Administrador o Personal administrativo puede justificar una falta o modificar un estado de asistencia ya registrado. | Intento de modificar asistencia | Rechazo si el rol no está autorizado. | — | RF-AST-06 |
| RN-AST-05 | HAB | Toda justificación o modificación de un registro de asistencia exige capturar un motivo y conserva el valor anterior, el nuevo valor, el usuario y la fecha/hora del cambio. | Modificación de asistencia | Registro inmutable de trazabilidad. | — | RF-AST-06, RN-AUT-05 |
| RN-AST-06 | RES | Un registro de asistencia no puede eliminarse; solo puede modificarse su estado mediante el flujo de justificación (RN-AST-04). | Intento de borrado | Rechazo. | — | RF-AST-06 |
| RN-AST-07 | RES | Un escaneo válido posterior al primero (fuera de la ventana de rebote) de un estudiante que ya tiene estado `ASISTIÓ` o `LLEGÓ TARDE` para la fecha y jornada se conserva como evento adicional y NO modifica el estado ya determinado. | Escaneo válido posterior con estado ya determinado | Se guarda el evento adicional; el estado no cambia. | Si el estado es `FALTÓ` automático se aplica RN-AST-09. | RF-AST-03, RN-AST-01 |
| RN-AST-08 | CMP | Un estudiante con estatus `ACTIVO` se marca como `FALTÓ` únicamente cuando haya transcurrido la hora de verificación de ausencias establecida por la institución y no exista ningún registro válido de asistencia de entrada correspondiente a la fecha y jornada. | Verificación diaria de ausencias | El sistema asigna automáticamente el estado `FALTÓ` a los estudiantes que cumplan ambas condiciones. Antes de dicha hora, la ausencia no se considera definitiva. | La hora de verificación de ausencias es configurable y, para la operación inicial del proyecto, será las 10:00 horas. | RF-AST-03, RF-AST-04 |
| RN-AST-09 | CMP | Un estudiante marcado automáticamente como `FALTÓ` (RN-AST-08) que realiza un escaneo válido de entrada posterior se reclasifica comparando la **hora efectiva** del escaneo (RN-TRX-04) con la hora de corte de su grupo y jornada: a más tardar la hora de corte → `ASISTIÓ`; después → `LLEGÓ TARDE`. | Escaneo válido posterior a la asignación automática de `FALTÓ` | Se conserva la trazabilidad del `FALTÓ` previo, se actualiza el estado sin crear un segundo registro de entrada para la fecha y jornada, y el cambio queda con origen `AUTOMÁTICO` (distinto de una justificación manual, RN-TRX-07). | Un `FALTÓ` justificado manualmente (`FALTA JUSTIFICADA`) o modificado por un usuario NO se reclasifica por escaneo: el estado manual prevalece. Un evento capturado sin conexión antes de la hora de corte y sincronizado después produce `ASISTIÓ` por su hora efectiva. | RF-AST-01, RF-AST-03, RF-AST-06, RN-TRX-04, RN-TRX-07 |

### 2.5.1 Control de asistencia del personal docente

### 2.5.1 Control de asistencia del personal docente

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-AST-10 | RES | Solo el Personal administrativo puede registrar la asistencia del personal docente. | Intento de registrar asistencia docente | Se rechaza la operación cuando el usuario no posee el rol autorizado. | — | RF-AST-08 |
| RN-AST-11 | DEF | Cada docente debe contar con un código QR vigente asociado inequívocamente a su identidad dentro de SIGE. | Escaneo del QR de un docente | El sistema identifica al docente asociado al código QR. | Un QR inválido, revocado o no asociado a un docente debe ser rechazado. | RF-AST-08, RF-QR-04, RN-QR-06 |
| RN-AST-12 | RES | El Personal administrativo debe indicar manualmente si el registro que realizará corresponde a una `ENTRADA` o una `SALIDA`. | Después de identificar al docente | SIGE procesa el registro conforme al tipo seleccionado. | — | RF-AST-08 |
| RN-AST-13 | RES | Un docente puede tener como máximo un registro de `ENTRADA` y un registro de `SALIDA` por fecha. | Intento de registrar un segundo evento del mismo tipo en la misma fecha | El segundo registro del mismo tipo es rechazado y no genera un nuevo registro. | El estado `FALTÓ` asignado automáticamente NO cuenta como registro de `ENTRADA`. | RF-AST-08 |
| RN-AST-14 | CMP | La puntualidad de la `ENTRADA` docente se determina comparando la hora efectiva registrada contra el **límite de entrada** del docente para ese día: hora esperada de entrada + tolerancia de puntualidad. | Registro de `ENTRADA` con asistencia programada | Hora registrada ≤ límite → `ASISTIÓ`; hora registrada > límite → `LLEGÓ TARDE`. | La tolerancia se define por docente en su programación (RF-AST-09); si no se define, se usa la tolerancia institucional (0 minutos inicial, RN-ADM-02). El horario de cada docente puede ser distinto y solo aplica en los días programados. | RF-AST-08, RF-AST-09 |
| RN-AST-15 | DEF | La ausencia docente solo puede determinarse para un docente que tenga asistencia programada para la fecha correspondiente y no cuente con un registro válido de `ENTRADA`. | Verificación de ausencias docentes | El sistema identifica al docente como `FALTÓ` conforme a la hora de verificación configurada para el personal docente. | Los docentes sin asistencia programada para ese día no deben considerarse ausentes. | RF-AST-08, RF-AST-09 |
| RN-AST-16 | RES | Un registro de `SALIDA` debe asociarse a la fecha correspondiente y no puede existir más de uno por docente y fecha. | Intento de registrar salida | El sistema rechaza una segunda salida para la misma fecha. | — | RF-AST-08 |
| RN-AST-17 | RES | La modificación o justificación de la asistencia docente requiere autorización, motivo y trazabilidad inmutable. | Modificación de asistencia docente | Se conserva usuario, fecha/hora, estado anterior, estado nuevo y motivo. | — | RF-AST-06, RF-AUT-05 |
| RN-AST-18 | RES | Un docente solo debe ser evaluado como ausente en una fecha en la que tenga asistencia programada. | Evaluación de asistencia diaria | Si no existe asistencia programada para el docente en esa fecha, el sistema no genera una ausencia. | — | RF-AST-09 |
| RN-AST-19 | CMP | La puntualidad de un docente se determina utilizando el horario de entrada programado específicamente para ese docente y fecha. | Registro de entrada | El sistema compara la hora registrada contra el horario esperado correspondiente. | — | RF-AST-09, RF-AST-08 |
| RN-AST-20 | CMP | La salida docente se registra conforme a la hora efectiva del escaneo y no debe generar un segundo registro de salida para la misma fecha. | Registro de salida | El sistema conserva la hora efectiva de salida. | La existencia de un horario esperado de salida no implica por sí misma que el docente haya salido a esa hora. | RF-AST-08 |
| RN-AST-21 | RES | El registro de asistencia del personal docente (`ENTRADA`, `SALIDA` y su estado derivado) se conserva de forma permanente en la base de datos y no se elimina físicamente. | Intento de borrado de un registro de asistencia docente | Se rechaza el borrado; la corrección solo procede mediante el flujo de justificación (RN-AST-17), aplicando el mismo principio de archivado lógico que rige la asistencia estudiantil. | — | RF-AST-10, RN-AST-06, RN-TRX-03 |
| RN-AST-22 | DEF | Los estados de asistencia (estudiantes y docentes) son `ASISTIÓ`, `LLEGÓ TARDE`, `FALTÓ` y `FALTA JUSTIFICADA`. `FALTA JUSTIFICADA` solo resulta de justificar un registro `FALTÓ` mediante RN-AST-04/05 (estudiantes) o RN-AST-17 (docentes); nunca se asigna automáticamente. Todo estado registra su origen: `ESCANEO`, `AUTOMÁTICO` o `MANUAL`. | Justificación de un registro `FALTÓ` | El estado pasa a `FALTA JUSTIFICADA` con origen `MANUAL` y trazabilidad completa. | — | RF-AST-03, RF-AST-06, RN-TRX-07 |
| RN-AST-23 | DEF | Un docente es una persona registrada en SIGE con datos mínimos (nombre completo, identificador interno, estatus `ACTIVO`/`INACTIVO`), independiente de las cuentas de usuario; no requiere cuenta para que se registre su asistencia. Solo los docentes `ACTIVO` con programación vigente son evaluados y pueden registrar asistencia. | Alta, edición o desactivación de un docente | Un docente `INACTIVO` conserva su historial (archivado lógico) y deja de evaluarse. | — | RF-AST-11, RN-TRX-01, RN-TRX-03 |
| RN-AST-24 | CMP | Un docente marcado `FALTÓ` automáticamente (RN-AST-15) que registra una `ENTRADA` válida ese mismo día se reclasifica con RN-AST-14 (`ASISTIÓ` o `LLEGÓ TARDE`). | Registro de `ENTRADA` de un docente con `FALTÓ` automático | Se conserva la trazabilidad del `FALTÓ` previo, no se cuenta como segunda entrada (RN-AST-13) y el cambio queda con origen `AUTOMÁTICO` (RN-TRX-07). | Un `FALTÓ` justificado manualmente prevalece y no se reclasifica. | RF-AST-08, RN-AST-13, RN-AST-15, RN-TRX-07 |
| RN-AST-25 | RES | Se permite registrar la `SALIDA` de un docente aunque no exista `ENTRADA` ese día, pero el registro queda marcado como "SALIDA SIN ENTRADA" y visible en el historial para su revisión. | Registro de `SALIDA` sin `ENTRADA` en la fecha | Se guarda la salida con la marca de anomalía; su corrección solo procede por RN-AST-17. | — | RF-AST-08, RN-AST-16, RN-AST-17 |

### 2.6 Reportes escolares (REP)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-REP-01 | RES | La observación adicional de un reporte debe tener entre 50 y 100 caracteres inclusive. | Registro del reporte | El sistema no permite guardar fuera de ese rango. | — | RF-REP-01 |
| RN-REP-02 | DEF | Un reporte tiene exactamente un tipo (`emocional`, `académico`, `conductual`) y un nivel de gravedad, ambos asignados al momento del registro y no modificables después de enviarse al prefecto. | Registro / envío del reporte | Cambios posteriores requieren un reporte nuevo referenciado al original. | — | RF-REP-01 |
| RN-REP-03 | RES | Un reporte solo puede avanzar en el orden `Registrado por docente → Revisado por prefecto → Canalizado → Revisado por administrativo → Comunicado a familia` (o `Resuelto` sin comunicación, RN-REP-07); no puede saltarse etapas. Los retrocesos solo ocurren por rechazo explícito con motivo obligatorio. | Cambio de estado del reporte | Rechazo de transiciones no válidas. **Rechazo del prefecto:** el reporte queda `RECHAZADO` (fin del flujo del original; la corrección exige un reporte nuevo, RN-REP-02/08). **Rechazo del Personal administrativo:** el reporte regresa a la revisión del prefecto. | — | RF-REP-02, RF-REP-04 |
| RN-REP-04 | HAB | Un reporte solo puede comunicarse a la familia después de haber sido revisado y autorizado por Personal administrativo; nunca directamente desde el registro del docente o la revisión del prefecto. | Intento de comunicación a familia | Rechazo si no pasó por revisión administrativa. | — | RF-REP-02, OE-05/06 |
| RN-REP-05 | RES | Un docente solo puede consultar el estado de los reportes que él mismo registró; un prefecto consulta los reportes de los grupos que tiene asignados (RN-REP-09); el Personal administrativo y el Administrador ven todos. | Consulta de reportes | Filtrado automático por autor, por grupos asignados o sin filtro según el rol. | — | RF-REP-03, RN-AUT-02, RN-AUT-06 |
| RN-REP-06 | HAB | Cada cambio de etapa de un reporte genera automáticamente una entrada en su historial de trazabilidad, visible según el rol. | Cambio de etapa | Registro de trazabilidad. | — | RF-REP-04 |
| RN-REP-07 | DEF | Además de los estados del flujo existen: `RECHAZADO` (RN-REP-03), `AUTORIZADO` (comunicación autorizada pero sin contacto válido, pendiente) y `RESUELTO`. Un reporte pasa a `RESUELTO` cuando (a) el envío a la familia resultó `ENVIADO`, o (b) el Personal administrativo decide no comunicarlo y registra el motivo. | Cierre del ciclo del reporte | Se registra el estado con usuario, fecha/hora y motivo cuando aplique. | Un reporte `AUTORIZADO` regresa al flujo de comunicación cuando se registra un contacto válido. | RF-REP-04, RN-COM-01, RN-COM-03 |
| RN-REP-08 | HAB | Cuando el prefecto rechaza un reporte, SIGE notifica al docente autor con el motivo; el docente puede registrar un reporte nuevo referenciado al original, que queda archivado sin modificación. | Rechazo del prefecto | Notificación + posibilidad de reporte nuevo referenciado. | Si el docente no corrige, el original permanece `RECHAZADO`. | RN-REP-02, RN-REP-03, RN-TRX-03 |
| RN-REP-09 | RES | Cada grupo tiene uno o más prefectos asignados y cada docente tiene los grupos que atiende (catálogos de RF-ADM-01). Un docente solo puede registrar reportes de estudiantes `ACTIVO` de sus grupos asignados; el reporte se envía a los prefectos asignados al grupo del estudiante. | Registro de reporte | Se rechaza el registro fuera de los grupos asignados. Si el grupo no tiene prefecto asignado, el reporte queda en la bandeja del Personal administrativo y del Administrador y se genera alerta. | — | RF-REP-01, RF-REP-03, RF-ADM-01, RN-TRX-02 |

### 2.7 Comunicación con familiares (COM)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-COM-01 | RES | Solo se envía comunicación a un familiar marcado como contacto válido en el expediente del estudiante. | Envío de comunicación | Rechazo si no hay contacto válido registrado. | — | RF-EST-03, RF-COM-01, RN-EST-11 |
| RN-COM-02 | RES | El contenido enviado a terceros (correo/mensajería) se limita a la información explícitamente autorizada para ese envío; nunca se adjunta el expediente completo del estudiante. | Preparación del envío | Filtrado de datos antes de enviar. | — | RF-COM-03, LFPDPPP |
| RN-COM-03 | HAB | Todo intento de envío de una comunicación por correo electrónico debe generar un registro de su estado de procesamiento. | Solicitud de envío | El sistema registra como mínimo fecha, hora y estado (`PENDIENTE`, `ENVIADO`, `FALLIDO`); si el proveedor proporciona información adicional de entrega, esta puede conservarse sin interpretarla como confirmación de lectura. | La confirmación de entrega o lectura no puede garantizarse. | RF-COM-01, RF-COM-02 |
| RN-COM-04 | RES | No se envía comunicación a un tutor cuyo consentimiento está `REVOCADO`. | Envío de comunicación | Se rechaza el envío a ese tutor y se advierte al personal; si existe otro tutor con contacto válido y consentimiento no revocado, puede usarse. | El alcance legal de la revocación sobre el tratamiento interno de datos debe definirlo la institución. | RN-EST-07, RN-EST-08, RN-COM-01, LFPDPPP |

### 2.8 Panel administrativo (ADM)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-ADM-01 | RES | Solo el rol Administrador puede modificar catálogos institucionales (grupos, grados, ciclos, tipos y niveles de gravedad de reporte, asignaciones prefecto–grupo y docente–grupo). | Modificación de catálogo | Rechazo para otros roles. Los elementos con historial se desactivan, no se eliminan (RN-TRX-03). | — | RF-ADM-01 |
| RN-ADM-02 | RES | Los parámetros operativos —ventana de prevención de rebote (1 a 30 min, 5 por defecto), hora de corte por grupo y jornada, hora de verificación de ausencias estudiantil (10:00 inicial) y docente, y tolerancia institucional de puntualidad docente (0 min inicial)— solo pueden configurarse desde el panel administrativo por el rol Administrador. La hora de verificación de ausencias DEBE ser posterior a la hora de corte del mismo grupo y jornada. | Cambio de parámetro operativo | Registro en bitácora y aplicación desde la fecha y hora del cambio; los cambios no alteran retroactivamente registros históricos ya determinados. Se rechaza un valor fuera de rango o que viole la restricción de horas. | — | RF-ADM-02, RN-AST-01, RN-AST-03, RN-AST-08, RN-AST-14, RN-AUT-05 |
### 2.9 Backend, API y Base de Datos (API)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-API-01 | RES | Toda regla de negocio se valida en el backend, independientemente de si el cliente (web o móvil) ya la validó. | Cualquier solicitud a la API | Rechazo si la validación de servidor falla, sin importar lo que haya permitido el cliente. | — | RF-API-02, OE-13 |
| RN-API-02 | DEF | La plataforma web y la aplicación móvil consumen exclusivamente la misma API y la misma base de datos; ningún cliente mantiene lógica de negocio ni almacenamiento propio de forma permanente. | — | — | Buffer temporal offline (RNF-FIA-01), que se sincroniza y no sustituye la fuente central. | RF-API-01, RF-MOV-02, OE-13 |
| RN-API-03 | HAB | Todo respaldo de base de datos se ejecuta automáticamente según la periodicidad configurada, sin depender de una acción manual del personal. | Cumplimiento del periodo configurado | Ejecución automática + registro del resultado (éxito/fallo). | — | RF-API-03 |

### 2.10 Aplicación móvil (MOV)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-MOV-01 | RES | Un registro generado desde la app móvil se sujeta exactamente a las mismas reglas (RN-AST-*, RN-REP-*) que uno generado desde la plataforma web. | Registro desde móvil | Mismas validaciones de backend (RN-API-01). | — | RF-MOV-02 |
| RN-MOV-02 | HAB | Si el dispositivo pierde conexión con el servidor durante una captura, almacena localmente únicamente el evento (fecha, hora de captura, tipo de evento e identificador QR leído), en un buffer de hasta 1,000 registros, y lo sincroniza automáticamente al restablecerse la conexión. | Pérdida de conectividad durante la captura | El evento queda marcado como **pendiente de validación**. Al sincronizarse, el backend valida existencia y vigencia del QR, identidad, estatus del estudiante, unicidad y rebote antes de incorporarlo al historial definitivo; los inválidos se descartan y se notifica al operador. | La captura offline no es una validación definitiva hasta sincronizar. Sin conexión no se puede verificar la existencia del token ni el estatus del estudiante. | RF-MOV-01, RNF-FIA-01, RN-API-01, RN-AST-02, RN-AST-03, RN-TRX-04 |
| RN-MOV-03 | RES | Con 1,000 eventos pendientes en el buffer, no se almacena ninguno nuevo. | Intento de captura con el buffer lleno | Se rechaza el evento y se alerta al operador para que reintente cuando haya conexión. | — | RNF-FIA-01, RN-MOV-02 |

### 2.11 Infraestructura y servidor local (INF)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-INF-01 | DEF | Las funciones de asistencia estudiantil y docente, reportes y consulta operan dentro de la red local institucional y no dependen de Internet. | — | — | — | RF-INF-02, OE-12 |
| RN-INF-02 | DEF | El envío de correo electrónico y el acceso remoto dependen de Internet; su indisponibilidad no debe afectar las funciones internas (RN-INF-01). | Caída de Internet (no de la red local) | Las funciones internas siguen operando; solo se detienen las dependientes de Internet. | — | RF-INF-02, RF-COM-01 |
| RN-INF-03 | HAB | Ante una interrupción del servidor local, el sistema sigue un procedimiento de recuperación documentado que restaura desde el último respaldo válido. | Interrupción del servidor | Ejecución del procedimiento de recuperación. | — | RF-INF-03, RN-API-03 |

---

## 3. Reglas transversales (TRX)

Aplican a **todos los módulos** por igual y suelen ser las que más se olvidan al programar módulo por módulo:

| ID | Tipo | Enunciado | Trazabilidad |
|---|---|---|---|
| RN-TRX-01 | RES | Ningún dato personal de un estudiante menor de edad se recolecta si no es estrictamente necesario para alguno de los módulos definidos en el alcance (principio de minimización). | LFPDPPP, RNF-SEG-04 |
| RN-TRX-02 | RES | El acceso a datos de menores se restringe exclusivamente al personal cuyo rol lo requiera para su función; ningún rol tiene acceso "por defecto" a todos los datos. | LFPDPPP, RN-AUT-02 |
| RN-TRX-03 | DEF | Ningún registro histórico (asistencia estudiantil y docente, reportes, expedientes dados de baja) se elimina físicamente de la base de datos; solo se archiva lógicamente. | RN-EST-04, RN-AST-06, RN-AST-21 |
| RN-TRX-04 | RES | La hora efectiva de un evento de asistencia es la hora en que ocurrió el escaneo: para eventos en línea, la hora del servidor al recibirlo; para eventos capturados sin conexión, la hora de captura del dispositivo corregida con el desfase respecto del servidor conocido en la última conexión. Un evento con hora efectiva futura se rechaza en la validación del backend y se notifica al operador. | RNF-FIA-04, RN-AST-01, RN-AST-09, RN-MOV-02 |
| RN-TRX-05 | RES | Ninguna regla de negocio se implementa únicamente en el frontend (web o móvil); toda regla vive en el backend y el frontend solo la refleja para mejorar la experiencia de uso. | RN-API-01, RNF-MAN-02 |
| RN-TRX-06 | INF | Un dato o registro que involucre a un tutor/familiar hereda las mismas restricciones de acceso por rol que el expediente del estudiante al que pertenece. | RN-EST-03, RN-TRX-02 |
| RN-TRX-07 | DEF | Los cambios automáticos de estado derivados de reglas de negocio deben distinguirse de las modificaciones manuales realizadas por un usuario, y conservar la información necesaria para identificar el origen del cambio (`ESCANEO`, `AUTOMÁTICO` o `MANUAL`). El historial debe permitir determinar si un estado fue generado por SIGE o modificado después por un usuario autorizado. | RN-AST-01, RN-AST-07, RN-AST-09, RN-AST-22, RN-AUT-05 |

---

## 4. Matriz de conflictos y dependencias entre reglas

Algunas reglas dependen o pueden entrar en tensión con otras; conviene tenerlas presentes al implementar:

| Reglas relacionadas | Tipo de relación | Nota |
|---|---|---|
| RN-AST-01 / RN-AST-07 / RN-AST-08 / RN-AST-09 | Secuencia | `ASISTIÓ`/`LLEGÓ TARDE` dependen de la hora efectiva del primer registro válido (RN-AST-01); los escaneos posteriores no cambian el estado (RN-AST-07); `FALTÓ` depende de la ausencia de registro a la hora de verificación (RN-AST-08); un escaneo posterior a `FALTÓ` reclasifica (RN-AST-09). |
| RN-AST-02 / RN-AST-03 / RN-MOV-02 / RN-API-01 | Dependencia | Los eventos offline no son definitivos hasta que el backend valide identidad, estatus, unicidad y rebote; la ventana de rebote se cuenta desde el último escaneo procesado. |
| RN-ADM-02 / RN-AST-08 / RN-AST-09 | Restricción | La hora de verificación debe ser posterior a la hora de corte; por eso la reclasificación depende de la hora efectiva del escaneo y no de la hora de sincronización (RN-TRX-04). |
| RN-REP-03 / RN-REP-07 / RN-REP-08 | Refuerzo | El rechazo del prefecto termina el flujo del original (corrección con reporte nuevo); el rechazo administrativo regresa al prefecto; `RESUELTO` se alcanza por RN-REP-07. |
| RN-EST-03 / RN-EST-10 / RN-EST-11 | Precondición | Ningún registro se guarda sin tutor con contacto válido; el incompleto solo admite faltantes diferidos. |
| RN-AST-13 / RN-AST-24 | Excepción | El `FALTÓ` automático docente no cuenta como entrada, lo que permite la reclasificación. |

---

## 5. Próximo paso sugerido

Este catálogo de reglas de negocio, junto con la Especificación de Requisitos v1, es el insumo directo para:
1. Redactar las **Historias de Usuario** (formato *Como \<rol\>, quiero \<acción\>, para \<beneficio\>*), cada una ligada a uno o más RF y validada contra las reglas de este catálogo.
2. Derivar los **Criterios de Aceptación específicos** en formato *Given/When/Then*, usando directamente el par condición→consecuencia de cada regla.
3. Alimentar el **Modelo de Datos**, ya que varias reglas (`DEF`, `RES`) implican restricciones de integridad que deben reflejarse en el esquema de PostgreSQL (unicidad, llaves foráneas, enumeraciones).

Si quieres, seguimos con las Historias de Usuario tomando como base este catálogo.
