# **ACTA CONSTITUTIVA DEL PROYECTO**

## **Sistema Integral de Gestión Escolar**

**1\. Identificación del proyecto**

### **1.1 Nombre provisional**

**Sistema Integral de Gestión Escolar**

Nombre técnico provisional del producto:

**SIGE**

## **2\. Propósito del proyecto**

El proyecto tiene como propósito establecer una infraestructura tecnológica centralizada, escalable y sostenible que reduzca la dependencia de procesos manuales, facilite el acceso y gestión de la información escolar y siente las bases para la incorporación progresiva de nuevas herramientas y servicios digitales que atiendan las necesidades de la institución. 

## **3\. Problema que se busca resolver**

La institución requiere una solución tecnológica que permita modernizar y centralizar diversos procesos de gestión escolar que actualmente pueden depender de herramientas y procedimientos independientes o manuales.

Esta situación dificulta la organización de la información, incrementar la posibilidad de errores, limitar la trazabilidad de los procesos y hacer más compleja la consulta y generación de información útil para la toma de decisiones.

El proyecto busca atender esta necesidad mediante el desarrollo de una plataforma que integre progresivamente los principales procesos relacionados con:

* administración y consulta de información de estudiantes;  
* identificación de estudiantes mediante códigos QR asociados a sus credenciales;  
* registro y consulta de asistencia;  
* registro y seguimiento de incidencias y comportamiento;  
* generación de reportes escolares;  
* comunicación de información relevante con los familiares;  
* incorporación futura de herramientas y servicios adicionales de gestión escolar.

La solución deberá permitir que estas funcionalidades se desarrollen de manera progresiva sobre una misma infraestructura tecnológica, priorizando aquellas necesidades que representen mayor valor operativo para la institución.

## **4\. Objetivo general**

Desarrollar e implementar una plataforma digital integral para la gestión escolar que permita a la institución centralizar, organizar y automatizar procesos relacionados con la administración de estudiantes, identificación, control de asistencia, seguimiento de incidencias y comportamiento, generación de reportes y comunicación de información relevante a los familiares. 

## **5\. Objetivos específicos**

### **OE-01 — Identificación y códigos QR**

Diseñar, desarrollar y validar un módulo que permita generar un identificador QR único para el 100 % de los estudiantes registrados, asociándolo inequívocamente con su información dentro del sistema y proporcionando los códigos en un formato apto para su incorporación en las credenciales institucionales, dentro de las primeras seis semanas del proyecto.

### **OE-02 — Gestión de estudiantes**

Implementar un módulo que permita registrar, consultar, modificar y administrar la información de los estudiantes, garantizando que el 100 % de los estudiantes registrados cuente con un expediente digital único y asociado a su identificador correspondiente antes de la puesta en operación del sistema.

### **OE-03 — Gestión de usuarios y permisos**

Implementar un sistema de autenticación y autorización que permita gestionar el acceso a la plataforma mediante los roles definidos por la institución, asegurando que cada usuario pueda acceder únicamente a las funciones y datos correspondientes a sus permisos antes de la puesta en operación del sistema.

### **OE-04 — Registro de asistencia**

Desarrollar e implementar un módulo de control de asistencia que permita registrar automáticamente la entrada y salida de los estudiantes mediante el escaneo de sus códigos QR, almacenando cada registro con información de identificación, fecha y hora, y permitiendo su posterior consulta por parte del personal autorizado.

### **OE-05 — Incidencias y comportamiento**

Implementar un módulo que permita al personal autorizado registrar, consultar, modificar y dar seguimiento a incidencias relacionadas con el comportamiento de los estudiantes, manteniendo un historial asociado a cada estudiante y permitiendo la generación de información consolidada para su consulta.

### **OE-06 — Reportes**

Implementar mecanismos para generar y consultar reportes a partir de la información almacenada en el sistema, incluyendo al menos información relacionada con estudiantes, asistencia e incidencias, de acuerdo con las necesidades operativas definidas por la institución.

### **OE-07 — Comunicación con familiares**

Integrar un mecanismo de comunicación automatizada con los familiares de los estudiantes mediante la plataforma de WhatsApp seleccionada por la institución, permitiendo enviar información y reportes previamente definidos y autorizados, una vez que los módulos necesarios para generar dicha información se encuentren operativos.

### **OE-08 — Calidad, seguridad y continuidad**

Implementar mecanismos de validación de datos, control de acceso, protección de información, manejo de errores, pruebas funcionales y respaldo de datos, estableciendo criterios mínimos de calidad y seguridad que deberán cumplirse antes de la puesta en operación de cada módulo.

## **6\. Producto final esperado**

El proyecto deberá producir una **plataforma integral de gestión escolar**, compuesta por los siguientes módulos y componentes principales:

### **6.1. Gestión de estudiantes**

Módulo destinado a centralizar la información básica y administrativa de los estudiantes, permitiendo:

* registrar y modificar datos de identificación, como nombre completo, fecha de nacimiento y fotografía;  
* registrar información escolar, como grado, grupo, ciclo escolar y matrícula;  
* asociar familiares o tutores, incluyendo sus datos de contacto y relación con el estudiante;  
* consultar el expediente del estudiante;  
* consultar la información relacionada con asistencia e incidencias;  
* administrar el estado del estudiante dentro de la institución, como activo, egresado o dado de baja.

  ### **6.2. Gestión de usuarios y permisos**

Sistema de acceso que permita:

* autenticar usuarios;  
* administrar cuentas;  
* asignar roles y permisos;  
* restringir el acceso a información y funciones según el rol.

  ### **6.3. Identificación y credenciales**

Módulo encargado de generar y administrar la identificación digital de los estudiantes mediante:

* generación de un código QR único por estudiante;  
* asociación del QR con su estudiante correspondiente;  
* consulta y validación del identificador;  
* generación de los códigos en un formato adecuado para su incorporación a las credenciales físicas.

  ### **6.4. Control de asistencia**

Módulo que utilice los códigos QR como mecanismo de identificación para:

* leer y validar códigos;  
* registrar asistencia con fecha y hora;  
* consultar registros;  
* prevenir registros inválidos o duplicados conforme a las reglas establecidas.

  ### **6.5. Incidencias y comportamiento**

Módulo para que el personal autorizado pueda:

* registrar incidencias;  
* consultar y modificar registros;  
* mantener un historial asociado a cada estudiante;  
* dar seguimiento a los reportes realizados.

  ### **6.6. Reportes**

Módulo para:

* registrar y consultar reportes;  
* generar información consolidada sobre estudiantes, asistencia e incidencias;  
* visualizar la información de acuerdo con los permisos del usuario.

Los reportes serán redactados y registrados manualmente por el personal correspondiente; el sistema se encargará de su almacenamiento, organización y consulta.

### **6.7. Comunicación con familiares**

Componente destinado a facilitar la comunicación institucional mediante:

* preparación de información y reportes para envío;  
* integración con el servicio de mensajería seleccionado;  
* envío automatizado de comunicaciones conforme a las condiciones técnicas y comerciales del servicio.

  ### **6.8. Panel administrativo**

Interfaz central para que el personal autorizado pueda:

* administrar usuarios y estudiantes;  
* consultar información;  
* gestionar los módulos disponibles según su rol;  
* acceder a las principales funciones operativas del sistema.

  ### **6.9. Backend, base de datos y API**

Infraestructura de software que proporcione:

* almacenamiento centralizado de la información;  
* lógica de negocio;  
* API para comunicación entre aplicaciones;  
* control de acceso y validación;  
* mecanismos básicos de seguridad, manejo de errores y respaldo.

## **7\. Matriz de alcance**

La siguiente matriz delimita los componentes y funcionalidades contemplados dentro del proyecto, así como aquellos elementos que quedan fuera de su alcance. Esta delimitación busca establecer una base clara para la planificación, desarrollo, validación y aceptación del sistema, evitando la incorporación de funcionalidades no contempladas originalmente.

| Área | Dentro del alcance | Fuera del alcance |
| ----- | ----- | ----- |
| **Gestión de estudiantes** | Registro, consulta, modificación y administración de la información de los estudiantes. | Carga o incorporación masiva de información histórica de estudiantes cuando los datos no se encuentren en archivos estructurados, como Excel o CSV, o cuando requieran limpieza, corrección o transformación adicional antes de poder utilizarse en el sistema.  |
| **Gestión de usuarios** | Registro de usuarios, autenticación, gestión de cuentas y asignación de permisos de acuerdo con los roles definidos por la institución. | Administración de cuentas personales externas a la plataforma o sistemas de identidad institucional no contemplados durante la definición del proyecto. |
| **Gestión de familiares** | Registro y asociación de familiares o responsables con los estudiantes correspondientes y consulta de la información necesaria para los procesos de comunicación. | Gestión de información familiar que no sea necesaria para la operación del sistema. |
| **Identificación mediante QR** | Generación de identificadores QR únicos, asociación con estudiantes, consulta y validación de los códigos y preparación de los mismos para su incorporación en credenciales. | Diseño, fabricación, impresión, distribución o reposición física de las credenciales. |
| **Control de asistencia** | Lectura y validación de códigos QR, registro de asistencia con fecha y hora, consulta de registros y aplicación de reglas para prevenir registros inválidos o duplicados. | Desarrollo de dispositivos físicos especializados para lectura de QR o sistemas biométricos. |
| **Incidencias y comportamiento** | Registro, consulta, modificación y seguimiento de incidencias relacionadas con los estudiantes, así como almacenamiento de su historial. | Automatización de decisiones disciplinarias o evaluación automática del comportamiento de los estudiantes. |
| **Reportes** | Generación, consulta y visualización de reportes relacionados con estudiantes, asistencia e incidencias, redactados y registrados manualmente por los prefectos de acuerdo con los requerimientos definidos por la institución. | Desarrollo de sistemas avanzados de analítica, inteligencia artificial o predicción que no hayan sido definidos dentro de los requerimientos originales. |
| **Panel administrativo** | Panel web para la administración y consulta de la información y funcionalidades disponibles para cada rol. | Personalizaciones independientes para cada usuario que no sean necesarias para la operación general del sistema. |
| **Comunicación con familiares** | Integración con el servicio de mensajería seleccionado para permitir el envío automatizado de información y reportes definidos por la institución. | Costos de servicios externos, campañas masivas, funcionalidades propias de la plataforma de mensajería no relacionadas con el sistema y canales de comunicación adicionales no contemplados. |
| **Backend y API** | Desarrollo de los servicios, API y mecanismos de comunicación necesarios para soportar las aplicaciones y módulos incluidos en el proyecto. | APIs o integraciones con sistemas externos no identificados o aprobados durante la definición del alcance. |
| **Base de datos** | Diseño, implementación y administración de la base de datos necesaria para almacenar la información del sistema. | Almacenamiento de información ajena a los procesos contemplados en el proyecto. |
| **Seguridad y control** | Autenticación, autorización, validación de información, protección de datos, manejo de errores y mecanismos básicos de seguridad y respaldo. | Certificaciones especializadas, auditorías externas de seguridad o infraestructura de seguridad avanzada que no formen parte de los requerimientos acordados. |
| **Pruebas y validación** | Pruebas funcionales, validación de los módulos desarrollados y corrección de errores identificados antes de la puesta en operación. | Pruebas de certificación externa o auditorías independientes no contempladas en el proyecto. |
| **Infraestructura y despliegue** | Configuración de la infraestructura necesaria para poner en operación el sistema dentro del entorno tecnológico definido para el proyecto. | Adquisición de equipos físicos, redes institucionales, servidores físicos u otra infraestructura no especificada como parte del proyecto. |
| **Mantenimiento y evolución** | Corrección de errores derivados de la implementación y ajustes necesarios durante la validación y puesta en operación inicial. | Desarrollo indefinido de nuevas funcionalidades posteriores a la entrega sin un proceso de ampliación o modificación del alcance. |

## **8\. Condiciones y modalidad de ejecución del proyecto**

### **Tiempo**

El proyecto dispone de un máximo de:

**480 horas de trabajo**

distribuidas en:

**24 semanas × 20 horas/semana del equipo.**

### **Recursos humanos**

El desarrollo será realizado por un **equipo de dos personas**, con una disponibilidad conjunta de **20 horas semanales**, equivalente a aproximadamente **10 horas semanales por integrante**.

El equipo será responsable de:

* análisis y levantamiento de requisitos;  
* diseño y arquitectura del sistema;  
* desarrollo frontend y backend;  
* diseño e implementación de la base de datos;  
* pruebas y corrección de errores;  
* documentación;  
* despliegue y validación del producto.

Se contempla adicionalmente la participación de usuarios o representantes de la institución para:

* levantamiento y validación de requisitos;  
* revisión de prototipos y funcionalidades;  
* pruebas de aceptación;  
* retroalimentación sobre el funcionamiento del sistema.

### 

### **Modalidad de trabajo**

Debido a que el desarrollo del proyecto se realizará como parte de un **servicio social**, se propone implementar una **modalidad de trabajo mixta (presencial y virtual)**, buscando aprovechar las ventajas de ambas modalidades sin comprometer las necesidades de levantamiento de información, desarrollo y validación del sistema.

La **modalidad virtual** estará orientada principalmente a las actividades que puedan realizarse de manera remota utilizando los equipos de cómputo del equipo de desarrollo, proporcionado mayor flexibilidad y autonomía durante las actividades de desarrollo:

* programación;  
* diseño y administración de la base de datos;  
* documentación;  
* diseño de interfaces y prototipos;  
* análisis de requisitos;  
* corrección de errores;  
* pruebas técnicas;

La **modalidad presencial** se utilizará para las actividades que requieran interacción directa con la institución, usuarios o el entorno real donde será utilizado el sistema, particularmente:

* levantamiento de información de campo;  
* observación de los procesos actuales;  
* aclaración y validación de requisitos;  
* reuniones y seguimiento del proyecto con responsables y usuarios;  
* revisión presencial de prototipos y funcionalidades;  
* pruebas de usabilidad;  
* pruebas de aceptación;  
* recopilación de retroalimentación;  
* identificación y validación de necesidades

La modalidad propuesta estará sujeta a la **autorización y disponibilidad de la institución receptora del servicio social**, así como a los horarios y condiciones que ésta establezca.

### **Restricción tecnológica**

| STACK BASE |  |
| ----- | :---: |
| **Componente** | **Tecnología** |
| **Lenguaje principal** | TypeScript, Python |
| **Framework web** | Next.js , Django |
| **Base de datos** | PostgreSQL |
| **Control de versiones y repositorio** | Git \+ GitHub |

### **Costos estimados**

El proyecto contempla principalmente costos asociados a infraestructura, servicios tecnológicos y comunicación. Debido a que el proyecto se encuentra en etapa de planeación, los siguientes valores deben considerarse **estimaciones de referencia** y podrán variar dependiendo de las necesidades finales del sistema, el volumen de usuarios, el consumo de servicios externos y las tarifas vigentes al momento de su implementación.

| Concepto | Costo estimado | Observaciones |
| ----- | ----- | ----- |
| **Computadoras y equipo de desarrollo** | $0 MXN | Se utilizarán los equipos de cómputo disponibles del equipo de desarrollo, por lo que no se contempla la adquisición de nuevos equipos dentro del presupuesto base. |
| **Software de desarrollo** | $0 MXN | Se priorizará el uso de herramientas y tecnologías de código abierto o con versiones gratuitas, como Python, Django, PostgreSQL y herramientas de desarrollo compatibles. |
| **Alojamiento / servidor** | $0–$500 MXN/mes | Estimación inicial. El costo dependerá del proveedor, capacidad requerida y si durante el desarrollo se utiliza infraestructura gratuita o un servidor contratado. |
| **Dominio web** | $200–$500 MXN/año | Estimación para un dominio convencional. Podría no ser necesario durante las primeras etapas del desarrollo. |
| **Base de datos** | $0–$500 MXN/mes | Puede mantenerse dentro de la infraestructura del servidor. El costo adicional dependerá de la cantidad de información y del proveedor utilizado. |
| **Servicio de mensajería** | **Variable** | El costo dependerá del medio utilizado y del volumen de mensajes enviados. Se deberá considerar el precio por mensaje, posibles tarifas de plataforma y, en su caso, costos asociados al uso de APIs de terceros. |
| **Correo electrónico transaccional** | $0–$500 MXN/mes | Se contempla para el envío de notificaciones, recuperación de cuentas, avisos y otros mensajes automáticos. El costo dependerá del volumen mensual y del proveedor seleccionado. |
| **Materiales para pruebas y levantamiento de información** | $0–$500 MXN | Impresiones, formatos, hojas de evaluación u otros materiales que pudieran requerirse durante las actividades presenciales. |
| **Otros servicios tecnológicos** | $0–$500 MXN/mes | Costos eventuales de almacenamiento, herramientas complementarias, servicios de terceros u otros recursos que resulten necesarios durante el desarrollo. |

#### **Consideración específica sobre el servicio de mensajería**

Debido a que el sistema contempla la posibilidad de enviar **notificaciones automáticas a usuarios**, el servicio de mensajería representa uno de los costos variables más importantes del proyecto.

Para efectos de planeación, se propone contemplar inicialmente un presupuesto estimado de **$300 a $1,000 MXN mensuales**, sujeto a validación durante la etapa de diseño y selección del proveedor. Este monto es únicamente una **estimación de referencia** y no constituye un precio definitivo.

El costo final dependerá principalmente de:

* número de usuarios registrados;  
* cantidad de mensajes enviados mensualmente;  
* tipo de mensaje y canal utilizado;  
* proveedor seleccionado;  
* tarifas por mensaje o por conversación;  
* utilización de SMS, correo electrónico, WhatsApp u otros canales;  
* posibles costos de establecimiento, número telefónico o servicios adicionales de la plataforma.

Durante el desarrollo se priorizarán alternativas de **bajo costo o gratuitas para pruebas**, evitando generar gastos innecesarios mientras el sistema se encuentre en etapa de desarrollo. 

**Presupuesto general de referencia**

Considerando únicamente los costos externos potenciales, se estima que el proyecto podría requerir inicialmente entre **$500 y $2,000 MXN mensuales** durante las etapas en las que se encuentren activos servicios de infraestructura y mensajería.

Este rango es **preliminar y sujeto a cambios**, por lo que el presupuesto definitivo deberá establecerse después de determinar la arquitectura final del sistema, el número esperado de usuarios, los mecanismos de notificación y los proveedores que serán utilizados.

## **8\. Principios de desarrollo**

El proyecto seguirá los siguientes principios:

1. **Valor antes que volumen:** se priorizarán funcionalidades que solucionen necesidades reales.  
2. **Software funcionando como evidencia de progreso.**  
3. **Desarrollo incremental:** cada etapa deberá producir un incremento verificable (ver sección . Hitos).  
4. **Validación temprana:** las decisiones importantes deberán comprobarse lo antes posible.  
5. **Simplicidad:** evitar funcionalidades y tecnologías innecesarias.  
6. **Calidad integrada:** las pruebas no se dejarán exclusivamente para el final.  
7. **Seguridad desde el diseño:** la información escolar será tratada como información sensible.  
8. **Documentación progresiva:** la documentación crecerá junto con el producto.  
9. **Mejora continua:** al finalizar cada ciclo se identificarán oportunidades de mejora.  
10. **Control de cambios:** ningún cambio importante de alcance se incorporará sin evaluar su impacto en tiempo, riesgo y objetivos.

## 

## **9\. Criterio general de éxito**

El proyecto se considerará exitoso cuando exista una versión funcional y validada del sistema que permita ejecutar de principio a fin los procesos prioritarios definidos en el alcance, con datos persistentes, control de acceso, registro verificable de operaciones, pruebas documentadas y una versión preparada para su utilización en un entorno real o piloto.

## **10\. Hitos y niveles de madurez tecnológica**

Cada hito permitirá evaluar de manera progresiva el grado de desarrollo, integración, validación y preparación para operación del producto. Representa un punto de control del proyecto y deberá contar con resultados verificables y KPIs que permitan determinar objetivamente si se cumplen las condiciones necesarias para avanzar a la siguiente etapa.

### **Hito 01 — Base funcional y generación de QR**

**Periodo objetivo:** Semanas 1–8

**Resultado esperado:**  
Contar con una primera versión funcional del sistema capaz de registrar estudiantes y generar un código QR único asociado a cada uno, en un formato adecuado para su incorporación a las credenciales institucionales.

**Actividades principales:**

* configuración de la arquitectura inicial;  
* implementación de la base de datos;  
* desarrollo de la gestión básica de estudiantes;  
* generación y asociación de códigos QR;  
* validación de unicidad e integridad de los identificadores;  
* pruebas funcionales del flujo de generación;  
* generación de una muestra de códigos para validación con la institución.

**KPIs:**

* 100 % de los estudiantes de prueba con un QR único asociado;  
* 0 identificadores duplicados durante las pruebas;  
* 100 % de los QR generados correctamente legibles;  
* 100 % de los QR correctamente asociados con su estudiante;  
* generación de los QR dentro del plazo de 6-8 semanas;  
* aprobación de la institución para iniciar el proceso de producción de credenciales.

### 

### **Hito 02 — Sistema web integrado**

**Periodo objetivo:** Semanas 8–11

**Resultado esperado:**  
Contar con una versión web integrada que permita administrar estudiantes, usuarios, familiares e identificadores, con autenticación y control de acceso de acuerdo con los roles definidos.

**Actividades principales:**

* consolidación de los módulos de gestión;  
* implementación de autenticación;  
* implementación de roles y permisos;  
* integración de módulos con la base de datos;  
* desarrollo del panel administrativo;  
* pruebas funcionales y de integración.

**KPIs:**

* 100 % de los módulos definidos para esta etapa integrados;  
* 100 % de los roles definidos con permisos funcionales;  
* 100 % de las operaciones críticas con datos persistentes;  
* 0 errores críticos abiertos al cierre del hito;  
* 100 % de los casos de prueba críticos ejecutados.

### **Hito 03 — Control de asistencia mediante QR**

**Periodo objetivo:** Semanas 11–15

**Resultado esperado:**  
Contar con un flujo completo de identificación y registro de asistencia mediante los códigos QR previamente generados.

**Actividades principales:**

* implementación de lectura de QR;  
* validación de identificadores;  
* registro de fecha y hora;  
* aplicación de reglas de asistencia;  
* prevención de registros inválidos o duplicados;  
* pruebas de integración;  
* pruebas en condiciones controladas con usuarios reales.

**KPIs:**

* ≥ 99 % de lecturas correctas durante las pruebas;  
* 100 % de lecturas válidas asociadas al estudiante correcto;  
* 0 registros de asistencia asociados a estudiantes inexistentes;  
* 100 % de registros almacenados con fecha y hora;  
* 0 duplicados generados en escenarios contemplados por las reglas;  
* 100 % de los casos críticos de asistencia superados.

### **Hito 04 — Validación con usuarios y operación piloto**

**Periodo objetivo:** Semanas 16–19

**Resultado esperado:**  
Validar la facilidad de uso, funcionamiento y comportamiento del sistema mediante pruebas con estudiantes y personal escolar en un entorno representativo de su utilización real.

**Actividades principales:**

* pruebas de usabilidad con estudiantes;  
* pruebas operativas con personal escolar;  
* simulación de jornadas de registro de asistencia;  
* identificación y documentación de errores;  
* recopilación de retroalimentación;  
* ajustes derivados de las pruebas;  
* nueva ronda de validación.

**KPIs:**

* participación de una muestra definida de estudiantes y personal;  
* ≥ 90 % de las tareas principales completadas correctamente por los participantes;  
* ≥ 80 % de valoración positiva de usabilidad;  
* 100 % de errores críticos identificados corregidos antes de avanzar;  
* 100 % de escenarios críticos de uso validados;  
* registro y análisis del 100 % de la retroalimentación recopilada.

### **Hito 05 — Plataforma integral validada**

**Periodo objetivo:** Semanas 20–22

**Resultado esperado:**  
Contar con una versión integrada de la plataforma que incorpore los módulos contemplados para la entrega y permita ejecutar de principio a fin los procesos prioritarios definidos en el alcance.

**Actividades principales:**

* integración de módulos restantes;  
* implementación de incidencias y comportamiento;  
* implementación de reportes;  
* integración de comunicación con familiares;  
* integración de la aplicación móvil en las funciones priorizadas;  
* pruebas de integración del sistema completo.

**KPIs:**

* 100 % de los módulos incluidos en la versión final integrados;  
* 100 % de los flujos prioritarios ejecutables de principio a fin;  
* 100 % de las funcionalidades críticas con pruebas documentadas;  
* 0 errores críticos abiertos;  
* ≥ 95 % de los casos de prueba críticos aprobados.

### **Hito 06 — Preparación para operación**

**Periodo objetivo:** Semanas 23–24

**Resultado esperado:**  
Disponer de una versión estable, documentada y preparada para su utilización en un entorno real o piloto, con los mecanismos de seguridad, respaldo, validación y control necesarios.

**Actividades principales:**

* pruebas finales de aceptación;  
* pruebas de seguridad y control de acceso;  
* validación de respaldos y recuperación;  
* corrección de errores finales;  
* documentación técnica y operativa;  
* preparación del entorno de despliegue;  
* capacitación inicial de los usuarios designados;  
* entrega formal del sistema.

**KPIs:**

* 100 % de los criterios de aceptación cumplidos;  
* 100 % de los roles y permisos validados;  
* 100 % de los respaldos y procedimientos de recuperación probados;  
* 100 % de los procesos prioritarios validados;  
* 0 errores críticos abiertos al momento de la entrega;  
* 100 % de los entregables documentados y entregados;  
* aprobación formal de la versión final por parte de la institución.

### **Criterio de avance entre hitos**

El avance hacia un nuevo nivel de madurez estará condicionado al cumplimiento de los criterios de aceptación y KPIs establecidos para el hito anterior. Cuando un hito no alcance los criterios definidos, las actividades de corrección y validación correspondientes deberán priorizarse antes de continuar con funcionalidades que dependan directamente de dicho resultado.

La escala de madurez funcionará como mecanismo de seguimiento y toma de decisiones del proyecto, sin sustituir la planificación detallada de actividades, dependencias y recursos establecida posteriormente mediante la EDT/WBS y el cronograma.

## **Matriz consolidada de KPIs**

La siguiente matriz consolida los indicadores definidos para cada hito del proyecto. Su propósito es facilitar el seguimiento del avance, cumplimiento y nivel de madurez del sistema durante la ejecución del proyecto.

| ID | Hito | KPI | Meta / criterio |
| ----- | ----- | ----- | ----- |
| **KPI-01** | Hito 01 — Base funcional y generación de QR | Estudiantes de prueba con QR único asociado | **100 %** |
| **KPI-02** | Hito 01 — Base funcional y generación de QR | Identificadores duplicados durante las pruebas | **0** |
| **KPI-03** | Hito 01 — Base funcional y generación de QR | QR generados correctamente legibles | **100 %** |
| **KPI-04** | Hito 01 — Base funcional y generación de QR | QR correctamente asociados con su estudiante | **100 %** |
| **KPI-05** | Hito 01 — Base funcional y generación de QR | Generación de QR dentro del plazo establecido | **Máximo 6 semanas** |
| **KPI-06** | Hito 01 — Base funcional y generación de QR | Aprobación institucional para iniciar producción de credenciales | **Aprobado** |
| **KPI-07** | Hito 02 — Sistema web integrado | Módulos definidos para la etapa integrados | **100 %** |
| **KPI-08** | Hito 02 — Sistema web integrado | Roles definidos con permisos funcionales | **100 %** |
| **KPI-09** | Hito 02 — Sistema web integrado | Operaciones críticas con datos persistentes | **100 %** |
| **KPI-10** | Hito 02 — Sistema web integrado | Errores críticos abiertos al cierre del hito | **0** |
| **KPI-11** | Hito 02 — Sistema web integrado | Casos de prueba críticos ejecutados | **100 %** |
| **KPI-12** | Hito 03 — Control de asistencia mediante QR | Lecturas correctas durante las pruebas | **≥ 99 %** |
| **KPI-13** | Hito 03 — Control de asistencia mediante QR | Lecturas válidas asociadas al estudiante correcto | **100 %** |
| **KPI-14** | Hito 03 — Control de asistencia mediante QR | Registros de asistencia asociados a estudiantes inexistentes | **0** |
| **KPI-15** | Hito 03 — Control de asistencia mediante QR | Registros almacenados con fecha y hora | **100 %** |
| **KPI-16** | Hito 03 — Control de asistencia mediante QR | Duplicados generados en escenarios contemplados por las reglas | **0** |
| **KPI-17** | Hito 03 — Control de asistencia mediante QR | Casos críticos de asistencia superados | **100 %** |
| **KPI-18** | Hito 04 — Validación con usuarios y operación piloto | Participación de una muestra definida de estudiantes y personal | **Cumplida** |
| **KPI-19** | Hito 04 — Validación con usuarios y operación piloto | Tareas principales completadas correctamente por participantes | **≥ 90 %** |
| **KPI-20** | Hito 04 — Validación con usuarios y operación piloto | Valoración positiva de usabilidad | **≥ 80 %** |
| **KPI-21** | Hito 04 — Validación con usuarios y operación piloto | Errores críticos identificados corregidos antes de avanzar | **100 %** |
| **KPI-22** | Hito 04 — Validación con usuarios y operación piloto | Escenarios críticos de uso validados | **100 %** |
| **KPI-23** | Hito 04 — Validación con usuarios y operación piloto | Retroalimentación recopilada y analizada | **100 %** |
| **KPI-24** | Hito 05 — Plataforma integral validada | Módulos incluidos en la versión final integrados | **100 %** |
| **KPI-25** | Hito 05 — Plataforma integral validada | Flujos prioritarios ejecutables de principio a fin | **100 %** |
| **KPI-26** | Hito 05 — Plataforma integral validada | Funcionalidades críticas con pruebas documentadas | **100 %** |
| **KPI-27** | Hito 05 — Plataforma integral validada | Errores críticos abiertos | **0** |
| **KPI-28** | Hito 05 — Plataforma integral validada | Casos de prueba críticos aprobados | **≥ 95 %** |
| **KPI-29** | Hito 06 — Preparación para operación | Criterios de aceptación cumplidos | **100 %** |
| **KPI-30** | Hito 06 — Preparación para operación | Roles y permisos validados | **100 %** |
| **KPI-31** | Hito 06 — Preparación para operación | Respaldos y procedimientos de recuperación probados | **100 %** |
| **KPI-32** | Hito 06 — Preparación para operación | Procesos prioritarios validados | **100 %** |
| **KPI-33** | Hito 06 — Preparación para operación | Errores críticos abiertos al momento de la entrega | **0** |
| **KPI-34** | Hito 06 — Preparación para operación | Entregables documentados y entregados | **100 %** |
| **KPI-35** | Hito 06 — Preparación para operación | Aprobación de la versión final por parte de la institución | **Aprobada** |

## 

## **11\. Criterio de aceptación del proyecto**

El proyecto se considerará formalmente aceptado cuando la versión final del sistema alcance el nivel de madurez establecido para la entrega, cumpla los requisitos y criterios de aceptación definidos para los módulos incluidos en el alcance y exista evidencia verificable de su funcionamiento en un entorno real o piloto.

La aceptación se determinará mediante la evidencia obtenida durante las pruebas, validaciones y revisiones del proyecto, utilizando como referencia los **KPI definidos en la Matriz consolidada de seguimiento (KPI-01 a KPI-35)**. Los indicadores correspondientes deberán alcanzar sus valores objetivo en los hitos en los que sean aplicables.

### **11.1. Funcionalidad**

La versión final deberá demostrar que las funcionalidades y procesos prioritarios contemplados en el alcance se encuentran implementados, integrados y operativos.

La aceptación de la funcionalidad deberá sustentarse principalmente en:

* **KPI-07:** 100 % de los módulos definidos para la etapa correspondiente deberán encontrarse integrados.  
* **KPI-08:** 100 % de los roles definidos deberán contar con permisos funcionales.  
* **KPI-09:** 100 % de las operaciones críticas deberán mantener datos persistentes.  
* **KPI-13:** 100 % de las lecturas válidas de QR deberán asociarse con el estudiante correspondiente.  
* **KPI-15:** 100 % de los registros de asistencia deberán almacenarse con fecha y hora.  
* **KPI-17:** 100 % de los casos críticos de asistencia deberán resultar satisfactorios.  
* **KPI-24:** 100 % de los módulos contemplados en la versión final deberán encontrarse integrados.  
* **KPI-25:** 100 % de los procesos prioritarios deberán poder ejecutarse de principio a fin.  
* **KPI-26:** 100 % de las funcionalidades críticas deberán contar con pruebas documentadas.  
* **KPI-32:** 100 % de los procesos prioritarios deberán encontrarse validados antes de la entrega.

Asimismo, deberá verificarse que el flujo de generación, asociación y validación de códigos QR se encuentre operativo, de acuerdo con los resultados establecidos en los **KPI-01 a KPI-06**.

### **11.2. Calidad y pruebas**

La calidad de la versión final deberá demostrarse mediante la ejecución documentada de las pruebas funcionales, de integración y de los escenarios críticos definidos durante el proyecto.

La aceptación deberá considerar:

* **KPI-11:** 100 % de los casos de prueba críticos deberán haber sido ejecutados.  
* **KPI-17:** 100 % de los casos críticos de asistencia deberán haber sido aprobados.  
* **KPI-26:** 100 % de las funcionalidades críticas deberán contar con pruebas documentadas.  
* **KPI-28:** al menos el 95 % de los casos de prueba críticos de la versión final deberán resultar satisfactorios.  
* **KPI-10, KPI-27 y KPI-33:** no deberán existir errores críticos abiertos al cierre de los hitos correspondientes ni al momento de la entrega final.

Los errores detectados durante las pruebas deberán encontrarse documentados, clasificados y atendidos conforme a su prioridad. Las pruebas de integración deberán demostrar que los componentes principales del sistema funcionan correctamente en conjunto.

### **11.3. Validación con usuarios**

La validación con usuarios deberá demostrar que el sistema puede ser utilizado correctamente en un entorno representativo por los usuarios definidos para el proyecto.

La aceptación de esta etapa deberá sustentarse en:

* **KPI-18:** participación de la muestra de estudiantes y personal escolar definida para las pruebas.  
* **KPI-19:** al menos el 90 % de las tareas principales deberá completarse correctamente.  
* **KPI-20:** la evaluación de usabilidad deberá alcanzar al menos el 80 % de valoración positiva.  
* **KPI-21:** 100 % de los errores críticos identificados durante la validación deberán haber sido corregidos antes de avanzar a la siguiente etapa.  
* **KPI-22:** 100 % de los escenarios críticos de uso deberán encontrarse validados.  
* **KPI-23:** 100 % de la retroalimentación obtenida deberá encontrarse registrada y analizada.

Deberán realizarse pruebas de usabilidad con la muestra definida de estudiantes y personal escolar, así como pruebas operativas en un entorno representativo.

### **11.4. Datos, seguridad y operación**

La versión final deberá demostrar que la información se almacena correctamente, que el acceso al sistema se encuentra controlado y que existen mecanismos básicos para preservar y recuperar la información.

La aceptación deberá sustentarse en:

* **KPI-08:** 100 % de los roles definidos deberán contar con permisos funcionales.  
* **KPI-09:** 100 % de las operaciones críticas deberán mantener datos persistentes.  
* **KPI-30:** 100 % de los roles y permisos deberán haber sido validados.  
* **KPI-31:** 100 % de los procedimientos de respaldo y recuperación deberán haber sido probados.  
* **KPI-32:** 100 % de los procesos prioritarios deberán haber sido validados.  
* **KPI-33:** deberán existir 0 errores críticos abiertos al momento de la entrega.

Las operaciones críticas deberán generar registros verificables y deberá comprobarse la integridad de la información almacenada. La versión final deberá encontrarse desplegada o preparada para su despliegue en el entorno definido por la institución.

### **11.5. Identificación mediante códigos QR**

Debido a que la generación de identificadores QR constituye una necesidad prioritaria del proyecto, su aceptación deberá verificarse específicamente mediante los indicadores correspondientes al primer hito:

* **KPI-01:** 100 % de los estudiantes incluidos en la prueba deberán contar con un QR único.  
* **KPI-02:** deberán existir 0 identificadores duplicados.  
* **KPI-03:** 100 % de los códigos QR deberán ser correctamente legibles.  
* **KPI-04:** 100 % de los códigos deberán encontrarse correctamente asociados con su estudiante.  
* **KPI-05:** la generación de los códigos deberá completarse dentro del plazo máximo establecido de seis semanas.  
* **KPI-06:** deberá existir aprobación institucional para iniciar la producción de las credenciales.

El cumplimiento de estos indicadores permitirá considerar validada la primera versión funcional del mecanismo de identificación y habilitar el avance hacia las etapas posteriores del proyecto.

### **11.6. Documentación y entrega**

La entrega deberá incluir la documentación y las evidencias necesarias para demostrar el cumplimiento de los criterios establecidos durante el proyecto.

Como parte de la aceptación final deberán encontrarse documentados y entregados:

* los resultados y evidencias de las pruebas realizadas;  
* la documentación técnica mínima del sistema y su arquitectura;  
* la documentación básica para los usuarios finales;  
* los procedimientos básicos de operación, respaldo y recuperación;  
* la evidencia correspondiente al cumplimiento de los KPIs aplicables;  
* la demostración integral de los procesos prioritarios.

El cumplimiento de la entrega deberá verificarse mediante el **KPI-34**, que establece que el 100 % de los entregables deberán encontrarse documentados y entregados.

### **11.7. Aceptación institucional**

La aceptación definitiva requerirá la revisión y aprobación de la versión final por parte de los responsables designados por la institución.

La aprobación institucional deberá sustentarse en:

* **KPI-06:** aprobación para iniciar la producción de credenciales en la primera etapa.  
* **KPI-35:** aprobación institucional de la versión final.  
* Cumplimiento de los KPIs aplicables a los hitos precedentes.  
* Evidencia de que los procesos prioritarios pueden ejecutarse correctamente.  
* Evidencia de que el sistema cumple los requisitos acordados y se encuentra preparado para su utilización en un entorno real o piloto.

### **11.8. Regla de aceptación**

El cumplimiento de los criterios de aceptación se determinará mediante la **Matriz consolidada de KPIs**, considerando los valores objetivo establecidos para cada indicador.

Un hito podrá considerarse cumplido únicamente cuando los KPIs correspondientes alcancen sus valores objetivo y exista evidencia verificable de su cumplimiento.

La aceptación del proyecto completo requerirá, como mínimo:

1. el cumplimiento de los criterios establecidos para cada hito;  
2. la validación de los procesos prioritarios;  
3. la ausencia de errores críticos abiertos al momento de la entrega;  
4. la entrega de la documentación y evidencias correspondientes; y  
5. la aprobación institucional de la versión final, conforme al **KPI-35**.

Los criterios específicos de aceptación de cada módulo, requisito, historia de usuario y entregable se desarrollarán durante la fase de planificación detallada y deberán mantener trazabilidad con los KPIs, pruebas y criterios de aceptación definidos para el proyecto.

## **12\. Cronograma, lista de actividades y Diagrama de Gantt:**

![][image1]

## **13\. Próximos documentos de planificación**

Esta acta constituye únicamente el punto de partida del proyecto.

A partir de ella se desarrollarán, en este orden:

1. **Requisitos funcionales y no funcionales**  
2. **Historias de usuario**  
3. **Criterios de aceptación específicos por requisito**  
4. **Arquitectura del sistema**  
5. **Modelo de datos**  
6. **Estimación de esfuerzo**  
7. **Plan de pruebas y calidad**  
8. **Plan de despliegue**  
9. **Plan de mantenimiento y evolución**

## **14\. Estado del documento**

**Estado:** Acta constitutiva para aprobación.

El presente documento establece las bases generales del proyecto, incluyendo su propósito, objetivos, alcance, producto esperado, criterios generales de éxito, hitos, niveles de madurez tecnológica, KPIs y criterios generales de aceptación.

La aprobación de esta acta autorizará el inicio formal de la fase de planificación detallada, durante la cual se desarrollarán y documentarán los requisitos funcionales y no funcionales, historias de usuario, arquitectura del sistema, modelo de datos, EDT/WBS, estimación de esfuerzo, dependencias, ruta crítica, cronograma, matriz de riesgos, plan de pruebas, plan de despliegue y demás elementos necesarios para la ejecución del proyecto.

Los detalles técnicos, estimaciones, fechas específicas de actividades y demás elementos de planificación podrán ser refinados durante dicha fase, siempre que se mantengan consistentes con el propósito, objetivos, alcance y restricciones establecidos en esta acta. Cualquier modificación sustancial al alcance aprobado deberá someterse al proceso de evaluación y aprobación correspondiente.

[image1]: <data:image/png;base64,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>