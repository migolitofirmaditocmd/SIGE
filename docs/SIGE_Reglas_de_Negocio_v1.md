# Catálogo de Reglas de Negocio — SIGE
### Sistema Integral de Gestión Escolar
**Documento derivado del Acta Constitutiva v8 y de la Especificación de Requisitos v1**
**Versión:** 1.0 | **Estado:** Para revisión del equipo

---

## 1. Introducción

### 1.1 Propósito
Mientras que el documento de Requisitos Funcionales (RF) describe **qué debe hacer el sistema**, este catálogo describe **las reglas que gobiernan el comportamiento del negocio**, independientemente de cómo se implementen. Una regla de negocio es una afirmación que define o restringe algún aspecto del negocio, y que debe cumplirse sin importar qué módulo, pantalla o API la ejecute. Separarlas de los RF permite:

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
| RN-EST-01 | DEF | Un estudiante tiene exactamente un estatus: `ACTIVO`, `BAJA` o `EGRESADO`. | — | — | — | RF-EST-01, OE-02 |
| RN-EST-02 | RES | La matrícula de un estudiante es única e inmutable una vez asignada. | Alta o edición de estudiante | Se rechaza la operación si la matrícula ya existe o si se intenta modificar la de un registro existente. | Corrección administrativa excepcional, solo por Administrador, con registro en bitácora. | RF-EST-01 |
| RN-EST-03 | RES | Un estudiante DEBE tener al menos un tutor/familiar asociado con datos de contacto válidos antes de pasar a estatus `ACTIVO`. | Cambio a `ACTIVO` o alta inicial | Se bloquea la activación hasta contar con al menos un tutor. | — | RF-EST-03 |
| RN-EST-04 | HAB | Si un estudiante cambia a estatus `BAJA` o `EGRESADO`, el sistema conserva su expediente e historial, pero deja de aparecer en las operaciones activas del día (asistencia, reportes nuevos). | Cambio de estatus | Archivado lógico, no eliminación física. | Consulta histórica por rol autorizado. | RF-EST-02 |
| RN-EST-05 | RES | Solo un estudiante en estatus `ACTIVO` puede generar nuevos registros de asistencia o de reportes. | Intento de registrar asistencia/reporte | Se rechaza el registro con mensaje explícito. | — | RF-EST-02, RF-AST-01, RF-REP-01 |
| RN-EST-06 | INF | Un cambio de `BAJA` a `ACTIVO` (reingreso) requiere autorización explícita de Administrador y queda registrado como evento distinto del alta original. | Reactivación de estudiante | Se genera un registro de auditoría diferenciado. | — | RF-EST-02, RF-AUT-05 |

### 2.2 Importación masiva (IMP)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-IMP-01 | RES | Un archivo de importación solo se procesa si cumple exactamente el diccionario de datos vigente (columnas, tipos y formato). | Carga de archivo | Se rechaza el archivo completo antes de intentar procesar filas si la estructura no corresponde. | — | RF-IMP-01, OE-02 |
| RN-IMP-02 | CMP | Cada fila del archivo se procesa de forma independiente: una fila inválida no afecta el procesamiento de las demás filas válidas. | Procesamiento del archivo | Inserción parcial + reporte de errores por fila. | — | RF-IMP-01 |
| RN-IMP-03 | RES | Una fila cuya matrícula ya exista en el sistema se rechaza y se reporta como duplicada; nunca sobrescribe el registro existente. | Procesamiento de fila | Registro en el reporte de errores. | — | RF-IMP-01, RN-EST-02 |
| RN-IMP-04 | HAB | Toda importación DEBE ejecutarse primero en modo de vista previa ("dry-run") antes de habilitar la confirmación definitiva. | Inicio de importación | El sistema no persiste datos hasta la confirmación explícita del usuario. | — | RF-IMP-01 |

### 2.3 Identificación QR y Credenciales (QR / CRE)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-QR-01 | RES | Un estudiante tiene, en todo momento, cuando mucho un identificador QR **vigente**. | Generación de QR | Se rechaza generar un segundo QR vigente para el mismo estudiante sin revocar el anterior. | — | RF-QR-01, RF-QR-03 |
| RN-QR-02 | RES | El identificador QR no debe contener, en su payload, datos personales directamente legibles del estudiante. | Generación de QR | El valor codificado es un identificador opaco (token) sin nombre, matrícula visible ni CURP. | — | RF-QR-01, RNF-SEG-02, LFPDPPP |
| RN-QR-03 | DEF | Un identificador QR revocado nunca vuelve a estar vigente ni se reutiliza para otro estudiante. | Revocación | El histórico conserva la referencia al identificador revocado y a su reemplazo. | — | RF-QR-03 |
| RN-QR-04 | HAB | Si un identificador QR se revoca, todo escaneo posterior con ese identificador se rechaza automáticamente, aunque el estudiante siga `ACTIVO`. | Escaneo con QR revocado | Rechazo + alerta al operador para verificar identidad manualmente. | — | RF-QR-03, RF-AST-01 |
| RN-CRE-01 | RES | Solo se generan credenciales para estudiantes en estatus `ACTIVO` con QR vigente y fotografía cargada. | Solicitud de exportación de credenciales | Se excluyen del PDF los estudiantes que no cumplan la condición, listándolos aparte como pendientes. | — | RF-CRE-01, RF-EST-01 |

### 2.4 Autenticación y control de acceso (AUT)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-AUT-01 | DEF | Todo usuario del sistema tiene exactamente un rol activo entre: Administrador/Directivo, Prefecto, Docente, Personal administrativo, Solo lectura. | — | — | Un usuario puede tener roles distintos en momentos distintos, pero nunca dos roles simultáneos activos. | RF-AUT-02 |
| RN-AUT-02 | RES | Ninguna acción de escritura (crear, modificar, eliminar) puede ejecutarse desde el rol Solo lectura. | Cualquier operación de escritura | Rechazo a nivel de API, no solo ocultando el botón en la interfaz. | — | RF-AUT-02 |
| RN-AUT-03 | HAB | Tras un número configurable de intentos fallidos de inicio de sesión (por defecto 5), la cuenta se bloquea temporalmente. | Intento fallido de login | Bloqueo temporal + notificación al usuario del tiempo de espera. | Desbloqueo manual anticipado por Administrador. | RF-AUT-03, RNF-SEG-03 |
| RN-AUT-04 | RES | Un token de acceso (JWT) vencido no debe permitir ninguna operación, aunque el token de renovación siga vigente. | Solicitud con token vencido | Rechazo 401 + solicitud de renovación. | — | RF-AUT-01 |
| RN-AUT-05 | HAB | Toda acción crítica (cambio de rol, modificación de asistencia, modificación de reporte, cambio de estatus de estudiante) genera un registro de auditoría inmutable. | Ejecución de la acción | Registro con usuario, fecha/hora, valor anterior y valor nuevo. | — | RF-AUT-05 |

### 2.5 Control de asistencia (AST)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-AST-01 | CMP | El estado de asistencia (`ASISTIÓ`, `LLEGÓ TARDE`, `FALTÓ`) se determina comparando la hora del primer escaneo válido del día contra la hora de corte configurada para el grupo/jornada. | Cierre del periodo de registro de entrada | Asignación automática del estado. | El estado puede sobrescribirse posteriormente solo mediante justificación autorizada (RN-AST-04). | RF-AST-03 |
| RN-AST-02 | RES | Un estudiante no puede generar más de un registro de asistencia de entrada por fecha y jornada. | Segundo escaneo del mismo estudiante, mismo día, misma jornada | El segundo escaneo se descarta silenciosamente para el usuario y se registra como "rebote" en el log técnico. | — | RF-AST-02 |
| RN-AST-03 | CMP | Dos escaneos del mismo estudiante se consideran "rebote" (duplicado) si ocurren dentro de una ventana de tiempo configurable, con valor por defecto de 5 minutos. | Escaneo dentro de la ventana | Se ignora el segundo escaneo (ver RN-AST-02). | Configuración institucional entre 1 y 30 minutos. | RF-AST-02 |
| RN-AST-04 | RES | Solo un usuario con rol Administrador o Personal administrativo puede justificar una falta o modificar un estado de asistencia ya registrado. | Intento de modificar asistencia | Rechazo si el rol no está autorizado. | — | RF-AST-06 |
| RN-AST-05 | HAB | Toda justificación o modificación de un registro de asistencia exige capturar un motivo y conserva el valor anterior, el nuevo valor, el usuario y la fecha/hora del cambio. | Modificación de asistencia | Registro inmutable de trazabilidad. | — | RF-AST-06, RN-AUT-05 |
| RN-AST-06 | RES | Un registro de asistencia no puede eliminarse; solo puede modificarse su estado mediante el flujo de justificación (RN-AST-04). | Intento de borrado | Rechazo. | — | RF-AST-06 |
| RN-AST-07 | DEF | El historial diario de asistencia de un grupo siempre debe reflejar el 100% de los estudiantes `ACTIVO` del grupo para esa fecha, incluso los que no registraron ningún escaneo (se marcan como `FALTÓ` por omisión). | Generación del historial diario | — | — | RF-AST-04 |

### 2.6 Reportes escolares (REP)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-REP-01 | RES | La observación adicional de un reporte debe tener entre 50 y 100 caracteres inclusive. | Registro del reporte | El sistema no permite guardar fuera de ese rango. | — | RF-REP-01 |
| RN-REP-02 | DEF | Un reporte tiene exactamente un tipo (`emocional`, `académico`, `conductual`) y un nivel de gravedad, ambos asignados al momento del registro y no modificables después de enviarse al prefecto. | Registro / envío del reporte | Cambios posteriores requieren un reporte nuevo referenciado al original. | — | RF-REP-01 |
| RN-REP-03 | RES | Un reporte solo puede avanzar en el orden `Registrado → Revisado por prefecto → Canalizado → Revisado por administrativo → Comunicado a familia`; no puede saltarse etapas ni retroceder salvo rechazo explícito documentado. | Cambio de estado del reporte | Rechazo de transiciones no válidas. | Rechazo explícito por el prefecto o administrativo, con motivo obligatorio, regresa el reporte a una etapa anterior. | RF-REP-02, RF-REP-04 |
| RN-REP-04 | HAB | Un reporte solo puede comunicarse a la familia después de haber sido revisado y autorizado por Personal administrativo; nunca directamente desde el registro del docente o la revisión del prefecto. | Intento de comunicación a familia | Rechazo si no pasó por revisión administrativa. | — | RF-REP-02, OE-05/06 |
| RN-REP-05 | RES | Un docente solo puede consultar el estado de los reportes que él mismo registró, no los de otros docentes. | Consulta de reportes | Filtrado automático por autor. | Administrador y Personal administrativo ven todos. | RF-REP-03, RN-AUT-02 |
| RN-REP-06 | HAB | Cada cambio de etapa de un reporte genera automáticamente una entrada en su historial de trazabilidad, visible según el rol. | Cambio de etapa | Registro de trazabilidad. | — | RF-REP-04 |

### 2.7 Comunicación con familiares (COM)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-COM-01 | RES | Solo se envía comunicación a un familiar marcado como contacto válido en el expediente del estudiante. | Envío de comunicación | Rechazo si no hay contacto válido registrado. | — | RF-EST-03, RF-COM-01 |
| RN-COM-02 | RES | El contenido enviado a terceros (correo/mensajería) se limita a la información explícitamente autorizada para ese envío; nunca se adjunta el expediente completo del estudiante. | Preparación del envío | Filtrado de datos antes de enviar. | — | RF-COM-03, LFPDPPP |
| RN-COM-03 | HAB | Todo intento de envío (exitoso o fallido) queda registrado con fecha, hora y estado, cuando el proveedor lo permita. | Envío de comunicación | Registro de estado. | Si el proveedor no confirma entrega, se marca como "enviado sin confirmación", nunca como "entregado". | RF-COM-02 |

### 2.8 Panel administrativo (ADM)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-ADM-01 | RES | Solo el rol Administrador puede modificar catálogos institucionales (grupos, ciclos, tipos y niveles de gravedad de reporte). | Modificación de catálogo | Rechazo para otros roles. | — | RF-ADM-01 |
| RN-ADM-02 | RES | La ventana de prevención de rebote (RN-AST-03) y la hora de corte de asistencia (RN-AST-01) solo pueden configurarse desde el panel administrativo por rol Administrador, y todo cambio queda auditado. | Cambio de parámetro operativo | Registro en bitácora + aplicación inmediata a partir del cambio (no retroactiva). | — | RF-ADM-02, RN-AUT-05 |

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
| RN-MOV-02 | HAB | Si el dispositivo pierde conexión con el servidor, los registros se almacenan en el buffer local (hasta 1,000) y se sincronizan automáticamente al reconectar, aplicando las reglas de duplicidad (RN-AST-02/03) en el momento de la sincronización, no en el momento de la captura. | Pérdida y recuperación de conexión | Sincronización diferida + resolución de duplicados. | — | RF-MOV-03, RNF-FIA-01 |

### 2.11 Infraestructura y servidor local (INF)

| ID | Tipo | Enunciado | Condición / Disparador | Consecuencia | Excepciones | Trazabilidad |
|---|---|---|---|---|---|---|
| RN-INF-01 | DEF | Las funciones de asistencia, reportes y consulta operan exclusivamente dentro de la red local institucional y no dependen de Internet. | — | — | — | RF-INF-02, OE-12 |
| RN-INF-02 | DEF | El envío de correo electrónico y el acceso remoto dependen de Internet; su indisponibilidad no debe afectar las funciones internas (RN-INF-01). | Caída de Internet (no de la red local) | Las funciones internas siguen operando; solo se detienen las dependientes de Internet. | — | RF-INF-02, RF-COM-01 |
| RN-INF-03 | HAB | Ante una interrupción del servidor local, el sistema sigue un procedimiento de recuperación documentado que restaura desde el último respaldo válido. | Interrupción del servidor | Ejecución del procedimiento de recuperación. | — | RF-INF-03, RN-API-03 |

---

## 3. Reglas transversales (TRX)

Aplican a **todos los módulos** por igual y suelen ser las que más se olvidan al programar módulo por módulo:

| ID | Tipo | Enunciado | Trazabilidad |
|---|---|---|---|
| RN-TRX-01 | RES | Ningún dato personal de un estudiante menor de edad se recolecta si no es estrictamente necesario para alguno de los módulos definidos en el alcance (principio de minimización). | LFPDPPP, RNF-SEG-04 |
| RN-TRX-02 | RES | El acceso a datos de menores se restringe exclusivamente al personal cuyo rol lo requiera para su función; ningún rol tiene acceso "por defecto" a todos los datos. | LFPDPPP, RN-AUT-02 |
| RN-TRX-03 | DEF | Ningún registro histórico (asistencia, reportes, expedientes dados de baja) se elimina físicamente de la base de datos; solo se archiva lógicamente. | RN-EST-04, RN-AST-06 |
| RN-TRX-04 | HAB | Toda operación que modifique un dato ya persistido (no una creación nueva) genera una entrada de auditoría con el valor anterior y el nuevo. | RN-AUT-05 |
| RN-TRX-05 | RES | Ninguna regla de negocio se implementa únicamente en el frontend (web o móvil); toda regla vive en el backend y el frontend solo la refleja para mejorar la experiencia de uso. | RN-API-01, RNF-MAN-02 |
| RN-TRX-06 | INF | Un dato o registro que involucre a un tutor/familiar hereda las mismas restricciones de acceso por rol que el expediente del estudiante al que pertenece. | RN-EST-03, RN-TRX-02 |

---

## 4. Matriz de conflictos y dependencias entre reglas

Algunas reglas dependen o pueden entrar en tensión con otras; conviene tenerlas presentes al implementar:

| Reglas relacionadas | Tipo de relación | Nota |
|---|---|---|
| RN-AST-02 / RN-MOV-02 | Dependencia | La regla de "un solo registro por día" debe aplicarse también al sincronizar el buffer offline, no solo en tiempo real. |
| RN-QR-01 / RN-QR-03 | Secuencia | Revocar (RN-QR-03) es la única vía válida para que RN-QR-01 permita generar un nuevo QR vigente. |
| RN-REP-03 / RN-REP-04 | Refuerzo | RN-REP-04 es un caso particular de RN-REP-03 aplicado específicamente a la última etapa del flujo. |
| RN-EST-05 / RN-AST-01 | Precondición | Antes de calcular un estado de asistencia (RN-AST-01), el sistema debe verificar que el estudiante siga `ACTIVO` (RN-EST-05). |
| RN-API-01 / RN-TRX-05 | Refuerzo | Ambas reglas existen para blindar contra el riesgo R-07 y R-10 del acta (inconsistencia web/móvil). |

---

## 5. Próximo paso sugerido

Este catálogo de reglas de negocio, junto con la Especificación de Requisitos v1, es el insumo directo para:
1. Redactar las **Historias de Usuario** (formato *Como \<rol\>, quiero \<acción\>, para \<beneficio\>*), cada una ligada a uno o más RF y validada contra las reglas de este catálogo.
2. Derivar los **Criterios de Aceptación específicos** en formato *Given/When/Then*, usando directamente el par condición→consecuencia de cada regla.
3. Alimentar el **Modelo de Datos**, ya que varias reglas (`DEF`, `RES`) implican restricciones de integridad que deben reflejarse en el esquema de PostgreSQL (unicidad, llaves foráneas, enumeraciones).

Si quieres, seguimos con las Historias de Usuario tomando como base este catálogo.
