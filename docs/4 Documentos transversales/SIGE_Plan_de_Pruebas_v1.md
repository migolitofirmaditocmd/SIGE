# SIGE — Plan de Pruebas
### Sistema Integral de Gestión Escolar

**Archivo:** `SIGE_Plan_de_Pruebas_v1.md` · **Anexo:** `SIGE_Plan_de_Pruebas_Anexo_A_Matriz.md`
**Versión:** 1.0 | **Estado:** Para revisión del equipo
**Fuentes:** Criterios de Aceptación v2 (con los parches PAQ1 y PAQ3) · Reglas de Negocio v3 · Requisitos v3 · API REST v2 · Seguridad y Autenticación v2 · Procesos Programados v2 · Arquitectura C4 v2 · Modelo de Datos v3.2 · Arquitectura Frontend y PWA v1 · Acta Constitutiva v10 (hitos y KPIs)

---

## 0. Cómo leer este documento

1. **Dos documentos.** Este plan define la estrategia, los niveles, los recorridos, los datos y los criterios de salida. El **Anexo A** trae la matriz de trazabilidad: **cada criterio de aceptación, con su nivel de prueba, sus casos, su recorrido E2E y su prioridad**.
2. **El número de criterios no es 407.** La tabla de cobertura del documento de criterios (§6) dice 407, pero el archivo trae **442 criterios** y los parches ratificados agregan **15**,para un total vigente de **457 criterios** (**461** al sumar CA-033-13, de PT-02, y los tres de esta revisión: CA-001-11, CA-030-08 y CA-042-09). El §5.3 muestra la diferencia por épica y el §9 trae el parche que corrige esa tabla. Todo lo que sigue usa las cifras reales.
3. **Lo que está fijado y lo que propongo.** Los requisitos, reglas, criterios, KPIs de hito y niveles de exigencia vienen de los documentos del proyecto. Las **herramientas, umbrales de cobertura, tiempos y reglas de asignación** fueron propuestas mías y quedaron **aprobadas**; las marcas **(Propuesta)** que quedan en el texto se leen como decisiones aprobadas. El §12 registra qué se decidió.
4. **La asignación de nivel y de prioridad por criterio se hizo por reglas** (§5.1) y la revisé por muestreo; no la validé uno por uno. Se afina historia por historia cuando cumpla el *Definition of Ready*.

---

## 1. Objetivos y alcance

### 1.1 Objetivos

| # | Objetivo | Fuente |
|---|---|---|
| 1 | Demostrar que **cada criterio de aceptación** tiene al menos una prueba y que esa prueba pasa | CA §1 ("cada criterio... al menos un caso de prueba"), Acta Hito 08 |
| 2 | Proteger lo que no se puede corregir después: **asistencia** (los registros no se borran), **permisos** y **datos de menores** | RN-TRX-03, RNF-SEG-04 |
| 3 | Verificar los requisitos no funcionales que no son criterios: tiempo de 250 ms, tolerancia a desconexión, respaldos probados, compatibilidad de dispositivos | RNF-DES-01, RNF-FIA-01, RNF-FIA-03, RNF-COM-02 |
| 4 | Dar a cada hito de la Acta su evidencia de cierre (KPIs) | Acta §11 |

### 1.2 Dentro del alcance

Los diez módulos funcionales (62 historias), los 16 criterios transversales (CT-01 a CT-16), la PWA (incluido el modo sin conexión), los procesos programados (ausencias y respaldo), el envío de correo, la instalación en el servidor local y la recuperación ante fallo.

### 1.3 Fuera del alcance

- **Asistencia del personal administrativo:** está en espera (CC-02) y no tiene historias ni criterios.
- **Acceso remoto desde Internet** y copia externa de respaldos por defecto (apagada hasta su autorización, D-05); solo se prueba que, si se habilita, no altera el resultado del respaldo local.
- **Pruebas con datos reales de menores:** no se hacen en ningún entorno de prueba (§8.1).

---

## 2. Estrategia

### 2.1 Principios

| # | Principio | Consecuencia |
|---|---|---|
| 1 | **Las reglas de negocio viven en el backend** (RN-TRX-05, CT-02), así que se prueban ahí | Casi todo criterio se verifica por la **API con una base PostgreSQL real**; la interfaz se prueba para lo que solo ella hace |
| 2 | **Una prueba rápida y precisa vale más que una lenta que cubre todo** | Pirámide: muchas unitarias y de integración, pocas E2E, y las E2E van **por recorrido**, no una por criterio |
| 3 | **PostgreSQL real, nunca SQLite** | Las restricciones (`UNIQUE`, `CHECK`, índices parciales, claves foráneas) son parte de las reglas; los criterios CT-16 y CA-0xx de unicidad dependen de ellas |
| 4 | **El tiempo es una entrada** | Todo lo que depende de la hora (corte, rebote, ausencias, vigencias, bloqueos) se prueba con un **reloj controlado** (§3.2) |
| 5 | **Cada defecto corregido deja una prueba** | Una regresión es una prueba nueva, no solo un arreglo |
| 6 | **Lo que no se puede automatizar se declara** | Cámara con luz solar, lectura de QR impreso y compatibilidad en dispositivos reales son pruebas manuales, planeadas y registradas (§3.7) |

### 2.2 Pirámide resultante

El nivel **principal** es donde se verifica el criterio; los **complementarios** lo refuerzan. Cifras tomadas del Anexo A.

| Nivel | Criterios con este nivel **principal** | Criterios en que interviene (principal o complementario) | Casos de prueba `TC-…` |
|---|---|---|---|
| **U** Unitaria | 16 | 82 | 82 |
| **I** Integración | 399 | 420 | 420 |
| **E** E2E (por recorrido) | 37 | 142 | — (se cubren en los recorridos) |
| **R** Rendimiento | 1 | 1 | 1 |
| **S** Seguridad | 0 | 19 | 19 |
| **O** Operación | 4 | 6 | 6 |
| **M** Manual con dispositivos | 0 | 1 | 1 |
| **Total** | **457** | | **529** más 20 recorridos E2E |

Además de los casos de prueba por criterio, hay **20 recorridos E2E** (§4.3) que ejecutan los flujos completos y cubren **142** criterios de forma complementaria.

---

## 3. Niveles de prueba

### 3.1 Resumen

| Nivel | Qué verifica | Herramientas **(Propuesta)** | Cuándo corre |
|---|---|---|---|
| **U** Unitaria | Funciones puras y reglas de cálculo: estado por hora de corte, rebote, tolerancia, umbral de ausencia, normalización de nombres, validadores, generación de tokens, cálculo de offset de reloj, buffer offline | Backend: `pytest` y `pytest-django`. Frontend: `Vitest` y Testing Library | En cada confirmación de código |
| **I** Integración | Endpoints con base real: permisos por rol, transacciones, restricciones, auditoría, jobs, correo, importación, sincronización | `pytest-django`, `DRF APIClient`, `factory_boy`, PostgreSQL real, reloj controlado, servidor SMTP de pruebas | En cada confirmación de código |
| **E** E2E | Recorridos completos con interfaz real, incluidos los estados de CT-13, el modo sin conexión y el Service Worker | `Playwright` (Chromium y WebKit), `axe-core` | En cada fusión a la rama principal y antes de cada hito |
| **R** Rendimiento | 250 ms en el escaneo y capacidad en hora pico | `k6` o `Locust` contra el entorno de preproducción | Antes de los Hitos 05 y 06 |
| **S** Seguridad | Autenticación, sesión, bloqueo, cabeceras, dependencias, controles del checklist OWASP ASVS de SEG §4 | Pruebas de integración dirigidas, `bandit`, `pip-audit`, `npm audit`, escaneo básico de la aplicación | Dependencias en cada fusión; el resto antes del Hito 08 |
| **O** Operación | Respaldo, restauración y recuperación (runbook), arranque en orden, operación sin Internet | Guion de pruebas sobre el entorno de preproducción | Antes de cada hito de cierre (RNF-FIA-03) |
| **M** Manual | Cámara y lectura de QR en dispositivos reales, luz solar, impresión, usabilidad | Guías de prueba y registro de resultados | Hito 04 (dispositivos) y Hito 06 (piloto) |
| **A** Accesibilidad | CT-14: teclado, foco, etiquetas, no depender del color | `axe-core` automático más revisión manual | Con los recorridos E2E |

### 3.2 Requisitos de testabilidad para el desarrollo **(Propuesta)**

Para que las pruebas del §3.1 sean posibles, el código debe cumplir esto desde el Hito 01. Si no, los criterios dependientes del tiempo y de los jobs no se pueden verificar de forma estable.

| # | Requisito | Por qué |
|---|---|---|
| 1 | **Reloj inyectable.** Ninguna regla llama a la hora del sistema directamente; todas usan un servicio único de reloj que las pruebas reemplazan | Corte, rebote, ausencias, vigencia de enlaces, bloqueo y expiración de sesión (CA-028-*, CA-029-*, CA-030-*, CA-002-*) |
| 2 | **Cada job se puede ejecutar a mano** con una orden de administración que reciba la fecha y el turno | Los recorridos E2E-09, E2E-14 y E2E-19 no pueden esperar a las 10:00 |
| 3 | **Configuración de pruebas separada.** Los atajos de prueba (reloj fijo, límite de intentos reducido, correo a un buzón de pruebas) existen **solo** en esa configuración y nunca en producción | Evita un "endpoint de pruebas" abierto en el servidor real |
| 4 | **Semillas reproducibles** a partir de las migraciones de datos (MIG §4) más fábricas de datos sintéticos | Todo entorno parte del mismo estado |
| 5 | **Identificadores y errores estables.** Cada error de la API trae `error_code` y `rn_reference` (API §1.2) | Las pruebas aseveran el código, no el texto |
| 6 | **Esquema OpenAPI publicado** (`/api/v1/schema/`) | Base de las pruebas de contrato y de los tipos del frontend |

### 3.3 Pruebas de integración: la matriz de autorización

Los **54 criterios `[Perm]`** y CT-03 se prueban con **una sola prueba parametrizada** que recorre cada endpoint contra cada rol (ADM, PRE, DOC, PAD, SL) y compara el resultado con la matriz de RN-AUT-06 y con la columna de roles de la API.

- Esperado para un rol sin permiso: **403**, o **404** si el recurso está fuera de su alcance (RN-REP-05).
- Se ejecuta también contra la **API directa**, sin pasar por la interfaz, como pide el DoD ("acceso por URL/API").
- Cuando cambie la matriz de roles, cambia la tabla de datos de la prueba, no su código.

### 3.4 Pruebas unitarias de las reglas de cálculo

Los criterios `[Límite]` (20) se concentran aquí. Cada regla se prueba con **valores frontera** tomados del criterio:

| Regla | Frontera que se prueba | Criterios |
|---|---|---|
| Hora de corte | Escaneo a las 08:00 frente a las 08:01 | CA-028-01, CA-028-02 |
| Ventana de rebote | 07:55:00 frente a 07:55:01; ventana de 0, 1, 30 y 31 min; conteo desde el **último escaneo procesado** | CA-029-01, 02, 04, 07; CA-055-02 |
| Verificación de ausencias | 09:59 frente a 10:00 | CA-030-02 |
| Tolerancia docente | Tolerancia 0 y hora esperada 08:00 | CA-040-02, CA-040-09 |
| Observación de reporte | 49, 50, 100 y 101 caracteres | CA-045-02, CA-045-03 |
| Nombre de persona | 1, 2, 60 y 61 caracteres | CA-008-15 |
| Bloqueo por intentos | 4 intentos frente a 5 | CA-002-01 |
| Buffer offline | 999 y 1,000 eventos | CA-032-03, CA-032-04 |
| Colisión de QR | Máximo de 5 reintentos | CA-022-05 |

### 3.5 Pruebas de integración de procesos programados

Cada job se prueba **ejecutándolo directamente** con el reloj controlado (§3.2, requisitos 1 y 2), contra una base con datos preparados:

- **Ausencias estudiantiles y docentes:** quién recibe `FALTÓ`, quién no (ya tiene registro, es de otro turno, sin programación hoy, `INACTIVO`), idempotencia (correr dos veces no duplica) y concurrencia con un escaneo (gana el escaneo).
- **Guardias:** sin ciclo activo y sin actividad de asistencia → `OMITIDO` y alerta (D-03, CA-042-08).
- **Respaldo:** archivo generado, verificado y rotado; falla simulada y alerta (CA-057-01, CA-057-02).
- **Dispatcher:** recupera una corrida vencida tras una "caída" simulada.
- **Correo:** reintentos con retroceso y consentimiento revocado a mitad del envío.

### 3.6 Pruebas de la PWA y del modo sin conexión

Combinan componentes (unitarias del buffer, del cálculo de offset y de la sesión), integración de la sincronización contra la API y E2E con el navegador sin red. La lista completa de pruebas de aceptación offline está en la Arquitectura Frontend §5.3.8; aquí quedan trazadas a los criterios:

| Prueba (Arq. Frontend §5.3.8) | Criterios |
|---|---|
| 1. Abrir la PWA instalada sin red | CA-032-08 |
| 2 y 3. Escanear sin conexión; el registro tiene solo los seis campos | CA-032-01, CA-032-07 |
| 4. Capturar el evento 1,001 | CA-032-04 |
| 5. Recargar sin conexión conserva pendientes | CA-032-09 |
| 6 a 8. Sincronización automática, en orden, idempotente | CA-033-01, 02, 07, 10, 11 |
| 7. Descartes (baja, QR revocado, duplicado) y aviso al operador | CA-033-03, 04, 05, 08 |
| 9. Refresh vencido durante la desconexión | **Sin criterio hoy** (SEG §7); se propone CA-033-13 (§5.4) |
| 10. Reloj adelantado | CA-033-09, CA-033-12 |
| 11. Versión nueva con pendientes | (sin criterio; verifica el ciclo del Service Worker) |
| 12. Cerrar sesión con pendientes | CA-001-09 |

Particularidades de automatización **(Propuesta)**: el navegador de pruebas permite simular la desconexión; la cámara se sustituye por un video de prueba con códigos QR conocidos (la lectura real con cámara es prueba manual, §3.7).

### 3.7 Pruebas manuales con dispositivos reales

No se pueden automatizar de forma fiable y se ejecutan con guías y registro:

| Prueba | Qué se comprueba | Cuándo |
|---|---|---|
| **Lectura de QR en dispositivos representativos** | Meta del Acta Hito 04: **≥ 99 % de lecturas correctas**. Muestra: **300 lecturas por combinación** de tipo de dispositivo y formato de impresión (credencial y sticker), 200 en condiciones normales y 100 en exterior con luz solar; se aprueba con una tasa observada de al menos 99 % en cada combinación | Hito 04 |
| **Legibilidad a pleno sol** | Contraste y retroalimentación visual y sonora en exteriores (CT-11) | Hito 04 y piloto |
| **Instalación de la CA interna y de la PWA** | En cada modelo y versión de la matriz de RNF-COM-02 | Antes del Hito 04 |
| **Credenciales impresas** | QR legible tras impresión y desgaste razonable (CA-025-03) | Hito 04 |
| **Usabilidad con estudiantes y personal** | KPIs del Hito 06 (≥ 90 % de tareas, ≥ 80 % de valoración positiva) | Hito 06 |

---


## 4. Recorridos E2E

### 4.1 Reglas

- Un recorrido es una **historia de uso completa** con la interfaz real, no un criterio suelto.
- Corre con **navegador de escritorio** y con **emulación móvil** cuando el rol es móvil (PRE, DOC, escaneo).
- Cada recorrido verifica, de paso, los estados de CT-13 que aparezcan en su camino.
- Los recorridos **no repiten** lo que ya verifica la integración (permisos, límites, auditoría): se enfocan en que las piezas funcionen juntas.

### 4.2 Datos y entorno de los recorridos

Una base de datos reiniciada con semillas por cada recorrido (o por cada grupo de recorridos), un ciclo escolar activo, estudiantes y docentes sintéticos, un servidor SMTP de pruebas y el reloj controlado del §3.2.

### 4.3 Catálogo de recorridos

| ID | Recorrido | Roles | Historias (SIGE-US-) | Criterios que ejecuta | Particularidad |
|---|---|---|---|---|---|
| **E2E-01** | Sesión: inicio, renovación transparente, bloqueo por intentos, desbloqueo, recuperación de contraseña, cierre | Todos | 001, 002, 005 | 5 | — |
| **E2E-02** | Autorización por rol: cada rol ve su menú; entrar por URL a lo no permitido muestra "Permiso denegado" | Todos | 006 | 3 | — |
| **E2E-03** | Cuentas: alta, desactivación con efecto inmediato y consulta de la bitácora | ADM | 003, 004, 007 | 4 | Sesión abierta del usuario desactivado (CA-004-07) |
| **E2E-04** | Alta de estudiante con tutor, tutor compartido y registro incompleto que se completa | PAD | 008, 009, 010, 012 | 8 | — |
| **E2E-05** | Expediente: consulta y filtros, cambio de grupo, baja, reingreso y consentimiento | PAD, ADM | 011, 013, 014, 015, 016 | 10 | — |
| **E2E-06** | Importación: plantilla, carga, vista previa, confirmación y reporte | PAD, ADM | 017 a 021 | 14 | Archivos de prueba (§8.1) |
| **E2E-07** | QR: generar, validar lote, revocar y reemplazar, exportar y reexportar | PAD, ADM | 022 a 026 | 11 | Descarga de archivos |
| **E2E-08** | Escaneo en línea: válido, tardío, rebote, QR inválido o revocado, estudiante dado de baja | PRE, PAD | 027, 028, 029 | 9 | Cámara simulada; vista móvil |
| **E2E-09** | Ausencia automática y reclasificación: `FALTÓ` a la hora de verificación y un escaneo posterior lo corrige | PRE, PAD | 030, 031 | 5 | Job ejecutado a mano con reloj controlado |
| **E2E-10** | Modo sin conexión: capturar, buffer, recargar sin red, reconectar, sincronizar y ver el resumen | PRE, PAD | 032, 033 | 15 | Navegador sin red; Service Worker; vista móvil |
| **E2E-11** | Justificar y modificar asistencia (estudiante y docente) con auditoría visible | PAD, ADM | 034, 043 | 4 | — |
| **E2E-12** | Consultas de asistencia: diaria por grupo, historial individual y consolidada | ADM, PRE, PAD, SL | 035, 036, 037, 044 | 8 | — |
| **E2E-13** | Docente: ficha, QR, programación, desactivación, reactivación y vínculo con cuenta | PAD, ADM | 038, 039, 059 a 062 | 9 | — |
| **E2E-14** | Asistencia docente: entrada, salida, ausencia automática y reclasificación | PAD | 040, 041, 042 | 10 | Job ejecutado a mano con reloj controlado |
| **E2E-15** | Reporte completo: registrar, revisar y canalizar, aprobar y decidir si se comunica o se resuelve | DOC, PRE, PAD | 045, 046, 047, 049, 050 | 12 | Vista móvil para DOC y PRE |
| **E2E-16** | Rechazo y corrección: el prefecto rechaza, el docente corrige con un reporte nuevo referenciado y se consulta la trazabilidad | DOC, PRE | 048, 051 | 2 | — |
| **E2E-17** | Comunicación por correo: vista previa, envío, estado y reintento manual | PAD | 052, 053 | 5 | Servidor SMTP de pruebas, con fallo simulado |
| **E2E-18** | Administración: catálogos, parámetros con efecto no retroactivo y panel de indicadores | ADM | 054, 055, 056 | 6 | — |
| **E2E-19** | Continuidad: respaldo visible en el panel y operación completa **sin Internet** | ADM, PRE | 057, 058 | 2 | Salida a Internet bloqueada (CT-15) |
| **E2E-20** | Estados de interfaz y accesibilidad en las pantallas principales de cada rol | Todos | (transversal) | CT-13, CT-14 | CT-13 y CT-14; `axe-core` |

> **E2E-20** no corresponde a una historia: ejecuta los siete estados de interfaz (CT-13) y las verificaciones de accesibilidad (CT-14) sobre las pantallas principales de cada rol.

---

## 5. Trazabilidad con los criterios de aceptación

### 5.1 Cómo se asignó el nivel y la prioridad **(Propuesta)**

La asignación se hizo con reglas sobre la etiqueta del criterio y sobre su texto, y se revisó por muestreo. Se corrige historia por historia al cumplir el DoR; el Anexo A es la fuente de verdad cuando cambie.

**Nivel principal**

| Regla (en este orden) | Nivel principal | Complementarios |
|---|---|---|
| Criterio de la épica EP-10 sobre restauración o recuperación | **O** | I |
| Criterio de la épica EP-10 sobre respaldo (ejecución, alerta) | **I** | O |
| Habla de tiempo de respuesta de 250 ms | **R** | I |
| Historia SIGE-US-032 (captura sin conexión, lado cliente) | **E** | U |
| Historia SIGE-US-033 (validación en el backend al sincronizar) | **I** | E si habla de la interfaz |
| Etiqueta `[UX]` | **E** | A si habla de contraste, teclado, etiquetas o color |
| El texto describe la ejecución de un proceso programado | **I** | U |
| Etiqueta `[Perm]` | **I** (matriz de autorización, §3.3) | E si habla de menús o pantallas |
| Etiqueta `[Aud]` | **I** | — |
| Etiqueta `[Límite]` | **U** si hay un cálculo o validación; si no, **I** | I |
| Etiqueta `[Neg]` | **I** | U si es una validación de formato o de cálculo |
| Etiqueta `[Alt]` | **I** | E si habla de interfaz o de modo sin conexión |
| Etiqueta `[Feliz]` | **I** | E si habla de interfaz o de modo sin conexión |

Reglas adicionales sobre los complementarios:

- Los criterios `[Feliz]` de los flujos centrales (escaneo, estado, ausencias automáticas, reclasificación, entrada y salida docente, alta y revocación de QR, justificación, importación, reporte y envío de correo) llevan **E** complementario, porque cada recorrido debe ejecutar su camino principal.
- Los criterios de EP-01 sobre sesión, contraseña, bloqueo y credenciales llevan **S** complementario.
- Los que hablan de lectura o impresión del QR llevan **M** complementario.

**Prioridad**

| Prioridad | Qué entra | Uso |
|---|---|---|
| **P0** | Todo criterio `[Perm]`; las historias de sesión y acceso (US-001, 002, 004, 005, 006); consentimiento (US-016); QR único y revocación (US-022, 024); escaneo, estado, rebote, ausencias automáticas, reclasificación, captura y sincronización sin conexión (US-027 a 033); justificación y modificación de asistencia (US-034, 043); entrada, salida y ausencias docentes (US-040 a 042); continuidad (US-057, 058); y todo proceso programado | Son los **casos críticos** del Acta: bloquean el cierre de hito (Hito 07: ≥ 95 % de los casos críticos aprobados) |
| **P1** | Resto de los criterios funcionales | Se ejecutan completos antes de cada hito de cierre |
| **P2** | Criterios `[UX]` de presentación fuera de las historias P0 | Se corrigen en el piloto sin bloquear el hito |

### 5.2 Resumen por épica

| Épica | Historias | Criterios | U | I | E | R | O | P0 | P1 | P2 |
|---|---|---|---|---|---|---|---|---|---|---|
| EP-01 Autenticación y acceso | 7 | 52 | 2 | 45 | 5 | 0 | 0 | 41 | 10 | 1 |
| EP-02 Estudiantes | 9 | 76 | 1 | 69 | 6 | 0 | 0 | 15 | 56 | 5 |
| EP-03 Importación | 5 | 35 | 0 | 34 | 1 | 0 | 0 | 3 | 31 | 1 |
| EP-04 QR y credenciales | 5 | 32 | 1 | 29 | 2 | 0 | 0 | 18 | 12 | 2 |
| EP-05 Asistencia estudiantil | 11 | 86 | 7 | 63 | 15 | 1 | 0 | 71 | 12 | 3 |
| EP-06 Asistencia docente | 11 | 82 | 2 | 78 | 2 | 0 | 0 | 39 | 41 | 2 |
| EP-07 Reportes | 7 | 48 | 2 | 43 | 3 | 0 | 0 | 11 | 34 | 3 |
| EP-08 Comunicación | 2 | 13 | 0 | 12 | 1 | 0 | 0 | 0 | 12 | 1 |
| EP-09 Administración | 3 | 21 | 1 | 18 | 2 | 0 | 0 | 9 | 10 | 2 |
| EP-10 Continuidad | 2 | 12 | 0 | 8 | 0 | 0 | 4 | 12 | 0 | 0 |
| **Total** | **62** | **457** | 16 | 399 | 37 | 1 | 4 | **219** | 218 | 20 |

Las columnas U, I, E, R y O cuentan el **nivel principal** de cada criterio. Las cifras están al corte de PAQ3 (457 criterios); la adenda del Anexo A suma 4 criterios (EP-01 +1, EP-05 +2 y EP-06 +1) y lleva el total a 461.

### 5.3 La tabla de cobertura del documento de criterios está desactualizada

El §6 del documento de criterios dice **407** criterios y 62 historias. Las historias son 62, pero el archivo trae más criterios de los que declara:

| Épica | Declarado en §6 | En el archivo v2 | Vigentes (con parches) |
|---|---|---|---|
| EP-01 | 45 | 48 | 52 |
| EP-02 | 55 | 76 | 76 |
| EP-03 | 29 | 35 | 35 |
| EP-04 | 32 | 32 | 32 |
| EP-05 | 80 | 80 | 86 |
| EP-06 | 77 | 78 | 82 |
| EP-07 | 48 | 48 | 48 |
| EP-08 | 13 | 13 | 13 |
| EP-09 | 17 | 21 | 21 |
| EP-10 | 11 | 11 | 12 |
| **Total** | **407** | **442** | **457** |

La diferencia viene sobre todo de EP-02 (+21), EP-03 (+6) y EP-09 (+4). El parche del §9 (PT-01) corrige la tabla.

### 5.4 Criterios agregados por los parches y brechas detectadas

**Los 15 criterios nuevos** (de los parches PAQ1 y PAQ3) ya están en el Anexo A, marcados como *(nuevo)*; la adenda del Anexo A agrega CA-033-13, CA-030-08, CA-042-09 y CA-001-11: CA-001-08 a 10, CA-004-07, CA-032-08 a 10, CA-033-10 a 12, CA-040-11, CA-042-07, CA-042-08, CA-057-07 y CA-060-10.

**Brechas** que aparecieron al trazar las pruebas:

| # | Brecha | Propuesta |
|---|---|---|
| 1 | La prueba de "refresh vencido durante la desconexión" (Arq. Frontend §5.3.8, prueba 9) **no tiene criterio**, aunque SEG §7 lo exige | Agregar **CA-033-13** (parche PT-02, §9) |
| 2 | **RNF-DES-02** (capacidad en hora pico) deja el valor de *N* "a definir con la institución" | Definirlo antes del Hito 05; ver §7 y §12 (P-T3) |
| 3 | La prueba de actualización del Service Worker con eventos pendientes (prueba 11) no tiene criterio funcional | Se mantiene como prueba técnica de la PWA, sin criterio |

### 5.5 Cómo se mantiene la trazabilidad **(Propuesta)**

- Cada prueba automatizada lleva una marca con el criterio que verifica (por ejemplo `CA-030-01`) y sigue la convención `TC-<historia>-<n>-<nivel>` del Anexo A.
- Una verificación en CI recorre el documento de criterios y **falla si un criterio no tiene ninguna prueba marcada** (excepto los de nivel manual, que se registran en las guías).
- Los criterios nuevos o modificados por un control de cambios agregan su fila al Anexo A en el mismo cambio.

---

## 6. Criterios transversales (CT-01 a CT-16)

Los CT no se repiten en cada historia (CA §2) y se verifican con pruebas propias, no criterio por criterio:

| CT | Cómo se verifica | Nivel |
|---|---|---|
| **CT-01** Cifrado en tránsito | El proxy rechaza o redirige HTTP; los dispositivos de la matriz confían en la CA interna y no muestran advertencias; no hay recursos mixtos | S, O, M |
| **CT-02** Validación en backend | Para cada regla con interfaz, una prueba **envía a la API la solicitud que la interfaz impediría** y comprueba el rechazo | I |
| **CT-03** Autorización en API | Matriz de autorización parametrizada (§3.3) y llamadas directas sin pasar por la interfaz | I |
| **CT-04** Paridad web/móvil | La misma historia corre con vista de escritorio y vista móvil contra la misma API; revisión de contrato: no existen endpoints exclusivos de un cliente | I, E |
| **CT-05** Auditoría | Por cada acción crítica listada en RN-AUT-05 se verifica el registro con usuario, fecha, valor anterior y nuevo, y motivo | I |
| **CT-06** Sin eliminación física | No existe operación de borrado para esas entidades y el rol de la aplicación en PostgreSQL no tiene `DELETE` sobre ellas (SEG §8) | I, S |
| **CT-07** Datos de menores | Revisión de campos recolectados frente a la lista mínima; tutor hereda las restricciones del expediente; fotos solo por la API autorizada | I, S |
| **CT-08** Origen del cambio | Cada transición de asistencia deja `AUTOMATICO`, `ESCANEO` o `MANUAL` y el historial lo muestra | I |
| **CT-09** Errores consistentes | Todo `4xx` y `5xx` validado contra el esquema de error (`error_code`, `message`, `trace_id`) y la interfaz muestra el mensaje y la referencia | I, E |
| **CT-10** 250 ms | Prueba de rendimiento del escaneo (§7) | R |
| **CT-11** Ergonomía y retroalimentación | Contraste calculado de los tokens, radio de esquinas calculado de los componentes, sonido y retroalimentación en E2E, legibilidad a pleno sol en manual | E, A, M |
| **CT-12** Compatibilidad | Lector HID emulado con eventos de teclado en E2E; cámara UVC y dispositivos de la matriz en manual | E, M |
| **CT-13** Estados de interfaz | Recorrido E2E-20 y pruebas de componente de los siete estados en cada pantalla con datos | E |
| **CT-14** Responsive y accesibilidad | `axe-core` automático, navegación solo con teclado y revisión manual de foco y etiquetas | A, E, M |
| **CT-15** Red local | Con la salida a Internet bloqueada, los recorridos de asistencia, reportes y consultas pasan completos (E2E-19) | E, O |
| **CT-16** Persistencia | Una operación que falla a mitad (fila de importación, alta con tutor inválido, envío que falla) no deja datos parciales; una exitosa deja datos verificables | I |

---

## 7. Requisitos no funcionales

| Requisito | Prueba | Nivel | Criterio de aprobación |
|---|---|---|---|
| **RNF-DES-01** 250 ms | Escaneo con la red local de preproducción y carga normal; se mide de la solicitud a la respuesta y, en el cliente, hasta pintar el resultado | R | Latencia del servidor en el percentil 95 por debajo de 250 ms; si la medida incluye el pintado en el cliente, se acuerda el método (P-T4). Criterio CA-027-06 |
| **RNF-DES-02** Hora pico | Carga de *N* escaneos por minuto sostenida durante 15 minutos con el mismo criterio de 250 ms | R | *N* **sin definir**. Propuesta: *N* = 2 × (estudiantes del turno más grande ÷ 15 minutos) (P-T3) |
| **RNF-SEG-01** TLS | Ver CT-01 | S, O | Sin tráfico en claro |
| **RNF-SEG-02** Payload opaco | El token del QR es un UUIDv4 sin datos personales; dos QR del mismo estudiante no comparten patrón | U, I | 0 identificadores duplicados (KPI02) |
| **RNF-SEG-03** Contraseñas y bloqueo | Políticas configurables, hash fuerte, bloqueo al 5.º intento | I, S | CA-002-*, CA-005-* |
| **RNF-SEG-04** Datos de menores | Ver CT-07 | I, S | |
| **RNF-FIA-01** Buffer offline | Ver §3.6 | E, U | 1,000 eventos, sin pérdida |
| **RNF-FIA-02** Disponibilidad | Prueba de **recuperación** del plan de despliegue (6.2): caída del servicio, caída de PostgreSQL y servidor de reemplazo | O | Cumple los tiempos acordados (RTO, P-R1 del runbook) |
| **RNF-FIA-03** Respaldo probado | Restauración completa de un respaldo verificado antes de cada hito | O | 100 % de los respaldos de prueba recuperados (KPI del Hito 05) |
| **RNF-FIA-04** Sincronización horaria | Reloj del servidor desviado más de 2 minutos: el job de ausencias no inicia; cálculo del desfase en el cliente; **procedimiento manual de revisión de hora al inicio de cada jornada sin Internet** | U, I, O | Ver 6.2 §6.4 |
| **RNF-USA-01** Ergonomía | Ver CT-11 | E, A, M | |
| **RNF-USA-02** Curva de aprendizaje | Pruebas de usabilidad del piloto con una guía mínima | M | ≥ 90 % de tareas completadas (Hito 06) |
| **RNF-COM-01 y 02** Hardware y dispositivos | Matriz de dispositivos (§3.7) | M, E | Matriz documentada y validada antes del Hito 04 |
| **RNF-POR-01** Reproducibilidad | Reinstalar el servidor en un equipo limpio siguiendo el plan de despliegue | O | Sistema operativo y pasa las pruebas de humo (6.2 §8) |
| **RNF-MAN-02** Frontend sin lógica de negocio | Revisión de código y regla de dependencias de la Arquitectura Frontend §5.2.3 | revisión | Sin reglas duplicadas |

---

## 8. Datos de prueba y entornos

### 8.1 Datos

- **Nunca datos reales de menores** en ningún entorno de prueba (RN-TRX-01, RNF-SEG-04). Todos los estudiantes, tutores y docentes son **sintéticos**: nombres inventados, correos en un dominio reservado para pruebas y teléfonos ficticios.
- **Semillas:** las de MIG §4 (parámetros operativos, ciclo activo, catálogos de reporte) más fábricas de datos que generan grupos, estudiantes, tutores compartidos, docentes con y sin programación, QR vigentes y revocados.
- **Casos de nombres:** compuestos ("María José"), con partículas ("De la Cruz"), con acentos, apellido materno vacío, longitudes frontera (CA-008-*).
- **Archivos de importación:** válidos, con estructura inválida, con filas mixtas, con matrículas duplicadas, con formatos inesperados, de tamaño máximo (CA-017-* a CA-021-*).
- **QR de prueba:** imágenes con tokens conocidos para la cámara simulada.
- **Sin dependencia de producción:** ninguna prueba toca el servidor de la institución.

### 8.2 Entornos

| Entorno | Para qué | Contenido |
|---|---|---|
| **Desarrollo y CI** | Unitarias, integración, E2E y verificación de trazabilidad | PostgreSQL real descartable, servidor SMTP de pruebas, reloj controlado |
| **Preproducción** (réplica del servidor local) | Rendimiento, operación, recuperación, instalación (RNF-POR-01) y dispositivos reales | Mismo despliegue que producción (6.2), con datos sintéticos |
| **Piloto** (Hito 06) | Usabilidad y jornadas simuladas con personal y estudiantes | Producción de ensayo con datos sintéticos o anonimizados con autorización |
| **Producción** | Solo pruebas de humo tras la puesta en marcha (6.2 §8) | Datos reales; sin pruebas destructivas |

---

## 9. Parches derivados

### PT-01 · Tabla de cobertura del documento de criterios

**Documento:** CA · §6 "Resumen de cobertura"
**Acción:** REEMPLAZAR

*Texto actual:*

````markdown
| Épica | Historias | Criterios |
|---|---|---|
| EP-01 Autenticación y acceso | 7 | 45 |
| EP-02 Estudiantes | 9 | 55 |
| EP-03 Importación | 5 | 29 |
| EP-04 QR y credenciales | 5 | 32 |
| EP-05 Asistencia estudiantil | 11 | 80 |
| EP-06 Asistencia docente | 11 | 77 |
| EP-07 Reportes | 7 | 48 |
| EP-08 Comunicación | 2 | 13 |
| EP-09 Administración | 3 | 17 |
| EP-10 Continuidad | 2 | 11 |
| **Total** | **62** | **407** (más los 16 transversales, que no cambian). |
````

*Texto nuevo:*

````markdown
| Épica | Historias | Criterios |
|---|---|---|
| EP-01 Autenticación y acceso | 7 | 53 |
| EP-02 Estudiantes | 9 | 76 |
| EP-03 Importación | 5 | 35 |
| EP-04 QR y credenciales | 5 | 32 |
| EP-05 Asistencia estudiantil | 11 | 88 |
| EP-06 Asistencia docente | 11 | 83 |
| EP-07 Reportes | 7 | 48 |
| EP-08 Comunicación | 2 | 13 |
| EP-09 Administración | 3 | 21 |
| EP-10 Continuidad | 2 | 12 |
| **Total** | **62** | **461** (442 del archivo v2, 15 de los parches PAQ1 y PAQ3 y 4 de PT-02 y de la revisión de decisiones; más los 16 transversales, que no cambian). |
````

### PT-02 · Criterio de sesión vencida durante la desconexión (brecha 1)

**Documento:** CA · US-033, después de CA-033-12
**Acción:** REEMPLAZAR

*Texto actual:*

````markdown
- **CA-033-12 · UX** — **Dado que** el desfase del reloj del dispositivo supera 5 minutos, **cuando** el operador captura un evento sin conexión, **entonces** se le advierte que la hora del dispositivo difiere del servidor, y el evento se marca para revisión al sincronizar (SEG §7).
````

*Texto nuevo:*

````markdown
- **CA-033-12 · UX** — **Dado que** el desfase del reloj del dispositivo supera 5 minutos, **cuando** el operador captura un evento sin conexión, **entonces** se le advierte que la hora del dispositivo difiere del servidor, y el evento se marca para revisión al sincronizar (SEG §7).
- **CA-033-13 · Alt** — **Dado que** el token de renovación venció mientras el dispositivo estuvo sin conexión, **cuando** el operador intenta sincronizar, **entonces** SIGE le pide iniciar sesión de nuevo y los eventos pendientes se conservan sin borrarse (SEG §7).
````

Si se aplica PT-02, el criterio entra al Anexo A como P0, nivel E con U complementario.

---

## 10. Ejecución y criterios de salida

### 10.1 Canalización de integración continua **(Propuesta)**

| Etapa | Qué corre | Debe pasar para continuar |
|---|---|---|
| 1. Confirmación de código | Análisis estático, unitarias (U), integración (I) con PostgreSQL real, verificación de trazabilidad | Todo en verde |
| 2. Fusión a la rama principal | Etapa 1 más E2E (Chromium y WebKit), accesibilidad (A), pruebas de contrato contra el OpenAPI, dependencias (S) | Todo en verde |
| 3. Candidata a hito | Etapa 2 más rendimiento (R), operación (O), seguridad dirigida (S) y manuales (M) | Criterios del hito (§10.2) |

### 10.2 Criterios de salida por hito

Los KPIs vienen del Acta; la columna de pruebas indica con qué se demuestran.

| Hito | KPIs relevantes (Acta) | Evidencia de este plan |
|---|---|---|
| **04** Aplicación móvil | 100 % de funciones móviles críticas y roles con permisos; **≥ 99 % de lecturas correctas de QR**; 100 % de los reportes de prueba recibidos; **0 errores críticos** | E2E de PRE, DOC y PAD en móvil; matriz de dispositivos; pruebas manuales de lectura de QR; CA-032-08 (abrir sin red) |
| **05** Servidor local | 100 % de servicios desplegados y conexiones web y móvil en la LAN; **100 % de procesos prioritarios sin Internet**; **100 % de los respaldos de prueba recuperados**; 0 errores críticos | Pruebas de humo del despliegue (6.2 §8), E2E-19, restauración completa (O), CT-15 |
| **06** Piloto | **≥ 90 % de tareas completadas**; **≥ 80 % de valoración positiva**; 100 % de errores críticos corregidos; 100 % de escenarios críticos validados | Pruebas de usabilidad (M), jornadas simuladas, RNF-USA-02 |
| **07** Plataforma integral | 100 % de flujos prioritarios de principio a fin; 100 % de funcionalidades críticas con pruebas documentadas; **≥ 95 % de los casos críticos aprobados**; 0 errores críticos | Los 20 recorridos E2E; los criterios **P0** del Anexo A |
| **08** Preparación para operación | **100 % de los criterios de aceptación cumplidos**; 100 % de roles y permisos validados; **100 % de respaldos y procedimientos de recuperación probados**; 0 errores críticos | Todo el Anexo A; matriz de autorización (§3.3); restauración y recuperación (O); seguridad (S) |

### 10.3 Severidad y gestión de defectos **(Propuesta)**

| Severidad | Qué es | Ejemplos | Efecto |
|---|---|---|---|
| **Crítica** | Pérdida o corrupción de datos, falla de seguridad o de permisos, imposibilidad de registrar asistencia | Un rol sin permiso accede a datos de menores; un escaneo válido no se registra; el buffer pierde eventos | Bloquea el hito (el KPI exige **0 críticos abiertos**) |
| **Alta** | Una función principal no se puede usar o da un resultado incorrecto sin pérdida de datos | Reclasificación con estado equivocado | Se corrige antes del cierre del hito |
| **Media** | Función secundaria con alternativa | Filtro que no recuerda la página | Se planea en el siguiente ciclo |
| **Baja** | Presentación, texto, estilo | Alineación | Se agrupa |

Cada defecto tiene criterio o requisito afectado, pasos para reproducirlo, severidad y su prueba de regresión.

### 10.4 Métricas de seguimiento **(Propuesta)**

- **Cobertura de criterios:** porcentaje de criterios con prueba escrita y con prueba aprobada, por épica y por prioridad (objetivo: 100 % para el Hito 08).
- **Tasa de aprobación de casos críticos (P0)** (objetivo: ≥ 95 % en el Hito 07 y 100 % en el Hito 08).
- **Cobertura de código** de los módulos que contienen reglas (asistencia, QR, reportes, comunicación, importación, auth): meta de **≥ 90 % de líneas y ramas**. No sustituye a la cobertura de criterios.
- **Defectos por severidad abiertos** y tiempo de resolución.
- **Estabilidad de la suite E2E:** pruebas que fallan de forma intermitente se aíslan y se corrigen, no se reintentan sin límite.

---

## 11. Riesgos de prueba

| # | Riesgo | Mitigación |
|---|---|---|
| 1 | Las reglas dependientes del tiempo se prueban con la hora real y fallan de forma intermitente | Reloj inyectable (§3.2, requisito 1) |
| 2 | Una suite E2E lenta o inestable que nadie ejecuta | Pocos recorridos, datos reiniciados por recorrido y ejecución solo en fusión y en candidatas a hito |
| 3 | No poder simular la cámara real, la luz solar ni las impresiones | Declararlo como prueba manual con guía y registro (§3.7) |
| 4 | El comportamiento de iOS (sin Background Sync, purga de almacenamiento) no se reproduce en el simulador | Dispositivos reales de la matriz de RNF-COM-02 |
| 5 | Datos reales de menores que se cuelan a un entorno de prueba | Datos sintéticos obligatorios (§8.1) y revisión del procedimiento de restauración de respaldos en preproducción |
| 6 | El conteo de criterios cambia y la matriz se desactualiza | Verificación de trazabilidad en CI (§5.5) |
| 7 | La asignación por reglas deja algún criterio en un nivel poco adecuado | Revisión por historia al cumplir el DoR; el Anexo A se actualiza |
| 8 | RNF-DES-02 sin valor de *N* y sin criterio | Definirlo antes del Hito 05 (P-T3) |

---

## 12. Decisiones propuestas y pendientes

Todo lo marcado **(Propuesta)** está en este plan y está aquí para ratificarse. Hasta que se ratifique, el plan sigue siendo válido con esos valores.

| # | Tema | Qué hace falta | Quién |
|---|---|---|---|
| **P-T1** | Herramientas de prueba (pytest, Vitest, Playwright, axe-core, k6 o Locust, bandit, pip-audit, npm audit) | Ratificar o sustituir | Equipo de desarrollo |
| **P-T2** | Reglas de asignación de nivel y prioridad (§5.1) y el que **P0 = casos críticos** del Acta | Ratificar. Si se cambia la definición de *crítico*, cambia el KPI del Hito 07 | Equipo e institución |
| **P-T3** | **Valor de *N*** de RNF-DES-02. Propuesta: 2 × (estudiantes del turno más grande ÷ 15) | Definirlo con la matrícula real, antes del Hito 05 | Institución |
| **P-T4** | **Método de medición** de los 250 ms: ¿solo el servidor o hasta pintar el resultado en el dispositivo? | Acordar | Equipo |
| **P-T5** | Metas de cobertura de código (≥ 90 % en módulos de reglas) | Ratificar | Equipo |
| **P-T6** | Requisitos de testabilidad del §3.2 (reloj inyectable, jobs ejecutables a mano, configuración de pruebas separada) | Que desarrollo los adopte desde el Hito 01 | Desarrollo |
| **P-T7** | Agregar **CA-033-13** (PT-02) y corregir la tabla de cobertura (PT-01) | Aplicar los parches | Documentación |
| **P-T8** | Tamaño de la muestra de **lecturas de QR** para el KPI ≥ 99 % del Hito 04 | Definirla junto con la matriz de dispositivos | Equipo |

---

*Fin del documento.*
