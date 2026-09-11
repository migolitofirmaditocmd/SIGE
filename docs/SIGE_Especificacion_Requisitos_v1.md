# Especificación de Requisitos del Sistema — SIGE
### Sistema Integral de Gestión Escolar
**Documento derivado del Acta Constitutiva del Proyecto v8**
**Versión:** 1.0 — Ampliación de RF/RNF | **Estado:** Para revisión del equipo

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
| **CRE** | Credenciales | Toma esos códigos QR y arma el PDF listo para imprimir en tamaño de credencial física, para pegarlo o mandarlo a laminar. |
| **AUT** | Autenticación y usuarios | El "login" del sistema: quién puede entrar, con qué contraseña, y qué rol tiene (Admin, Prefecto, Docente, etc.), para que cada quien vea solo lo que le toca. |
| **AST** | Asistencia | El corazón operativo diario: cuando un alumno escanea su QR en la entrada, aquí se decide si llegó a tiempo, tarde, o si faltó, y se guarda el historial. |
| **REP** | Reportes escolares | El flujo de "reportes de conducta/académicos/emocionales": el maestro lo levanta, el prefecto lo revisa, administración decide si se avisa a la familia. |
| **COM** | Comunicación con familiares | La parte que efectivamente le manda el aviso al papá/mamá/tutor (por correo, o por WhatsApp como respaldo manual). |
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
| **Docente** | Registro de reportes escolares | Móvil |
| **Personal administrativo** | Revisión de reportes canalizados, autorización de comunicación a familia, justificación de faltas | Web |
| **Solo lectura / Auditoría** | Consulta de estadísticas e información consolidada, sin capacidad de modificación | Web |
| **Familiar / Tutor** | Receptor pasivo de comunicaciones (Solo correo); no tiene cuenta en el sistema en esta fase | Ninguno (canal externo) |
| **Estudiante** | Sujeto de los datos; se identifica mediante credencial con QR | No aplica (no es usuario del sistema) |

> Nota respecto a la matriz original: el RF-05 proponía 3 roles (Administrador, Prefecto, Solo Lectura). El acta (OE-05/06) exige distinguir explícitamente **Docente** y **Personal administrativo** como actores del flujo de reportes, por lo que se amplían a 5 roles funcionales. Esto debe reflejarse en el modelo de datos de usuarios y permisos.

---

## 3. Requisitos Funcionales (RF)

### 3.1 Gestión de Estudiantes e Importación — *(OE-02, OE-01 parcial · Hito 01–02)*

**RF-EST-01 — Expediente digital del estudiante** *(reemplaza y expande RF-02)*
El sistema DEBE mantener una ficha centralizada y única por estudiante con: nombre completo, fecha de nacimiento, fotografía, grado, grupo, ciclo escolar, matrícula, estatus (`ACTIVO`, `BAJA`, `EGRESADO`) y al menos un tutor/familiar asociado con datos de contacto y relación (padre, madre, tutor legal, otro).
- *Reglas de negocio:* la matrícula es única e inmutable; un cambio de estatus a `BAJA` o `EGRESADO` DEBE conservar el expediente histórico (no se elimina, se archiva lógicamente); DEBE existir bitácora de quién y cuándo modificó cada campo sensible.
- *Criterios de aceptación:* 100% de estudiantes de prueba con expediente completo y estatus consistente (KPI-07, KPI-09).
- *Prioridad:* Must. **Trazabilidad:** OE-02 · Hito 02 · KPI-07, KPI-09.

**RF-EST-02 — Transiciones de estatus del estudiante**
El sistema DEBE restringir las transiciones de estatus a un conjunto válido (`ACTIVO → BAJA`, `ACTIVO → EGRESADO`, `BAJA → ACTIVO` solo con autorización explícita) y DEBE impedir el registro de nueva asistencia o reportes para estudiantes en estatus distinto de `ACTIVO`.
- *Prioridad:* Should. **Trazabilidad:** OE-02 · Hito 02.

**RF-EST-03 — Asociación de familiares/tutores**
El sistema DEBE permitir asociar uno o más tutores por estudiante, cada uno con nombre, relación, teléfono y correo, y DEBE permitir marcar un tutor como "contacto principal" para efectos de notificación.
- *Prioridad:* Must. **Trazabilidad:** OE-02 · Hito 02.

**RF-EST-04 — Consulta y filtrado de expedientes**
El sistema DEBE permitir buscar y filtrar estudiantes por nombre, matrícula, grupo, grado y estatus, con resultados paginados.
- *Prioridad:* Must. **Trazabilidad:** OE-02 · Hito 02.

**RF-IMP-01 — Importación masiva de estudiantes (CSV/XLSX)** *(expande RF-01)*
El sistema DEBE permitir cargar archivos CSV y XLSX basados estrictamente en un diccionario de datos publicado por el equipo de desarrollo, ejecutando el proceso en modo transaccional por fila (una fila inválida no bloquea a las demás) y emitiendo, al finalizar, un reporte descargable con: total de filas procesadas, filas insertadas, filas con error y el detalle del error por fila (columna y motivo).
- *Reglas de negocio:* el sistema DEBE ofrecer una vista previa ("dry-run") antes de confirmar la importación definitiva; los registros duplicados (misma matrícula) DEBEN rechazarse y reportarse, no sobrescribirse silenciosamente.
- *Fuera de alcance (heredado del acta):* limpieza o transformación de datos históricos no estructurados — la institución debe entregar los archivos ya conformes al diccionario de datos.
- *Prioridad:* Must. **Trazabilidad:** OE-02 · Hito 02 · Fuera de alcance §7.

**RF-IMP-02 — Plantilla de importación descargable**
El sistema DEBERÍA proveer una plantilla CSV/XLSX descargable con las columnas exactas del diccionario de datos y ejemplos de formato válido, para reducir errores de captura por parte de la institución.
- *Prioridad:* Should. **Trazabilidad:** OE-02 · Hito 02.

---

### 3.2 Identificación mediante QR y Credenciales — *(OE-01 · Hito 01)*

**RF-QR-01 — Generación de identificador seguro por estudiante** *(expande RF-03)*
El sistema DEBE generar, para el 100% de los estudiantes registrados, un identificador único e irrepetible que **no exponga datos personales directamente legibles en el payload del código QR** (ver RNF-SEG-02); el identificador DEBE quedar asociado inequívocamente al registro del estudiante en la base de datos.
- *Reglas de negocio:* el identificador se genera una sola vez por estudiante salvo proceso explícito de regeneración (RF-QR-03); el sistema DEBE validar unicidad antes de persistir.
- *Criterios de aceptación:* 0 identificadores duplicados; 100% de QR legibles y correctamente asociados (KPI-01 a KPI-04).
- *Prioridad:* Must. **Trazabilidad:** OE-01 · Hito 01 · KPI-01, KPI-02, KPI-03, KPI-04.

**RF-QR-02 — Validación de unicidad e integridad**
El sistema DEBE ejecutar una validación automática de integridad (sin duplicados, sin huérfanos) antes de habilitar el lote de códigos para producción de credenciales, dentro del plazo máximo de 6 semanas desde el inicio del proyecto.
- *Prioridad:* Must. **Trazabilidad:** OE-01 · Hito 01 · KPI-05.

**RF-QR-03 — Revocación y regeneración de identificador**
El sistema DEBE permitir, únicamente al rol Administrador, revocar el identificador de un estudiante (p. ej. por pérdida o duplicidad de credencial física) y generar uno nuevo, invalidando el anterior para cualquier registro futuro de asistencia y conservando la trazabilidad del cambio.
- *Justificación:* no contemplado explícitamente en la matriz original, pero necesario en operación real (credenciales extraviadas); se agrega como requisito complementario al OE-01.
- *Prioridad:* Should. **Trazabilidad:** OE-01 · Hito 01 (complementario).

**RF-CRE-01 — Exportación de credenciales para impresión** *(expande RF-04)*
El sistema DEBE generar documentos PDF listos para imprimir en pliegos tamaño carta, con credenciales en medida estándar CR-80 (85.6 mm × 54 mm), incluyendo fotografía, nombre, grupo/grado, datos institucionales mínimos y el código QR, respetando márgenes de sangrado y guías de corte.
- *Prioridad:* Must. **Trazabilidad:** OE-01 · Hito 01 · KPI-06.

**RF-CRE-02 — Reimpresión selectiva de credenciales**
El sistema DEBERÍA permitir generar el PDF de credenciales para un subconjunto de estudiantes (por grupo o de forma individual), para atender reposiciones sin regenerar el lote completo.
- *Prioridad:* Should. **Trazabilidad:** OE-01 · Hito 01 (complementario).

---

### 3.3 Autenticación, Usuarios y Control de Acceso (RBAC) — *(OE-03 · Hito 02)*

**RF-AUT-01 — Autenticación basada en JWT** *(expande RF-05)*
El sistema DEBE autenticar usuarios mediante usuario/contraseña y emitir un token de acceso (JWT) de vida corta y un token de renovación (refresh token) de vida más larga, invalidable en caso de cierre de sesión o compromiso de cuenta.
- *Prioridad:* Must. **Trazabilidad:** OE-03 · Hito 02 · KPI-08.

**RF-AUT-02 — Control de acceso basado en roles (RBAC)** *(expande RF-05)*
El sistema DEBE restringir cada función y cada dato mostrado según el rol del usuario autenticado (Administrador/Directivo, Prefecto, Docente, Personal administrativo, Solo lectura), de forma que ningún usuario pueda acceder a información o acciones fuera de su rol, ni siquiera manipulando directamente la URL o la API.
- *Criterios de aceptación:* 100% de los roles definidos con permisos funcionales verificados mediante pruebas de autorización negativa (KPI-08).
- *Prioridad:* Must. **Trazabilidad:** OE-03 · Hito 02 · KPI-08.

**RF-AUT-03 — Gestión del ciclo de vida de cuentas**
El sistema DEBE permitir a Administrador dar de alta, desactivar y reasignar el rol de una cuenta de usuario, y DEBE bloquear temporalmente una cuenta tras un número configurable de intentos fallidos de inicio de sesión.
- *Prioridad:* Must. **Trazabilidad:** OE-03 · Hito 02.

**RF-AUT-04 — Recuperación segura de contraseña**
El sistema DEBE proveer un mecanismo de restablecimiento de contraseña mediante enlace de un solo uso enviado al correo institucional registrado, con expiración configurable.
- *Prioridad:* Should. **Trazabilidad:** OE-03 · Hito 02.

**RF-AUT-05 — Bitácora de auditoría de accesos y acciones críticas**
El sistema DEBE registrar usuario, fecha/hora, acción y resultado para inicios de sesión, cambios de rol, modificaciones de asistencia y reportes, y cambios de estatus de estudiante, de forma consultable por el rol Administrador.
- *Prioridad:* Must. **Trazabilidad:** OE-03, OE-08 · Hito 02 · KPI-58, KPI-61.

---

### 3.4 Control de Asistencia — *(OE-04 · Hito 03)*

**RF-AST-01 — Registro de asistencia por escaneo QR**
El sistema DEBE generar un registro de asistencia al validar el código QR de un estudiante, asociándolo a fecha, hora, grupo y jornada/periodo escolar correspondiente.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03 · KPI-13, KPI-15, KPI-18.

**RF-AST-02 — Prevención de escaneos duplicados ("rebote")** *(expande RF-06)*
El motor de asistencia DEBE ignorar y notificar (sin generar un segundo registro) escaneos del mismo estudiante que ocurran dentro de una ventana configurable, con valor por defecto de 5 minutos.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03 · KPI-16.

**RF-AST-03 — Determinación automática del estado de asistencia**
El sistema DEBE determinar el estado (`ASISTIÓ`, `FALTÓ`, `LLEGÓ TARDE`) a partir de reglas de horario configurables por la institución (hora de corte de entrada), aplicadas de forma consistente por grupo y jornada.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 03.

**RF-AST-04 — Historial diario de asistencia por grupo**
El sistema DEBE permitir consultar, para una fecha y grupo dados, la relación completa de estudiantes y su estado de asistencia correspondiente.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 07 · KPI-59.

**RF-AST-05 — Historial individual de asistencia**
El sistema DEBE permitir consultar el historial acumulado de asistencia de un estudiante específico a lo largo del ciclo escolar.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 07 · KPI-62.

**RF-AST-06 — Justificación y modificación de faltas con trazabilidad**
El sistema DEBE permitir a personal autorizado justificar una falta o modificar el estado registrado, exigiendo un motivo, y DEBE conservar un registro inmutable de quién hizo el cambio, cuándo y cuál era el estado anterior.
- *Prioridad:* Must. **Trazabilidad:** OE-04 · Hito 07 · KPI-63, KPI-64.

**RF-AST-07 — Información consolidada de apoyo a evaluación académica**
El sistema DEBE generar información agregada de asistencia (por estudiante, grupo y periodo) exportable o consultable, para ser usada por los docentes conforme a las reglas de evaluación que defina la institución (la fórmula de ponderación queda fuera de este documento).
- *Prioridad:* Should. **Trazabilidad:** OE-04 · Hito 07.

**RF-AST-08 — Notificación de contingencia vía WhatsApp** *(expande RF-07)*
El sistema DEBE incluir, en la vista de asistencia del estudiante, un botón que genere un enlace `https://wa.me/<telefono_tutor>?text=<mensaje>` con el estatus de asistencia prellenado, para envío manual por parte del prefecto sin costo para la institución, mientras el módulo de mensajería automatizada (OE-07) no esté disponible o como respaldo ante fallas del correo (ver riesgo R-02).
- *Reglas de negocio:* el mensaje generado NO DEBE incluir el identificador QR ni datos sensibles adicionales al nombre del estudiante y su estatus del día.
- *Prioridad:* Should. **Trazabilidad:** OE-04, OE-07 (contingencia) · Hito 03/07.

---

### 3.5 Reportes Escolares — *(OE-05/OE-06 · Hito 04/07)*

**RF-REP-01 — Registro de reporte por el docente**
El sistema DEBE permitir al docente registrar un reporte seleccionando tipo (`emocional`, `académico`, `conductual`), nivel de gravedad, una o más opciones predeterminadas según tipo/gravedad (basadas en el reglamento escolar) y una observación adicional de entre 50 y 100 caracteres, con contador de caracteres visible.
- *Prioridad:* Must. **Trazabilidad:** OE-05/06 · Hito 04/07 · KPI-45 a KPI-48.

**RF-REP-02 — Flujo de canalización del reporte**
El sistema DEBE encaminar cada reporte por el flujo `Docente → Prefecto → Personal administrativo → Familia`, permitiendo a cada rol únicamente las acciones que le correspondan (consultar, filtrar, canalizar, autorizar comunicación), sin importar si la etapa se ejecutó desde la app móvil o la plataforma web.
- *Prioridad:* Must. **Trazabilidad:** OE-05/06 · Hito 07 · KPI-49 a KPI-52.

**RF-REP-03 — Bandeja y filtrado por rol**
El sistema DEBE proveer, para prefectos y personal administrativo, una bandeja de reportes filtrable por tipo, gravedad, grupo, estudiante y estado.
- *Prioridad:* Must. **Trazabilidad:** OE-05/06 · Hito 04.

**RF-REP-04 — Trazabilidad completa del reporte**
El sistema DEBE conservar el historial de estados de cada reporte (registrado, revisado, canalizado, comunicado, resuelto) con usuario y fecha/hora de cada transición.
- *Prioridad:* Must. **Trazabilidad:** OE-05/06 · Hito 07 · KPI-53.

**RF-REP-05 — Paridad funcional en aplicación móvil**
El sistema DEBE permitir a docentes registrar reportes y a prefectos consultarlos/canalizarlos desde la aplicación móvil, con las mismas reglas de negocio, permisos y datos que la plataforma web.
- *Prioridad:* Must. **Trazabilidad:** OE-11 · Hito 04 · KPI-22, KPI-23.

---

### 3.6 Comunicación con Familiares — *(OE-07 · Hito 07)*

**RF-COM-01 — Envío automatizado de comunicaciones por correo**
El sistema DEBE permitir preparar y enviar por correo electrónico la información y los reportes previamente autorizados, utilizando los datos de contacto del expediente del estudiante.
- *Prioridad:* Should. **Trazabilidad:** OE-07 · Hito 07.

**RF-COM-02 — Registro de estado de envío**
El sistema DEBE registrar, cuando sea técnicamente posible, el estado de cada envío (enviado, fallido, pendiente), sin garantizar confirmación de lectura por parte del tutor.
- *Prioridad:* Should. **Trazabilidad:** OE-07 · Hito 07 · Riesgo R-02.

**RF-COM-03 — Consentimiento y minimización de datos en el envío**
El sistema DEBE limitar la información enviada a terceros (proveedor de mensajería/correo) a la estrictamente necesaria para la comunicación autorizada, sin exponer el expediente completo del estudiante.
- *Prioridad:* Must (regulatorio). **Trazabilidad:** OE-07, protección de datos de menores.

---

### 3.7 Panel Administrativo — *(OE-10 · Hito 02)*

**RF-ADM-01 — Administración centralizada**
El sistema DEBE proveer una interfaz única para que el rol Administrador gestione usuarios, estudiantes, catálogos (grupos, grados, ciclos, tipos y niveles de gravedad de reporte) y módulos habilitados.
- *Prioridad:* Must. **Trazabilidad:** OE-10 · Hito 02.

**RF-ADM-02 — Configuración de parámetros operativos**
El sistema DEBE permitir configurar, sin intervención de desarrollo, parámetros como la ventana de prevención de rebote (RF-AST-02), el horario de corte de asistencia (RF-AST-03) y las opciones predeterminadas del reglamento escolar por tipo/gravedad de reporte.
- *Prioridad:* Should. **Trazabilidad:** OE-10 · Hito 02/07.

**RF-ADM-03 — Panel de indicadores (KPIs)**
El sistema DEBERÍA mostrar al Administrador un tablero con los indicadores operativos clave (asistencia del día, reportes abiertos, credenciales pendientes), como apoyo a la toma de decisiones.
- *Prioridad:* Could. **Trazabilidad:** OE-10 (valor agregado, no explícito en el acta).

---

### 3.8 Backend, API y Base de Datos — *(OE-09 · Hito 01/03)*

**RF-API-01 — API documentada como fuente única de verdad**
El sistema DEBE exponer una API REST documentada (OpenAPI/Swagger) que sea consumida de forma exclusiva tanto por la plataforma web como por la aplicación móvil, evitando lógica de negocio duplicada entre clientes.
- *Prioridad:* Must. **Trazabilidad:** OE-09, OE-13 · Hito 03.

**RF-API-02 — Validación de datos del lado del servidor**
El sistema DEBE validar toda entrada de datos en el backend independientemente de la validación realizada en el cliente (web o móvil).
- *Prioridad:* Must. **Trazabilidad:** OE-08, OE-09.

**RF-API-03 — Respaldo periódico de la base de datos**
El sistema DEBE ejecutar respaldos automáticos de la base de datos con una periodicidad definida (mínimo diaria) y DEBE permitir restaurar un respaldo en un procedimiento documentado y probado.
- *Prioridad:* Must. **Trazabilidad:** OE-08, OE-12 · Hito 05 · KPI-32.

**RF-API-04 — Manejo estructurado de errores**
El sistema DEBE devolver errores en un formato consistente (código, mensaje, referencia de trazabilidad) tanto a la plataforma web como a la aplicación móvil.
- *Prioridad:* Should. **Trazabilidad:** OE-08, OE-09.

---

### 3.9 Aplicación Móvil — *(OE-11 · Hito 04)*

**RF-MOV-01 — Escaneo y validación de QR desde el dispositivo móvil**
La aplicación móvil DEBE permitir escanear el código QR de un estudiante usando la cámara del dispositivo y validar el identificador contra el backend en tiempo real.
- *Prioridad:* Must. **Trazabilidad:** OE-11 · Hito 04 · KPI-19, KPI-26.

**RF-MOV-02 — Registro y consulta de asistencia y reportes desde móvil**
La aplicación móvil DEBE permitir a los roles correspondientes registrar asistencia, registrar reportes y consultar su estado, utilizando la misma API, autenticación y reglas de negocio que la plataforma web (sin base de datos independiente).
- *Prioridad:* Must. **Trazabilidad:** OE-11, OE-13 · Hito 04 · KPI-21, KPI-24, KPI-25.

**RF-MOV-03 — Operación dentro de la red institucional**
La aplicación móvil DEBE poder comunicarse con el servidor local a través de la red Wi-Fi institucional para las funciones internas, sin requerir conexión a Internet.
- *Prioridad:* Must. **Trazabilidad:** OE-11, OE-12 · Hito 05 · KPI-30.

---

### 3.10 Infraestructura y Servidor Local — *(OE-12/OE-13 · Hito 05)*

**RF-INF-01 — Despliegue en servidor local institucional**
El sistema DEBE poder desplegarse en una computadora proporcionada por la institución, conectada a la red local, alojando backend, API y base de datos.
- *Prioridad:* Must. **Trazabilidad:** OE-12 · Hito 05 · KPI-28.

**RF-INF-02 — Separación de funciones internas y dependientes de Internet**
El diseño DEBE identificar y separar explícitamente qué funcionalidades operan exclusivamente dentro de la red local (asistencia, reportes, consultas) de aquellas que requieren Internet (envío de correo, acceso remoto).
- *Prioridad:* Must. **Trazabilidad:** OE-12 · Hito 05 · KPI-31.

**RF-INF-03 — Procedimiento de recuperación ante interrupción**
El sistema DEBE contar con un procedimiento documentado y probado de recuperación del servidor local y restauración de respaldo ante una interrupción del servicio.
- *Prioridad:* Must. **Trazabilidad:** OE-08, OE-12 · Hito 05/06 · KPI-32, KPI-44.

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
- *Prioridad:* Must. **Trazabilidad:** OE-08.

**RNF-SEG-02 — Privacidad del payload del QR** *(= RNF-02 original)*
El payload del código QR físico impreso en la credencial NO DEBE incluir datos personales directamente identificables (nombre, matrícula visible en claro, etc.); DEBE tratarse de un identificador opaco resoluble únicamente dentro del sistema.
- *Prioridad:* Must (regulatorio). **Trazabilidad:** LFPDPPP, OE-01.

**RNF-SEG-03 — Política de contraseñas y bloqueo por intentos fallidos**
El sistema DEBE exigir contraseñas con una longitud y complejidad mínimas configurables y DEBE bloquear temporalmente una cuenta tras un número definido de intentos fallidos consecutivos.
- *Prioridad:* Must. **Trazabilidad:** OE-03, OE-08.

**RNF-SEG-04 — Minimización y control de acceso a datos de menores**
El sistema DEBE limitar los campos de datos personales recolectados a los estrictamente necesarios (principio de minimización) y DEBE restringir el acceso a datos de menores exclusivamente al personal autorizado según su rol.
- *Prioridad:* Must (regulatorio). **Trazabilidad:** LFPDPPP, sección "Protección de datos de menores" del acta.

### 4.3 Fiabilidad / Disponibilidad

**RNF-FIA-01 — Tolerancia a desconexión con buffer local** *(= RNF-03 original)*
El módulo de escaneo de asistencia DEBE almacenar en un buffer local del navegador/dispositivo hasta 1,000 registros generados durante una pérdida de conectividad, y DEBE sincronizarlos automáticamente con el servidor al restablecerse la conexión, resolviendo conflictos de duplicidad conforme a la regla de rebote (RF-AST-02).
- *Prioridad:* Must. **Trazabilidad:** OE-04, OE-12 · Hito 06 · KPI-39.

**RNF-FIA-02 — Disponibilidad durante jornada escolar**
El sistema DEBE mantener disponibilidad del servidor local durante el horario de operación escolar definido por la institución, con un procedimiento de contingencia documentado ante caídas (ver RF-INF-03).
- *Prioridad:* Must. **Trazabilidad:** OE-12 · Riesgo R-09.

**RNF-FIA-03 — Respaldo y recuperación probados**
El procedimiento de respaldo de base de datos DEBE probarse mediante una restauración completa antes de cada hito de cierre, verificando la integridad de los datos recuperados.
- *Prioridad:* Must. **Trazabilidad:** OE-08 · Hito 05/08 · KPI-33, KPI-67.

### 4.4 Usabilidad

**RNF-USA-01 — Diseño visual y ergonomía en punto de acceso** *(= RNF-04 original)*
La interfaz DEBE implementar curvaturas tipo "squircle" (`border-radius: 12–16px`), contraste tipográfico elevado apto para pantallas expuestas a luz solar directa (zona de puerta/entrada), y retroalimentación visual/sonora inmediata ante un escaneo válido o inválido.
- *Prioridad:* Should. **Trazabilidad:** Hito 06 (validación de usabilidad) · KPI-37.

**RNF-USA-02 — Curva de aprendizaje del personal operativo**
Un prefecto o docente sin capacitación previa DEBERÍA poder completar las tareas críticas de su rol (escanear asistencia, registrar un reporte) con una guía mínima, alcanzando al menos 90% de tareas completadas correctamente en las pruebas de usabilidad.
- *Prioridad:* Should. **Trazabilidad:** Hito 06 · KPI-36.

### 4.5 Compatibilidad

**RNF-COM-01 — Hardware de captura de QR** *(= RNF-05 original)*
El módulo de captura de QR DEBE aceptar lectores USB emuladores de teclado (HID) y cámaras web estándar (UVC), sin requerir instalación de controladores propietarios.
- *Prioridad:* Could. **Trazabilidad:** Hito 03/06 · Riesgo R-13.

**RNF-COM-02 — Dispositivos y navegadores soportados**
El equipo DEBE definir y documentar, antes del Hito 04, el conjunto mínimo de dispositivos móviles (SO y versión) y navegadores web soportados, y validar la aplicación contra una muestra representativa de dicho conjunto.
- *Prioridad:* Must. **Trazabilidad:** OE-11 · Hito 04 · KPI-26 · Riesgo R-13.

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
- *Prioridad:* Must. **Trazabilidad:** OE-12 · Hito 05 · Riesgo R-14.

---

## 5. Matriz de trazabilidad resumida

| Módulo | Requisitos clave | OE | Hito principal | KPIs asociados |
|---|---|---|---|---|
| Estudiantes / Importación | RF-EST-01..04, RF-IMP-01..02 | OE-02 | Hito 02 | KPI-07, KPI-09 |
| QR / Credenciales | RF-QR-01..03, RF-CRE-01..02 | OE-01 | Hito 01 | KPI-01 a KPI-06 |
| Autenticación / RBAC | RF-AUT-01..05 | OE-03 | Hito 02 | KPI-08 |
| Asistencia | RF-AST-01..08 | OE-04 | Hito 03 / Hito 07 | KPI-13 a KPI-18, KPI-59 a KPI-64 |
| Reportes | RF-REP-01..05 | OE-05/06 | Hito 04 / Hito 07 | KPI-22, KPI-23, KPI-45 a KPI-53 |
| Comunicación | RF-COM-01..03 | OE-07 | Hito 07 | — |
| Panel administrativo | RF-ADM-01..03 | OE-10 | Hito 02 | KPI-07, KPI-08 |
| Backend/API/BD | RF-API-01..04 | OE-09 | Hito 01 / Hito 03 | KPI-28 a KPI-30 |
| App móvil | RF-MOV-01..03 | OE-11 | Hito 04 | KPI-19 a KPI-27 |
| Infraestructura local | RF-INF-01..03 | OE-12/13 | Hito 05 | KPI-28 a KPI-34, KPI-43, KPI-44 |
| RNF transversales | RNF-DES, RNF-SEG, RNF-FIA, RNF-USA, RNF-COM, RNF-MAN, RNF-POR | OE-08 | Todos | Ver secciones 4.1–4.7 |

---

## 6. Resumen de priorización MoSCoW (fase Hito 01–02)

**Must (bloquean el cierre de Hito 01/02):**
RF-EST-01, RF-EST-03, RF-EST-04, RF-IMP-01, RF-QR-01, RF-QR-02, RF-CRE-01, RF-AUT-01, RF-AUT-02, RF-AUT-03, RF-AUT-05, RF-ADM-01, RNF-SEG-01, RNF-SEG-02, RNF-SEG-03, RNF-SEG-04.

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
