# SIGE — Plan de Pruebas · Anexo A: Matriz de trazabilidad criterio → prueba

**Versión:** 1.0 | **Estado:** Para revisión del equipo
**Pertenece a:** `SIGE_Plan_de_Pruebas_v1.md` (§5)
**Criterios cubiertos:** 457 (442 del archivo de criterios v2 + 15 agregados por los parches PAQ1 y PAQ3)

## Cómo leer la matriz

| Columna | Significado |
|---|---|
| **CA** | Criterio de aceptación. Los marcados **(nuevo)** vienen de los parches PAQ1 o PAQ3 |
| **Tipo** | Etiqueta del criterio: Feliz, Alt, Neg, Límite, Perm, Aud, UX |
| **Resultado esperado** | Resumen de la cláusula *entonces* (el texto completo está en el documento de criterios) |
| **Nivel** | Nivel principal de prueba: **U** unitaria, **I** integración (API con PostgreSQL real), **E** E2E, **R** rendimiento, **O** operación (respaldos y recuperación) |
| **Compl.** | Niveles complementarios: **U**, **I**, **E**, **S** seguridad, **M** manual con dispositivos reales, **O** operación |
| **Casos** | Identificadores de los casos de prueba de nivel U, I, S, O, R y M (`TC-<historia>-<n>-<nivel>`). El nivel E no genera caso propio: se cubre en el recorrido E2E de la columna siguiente |
| **Recorrido E2E** | Recorrido de extremo a extremo (§4.3 del plan) que ejecuta el criterio, cuando aplica |
| **Pri.** | Prioridad: **P0** riesgo alto, **P1** funcional, **P2** presentación |

> La asignación de nivel y prioridad se hizo **por reglas** (§5.1 del plan) y se revisó por muestreo. Se refina historia por historia al cumplir el *Definition of Ready* (DoR); cuando cambie, cambia aquí.


## EP-01 — Autenticación y acceso


### SIGE-US-001 — Iniciar y mantener sesión

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-001-01 | Feliz | SIGE emite un token de acceso de vida corta y un token de renovación, y muestra la pantalla… | I | E+S | TC-001-01-I, TC-001-01-S | E2E-01 | P0 |
| CA-001-02 | Neg | SIGE muestra un mensaje genérico que no revela si falló el usuario o la contraseña y no emit… | I | S | TC-001-02-I, TC-001-02-S | — | P0 |
| CA-001-03 | Neg | se rechaza el acceso con un mensaje de cuenta no disponible. | I | S | TC-001-03-I, TC-001-03-S | — | P0 |
| CA-001-04 | Alt | el sistema renueva la sesión de forma transparente y completa la operación. | I | S | TC-001-04-I, TC-001-04-S | — | P0 |
| CA-001-05 | Neg | se responde 401 y no se ejecuta ninguna operación. | I | S | TC-001-05-I, TC-001-05-S | — | P0 |
| CA-001-06 | Alt | se rechaza por estar invalidado. | I | S | TC-001-06-I, TC-001-06-S | — | P0 |
| CA-001-07 | UX | se muestra un error recuperable con opción de reintentar. | E | — | — | E2E-01 | P0 |
| CA-001-08 **(nuevo)** | Alt | la sesión se recupera con el token de renovación y se muestra la pantalla de su rol, con el… | I | E+S | TC-001-08-I, TC-001-08-S | E2E-01 | P0 |
| CA-001-09 **(nuevo)** | UX | SIGE le advierte que quedan eventos pendientes y, al confirmar, los conserva en el dispositi… | E | — | — | E2E-01 | P0 |
| CA-001-10 **(nuevo)** | Alt | las renovaciones se atienden una tras otra y la sesión no se cierra por detección de reutili… | I | S | TC-001-10-I, TC-001-10-S | — | P0 |

### SIGE-US-002 — Bloqueo temporal por intentos fallidos y desbloqueo manual

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-002-01 | Límite | la cuenta sigue disponible y cada intento responde 401; y cuando falla el 5.º, entonces la c… | U | I+S | TC-002-01-U, TC-002-01-I, TC-002-01-S | — | P0 |
| CA-002-02 | UX | SIGE informa el tiempo de espera restante. | E | — | — | E2E-01 | P0 |
| CA-002-03 | Neg | el acceso se rechaza hasta que venza el bloqueo. | I | S | TC-002-03-I, TC-002-03-S | — | P0 |
| CA-002-04 | Feliz | el contador de fallos vuelve a cero. | I | S | TC-002-04-I, TC-002-04-S | — | P0 |
| CA-002-05 | Perm | el usuario puede ingresar de inmediato y queda registro del desbloqueo. | I | S | TC-002-05-I, TC-002-05-S | — | P0 |
| CA-002-06 | Perm | se rechaza la operación. | I | S | TC-002-06-I, TC-002-06-S | — | P0 |
| CA-002-07 | Alt | el nuevo valor rige para bloqueos posteriores y el cambio queda auditado. | I | S | TC-002-07-I, TC-002-07-S | — | P0 |
| CA-002-08 | Alt | la cuenta vuelve a aceptar intentos. | I | S | TC-002-08-I, TC-002-08-S | — | P0 |

### SIGE-US-003 — Dar de alta una cuenta de usuario con rol

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-003-01 | Feliz | se crea la cuenta con exactamente un rol y queda auditada. | I | S | TC-003-01-I, TC-003-01-S | — | P1 |
| CA-003-02 | Neg | se rechaza con indicación del campo duplicado. | I | U | TC-003-02-I, TC-003-02-U | — | P1 |
| CA-003-03 | Neg | se rechaza indicando qué requisito falta. | I | S | TC-003-03-I, TC-003-03-S | — | P1 |
| CA-003-04 | Perm | recibe permiso denegado. | I | E | TC-003-04-I | E2E-03 | P0 |
| CA-003-05 | Neg | se rechaza: solo un rol activo (RN-AUT-01). | I | — | TC-003-05-I | — | P1 |
| CA-003-06 | Neg | se rechaza indicando el campo faltante. | I | U | TC-003-06-I, TC-003-06-U | — | P1 |

### SIGE-US-004 — Desactivar cuentas y reasignar rol

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-004-01 | Feliz | la cuenta queda DESACTIVADA, sus tokens de renovación se invalidan y no se elimina ningún re… | I | E | TC-004-01-I | E2E-03 | P0 |
| CA-004-02 | Aud | el nuevo rol se aplica y la bitácora guarda rol anterior, rol nuevo, usuario y fecha/hora. | I | — | TC-004-02-I | — | P0 |
| CA-004-03 | Neg | se rechaza. | I | — | TC-004-03-I | — | P0 |
| CA-004-04 | Neg | se rechaza para no dejar el sistema sin administrador. | I | — | TC-004-04-I | — | P0 |
| CA-004-05 | Perm | se deniega (también por API). | I | — | TC-004-05-I | — | P0 |
| CA-004-06 | Feliz | siguen mostrando su autoría. | I | — | TC-004-06-I | — | P0 |
| CA-004-07 **(nuevo)** | Neg | se responde 401 SESSION_REVOKED, no se ejecuta ninguna operación y el cliente vuelve al inic… | I | S | TC-004-07-I, TC-004-07-S | — | P0 |

### SIGE-US-005 — Recuperar contraseña mediante enlace de un solo uso

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-005-01 | Feliz | recibe un enlace de un solo uso con expiración configurable. | I | — | TC-005-01-I | — | P0 |
| CA-005-02 | Neg | la pantalla muestra el mismo mensaje que en el caso exitoso y no se envía correo. | I | U | TC-005-02-I, TC-005-02-U | — | P0 |
| CA-005-03 | Límite | se rechaza y se ofrece solicitar uno nuevo. | U | I | TC-005-03-U, TC-005-03-I | — | P0 |
| CA-005-04 | Neg | se rechaza. | I | — | TC-005-04-I | — | P0 |
| CA-005-05 | Feliz | se actualiza y las sesiones anteriores quedan invalidadas. | I | S | TC-005-05-I, TC-005-05-S | — | P0 |
| CA-005-06 | Alt | SIGE informa que el servicio de correo no está disponible sin afectar el resto de funciones. | I | — | TC-005-06-I | — | P0 |
| CA-005-07 | Feliz | recibe el nuevo enlace y el anterior deja de funcionar aunque no haya expirado. | I | — | TC-005-07-I | — | P0 |
| CA-005-08 | Neg | se rechaza igual que un enlace expirado. | I | U | TC-005-08-I, TC-005-08-U | — | P0 |

### SIGE-US-006 — Restringir funciones y datos según el rol

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-006-01 | Perm | el 100 % de los intentos se rechaza en la API. | I | — | TC-006-01-I | — | P0 |
| CA-006-02 | Perm | se rechaza aunque no exista el botón en la interfaz. | I | E | TC-006-02-I | E2E-02 | P0 |
| CA-006-03 | Perm | ve permiso denegado sin datos. | I | E | TC-006-03-I | E2E-02 | P0 |
| CA-006-04 | UX | esa función no aparece en su menú. | E | — | — | E2E-02 | P0 |
| CA-006-05 | Neg | no obtiene esos datos. | I | — | TC-006-05-I | — | P0 |
| CA-006-06 | Perm | tampoco accede al dato del tutor. | I | — | TC-006-06-I | — | P0 |

### SIGE-US-007 — Consultar la bitácora de auditoría

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-007-01 | Feliz | ve los registros paginados que cumplen. | I | E | TC-007-01-I | E2E-03 | P1 |
| CA-007-02 | Aud | aparece con usuario, fecha/hora, valor anterior y valor nuevo. | I | — | TC-007-02-I | — | P1 |
| CA-007-03 | Neg | no existe la opción y la API la rechaza. | I | — | TC-007-03-I | — | P1 |
| CA-007-04 | Perm | se deniega. | I | — | TC-007-04-I | — | P0 |
| CA-007-05 | Aud | el evento aparece con su resultado. | I | — | TC-007-05-I | — | P1 |
| CA-007-06 | Aud | ambos eventos se distinguen por origen (AUTOMÁTICO/MANUAL). | I | — | TC-007-06-I | — | P1 |
| CA-007-07 | UX | se muestra un estado vacío informativo. | E | — | — | E2E-03 | P2 |

## EP-02 — Estudiantes


### SIGE-US-008 — Registrar un estudiante desde la interfaz web

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-008-01 | Feliz | se crea una ficha única en estatus ACTIVO, asignada a su grupo y ciclo. | I | — | TC-008-01-I | — | P1 |
| CA-008-02 | Neg | se rechaza indicando la matrícula duplicada y no se crea ni modifica ninguna ficha. | I | U | TC-008-02-I, TC-008-02-U | — | P1 |
| CA-008-03 | Neg | no se guarda el registro y se pide al menos un tutor. | I | — | TC-008-03-I | — | P1 |
| CA-008-04 | Neg | se señala el campo y no se guarda. | I | U | TC-008-04-I, TC-008-04-U | — | P1 |
| CA-008-05 | Neg | solo una se persiste y la otra se rechaza por unicidad. | I | U | TC-008-05-I, TC-008-05-U | — | P1 |
| CA-008-06 | Perm | se deniega. | I | E | TC-008-06-I | E2E-04 | P0 |
| CA-008-07 | Aud | registra quién y cuándo la realizó. | I | — | TC-008-07-I | — | P1 |
| CA-008-08 | Feliz | los ve; cuando consulta el adeudo de pago o materias pendientes, entonces no los ve. | I | — | TC-008-08-I | — | P1 |
| CA-008-09 | Perm | no ve ningún campo de salud ni de situación administrativa. | I | E | TC-008-09-I | E2E-04 | P0 |
| CA-008-10 | Feliz | el registro se guarda con esos campos tal como se capturaron y el apellido materno queda vacío. | I | E | TC-008-10-I | E2E-04 | P1 |
| CA-008-11 | Neg | no se guarda nada y se señala el campo faltante. | I | U | TC-008-11-I, TC-008-11-U | — | P1 |
| CA-008-12 | Neg | se rechaza señalando el campo. | I | U | TC-008-12-I, TC-008-12-U | — | P1 |
| CA-008-13 | Neg | se rechaza indicando que el apellido materno se deja vacío si no existe. | I | U | TC-008-13-I, TC-008-13-U | — | P1 |
| CA-008-14 | Alt | se almacena sin espacios sobrantes («Juan Carlos») y sin alterar mayúsculas ni acentos. | I | — | TC-008-14-I | — | P1 |
| CA-008-15 | Límite | se rechazan 1 y 61 y se aceptan 2 y 60. | U | I | TC-008-15-U, TC-008-15-I | — | P1 |

### SIGE-US-009 — Guardar y completar un registro incompleto

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-009-01 | Alt | el registro se guarda como INCOMPLETO, permanece ACTIVO y la ficha lista los campos faltantes. | I | E | TC-009-01-I | E2E-04 | P1 |
| CA-009-02 | Neg | no se guarda nada. | I | — | TC-009-02-I | — | P1 |
| CA-009-03 | UX | muestra la insignia "Incompleto". | E | — | — | E2E-04 | P2 |
| CA-009-04 | Feliz | la insignia desaparece. | I | E | TC-009-04-I | E2E-04 | P1 |
| CA-009-05 | Neg | se excluye y se lista como pendiente (RN-CRE-01). | I | — | TC-009-05-I | — | P1 |
| CA-009-06 | Neg | se rechaza: el tutor nunca es opcional. | I | — | TC-009-06-I | — | P1 |
| CA-009-07 | Neg | no se guarda nada. | I | U | TC-009-07-I, TC-009-07-U | — | P1 |

### SIGE-US-010 — Asociar y administrar tutores de un estudiante

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-010-01 | Feliz | queda asociado al estudiante. | I | — | TC-010-01-I | — | P1 |
| CA-010-02 | Feliz | solo uno queda como principal. | I | — | TC-010-02-I | — | P1 |
| CA-010-03 | Neg | se rechaza. | I | — | TC-010-03-I | — | P1 |
| CA-010-04 | Neg | se señala el error (falta al menos un dato de contacto válido). | I | U | TC-010-04-I, TC-010-04-U | — | P1 |
| CA-010-05 | Perm | se deniega; los roles sin acceso al expediente tampoco los consultan. | I | — | TC-010-05-I | — | P0 |
| CA-010-06 | Neg | se rechaza (RN-COM-01). | I | — | TC-010-06-I | — | P1 |
| CA-010-07 | Feliz | queda marcado como contacto válido. | I | — | TC-010-07-I | — | P1 |
| CA-010-08 | Neg | se rechaza por falta de correo (RN-COM-01), aunque el tutor sea "contacto válido". | I | U | TC-010-08-I, TC-010-08-U | — | P1 |
| CA-010-09 | Neg | se rechaza indicando el campo faltante. | I | U | TC-010-09-I, TC-010-09-U | — | P1 |
| CA-010-10 | Feliz | el tutor se guarda con el apellido materno vacío. | I | — | TC-010-10-I | — | P1 |
| CA-010-11 | Feliz | SIGE lo detecta como coincidencia fuerte y ofrece reutilizarlo. | I | — | TC-010-11-I | — | P1 |
| CA-010-12 | Neg | SIGE NO los reconoce como el mismo tutor y crea un GUARDIAN independiente. | I | U | TC-010-12-I, TC-010-12-U | — | P1 |
| CA-010-13 | Feliz | ve el aviso "Este cambio afectará a 3 estudiantes" con sus nombres antes de guardar. | I | E | TC-010-13-I | E2E-04 | P1 |
| CA-010-14 | Feliz | los 3 vínculos reflejan el nuevo teléfono de inmediato. | I | — | TC-010-14-I | — | P1 |
| CA-010-15 | Feliz | la invalidación manual se retira y el indicador de contacto válido se recalcula. | I | E | TC-010-15-I | E2E-04 | P1 |
| CA-010-16 | Feliz | se crea un GUARDIAN independiente solo para ese estudiante y los demás vínculos del tutor or… | I | — | TC-010-16-I | — | P1 |

### SIGE-US-011 — Consultar y filtrar expedientes

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-011-01 | Feliz | obtiene resultados paginados que cumplen. | I | E | TC-011-01-I | E2E-05 | P1 |
| CA-011-02 | Feliz | se combinan. | I | E | TC-011-02-I | E2E-05 | P1 |
| CA-011-03 | Alt | el expediente aparece con su historial completo. | I | — | TC-011-03-I | — | P1 |
| CA-011-04 | Perm | se deniega. | I | — | TC-011-04-I | — | P0 |
| CA-011-05 | UX | ve una advertencia sin que se bloquee la consulta. | E | — | — | E2E-05 | P2 |
| CA-011-06 | UX | se muestra un estado vacío; en móvil los resultados se presentan como tarjetas. | E | — | — | E2E-05 | P2 |
| CA-011-07 | Feliz | el estudiante aparece en los resultados (sin distinguir acentos, mayúsculas ni el campo de n… | I | E | TC-011-07-I | E2E-05 | P1 |
| CA-011-08 | Feliz | el orden es apellido paterno, apellido materno y nombre(s). | I | E | TC-011-08-I | E2E-05 | P1 |

### SIGE-US-012 — Modificar los datos de un estudiante

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-012-01 | Feliz | se actualiza la ficha. | I | — | TC-012-01-I | — | P1 |
| CA-012-02 | Neg | el campo está bloqueado y la API rechaza el cambio. | I | U | TC-012-02-I, TC-012-02-U | — | P1 |
| CA-012-03 | Alt | se aplica y queda en bitácora con valor anterior y nuevo. | I | — | TC-012-03-I | — | P1 |
| CA-012-04 | Neg | se rechaza. | I | U | TC-012-04-I, TC-012-04-U | — | P1 |
| CA-012-05 | Perm | se deniega. | I | — | TC-012-05-I | — | P0 |
| CA-012-06 | Neg | la API rechaza el cambio y la ficha no se modifica. | I | U | TC-012-06-I, TC-012-06-U | — | P1 |

### SIGE-US-013 — Cambiar grupo o ciclo conservando el historial

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-013-01 | Feliz | la ficha refleja el grupo nuevo. | I | — | TC-013-01-I | — | P1 |
| CA-013-02 | Feliz | siguen asociadas al grupo anterior. | I | — | TC-013-02-I | — | P1 |
| CA-013-03 | UX | el historial de grupos se muestra con fechas. | E | — | — | E2E-05 | P2 |
| CA-013-04 | Neg | se rechaza. | I | — | TC-013-04-I | — | P1 |
| CA-013-05 | Perm | se deniega. | I | — | TC-013-05-I | — | P0 |

### SIGE-US-014 — Dar de baja o registrar egreso de un estudiante

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-014-01 | Feliz | cambia el estatus, se conserva el expediente y el cambio queda auditado. | I | — | TC-014-01-I | — | P1 |
| CA-014-02 | Neg | se rechaza por transición no válida. | I | — | TC-014-02-I | — | P1 |
| CA-014-03 | Neg | se rechaza (RN-EST-05). | I | — | TC-014-03-I | — | P1 |
| CA-014-04 | Feliz | no se le genera FALTÓ. | I | U | TC-014-04-I, TC-014-04-U | — | P0 |
| CA-014-05 | Feliz | ve todos sus registros anteriores; ninguno se eliminó. | I | — | TC-014-05-I | — | P1 |
| CA-014-06 | UX | se explica que dejará de aparecer en asistencia y reportes nuevos. | E | — | — | E2E-05 | P2 |

### SIGE-US-015 — Reingresar a un estudiante dado de baja

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-015-01 | Feliz | pasa a ACTIVO y se registra un evento de reingreso distinto del alta original. | I | — | TC-015-01-I | — | P1 |
| CA-015-02 | Perm | se rechaza. | I | — | TC-015-02-I | — | P0 |
| CA-015-03 | Neg | se rechaza hasta que lo tenga (RN-EST-03). | I | — | TC-015-03-I | — | P1 |
| CA-015-04 | Aud | aparece un registro diferenciado de auditoría. | I | — | TC-015-04-I | — | P1 |
| CA-015-05 | Neg | se rechaza (RN-EST-09). | I | — | TC-015-05-I | — | P1 |
| CA-015-06 | Feliz | conserva ese QR vigente. | I | — | TC-015-06-I | — | P1 |

### SIGE-US-016 — Registrar y consultar el consentimiento del tutor

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-016-01 | Feliz | se guarda estatus y fecha de registro. | I | — | TC-016-01-I | — | P0 |
| CA-016-02 | Feliz | se acepta sin requerir adjuntos. | I | — | TC-016-02-I | — | P0 |
| CA-016-03 | UX | ve la advertencia. | E | — | — | E2E-05 | P0 |
| CA-016-04 | Alt | se conserva la fecha y el historial, el expediente muestra advertencia y no se envían comuni… | I | E | TC-016-04-I | E2E-05 | P0 |
| CA-016-05 | Neg | se rechaza. | I | — | TC-016-05-I | — | P0 |
| CA-016-06 | Perm | se deniega. | I | — | TC-016-06-I | — | P0 |
| CA-016-07 | Feliz | su consentimiento queda en PENDIENTE; y dado que se revisa el total de tutores de prueba, en… | I | — | TC-016-07-I | — | P0 |

## EP-03 — Importación


### SIGE-US-017 — Descargar la plantilla de importación

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-017-01 | Feliz | obtiene un CSV/XLSX con las columnas exactas del diccionario de datos vigente. | I | E | TC-017-01-I | E2E-06 | P1 |
| CA-017-02 | Feliz | contiene ejemplos de formato válido. | I | E | TC-017-02-I | E2E-06 | P1 |
| CA-017-03 | UX | la opción de plantilla está visible antes del selector. | E | — | — | E2E-06 | P2 |
| CA-017-04 | Aud | refleja la versión vigente. | I | — | TC-017-04-I | — | P1 |
| CA-017-05 | Perm | se deniega. | I | — | TC-017-05-I | — | P0 |
| CA-017-06 | Feliz | trae columnas separadas de nombre(s), apellido paterno y apellido materno para el estudiante… | I | E | TC-017-06-I | E2E-06 | P1 |

### SIGE-US-018 — Cargar un archivo y validar su estructura

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-018-01 | Feliz | SIGE continúa al procesamiento de filas. | I | E | TC-018-01-I | E2E-06 | P1 |
| CA-018-02 | Neg | se rechaza el archivo completo antes de procesar filas, indicando qué columnas fallan. | I | U | TC-018-02-I, TC-018-02-U | — | P1 |
| CA-018-03 | Neg | se rechaza el archivo completo. | I | U | TC-018-03-I, TC-018-03-U | — | P1 |
| CA-018-04 | Neg | se rechaza. | I | U | TC-018-04-I, TC-018-04-U | — | P1 |
| CA-018-05 | Neg | no se persiste ningún registro. | I | — | TC-018-05-I | — | P1 |
| CA-018-06 | Perm | se deniega (RN-IMP-05). | I | — | TC-018-06-I | — | P0 |
| CA-018-07 | Feliz | todas las filas válidas quedan asociadas a ese grupo. | I | E | TC-018-07-I | E2E-06 | P1 |
| CA-018-08 | Neg | SIGE no tiene forma de detectarlo (queda como responsabilidad operativa de quien importa div… | I | — | TC-018-08-I | — | P1 |
| CA-018-09 | Neg | se rechaza el archivo completo indicando qué columnas faltan y no se persiste ningún registro. | I | U | TC-018-09-I, TC-018-09-U | — | P1 |

### SIGE-US-019 — Procesar cada fila de forma independiente

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-019-01 | Feliz | las válidas quedan listas para insertar y las inválidas se descartan sin afectar a las demás. | I | E | TC-019-01-I | E2E-06 | P1 |
| CA-019-02 | Neg | se rechaza como duplicada y jamás sobrescribe al estudiante existente. | I | U | TC-019-02-I, TC-019-02-U | — | P1 |
| CA-019-03 | Neg | solo la primera válida avanza y la otra se reporta como duplicada. | I | U | TC-019-03-I, TC-019-03-U | — | P1 |
| CA-019-04 | Neg | se descarta y ninguno de sus datos se guarda. | I | — | TC-019-04-I | — | P1 |
| CA-019-05 | Neg | el reporte registra fila, campo, tipo de error y descripción. | I | U | TC-019-05-I, TC-019-05-U | — | P1 |
| CA-019-06 | Alt | se muestra el reporte de filas descartadas al terminar. | I | E | TC-019-06-I | E2E-06 | P1 |
| CA-019-07 | Alt | se inserta como INCOMPLETO. | I | — | TC-019-07-I | — | P1 |
| CA-019-08 | Neg | se descarta y el reporte registra fila, columna y motivo. | I | U | TC-019-08-I, TC-019-08-U | — | P1 |
| CA-019-09 | Alt | es válida y se inserta. | I | — | TC-019-09-I | — | P1 |

### SIGE-US-020 — Revisar la vista previa y confirmar la importación

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-020-01 | Feliz | indica cuántos registros se insertarán y cuántos se rechazarán. | I | E | TC-020-01-I | E2E-06 | P1 |
| CA-020-02 | Neg | no existe ningún estudiante nuevo persistido por esa importación. | I | — | TC-020-02-I | — | P1 |
| CA-020-03 | Feliz | se generan las fichas de los registros válidos en estatus ACTIVO, asignadas a su grupo y ciclo. | I | E | TC-020-03-I | E2E-06 | P1 |
| CA-020-04 | Alt | la importación termina y no se persiste ningún dato. | I | — | TC-020-04-I | — | P1 |
| CA-020-05 | Neg | no se ofrece confirmar (o se advierte que no hay nada que insertar). | I | — | TC-020-05-I | — | P1 |
| CA-020-06 | Neg | solo esa fila se rechaza, se reporta como duplicada y el resto se importa. | I | U | TC-020-06-I, TC-020-06-U | — | P1 |

### SIGE-US-021 — Descargar el reporte de resultados de la importación

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-021-01 | Feliz | muestra total procesadas, insertadas y con error. | I | E | TC-021-01-I | E2E-06 | P1 |
| CA-021-02 | Feliz | cada fila con error incluye el número de fila, la columna y el motivo. | I | E | TC-021-02-I | E2E-06 | P1 |
| CA-021-03 | Límite | el total de errores es 0 y el detalle está vacío. | I | — | TC-021-03-I | — | P1 |
| CA-021-04 | Feliz | las cifras coinciden. | I | E | TC-021-04-I | E2E-06 | P1 |
| CA-021-05 | Perm | se deniega. | I | E | TC-021-05-I | E2E-06 | P0 |

## EP-04 — QR y credenciales


### SIGE-US-022 — Generar el QR único de un estudiante

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-022-01 | Feliz | se crea un token único, un QR que codifica solo ese token, se asocia al estudiante y queda V… | I | E | TC-022-01-I | E2E-07 | P0 |
| CA-022-02 | Neg | no contiene nombre, matrícula visible ni CURP, solo el token opaco. | I | U | TC-022-02-I, TC-022-02-U | — | P0 |
| CA-022-03 | Neg | se rechaza (o se trata como reemplazo, US-024). | I | — | TC-022-03-I | — | P0 |
| CA-022-04 | Alt | se incrementa el contador de colisiones y se genera otro candidato. | I | — | TC-022-04-I | — | P0 |
| CA-022-05 | Límite | se alerta al ADM, se aborta el proceso y no se guarda ningún QR. | U | I | TC-022-05-U, TC-022-05-I | — | P0 |
| CA-022-06 | Neg | se descarta y se genera otro. | I | U | TC-022-06-I, TC-022-06-U | — | P0 |
| CA-022-07 | Neg | se rechaza. | I | — | TC-022-07-I | — | P0 |
| CA-022-08 | Aud | registra estudiante, token, fecha/hora, usuario, estado y origen (alta inicial). | I | — | TC-022-08-I | — | P0 |
| CA-022-09 | Feliz | 100 % tiene QR único y 0 identificadores duplicados. | I | E | TC-022-09-I | E2E-07 | P0 |

### SIGE-US-023 — Validar la integridad del lote de QR

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-023-01 | Feliz | el resultado es 0 duplicados, 0 huérfanos y el lote pasa a HABILITADO. | I | — | TC-023-01-I | — | P1 |
| CA-023-02 | Neg | el lote queda BLOQUEADO y se lista el duplicado. | I | U | TC-023-02-I, TC-023-02-U | — | P1 |
| CA-023-03 | Neg | se reportan como huérfanos y el lote no se habilita. | I | — | TC-023-03-I | — | P1 |
| CA-023-04 | Neg | se rechaza. | I | — | TC-023-04-I | — | P1 |
| CA-023-05 | Perm | se deniega. | I | — | TC-023-05-I | — | P0 |
| CA-023-06 | Feliz | puede descargarlo con fecha y resultado. | I | E | TC-023-06-I | E2E-07 | P1 |

### SIGE-US-024 — Revocar y reemplazar el QR de un estudiante

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-024-01 | Feliz | el QR pasa a REVOCADO con fecha, usuario y motivo, y se genera uno nuevo VIGENTE enlazado al… | I | E | TC-024-01-I | E2E-07 | P0 |
| CA-024-02 | Perm | se rechaza con "Se requiere autorización de rol Administrador" y no hay cambios. | I | — | TC-024-02-I | — | P0 |
| CA-024-03 | Neg | se rechaza y se alerta al operador aunque el estudiante siga ACTIVO. | I | — | TC-024-03-I | — | P0 |
| CA-024-04 | Neg | nunca se reutiliza ese token. | I | — | TC-024-04-I | — | P0 |
| CA-024-05 | Alt | se omite la revocación y se genera el nuevo QR. | I | — | TC-024-05-I | — | P0 |
| CA-024-06 | Aud | ambos conservan la referencia al identificador revocado y a su reemplazo. | I | — | TC-024-06-I | — | P0 |
| CA-024-07 | Neg | se rechaza. | I | — | TC-024-07-I | — | P0 |

### SIGE-US-025 — Exportar el QR para la credencial física

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-025-01 | Feliz | obtiene su QR en alta resolución/PDF. | I | E | TC-025-01-I | E2E-07 | P1 |
| CA-025-02 | Neg | se excluye y se lista como pendiente con motivo; y dado que no tiene fotografía, cuando se e… | I | — | TC-025-02-I | — | P1 |
| CA-025-03 | Feliz | 100 % es legible y corresponde al estudiante correcto. | I | E+M | TC-025-03-I, TC-025-03-M | E2E-07 | P1 |
| CA-025-04 | Neg | no aparece en el archivo. | I | — | TC-025-04-I | — | P1 |
| CA-025-05 | UX | puede distinguir el formato para credencial nueva y el de sticker. | E | — | — | E2E-07 | P2 |
| CA-025-06 | Perm | se deniega. | I | E | TC-025-06-I | E2E-07 | P0 |

### SIGE-US-026 — Reexportar QR de forma selectiva

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-026-01 | Feliz | solo se genera el QR vigente del subconjunto y no se reexporta el lote completo. | I | E | TC-026-01-I | E2E-07 | P1 |
| CA-026-02 | Feliz | el archivo contiene el nuevo QR (sticker de reposición) y no el revocado. | I | E | TC-026-02-I | E2E-07 | P1 |
| CA-026-03 | Neg | se excluye y se lista como pendiente. | I | — | TC-026-03-I | — | P1 |
| CA-026-04 | UX | ve una vista previa de a cuántos estudiantes aplica. | E | — | — | E2E-07 | P2 |

## EP-05 — Asistencia estudiantil


### SIGE-US-027 — Validar el QR al escanear

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-027-01 | Feliz | SIGE identifica al estudiante y continúa al registro. | I | E | TC-027-01-I | E2E-08 | P0 |
| CA-027-02 | Neg | se muestra "QR no reconocido" y no se genera ningún registro. | I | U | TC-027-02-I, TC-027-02-U | — | P0 |
| CA-027-03 | Neg | se rechaza automáticamente y se alerta al operador para verificar identidad manualmente. | I | — | TC-027-03-I | — | P0 |
| CA-027-04 | Neg | se rechaza el registro. | I | — | TC-027-04-I | — | P0 |
| CA-027-05 | UX | hay retroalimentación visual y sonora inmediata distinguible entre válido e inválido. | E | — | — | E2E-08 | P0 |
| CA-027-06 | Límite | la validación y confirmación tardan menos de 250 ms (CT-10). | R | I | TC-027-06-R, TC-027-06-I | — | P0 |
| CA-027-07 | Perm | se deniega. | I | — | TC-027-07-I | — | P0 |
| CA-027-08 | Feliz | el resultado es equivalente al de la app móvil. | I | E | TC-027-08-I | E2E-08 | P0 |

### SIGE-US-028 — Registrar la asistencia y determinar ASISTIÓ o LLEGÓ TARDE

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-028-01 | Límite | el estado es ASISTIÓ. | U | I | TC-028-01-U, TC-028-01-I | — | P0 |
| CA-028-02 | Límite | el estado es LLEGÓ TARDE. | U | I | TC-028-02-U, TC-028-02-I | — | P0 |
| CA-028-03 | Feliz | se guarda estudiante, fecha, hora, grupo, jornada, estado y origen ESCANEO. | I | E | TC-028-03-I | E2E-08 | P0 |
| CA-028-04 | Alt | el escaneo se guarda como evento adicional sin cambiar el estado ya determinado. | I | — | TC-028-04-I | — | P0 |
| CA-028-05 | Alt | se aplica el flujo de reclasificación (US-031). | I | — | TC-028-05-I | — | P0 |
| CA-028-06 | Feliz | se usa la del grupo y jornada del estudiante. | I | E | TC-028-06-I | E2E-08 | P0 |
| CA-028-07 | Feliz | conservan su estado (sin efecto retroactivo). | I | E | TC-028-07-I | E2E-08 | P0 |
| CA-028-08 | Feliz | se rechaza; solo puede modificarse vía justificación. | I | E | TC-028-08-I | E2E-08 | P0 |
| CA-028-09 | UX | el operador ve nombre del estudiante y estado resultante. | E | — | — | E2E-08 | P0 |
| CA-028-10 | Alt | se guarda un evento adicional y el estado no cambia (RN-AST-07). | I | — | TC-028-10-I | — | P0 |

### SIGE-US-029 — Ignorar escaneos duplicados (rebote)

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-029-01 | Límite | el segundo se ignora. | U | I | TC-029-01-U, TC-029-01-I | — | P0 |
| CA-029-02 | Límite | ya no es rebote y se procesa con las reglas normales. | U | I | TC-029-02-U, TC-029-02-I | — | P0 |
| CA-029-03 | Feliz | no se crea un segundo registro y el operador ve "registro duplicado". | I | — | TC-029-03-I | — | P0 |
| CA-029-04 | Límite | se rechaza; 1 y 30 se aceptan. | U | I | TC-029-04-U, TC-029-04-I | — | P0 |
| CA-029-05 | Feliz | ambos se procesan. | I | — | TC-029-05-I | — | P0 |
| CA-029-06 | Alt | también se descarta como rebote. | I | E | TC-029-06-I | E2E-08 | P0 |
| CA-029-07 | Límite | se procesa. | U | I | TC-029-07-U, TC-029-07-I | — | P0 |

### SIGE-US-030 — Marcar automáticamente FALTÓ a quien no registró entrada

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-030-01 | Feliz | se le asigna FALTÓ con origen AUTOMÁTICO. | I | U+E | TC-030-01-I, TC-030-01-U | E2E-09 | P0 |
| CA-030-02 | Límite | no tiene estado definitivo de ausencia. | U | I | TC-030-02-U, TC-030-02-I | — | P0 |
| CA-030-03 | Feliz | no se realiza ninguna acción sobre él. | I | U+E | TC-030-03-I, TC-030-03-U | E2E-09 | P0 |
| CA-030-04 | Neg | se omite. | I | U | TC-030-04-I, TC-030-04-U | — | P0 |
| CA-030-05 | Feliz | no se generan registros duplicados. | I | E | TC-030-05-I | E2E-09 | P0 |
| CA-030-06 | Feliz | el proceso se dispara a la nueva hora y la ausencia de días previos no se recalcula. | I | U+E | TC-030-06-I, TC-030-06-U | E2E-09 | P0 |
| CA-030-07 | Aud | el origen es AUTOMÁTICO, distinto de una modificación manual. | I | — | TC-030-07-I | — | P0 |

### SIGE-US-031 — Reclasificar la asistencia de quien llega después de un FALTÓ automático

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-031-01 | Feliz | se reclasifica: ASISTIÓ si su hora efectiva es ≤ la hora de corte, LLEGÓ TARDE si es posterior. | I | E | TC-031-01-I | E2E-09 | P0 |
| CA-031-02 | Aud | aparecen el estado FALTÓ previo (automático) y el nuevo con su origen y hora. | I | — | TC-031-02-I | — | P0 |
| CA-031-03 | Neg | no existe un segundo registro de entrada para la misma fecha y jornada. | I | U | TC-031-03-I, TC-031-03-U | — | P0 |
| CA-031-04 | Aud | se distingue de una justificación manual. | I | — | TC-031-04-I | — | P0 |
| CA-031-05 | Neg | se rechaza (no reclasifica). | I | — | TC-031-05-I | — | P0 |
| CA-031-06 | Neg | se ignora sin cambios. | I | U | TC-031-06-I, TC-031-06-U | — | P0 |
| CA-031-07 | Neg | no se reclasifica. | I | U | TC-031-07-I, TC-031-07-U | — | P0 |

### SIGE-US-032 — Capturar asistencia sin conexión al servidor (app móvil)

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-032-01 | Feliz | el evento se almacena localmente con fecha, hora, tipo y QR leído, marcado PENDIENTE DE VALI… | E | U | TC-032-01-U | E2E-10 | P0 |
| CA-032-02 | UX | un indicador persistente muestra "sin conexión" y el número de pendientes. | E | U | TC-032-02-U | E2E-10 | P0 |
| CA-032-03 | Límite | se almacena. | E | U | TC-032-03-U | E2E-10 | P0 |
| CA-032-04 | Límite | se rechaza y se alerta al operador (RN-MOV-03). | E | U | TC-032-04-U | E2E-10 | P0 |
| CA-032-05 | Neg | no aparece como registro definitivo. | E | U | TC-032-05-U | E2E-10 | P0 |
| CA-032-06 | Feliz | se le informa que quedó pendiente, no confirmado. | E | U | TC-032-06-U | E2E-10 | P0 |
| CA-032-07 | UX | no se almacena ningún dato del estudiante: solo fecha, hora de captura, tipo y token, más lo… | E | U | TC-032-07-U | E2E-10 | P0 |
| CA-032-08 **(nuevo)** | Alt | llega a la pantalla de escaneo y puede capturar eventos. | E | U | TC-032-08-U | E2E-10 | P0 |
| CA-032-09 **(nuevo)** | Alt | los eventos pendientes siguen en el buffer. | E | U | TC-032-09-U | E2E-10 | P0 |
| CA-032-10 **(nuevo)** | Neg | no se almacena el evento y se le indica conectarse una vez al servidor para calibrar el relo… | E | U | TC-032-10-U | E2E-10 | P0 |

### SIGE-US-033 — Sincronizar y validar los eventos capturados sin conexión

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-033-01 | Feliz | se sincronizan automáticamente sin intervención del operador. | I | — | TC-033-01-I | — | P0 |
| CA-033-02 | Feliz | se incorpora con el estado calculado a partir de su hora de captura corregida por el desfase… | I | — | TC-033-02-I | — | P0 |
| CA-033-03 | Neg | se descarta y se notifica al operador con motivo. | I | E | TC-033-03-I | E2E-10 | P0 |
| CA-033-04 | Neg | se descarta y se notifica. | I | E | TC-033-04-I | E2E-10 | P0 |
| CA-033-05 | Neg | se descarta y se notifica como duplicado. | I | E | TC-033-05-I | E2E-10 | P0 |
| CA-033-06 | Alt | se aplica US-031. | I | — | TC-033-06-I | — | P0 |
| CA-033-07 | Alt | los eventos no enviados permanecen en el buffer y se reintentan. | I | — | TC-033-07-I | — | P0 |
| CA-033-08 | UX | muestra cuántos se aceptaron y cuántos se descartaron. | I | E | TC-033-08-I | E2E-10 | P0 |
| CA-033-09 | Neg | se rechaza y se notifica al operador. | I | E | TC-033-09-I | E2E-10 | P0 |
| CA-033-10 **(nuevo)** | Alt | se devuelven los mismos resultados y no se duplica ningún registro. | I | — | TC-033-10-I | — | P0 |
| CA-033-11 **(nuevo)** | Alt | se envían ordenados por hora de captura, para que el rebote y el primer escaneo se evalúen e… | I | — | TC-033-11-I | — | P0 |
| CA-033-12 **(nuevo)** | UX | se le advierte que la hora del dispositivo difiere del servidor, y el evento se marca para r… | I | — | TC-033-12-I | E2E-20 | P0 |

### SIGE-US-034 — Justificar o modificar la asistencia de un estudiante

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-034-01 | Feliz | el estado pasa a FALTA JUSTIFICADA con origen MANUAL. | I | E | TC-034-01-I | E2E-11 | P0 |
| CA-034-02 | Aud | conserva estado anterior, nuevo, usuario, fecha/hora, motivo y origen MANUAL. | I | — | TC-034-02-I | — | P0 |
| CA-034-03 | Neg | se rechaza. | I | — | TC-034-03-I | — | P0 |
| CA-034-04 | Perm | se rechaza. | I | — | TC-034-04-I | — | P0 |
| CA-034-05 | Neg | se rechaza. | I | — | TC-034-05-I | — | P0 |
| CA-034-06 | Alt | el historial muestra ambos cambios con orígenes distintos. | I | E | TC-034-06-I | E2E-11 | P0 |
| CA-034-07 | Feliz | se aplican las mismas reglas que en web (CT-04). | I | E | TC-034-07-I | E2E-11 | P0 |

### SIGE-US-035 — Consultar la asistencia diaria de un grupo

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-035-01 | Feliz | ve la relación completa de estudiantes con su estado. | I | E | TC-035-01-I | E2E-12 | P1 |
| CA-035-02 | Feliz | el historial de esa fecha está íntegro. | I | — | TC-035-02-I | — | P1 |
| CA-035-03 | Feliz | solo aparecen los estudiantes con ese estado. | I | E | TC-035-03-I | E2E-12 | P1 |
| CA-035-04 | UX | el origen es visible para roles autorizados. | E | — | — | E2E-12 | P2 |
| CA-035-05 | UX | se muestra estado vacío. | E | — | — | E2E-12 | P2 |
| CA-035-06 | Perm | se deniega. | I | — | TC-035-06-I | — | P0 |
| CA-035-07 | Feliz | sigue apareciendo en él. | I | — | TC-035-07-I | — | P1 |

### SIGE-US-036 — Consultar el historial individual de asistencia

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-036-01 | Feliz | ve estado, hora y origen por fecha. | I | — | TC-036-01-I | — | P1 |
| CA-036-02 | Feliz | ve las modificaciones con su trazabilidad. | I | — | TC-036-02-I | — | P1 |
| CA-036-03 | Feliz | coinciden. | I | E | TC-036-03-I | E2E-12 | P1 |
| CA-036-04 | Feliz | ve su historial completo. | I | — | TC-036-04-I | — | P1 |
| CA-036-05 | Perm | se deniega. | I | — | TC-036-05-I | — | P0 |
| CA-036-06 | UX | se muestra estado vacío. | E | — | — | E2E-12 | P2 |

### SIGE-US-037 — Obtener información consolidada de asistencia

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-037-01 | Feliz | ve conteos por estado y porcentajes. | I | — | TC-037-01-I | — | P1 |
| CA-037-02 | Feliz | obtiene un archivo con los mismos datos. | I | E | TC-037-02-I | E2E-12 | P1 |
| CA-037-03 | Feliz | el consolidado refleja el estado vigente. | I | — | TC-037-03-I | — | P1 |
| CA-037-04 | Perm | solo ve información consolidada, no datos de menores individuales innecesarios. | I | — | TC-037-04-I | — | P0 |
| CA-037-05 | Neg | no calcula calificaciones. | I | U | TC-037-05-I, TC-037-05-U | — | P1 |

## EP-06 — Asistencia docente


### SIGE-US-038 — Registrar a un docente y generar su QR

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-038-01 | Feliz | queda un único QR VIGENTE asociado a él. | I | E | TC-038-01-I | E2E-13 | P1 |
| CA-038-02 | Neg | se rechaza. | I | — | TC-038-02-I | — | P1 |
| CA-038-03 | Neg | se rechaza (identificadores independientes). | I | — | TC-038-03-I | — | P1 |
| CA-038-04 | Neg | se rechaza (RN-AST-11). | I | — | TC-038-04-I | — | P1 |
| CA-038-05 | Feliz | no requiere ni crea una cuenta de usuario de SIGE. | I | E | TC-038-05-I | E2E-13 | P1 |
| CA-038-06 | Feliz | es opaco y sin datos personales (RN-QR-02). | I | E | TC-038-06-I | E2E-13 | P1 |
| CA-038-07 | Perm | se rechaza. | I | — | TC-038-07-I | — | P0 |
| CA-038-08 | Feliz | el 100 % tiene un único QR vigente y 0 identificadores repetidos (KPI-72). | I | E | TC-038-08-I | E2E-13 | P1 |
| CA-038-09 | Neg | se rechaza y no se crea ni modifica ninguna ficha. | I | — | TC-038-09-I | — | P1 |
| CA-038-10 | Neg | no se guarda nada. | I | U | TC-038-10-I, TC-038-10-U | — | P1 |
| CA-038-11 | Feliz | el docente queda ACTIVO sin marca de incompleto, aunque no tenga fotografía, correo ni teléf… | I | E | TC-038-11-I | E2E-13 | P1 |
| CA-038-12 | Alt | se incluye como sticker y se excluye (con motivo) de la credencial completa. | I | E | TC-038-12-I | E2E-13 | P1 |

### SIGE-US-039 — Programar días y horarios de asistencia de cada docente

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-039-01 | Feliz | la programación queda asociada al docente. | I | — | TC-039-01-I | — | P1 |
| CA-039-02 | Feliz | cada uno se evalúa con la suya. | I | — | TC-039-02-I | — | P1 |
| CA-039-03 | Aud | muestra valor anterior, nuevo, usuario y fecha/hora. | I | — | TC-039-03-I | — | P1 |
| CA-039-04 | Neg | se rechaza. | I | — | TC-039-04-I | — | P1 |
| CA-039-05 | Alt | no se altera retroactivamente lo ya determinado. | I | — | TC-039-05-I | — | P1 |
| CA-039-06 | Perm | se deniega. | I | — | TC-039-06-I | — | P0 |

### SIGE-US-040 — Registrar la ENTRADA de un docente

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-040-01 | Feliz | se guarda con estado ASISTIÓ. | I | E | TC-040-01-I | E2E-14 | P0 |
| CA-040-02 | Límite | el estado es LLEGÓ TARDE. | U | I | TC-040-02-U, TC-040-02-I | — | P0 |
| CA-040-03 | Neg | se rechaza y no se crea registro. | I | U | TC-040-03-I, TC-040-03-U | — | P0 |
| CA-040-04 | Alt | se guarda el evento sin determinar puntualidad y no se le evalúa ausencia ese día. | I | — | TC-040-04-I | — | P0 |
| CA-040-05 | Perm | se rechaza la operación. | I | — | TC-040-05-I | — | P0 |
| CA-040-06 | Neg | se rechaza el registro. | I | — | TC-040-06-I | — | P0 |
| CA-040-07 | Feliz | el sistema no procesa el registro hasta que elige ENTRADA o SALIDA. | I | E | TC-040-07-I | E2E-14 | P0 |
| CA-040-08 | Feliz | se rechaza (RN-AST-21). | I | E | TC-040-08-I | E2E-14 | P0 |
| CA-040-09 | Límite | es ASISTIÓ; a las 08:01, LLEGÓ TARDE. | U | I | TC-040-09-U, TC-040-09-I | — | P0 |
| CA-040-10 | Feliz | el 100 % tiene fecha, hora y estado correctos y 0 docentes tienen más de una ENTRADA en la m… | I | E | TC-040-10-I | E2E-14 | P0 |
| CA-040-11 **(nuevo)** | Neg | se rechaza con QR_REVOKED y alerta de verificación manual; si el token no existe o pertenece… | I | — | TC-040-11-I | — | P0 |

### SIGE-US-041 — Registrar la SALIDA de un docente

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-041-01 | Feliz | se registra la hora efectiva del escaneo. | I | E | TC-041-01-I | E2E-14 | P0 |
| CA-041-02 | Neg | se rechaza. | I | — | TC-041-02-I | — | P0 |
| CA-041-03 | Feliz | se conserva 14:20 sin ajustarla. | I | E | TC-041-03-I | E2E-14 | P0 |
| CA-041-04 | Neg | el sistema no genera una salida automática. | I | — | TC-041-04-I | — | P0 |
| CA-041-05 | Alt | se guarda con la marca "SALIDA SIN ENTRADA" visible en el historial. | I | — | TC-041-05-I | — | P0 |
| CA-041-06 | Perm | se rechaza. | I | — | TC-041-06-I | — | P0 |
| CA-041-07 | Feliz | 0 docentes tienen más de una SALIDA en la misma fecha (KPI-74). | I | E | TC-041-07-I | E2E-14 | P0 |

### SIGE-US-042 — Detectar automáticamente las ausencias de docentes

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-042-01 | Feliz | se le asigna FALTÓ con origen AUTOMÁTICO. | I | U+E | TC-042-01-I, TC-042-01-U | E2E-14 | P0 |
| CA-042-02 | Neg | no se le genera ausencia. | I | U | TC-042-02-I, TC-042-02-U | — | P0 |
| CA-042-03 | Feliz | no se realiza ninguna acción. | I | U+E | TC-042-03-I, TC-042-03-U | E2E-14 | P0 |
| CA-042-04 | Feliz | el umbral de cada docente es su hora esperada de entrada del día + su tolerancia efectiva +… | I | U+E | TC-042-04-I, TC-042-04-U | E2E-14 | P0 |
| CA-042-05 | Alt | el estado se reclasifica según su límite de entrada, sin contarse como segunda entrada, con… | I | — | TC-042-05-I | — | P0 |
| CA-042-06 | Aud | su origen es AUTOMÁTICO. | I | — | TC-042-06-I | — | P0 |
| CA-042-07 **(nuevo)** | Neg | se rechaza como duplicada con details.reason = "MANUAL_STATE_PREVAILS" y el estado manual no… | I | U | TC-042-07-I, TC-042-07-U | — | P0 |
| CA-042-08 **(nuevo)** | Neg | no se asigna FALTÓ a ningún docente, el JOB_RUN del día queda OMITIDO y el Administrador rec… | I | U | TC-042-08-I, TC-042-08-U | — | P0 |

### SIGE-US-043 — Justificar o modificar la asistencia de un docente

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-043-01 | Feliz | se aplica el nuevo estado. | I | E | TC-043-01-I | E2E-11 | P0 |
| CA-043-02 | Aud | conserva usuario, fecha/hora, estado anterior, nuevo, motivo y origen MANUAL. | I | — | TC-043-02-I | — | P0 |
| CA-043-03 | Neg | se rechaza. | I | — | TC-043-03-I | — | P0 |
| CA-043-04 | Perm | se rechaza. | I | — | TC-043-04-I | — | P0 |
| CA-043-05 | Neg | se rechaza. | I | — | TC-043-05-I | — | P0 |

### SIGE-US-044 — Consultar el historial de asistencia docente

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-044-01 | Feliz | ve por día entrada, salida, estado y origen. | I | — | TC-044-01-I | — | P1 |
| CA-044-02 | Feliz | las ve con su trazabilidad. | I | — | TC-044-02-I | — | P1 |
| CA-044-03 | Feliz | todos los registros siguen disponibles. | I | — | TC-044-03-I | — | P1 |
| CA-044-04 | Perm | se deniega. | I | — | TC-044-04-I | — | P0 |
| CA-044-05 | UX | se muestra estado vacío. | E | — | — | E2E-12 | P2 |

## EP-07 — Reportes


### SIGE-US-045 — Registrar un reporte escolar

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-045-01 | Feliz | el reporte se guarda con estado REGISTRADO POR DOCENTE y queda disponible para el prefecto. | I | E | TC-045-01-I | E2E-15 | P1 |
| CA-045-02 | Límite | se rechaza; con 50 y con 100 se acepta. | U | I | TC-045-02-U, TC-045-02-I | — | P1 |
| CA-045-03 | Límite | se rechaza. | U | I | TC-045-03-U, TC-045-03-I | — | P1 |
| CA-045-04 | UX | un contador de caracteres visible se actualiza. | E | — | — | E2E-15 | P2 |
| CA-045-05 | Neg | se rechaza. | I | — | TC-045-05-I | — | P1 |
| CA-045-06 | Perm | se rechaza. | I | — | TC-045-06-I | — | P0 |
| CA-045-07 | Neg | se rechaza. | I | — | TC-045-07-I | — | P1 |
| CA-045-08 | Feliz | solo aparecen las opciones predeterminadas correspondientes a esa combinación. | I | E | TC-045-08-I | E2E-15 | P1 |
| CA-045-09 | Feliz | las validaciones y datos son idénticos (CT-04). | I | E | TC-045-09-I | E2E-15 | P1 |
| CA-045-10 | Perm | se rechaza. | I | — | TC-045-10-I | — | P0 |
| CA-045-11 | Alt | el reporte queda en la bandeja de PAD/ADM y se genera una alerta. | I | E | TC-045-11-I | E2E-15 | P1 |

### SIGE-US-046 — Consultar la bandeja y el estado de los reportes

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-046-01 | Perm | solo ve los reportes que él registró. | I | — | TC-046-01-I | — | P0 |
| CA-046-02 | Feliz | ven todos los reportes filtrables por tipo, gravedad, grupo, estudiante y estado. | I | — | TC-046-02-I | — | P1 |
| CA-046-03 | Perm | ve únicamente los reportes de los grupos que tiene asignados. | I | — | TC-046-03-I | — | P0 |
| CA-046-04 | Perm | se rechaza. | I | — | TC-046-04-I | — | P0 |
| CA-046-05 | Perm | se deniega. | I | — | TC-046-05-I | — | P0 |
| CA-046-06 | UX | se muestra estado vacío o de error con reintento. | E | — | — | E2E-15 | P2 |

### SIGE-US-047 — Revisar un reporte y canalizarlo o rechazarlo (prefecto)

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-047-01 | Feliz | pasa a REVISADO POR PREFECTO. | I | E | TC-047-01-I | E2E-15 | P1 |
| CA-047-02 | Feliz | pasa a CANALIZADO y aparece en la bandeja de PAD. | I | E | TC-047-02-I | E2E-15 | P1 |
| CA-047-03 | Neg | se rechaza (no se saltan etapas). | I | — | TC-047-03-I | — | P1 |
| CA-047-04 | Alt | el reporte queda RECHAZADO (fin del flujo del original) y se notifica al docente. | I | E | TC-047-04-I | E2E-15 | P1 |
| CA-047-05 | Neg | se rechaza la acción. | I | — | TC-047-05-I | — | P1 |
| CA-047-06 | Aud | hay una entrada con usuario y fecha/hora. | I | — | TC-047-06-I | — | P1 |
| CA-047-07 | Perm | se rechaza. | I | — | TC-047-07-I | — | P0 |
| CA-047-08 | Alt | puede valorarlo de nuevo. | I | — | TC-047-08-I | — | P1 |

### SIGE-US-048 — Corregir un reporte rechazado mediante uno nuevo referenciado

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-048-01 | Feliz | ve el motivo registrado. | I | E | TC-048-01-I | E2E-16 | P1 |
| CA-048-02 | Feliz | queda referenciado explícitamente al original, que permanece sin modificación y archivado. | I | — | TC-048-02-I | — | P1 |
| CA-048-03 | Alt | el original permanece RECHAZADO y no se genera reporte nuevo. | I | E | TC-048-03-I | E2E-16 | P1 |
| CA-048-04 | Feliz | pasa por todas las validaciones de registro (rango de observación, tipo, gravedad). | I | — | TC-048-04-I | — | P1 |
| CA-048-05 | Neg | se rechaza. | I | — | TC-048-05-I | — | P1 |
| CA-048-06 | Perm | se rechaza. | I | — | TC-048-06-I | — | P0 |

### SIGE-US-049 — Revisar reportes canalizados y aprobarlos o devolverlos (administrativo)

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-049-01 | Feliz | pasa a REVISADO POR ADMINISTRATIVO. | I | E | TC-049-01-I | E2E-15 | P1 |
| CA-049-02 | Alt | el reporte regresa a la revisión del prefecto. | I | — | TC-049-02-I | — | P1 |
| CA-049-03 | Neg | se rechaza la acción. | I | — | TC-049-03-I | — | P1 |
| CA-049-04 | Neg | se rechaza. | I | — | TC-049-04-I | — | P1 |
| CA-049-05 | Perm | se rechaza. | I | — | TC-049-05-I | — | P0 |
| CA-049-06 | Aud | se registra. | I | — | TC-049-06-I | — | P1 |

### SIGE-US-050 — Decidir si un reporte se comunica a la familia o se resuelve internamente

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-050-01 | Feliz | queda autorizado y SIGE verifica que exista un contacto válido. | I | E | TC-050-01-I | E2E-15 | P1 |
| CA-050-02 | Neg | el reporte queda AUTORIZADO pendiente de contacto y no se envía nada. | I | — | TC-050-02-I | — | P1 |
| CA-050-03 | Alt | el reporte pasa a RESUELTO. | I | — | TC-050-03-I | — | P1 |
| CA-050-04 | Neg | se rechaza. | I | — | TC-050-04-I | — | P1 |
| CA-050-05 | Perm | se rechaza (nunca desde el registro del docente ni la revisión del prefecto). | I | — | TC-050-05-I | — | P0 |
| CA-050-06 | UX | ve la advertencia. | E | — | — | E2E-15 | P2 |

### SIGE-US-051 — Consultar la trazabilidad completa de un reporte

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-051-01 | Feliz | ve cada estado con usuario y fecha/hora. | I | — | TC-051-01-I | — | P1 |
| CA-051-02 | Perm | ve lo que su rol permite y no el de reportes ajenos. | I | — | TC-051-02-I | — | P0 |
| CA-051-03 | Feliz | aparece el rechazo con su motivo y el reporte nuevo referenciado. | I | — | TC-051-03-I | — | P1 |
| CA-051-04 | Neg | se rechaza. | I | — | TC-051-04-I | — | P1 |
| CA-051-05 | Feliz | tienen su flujo completo trazado. | I | — | TC-051-05-I | — | P1 |

## EP-08 — Comunicación


### SIGE-US-052 — Enviar por correo la comunicación autorizada a la familia

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-052-01 | Feliz | se envía un correo al contacto con solo la información autorizada. | I | E | TC-052-01-I | E2E-17 | P1 |
| CA-052-02 | Neg | nunca incluye el expediente completo del estudiante. | I | — | TC-052-02-I | — | P1 |
| CA-052-03 | UX | ve exactamente lo que saldrá. | E | — | — | E2E-17 | P2 |
| CA-052-04 | Neg | se rechaza. | I | — | TC-052-04-I | — | P1 |
| CA-052-05 | Neg | se rechaza. | I | — | TC-052-05-I | — | P1 |
| CA-052-06 | Feliz | el reporte pasa a COMUNICADO A FAMILIA y luego a RESUELTO. | I | E | TC-052-06-I | E2E-17 | P1 |
| CA-052-07 | Alt | el envío no se completa y el estado se registra sin afectar las funciones internas. | I | — | TC-052-07-I | — | P1 |
| CA-052-08 | Neg | se rechaza y se advierte al PAD. | I | — | TC-052-08-I | — | P1 |

### SIGE-US-053 — Registrar el estado de cada envío y reintentarlo

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-053-01 | Feliz | se registra fecha, hora y estado PENDIENTE, ENVIADO o FALLIDO. | I | — | TC-053-01-I | — | P1 |
| CA-053-02 | Alt | el estado permanece FALLIDO y aparece la opción de reintento manual. | I | E | TC-053-02-I | E2E-17 | P1 |
| CA-053-03 | Feliz | el estado pasa a ENVIADO conservando el intento fallido en el historial. | I | — | TC-053-03-I | — | P1 |
| CA-053-04 | Neg | nunca se presenta como "leído". | I | U | TC-053-04-I, TC-053-04-U | — | P1 |
| CA-053-05 | Feliz | no se interpreta como confirmación de lectura. | I | E | TC-053-05-I | E2E-17 | P1 |

## EP-09 — Administración


### SIGE-US-054 — Administrar catálogos institucionales

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-054-01 | Feliz | el cambio queda disponible para el resto del sistema. | I | — | TC-054-01-I | — | P1 |
| CA-054-02 | Perm | se rechaza. | I | — | TC-054-02-I | — | P0 |
| CA-054-03 | Alt | se ofrece desactivarlo y el historial no se altera. | I | — | TC-054-03-I | — | P1 |
| CA-054-04 | Neg | se rechaza. | I | U | TC-054-04-I, TC-054-04-U | — | P1 |
| CA-054-05 | UX | ve una advertencia de uso. | E | — | — | E2E-18 | P2 |
| CA-054-06 | Perm | no existe ninguna interfaz para hacerlo. | I | E | TC-054-06-I | E2E-18 | P0 |
| CA-054-07 | Perm | se rechaza sin importar el rol. | I | — | TC-054-07-I | — | P0 |

### SIGE-US-055 — Configurar los parámetros operativos de asistencia

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-055-01 | Feliz | el valor se guarda y aplica desde el momento del cambio. | I | U | TC-055-01-I, TC-055-01-U | — | P0 |
| CA-055-02 | Límite | se rechaza. | U | I | TC-055-02-U, TC-055-02-I | — | P1 |
| CA-055-03 | Feliz | el otro no cambia. | I | — | TC-055-03-I | — | P1 |
| CA-055-04 | Aud | aparece con usuario, fecha/hora, valor anterior y nuevo. | I | — | TC-055-04-I | — | P1 |
| CA-055-05 | Neg | no cambian. | I | — | TC-055-05-I | — | P1 |
| CA-055-06 | Perm | se rechaza. | I | — | TC-055-06-I | — | P0 |
| CA-055-07 | Feliz | usa 5 min de rebote, 10:00 de verificación para el turno matutino y 16:00 de verificación pa… | I | — | TC-055-07-I | — | P1 |
| CA-055-08 | Neg | se rechaza. | I | U | TC-055-08-I, TC-055-08-U | — | P0 |
| CA-055-09 | Neg | se rechaza. | I | U | TC-055-09-I, TC-055-09-U | — | P0 |
| CA-055-10 | Neg | se rechaza (dejaría la verificación sin ser posterior al corte). | I | U | TC-055-10-I, TC-055-10-U | — | P0 |

### SIGE-US-056 — Ver el panel de indicadores operativos

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-056-01 | Feliz | ve asistencia del día, reportes abiertos y credenciales pendientes. | I | E | TC-056-01-I | E2E-18 | P1 |
| CA-056-02 | Feliz | la cifra refleja el dato vigente. | I | E | TC-056-02-I | E2E-18 | P1 |
| CA-056-03 | Perm | se deniega. | I | E | TC-056-03-I | E2E-18 | P0 |
| CA-056-04 | UX | se muestra estado vacío o de error con reintento. | E | — | — | E2E-18 | P2 |

## EP-10 — Continuidad


### SIGE-US-057 — Respaldar y restaurar la base de datos

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-057-01 | Feliz | el respaldo se ejecuta automáticamente sin intervención y se registra su resultado (éxito o… | I | O | TC-057-01-I, TC-057-01-O | — | P0 |
| CA-057-02 | Alt | el ADM ve una alerta. | I | O | TC-057-02-I, TC-057-02-O | — | P0 |
| CA-057-03 | Feliz | la base de datos se recupera íntegra (100 % de los respaldos de prueba recuperados). | O | I | TC-057-03-O, TC-057-03-I | — | P0 |
| CA-057-04 | Feliz | se restaura desde el último respaldo válido y el sistema vuelve a operar. | O | I | TC-057-04-O, TC-057-04-I | — | P0 |
| CA-057-05 | Feliz | se verifica la integridad de los datos recuperados. | O | I | TC-057-05-O, TC-057-05-I | — | P0 |
| CA-057-06 | Feliz | el entorno queda operativo siguiendo solo esa documentación. | I | — | TC-057-06-I | — | P0 |
| CA-057-07 **(nuevo)** | Aud | queda un registro de la restauración (fecha, respaldo usado, responsable y resultado) en la… | O | I | TC-057-07-O, TC-057-07-I | — | P0 |

### SIGE-US-058 — Operar las funciones internas sin Internet

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-058-01 | Feliz | todo funciona con normalidad. | I | — | TC-058-01-I | — | P0 |
| CA-058-02 | Alt | solo esas funciones no están disponibles, con mensaje que lo explica. | I | E | TC-058-02-I | E2E-19 | P0 |
| CA-058-03 | Alt | la app muestra el mensaje de "sin conexión al servidor" y activa el modo offline (US-032), d… | I | E | TC-058-03-I | E2E-19 | P0 |
| CA-058-04 | Feliz | el 100 % se supera (KPI-31/43). | I | — | TC-058-04-I | — | P0 |
| CA-058-05 | Feliz | el 100 % de las conexiones funciona sin Internet. | I | — | TC-058-05-I | — | P0 |

## EP-06 — Asistencia docente


### SIGE-US-059 — Editar la ficha de un docente

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-059-01 | Feliz | la ficha se actualiza y la edición queda auditada. | I | — | TC-059-01-I | — | P1 |
| CA-059-02 | Neg | el campo está bloqueado y la API rechaza el cambio. | I | — | TC-059-02-I | — | P1 |
| CA-059-03 | Alt | se aplica y la bitácora guarda valor anterior, valor nuevo, usuario, fecha/hora y motivo. | I | — | TC-059-03-I | — | P1 |
| CA-059-04 | Neg | se rechaza. | I | — | TC-059-04-I | — | P1 |
| CA-059-05 | Perm | se deniega. | I | — | TC-059-05-I | — | P0 |
| CA-059-06 | Neg | se rechaza. | I | — | TC-059-06-I | — | P1 |
| CA-059-07 | Neg | se rechaza y la ficha no se modifica. | I | U | TC-059-07-I, TC-059-07-U | — | P1 |

### SIGE-US-060 — Desactivar y reactivar a un docente

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-060-01 | Feliz | pasa a INACTIVO y el cambio queda auditado con usuario, fecha/hora, estatus anterior, nuevo… | I | — | TC-060-01-I | — | P1 |
| CA-060-02 | Neg | se rechaza. | I | — | TC-060-02-I | — | P1 |
| CA-060-03 | Feliz | no se le genera FALTÓ. | I | U | TC-060-03-I, TC-060-03-U | — | P0 |
| CA-060-04 | Neg | se rechaza el registro y el QR no aparece como revocado. | I | — | TC-060-04-I | — | P1 |
| CA-060-05 | Feliz | ve todos sus registros anteriores y su programación suspendida. | I | — | TC-060-05-I | — | P1 |
| CA-060-06 | Perm | se rechaza. | I | — | TC-060-06-I | — | P0 |
| CA-060-07 | Feliz | pasa a ACTIVO, conserva su QR vigente y queda un evento de reactivación distinto del alta or… | I | — | TC-060-07-I | — | P1 |
| CA-060-08 | Alt | SIGE advierte al ADM y la cuenta no se desactiva automáticamente. | I | — | TC-060-08-I | — | P1 |
| CA-060-09 | Neg | se rechaza. | I | — | TC-060-09-I | — | P1 |
| CA-060-10 **(nuevo)** | Feliz | la programación vuelve a aplicar desde esa fecha, no se evalúan retroactivamente los días en… | I | — | TC-060-10-I | — | P1 |

### SIGE-US-061 — Consultar y filtrar docentes

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-061-01 | Feliz | obtiene resultados paginados que cumplen. | I | E | TC-061-01-I | E2E-13 | P1 |
| CA-061-02 | Feliz | ve datos, estatus, estado del QR, programación vigente y acceso a su historial. | I | — | TC-061-02-I | — | P1 |
| CA-061-03 | Alt | aparecen los docentes desactivados con su historial íntegro. | I | — | TC-061-03-I | — | P1 |
| CA-061-04 | Perm | se deniega. | I | E | TC-061-04-I | E2E-13 | P0 |
| CA-061-05 | UX | se muestra un estado vacío; en móvil los resultados se presentan como tarjetas. | E | — | — | E2E-13 | P2 |

### SIGE-US-062 — Vincular a un docente con su cuenta de usuario

| CA | Tipo | Resultado esperado | Nivel | Compl. | Casos | Recorrido E2E | Pri. |
|---|---|---|---|---|---|---|---|
| CA-062-01 | Feliz | el vínculo queda registrado y auditado. | I | — | TC-062-01-I | — | P1 |
| CA-062-02 | Neg | se rechaza (relación 1 a 1). | I | — | TC-062-02-I | — | P1 |
| CA-062-03 | Neg | se rechaza. | I | — | TC-062-03-I | — | P1 |
| CA-062-04 | Neg | se rechaza. | I | — | TC-062-04-I | — | P1 |
| CA-062-05 | Perm | se rechaza. | I | — | TC-062-05-I | — | P0 |
| CA-062-06 | Alt | se rechaza. | I | — | TC-062-06-I | — | P1 |

---

*Fin del anexo.*