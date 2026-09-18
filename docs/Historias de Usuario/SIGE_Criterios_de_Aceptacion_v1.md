# Criterios de Aceptación — SIGE
### Sistema Integral de Gestión Escolar
**Documento complementario de:** `SIGE_Historias_de_Usuario_v1.md`
**Derivado de:** Catálogo de Reglas de Negocio v2 · Especificación de Requisitos v2 (RF/RNF) · Diagramas de flujo · Acta Constitutiva v9
**Versión:** 1.0 | **Estado:** Para revisión del equipo

---

## 1. Cómo leer este documento

- Cada historia (`SIGE-US-###`) tiene sus criterios `CA-###-##` en formato **Dado que / Cuando / Entonces**, derivados del par *condición → consecuencia* de las reglas de negocio.
- **Cada criterio es binario** (cumple / no cumple) y debe convertirse en al menos un caso de prueba (convención del catálogo de RN).
- Etiquetas: `[Feliz]` camino normal · `[Alt]` flujo alternativo · `[Neg]` rechazo/error · `[Límite]` valor frontera · `[Perm]` permisos · `[Aud]` auditoría · `[UX]` interfaz · `[⚠ A-##]` criterio sujeto a un hallazgo del Anexo A del documento de historias (validar antes de implementar).
- Los **criterios transversales (CT-##)** de la sección 2 aplican a **todas** las historias y no se repiten en cada una; cuando una historia los refuerza, se cita el CT.
- Los valores por defecto (5 min de rebote, 5 intentos, 10:00 de verificación, 1,000 eventos de buffer) son configurables donde así lo indican las RN.

---

## 2. Criterios transversales (aplican a todas las historias)

| ID | Criterio | Fuente |
|---|---|---|
| **CT-01** | **Seguridad en tránsito.** Toda comunicación cliente–servidor viaja cifrada (HTTPS/TLS), incluso dentro de la red local. | RNF-SEG-01 |
| **CT-02** | **Validación en backend.** Toda regla se valida en el servidor aunque el cliente ya la haya validado; una solicitud que viole una regla se rechaza sin importar lo que permitió la interfaz. | RN-API-01, RN-TRX-05, RF-API-02 |
| **CT-03** | **Autorización a nivel API.** Un usuario sin permiso recibe rechazo (403) aunque conozca la URL o llame a la API directamente; la interfaz oculta lo no permitido pero nunca es la única barrera. | RN-AUT-02, RF-AUT-02 |
| **CT-04** | **Paridad web/móvil.** Un registro generado desde la app móvil se sujeta exactamente a las mismas reglas, permisos y validaciones que desde la web; ambos clientes usan la misma API y base de datos. | RN-MOV-01, RN-API-02, RF-MOV-02 |
| **CT-05** | **Auditoría.** Toda acción crítica (cambios de rol, modificaciones de asistencia, modificaciones de reportes, cambios de estatus) genera un registro inmutable con usuario, fecha/hora y valor anterior/nuevo cuando aplique. | RN-AUT-05 |
| **CT-06** | **Sin eliminación física.** Ningún registro histórico (asistencia, reportes, expedientes en baja, QR revocados) se elimina físicamente; solo se archiva lógicamente. | RN-TRX-03 |
| **CT-07** | **Protección de datos de menores.** Solo se recolectan datos estrictamente necesarios; el acceso se limita al rol que lo requiere; los datos de tutores heredan las restricciones del expediente. | RN-TRX-01, 02, 06 · RNF-SEG-04 |
| **CT-08** | **Origen del cambio.** Los cambios automáticos de estado se distinguen de las modificaciones manuales y el historial permite saber cuál fue el origen. | RN-TRX-07 |
| **CT-09** | **Errores consistentes.** Los errores se devuelven con formato uniforme (código, mensaje, referencia de trazabilidad) en web y móvil, con mensajes comprensibles para el usuario. | RF-API-04 |
| **CT-10** | **Desempeño en punto de acceso.** La validación y confirmación de un QR se resuelve en menos de 250 ms bajo condiciones normales de red local. | RNF-DES-01 |
| **CT-11** | **Ergonomía y feedback.** Contraste alto apto para luz solar directa, esquinas tipo squircle (`border-radius` 12–16 px) y retroalimentación visual y sonora inmediata en escaneos válidos e inválidos. | RNF-USA-01 |
| **CT-12** | **Compatibilidad.** El escaneo acepta lectores USB tipo teclado (HID) y cámaras UVC sin controladores propietarios; la app funciona en los dispositivos y navegadores del conjunto soportado documentado. | RNF-COM-01, RNF-COM-02 |
| **CT-13** | **Estados de interfaz.** Toda pantalla con datos define comportamiento de: cargando, contenido, vacío, error (con reintento), éxito, permiso denegado y, en móvil, sin conexión. | Guía de historias |
| **CT-14** | **Responsive y accesibilidad.** La funcionalidad es usable en escritorio y móvil; navegación por teclado, foco visible, etiquetas en campos, mensajes de error comprensibles y sin depender solo del color para transmitir información. | Guía de historias · CT-11 |
| **CT-15** | **Red local.** Las funciones de asistencia, reportes y consultas operan dentro de la red institucional sin Internet. | RN-INF-01 |
| **CT-16** | **Persistencia.** Toda operación crítica exitosa deja datos persistentes verificables; una operación fallida no deja datos parciales inconsistentes. | KPI-09 |

---

## 3. Definition of Ready (DoR)

Una historia entra a sprint cuando se responde "sí" a: ¿se sabe quién la necesita y para qué? · ¿está acotada y es lo bastante pequeña para un incremento? · ¿sus criterios son binarios y QA puede convertirlos en casos de prueba? · ¿están definidos el comportamiento de UI y sus estados? · ¿se conocen datos, validaciones, reglas y permisos? · ¿se identificaron excepciones, no funcionales y dependencias? · ¿los hallazgos `⚠ A-##` que la afectan están resueltos o aceptados por escrito?

## 4. Definition of Done (DoD) global

- [ ] Código terminado y revisado; pruebas unitarias e integración necesarias.
- [ ] Todos los `CA-###-##` de la historia superados en QA y validados por el Product Owner.
- [ ] Criterios transversales CT-01 a CT-16 que apliquen verificados.
- [ ] Diseño UX/UI implementado según el flujo de referencia, incluyendo estados de interfaz.
- [ ] Responsive y accesibilidad validados; pruebas de autorización negativa (rol incorrecto, acceso por URL/API).
- [ ] Manejo de errores y auditoría implementados.
- [ ] Documentación técnica y de usuario actualizada.
- [ ] Sin defectos críticos abiertos (KPI de cierre de hito).

> **Criterios de aceptación (CA)** = qué debe cumplir *esta* historia. **DoD** = qué debe cumplir *toda* historia.

---

## 5. Criterios de aceptación por historia

# EP-01 — Autenticación, usuarios y control de acceso

### SIGE-US-001 — Iniciar y mantener sesión
- **CA-001-01 · Feliz** — **Dado que** un usuario tiene cuenta activa con un rol, **cuando** ingresa usuario y contraseña correctos, **entonces** SIGE emite un token de acceso de vida corta y un token de renovación, y muestra la pantalla inicial de su rol.
- **CA-001-02 · Neg** — **Dado que** ingresa una contraseña incorrecta, **cuando** envía el formulario, **entonces** SIGE muestra un mensaje genérico que no revela si falló el usuario o la contraseña y no emite tokens.
- **CA-001-03 · Neg** — **Dado que** la cuenta está desactivada, **cuando** intenta iniciar sesión, **entonces** se rechaza el acceso con un mensaje de cuenta no disponible.
- **CA-001-04 · Alt** — **Dado que** el token de acceso venció y el de renovación sigue vigente, **cuando** el usuario realiza una operación, **entonces** el sistema renueva la sesión de forma transparente y completa la operación.
- **CA-001-05 · Neg** — **Dado que** el token de acceso está vencido, **cuando** se envía una solicitud a la API sin renovarlo, **entonces** se responde 401 y no se ejecuta ninguna operación.
- **CA-001-06 · Alt** — **Dado que** el usuario cierra sesión, **cuando** intenta reutilizar su token de renovación, **entonces** se rechaza por estar invalidado.
- **CA-001-07 · UX** — **Dado que** el servidor no está disponible, **cuando** el usuario intenta iniciar sesión, **entonces** se muestra un error recuperable con opción de reintentar.

### SIGE-US-002 — Bloqueo temporal por intentos fallidos y desbloqueo manual
- **CA-002-01 · Límite** — **Dado que** el umbral es 5 intentos, **cuando** un usuario falla 4 veces consecutivas, **entonces** la cuenta sigue disponible; **y cuando** falla el 5.º, **entonces** la cuenta se bloquea temporalmente.
- **CA-002-02 · UX** — **Dado que** la cuenta está bloqueada, **cuando** el usuario intenta ingresar, **entonces** SIGE informa el tiempo de espera restante.
- **CA-002-03 · Neg** — **Dado que** la cuenta está bloqueada, **cuando** el usuario envía la contraseña correcta, **entonces** el acceso se rechaza hasta que venza el bloqueo.
- **CA-002-04 · Feliz** — **Dado que** un usuario acumuló 3 fallos, **cuando** inicia sesión correctamente, **entonces** el contador de fallos vuelve a cero.
- **CA-002-05 · Perm** — **Dado que** una cuenta está bloqueada, **cuando** un ADM la desbloquea, **entonces** el usuario puede ingresar de inmediato y queda registro del desbloqueo.
- **CA-002-06 · Perm** — **Dado que** el actor no es ADM, **cuando** intenta desbloquear una cuenta, **entonces** se rechaza la operación.
- **CA-002-07 · Alt** — **Dado que** el ADM cambia el umbral de intentos, **cuando** se aplica, **entonces** el nuevo valor rige para bloqueos posteriores y el cambio queda auditado.

### SIGE-US-003 — Dar de alta una cuenta de usuario con rol
- **CA-003-01 · Feliz** — **Dado que** un ADM captura nombre, usuario único, correo, rol y contraseña válida, **cuando** guarda, **entonces** se crea la cuenta con exactamente un rol y queda auditada.
- **CA-003-02 · Neg** — **Dado que** el usuario o el correo ya existen, **cuando** el ADM guarda, **entonces** se rechaza con indicación del campo duplicado.
- **CA-003-03 · Neg** — **Dado que** la contraseña no cumple la política mínima, **cuando** el ADM guarda, **entonces** se rechaza indicando qué requisito falta.
- **CA-003-04 · Perm** — **Dado que** el usuario autenticado no es ADM, **cuando** accede a la sección de altas (por menú o por URL/API), **entonces** recibe permiso denegado.
- **CA-003-05 · Neg** — **Dado que** se intenta asignar dos roles a la misma cuenta, **cuando** se guarda, **entonces** se rechaza: solo un rol activo (RN-AUT-01).

### SIGE-US-004 — Desactivar cuentas y reasignar rol
- **CA-004-01 · Feliz** — **Dado que** un ADM selecciona una cuenta activa, **cuando** confirma la desactivación, **entonces** la cuenta queda `DESACTIVADA`, sus tokens de renovación se invalidan y no se elimina ningún registro.
- **CA-004-02 · Aud** — **Dado que** un ADM cambia el rol de un usuario, **cuando** confirma, **entonces** el nuevo rol se aplica y la bitácora guarda rol anterior, rol nuevo, usuario y fecha/hora.
- **CA-004-03 · Neg** — **Dado que** el cambio de rol dejaría al usuario con dos roles activos, **cuando** se intenta, **entonces** se rechaza.
- **CA-004-04 · Neg** — **Dado que** solo queda un ADM activo, **cuando** se intenta desactivarlo o quitarle el rol, **entonces** se rechaza para no dejar el sistema sin administrador.
- **CA-004-05 · Perm** — **Dado que** el actor no es ADM, **cuando** intenta desactivar o reasignar, **entonces** se deniega (también por API).
- **CA-004-06 · Feliz** — **Dado que** una cuenta fue desactivada, **cuando** se consultan los registros que creó, **entonces** siguen mostrando su autoría.

### SIGE-US-005 — Recuperar contraseña mediante enlace de un solo uso
- **CA-005-01 · Feliz** — **Dado que** un usuario solicita recuperación con su correo institucional registrado, **cuando** hay Internet, **entonces** recibe un enlace de un solo uso con expiración configurable.
- **CA-005-02 · Neg** — **Dado que** el correo no corresponde a ninguna cuenta, **cuando** se solicita el enlace, **entonces** la pantalla muestra el mismo mensaje que en el caso exitoso y no se envía correo.
- **CA-005-03 · Límite** — **Dado que** el enlace expiró, **cuando** el usuario lo abre, **entonces** se rechaza y se ofrece solicitar uno nuevo.
- **CA-005-04 · Neg** — **Dado que** el enlace ya se usó, **cuando** se abre otra vez, **entonces** se rechaza.
- **CA-005-05 · Feliz** — **Dado que** el usuario define una nueva contraseña que cumple la política, **cuando** confirma, **entonces** se actualiza y las sesiones anteriores quedan invalidadas.
- **CA-005-06 · Alt** — **Dado que** no hay Internet, **cuando** se solicita el enlace, **entonces** SIGE informa que el servicio de correo no está disponible sin afectar el resto de funciones.

### SIGE-US-006 — Restringir funciones y datos según el rol
- **CA-006-01 · Perm** — **Dado que** cada rol tiene permisos definidos, **cuando** se ejecuta la batería de pruebas de autorización negativa (cada rol contra cada función no permitida), **entonces** el 100 % de los intentos se rechaza en la API.
- **CA-006-02 · Perm** — **Dado que** el usuario tiene rol Solo lectura, **cuando** ejecuta cualquier operación de escritura (crear, modificar, eliminar) por API, **entonces** se rechaza aunque no exista el botón en la interfaz.
- **CA-006-03 · Perm** — **Dado que** un usuario conoce la URL de una pantalla fuera de su rol, **cuando** la abre directamente, **entonces** ve permiso denegado sin datos.
- **CA-006-04 · UX** — **Dado que** un rol no tiene una función, **cuando** navega por el sistema, **entonces** esa función no aparece en su menú.
- **CA-006-05 · Neg** — **Dado que** un rol no requiere datos de menores para su función, **cuando** consulta cualquier endpoint que los contenga, **entonces** no obtiene esos datos.
- **CA-006-06 · Perm** — **Dado que** un dato de tutor pertenece a un expediente, **cuando** consulta un rol sin acceso al expediente, **entonces** tampoco accede al dato del tutor.

### SIGE-US-007 — Consultar la bitácora de auditoría
- **CA-007-01 · Feliz** — **Dado que** un ADM abre la bitácora, **cuando** aplica filtros de usuario, fechas, acción o resultado, **entonces** ve los registros paginados que cumplen.
- **CA-007-02 · Aud** — **Dado que** se ejecuta una acción crítica (cambio de rol, modificación de asistencia, de reporte o de estatus), **cuando** se consulta la bitácora, **entonces** aparece con usuario, fecha/hora, valor anterior y valor nuevo.
- **CA-007-03 · Neg** — **Dado que** cualquier usuario abre la bitácora, **cuando** intenta editar o borrar un registro, **entonces** no existe la opción y la API la rechaza.
- **CA-007-04 · Perm** — **Dado que** el usuario no es ADM, **cuando** intenta abrir la bitácora, **entonces** se deniega.
- **CA-007-05 · Aud** — **Dado que** un usuario inicia sesión (éxito o fallo), **cuando** se consulta la bitácora, **entonces** el evento aparece con su resultado.
- **CA-007-06 · Aud** — **Dado que** un estado cambió automáticamente y luego fue modificado por un usuario, **cuando** se consulta el historial, **entonces** ambos eventos se distinguen por origen (`AUTOMÁTICO`/`MANUAL`).
- **CA-007-07 · UX** — **Dado que** los filtros no arrojan resultados, **cuando** se aplican, **entonces** se muestra un estado vacío informativo.

---

# EP-02 — Gestión de estudiantes

### SIGE-US-008 — Registrar un estudiante desde la interfaz web
- **CA-008-01 · Feliz** — **Dado que** el PAD captura todos los datos válidos y al menos un tutor con contacto válido, **cuando** guarda, **entonces** se crea una ficha única en estatus `ACTIVO`, asignada a su grupo y ciclo.
- **CA-008-02 · Neg** — **Dado que** la matrícula ya existe, **cuando** el PAD guarda, **entonces** se rechaza indicando la matrícula duplicada y no se crea ni modifica ninguna ficha.
- **CA-008-03 · Neg** — **Dado que** no se capturó ningún tutor, **cuando** el PAD guarda, **entonces** no se guarda el registro y se pide al menos un tutor.
- **CA-008-04 · Neg** — **Dado que** un campo tiene formato inválido (p. ej. fecha, CURP), **cuando** el PAD guarda, **entonces** se señala el campo y no se guarda.
- **CA-008-05 · Neg** — **Dado que** dos altas simultáneas usan la misma matrícula, **cuando** se procesan, **entonces** solo una se persiste y la otra se rechaza por unicidad.
- **CA-008-06 · Perm** — **Dado que** el usuario es DOC, PRE o SL, **cuando** intenta crear un estudiante (menú, URL o API), **entonces** se deniega.
- **CA-008-07 · Aud** — **Dado que** el alta se completa, **cuando** se consulta el expediente, **entonces** registra quién y cuándo la realizó.

### SIGE-US-009 — Guardar y completar un registro incompleto
- **CA-009-01 · Alt** — **Dado que** faltan datos obligatorios distintos al tutor pero se cumplen los requisitos mínimos `[⚠ A-14]`, **cuando** el PAD guarda, **entonces** el registro se guarda como **incompleto** y la ficha lista los campos faltantes.
- **CA-009-02 · Neg** — **Dado que** no se cumplen los requisitos mínimos, **cuando** el PAD intenta guardar, **entonces** no se guarda nada.
- **CA-009-03 · UX** — **Dado que** un registro es incompleto, **cuando** aparece en listas o en su ficha, **entonces** muestra la insignia "Incompleto".
- **CA-009-04 · Feliz** — **Dado que** el PAD completa el último campo faltante, **cuando** guarda, **entonces** la insignia desaparece.
- **CA-009-05 · Neg** — **Dado que** un registro incompleto no tiene fotografía, **cuando** se solicita exportar credenciales, **entonces** se excluye y se lista como pendiente (RN-CRE-01).
- **CA-009-06 · Neg** — **Dado que** el registro no tiene tutor, **cuando** se intenta guardar como incompleto, **entonces** se rechaza: el tutor nunca es opcional.

### SIGE-US-010 — Asociar y administrar tutores de un estudiante
- **CA-010-01 · Feliz** — **Dado que** un estudiante tiene ficha, **cuando** el PAD agrega un tutor con nombre, relación, teléfono y correo válidos, **entonces** queda asociado al estudiante.
- **CA-010-02 · Feliz** — **Dado que** hay dos tutores, **cuando** el PAD marca uno como contacto principal, **entonces** solo uno queda como principal.
- **CA-010-03 · Neg** — **Dado que** el estudiante `ACTIVO` tiene un único tutor válido, **cuando** se intenta eliminarlo o invalidarlo, **entonces** se rechaza.
- **CA-010-04 · Neg** — **Dado que** el correo tiene formato inválido, **cuando** se guarda, **entonces** se señala el error.
- **CA-010-05 · Perm** — **Dado que** el usuario no es PAD/ADM, **cuando** intenta modificar tutores, **entonces** se deniega; los roles sin acceso al expediente tampoco los consultan.
- **CA-010-06 · Neg** — **Dado que** una comunicación va dirigida a un tutor no marcado como válido, **cuando** se intenta enviar, **entonces** se rechaza (RN-COM-01).

### SIGE-US-011 — Consultar y filtrar expedientes
- **CA-011-01 · Feliz** — **Dado que** un PRE/PAD/ADM abre el listado, **cuando** filtra por nombre, matrícula, grupo, grado o estatus, **entonces** obtiene resultados paginados que cumplen.
- **CA-011-02 · Feliz** — **Dado que** aplica varios filtros a la vez, **cuando** consulta, **entonces** se combinan.
- **CA-011-03 · Alt** — **Dado que** un estudiante está en `BAJA` o `EGRESADO`, **cuando** un rol autorizado filtra por ese estatus, **entonces** el expediente aparece con su historial completo.
- **CA-011-04 · Perm** — **Dado que** el usuario es DOC o SL, **cuando** intenta consultar expedientes, **entonces** se deniega.
- **CA-011-05 · UX** — **Dado que** el consentimiento de un tutor está `PENDIENTE`, **cuando** un rol autorizado abre el expediente, **entonces** ve una advertencia sin que se bloquee la consulta.
- **CA-011-06 · UX** — **Dado que** no hay coincidencias, **cuando** se aplica el filtro, **entonces** se muestra un estado vacío; en móvil los resultados se presentan como tarjetas.

### SIGE-US-012 — Modificar los datos de un estudiante
- **CA-012-01 · Feliz** — **Dado que** el PAD edita un dato no inmutable, **cuando** guarda, **entonces** se actualiza la ficha.
- **CA-012-02 · Neg** — **Dado que** la ficha ya tiene matrícula, **cuando** el usuario intenta cambiarla por la edición normal, **entonces** el campo está bloqueado y la API rechaza el cambio.
- **CA-012-03 · Alt** — **Dado que** hay un error de matrícula, **cuando** un PAD/ADM usa la corrección excepcional con motivo, **entonces** se aplica y queda en bitácora con valor anterior y nuevo.
- **CA-012-04 · Neg** — **Dado que** la matrícula corregida ya existe en otro estudiante, **cuando** se guarda, **entonces** se rechaza.
- **CA-012-05 · Perm** — **Dado que** el usuario no es PAD/ADM, **cuando** intenta modificar datos, **entonces** se deniega.

### SIGE-US-013 — Cambiar grupo o ciclo conservando el historial
- **CA-013-01 · Feliz** — **Dado que** un estudiante `ACTIVO` está en un grupo, **cuando** el PAD lo cambia a otro con fecha efectiva, **entonces** la ficha refleja el grupo nuevo.
- **CA-013-02 · Feliz** — **Dado que** el cambio se realizó, **cuando** se consulta la asistencia de fechas anteriores al cambio, **entonces** siguen asociadas al grupo anterior.
- **CA-013-03 · UX** — **Dado que** hubo cambios de grupo, **cuando** se abre la ficha, **entonces** el historial de grupos se muestra con fechas.
- **CA-013-04 · Neg** — **Dado que** el grupo destino no existe en el catálogo o está desactivado, **cuando** se intenta el cambio, **entonces** se rechaza.
- **CA-013-05 · Perm** — **Dado que** el usuario no es PAD/ADM, **cuando** intenta el cambio, **entonces** se deniega.

### SIGE-US-014 — Dar de baja o registrar egreso de un estudiante
- **CA-014-01 · Feliz** — **Dado que** un estudiante está `ACTIVO`, **cuando** el PAD lo pasa a `BAJA` o `EGRESADO` y confirma, **entonces** cambia el estatus, se conserva el expediente y el cambio queda auditado.
- **CA-014-02 · Neg** — **Dado que** el estudiante está en `BAJA`, **cuando** se intenta pasarlo a `EGRESADO`, **entonces** se rechaza por transición no válida.
- **CA-014-03 · Neg** — **Dado que** el estudiante está en `BAJA` o `EGRESADO`, **cuando** se intenta registrar asistencia o un reporte nuevo, **entonces** se rechaza (RN-EST-05).
- **CA-014-04 · Feliz** — **Dado que** un estudiante pasó a `BAJA`, **cuando** corre la verificación de ausencias, **entonces** no se le genera `FALTÓ`.
- **CA-014-05 · Feliz** — **Dado que** el estudiante está en `BAJA`, **cuando** un rol autorizado consulta su historial, **entonces** ve todos sus registros anteriores; ninguno se eliminó.
- **CA-014-06 · UX** — **Dado que** el PAD inicia la baja, **cuando** se abre la confirmación, **entonces** se explica que dejará de aparecer en asistencia y reportes nuevos.

### SIGE-US-015 — Reingresar a un estudiante dado de baja
- **CA-015-01 · Feliz** — **Dado que** un estudiante está en `BAJA` y conserva un tutor válido, **cuando** un ADM autoriza explícitamente el reingreso con motivo, **entonces** pasa a `ACTIVO` y se registra un evento de reingreso distinto del alta original.
- **CA-015-02 · Perm** — **Dado que** el actor es PAD u otro rol distinto de ADM, **cuando** intenta reactivar, **entonces** se rechaza.
- **CA-015-03 · Neg** — **Dado que** el estudiante no tiene tutor válido, **cuando** el ADM intenta reactivarlo, **entonces** se rechaza hasta que lo tenga (RN-EST-03).
- **CA-015-04 · Aud** — **Dado que** el reingreso se completó, **cuando** se consulta la bitácora, **entonces** aparece un registro diferenciado de auditoría.
- **CA-015-05 · Neg** — **Dado que** el estudiante está en `EGRESADO`, **cuando** se intenta reingresar, **entonces** se rechaza `[⚠ A-05]`.

### SIGE-US-016 — Registrar y consultar el consentimiento del tutor
- **CA-016-01 · Feliz** — **Dado que** un tutor está asociado a un estudiante, **cuando** el PAD registra su consentimiento como `OTORGADO`, **entonces** se guarda estatus y fecha de registro.
- **CA-016-02 · Feliz** — **Dado que** el consentimiento se documentó fuera de SIGE (formato físico), **cuando** el PAD captura solo el estatus, **entonces** se acepta sin requerir adjuntos.
- **CA-016-03 · UX** — **Dado que** el estatus es `PENDIENTE`, **cuando** un rol autorizado consulta el expediente, **entonces** ve la advertencia.
- **CA-016-04 · Alt** — **Dado que** el estatus cambia a `REVOCADO`, **cuando** se guarda, **entonces** queda la fecha del cambio y el historial previo `[⚠ A-05: efecto operativo pendiente]`.
- **CA-016-05 · Neg** — **Dado que** se intenta un valor distinto de `PENDIENTE`, `OTORGADO` o `REVOCADO`, **cuando** se guarda, **entonces** se rechaza.
- **CA-016-06 · Perm** — **Dado que** el rol no tiene acceso al expediente, **cuando** intenta ver o cambiar el consentimiento, **entonces** se deniega.

---

# EP-03 — Importación masiva de estudiantes

### SIGE-US-017 — Descargar la plantilla de importación
- **CA-017-01 · Feliz** — **Dado que** el usuario abre la importación, **cuando** pulsa "Descargar plantilla", **entonces** obtiene un CSV/XLSX con las columnas exactas del diccionario de datos vigente.
- **CA-017-02 · Feliz** — **Dado que** descarga la plantilla, **cuando** la abre, **entonces** contiene ejemplos de formato válido.
- **CA-017-03 · UX** — **Dado que** se muestra la pantalla de importación, **cuando** el usuario aún no selecciona archivo, **entonces** la opción de plantilla está visible antes del selector.
- **CA-017-04 · Aud** — **Dado que** se actualiza el diccionario, **cuando** se descarga la plantilla, **entonces** refleja la versión vigente.
- **CA-017-05 · Perm** — **Dado que** el rol no es PAD/ADM, **cuando** intenta acceder a la importación, **entonces** se deniega.

### SIGE-US-018 — Cargar un archivo y validar su estructura
- **CA-018-01 · Feliz** — **Dado que** el archivo `.csv` o `.xlsx` cumple exactamente el diccionario (columnas, tipos, formato), **cuando** se carga, **entonces** SIGE continúa al procesamiento de filas.
- **CA-018-02 · Neg** — **Dado que** falta una columna o su nombre no coincide, **cuando** se carga, **entonces** se rechaza el archivo **completo** antes de procesar filas, indicando qué columnas fallan.
- **CA-018-03 · Neg** — **Dado que** el tipo de una columna no corresponde (p. ej. texto donde va fecha en el encabezado/estructura), **cuando** se carga, **entonces** se rechaza el archivo completo.
- **CA-018-04 · Neg** — **Dado que** el formato de archivo no es CSV ni XLSX, **cuando** se intenta cargar, **entonces** se rechaza.
- **CA-018-05 · Neg** — **Dado que** la estructura es inválida, **cuando** se rechaza el archivo, **entonces** no se persiste ningún registro.
- **CA-018-06 · Perm** — **Dado que** el rol no es PAD/ADM `[⚠ A-15]`, **cuando** intenta cargar un archivo, **entonces** se deniega.

### SIGE-US-019 — Procesar cada fila de forma independiente
- **CA-019-01 · Feliz** — **Dado que** el archivo tiene filas válidas e inválidas, **cuando** se procesa, **entonces** las válidas quedan listas para insertar y las inválidas se descartan sin afectar a las demás.
- **CA-019-02 · Neg** — **Dado que** una fila tiene una matrícula ya existente, **cuando** se procesa, **entonces** se rechaza como duplicada y jamás sobrescribe al estudiante existente.
- **CA-019-03 · Neg** — **Dado que** dos filas del mismo archivo repiten matrícula, **cuando** se procesan, **entonces** solo la primera válida avanza y la otra se reporta como duplicada.
- **CA-019-04 · Neg** — **Dado que** una fila no incluye un tutor válido, **cuando** se procesa, **entonces** se descarta y ninguno de sus datos se guarda.
- **CA-019-05 · Neg** — **Dado que** una fila tiene un campo con formato inválido, **cuando** se procesa, **entonces** el reporte registra fila, campo, tipo de error y descripción.
- **CA-019-06 · Alt** — **Dado que** el proceso termina la última fila, **cuando** existen filas descartadas, **entonces** se muestra el reporte de filas descartadas al terminar.

### SIGE-US-020 — Revisar la vista previa y confirmar la importación
- **CA-020-01 · Feliz** — **Dado que** el procesamiento terminó, **cuando** SIGE muestra la vista previa, **entonces** indica cuántos registros se insertarán y cuántos se rechazarán.
- **CA-020-02 · Neg** — **Dado que** el usuario aún no confirma, **cuando** se consulta la base de datos, **entonces** no existe ningún estudiante nuevo persistido por esa importación.
- **CA-020-03 · Feliz** — **Dado que** el usuario confirma la importación definitiva, **cuando** se ejecuta, **entonces** se generan las fichas de los registros válidos en estatus `ACTIVO`, asignadas a su grupo y ciclo.
- **CA-020-04 · Alt** — **Dado que** el usuario cancela, **cuando** confirma la cancelación, **entonces** la importación termina y no se persiste ningún dato.
- **CA-020-05 · Neg** — **Dado que** ninguna fila es válida, **cuando** llega a la vista previa, **entonces** no se ofrece confirmar (o se advierte que no hay nada que insertar).
- **CA-020-06 · Neg** — **Dado que** durante la confirmación otro proceso creó una de las matrículas `[⚠ A-15]`, **cuando** se confirma, **entonces** el sistema no sobrescribe y reporta el conflicto.

### SIGE-US-021 — Descargar el reporte de resultados de la importación
- **CA-021-01 · Feliz** — **Dado que** finalizó la importación, **cuando** se abre el reporte, **entonces** muestra total procesadas, insertadas y con error.
- **CA-021-02 · Feliz** — **Dado que** hubo filas con error, **cuando** el usuario descarga el reporte, **entonces** cada fila con error incluye el número de fila, la columna y el motivo.
- **CA-021-03 · Límite** — **Dado que** todas las filas fueron válidas, **cuando** se abre el reporte, **entonces** el total de errores es 0 y el detalle está vacío.
- **CA-021-04 · Feliz** — **Dado que** total procesadas = insertadas + con error, **cuando** se verifica el reporte, **entonces** las cifras coinciden.
- **CA-021-05 · Perm** — **Dado que** un rol no autorizado conoce el enlace del reporte, **cuando** intenta descargarlo, **entonces** se deniega.

---

# EP-04 — Identificación QR y credenciales

### SIGE-US-022 — Generar el QR único de un estudiante
- **CA-022-01 · Feliz** — **Dado que** un estudiante `ACTIVO` no tiene QR vigente, **cuando** el personal autorizado lo genera, **entonces** se crea un token único, un QR que codifica solo ese token, se asocia al estudiante y queda `VIGENTE`.
- **CA-022-02 · Neg** — **Dado que** el payload del QR se decodifica, **cuando** se inspecciona, **entonces** no contiene nombre, matrícula visible ni CURP, solo el token opaco.
- **CA-022-03 · Neg** — **Dado que** el estudiante ya tiene un QR vigente, **cuando** se intenta generar otro sin revocar, **entonces** se rechaza (o se trata como reemplazo, US-024).
- **CA-022-04 · Alt** — **Dado que** el token candidato ya existe entre los vigentes **o** revocados, **cuando** se valida, **entonces** se incrementa el contador de colisiones y se genera otro candidato.
- **CA-022-05 · Límite** — **Dado que** se llegan al máximo configurado (5) de colisiones, **cuando** ocurre el siguiente intento, **entonces** se alerta al ADM, se aborta el proceso y no se guarda ningún QR.
- **CA-022-06 · Neg** — **Dado que** el formato o la longitud del token candidato es inválido, **cuando** se valida, **entonces** se descarta y se genera otro.
- **CA-022-07 · Neg** — **Dado que** el estudiante no está `ACTIVO`, **cuando** se intenta generar el QR, **entonces** se rechaza.
- **CA-022-08 · Aud** — **Dado que** se generó el QR, **cuando** se consulta su historial, **entonces** registra estudiante, token, fecha/hora, usuario, estado y origen (alta inicial).
- **CA-022-09 · Feliz** — **Dado que** se generan QR para el lote de pruebas, **cuando** se verifica, **entonces** 100 % tiene QR único y 0 identificadores duplicados.

### SIGE-US-023 — Validar la integridad del lote de QR
- **CA-023-01 · Feliz** — **Dado que** todos los estudiantes `ACTIVO` tienen un único QR vigente, **cuando** el ADM ejecuta la validación, **entonces** el resultado es 0 duplicados, 0 huérfanos y el lote pasa a `HABILITADO`.
- **CA-023-02 · Neg** — **Dado que** existe un token repetido, **cuando** se ejecuta la validación, **entonces** el lote queda `BLOQUEADO` y se lista el duplicado.
- **CA-023-03 · Neg** — **Dado que** existe un QR sin estudiante asociado o un estudiante `ACTIVO` sin QR, **cuando** se valida, **entonces** se reportan como huérfanos y el lote no se habilita.
- **CA-023-04 · Neg** — **Dado que** el lote está `BLOQUEADO`, **cuando** se intenta exportar credenciales, **entonces** se rechaza.
- **CA-023-05 · Perm** — **Dado que** el actor no es ADM, **cuando** intenta ejecutar la validación, **entonces** se deniega.
- **CA-023-06 · Feliz** — **Dado que** la validación terminó, **cuando** el ADM abre el reporte, **entonces** puede descargarlo con fecha y resultado.

### SIGE-US-024 — Revocar y reemplazar el QR de un estudiante
- **CA-024-01 · Feliz** — **Dado que** el ADM registra el motivo (pérdida, robo, daño o duplicidad) de un estudiante con QR vigente, **cuando** confirma, **entonces** el QR pasa a `REVOCADO` con fecha, usuario y motivo, y se genera uno nuevo `VIGENTE` enlazado al anterior.
- **CA-024-02 · Perm** — **Dado que** el actor no es ADM, **cuando** intenta revocar o regenerar (UI o API), **entonces** se rechaza con "Se requiere autorización de rol Administrador" y no hay cambios.
- **CA-024-03 · Neg** — **Dado que** un QR fue revocado, **cuando** se escanea después, **entonces** se rechaza y se alerta al operador aunque el estudiante siga `ACTIVO`.
- **CA-024-04 · Neg** — **Dado que** un token fue revocado, **cuando** se genera cualquier nuevo QR para cualquier estudiante, **entonces** nunca se reutiliza ese token.
- **CA-024-05 · Alt** — **Dado que** el estudiante no tiene QR vigente, **cuando** el ADM solicita el reemplazo, **entonces** se omite la revocación y se genera el nuevo QR.
- **CA-024-06 · Aud** — **Dado que** se revocó un QR, **cuando** se consulta la bitácora y el histórico, **entonces** ambos conservan la referencia al identificador revocado y a su reemplazo.
- **CA-024-07 · Neg** — **Dado que** falta el motivo, **cuando** el ADM intenta confirmar, **entonces** se rechaza.

### SIGE-US-025 — Exportar el QR para la credencial física
- **CA-025-01 · Feliz** — **Dado que** un estudiante `ACTIVO` tiene QR vigente y fotografía, **cuando** el PAD exporta, **entonces** obtiene su QR en alta resolución/PDF.
- **CA-025-02 · Neg** — **Dado que** un estudiante no cumple alguna condición (no `ACTIVO`, sin QR vigente o sin foto), **cuando** se exporta el lote, **entonces** se excluye del PDF y aparece en el listado de pendientes con el motivo.
- **CA-025-03 · Feliz** — **Dado que** el lote se exporta, **cuando** se verifica el QR de una muestra, **entonces** 100 % es legible y corresponde al estudiante correcto.
- **CA-025-04 · Neg** — **Dado que** un QR está revocado, **cuando** se exporta, **entonces** no aparece en el archivo.
- **CA-025-05 · UX** — **Dado que** se exporta, **cuando** el personal ve el resultado, **entonces** puede distinguir el formato para credencial nueva y el de sticker.
- **CA-025-06 · Perm** — **Dado que** el rol no es PAD/ADM, **cuando** intenta exportar, **entonces** se deniega.

### SIGE-US-026 — Reexportar QR de forma selectiva
- **CA-026-01 · Feliz** — **Dado que** el PAD elige un estudiante o un grupo, **cuando** reexporta, **entonces** solo se genera el QR vigente del subconjunto y no se reexporta el lote completo.
- **CA-026-02 · Feliz** — **Dado que** un QR fue reemplazado por revocación, **cuando** se reexporta a ese estudiante, **entonces** el archivo contiene el nuevo QR (sticker de reposición) y no el revocado.
- **CA-026-03 · Neg** — **Dado que** un estudiante del grupo no cumple RN-CRE-01, **cuando** se reexporta, **entonces** se excluye y se lista como pendiente.
- **CA-026-04 · UX** — **Dado que** el usuario selecciona el subconjunto, **cuando** aún no exporta, **entonces** ve una vista previa de a cuántos estudiantes aplica.

---

# EP-05 — Control de asistencia estudiantil

### SIGE-US-027 — Validar el QR al escanear
- **CA-027-01 · Feliz** — **Dado que** el token es válido, existe, está `VIGENTE` y el estudiante está `ACTIVO`, **cuando** el operador escanea, **entonces** SIGE identifica al estudiante y continúa al registro.
- **CA-027-02 · Neg** — **Dado que** el token tiene formato inválido o no existe, **cuando** se escanea, **entonces** se muestra "QR no reconocido" y no se genera ningún registro.
- **CA-027-03 · Neg** — **Dado que** el QR está revocado, **cuando** se escanea, **entonces** se rechaza automáticamente y se alerta al operador para verificar identidad manualmente.
- **CA-027-04 · Neg** — **Dado que** el estudiante está en `BAJA` o `EGRESADO`, **cuando** se escanea su QR vigente, **entonces** se rechaza el registro.
- **CA-027-05 · UX** — **Dado que** se produce cualquier resultado, **cuando** termina la lectura, **entonces** hay retroalimentación visual y sonora inmediata distinguible entre válido e inválido.
- **CA-027-06 · Límite** — **Dado que** hay conexión a la red local, **cuando** se escanea, **entonces** la validación y confirmación tardan menos de 250 ms (CT-10).
- **CA-027-07 · Perm** — **Dado que** el usuario no es PRE ni PAD, **cuando** intenta usar el escaneo, **entonces** se deniega.
- **CA-027-08 · Feliz** — **Dado que** se usa lector HID o cámara UVC en web, **cuando** se escanea, **entonces** el resultado es equivalente al de la app móvil.

### SIGE-US-028 — Registrar la asistencia y determinar ASISTIÓ o LLEGÓ TARDE
- **CA-028-01 · Límite** — **Dado que** la hora de corte es 08:00, **cuando** el primer escaneo válido ocurre a las 08:00, **entonces** el estado es `ASISTIÓ`.
- **CA-028-02 · Límite** — **Dado que** la hora de corte es 08:00, **cuando** el primer escaneo válido ocurre a las 08:01, **entonces** el estado es `LLEGÓ TARDE`.
- **CA-028-03 · Feliz** — **Dado que** el escaneo es válido y fuera de rebote, **cuando** se registra, **entonces** se guarda estudiante, fecha, hora, grupo, jornada, estado y origen `ESCANEO`.
- **CA-028-04 · Alt** — **Dado que** el estudiante ya tiene `ASISTIÓ` o `LLEGÓ TARDE` ese día y jornada, **cuando** vuelve a escanear fuera de la ventana de rebote, **entonces** el escaneo se guarda como evento adicional sin cambiar el estado ya determinado.
- **CA-028-05 · Alt** — **Dado que** el estudiante ya está en `FALTÓ`, **cuando** escanea, **entonces** se aplica el flujo de reclasificación (US-031).
- **CA-028-06 · Feliz** — **Dado que** el grupo tiene su propia hora de corte, **cuando** se calcula el estado, **entonces** se usa la del grupo y jornada del estudiante.
- **CA-028-07 · Feliz** — **Dado que** el ADM cambia la hora de corte, **cuando** se consultan registros ya determinados, **entonces** conservan su estado (sin efecto retroactivo).
- **CA-028-08 · Feliz** — **Dado que** el registro se guardó, **cuando** se intenta eliminarlo, **entonces** se rechaza; solo puede modificarse vía justificación.
- **CA-028-09 · UX** — **Dado que** se completó el registro, **cuando** se muestra el resultado, **entonces** el operador ve nombre del estudiante y estado resultante.

### SIGE-US-029 — Ignorar escaneos duplicados (rebote)
- **CA-029-01 · Límite** — **Dado que** la ventana es 5 min y hubo un escaneo válido a las 07:50:00, **cuando** el mismo estudiante escanea a las 07:54:59, **entonces** el segundo se ignora.
- **CA-029-02 · Límite** — **Dado que** la ventana es 5 min, **cuando** escanea a las 07:55:01, **entonces** ya no es rebote y se procesa con las reglas normales.
- **CA-029-03 · Feliz** — **Dado que** se ignora un escaneo por rebote, **cuando** ocurre, **entonces** no se crea un segundo registro y el operador ve "registro duplicado".
- **CA-029-04 · Límite** — **Dado que** el ADM configura la ventana, **cuando** ingresa 0 o 31 min, **entonces** se rechaza; 1 y 30 se aceptan.
- **CA-029-05 · Feliz** — **Dado que** el rebote se evalúa por estudiante, **cuando** dos estudiantes distintos escanean en la misma ventana, **entonces** ambos se procesan.
- **CA-029-06 · Alt** — **Dado que** un evento offline se sincroniza, **cuando** cae dentro de la ventana de un escaneo previo del mismo estudiante, **entonces** también se descarta como rebote.

### SIGE-US-030 — Marcar automáticamente FALTÓ a quien no registró entrada
- **CA-030-01 · Feliz** — **Dado que** llegó la hora de verificación (10:00 inicial) y un estudiante `ACTIVO` programado no tiene registro válido de entrada, **cuando** corre el proceso, **entonces** se le asigna `FALTÓ` con origen `AUTOMÁTICO`.
- **CA-030-02 · Límite** — **Dado que** son las 09:59, **cuando** se consulta a un estudiante sin registro, **entonces** no tiene estado definitivo de ausencia.
- **CA-030-03 · Feliz** — **Dado que** un estudiante tiene `ASISTIÓ` o `LLEGÓ TARDE`, **cuando** corre el proceso, **entonces** no se realiza ninguna acción sobre él.
- **CA-030-04 · Neg** — **Dado que** un estudiante está en `BAJA` o `EGRESADO`, **cuando** corre el proceso, **entonces** se omite.
- **CA-030-05 · Feliz** — **Dado que** el proceso se ejecuta dos veces el mismo día, **cuando** termina, **entonces** no se generan registros duplicados.
- **CA-030-06 · Feliz** — **Dado que** el ADM cambia la hora de verificación, **cuando** rige el nuevo valor, **entonces** el proceso se dispara a la nueva hora y la ausencia de días previos no se recalcula.
- **CA-030-07 · Aud** — **Dado que** se asignó `FALTÓ`, **cuando** se consulta el historial, **entonces** el origen es `AUTOMÁTICO`, distinto de una modificación manual.

### SIGE-US-031 — Reclasificar la asistencia de quien llega después de un FALTÓ automático
- **CA-031-01 · Feliz** — **Dado que** un estudiante quedó `FALTÓ` automático, **cuando** realiza un escaneo válido posterior, **entonces** su estado se actualiza según la hora efectiva del escaneo comparada con la hora de corte `[⚠ A-01]`.
- **CA-031-02 · Aud** — **Dado que** se reclasificó, **cuando** se consulta su expediente, **entonces** aparecen el estado `FALTÓ` previo (automático) y el nuevo con su origen y hora.
- **CA-031-03 · Neg** — **Dado que** se reclasificó, **cuando** se revisan los registros del día, **entonces** no existe un segundo registro de entrada para la misma fecha y jornada.
- **CA-031-04 · Aud** — **Dado que** la reclasificación ocurrió por escaneo, **cuando** se revisa el historial, **entonces** se distingue de una justificación manual.
- **CA-031-05 · Neg** — **Dado que** el estudiante ya no está `ACTIVO`, **cuando** escanea, **entonces** se rechaza (no reclasifica).
- **CA-031-06 · Neg** — **Dado que** el escaneo cae dentro de la ventana de rebote de otro previo, **cuando** llega, **entonces** se ignora sin cambios.

### SIGE-US-032 — Capturar asistencia sin conexión al servidor (app móvil)
- **CA-032-01 · Feliz** — **Dado que** el dispositivo perdió conexión con el servidor, **cuando** el operador escanea, **entonces** el evento se almacena localmente con fecha, hora, tipo y QR leído, marcado `PENDIENTE DE VALIDACIÓN`.
- **CA-032-02 · UX** — **Dado que** hay eventos pendientes, **cuando** el operador ve la pantalla, **entonces** un indicador persistente muestra "sin conexión" y el número de pendientes.
- **CA-032-03 · Límite** — **Dado que** el buffer tiene 999 eventos, **cuando** se captura el 1,000.º, **entonces** se almacena.
- **CA-032-04 · Límite** — **Dado que** el buffer tiene 1,000 eventos, **cuando** se intenta capturar otro, **entonces** se rechaza con alerta de buffer lleno `[⚠ A-13]`.
- **CA-032-05 · Neg** — **Dado que** un evento está pendiente, **cuando** se consulta el historial definitivo, **entonces** no aparece como registro definitivo.
- **CA-032-06 · Feliz** — **Dado que** no hay conexión, **cuando** el operador consulta el resultado del escaneo, **entonces** se le informa que quedó pendiente, no confirmado.

### SIGE-US-033 — Sincronizar y validar los eventos capturados sin conexión
- **CA-033-01 · Feliz** — **Dado que** hay eventos pendientes, **cuando** se restablece la conexión, **entonces** se sincronizan automáticamente sin intervención del operador.
- **CA-033-02 · Feliz** — **Dado que** el backend valida un evento (identidad, estatus `ACTIVO`, QR vigente, unicidad y rebote) y es correcto, **cuando** se procesa, **entonces** se incorpora al historial definitivo con el estado calculado a partir de la hora de captura `[⚠ A-18]`.
- **CA-033-03 · Neg** — **Dado que** el estudiante pasó a `BAJA` durante la desconexión, **cuando** se sincroniza su evento, **entonces** se descarta y se notifica al operador con motivo.
- **CA-033-04 · Neg** — **Dado que** el QR fue revocado durante la desconexión, **cuando** se sincroniza, **entonces** se descarta y se notifica.
- **CA-033-05 · Neg** — **Dado que** el evento duplica otro por regla de rebote, **cuando** se sincroniza, **entonces** se descarta y se notifica como duplicado.
- **CA-033-06 · Alt** — **Dado que** el estudiante ya fue marcado `FALTÓ` a las 10:00 y su evento offline llega después, **cuando** se sincroniza y es válido, **entonces** se aplica US-031.
- **CA-033-07 · Alt** — **Dado que** el servidor vuelve a fallar durante la sincronización, **cuando** ocurre, **entonces** los eventos no enviados permanecen en el buffer y se reintentan.
- **CA-033-08 · UX** — **Dado que** terminó la sincronización, **cuando** el operador ve el resumen, **entonces** muestra cuántos se aceptaron y cuántos se descartaron.

### SIGE-US-034 — Justificar o modificar la asistencia de un estudiante
- **CA-034-01 · Feliz** — **Dado que** un PAD/ADM selecciona un registro `FALTÓ`, **cuando** captura motivo y confirma la justificación, **entonces** el estado pasa a `FALTA JUSTIFICADA` `[⚠ A-07]`.
- **CA-034-02 · Aud** — **Dado que** se modificó un registro, **cuando** se consulta su trazabilidad, **entonces** conserva estado anterior, nuevo, usuario, fecha/hora, motivo y origen `MANUAL`.
- **CA-034-03 · Neg** — **Dado que** el motivo está vacío, **cuando** se intenta confirmar, **entonces** se rechaza.
- **CA-034-04 · Perm** — **Dado que** el usuario es PRE, DOC o SL, **cuando** intenta modificar asistencia (UI o API), **entonces** se rechaza.
- **CA-034-05 · Neg** — **Dado que** existe un registro de asistencia, **cuando** alguien intenta eliminarlo, **entonces** se rechaza.
- **CA-034-06 · Alt** — **Dado que** el registro previo era automático, **cuando** el PAD lo modifica, **entonces** el historial muestra ambos cambios con orígenes distintos.
- **CA-034-07 · Feliz** — **Dado que** el PAD usa la app móvil, **cuando** justifica una falta, **entonces** se aplican las mismas reglas que en web (CT-04).

### SIGE-US-035 — Consultar la asistencia diaria de un grupo
- **CA-035-01 · Feliz** — **Dado que** el usuario selecciona fecha y grupo, **cuando** consulta, **entonces** ve la relación completa de estudiantes con su estado.
- **CA-035-02 · Feliz** — **Dado que** la fecha es anterior, **cuando** consulta, **entonces** el historial de esa fecha está íntegro.
- **CA-035-03 · Feliz** — **Dado que** el usuario filtra por estado, **cuando** aplica el filtro, **entonces** solo aparecen los estudiantes con ese estado.
- **CA-035-04 · UX** — **Dado que** un estado fue automático o manual, **cuando** se muestra, **entonces** el origen es visible para roles autorizados.
- **CA-035-05 · UX** — **Dado que** no hay registros para el día, **cuando** se consulta, **entonces** se muestra estado vacío.
- **CA-035-06 · Perm** — **Dado que** el rol no tiene acceso a asistencia detallada (DOC o SL), **cuando** intenta la consulta, **entonces** se deniega.
- **CA-035-07 · Feliz** — **Dado que** el estudiante cambió de grupo, **cuando** se consulta el grupo anterior en una fecha previa al cambio, **entonces** sigue apareciendo en él.

### SIGE-US-036 — Consultar el historial individual de asistencia
- **CA-036-01 · Feliz** — **Dado que** el usuario elige un estudiante y un periodo, **cuando** consulta, **entonces** ve estado, hora y origen por fecha.
- **CA-036-02 · Feliz** — **Dado que** hubo justificaciones, **cuando** un rol con permiso consulta, **entonces** ve las modificaciones con su trazabilidad.
- **CA-036-03 · Feliz** — **Dado que** se comparan la vista por grupo y la individual de una misma fecha, **cuando** se revisan, **entonces** coinciden.
- **CA-036-04 · Feliz** — **Dado que** el estudiante está en `BAJA`, **cuando** un rol autorizado consulta, **entonces** ve su historial completo.
- **CA-036-05 · Perm** — **Dado que** el rol no tiene acceso, **cuando** consulta, **entonces** se deniega.
- **CA-036-06 · UX** — **Dado que** el periodo no tiene registros, **cuando** se consulta, **entonces** se muestra estado vacío.

### SIGE-US-037 — Obtener información consolidada de asistencia
- **CA-037-01 · Feliz** — **Dado que** el usuario elige estudiante, grupo o periodo, **cuando** consulta, **entonces** ve conteos por estado y porcentajes.
- **CA-037-02 · Feliz** — **Dado que** hay información, **cuando** el usuario la exporta, **entonces** obtiene un archivo con los mismos datos.
- **CA-037-03 · Feliz** — **Dado que** se recalcula, **cuando** se modifica una asistencia, **entonces** el consolidado refleja el estado vigente.
- **CA-037-04 · Perm** — **Dado que** el usuario es SL, **cuando** consulta, **entonces** solo ve información consolidada, no datos de menores individuales innecesarios.
- **CA-037-05 · Neg** — **Dado que** la fórmula de evaluación queda fuera del alcance, **cuando** se genera el consolidado, **entonces** no calcula calificaciones.

---

# EP-06 — Control de asistencia del personal docente

### SIGE-US-038 — Registrar a un docente y generar su QR
- **CA-038-01 · Feliz** — **Dado que** el PAD registra a un docente con los datos mínimos, **cuando** genera su QR, **entonces** queda un único QR `VIGENTE` asociado a él.
- **CA-038-02 · Neg** — **Dado que** el docente ya tiene QR vigente, **cuando** se intenta generar otro, **entonces** se rechaza.
- **CA-038-03 · Neg** — **Dado que** el QR de un docente es escaneado en el flujo de estudiantes, **cuando** se lee, **entonces** se rechaza (identificadores independientes).
- **CA-038-04 · Neg** — **Dado que** el QR de un estudiante se escanea en el flujo docente, **cuando** se lee, **entonces** se rechaza (RN-AST-11).
- **CA-038-05 · Feliz** — **Dado que** se registra un docente, **cuando** se revisa, **entonces** no requiere ni crea una cuenta de usuario de SIGE.
- **CA-038-06 · Feliz** — **Dado que** se genera el token, **cuando** se verifica, **entonces** es opaco y sin datos personales (RN-QR-02).

### SIGE-US-039 — Programar días y horarios de asistencia de cada docente
- **CA-039-01 · Feliz** — **Dado que** el PAD captura días, hora de entrada y hora de salida de un docente, **cuando** guarda, **entonces** la programación queda asociada al docente.
- **CA-039-02 · Feliz** — **Dado que** dos docentes tienen programaciones distintas, **cuando** se evalúan, **entonces** cada uno se evalúa con la suya.
- **CA-039-03 · Aud** — **Dado que** se modifica una programación, **cuando** se consulta el historial, **entonces** muestra valor anterior, nuevo, usuario y fecha/hora.
- **CA-039-04 · Neg** — **Dado que** la hora de salida es anterior a la de entrada, **cuando** se guarda, **entonces** se rechaza.
- **CA-039-05 · Alt** — **Dado que** se cambia la programación de un día ya evaluado, **cuando** se guarda, **entonces** no se altera retroactivamente lo ya determinado.
- **CA-039-06 · Perm** — **Dado que** el rol no es PAD, **cuando** intenta editar programaciones, **entonces** se deniega.

### SIGE-US-040 — Registrar la ENTRADA de un docente
- **CA-040-01 · Feliz** — **Dado que** un PAD escanea el QR vigente de un docente con asistencia programada y elige `ENTRADA`, **cuando** la hora cumple el horario esperado, **entonces** se guarda con estado `ASISTIÓ`.
- **CA-040-02 · Límite** — **Dado que** la hora excede el límite establecido de su horario `[⚠ A-10]`, **cuando** se registra, **entonces** el estado es `LLEGÓ TARDE`.
- **CA-040-03 · Neg** — **Dado que** ya existe una `ENTRADA` del docente en esa fecha, **cuando** se intenta otra, **entonces** se rechaza y no se crea registro.
- **CA-040-04 · Alt** — **Dado que** el docente no tiene asistencia programada ese día, **cuando** se registra la `ENTRADA`, **entonces** se guarda el evento sin determinar puntualidad y no se le evalúa ausencia ese día.
- **CA-040-05 · Perm** — **Dado que** el usuario no es PAD, **cuando** intenta registrar asistencia docente, **entonces** se rechaza la operación.
- **CA-040-06 · Neg** — **Dado que** el QR es inválido, revocado o no pertenece a un docente, **cuando** se escanea, **entonces** se rechaza el registro.
- **CA-040-07 · Feliz** — **Dado que** el PAD debe elegir el tipo, **cuando** escanea, **entonces** el sistema no procesa el registro hasta que elige `ENTRADA` o `SALIDA`.
- **CA-040-08 · Feliz** — **Dado que** se guardó la `ENTRADA`, **cuando** se intenta borrarla, **entonces** se rechaza (RN-AST-21).

### SIGE-US-041 — Registrar la SALIDA de un docente
- **CA-041-01 · Feliz** — **Dado que** un PAD escanea el QR vigente y elige `SALIDA`, **cuando** guarda, **entonces** se registra la hora efectiva del escaneo.
- **CA-041-02 · Neg** — **Dado que** ya existe una `SALIDA` ese día, **cuando** se intenta otra, **entonces** se rechaza.
- **CA-041-03 · Feliz** — **Dado que** el horario esperado de salida es 15:00 y el docente sale a las 14:20, **cuando** se registra, **entonces** se conserva 14:20 sin ajustarla.
- **CA-041-04 · Neg** — **Dado que** el docente no registra salida, **cuando** termina la jornada, **entonces** el sistema no genera una salida automática.
- **CA-041-05 · Alt** — **Dado que** no existe `ENTRADA` previa ese día, **cuando** se intenta registrar `SALIDA`, **entonces** se aplica la política definida `[⚠ A-10]`.
- **CA-041-06 · Perm** — **Dado que** el usuario no es PAD, **cuando** intenta registrar, **entonces** se rechaza.

### SIGE-US-042 — Detectar automáticamente las ausencias de docentes
- **CA-042-01 · Feliz** — **Dado que** llegó la hora de verificación docente y un docente con asistencia programada hoy no tiene `ENTRADA`, **cuando** corre el proceso, **entonces** se le asigna `FALTÓ` con origen `AUTOMÁTICO`.
- **CA-042-02 · Neg** — **Dado que** un docente no tiene asistencia programada hoy, **cuando** corre el proceso, **entonces** no se le genera ausencia.
- **CA-042-03 · Feliz** — **Dado que** el docente ya tiene `ENTRADA`, **cuando** corre el proceso, **entonces** no se realiza ninguna acción.
- **CA-042-04 · Feliz** — **Dado que** el ADM configuró una hora de verificación docente distinta de la estudiantil, **cuando** corre el proceso, **entonces** usa la del personal docente.
- **CA-042-05 · Alt** — **Dado que** un docente marcado `FALTÓ` registra después una `ENTRADA` válida ese día, **cuando** se registra, **entonces** el sistema aplica la política de reclasificación una vez definida `[⚠ A-09]`.
- **CA-042-06 · Aud** — **Dado que** se asignó `FALTÓ`, **cuando** se consulta el historial, **entonces** su origen es `AUTOMÁTICO`.

### SIGE-US-043 — Justificar o modificar la asistencia de un docente
- **CA-043-01 · Feliz** — **Dado que** un PAD/ADM selecciona un registro docente, **cuando** captura motivo y confirma, **entonces** se aplica el nuevo estado.
- **CA-043-02 · Aud** — **Dado que** se modificó, **cuando** se consulta, **entonces** conserva usuario, fecha/hora, estado anterior, nuevo, motivo y origen `MANUAL`.
- **CA-043-03 · Neg** — **Dado que** falta el motivo, **cuando** se intenta confirmar, **entonces** se rechaza.
- **CA-043-04 · Perm** — **Dado que** el usuario no es PAD/ADM, **cuando** intenta modificar, **entonces** se rechaza.
- **CA-043-05 · Neg** — **Dado que** existe un registro docente, **cuando** se intenta eliminar físicamente, **entonces** se rechaza.

### SIGE-US-044 — Consultar el historial de asistencia docente
- **CA-044-01 · Feliz** — **Dado que** el usuario elige un docente y un periodo, **cuando** consulta, **entonces** ve por día entrada, salida, estado y origen.
- **CA-044-02 · Feliz** — **Dado que** hay justificaciones, **cuando** consulta, **entonces** las ve con su trazabilidad.
- **CA-044-03 · Feliz** — **Dado que** se consultan fechas antiguas, **cuando** se abre el historial, **entonces** todos los registros siguen disponibles.
- **CA-044-04 · Perm** — **Dado que** el rol no es PAD/ADM, **cuando** intenta consultar, **entonces** se deniega.
- **CA-044-05 · UX** — **Dado que** no hay registros en el periodo, **cuando** se consulta, **entonces** se muestra estado vacío.

---

# EP-07 — Reportes escolares

### SIGE-US-045 — Registrar un reporte escolar
- **CA-045-01 · Feliz** — **Dado que** un DOC elige un estudiante `ACTIVO`, tipo, gravedad, opciones y una observación válida, **cuando** envía, **entonces** el reporte se guarda con estado `REGISTRADO POR DOCENTE` y queda disponible para el prefecto.
- **CA-045-02 · Límite** — **Dado que** la observación tiene 49 caracteres, **cuando** intenta guardar, **entonces** se rechaza; con 50 y con 100 se acepta.
- **CA-045-03 · Límite** — **Dado que** la observación tiene 101 caracteres, **cuando** intenta guardar, **entonces** se rechaza.
- **CA-045-04 · UX** — **Dado que** el docente escribe la observación, **cuando** teclea, **entonces** un contador de caracteres visible se actualiza.
- **CA-045-05 · Neg** — **Dado que** el estudiante no está `ACTIVO`, **cuando** se intenta registrar, **entonces** se rechaza.
- **CA-045-06 · Perm** — **Dado que** el usuario no es DOC, **cuando** intenta registrar, **entonces** se rechaza.
- **CA-045-07 · Neg** — **Dado que** el reporte ya fue enviado al prefecto, **cuando** se intenta modificar tipo o gravedad, **entonces** se rechaza.
- **CA-045-08 · Feliz** — **Dado que** el docente elige tipo y gravedad, **cuando** avanza, **entonces** solo aparecen las opciones predeterminadas correspondientes a esa combinación.
- **CA-045-09 · Feliz** — **Dado que** el registro se hace desde el móvil, **cuando** se compara con web, **entonces** las validaciones y datos son idénticos (CT-04).

### SIGE-US-046 — Consultar la bandeja y el estado de los reportes
- **CA-046-01 · Perm** — **Dado que** un DOC abre su bandeja, **cuando** consulta, **entonces** solo ve los reportes que él registró.
- **CA-046-02 · Feliz** — **Dado que** PAD o ADM abren la bandeja, **cuando** consultan, **entonces** ven todos los reportes filtrables por tipo, gravedad, grupo, estudiante y estado.
- **CA-046-03 · Feliz** — **Dado que** el PRE abre su bandeja, **cuando** consulta, **entonces** ve los reportes que le corresponden `[⚠ A-12]` con los mismos filtros.
- **CA-046-04 · Perm** — **Dado que** un reporte es visible para un rol que no puede canalizar o autorizar, **cuando** intenta la acción, **entonces** se rechaza.
- **CA-046-05 · Perm** — **Dado que** un DOC conoce el ID de un reporte ajeno, **cuando** lo solicita por URL/API, **entonces** se deniega.
- **CA-046-06 · UX** — **Dado que** no hay reportes o falla la carga, **cuando** se abre, **entonces** se muestra estado vacío o de error con reintento.

### SIGE-US-047 — Revisar un reporte y canalizarlo o rechazarlo (prefecto)
- **CA-047-01 · Feliz** — **Dado que** el reporte está `REGISTRADO POR DOCENTE`, **cuando** el PRE lo aprueba, **entonces** pasa a `REVISADO POR PREFECTO`.
- **CA-047-02 · Feliz** — **Dado que** está `REVISADO POR PREFECTO`, **cuando** el PRE ejecuta la acción de canalizar, **entonces** pasa a `CANALIZADO` y aparece en la bandeja de PAD.
- **CA-047-03 · Neg** — **Dado que** el reporte no ha sido revisado, **cuando** se intenta canalizar directamente, **entonces** se rechaza (no se saltan etapas).
- **CA-047-04 · Alt** — **Dado que** el PRE rechaza el reporte, **cuando** captura el motivo, **entonces** pasa a `RECHAZADO` y se notifica al docente autor.
- **CA-047-05 · Neg** — **Dado que** el PRE rechaza, **cuando** deja el motivo vacío, **entonces** se rechaza la acción.
- **CA-047-06 · Aud** — **Dado que** cambia la etapa, **cuando** se consulta la trazabilidad, **entonces** hay una entrada con usuario y fecha/hora.
- **CA-047-07 · Perm** — **Dado que** el usuario no es PRE, **cuando** intenta revisar o canalizar, **entonces** se rechaza.
- **CA-047-08 · Alt** — **Dado que** PAD devolvió un reporte, **cuando** llega al PRE, **entonces** puede valorarlo de nuevo.

### SIGE-US-048 — Corregir un reporte rechazado mediante uno nuevo referenciado
- **CA-048-01 · Feliz** — **Dado que** el docente recibe un rechazo, **cuando** abre la notificación, **entonces** ve el motivo registrado.
- **CA-048-02 · Feliz** — **Dado que** decide corregir, **cuando** registra un reporte nuevo, **entonces** queda referenciado explícitamente al original, que permanece sin modificación y archivado.
- **CA-048-03 · Alt** — **Dado que** decide no corregir, **cuando** cierra la notificación, **entonces** el original permanece `RECHAZADO` y no se genera reporte nuevo.
- **CA-048-04 · Feliz** — **Dado que** se registra el reporte nuevo, **cuando** entra al flujo, **entonces** pasa por todas las validaciones de registro (rango de observación, tipo, gravedad).
- **CA-048-05 · Neg** — **Dado que** el reporte original está `RECHAZADO`, **cuando** se intenta editarlo, **entonces** se rechaza.
- **CA-048-06 · Perm** — **Dado que** un DOC distinto del autor, **cuando** intenta referenciar el reporte, **entonces** se rechaza.

### SIGE-US-049 — Revisar reportes canalizados y aprobarlos o devolverlos (administrativo)
- **CA-049-01 · Feliz** — **Dado que** el reporte está `CANALIZADO`, **cuando** el PAD lo aprueba, **entonces** pasa a `REVISADO POR ADMINISTRATIVO`.
- **CA-049-02 · Alt** — **Dado que** el PAD lo rechaza con motivo, **cuando** confirma, **entonces** pasa a `RECHAZADO` y regresa a la bandeja del prefecto `[⚠ A-11]`.
- **CA-049-03 · Neg** — **Dado que** el motivo está vacío, **cuando** rechaza, **entonces** se rechaza la acción.
- **CA-049-04 · Neg** — **Dado que** el reporte no está `CANALIZADO`, **cuando** el PAD intenta revisarlo, **entonces** se rechaza.
- **CA-049-05 · Perm** — **Dado que** el usuario es PRE o DOC, **cuando** intenta la revisión administrativa, **entonces** se rechaza.
- **CA-049-06 · Aud** — **Dado que** hay un cambio de etapa, **cuando** se consulta el historial, **entonces** se registra.

### SIGE-US-050 — Decidir si un reporte se comunica a la familia o se resuelve internamente
- **CA-050-01 · Feliz** — **Dado que** el reporte está `REVISADO POR ADMINISTRATIVO`, **cuando** el PAD decide comunicarlo, **entonces** queda autorizado y SIGE verifica que exista un contacto válido.
- **CA-050-02 · Neg** — **Dado que** no hay contacto familiar válido, **cuando** se autoriza, **entonces** el reporte queda `AUTORIZADO` pendiente de contacto y no se envía nada.
- **CA-050-03 · Alt** — **Dado que** el PAD decide que no requiere comunicación, **cuando** registra el motivo, **entonces** el reporte pasa a `RESUELTO` `[⚠ A-11]`.
- **CA-050-04 · Neg** — **Dado que** el PAD decide no comunicar, **cuando** omite el motivo, **entonces** se rechaza.
- **CA-050-05 · Perm** — **Dado que** el usuario es DOC o PRE, **cuando** intenta comunicar a la familia, **entonces** se rechaza (nunca desde el registro del docente ni la revisión del prefecto).
- **CA-050-06 · UX** — **Dado que** el consentimiento del tutor está `PENDIENTE`, **cuando** el PAD decide, **entonces** ve la advertencia.

### SIGE-US-051 — Consultar la trazabilidad completa de un reporte
- **CA-051-01 · Feliz** — **Dado que** un reporte recorrió varias etapas, **cuando** un usuario autorizado abre su historial, **entonces** ve cada estado con usuario y fecha/hora.
- **CA-051-02 · Perm** — **Dado que** un DOC abre el historial de su reporte, **cuando** lo consulta, **entonces** ve lo que su rol permite y no el de reportes ajenos.
- **CA-051-03 · Feliz** — **Dado que** un reporte fue rechazado, **cuando** se consulta el historial, **entonces** aparece el rechazo con su motivo y el reporte nuevo referenciado.
- **CA-051-04 · Neg** — **Dado que** existe un reporte, **cuando** alguien intenta eliminarlo, **entonces** se rechaza.
- **CA-051-05 · Feliz** — **Dado que** el 100 % de los reportes de prueba, **cuando** se revisan, **entonces** tienen su flujo completo trazado.

---

# EP-08 — Comunicación con familiares

### SIGE-US-052 — Enviar por correo la comunicación autorizada a la familia
- **CA-052-01 · Feliz** — **Dado que** el reporte está autorizado y hay contacto válido, **cuando** hay Internet y el PAD envía, **entonces** se envía un correo al contacto con solo la información autorizada.
- **CA-052-02 · Neg** — **Dado que** se prepara el mensaje, **cuando** se revisa su contenido, **entonces** nunca incluye el expediente completo del estudiante.
- **CA-052-03 · UX** — **Dado que** el PAD va a enviar, **cuando** abre la vista previa, **entonces** ve exactamente lo que saldrá.
- **CA-052-04 · Neg** — **Dado que** el reporte no pasó por revisión administrativa, **cuando** se intenta enviar, **entonces** se rechaza.
- **CA-052-05 · Neg** — **Dado que** el destinatario no está marcado como válido, **cuando** se intenta enviar, **entonces** se rechaza.
- **CA-052-06 · Feliz** — **Dado que** el envío fue exitoso, **cuando** termina, **entonces** el reporte pasa a `COMUNICADO A FAMILIA` y luego a `RESUELTO`.
- **CA-052-07 · Alt** — **Dado que** no hay Internet, **cuando** se intenta enviar, **entonces** el envío no se completa y el estado se registra sin afectar las funciones internas.

### SIGE-US-053 — Registrar el estado de cada envío y reintentarlo
- **CA-053-01 · Feliz** — **Dado que** se solicita un envío, **cuando** se procesa, **entonces** se registra fecha, hora y estado `PENDIENTE`, `ENVIADO` o `FALLIDO`.
- **CA-053-02 · Alt** — **Dado que** el envío falla, **cuando** se registra, **entonces** el estado permanece `FALLIDO` y aparece la opción de reintento manual.
- **CA-053-03 · Feliz** — **Dado que** el PAD reintenta un envío fallido y tiene éxito, **cuando** termina, **entonces** el estado pasa a `ENVIADO` conservando el intento fallido en el historial.
- **CA-053-04 · Neg** — **Dado que** el estado es `ENVIADO`, **cuando** se muestra al usuario, **entonces** nunca se presenta como "leído".
- **CA-053-05 · Feliz** — **Dado que** el proveedor devuelve información adicional de entrega, **cuando** se conserva, **entonces** no se interpreta como confirmación de lectura.

---

# EP-09 — Panel administrativo

### SIGE-US-054 — Administrar catálogos institucionales
- **CA-054-01 · Feliz** — **Dado que** el ADM abre catálogos, **cuando** agrega o edita un grupo, grado, ciclo, tipo o nivel de gravedad, **entonces** el cambio queda disponible para el resto del sistema.
- **CA-054-02 · Perm** — **Dado que** el usuario no es ADM, **cuando** intenta modificar un catálogo, **entonces** se rechaza.
- **CA-054-03 · Alt** — **Dado que** un elemento tiene historial asociado, **cuando** el ADM intenta eliminarlo, **entonces** se ofrece desactivarlo y el historial no se altera.
- **CA-054-04 · Neg** — **Dado que** ya existe un elemento con el mismo nombre en el catálogo, **cuando** se guarda otro igual, **entonces** se rechaza.
- **CA-054-05 · UX** — **Dado que** el ADM va a desactivar un elemento en uso, **cuando** confirma, **entonces** ve una advertencia de uso.

### SIGE-US-055 — Configurar los parámetros operativos de asistencia
- **CA-055-01 · Feliz** — **Dado que** el ADM abre parámetros, **cuando** modifica ventana de rebote, hora de corte u hora de verificación, **entonces** el valor se guarda y aplica desde el momento del cambio.
- **CA-055-02 · Límite** — **Dado que** la ventana de rebote admite 1–30 min, **cuando** el ADM ingresa 0 o 31, **entonces** se rechaza.
- **CA-055-03 · Feliz** — **Dado que** hay parámetros de estudiantes y de docentes, **cuando** se cambia uno, **entonces** el otro no cambia.
- **CA-055-04 · Aud** — **Dado que** se cambió un parámetro, **cuando** se consulta la bitácora, **entonces** aparece con usuario, fecha/hora, valor anterior y nuevo.
- **CA-055-05 · Neg** — **Dado que** se modificó un parámetro, **cuando** se consultan registros históricos ya determinados, **entonces** no cambian.
- **CA-055-06 · Perm** — **Dado que** el usuario no es ADM, **cuando** intenta modificar, **entonces** se rechaza.
- **CA-055-07 · Feliz** — **Dado que** no se ha configurado, **cuando** el sistema inicia, **entonces** usa 5 min de rebote y 10:00 de verificación por defecto.

### SIGE-US-056 — Ver el panel de indicadores operativos
- **CA-056-01 · Feliz** — **Dado que** el ADM abre el panel, **cuando** carga, **entonces** ve asistencia del día, reportes abiertos y credenciales pendientes.
- **CA-056-02 · Feliz** — **Dado que** se registra una asistencia nueva, **cuando** se actualiza el panel, **entonces** la cifra refleja el dato vigente.
- **CA-056-03 · Perm** — **Dado que** el rol no tiene acceso `[⚠ A-21]`, **cuando** intenta abrirlo, **entonces** se deniega.
- **CA-056-04 · UX** — **Dado que** no hay datos o falla la carga, **cuando** se abre, **entonces** se muestra estado vacío o de error con reintento.

---

# EP-10 — Continuidad y operación local

### SIGE-US-057 — Respaldar y restaurar la base de datos
- **CA-057-01 · Feliz** — **Dado que** llega el periodo configurado (mínimo diario), **cuando** se cumple, **entonces** el respaldo se ejecuta automáticamente sin intervención y se registra su resultado (éxito o fallo).
- **CA-057-02 · Alt** — **Dado que** un respaldo falla, **cuando** se registra, **entonces** el ADM ve una alerta.
- **CA-057-03 · Feliz** — **Dado que** existe un respaldo válido, **cuando** se sigue el procedimiento documentado de restauración, **entonces** la base de datos se recupera íntegra (100 % de los respaldos de prueba recuperados).
- **CA-057-04 · Feliz** — **Dado que** falla el servidor local, **cuando** se sigue el procedimiento de recuperación, **entonces** se restaura desde el último respaldo válido y el sistema vuelve a operar.
- **CA-057-05 · Feliz** — **Dado que** se prepara el cierre de un hito, **cuando** se prueba la restauración completa, **entonces** se verifica la integridad de los datos recuperados.
- **CA-057-06 · Feliz** — **Dado que** se documenta la instalación, **cuando** se reproduce en un equipo de reemplazo, **entonces** el entorno queda operativo siguiendo solo esa documentación.

### SIGE-US-058 — Operar las funciones internas sin Internet
- **CA-058-01 · Feliz** — **Dado que** no hay Internet pero sí red local y servidor, **cuando** el personal registra asistencia, reportes o consultas, **entonces** todo funciona con normalidad.
- **CA-058-02 · Alt** — **Dado que** no hay Internet, **cuando** se intenta enviar correo o usar acceso remoto, **entonces** solo esas funciones no están disponibles, con mensaje que lo explica.
- **CA-058-03 · Alt** — **Dado que** el dispositivo pierde la red local, **cuando** ocurre, **entonces** la app muestra el mensaje de "sin conexión al servidor" y activa el modo offline (US-032), distinto del de "sin Internet".
- **CA-058-04 · Feliz** — **Dado que** se ejecutan los escenarios definidos de pérdida de Internet con servidor disponible, **cuando** se prueban, **entonces** el 100 % se supera (KPI-31/43).
- **CA-058-05 · Feliz** — **Dado que** web y móvil usan el servidor local, **cuando** se conectan por la red institucional, **entonces** el 100 % de las conexiones funciona sin Internet.

---

## 6. Resumen de cobertura

| Épica | Historias | Criterios |
|---|---|---|
| EP-01 Autenticación y acceso | 7 | 42 |
| EP-02 Estudiantes | 9 | 51 |
| EP-03 Importación | 5 | 28 |
| EP-04 QR y credenciales | 5 | 34 |
| EP-05 Asistencia estudiantil | 11 | 76 |
| EP-06 Asistencia docente | 7 | 41 |
| EP-07 Reportes | 7 | 45 |
| EP-08 Comunicación | 2 | 12 |
| EP-09 Administración | 3 | 16 |
| EP-10 Continuidad | 2 | 11 |
| **Total** | **58** | **≈ 356** + 16 transversales |

> Antes de implementar, resolver o aceptar por escrito los criterios marcados `[⚠ A-##]` (vacíos e inconsistencias del Anexo A del documento de historias); son los puntos donde los documentos fuente se contradicen o no definen la regla.
