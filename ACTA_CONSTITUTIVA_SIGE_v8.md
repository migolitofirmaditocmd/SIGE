# ACTA CONSTITUTIVA DEL PROYECTO v8
# Sistema Integral de Gestión Escolar


## 1. Identificación del proyecto

### 1.1 Nombre provisional
**Sistema Integral de Gestión Escolar**

Nombre técnico provisional del producto: **SIGE**

---

## 2. Propósito del proyecto

El proyecto tiene como propósito establecer una infraestructura tecnológica centralizada, escalable y sostenible que reduzca la dependencia de procesos manuales, facilite el acceso y gestión de la información escolar y siente las bases para la incorporación progresiva de nuevas herramientas y servicios digitales que atiendan las necesidades de la institución.

---

## 3. Problema que se busca resolver

La institución requiere una solución tecnológica que permita modernizar y centralizar diversos procesos de gestión escolar que actualmente pueden depender de herramientas y procedimientos independientes o manuales.

Esta situación dificulta la organización de la información, incrementar la posibilidad de errores, limitar la trazabilidad de los procesos y hacer más compleja la consulta y generación de información útil para la toma de decisiones.

El proyecto busca atender esta necesidad mediante el desarrollo de una plataforma que integre progresivamente los principales procesos relacionados con:

- administración y consulta de información de estudiantes;
- identificación de estudiantes mediante códigos QR asociados a sus credenciales;
- registro y consulta de asistencia;
- registro y seguimiento de incidencias y comportamiento;
- generación de reportes escolares;
- comunicación de información relevante con los familiares;
- incorporación futura de herramientas y servicios adicionales de gestión escolar.

La solución deberá permitir que estas funcionalidades se desarrollen de manera progresiva sobre una misma infraestructura tecnológica, priorizando aquellas necesidades que representen mayor valor operativo para la institución.

---

## 4. Objetivo general

Desarrollar e implementar una plataforma digital integral para la gestión escolar que permita a la institución centralizar, organizar y automatizar procesos relacionados con la administración de estudiantes, identificación, control de asistencia, seguimiento de incidencias y comportamiento, generación de reportes y comunicación de información relevante a los familiares.

---

## 5. Objetivos específicos

### OE-01 — Identificación y códigos QR
Diseñar, desarrollar y validar un módulo que permita generar un identificador QR único para el 100 % de los estudiantes registrados, asociándolo inequívocamente con su información dentro del sistema y proporcionando los códigos en un formato apto para su incorporación en las credenciales institucionales, dentro de las primeras seis semanas del proyecto.

### OE-02 — Gestión de estudiantes
Implementar un módulo que permita registrar, consultar, modificar y administrar la información de los estudiantes, garantizando que el 100 % de los estudiantes registrados cuente con un expediente digital único y asociado a su identificador correspondiente antes de la puesta en operación del sistema.

### OE-03 — Gestión de usuarios y permisos
Implementar un sistema de autenticación y autorización que permita gestionar el acceso a la plataforma mediante los roles definidos por la institución, asegurando que cada usuario pueda acceder únicamente a las funciones y datos correspondientes a sus permisos antes de la puesta en operación del sistema.

### OE-04 — Registro y gestión de asistencia
Desarrollar e implementar un módulo de control de asistencia que permita registrar, consultar, modificar conforme a permisos y administrar la asistencia de estudiantes, docentes y personal administrativo, mediante mecanismos de identificación definidos por la institución, incluyendo el escaneo de códigos QR desde la aplicación móvil cuando corresponda.

Para los estudiantes, el sistema deberá permitir generar un registro de asistencia asociado a una fecha, grupo y jornada o periodo escolar, determinando el estado correspondiente de cada alumno, como:

- asistió;
- faltó;
- llegó tarde;
- falta justificada.

La información deberá almacenarse de manera que permita generar y consultar el historial diario de asistencia de cada grupo, incluyendo la relación de alumnos que lo integran y el estado de asistencia correspondiente a cada fecha.

El sistema deberá permitir que el personal autorizado pueda justificar faltas o modificar su estado cuando exista una situación especial debidamente autorizada por la institución, conservando la trazabilidad del cambio realizado.

Asimismo, deberá permitir consultar el historial individual de asistencia de un estudiante y generar información agregada que pueda ser utilizada por los docentes como apoyo para la determinación de la calificación, conforme a los criterios y reglas que establezca la institución.

### OE-05 — Reportes e incidencias escolares
Implementar un módulo de reportes escolares accesible desde la plataforma web y desde la aplicación móvil, que permita al personal docente registrar reportes relacionados con estudiantes mediante un flujo estructurado de clasificación, revisión, canalización y seguimiento.

El docente deberá poder registrar el reporte desde un dispositivo móvil o desde la plataforma web y determinar inicialmente:

- tipo de reporte: emocional, académico o conductual;
- nivel de gravedad del reporte;
- opciones o situaciones predeterminadas correspondientes al tipo y nivel de gravedad seleccionado, basadas en el reglamento escolar;
- una observación adicional de entre 50 y 100 caracteres.

Una vez registrado, el reporte deberá enviarse al prefecto correspondiente, quien podrá consultarlo, revisarlo y filtrarlo desde la plataforma web o aplicación móvil disponible para su rol.

El prefecto podrá determinar cuáles reportes deberán ser canalizados al personal administrativo autorizado, quien realizará la revisión correspondiente y determinará cuáles reportes deberán ser comunicados a la familia del estudiante.

El sistema deberá conservar el historial, estado y trazabilidad de cada reporte, permitiendo identificar su registro, revisión, canalización, comunicación y resolución conforme a los permisos definidos para cada rol.

### OE-06 — Reportes e incidencias escolares
Implementar un módulo de reportes escolares accesible desde la plataforma web y desde la aplicación móvil, que permita al personal docente registrar reportes relacionados con estudiantes mediante un flujo estructurado de clasificación, revisión, canalización y seguimiento.

El docente deberá poder registrar el reporte desde un dispositivo móvil o desde la plataforma web y determinar inicialmente:

- tipo de reporte: emocional, académico o conductual;
- nivel de gravedad del reporte;
- opciones o situaciones predeterminadas correspondientes al tipo y nivel de gravedad seleccionado, basadas en el reglamento escolar;
- una observación adicional de entre 50 y 100 caracteres.

Una vez registrado, el reporte deberá enviarse al prefecto correspondiente, quien podrá consultarlo, revisarlo y filtrarlo desde la plataforma web o aplicación móvil disponible para su rol.

El prefecto podrá determinar cuáles reportes deberán ser canalizados al personal administrativo autorizado, quien realizará la revisión correspondiente y determinará cuáles reportes deberán ser comunicados a la familia del estudiante.

El sistema deberá conservar el historial, estado y trazabilidad de cada reporte, permitiendo identificar su registro, revisión, canalización, comunicación y resolución conforme a los permisos definidos para cada rol.

### OE-07 — Comunicación con familiares
Integrar un mecanismo de comunicación automatizada con los familiares de los estudiantes mediante correo electrónico, permitiendo enviar información y reportes previamente definidos y autorizados, una vez que los módulos necesarios para generar dicha información se encuentren operativos.

El sistema deberá permitir preparar y enviar las comunicaciones autorizadas utilizando los datos de contacto registrados en el expediente del estudiante, manteniendo trazabilidad básica del envío y respetando los permisos y criterios definidos por la institución.

### OE-08 — Calidad, seguridad y continuidad
Implementar mecanismos de validación de datos, control de acceso, protección de información, manejo de errores, pruebas funcionales y respaldo de datos almacenados en el servidor local institucional, estableciendo criterios mínimos de calidad, seguridad, continuidad y recuperación que deberán cumplirse antes de la puesta en operación de cada módulo.

### OE-09 — Backend, base de datos y API
Diseñar e implementar la infraestructura de backend, base de datos y API necesaria para soportar de forma centralizada, segura y escalable el resto de los módulos del sistema, incluyendo mecanismos básicos de manejo de errores y respaldo, disponible de forma incremental desde el Hito 01.

### OE-10 — Panel administrativo
Implementar una interfaz centralizada que permita al personal autorizado administrar usuarios, estudiantes y módulos disponibles conforme a su rol, consolidando el acceso a las principales funciones operativas del sistema.

### OE-11 — Aplicación móvil para operación escolar
Diseñar, desarrollar e implementar una aplicación móvil integrada con la infraestructura de backend y API de SIGE, destinada a facilitar las operaciones escolares que requieran movilidad dentro de la institución.

La aplicación deberá contemplar, de acuerdo con los permisos correspondientes:

- escaneo de códigos QR de estudiantes;
- validación del identificador QR;
- registro de asistencia asociado al estudiante, grupo, fecha y hora;
- consulta del resultado del registro de asistencia;
- registro de reportes escolares por parte de docentes;
- consulta, revisión y canalización de reportes por parte de prefectos;
- acceso del personal autorizado a las funciones operativas que resulten necesarias para la gestión de asistencia y reportes.

La aplicación deberá utilizar los mismos mecanismos de autenticación, autorización, validación de datos y reglas de negocio establecidos para la plataforma web, evitando la creación de procesos independientes que puedan generar inconsistencias entre sistemas.

### OE-12 — Infraestructura y servidor local institucional
Configurar, desplegar y validar un entorno de operación local para SIGE mediante un servidor instalado en una computadora proporcionada por la institución y conectado a su red local, permitiendo que la plataforma web y la aplicación móvil accedan a los servicios internos del sistema sin depender de una conexión a Internet.

El entorno deberá contemplar la configuración de los servicios necesarios para la ejecución del sistema, conexión con la base de datos institucional, control de acceso, procedimientos básicos de respaldo y recuperación, así como mecanismos de diagnóstico y recuperación ante interrupciones del servicio.

La solución deberá diferenciar las funcionalidades que pueden operar exclusivamente dentro de la red institucional de aquellas que dependan de servicios externos, como el correo electrónico o el acceso remoto.

### OE-13 — Integración y operación multiplataforma
Integrar y validar la comunicación entre la plataforma web, aplicación móvil, API, base de datos y servidor local, garantizando que los componentes utilicen una fuente centralizada de información, las mismas reglas de negocio y mecanismos compatibles de autenticación, autorización y validación.

La integración deberá permitir ejecutar los procesos internos prioritarios desde computadoras y dispositivos móviles conectados a la red institucional, manteniendo la consistencia de la información independientemente del medio utilizado.

---

## 6. Producto final esperado

El proyecto deberá producir una plataforma integral de gestión escolar, compuesta por los siguientes módulos y componentes principales:

### 6.1. Gestión de estudiantes
Módulo destinado a centralizar la información básica y administrativa de los estudiantes, permitiendo:

- registrar y modificar datos de identificación, como nombre completo, fecha de nacimiento y fotografía;
- registrar información escolar, como grado, grupo, ciclo escolar y matrícula;
- asociar familiares o tutores, incluyendo sus datos de contacto y relación con el estudiante;
- consultar el expediente del estudiante;
- consultar la información relacionada con asistencia e incidencias;
- administrar el estado del estudiante dentro de la institución, como activo, egresado o dado de baja;
- importación de estudiantes a partir de archivos estructurados (Excel/CSV) que cumplan con un formato definido por el equipo de desarrollo, como mecanismo de alta inicial masiva.

### 6.2. Gestión de usuarios y permisos
Sistema de acceso que permita:

- autenticar usuarios;
- administrar cuentas;
- asignar roles y permisos;
- restringir el acceso a información y funciones según el rol.

### 6.3. Identificación y credenciales
Módulo encargado de generar y administrar la identificación digital de los estudiantes mediante:

- generación de un código QR único por estudiante;
- asociación del QR con su estudiante correspondiente;
- consulta y validación del identificador;
- generación de los códigos en un formato adecuado para su incorporación a las credenciales físicas.

### 6.4. Control de asistencia
Módulo destinado al registro, consulta y administración de asistencia de estudiantes, docentes y personal administrativo, integrado con la aplicación móvil y la plataforma web.

Se deberá poder:

- leer y validar códigos QR mediante la aplicación móvil;
- identificar al estudiante asociado al código;
- identificar el grupo al que pertenece;
- registrar la fecha y hora del escaneo;
- generar el registro correspondiente de asistencia;
- determinar el estado de asistencia de acuerdo con las reglas establecidas;
- prevenir registros inválidos o duplicados;
- consultar la asistencia diaria de un grupo;
- consultar el listado de alumnos pertenecientes a cada grupo;
- consultar el estado de cada alumno para una fecha determinada;
- diferenciar entre asistencia, falta, llegada tarde y falta justificada;
- consultar el historial de asistencia de un estudiante;
- permitir al personal autorizado justificar faltas o modificar su estado conforme a las reglas y permisos establecidos;
- conservar la trazabilidad de las modificaciones realizadas;
- generar información consolidada que pueda utilizarse como apoyo para los procesos de evaluación académica.

El sistema deberá conservar la información histórica de manera que los registros de asistencia puedan consultarse día por día y grupo por grupo, sin perder los registros correspondientes a fechas anteriores.

La aplicación móvil y la plataforma web deberán utilizar la misma fuente de información y las mismas reglas de negocio, manteniendo consistencia entre los registros generados desde ambos medios.

### 6.5. Reportes escolares
Módulo destinado al registro, revisión, clasificación y seguimiento de reportes escolares relacionados con estudiantes.

El flujo deberá permitir:

1. **Registro por el docente:** el docente seleccionará el tipo de reporte entre: emocional, académico, conductual.
2. **Clasificación de gravedad:** el docente seleccionará el nivel de gravedad correspondiente, de acuerdo con las categorías definidas por la institución.
3. **Opciones predeterminadas:** a partir del tipo y nivel de gravedad seleccionado, el sistema mostrará opciones predeterminadas basadas en el reglamento escolar, de las cuales el docente podrá seleccionar aquellas que describan mejor la situación.
4. **Observación adicional:** el docente podrá añadir una observación complementaria con una extensión limitada de 50 a 100 caracteres.
5. **Envío al prefecto:** una vez registrado, el reporte será enviado al prefecto correspondiente para su revisión.
6. **Filtrado por prefectura:** el prefecto podrá consultar, revisar y filtrar los reportes recibidos, determinando cuáles deberán ser canalizados al personal administrativo.
7. **Revisión administrativa:** el personal administrativo autorizado revisará los reportes canalizados por el prefecto y determinará cuáles deberán ser comunicados a la familia.
8. **Comunicación:** los reportes seleccionados podrán continuar hacia el módulo de comunicación con familiares para su envío mediante el canal autorizado por la institución.

El sistema deberá mantener el historial, estado y trazabilidad de cada reporte, registrando las etapas correspondientes del flujo sin permitir que un usuario acceda a información que no corresponda a su rol.

#### 6.5 B — Acceso desde aplicación móvil
El módulo de reportes escolares deberá encontrarse disponible tanto en la plataforma web como en la aplicación móvil para los roles que la institución determine.

La aplicación móvil deberá permitir al docente registrar reportes desde el dispositivo utilizado durante sus actividades escolares, así como consultar el estado de los reportes que haya generado cuando sus permisos lo permitan.

El prefecto deberá poder consultar, revisar y filtrar desde el dispositivo móvil los reportes que le hayan sido asignados y efectuar la canalización correspondiente hacia el personal administrativo.

La operación móvil deberá utilizar la misma información, reglas de negocio, autenticación, permisos y trazabilidad que la plataforma web.

El flujo funcional será:

> **Docente → Prefecto → Personal administrativo → Familia**

sin importar si una de las etapas fue ejecutada desde la aplicación móvil o desde la plataforma web.

### 6.6. Consultas e información consolidada
Módulo destinado a la consulta y generación de información a partir de los datos almacenados en el sistema.

Deberá permitir:

- consultar información de estudiantes;
- consultar registros de asistencia;
- consultar reportes escolares de acuerdo con los permisos del usuario;
- obtener información consolidada;
- aplicar filtros de consulta;
- generar información para apoyar los procesos administrativos y de seguimiento escolar;
- consultar el historial diario de asistencia de cualquier grupo autorizado;
- seleccionar una fecha y visualizar la relación completa de estudiantes pertenecientes al grupo;
- identificar el estado de cada estudiante: asistió, faltó, llegó tarde o falta justificada;
- consultar el historial acumulado de asistencia de un estudiante específico;
- filtrar información de asistencia por estudiante, grupo, fecha, periodo y estado;
- consultar las modificaciones o justificaciones realizadas sobre registros de asistencia, de acuerdo con los permisos del usuario;
- proporcionar información de asistencia para apoyar el cálculo o determinación de evaluaciones académicas conforme a las reglas establecidas por la institución.

### 6.7. Comunicación con familiares
Componente destinado a facilitar la comunicación institucional mediante correo electrónico:

- preparación de información y reportes para envío;
- identificación de los familiares o responsables autorizados para recibir la comunicación;
- generación de comunicaciones a partir de información previamente definida;
- envío automatizado de correos electrónicos;
- registro básico del estado del envío, cuando sea técnicamente posible.

### 6.8. Panel administrativo
Interfaz central para que el personal autorizado pueda:

- administrar usuarios y estudiantes;
- consultar información;
- gestionar los módulos disponibles según su rol;
- acceder a las principales funciones operativas del sistema.

### 6.9. Backend, base de datos, API y servidor local
Infraestructura de software y despliegue encargada de proporcionar:

- almacenamiento centralizado de la información;
- lógica de negocio;
- API para la comunicación entre aplicaciones y módulos;
- control de acceso y validación;
- mecanismos básicos de seguridad y manejo de errores;
- base de datos institucional;
- mecanismos de respaldo y recuperación de información;
- servicios necesarios para la operación del sistema dentro de la red institucional.

La solución deberá contemplar como infraestructura principal de operación un servidor local instalado en una computadora de la institución, conectado a la red local de la escuela, donde se almacenará la base de datos y la información generada por el sistema.

El servidor local permitirá que los principales procesos internos del sistema continúen disponibles dentro de la institución aun cuando exista una interrupción temporal de la conexión a Internet. La conexión a Internet se utilizará para aquellas funciones que dependan de servicios externos, como determinadas funciones de comunicación o acceso remoto.

El diseño deberá contemplar mecanismos de respaldo de la información y procedimientos básicos de recuperación ante fallos, de acuerdo con las capacidades y recursos disponibles de la institución.

### 6.10. Aplicación móvil
Aplicación móvil integrada con SIGE, destinada a facilitar operaciones escolares que requieran movilidad dentro de la institución.

La aplicación deberá contemplar, de acuerdo con el rol del usuario:

**Para docentes:**
- autenticación;
- escaneo de códigos QR;
- registro de asistencia;
- consulta del resultado de los registros realizados;
- registro de reportes escolares;
- consulta de los reportes generados y su estado, conforme a sus permisos.

**Para prefectos:**
- autenticación;
- consulta de reportes recibidos;
- filtrado y revisión de reportes;
- canalización de reportes hacia el personal administrativo;
- consulta del estado de los reportes conforme a sus permisos.

**Para personal autorizado:**
- consulta de información operativa;
- consulta y gestión de asistencias;
- justificación de faltas;
- modificación del estado de asistencia cuando exista autorización;
- consulta de información necesaria para las funciones administrativas asignadas.

La aplicación deberá comunicarse con el backend mediante la API institucional de SIGE y utilizar la misma base de datos, reglas de negocio, mecanismos de autenticación, autorización y validación que la plataforma web.

Cuando el sistema se encuentre operando dentro de la institución, los dispositivos móviles deberán poder comunicarse con el servidor local mediante la red institucional, permitiendo realizar las funciones internas sin depender de una conexión a Internet, siempre que exista conectividad con la red local.

Las funciones que dependan de servicios externos, como el envío de correo electrónico o el acceso remoto desde fuera de la institución, permanecerán sujetas a la disponibilidad de Internet y de dichos servicios.

---

## 7. Matriz de alcance

La siguiente matriz delimita los componentes y funcionalidades contemplados dentro del proyecto, así como aquellos elementos que quedan fuera de su alcance. Esta delimitación busca establecer una base clara para la planificación, desarrollo, validación y aceptación del sistema, evitando la incorporación de funcionalidades no contempladas originalmente.

| Área | Dentro del alcance | Fuera del alcance |
|---|---|---|
| **Gestión de estudiantes** | Registro, consulta, modificación y administración de la información de los estudiantes. Importación desde archivos estructurados (Excel/CSV) con formato definido. | Carga o incorporación masiva de información histórica de estudiantes cuando los datos no se encuentren en archivos estructurados, como Excel o CSV, o cuando requieran limpieza, corrección o transformación adicional antes de poder utilizarse en el sistema. |
| **Gestión de usuarios** | Registro de usuarios, autenticación, gestión de cuentas y asignación de permisos de acuerdo con los roles definidos por la institución. | Administración de cuentas personales externas a la plataforma o sistemas de identidad institucional no contemplados durante la definición del proyecto. |
| **Gestión de familiares** | Registro y asociación de familiares o responsables con los estudiantes correspondientes y consulta de la información necesaria para los procesos de comunicación. | Gestión de información familiar que no sea necesaria para la operación del sistema. |
| **Identificación mediante QR** | Generación de identificadores QR únicos, asociación con estudiantes, consulta y validación de los códigos y preparación de los mismos para su incorporación en credenciales. | Diseño, fabricación, impresión, distribución o reposición física de las credenciales. |
| **Control de asistencia** | Registro y consulta de asistencia de estudiantes, docentes y personal administrativo; escaneo y validación de QR mediante la aplicación móvil; registro de fecha y hora; asociación con grupo y jornada; historial diario por grupo; historial individual por estudiante; estados de asistió, faltó, llegó tarde y falta justificada; justificación y modificación de faltas por personal autorizado; prevención de registros inválidos o duplicados; generación de información de asistencia para apoyar procesos de evaluación. | Desarrollo de dispositivos físicos especializados para lectura de QR, sistemas biométricos o mecanismos de identificación no contemplados en los requerimientos del proyecto. |
| **Reportes escolares** | Registro de reportes por parte de docentes; clasificación por tipo emocional, académico o conductual; selección del nivel de gravedad; selección de opciones predeterminadas basadas en el reglamento escolar; observación adicional de 50–100 caracteres; envío al prefecto; filtrado y canalización por parte del prefecto; revisión por personal administrativo y determinación de los reportes que serán comunicados a la familia; almacenamiento y trazabilidad del flujo. | Automatización de decisiones disciplinarias, interpretación automática de situaciones, evaluación automática del comportamiento mediante inteligencia artificial o modificación del reglamento escolar desde el sistema. |
| **Consultas e información** | Consulta, filtrado y generación de información consolidada sobre estudiantes, asistencia y reportes, de acuerdo con los permisos establecidos para cada rol. | Sistemas avanzados de analítica, inteligencia artificial o predicción que no hayan sido definidos dentro de los requerimientos originales. |
| **Panel administrativo** | Administración de usuarios y estudiantes; consulta de información; gestión de módulos disponibles según el rol; gestión de asistencia; consulta y seguimiento de reportes; administración de catálogos y configuraciones necesarias para la operación del sistema. | Personalizaciones independientes para cada usuario que no sean necesarias para la operación general del sistema; funcionalidades administrativas no contempladas en los requisitos aprobados. |
| **Comunicación con familiares** | Integración con el servicio de mensajería seleccionado para permitir el envío automatizado de información y reportes definidos por la institución. | Costos de servicios externos, campañas masivas, funcionalidades propias de la plataforma de mensajería no relacionadas con el sistema y canales de comunicación adicionales no contemplados. |
| **Aplicación Móvil** | Autenticación; escaneo y validación de códigos QR; registro de asistencia; consulta de resultados; registro y consulta de reportes; revisión y canalización de reportes por prefectura; consulta de información operativa según permisos; comunicación con la API institucional; operación mediante la red local cuando se encuentre dentro de la institución. | Desarrollo de aplicaciones móviles no relacionadas con SIGE; funcionalidades no contempladas en los requisitos aprobados; versiones para plataformas o dispositivos fuera de las plataformas definidas durante la planificación. |
| **Backend y API** | Desarrollo de los servicios, API y mecanismos de comunicación necesarios para soportar las aplicaciones y módulos incluidos en el proyecto. | APIs o integraciones con sistemas externos no identificados o aprobados durante la definición del alcance. |
| **Base de datos** | Diseño, implementación y administración de la base de datos necesaria para almacenar la información del sistema, así como su configuración dentro del servidor local institucional y la implementación de mecanismos básicos de respaldo y recuperación. | Almacenamiento de información ajena a los procesos contemplados en el proyecto o infraestructura de almacenamiento externa no requerida para la operación definida. |
| **Seguridad y control** | Autenticación, autorización, control de acceso por roles, validación de información, protección de datos, manejo de errores, control de acceso a reportes según el rol, mecanismos básicos de seguridad del sistema y respaldo de información. | Certificaciones especializadas, auditorías externas de seguridad, infraestructura avanzada de ciberseguridad o servicios especializados que no formen parte de los requerimientos acordados. |
| **Pruebas y validación** | Pruebas funcionales, validación de los módulos desarrollados y corrección de errores identificados antes de la puesta en operación. | Pruebas de certificación externa o auditorías independientes no contempladas en el proyecto. |
| **Infraestructura y despliegue** | Configuración y preparación de la infraestructura necesaria para poner en operación el sistema dentro del entorno tecnológico definido por la institución, incluyendo la configuración del servidor local en una computadora de la escuela y su conexión con la red institucional. | Adquisición de servidores físicos, computadoras, redes institucionales u otra infraestructura física que no haya sido especificada como parte del proyecto. |
| **Servidor local y red institucional** | Configuración de una computadora proporcionada por la institución como servidor local; instalación y configuración de los servicios necesarios para SIGE; despliegue de backend, API y base de datos; conexión con la red local; configuración para acceso desde plataforma web y aplicación móvil; mecanismos básicos de respaldo y recuperación; pruebas de operación sin Internet. | Adquisición de hardware especializado; administración integral de la infraestructura de red institucional; reparación de equipos físicos; ampliación de la red Wi-Fi; servicios de acceso remoto no contemplados; infraestructura de alta disponibilidad o redundancia especializada. |
| **Mantenimiento y evolución** | Corrección de errores derivados de la implementación y ajustes necesarios durante la validación y puesta en operación inicial. | Desarrollo indefinido de nuevas funcionalidades posteriores a la entrega sin un proceso de ampliación o modificación del alcance. |

---

## 8. Condiciones y modalidad de ejecución del proyecto

### Tiempo
El proyecto dispone de un máximo de **480 horas de trabajo**, distribuidas en **24 semanas × 20 horas/semana** del equipo.

### Recursos humanos
El desarrollo será realizado por un equipo de dos personas, con una disponibilidad conjunta de 20 horas semanales, equivalente a aproximadamente 10 horas semanales por integrante.

El equipo será responsable de:

- análisis y levantamiento de requisitos;
- diseño y arquitectura del sistema;
- desarrollo frontend y backend;
- diseño e implementación de la base de datos;
- pruebas y corrección de errores;
- documentación;
- despliegue y validación del producto.

Se contempla adicionalmente la participación de usuarios o representantes de la institución para:

- levantamiento y validación de requisitos;
- revisión de prototipos y funcionalidades;
- pruebas de aceptación;
- retroalimentación sobre el funcionamiento del sistema.

### Modalidad de trabajo
Debido a que el desarrollo del proyecto se realizará como parte de un servicio social, se propone implementar una modalidad de trabajo mixta (presencial y virtual), buscando aprovechar las ventajas de ambas modalidades sin comprometer las necesidades de levantamiento de información, desarrollo y validación del sistema.

La modalidad **virtual** estará orientada principalmente a las actividades que puedan realizarse de manera remota utilizando los equipos de cómputo del equipo de desarrollo, proporcionando mayor flexibilidad y autonomía durante las actividades de desarrollo:

- programación;
- diseño y administración de la base de datos;
- documentación;
- diseño de interfaces y prototipos;
- análisis de requisitos;
- corrección de errores;
- pruebas técnicas.

La modalidad **presencial** se utilizará para las actividades que requieran interacción directa con la institución, usuarios o el entorno real donde será utilizado el sistema, particularmente:

- levantamiento de información de campo;
- observación de los procesos actuales;
- aclaración y validación de requisitos;
- reuniones y seguimiento del proyecto con responsables y usuarios;
- revisión presencial de prototipos y funcionalidades;
- pruebas de usabilidad;
- pruebas de aceptación;
- recopilación de retroalimentación;
- identificación y validación de necesidades.

La modalidad propuesta estará sujeta a la autorización y disponibilidad de la institución receptora del servicio social, así como a los horarios y condiciones que ésta establezca.

### Restricción tecnológica — Stack base

| Componente | Tecnología |
|---|---|
| Lenguaje principal | TypeScript, Python |
| Framework web | Next.js (Frontend), Django (Backend/API) |
| Base de datos | PostgreSQL |
| Control de versiones y repositorio | Git + GitHub |

### Protección de datos de menores de edad

Debido a que el sistema tratará datos personales de estudiantes menores de edad, se aplicarán medidas mínimas conforme a la Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP) y su reglamento, en particular:

- Limitar los campos de datos personales recolectados a los estrictamente necesarios para la operación del sistema (principio de minimización);
- Obtener el consentimiento del padre, madre o tutor legal para el tratamiento de los datos del menor, según los medios que defina la institución;
- Restringir el acceso a datos de menores exclusivamente al personal autorizado conforme a sus roles;
- Evitar la exposición de datos de menores a terceros no contemplados en el alcance (por ejemplo, proveedores de mensajería) más allá de la información estrictamente necesaria para el envío autorizado.

### Infraestructura de operación

La operación principal del sistema se realizará mediante un servidor local instalado en una computadora proporcionada por la institución, conectado a la red local de la escuela.

Esta infraestructura será utilizada para alojar los servicios necesarios del sistema y la base de datos institucional, permitiendo que los usuarios autorizados puedan acceder a las funcionalidades principales desde los dispositivos conectados a la red institucional.

El diseño deberá considerar:

- disponibilidad del sistema dentro de la red local;
- almacenamiento de la información institucional;
- control de acceso al servidor;
- respaldo periódico de la base de datos;
- procedimientos básicos de recuperación;
- mantenimiento del servidor;
- dependencia de servicios externos únicamente cuando una funcionalidad específica lo requiera.

La adquisición, sustitución o ampliación del equipo físico utilizado como servidor quedará sujeta a la disponibilidad y autorización de la institución.

La infraestructura deberá permitir que la plataforma web y la aplicación móvil se comuniquen con la API y los servicios de SIGE alojados en el servidor local mediante la red institucional. De esta manera, las operaciones internas de registro y consulta de información podrán realizarse desde computadoras y dispositivos móviles conectados a la red local sin requerir acceso a Internet, siempre que el servidor y la red institucional permanezcan disponibles.

La arquitectura deberá separar las funciones internas del sistema de aquellas que dependan de servicios externos. La pérdida de conexión a Internet no deberá impedir, por sí misma, el funcionamiento de los procesos internos que puedan ejecutarse exclusivamente con la información y servicios alojados dentro de la institución.

El acceso remoto desde fuera de la red institucional no se considerará parte de la operación local y, en caso de implementarse, deberá definirse posteriormente mediante mecanismos de acceso remoto seguros y autorizados.

#### Aclaración sobre operación sin Internet

Para efectos de este proyecto, la operación sin Internet significa que las funciones internas de SIGE podrán ejecutarse mientras exista comunicación entre los dispositivos de los usuarios y el servidor local mediante la red institucional.

Esto no implica que el sistema sea completamente independiente de la conectividad de red. Las funciones que dependan de servicios externos, como el envío de correo electrónico, requerirán nuevamente conexión a Internet para ejecutarse.

La pérdida de Internet y la pérdida de conectividad con el servidor local deberán considerarse escenarios diferentes dentro del plan de pruebas y contingencia.

### Costos estimados

El proyecto contempla principalmente costos asociados a infraestructura, servicios tecnológicos y comunicación. Debido a que el proyecto se encuentra en etapa de planeación, los siguientes valores deben considerarse estimaciones de referencia y podrán variar dependiendo de las necesidades finales del sistema, el volumen de usuarios, el consumo de servicios externos y las tarifas vigentes al momento de su implementación.

| Concepto | Costo estimado | Observaciones |
|---|---|---|
| Computadoras y equipo de desarrollo | $0 MXN | Se utilizarán los equipos de cómputo disponibles del equipo de desarrollo, por lo que no se contempla la adquisición de nuevos equipos dentro del presupuesto base. |
| Software de desarrollo | $0 MXN | Se priorizará el uso de herramientas y tecnologías de código abierto o con versiones gratuitas, como Python, Django, PostgreSQL y herramientas de desarrollo compatibles. |
| Servidor local / infraestructura de operación | $0 MXN inicialmente | Se utilizará una computadora disponible de la institución como servidor local. No se contempla inicialmente la adquisición de un servidor físico dedicado. Podrían generarse costos posteriores por mantenimiento, almacenamiento, reemplazo o actualización del equipo. |
| Dominio web | $200–$500 MXN/año | Estimación para un dominio convencional. Podría no ser necesario durante las primeras etapas del desarrollo. |
| Base de datos | $0 MXN inicialmente | La base de datos será alojada en el servidor local de la institución. El costo adicional dependerá de las necesidades futuras de almacenamiento, respaldo o infraestructura complementaria. |
| Servicio de mensajería | Variable | El costo dependerá del medio utilizado y del volumen de mensajes enviados. Se deberá considerar el precio por mensaje, posibles tarifas de plataforma y, en su caso, costos asociados al uso de APIs de terceros. |
| Correo electrónico transaccional | $0–$500 MXN/mes | Se contempla para el envío de notificaciones, recuperación de cuentas, avisos y otros mensajes automáticos. El costo dependerá del volumen mensual y del proveedor seleccionado. |
| Materiales para pruebas y levantamiento de información | $0–$500 MXN | Impresiones, formatos, hojas de evaluación u otros materiales que pudieran requerirse durante las actividades presenciales. |
| Otros servicios tecnológicos | $0–$500 MXN/mes | Costos eventuales de almacenamiento, herramientas complementarias, servicios de terceros u otros recursos que resulten necesarios durante el desarrollo. |

#### Consideración específica sobre el servicio de mensajería

Debido a que el sistema contempla la posibilidad de enviar notificaciones automáticas a usuarios, el servicio de mensajería representa uno de los costos variables más importantes del proyecto.

Para efectos de planeación, se propone contemplar inicialmente un presupuesto estimado de $300 a $1,000 MXN mensuales, sujeto a validación durante la etapa de diseño y selección del proveedor. Este monto es únicamente una estimación de referencia y no constituye un precio definitivo.

El costo final dependerá principalmente de:

- número de usuarios registrados;
- cantidad de mensajes enviados mensualmente;
- tipo de mensaje y canal utilizado;
- proveedor seleccionado;
- tarifas por mensaje o por conversación;
- utilización de SMS, correo electrónico, WhatsApp u otros canales;
- posibles costos de establecimiento, número telefónico o servicios adicionales de la plataforma.

Durante el desarrollo se priorizarán alternativas de bajo costo o gratuitas para pruebas, evitando generar gastos innecesarios mientras el sistema se encuentre en etapa de desarrollo.

#### Presupuesto general de referencia

Considerando únicamente los costos externos potenciales, se estima que el proyecto podría requerir inicialmente entre $500 y $2,000 MXN mensuales durante las etapas en las que se encuentren activos servicios de infraestructura y mensajería.

Este rango es preliminar y sujeto a cambios, por lo que el presupuesto definitivo deberá establecerse después de determinar la arquitectura final del sistema, el número esperado de usuarios, los mecanismos de notificación y los proveedores que serán utilizados.

---

## 9. Principios de desarrollo

El proyecto seguirá los siguientes principios:

1. **Valor antes que volumen:** se priorizarán funcionalidades que solucionen necesidades reales.
2. **Software funcionando como evidencia de progreso.**
3. **Desarrollo incremental:** cada etapa deberá producir un incremento verificable (ver sección de Hitos).
4. **Validación temprana:** las decisiones importantes deberán comprobarse lo antes posible.
5. **Simplicidad:** evitar funcionalidades y tecnologías innecesarias.
6. **Calidad integrada:** las pruebas no se dejarán exclusivamente para el final.
7. **Seguridad desde el diseño:** la información escolar será tratada como información sensible.
8. **Documentación progresiva:** la documentación crecerá junto con el producto.
9. **Mejora continua:** al finalizar cada ciclo se identificarán oportunidades de mejora.
10. **Control de cambios:** ningún cambio importante de alcance se incorporará sin evaluar su impacto en tiempo, riesgo y objetivos.

---

## 10. Criterio general de éxito

El proyecto se considerará exitoso cuando exista una versión funcional, integrada y validada de SIGE que permita ejecutar de principio a fin los procesos prioritarios definidos en el alcance mediante la plataforma web y la aplicación móvil, utilizando una fuente centralizada de información alojada en el servidor local institucional.

La solución deberá demostrar interoperabilidad entre la aplicación móvil, la plataforma web, la API, la base de datos y el servidor local, así como control de acceso, trazabilidad de las operaciones críticas, mecanismos básicos de respaldo y recuperación y capacidad para ejecutar los procesos internos prioritarios dentro de la red institucional sin depender de Internet, salvo aquellas funciones que requieran servicios externos.

---

## 11. Hitos y niveles de madurez tecnológica

Cada hito permitirá evaluar de manera progresiva el grado de desarrollo, integración, validación y preparación para operación del producto. Representa un punto de control del proyecto y deberá contar con resultados verificables y KPIs que permitan determinar objetivamente si se cumplen las condiciones necesarias para avanzar a la siguiente etapa.

### Hito 01 — Base funcional y generación de QR
**Periodo objetivo:** Semanas 1–8

**Resultado esperado:** Contar con una primera versión funcional del sistema capaz de registrar estudiantes y generar un código QR único asociado a cada uno, en un formato adecuado para su incorporación a las credenciales institucionales.

**Actividades principales:**
- configuración de la arquitectura inicial;
- implementación de la base de datos;
- desarrollo de la gestión básica de estudiantes;
- generación y asociación de códigos QR;
- validación de unicidad e integridad de los identificadores;
- pruebas funcionales del flujo de generación;
- generación de una muestra de códigos para validación con la institución.

**KPIs:**
- 100 % de los estudiantes de prueba con un QR único asociado;
- 0 identificadores duplicados durante las pruebas;
- 100 % de los QR generados correctamente legibles;
- 100 % de los QR correctamente asociados con su estudiante;
- generación de los QR dentro del plazo de 6-8 semanas;
- aprobación de la institución para iniciar el proceso de producción de credenciales.

### Hito 02 — Sistema web integrado
**Periodo objetivo:** Semanas 8–11

**Resultado esperado:** Contar con una versión web integrada que permita administrar estudiantes, usuarios, familiares e identificadores, con autenticación y control de acceso de acuerdo con los roles definidos.

**Actividades principales:**
- consolidación de los módulos de gestión;
- implementación de autenticación;
- implementación de roles y permisos;
- integración de módulos con la base de datos;
- desarrollo del panel administrativo;
- pruebas funcionales y de integración.

**KPIs:**
- 100 % de los módulos definidos para esta etapa integrados;
- 100 % de los roles definidos con permisos funcionales;
- 100 % de las operaciones críticas con datos persistentes;
- 0 errores críticos abiertos al cierre del hito;
- 100 % de los casos de prueba críticos ejecutados.

### Hito 03 — Backend, API y control de asistencia
**Periodo objetivo:** Semanas 11–14

**Resultado esperado:** Contar con una infraestructura funcional de backend y API que permita implementar el registro y consulta de asistencia mediante códigos QR, utilizando una fuente centralizada de información y reglas de negocio consistentes.

**Actividades principales:**
- consolidación del backend y API;
- implementación de las reglas de negocio de asistencia;
- lectura y validación de códigos QR;
- identificación del estudiante y grupo correspondiente;
- registro de fecha y hora;
- determinación del estado de asistencia;
- prevención de registros inválidos o duplicados;
- creación del registro diario de asistencia por grupo;
- consulta de asistencia;
- pruebas de integración entre API y base de datos;
- definición de los servicios necesarios para su posterior consumo desde la aplicación móvil.

**KPIs:**
- 100 % de las lecturas válidas asociadas al estudiante correcto;
- 100 % de los registros asociados al grupo correcto;
- 100 % de los registros almacenados con fecha y hora;
- 0 registros asociados a estudiantes inexistentes;
- 0 duplicados en los escenarios definidos;
- 100 % de los casos críticos de asistencia superados.

### Hito 04 — Aplicación móvil operativa
**Periodo objetivo:** Semanas 14–17

**Resultado esperado:** Contar con una primera versión funcional de la aplicación móvil integrada con la API de SIGE, capaz de ejecutar las operaciones móviles prioritarias de asistencia y reportes de acuerdo con los permisos definidos para cada rol.

**Actividades principales:**
- configuración del proyecto móvil;
- implementación de autenticación;
- integración con la API;
- implementación del escaneo y validación de QR;
- registro de asistencia;
- consulta del resultado del registro;
- registro de reportes por docentes;
- consulta de reportes;
- consulta y filtrado de reportes por prefectos;
- canalización de reportes;
- implementación de control de permisos;
- manejo de errores de comunicación;
- pruebas con dispositivos representativos;
- validación de comunicación entre aplicación móvil, API y base de datos.

**KPIs:**
- 100 % de las funciones móviles críticas implementadas;
- 100 % de los roles móviles definidos con permisos funcionales;
- 100 % de los registros móviles válidos almacenados correctamente;
- ≥ 99 % de lecturas correctas de QR durante las pruebas;
- 100 % de los reportes de prueba enviados desde la aplicación recibidos correctamente;
- 100 % de las funciones críticas comunicadas mediante la API institucional;
- 0 errores críticos abiertos al cierre del hito.

### Hito 05 — Servidor local e infraestructura institucional
**Periodo objetivo:** Semanas 17–19

**Resultado esperado:** Contar con el entorno local de operación de SIGE configurado en una computadora proporcionada por la institución y conectado a la red institucional, permitiendo que la plataforma web y la aplicación móvil accedan a los servicios internos del sistema sin depender de Internet para las funciones que no requieran servicios externos.

**Actividades principales:**
- preparación de la computadora destinada como servidor;
- instalación y configuración del entorno de ejecución;
- despliegue del backend y API;
- configuración de PostgreSQL;
- configuración de la red local;
- conexión de la plataforma web con el servidor local;
- conexión de la aplicación móvil con el servidor local;
- configuración de mecanismos básicos de respaldo;
- prueba de recuperación de la base de datos;
- pruebas de operación sin conexión a Internet;
- identificación de funciones que requieren servicios externos;
- documentación básica de operación y recuperación;
- validación con la infraestructura real de la institución.

**KPIs:**
- 100 % de los servicios internos desplegados correctamente;
- 100 % de las conexiones web/API funcionando dentro de la red local;
- 100 % de las conexiones móvil/API funcionando dentro de la red local;
- 100 % de los procesos internos prioritarios ejecutables sin Internet;
- 100 % de los respaldos de prueba recuperados correctamente;
- 100 % de los servicios críticos documentados;
- 0 errores críticos abiertos al cierre del hito.

### Hito 06 — Validación con usuarios y operación piloto
**Periodo objetivo:** Semanas 19–22

**Resultado esperado:** Validar la facilidad de uso, funcionamiento y comportamiento del sistema mediante pruebas con estudiantes y personal escolar en un entorno representativo de su utilización real.

**Actividades principales:**
- pruebas de usabilidad con estudiantes;
- pruebas operativas con personal escolar;
- simulación de jornadas de registro de asistencia;
- identificación y documentación de errores;
- recopilación de retroalimentación;
- ajustes derivados de las pruebas;
- nueva ronda de validación.

**KPIs:**
- participación de una muestra definida de estudiantes y personal;
- ≥ 90 % de las tareas principales completadas correctamente por los participantes;
- ≥ 80 % de valoración positiva de usabilidad;
- 100 % de errores críticos identificados corregidos antes de avanzar;
- 100 % de escenarios críticos de uso validados;
- registro y análisis del 100 % de la retroalimentación recopilada.

### Hito 07 — Plataforma integral validada
**Periodo objetivo:** Semanas 22–23

**Resultado esperado:** Contar con una versión integrada de SIGE que permita ejecutar de principio a fin los procesos prioritarios de gestión de estudiantes, asistencia, reportes y comunicación, incluyendo la operación mediante plataforma web y aplicación móvil, el historial diario de asistencia por grupo, la consulta individual de asistencia, la justificación autorizada de faltas y el flujo completo de reportes entre docentes, prefectos, personal administrativo y familiares.

**Actividades principales:**
- implementación del historial diario de asistencia por grupo;
- implementación de consulta histórica de asistencia por estudiante;
- implementación de los estados asistió, falta, llegó tarde y falta justificada;
- implementación del flujo de justificación de faltas por personal autorizado;
- implementación del registro de trazabilidad de las modificaciones de asistencia;
- implementación de consultas de asistencia aplicables a procesos de evaluación académica;
- integración de la aplicación móvil para el registro de reportes docentes;
- implementación de consulta y filtrado de reportes para prefectos desde dispositivos móviles;
- implementación de canalización de reportes desde prefectura hacia personal administrativo;
- integración de la aplicación móvil con los mismos mecanismos de autenticación, permisos y reglas de negocio del sistema web;
- pruebas de integración entre plataforma web, aplicación móvil, API, servidor local y base de datos.

**KPIs:**
- 100 % de los módulos incluidos en la versión final integrados;
- 100 % de los flujos prioritarios ejecutables de principio a fin;
- 100 % de las funcionalidades críticas con pruebas documentadas;
- 0 errores críticos abiertos;
- ≥ 95 % de los casos de prueba críticos aprobados.

### Hito 08 — Preparación para operación
**Periodo objetivo:** Semanas 23–24

**Resultado esperado:** Disponer de una versión estable, documentada y preparada para su utilización en un entorno real o piloto, con los mecanismos de seguridad, respaldo, validación y control necesarios.

**Actividades principales:**
- pruebas finales de aceptación;
- pruebas de seguridad y control de acceso;
- validación de respaldos y recuperación;
- corrección de errores finales;
- documentación técnica y operativa;
- preparación del entorno de despliegue;
- capacitación inicial de los usuarios designados;
- entrega formal del sistema.

**KPIs:**
- 100 % de los criterios de aceptación cumplidos;
- 100 % de los roles y permisos validados;
- 100 % de los respaldos y procedimientos de recuperación probados;
- 100 % de los procesos prioritarios validados;
- 0 errores críticos abiertos al momento de la entrega;
- 100 % de los entregables documentados y entregados;
- aprobación formal de la versión final por parte de la institución.

### Criterio de avance entre hitos

El avance hacia un nuevo nivel de madurez estará condicionado al cumplimiento de los criterios de aceptación y KPIs establecidos para el hito anterior. Cuando un hito no alcance los criterios definidos, las actividades de corrección y validación correspondientes deberán priorizarse antes de continuar con funcionalidades que dependan directamente de dicho resultado.

La escala de madurez funcionará como mecanismo de seguimiento y toma de decisiones del proyecto, sin sustituir la planificación detallada de actividades, dependencias y recursos establecida posteriormente mediante la EDT/WBS y el cronograma.

### Matriz de KPIs

La siguiente matriz consolida los indicadores definidos para cada hito del proyecto. Su propósito es facilitar el seguimiento del avance, cumplimiento y nivel de madurez del sistema durante la ejecución del proyecto.

| ID | Hito | KPI | Meta / criterio |
|---|---|---|---|
| KPI01 | Hito 01 — Base funcional y generación de QR | Estudiantes de prueba con QR único asociado | 100 % |
| KPI02 | Hito 01 — Base funcional y generación de QR | Identificadores duplicados durante las pruebas | 0 |
| KPI03 | Hito 01 — Base funcional y generación de QR | QR generados correctamente legibles | 100 % |
| KPI04 | Hito 01 — Base funcional y generación de QR | QR correctamente asociados con su estudiante | 100 % |
| KPI05 | Hito 01 — Base funcional y generación de QR | Generación de QR dentro del plazo establecido | Máximo 6 semanas |
| KPI06 | Hito 01 — Base funcional y generación de QR | Aprobación institucional para iniciar producción de credenciales | Aprobado |
| KPI07 | Hito 02 — Sistema web integrado | Módulos definidos para la etapa integrados | 100 % |
| KPI08 | Hito 02 — Sistema web integrado | Roles definidos con permisos funcionales | 100 % |
| KPI09 | Hito 02 — Sistema web integrado | Operaciones críticas con datos persistentes | 100 % |
| KPI10 | Hito 02 — Sistema web integrado | Errores críticos abiertos al cierre del hito | 0 |
| KPI11 | Hito 02 — Sistema web integrado | Casos de prueba críticos ejecutados | 100 % |
| KPI12 | Hito 03 — Backend, API y control de asistencia | Lecturas correctas de QR durante las pruebas | ≥ 99 % |
| KPI13 | Hito 03 — Backend, API y control de asistencia | Lecturas válidas asociadas al estudiante correcto | 100 % |
| KPI14 | Hito 03 — Backend, API y control de asistencia | Registros de asistencia asociados a estudiantes inexistentes | 0 |
| KPI15 | Hito 03 — Backend, API y control de asistencia | Registros de asistencia almacenados con fecha y hora | 100 % |
| KPI16 | Hito 03 — Backend, API y control de asistencia | Registros duplicados en escenarios contemplados por las reglas | 0 |
| KPI17 | Hito 03 — Backend, API y control de asistencia | Casos críticos de asistencia superados | 100 % |
| KPI18 | Hito 03 — Backend, API y control de asistencia | Registros de asistencia asociados al grupo correcto | 100 % |
| KPI19 | Hito 04 — Aplicación móvil operativa | Funciones móviles críticas implementadas | 100 % |
| KPI20 | Hito 04 — Aplicación móvil operativa | Roles móviles con permisos funcionales | 100 % |
| KPI21 | Hito 04 — Aplicación móvil operativa | Registros móviles persistidos correctamente | 100 % |
| KPI22 | Hito 04 — Aplicación móvil operativa | Reportes creados desde la aplicación móvil recibidos correctamente por el prefecto | 100 % |
| KPI23 | Hito 04 — Aplicación móvil operativa | Reportes consultables y filtrables por prefectos desde la aplicación móvil | 100 % |
| KPI24 | Hito 04 — Aplicación móvil operativa | Funciones móviles críticas integradas mediante la API institucional | 100 % |
| KPI25 | Hito 04 — Aplicación móvil operativa | Comunicación móvil/API exitosa durante las pruebas | 100 % |
| KPI26 | Hito 04 — Aplicación móvil operativa | Dispositivos de prueba compatibles | 100 % de la muestra definida |
| KPI27 | Hito 04 — Aplicación móvil operativa | Errores críticos abiertos al cierre del hito | 0 |
| KPI28 | Hito 05 — Servidor local e infraestructura institucional | Servicios internos de SIGE desplegados correctamente | 100 % |
| KPI29 | Hito 05 — Servidor local e infraestructura institucional | Acceso web/API funcionando dentro de la red local | 100 % |
| KPI30 | Hito 05 — Servidor local e infraestructura institucional | Comunicación móvil/API funcionando mediante la red local | 100 % |
| KPI31 | Hito 05 — Servidor local e infraestructura institucional | Procesos internos prioritarios ejecutables sin Internet | 100 % |
| KPI32 | Hito 05 — Servidor local e infraestructura institucional | Respaldos de prueba recuperados correctamente | 100 % |
| KPI33 | Hito 05 — Servidor local e infraestructura institucional | Servicios críticos documentados | 100 % |
| KPI34 | Hito 05 — Servidor local e infraestructura institucional | Escenarios críticos de recuperación superados | 100 % |
| KPI35 | Hito 06 — Integración y operación piloto | Participación de una muestra definida de estudiantes y personal | Cumplida |
| KPI36 | Hito 06 — Integración y operación piloto | Tareas principales completadas correctamente por participantes | ≥ 90 % |
| KPI37 | Hito 06 — Integración y operación piloto | Valoración positiva de usabilidad | ≥ 80 % |
| KPI38 | Hito 06 — Integración y operación piloto | Errores críticos identificados corregidos antes de avanzar | 100 % |
| KPI39 | Hito 06 — Integración y operación piloto | Escenarios críticos de uso validados | 100 % |
| KPI40 | Hito 06 — Integración y operación piloto | Retroalimentación recopilada y analizada | 100 % |
| KPI41 | Hito 06 — Integración y operación piloto | Módulos principales comunicándose correctamente entre sí | 100 % |
| KPI42 | Hito 06 — Integración y operación piloto | Flujos prioritarios ejecutables de principio a fin | 100 % |
| KPI43 | Hito 06 — Integración y operación piloto | Operación del sistema validada ante pérdida de Internet con servidor local disponible | 100 % de escenarios definidos |
| KPI44 | Hito 06 — Integración y operación piloto | Recuperación del sistema validada después de una interrupción del servidor local | 100 % de escenarios definidos |
| KPI45 | Hito 07 — Plataforma integral validada | Reportes clasificados por tipo | 100 % |
| KPI46 | Hito 07 — Plataforma integral validada | Reportes con nivel de gravedad registrado | 100 % |
| KPI47 | Hito 07 — Plataforma integral validada | Reportes con observación dentro del límite establecido | 100 % |
| KPI48 | Hito 07 — Plataforma integral validada | Reportes con opciones del reglamento seleccionadas | 100 % |
| KPI49 | Hito 07 — Plataforma integral validada | Reportes enviados correctamente al prefecto | 100 % |
| KPI50 | Hito 07 — Plataforma integral validada | Reportes filtrados y canalizados por el prefecto conforme al flujo definido | 100 % |
| KPI51 | Hito 07 — Plataforma integral validada | Reportes revisados por personal administrativo antes de su comunicación a la familia | 100 % |
| KPI52 | Hito 07 — Plataforma integral validada | Reportes comunicados a la familia únicamente después de la revisión administrativa | 100 % |
| KPI53 | Hito 07 — Plataforma integral validada | Reportes con trazabilidad completa del flujo | 100 % |
| KPI54 | Hito 07 — Plataforma integral validada | Módulos incluidos en la versión final integrados | 100 % |
| KPI55 | Hito 07 — Plataforma integral validada | Flujos prioritarios ejecutables de principio a fin | 100 % |
| KPI56 | Hito 07 — Plataforma integral validada | Funcionalidades críticas con pruebas documentadas | 100 % |
| KPI57 | Hito 07 — Plataforma integral validada | Casos de prueba críticos aprobados | ≥ 95 % |
| KPI58 | Hito 07 — Plataforma integral validada | Errores críticos abiertos al cierre del hito | 0 |
| KPI59 | Hito 07 — Plataforma integral validada | Grupos de prueba con historial diario de asistencia generado correctamente | 100 % |
| KPI60 | Hito 07 — Plataforma integral validada | Estudiantes de prueba con estado diario de asistencia correctamente determinado | 100 % |
| KPI61 | Hito 07 — Plataforma integral validada | Estados de asistencia correctamente diferenciados entre asistió, falta, llegada tarde y falta justificada | 100 % |
| KPI62 | Hito 07 — Plataforma integral validada | Historial individual de asistencia consultable para estudiantes de prueba | 100 % |
| KPI63 | Hito 07 — Plataforma integral validada | Faltas justificadas registradas por usuarios autorizados | 100 % |
| KPI64 | Hito 07 — Plataforma integral validada | Modificaciones de asistencia con trazabilidad registrada | 100 % |
| KPI65 | Hito 08 — Preparación para operación y entrega | Criterios de aceptación cumplidos | 100 % |
| KPI66 | Hito 08 — Preparación para operación y entrega | Roles y permisos validados | 100 % |
| KPI67 | Hito 08 — Preparación para operación y entrega | Respaldos y procedimientos de recuperación probados | 100 % |
| KPI68 | Hito 08 — Preparación para operación y entrega | Procesos prioritarios validados | 100 % |
| KPI69 | Hito 08 — Preparación para operación y entrega | Errores críticos abiertos al momento de la entrega | 0 |
| KPI70 | Hito 08 — Preparación para operación y entrega | Entregables documentados y entregados | 100 % |
| KPI71 | Hito 08 — Preparación para operación y entrega | Aprobación de la versión final por parte de la institución | Aprobada |

---

## 12. Matriz de riesgos y supuestos

| ID | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R-01 | Falta de disponibilidad o retraso en autorización institucional para actividades presenciales | Alta | Alto | Calendarizar reuniones clave con 2 semanas de anticipación; definir punto de contacto único en la institución. |
| R-02 | Limitaciones o fallos del servicio de correo electrónico utilizado para la comunicación con familiares | Media | Medio | Mantener la generación de la comunicación dentro de SIGE aunque el envío externo no esté disponible; registrar el estado del envío cuando sea técnicamente posible; identificar y documentar los límites del servicio utilizado. |
| R-03 | Datos históricos de estudiantes no estructurados o incompletos al momento de la carga inicial | Media | Medio | Excluir explícitamente del alcance la transformación de datos históricos; la institución deberá entregar los datos limpios y estructurados requeridos para la carga inicial. |
| R-04 | Capacidad de 10 h/semana por integrante insuficiente frente al alcance total definido | Alta | Alto | Aplicar el principio de control de cambios: cualquier hito en riesgo se replanteará en alcance, no en calidad ni en horas no pagadas. |
| R-05 | Rotación o indisponibilidad de alguno de los dos integrantes del equipo | Baja | Alto | Mantener documentación progresiva; versionar código y decisiones técnicas en GitHub desde el inicio; distribuir el conocimiento de los componentes críticos entre ambos integrantes. |
| R-06 | Tratamiento inadecuado de datos personales de menores de edad | Baja | Alto | Aplicar las medidas de protección de datos definidas para el proyecto; limitar los campos recolectados a los estrictamente necesarios; establecer permisos de acceso según el rol. |
| R-07 | Ambigüedad en la división de responsabilidades entre Next.js y Django que genere retrabajo o arquitectura inconsistente | Media | Medio | Mantener definida la división de responsabilidades: Next.js como frontend y Django como backend/API; documentar las interfaces de comunicación entre ambos componentes. |
| R-08 | Cobertura insuficiente o inestabilidad de la red Wi-Fi institucional para los dispositivos móviles | Media | Alto | Realizar pruebas de conectividad en las áreas donde se utilizará la aplicación; identificar zonas críticas; validar la cobertura y estabilidad antes de la operación piloto. |
| R-09 | Indisponibilidad temporal del servidor local durante la jornada escolar | Media | Alto | Implementar procedimientos básicos de recuperación; supervisar el estado del servidor; realizar respaldos periódicos; documentar un procedimiento de contingencia para interrupciones del servicio. |
| R-10 | Inconsistencias entre registros realizados desde la aplicación móvil y la plataforma web | Media | Alto | Utilizar una única API, fuente central de datos y reglas de negocio; realizar pruebas de integración entre aplicación móvil, plataforma web, backend y base de datos. |
| R-11 | Errores en la determinación del estado diario de asistencia | Media | Alto | Definir formalmente las reglas para asistió, falta, llegada tarde y falta justificada; implementar validaciones y pruebas con casos límite antes de la operación piloto. |
| R-12 | Modificación no autorizada de registros históricos de asistencia o justificaciones | Baja | Alto | Implementar permisos por rol, registro de auditoría de cambios y validación de las operaciones de modificación. |
| R-13 | Compatibilidad insuficiente de la aplicación móvil con los dispositivos utilizados por la institución | Media | Medio | Definir durante la planificación las plataformas y versiones mínimas soportadas y realizar pruebas con una muestra representativa de dispositivos. |
| R-14 | Fallo físico o pérdida de disponibilidad del equipo utilizado como servidor local | Media | Alto | Definir un procedimiento de recuperación; realizar respaldos periódicos; documentar la reinstalación de los servicios; verificar periódicamente la integridad de las copias de seguridad. |
| R-15 | Pérdida de conectividad de la red local durante la jornada escolar | Media | Alto | Realizar pruebas de cobertura y estabilidad; diferenciar fallos de Internet de fallos de la red local; documentar procedimientos de contingencia; validar estos escenarios durante el piloto. |
| R-16 | El alcance de la aplicación móvil excede la capacidad disponible del equipo de desarrollo | Media | Alto | Priorizar únicamente las funciones móviles definidas como críticas; utilizar control de cambios; limitar las plataformas y versiones soportadas; validar un conjunto definido de dispositivos. |

---

## 13. Criterio de aceptación del proyecto

El proyecto se considerará exitoso cuando exista una versión funcional y validada del sistema que permita ejecutar de principio a fin los procesos prioritarios definidos en el alcance mediante la infraestructura web y móvil contemplada, manteniendo una fuente centralizada de información en el servidor local institucional y permitiendo registrar, consultar y administrar la asistencia y los reportes escolares de acuerdo con los roles definidos.

La solución deberá demostrar interoperabilidad entre la aplicación móvil, la plataforma web, la API, la base de datos y el servidor local, así como trazabilidad de las operaciones críticas y mecanismos básicos de respaldo y recuperación.

### 13.1. Funcionalidad

La versión final deberá demostrar que las funcionalidades y procesos prioritarios contemplados en el alcance se encuentran implementados, integrados y operativos.

La aceptación de la funcionalidad deberá sustentarse principalmente en:

- **KPI-07:** 100 % de los módulos definidos para la etapa correspondiente deberán encontrarse integrados.
- **KPI-08:** 100 % de los roles definidos deberán contar con permisos funcionales.
- **KPI-09:** 100 % de las operaciones críticas deberán mantener datos persistentes.
- **KPI-13:** 100 % de las lecturas válidas de QR deberán asociarse con el estudiante correspondiente.
- **KPI-15:** 100 % de los registros de asistencia deberán conservar fecha y hora.
- **KPI-16:** 0 % de los registros generados en escenarios de prueba deberán corresponder a duplicados no permitidos.
- **KPI-17:** 100 % de los casos críticos de asistencia deberán resultar satisfactorios.
- **KPI-19:** 100 % de las funciones críticas definidas para la aplicación móvil deberán encontrarse operativas.
- **KPI-21:** 100 % de los registros generados desde la aplicación móvil deberán persistir correctamente.
- **KPI-25:** 100 % de las funciones críticas de consulta y filtrado definidas para prefectura deberán encontrarse disponibles.
- **KPI-26:** 100 % de las funciones móviles críticas deberán operar mediante la API institucional definida.
- **KPI-27:** 100 % de los casos definidos de comunicación entre la aplicación móvil y la API deberán resultar satisfactorios.
- **KPI-42:** 100 % de los procesos prioritarios deberán poder ejecutarse de principio a fin.
- **KPI-55:** 100 % de los estados de asistencia deberán diferenciar correctamente entre asistió, falta, llegó tarde y falta justificada.
- **KPI-58:** 100 % de los registros de asistencia modificados deberán conservar trazabilidad.
- **KPI-66:** 100 % de los procedimientos de respaldo y recuperación deberán haber sido probados.
- **KPI-68:** 100 % de los procesos prioritarios deberán encontrarse validados antes de la entrega.

Asimismo, deberá verificarse que el flujo de generación, asociación y validación de códigos QR se encuentre operativo, de acuerdo con los resultados establecidos en los KPI-01 a KPI-06.

### 13.2. Calidad y pruebas

La calidad de la versión final deberá demostrarse mediante la ejecución documentada de las pruebas funcionales, de integración y de los escenarios críticos definidos durante el proyecto.

La aceptación deberá considerar:

- **KPI-11:** 100 % de los casos de prueba críticos definidos para la etapa deberán haber sido ejecutados.
- **KPI-17:** 100 % de los casos críticos de asistencia deberán resultar satisfactorios.
- **KPI-26:** 100 % de las funciones móviles críticas deberán utilizar la API, reglas de negocio y mecanismos de autorización definidos para el sistema.
- **KPI-30:** 100 % de los escenarios críticos definidos para la operación mediante servidor local y dispositivos móviles deberán ser superados.
- **KPI-39:** 100 % de los escenarios definidos para la operación con pérdida de Internet y servidor local disponible deberán ser superados.
- **KPI-40:** 100 % de los escenarios definidos para la recuperación después de una interrupción del servidor local deberán ser superados.
- **KPI-61:** al menos el 95 % de los casos de prueba críticos de la versión final deberán resultar satisfactorios.

Las pruebas deberán encontrarse documentadas y deberán proporcionar evidencia verificable del comportamiento de los módulos, las integraciones y los procesos prioritarios.

### 13.3. Validación con usuarios

La validación con usuarios deberá demostrar que el sistema puede ser utilizado correctamente en un entorno representativo por los usuarios definidos para el proyecto.

La aceptación de esta etapa deberá sustentarse en:

- **KPI-35:** cumplimiento de la participación de la muestra de estudiantes y personal escolar definida para las pruebas.
- **KPI-36:** al menos el 90 % de las tareas principales deberá completarse correctamente.
- **KPI-37:** la evaluación de usabilidad deberá alcanzar al menos el 80 % de valoración positiva.
- **KPI-38:** 100 % de los escenarios críticos de uso deberán encontrarse validados.
- **KPI-39:** 100 % de los escenarios definidos para la operación con pérdida de Internet y servidor local disponible deberán ser superados.
- **KPI-40:** 100 % de los escenarios definidos para la recuperación después de una interrupción del servidor local deberán ser superados.

Asimismo, deberá registrarse y analizarse la retroalimentación obtenida durante las pruebas con usuarios, de acuerdo con el KPI-40 correspondiente a la matriz vigente.

### 13.4. Datos, seguridad y operación

La versión final deberá demostrar que la información se almacena correctamente, que el acceso al sistema se encuentra controlado y que existen mecanismos básicos para preservar y recuperar la información.

La aceptación deberá sustentarse en:

- **KPI-08:** 100 % de los roles definidos deberán contar con permisos funcionales.
- **KPI-09:** 100 % de las operaciones críticas deberán mantener datos persistentes.
- **KPI-29:** 100 % de los servicios internos definidos deberán encontrarse desplegados en el servidor local institucional.
- **KPI-30:** 100 % de las conexiones web/API definidas mediante la red local deberán resultar satisfactorias.
- **KPI-31:** 100 % de las conexiones aplicación móvil/API mediante la red local deberán resultar satisfactorias.
- **KPI-32:** 100 % de los procesos internos prioritarios definidos deberán poder ejecutarse sin conexión a Internet cuando el servidor y la red local se encuentren disponibles.
- **KPI-33:** 100 % de los respaldos de prueba deberán poder recuperarse correctamente.
- **KPI-34:** 100 % de los servicios críticos deberán contar con documentación correspondiente.
- **KPI-66:** 100 % de los procedimientos de respaldo y recuperación deberán haber sido probados.
- **KPI-67:** 100 % de los procesos prioritarios deberán encontrarse validados.
- **KPI-70:** 100 % de los entregables deberán encontrarse documentados y entregados.

Las operaciones críticas deberán generar registros verificables y deberá comprobarse la integridad de la información almacenada. La versión final deberá encontrarse desplegada o preparada para su despliegue en el entorno definido por la institución.

### 13.5. Identificación mediante códigos QR

Debido a que la generación de identificadores QR constituye una necesidad prioritaria del proyecto, su aceptación deberá verificarse específicamente mediante los indicadores correspondientes al primer hito:

- **KPI-01:** 100 % de los estudiantes incluidos en la prueba deberán contar con un QR único.
- **KPI-02:** deberán existir 0 identificadores duplicados.
- **KPI-03:** 100 % de los códigos QR deberán ser correctamente legibles.
- **KPI-04:** 100 % de los códigos deberán encontrarse correctamente asociados con su estudiante.
- **KPI-05:** la generación de los códigos deberá completarse dentro del plazo máximo establecido de seis semanas.
- **KPI-06:** deberá existir aprobación institucional para iniciar la producción de las credenciales.

El cumplimiento de estos indicadores permitirá considerar validada la primera versión funcional del mecanismo de identificación y habilitar el avance hacia las etapas posteriores del proyecto.

### 13.6. Control histórico de asistencia

La aceptación del módulo de asistencia deberá demostrar que el sistema permite registrar, conservar, consultar y administrar la asistencia escolar de manera histórica y estructurada.

Deberá verificarse:

- **KPI-13:** 100 % de las lecturas válidas de QR deberán asociarse con el estudiante correcto.
- **KPI-14:** 100 % de las lecturas válidas deberán asociarse con el grupo correspondiente.
- **KPI-15:** 100 % de los registros deberán conservar fecha y hora.
- **KPI-16:** no deberán existir duplicados no permitidos en los escenarios contemplados.
- **KPI-56:** 100 % de los grupos de prueba deberán contar con historial diario correctamente generado.
- **KPI-57:** 100 % de los estudiantes de prueba deberán contar con un estado de asistencia correctamente determinado.
- **KPI-58:** el sistema deberá diferenciar correctamente entre asistió, falta, llegó tarde y falta justificada.
- **KPI-59:** deberá ser posible consultar el historial individual de asistencia de los estudiantes de prueba.
- **KPI-60:** las faltas justificadas deberán poder registrarse mediante usuarios con autorización.
- **KPI-61:** las modificaciones realizadas sobre registros de asistencia deberán conservar trazabilidad.

La aceptación deberá considerar tanto la consulta de asistencia por grupo y fecha como la consulta individual por estudiante, garantizando que ambas representaciones provengan de la misma información almacenada en el sistema.

La información de asistencia podrá utilizarse como insumo para procesos de evaluación académica de acuerdo con las reglas definidas por la institución. La fórmula o ponderación específica de dicha evaluación será establecida durante la definición de requisitos y criterios de aceptación específicos.

### 13.7. Aplicación móvil

La aplicación móvil deberá demostrar interoperabilidad con la plataforma web, backend, API, base de datos y servidor local institucional.

La aceptación deberá sustentarse en:

- **KPI-19:** 100 % de las funciones críticas definidas para la aplicación móvil deberán encontrarse operativas.
- **KPI-20:** 100 % de los roles definidos para la aplicación móvil deberán contar con los permisos correspondientes.
- **KPI-21:** 100 % de los registros generados desde la aplicación móvil deberán persistir correctamente.
- **KPI-22:** 100 % de los reportes de prueba creados desde la aplicación móvil deberán llegar correctamente al prefecto correspondiente.
- **KPI-23:** 100 % de los reportes definidos para consulta y filtrado por prefectura deberán encontrarse disponibles.
- **KPI-24:** 100 % de las funciones móviles críticas deberán operar mediante la API institucional definida.
- **KPI-25:** 100 % de las comunicaciones definidas entre la aplicación móvil y la API deberán resultar satisfactorias.
- **KPI-26:** 100 % de los dispositivos incluidos en la muestra definida deberán ser compatibles con la aplicación.
- **KPI-30:** 100 % de los escenarios críticos definidos para la operación mediante servidor local y dispositivos móviles deberán ser superados.

La aplicación móvil no deberá mantener una base de datos independiente de los registros institucionales, salvo mecanismos técnicos temporales que sean definidos durante la arquitectura y garanticen posteriormente la consistencia de la información.

Los registros generados desde la aplicación deberán utilizar la misma fuente central de información, API, reglas de negocio y mecanismos de autorización definidos para la plataforma institucional.

### 13.8. Documentación y entrega

La entrega deberá incluir la documentación y las evidencias necesarias para demostrar el cumplimiento de los criterios establecidos durante el proyecto.

Como parte de la aceptación final deberán encontrarse documentados y entregados:

- los resultados y evidencias de las pruebas realizadas;
- la documentación técnica mínima del sistema y su arquitectura;
- la documentación básica para los usuarios finales;
- los procedimientos básicos de operación, respaldo y recuperación;
- la evidencia correspondiente al cumplimiento de los KPIs aplicables;
- la demostración integral de los procesos prioritarios.

El cumplimiento de la entrega deberá verificarse mediante:

- **KPI-64:** 100 % de las funcionalidades críticas deberán contar con pruebas documentadas.
- **KPI-66:** 100 % de los procedimientos de respaldo y recuperación deberán haber sido probados.
- **KPI-70:** 100 % de los entregables deberán encontrarse documentados y entregados.

### 13.9. Aceptación institucional

La aceptación definitiva requerirá la revisión y aprobación de la versión final por parte de los responsables designados por la institución.

La aprobación institucional deberá sustentarse en:

- **KPI-06:** aprobación institucional para iniciar la producción de credenciales en la primera etapa.
- **KPI-71:** aprobación institucional de la versión final.
- Cumplimiento de los KPIs aplicables a los hitos precedentes.
- Evidencia de que los procesos prioritarios pueden ejecutarse correctamente.
- Evidencia de que el sistema cumple los requisitos acordados y se encuentra preparado para su utilización en un entorno real o piloto.

### 13.10. Regla de aceptación

El cumplimiento de los criterios de aceptación se determinará mediante la Matriz consolidada de KPIs, considerando los valores objetivo establecidos para cada indicador.

Un hito podrá considerarse cumplido únicamente cuando los KPIs correspondientes alcancen sus valores objetivo y exista evidencia verificable de su cumplimiento.

La aceptación del proyecto completo requerirá, como mínimo:

1. el cumplimiento de los criterios establecidos para cada hito;
2. la validación de los procesos prioritarios;
3. la ausencia de errores críticos abiertos al momento de la entrega;
4. la entrega de la documentación y evidencias correspondientes; y
5. la aprobación institucional de la versión final, conforme al KPI-35.

Los criterios específicos de aceptación de cada módulo, requisito, historia de usuario y entregable se desarrollarán durante la fase de planificación detallada y deberán mantener trazabilidad con los KPIs, pruebas y criterios de aceptación definidos para el proyecto.

---

## 14. Cronograma, lista de actividades y Diagrama de Gantt

[Ver hoja de Google Sheets con el Diagrama de Gantt y la Estructura WBS Nivel 2 y 3](https://docs.google.com/spreadsheets/d/1BXwPb_fENL0L7ktRKCCPXcXTgWyHHFsb3Zkel_jxOvI/edit?usp=sharing)

---

## 15. Próximos documentos de planificación

Esta acta constituye únicamente el punto de partida del proyecto.

A partir de ella se desarrollarán, en este orden:

1. Requisitos funcionales y no funcionales
2. Historias de usuario
3. Criterios de aceptación específicos por requisito
4. Arquitectura del sistema
5. Modelo de datos
6. Estimación de esfuerzo
7. Plan de pruebas y calidad
8. Plan de despliegue
9. Plan de mantenimiento y evolución

---

## 16. Estado del documento

**Estado:** Acta constitutiva para aprobación.

El presente documento establece las bases generales del proyecto, incluyendo su propósito, objetivos, alcance, producto esperado, criterios generales de éxito, hitos, niveles de madurez tecnológica, KPIs y criterios generales de aceptación.

La aprobación de esta acta autorizará el inicio formal de la fase de planificación detallada, durante la cual se desarrollarán y documentarán los requisitos funcionales y no funcionales, historias de usuario, arquitectura del sistema, modelo de datos, EDT/WBS, estimación de esfuerzo, dependencias, ruta crítica, cronograma, matriz de riesgos, plan de pruebas, plan de despliegue y demás elementos necesarios para la ejecución del proyecto.

Los detalles técnicos, estimaciones, fechas específicas de actividades y demás elementos de planificación podrán ser refinados durante dicha fase, siempre que se mantengan consistentes con el propósito, objetivos, alcance y restricciones establecidos en esta acta.

Cualquier modificación sustancial al alcance aprobado deberá someterse al proceso de evaluación y aprobación correspondiente.
