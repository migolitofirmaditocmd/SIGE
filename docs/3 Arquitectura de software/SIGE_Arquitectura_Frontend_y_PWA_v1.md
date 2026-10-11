# SIGE — Arquitectura Frontend y Aplicación Móvil
### Sistema Integral de Gestión Escolar

**Archivo:** `SIGE_Arquitectura_Frontend_y_PWA_v1.md` · **Sustituye a:** `PROPUESTA_TECNICA_APP_MOVIL_PWA.md`
**Versión:** 1.0 | **Estado:** Para revisión del equipo
**Fuentes:** Acta Constitutiva v10 (§6.10, OE-10) · Requisitos v3 (RF-MOV-01 a 03, RNF-FIA-01, RNF-FIA-04, RNF-USA-01, RNF-USA-02, RNF-COM-01, RNF-COM-02, RNF-MAN-02) · Reglas de Negocio v3 (RN-MOV-01 a 03, RN-TRX-04, RN-TRX-05, RN-TRX-08 a 10, RN-AUT-06) · Criterios de Aceptación v2 (CT-01 a CT-16) · Historias de Usuario v2 · Arquitectura C4 v2 (ADR-01) · API REST v2 con los parches de PAQ1 · Seguridad y Autenticación v2 (§1, §7) · Modelo de Datos v3.2

---

## 0. Cómo leer este documento

1. **El documento anterior no estaba entre los archivos que recibí.** La sección 5.1 se reconstruyó desde el Acta v10, la Arquitectura C4 y los requisitos; no conserva la redacción original. Si la propuesta original traía argumentos o comparativas adicionales, conviene pasarlos a 5.1.2 antes de archivarla.
2. **La decisión técnica no se reabre:** la aplicación móvil es una **PWA de Next.js** (ADR-01). Esta versión la documenta y la extiende a los cinco roles.
3. **Lo que está fijado y lo que propongo.** Las reglas, requisitos y contratos citados vienen de los documentos del proyecto. Las **elecciones de librerías, valores de tiempo y detalles de implementación** son propuestas mías y llevan la marca **(Propuesta)** y quedaron **aprobadas**; se concentran en el §6, con el parche que implementa cada una (`SIGE_Parches3_Implementacion_Frontend_v1.md`).
4. **Ninguna regla de negocio vive en el frontend** (RN-TRX-05, CT-02). Todo lo que aquí se describe como "validación del cliente" mejora la experiencia, pero el backend decide siempre.

---

## 5.1 Actualización del dictamen PWA

### 5.1.1 Decisión

| Aspecto | Decisión | Fuente |
|---|---|---|
| Tecnología de la "aplicación móvil" | **PWA instalable construida con Next.js**, misma base de código que la plataforma web | ADR-01 (C4 §6), Acta v10 §6.10 |
| Alternativa descartada | Aplicación nativa (iOS y Android) | Mismo ADR |
| Estado del ADR | Pasa de *Propuesta* a *Aceptada* (parche PF-04 de Parches 3) | Esta revisión |
| Referencia al Acta | **Acta Constitutiva v10** (la propuesta anterior citaba la v9) | Acta v10 |

### 5.1.2 Por qué una PWA y no una app nativa

| Criterio | Cómo lo cumple la PWA | Fuente |
|---|---|---|
| Misma API, misma base y mismas reglas | Un solo cliente consume `/api/v1`; no hay segunda implementación de reglas que mantener | RN-API-02, RN-MOV-01, CT-04 |
| Stack acordado en el proyecto | TypeScript y Next.js ya son el stack del frontend | Acta v10 (tabla de tecnologías), R-07 |
| Una sola división de responsabilidades | Next.js presenta, Django decide; sin lógica duplicada | RNF-MAN-02, RN-TRX-05 |
| Operación dentro de la LAN, sin Internet | Se sirve desde el servidor local por HTTPS; el Service Worker mantiene el shell disponible | RF-MOV-03, RN-INF-01, Acta §6.10 |
| Sin dependencia de tiendas de aplicaciones | Se instala desde el navegador; las actualizaciones llegan con el despliegue | Consecuencia de operar sin Internet (RN-INF-01) |
| Captura sin conexión | Service Worker + IndexedDB, hasta 1,000 eventos | RN-MOV-02, RN-MOV-03, RNF-FIA-01 |

### 5.1.3 Limitaciones conocidas y cómo se mitigan

Son las que ya señalan ADR-01 y RNF-COM-02; aquí se les asigna una respuesta concreta.

| Limitación | Impacto | Mitigación en el diseño |
|---|---|---|
| iOS/Safari no soporta *Background Sync* | La sincronización offline solo ocurre con la app abierta | La sincronización se dispara desde la página (eventos `online`, `visibilitychange`, arranque, botón manual y temporizador). **No se usa Background Sync en ningún sistema operativo** (§5.3.5) |
| El navegador puede purgar el almacenamiento local por inactividad | Podrían perderse eventos pendientes | Solicitar almacenamiento persistente; contador de pendientes siempre visible; indicación a los operadores de sincronizar al terminar la jornada (§5.3.7) |
| La cámara exige contexto seguro | Sin HTTPS válido no hay escaneo | Certificado de CA interna instalado y confiado en cada dispositivo (RNF-SEG-01, RNF-COM-02) |
| Instalar y confiar una CA interna en iOS y Android es el principal obstáculo operativo | La PWA no se instala ni registra su Service Worker | Incluirlo en la guía de despliegue y en la matriz de dispositivos (§6, P-F7) |
| Lectores USB (HID) y cámaras UVC en equipos de escritorio | Distintas formas de capturar el QR | Soportar ambos en la pantalla de escaneo (§5.3.4, RNF-COM-01) |
| Sin notificaciones push | Los avisos no llegan con la app cerrada | Fuera de alcance: los avisos son dentro de la aplicación (p. ej. rechazo de un reporte, PO-12) |

### 5.1.4 La aplicación para los cinco roles

Una sola aplicación atiende a los cinco roles de RN-AUT-01. El rol que devuelve el backend determina el menú, las rutas permitidas y qué acciones se muestran; **la interfaz nunca es la única barrera** (CT-03).

La "superficie principal" indica dónde se espera que cada rol trabaje la mayor parte del tiempo; todas las pantallas son responsivas (CT-14).

| Rol | Qué hace en la aplicación | Superficie principal | Escaneo y buffer offline |
|---|---|---|---|
| **Administrador / Directivo (ADM)** | Cuentas, roles y desbloqueos; catálogos (grupos, grados, ciclos) y asignaciones; parámetros operativos; bitácora; respaldos; panel de indicadores; revocar y regenerar QR; reingresar estudiantes; reactivar y vincular docentes; además todo lo que hace PAD | Escritorio | No (RN-AUT-06: no escanea) |
| **Prefecto (PRE)** | Escanear asistencia estudiantil; consultar expedientes y asistencia detallada; bandeja de reportes de **sus grupos**; revisar, canalizar o rechazar reportes | Móvil | **Sí** (escaneo estudiantil y sincronización) |
| **Docente (DOC)** | Registrar reportes escolares; consultar el estado de **sus** reportes; corregir un reporte rechazado con uno nuevo referenciado | Móvil | No |
| **Personal administrativo (PAD)** | Expedientes, tutores y consentimiento; importación masiva; generar QR y exportar credenciales; escaneo estudiantil; asistencia docente (entrada y salida); fichas y programación de docentes; justificar y modificar asistencia; revisión administrativa y comunicación a la familia | Escritorio y móvil | **Sí** (escaneo estudiantil y sincronización). La asistencia docente requiere conexión |
| **Solo lectura (SL)** | Panel de indicadores e información consolidada; ninguna escritura (RN-AUT-02) | Escritorio | No |

Notas:

- El Acta v10 §6.10 describe la aplicación móvil para **docentes**, **prefectos** y **personal autorizado** (PAD y ADM). ADM y SL pueden abrir la misma PWA, pero sus tareas principales (parámetros, bitácora, indicadores) son de escritorio.
- Las **funciones que dependen de Internet** (envío de correo, restablecimiento de contraseña por correo) se muestran con su estado; el resto opera solo con la LAN (RN-INF-01, RN-INF-02).
- **Offline:** solo existe captura sin conexión para el **escaneo de asistencia estudiantil** (RN-MOV-02). Los reportes, la asistencia docente y las consultas requieren conexión con el servidor local.

---

## 5.2 Arquitectura Frontend Next.js

### 5.2.1 Principios

| # | Principio | Origen |
|---|---|---|
| 1 | El frontend **presenta y captura**; el backend valida y decide. Cualquier validación del cliente es solo ayuda de UX | RN-TRX-05, CT-02, RNF-MAN-02 |
| 2 | El **access token vive solo en memoria**; el refresh solo en cookie `HttpOnly`. Ninguno en `localStorage`, `sessionStorage` ni IndexedDB | SEG §1, SG-01 |
| 3 | **Nada de datos personales de menores se guarda en el dispositivo**, salvo lo que fija RN-MOV-02 para el buffer (que no incluye ningún dato del estudiante) | RN-TRX-01, RN-TRX-02, CT-07 |
| 4 | Mismo origen para web y API (proxy inverso): **sin CORS** | SEG §1, C4 |
| 5 | Los nombres de personas se muestran con `display_name` y se ordenan con `sort_name`; **el cliente nunca concatena ni separa nombres** | RN-TRX-08, RN-TRX-10, API §1.5 |
| 6 | Fechas con zona horaria; la interfaz muestra la **zona horaria institucional**; el cliente nunca impone la hora efectiva de un evento en línea | API §1.6, RN-TRX-04 |

### 5.2.2 Estrategia de renderizado: SSR frente a CSR por pantalla

**La restricción que decide todo.** El refresh token viaja en una cookie con `Path=/api/v1/auth/` y el access token solo existe en la memoria del navegador (SEG §1). Por diseño, **el servidor de Next.js no puede autenticarse contra la API en nombre del usuario**: no recibe el refresh y nunca ve el access. Por eso **ninguna pantalla con datos privados se renderiza en el servidor**.

| Tipo de pantalla | Renderizado | Motivo |
|---|---|---|
| Inicio de sesión, recuperar y restablecer contraseña, página de error y página sin conexión | **Estática (SSG)** | No tienen datos privados; cargan rápido y se precachean |
| Shell autenticado (layout, navegación por rol, indicadores de sincronización) | **Estático + hidratación en el cliente** | El rol se conoce después de autenticar, en el navegador |
| **Todas** las pantallas con datos (expedientes, asistencia, reportes, docentes, administración, indicadores) | **CSR** (componentes de cliente que consultan la API con el access token en memoria) | Restricción de SEG §1; además los datos de menores no deben pasar por un renderizado de servidor ni quedar en cachés intermedias |
| Pantalla de escaneo | **CSR** + precacheada por el Service Worker | Debe abrirse sin red y resolver en menos de 250 ms (CT-10) |
| Descargas (reporte de importación, credenciales, QR) | Cliente con `fetch` y `Blob` | El archivo lo genera la API; el servidor de Next.js no lo toca |

**Consecuencias de diseño:**

- Cada pantalla con datos sigue el patrón *shell estático → verificar sesión → consultar → renderizar*, y define sus estados (§5.4.6).
- Ningún `fetch` con credenciales en Server Components, Route Handlers ni *middleware* de Next.js. El *middleware* solo puede aplicar cabeceras o redirecciones sin datos de usuario.
- **Riesgo a validar (P-F4):** la navegación interna del App Router pide cargas de componentes al servidor y podría fallar sin red. El criterio de aceptación es que, **con el dispositivo en modo avión, la PWA instalada abre `/escaneo`, permite capturar y guarda en el buffer**. Si la prueba técnica falla, la alternativa es exportar el frontend como sitio estático y servirlo desde el proxy (**Propuesta**; no cambia nada de lo demás).

### 5.2.3 Estructura de carpetas (Propuesta)

Organizada por módulo de negocio, igual que el backend (AUT, EST, IMP, QR, AST, REP, COM, ADM), para que un cambio de regla toque un solo lugar.

```
sige-frontend/
├─ public/
│  ├─ manifest.webmanifest
│  ├─ icons/                      # 192, 512, maskable y apple-touch-icon
│  └─ sw.js                       # generado en la compilación (§5.3.3)
├─ src/
│  ├─ app/                        # solo rutas: componen features, sin lógica de negocio
│  │  ├─ (publico)/
│  │  │  ├─ iniciar-sesion/
│  │  │  ├─ recuperar-contrasena/
│  │  │  ├─ restablecer-contrasena/
│  │  │  └─ sin-conexion/
│  │  ├─ (app)/                   # layout autenticado: AuthGate + menú por rol + SyncBanner
│  │  │  ├─ inicio/
│  │  │  ├─ escaneo/              # PRE, PAD: asistencia estudiantil y sincronización
│  │  │  ├─ estudiantes/          # listado, alta, expediente, tutores, importaciones
│  │  │  ├─ asistencia/           # consulta por grupo, historial, justificación
│  │  │  ├─ docentes/             # fichas, programación, asistencia docente
│  │  │  ├─ credenciales/         # generar, revocar, exportar QR
│  │  │  ├─ reportes/             # registro, bandeja, revisión, comunicación
│  │  │  └─ administracion/       # usuarios, catálogos, parámetros, bitácora, respaldos, indicadores
│  │  ├─ layout.tsx
│  │  └─ not-found.tsx
│  ├─ features/                   # un directorio por módulo de negocio
│  │  └─ <modulo>/
│  │     ├─ api/                  # llamadas tipadas al módulo (usan shared/lib/api)
│  │     ├─ components/           # pantallas y piezas propias del módulo
│  │     ├─ hooks/                # consultas y mutaciones del módulo
│  │     ├─ schemas/              # esquemas de formulario (solo formato, nunca reglas)
│  │     └─ index.ts              # única entrada pública del módulo
│  └─ shared/
│     ├─ ui/                      # sistema de diseño (§5.4)
│     ├─ lib/
│     │  ├─ api/                  # cliente HTTP, errores, paginación, tipos del OpenAPI
│     │  ├─ auth/                 # sesión en memoria, refresh, guardas por rol
│     │  ├─ format/               # fechas con zona institucional, nombres, estados
│     │  └─ config/               # variables de entorno de cliente (sin secretos)
│     ├─ pwa/
│     │  ├─ offline-db/           # esquema IndexedDB y acceso (§5.3.4)
│     │  ├─ capture/              # cámara, lector HID, decodificación
│     │  ├─ sync/                 # sincronización y offset de reloj (§5.3.5)
│     │  └─ sw-register.ts        # registro y actualización del Service Worker
│     └─ styles/tokens.css        # tokens del sistema de diseño (§5.4.2)
└─ tests/                         # unitarias, componentes y E2E (incluye flujos sin conexión)
```

**Reglas de dependencia:**

1. `app/` importa de `features/` y `shared/`; **no** contiene lógica.
2. Un `feature` **no importa de otro `feature`**; lo común sube a `shared/`.
3. `shared/` no importa de `features/`.
4. Los esquemas de `schemas/` validan **formato** (obligatorio, longitud, correo); nunca duplican reglas como "matrícula única" o "tutor válido" (RN-TRX-05).

### 5.2.4 Manejo de estado

| Tipo de estado | Dónde vive | Herramienta (Propuesta) | Se persiste |
|---|---|---|---|
| **Datos del servidor** (expedientes, asistencia, reportes…) | Caché de consultas en memoria | TanStack Query | **No.** No se guarda caché en disco (datos de menores) |
| **Sesión** (access token, `user`) | Módulo de sesión en memoria | Almacén propio con `useSyncExternalStore` | **No** |
| **Estado de pantalla** (diálogos, pestañas) | Componente | `useState` / `useReducer` | No |
| **Filtros y paginación** | Parámetros de la URL | `useSearchParams` | En la URL (compartible, funciona el botón Atrás) |
| **Formularios** | Componente | React Hook Form + Zod | No |
| **Buffer offline y reloj** | IndexedDB (`sige-offline`) | Capa propia sobre `idb` | **Sí**, solo lo que fija el §5.3.4 |
| **Estado de sincronización** (pendientes, último resultado) | Derivado del buffer + memoria | `useSyncExternalStore` sobre `shared/pwa/sync` | La fuente de verdad es IndexedDB |

Reglas:

- Tras una mutación se **invalidan** las consultas afectadas; nunca se actualiza la caché a mano con suposiciones de negocio.
- Al cerrar sesión se ejecuta `queryClient.clear()`.
- No se necesita una librería de estado global adicional.

### 5.2.5 Sesión

**Arranque (carga o recarga de la página):**

1. El access token no existe en memoria. La app llama a `POST /auth/refresh/` (la cookie viaja sola, mismo origen).
2. Éxito: guarda el `access` en memoria, programa la renovación y obtiene el `user` (ver **P-F1**) → pinta el shell del rol.
3. `401`: redirige a `iniciar-sesion` conservando solo una ruta **relativa y del mismo origen** (`?siguiente=`), para evitar redirecciones abiertas.

**Renovación (alineada con SEG §1):**

| Disparador | Comportamiento |
|---|---|
| Proactivo | Renueva cuando queda cerca del **80 %** de `expires_in` (unos 12 min de 15) mientras la pestaña está visible **(Propuesta)** |
| Reactivo | Ante `401 TOKEN_EXPIRED`, renueva **una vez** y repite la petición original; si falla, vuelve a iniciar sesión |
| `401 SESSION_REVOKED` (PO-03) | **No intenta renovar**: limpia la sesión y vuelve a iniciar sesión con el aviso "Tu sesión fue cerrada por el administrador" |
| `429` en el login | Muestra la cuenta regresiva a partir de `Retry-After` |

**Concurrencia entre pestañas (punto crítico).** El refresh **rota** en cada uso, y un refresh reutilizado revoca **todas** las sesiones del usuario (`REUSE_DETECTED`). Dos pestañas que renueven al mismo tiempo podrían presentar la misma cookie y provocar un cierre de sesión general. Por eso:

- Dentro de una pestaña: **una sola renovación en vuelo** (promesa compartida).
- Entre pestañas: la renovación se serializa con **Web Locks** (`navigator.locks.request('sige-auth-refresh', …)`); cada pestaña renueva con la cookie vigente en ese momento **(Propuesta)**.
- Si el navegador no soporta Web Locks, se usa un *líder* de pestaña por `BroadcastChannel`; si tampoco existe, se renueva con retraso aleatorio y se avisa del riesgo en la matriz de dispositivos (P-F7).

**Cerrar sesión:** si hay eventos pendientes, advierte y **no los borra** (SEG §7); llama a `POST /auth/logout/`; limpia memoria y caché de consultas; **conserva** el buffer de IndexedDB.

**Dispositivo compartido:** los eventos del buffer conservan el `user_id` de quien los capturó; otra persona que inicie sesión ve solo el número de pendientes y puede sincronizarlos (el backend valida el rol y la cuenta de quien capturó, SEG §7).

### 5.2.6 Capa de acceso a la API

**Cliente HTTP** (`shared/lib/api`):

| Aspecto | Especificación |
|---|---|
| Base | `/api/v1` en el mismo origen, `credentials: 'same-origin'` |
| Autenticación | `Authorization: Bearer <access>` tomado de la sesión en memoria |
| Tipos | Generados desde el OpenAPI en `/api/v1/schema/` (API §1.1) con `openapi-typescript` **(Propuesta)**; la compilación en CI falla si el esquema cambió y los tipos no se regeneraron |
| Errores | Todo error se convierte en `ApiError { status, error_code, message, details, rn_reference, trace_id, retryAfter }` según API §1.2 |
| Reintentos | Las consultas `GET` se reintentan una vez ante error de red. Las escrituras **no** se reintentan automáticamente, salvo las idempotentes con `client_event_id` (escaneo y sincronización) |
| Tiempo máximo | 10 s por petición **(Propuesta)**; el escaneo tiene su propio tiempo, ver §5.3.4 |
| Paginación | `page` y `page_size` (máximo 100); respuesta `{ count, next, previous, results }` (API §1.5) |
| Fechas | ISO 8601 con zona; se muestran con `Intl.DateTimeFormat` en la zona institucional, configurada, no escrita en el código |
| Personas | `display_name` para mostrar y `sort_name` para ordenar; nunca `nombre + apellido` armado en el cliente |
| Idioma | Los mensajes de la API ya vienen en español (RF-API-04); el cliente solo agrega contexto |

**Códigos de la API que el cliente trata de forma especial:**

| Respuesta | Qué hace el cliente |
|---|---|
| `401 TOKEN_EXPIRED` | Renueva y repite una vez |
| `401 SESSION_REVOKED` | Cierra sesión localmente sin renovar |
| `403 PERMISSION_DENIED` | Estado "Permiso denegado" (§5.4.6) |
| `404` | "No encontrado". En reportes, no insinúa que exista (RN-REP-05) |
| `422` + `error_code` | Muestra `message`; en formularios asocia `details` a cada campo |
| `422 GUARDIAN_MATCH_FOUND` | Abre la selección de tutor existente o motivo para declinar (4.3.1) |
| `422 CONFIRMATION_REQUIRED` | Abre el diálogo "Este cambio afectará a N estudiantes" con `details.affected_students` y reenvía con `confirm=true` (4.3.3, PO-13) |
| `429` | Muestra la espera a partir de `Retry-After` |
| Error de red o `5xx` | "Servidor no disponible" con **Reintentar** (CA-001-07). Siempre se muestra el `trace_id` para soporte (CT-09) |

**Mapa de módulos** (los contratos completos están en la API REST):

| Módulo | Endpoints que usa el frontend | Roles |
|---|---|---|
| AUT | `/auth/login/`, `/auth/refresh/`, `/auth/logout/`, `/auth/password-reset/`, `/users/`, `/users/{id}/unlock/`, `/users/{id}/deactivate/` | Todos; usuarios solo ADM |
| EST y tutores | `/students/`, `/students/{id}/`, `/students/{id}/photo/`, `/students/{id}/status/`, `/students/{id}/reinstate/`, `/guardians/{id}/`, `/guardians/{id}/split/`, `/student-guardians/{id}/consent/` | ADM, PAD; consulta también PRE |
| IMP | `/imports/template/`, `/imports/upload/`, `/imports/{id}/confirm/`, `/imports/{id}/cancel/`, `/imports/{id}/report/` | ADM, PAD |
| QR y credenciales | `/credentials/tokens/`, `/credentials/exports/preview/`, `/credentials/exports/` | ADM, PAD (revocar solo ADM) |
| AST estudiantil | `/attendance/students/scan/`, `/attendance/students/sync/`, `/attendance/students/`, `/attendance/students/history/`, `/attendance/students/{id}/justify/`, `/attendance/summary/` | PRE y PAD escanean; ADM y PAD justifican |
| AST docente | `/teachers/`, `/teachers/{id}/schedule/`, `/attendance/teachers/scan/`, `/attendance/teachers/{id}/justify/` | PAD (ADM reactiva y vincula) |
| REP | `/reports/`, `/reports/{id}/transitions/`, `/reports/{id}/history/`, `/reports/presets/` | DOC registra; PRE revisa y canaliza; PAD revisa |
| COM | `/reports/{id}/communications/`, `/reports/{id}/communications/preview/`, `/communications/`, `/communications/{id}/retry/` | PAD |
| ADM y operación | `/settings/parameters/`, `/catalogs/…`, `/assignments/…`, `/audit-log/`, `/ops/backups/`, `/dashboard/` | ADM; `/dashboard/` también SL |
| Sistema | `/system/status/` (`server_time`, `database`, `internet`, `smtp`, `last_backup`) | Cualquier usuario autenticado |

### 5.2.7 Rutas, guardas y navegación por rol

- **AuthGate** envuelve el layout `(app)`: sin sesión redirige al login; con sesión pinta el menú del rol.
- El menú se arma desde una tabla `rol → rutas` (la de §5.1.4). Una ruta no permitida muestra "Permiso denegado"; **el backend rechaza igualmente con 403**.
- Los elementos de acción (botones) se ocultan si el rol no puede ejecutarlos, pero no se confía en eso (CT-03).
- Los filtros y la paginación viven en la URL; los diálogos de acción con motivo obligatorio (desactivar, reactivar, justificar, revocar QR) usan un único componente `ConfirmarConMotivo` (§5.4.5).

### 5.2.8 Seguridad del cliente (Propuesta)

| Control | Valor |
|---|---|
| Política de contenido (CSP) | `default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; media-src 'self' blob:; connect-src 'self'; worker-src 'self'; frame-ancestors 'none'; base-uri 'self'`. `script-src 'self'` bloquea los scripts en línea que genera Next.js: hay que autorizarlos con *hashes* en la compilación o con *nonce*, y comprobarlo en la prueba P-F4. Si no fuera viable, `'unsafe-inline'` en `script-src` es el último recurso y se documenta como excepción |
| Permisos del navegador | `Permissions-Policy: camera=(self), microphone=(), geolocation=()` |
| Otras cabeceras | `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`; HSTS lo aplica el proxy (SEG §5) |
| Recursos externos | **Ninguno**: ni CDN, ni fuentes remotas, ni analítica. Sin Internet, todo debe cargar desde el servidor local (RN-INF-01) |
| Dependencias | Versiones fijadas en el *lockfile*; revisión de vulnerabilidades en CI |
| Mensajes de error | Nunca se muestra la pila ni datos del servidor; solo `message` y `trace_id` |

### 5.2.9 Calidad y pruebas (Propuesta)

| Nivel | Qué cubre |
|---|---|
| Unitarias | `shared/lib` (cliente HTTP, errores, sesión, cálculo de offset), esquemas de formulario |
| Componentes | Los siete estados de interfaz de cada pantalla (§5.4.6) y el panel de resultado de escaneo |
| Extremo a extremo | Flujos críticos por rol, incluyendo **sin conexión** (el navegador de pruebas puede simular la desconexión): captura con buffer, sincronización, buffer lleno, `QR_REVOKED` diferido y sesión vencida |
| Dispositivos | Matriz de RNF-COM-02 en el Hito 04, con instalación de la CA interna |
| Accesibilidad | Revisión automática más lista manual de CT-14 |

---

## 5.3 Especificación técnica de la PWA

### 5.3.1 Requisitos de plataforma

| Requisito | Detalle | Fuente |
|---|---|---|
| HTTPS con certificado de la CA interna **confiado en el dispositivo** | Sin esto no se registra el Service Worker, no se instala la PWA y no hay cámara | RNF-SEG-01, RNF-COM-02, SEG §5 |
| Contexto seguro | `getUserMedia`, `crypto.randomUUID()`, Service Worker y Web Locks lo exigen | ADR-01 |
| Navegadores y SO soportados | **Pendiente de definir antes del Hito 04** (P-F7); esta especificación no asume ninguno | RNF-COM-02 |
| Sin Internet | Ningún recurso se pide fuera del servidor local (§5.2.8) | RN-INF-01 |

### 5.3.2 `manifest.webmanifest`

```json
{
  "id": "/",
  "name": "SIGE — Sistema Integral de Gestión Escolar",
  "short_name": "SIGE",
  "description": "Asistencia y reportes escolares",
  "lang": "es-MX",
  "dir": "ltr",
  "start_url": "/inicio?origen=pwa",
  "scope": "/",
  "display": "standalone",
  "orientation": "any",
  "theme_color": "#0A3D91",
  "background_color": "#FFFFFF",
  "categories": ["education", "productivity"],
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ],
  "shortcuts": [
    { "name": "Escanear asistencia", "url": "/escaneo", "icons": [{ "src": "/icons/shortcut-scan.png", "sizes": "96x96" }] },
    { "name": "Reportes", "url": "/reportes", "icons": [{ "src": "/icons/shortcut-reports.png", "sizes": "96x96" }] }
  ]
}
```

Notas:

- `start_url` pasa por `AuthGate`: sin sesión llega al inicio de sesión; con sesión, al `inicio` del rol.
- `theme_color` y `background_color` salen de los tokens (`--color-primary` y fondo blanco, §5.4.2).
- Los accesos directos se muestran a todos; **la guarda de ruta** decide si el rol puede entrar (un DOC que abre "Escanear asistencia" ve "Permiso denegado").
- **iOS** no lee todo el manifest: se agregan además las etiquetas `apple-touch-icon` (180 px), `apple-mobile-web-app-capable` y `apple-mobile-web-app-title` en el `<head>`.
- Se omiten a propósito: notificaciones push, `share_target` y `related_applications` (fuera de alcance).
- **Instalación:** en Android se ofrece un botón propio con `beforeinstallprompt`; en iOS se muestra una guía ("Compartir → Añadir a pantalla de inicio"). Ambas dependen de haber confiado la CA interna.

### 5.3.3 Service Worker: ciclo de vida y estrategias

**Qué hace y qué no hace.** El Service Worker mantiene disponible el *shell* y las pantallas críticas sin red. **No toca tokens, no guarda respuestas de la API y no sincroniza eventos.** Los tokens existen solo en la memoria de la página (SG-01) y por eso un Service Worker no podría autenticar una sincronización en segundo plano: la sincronización ocurre siempre desde la página (§5.3.5).

**Ciclo de vida:**

| Fase | Comportamiento |
|---|---|
| Registro | Solo en producción y por HTTPS, con `scope: '/'`, tras cargar la página. El archivo `sw.js` se sirve con `Cache-Control: no-cache` para detectar versiones nuevas |
| `install` | Abre `sige-shell-<BUILD_ID>` y precachea las **rutas críticas** (`/escaneo`, `/inicio`, `/iniciar-sesion`, `/sin-conexion`), sus recursos estáticos de `_next/static`, los iconos y las fuentes. **No** llama a `skipWaiting()` |
| `waiting` | Si hay una versión nueva, la página muestra "Hay una versión nueva" con el botón **Actualizar** |
| Actualizar | Solo al pulsar el botón y **nunca durante una sincronización en curso** ni en medio de una captura. La página envía `{ type: 'SKIP_WAITING' }`; al cambiar el controlador, recarga |
| `activate` | Borra toda caché cuyo nombre no pertenezca a la versión vigente; después `clients.claim()` |
| Comprobación de versión | `registration.update()` al abrir la app y cada 60 min mientras esté abierta **(Propuesta)** |

**Estrategias de caché:**

| Petición | Estrategia | Nota |
|---|---|---|
| Navegación a una ruta crítica | Red primero con límite de 3 s; si falla, la copia precacheada; si no existe, `/sin-conexion` | Permite abrir la PWA instalada sin red |
| `_next/static/*` (con hash), iconos y fuentes | Caché primero | Son inmutables y no contienen datos personales |
| `manifest.webmanifest` | Obsoleto mientras revalida | |
| `/api/*` | **Solo red. Nunca se guarda en caché** | Datos de menores (RN-TRX-01, RN-TRX-02) y resultados que deben venir siempre del servidor |
| `/api/v1/students/{id}/photo/` | **Solo red**, sin caché del Service Worker | La imagen se muestra desde un `Blob` en memoria y se descarta |
| Cualquier otra | Solo red | |

Complemento del backend **(Propuesta)**: las respuestas con datos personales llevan `Cache-Control: no-store`.

**Esqueleto de `sw.js`** (ilustrativo; la generación real puede apoyarse en una librería de precache):

```js
const BUILD_ID = '__BUILD_ID__';                 // lo inyecta la compilación
const SHELL_CACHE = `sige-shell-${BUILD_ID}`;
const CRITICAL_ROUTES = ['/escaneo', '/inicio', '/iniciar-sesion', '/sin-conexion'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(SHELL_CACHE).then((c) => c.addAll(__PRECACHE_MANIFEST__)));
  // sin skipWaiting(): la actualización la decide el usuario
});

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    for (const name of await caches.keys()) {
      if (name.startsWith('sige-shell-') && name !== SHELL_CACHE) await caches.delete(name);
    }
    await self.clients.claim();
  })());
});

self.addEventListener('message', (e) => { if (e.data?.type === 'SKIP_WAITING') self.skipWaiting(); });

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin || url.pathname.startsWith('/api/')) return;   // red, sin caché
  if (request.mode === 'navigate') event.respondWith(navegacion(request));
  else if (url.pathname.startsWith('/_next/static/')) event.respondWith(cachePrimero(request));
});
// navegacion(): red con límite de 3 s → copia precacheada → /sin-conexion
```

### 5.3.4 Captura y buffer offline

#### Esquema de IndexedDB

Base de datos **`sige-offline`**, versión 1.

```ts
// Almacén "pending_events"  ·  keyPath: client_event_id  ·  índice: by_captured_at (captured_at)
interface PendingScanEvent {
  client_event_id: string;        // UUID v4 generado en el dispositivo (crypto.randomUUID())
  qr_token: string;               // el identificador leído del QR, tal cual
  event_type: 'ESCANEO_ESTUDIANTE';
  captured_at: string;            // ISO 8601 en UTC, con el reloj del dispositivo
  clock_offset_ms: number;        // entero: desfase del reloj conocido en la última conexión
  user_id: string;                // UUID del operador autenticado que capturó
}

// Almacén "meta"  ·  keyPath: key  ·  un único registro
interface ClockMeta {
  key: 'clock';
  offset_ms: number;              // último desfase medido contra el servidor
  measured_at: string;            // ISO 8601: cuándo se midió
}
```

#### Conformidad con RN-MOV-02

RN-MOV-02 fija que el buffer guarda **únicamente** el evento: fecha, hora de captura, tipo de evento e identificador QR leído, sin ningún dato del estudiante.

| Campo de IndexedDB | ¿Es parte del evento de RN-MOV-02? | Por qué está |
|---|---|---|
| `qr_token` | **Sí** (identificador QR leído) | Es lo que se valida al sincronizar |
| `event_type` | **Sí** (tipo de evento) | RN-MOV-02, RF-MOV-01, SEG §7 |
| `captured_at` | **Sí** (fecha y hora de captura) | Base de la hora efectiva (RN-TRX-04) |
| `client_event_id` | No: metadato técnico | Idempotencia al reintentar; es la clave del acuse `OFFLINE_EVENT_RECEIPT` (Modelo §3.8.1) |
| `clock_offset_ms` | No: metadato técnico | **Lo exigen** RN-TRX-04 y RNF-FIA-04: la hora efectiva se corrige con el desfase conocido en la última conexión |
| `user_id` | No: metadato técnico | Se envía como `captured_by` para validar que el operador conserve rol y cuenta activa (SEG §7, API §2.2) |

> **Sobre "nada más".** Los tres primeros campos son exactamente lo que dice RN-MOV-02. Los otros tres **no contienen ningún dato del estudiante**, pero no se pueden quitar sin romper otra regla o el contrato de la API (hora efectiva, idempotencia y atribución). Si se prefiere un buffer de solo tres campos, habría que cambiar RN-TRX-04, RNF-FIA-04 y la API de sincronización; se decidió **mantener los seis campos** (P-F5, aprobado) y alinear RN-MOV-02, RF-MOV-01, CA-032-01, CA-032-07 y SEG §7 (PF-05 y PF-06 de Parches 3).

**Lo que nunca se guarda en el dispositivo:** nombre, matrícula, grupo, fotografía ni estatus del estudiante; el resultado de una validación; el acuse del servidor; tokens de sesión; ni una lista local de tokens QR válidos o revocados.

El almacén `meta` guarda **solo el desfase de reloj** (no datos de eventos ni de personas). Es necesario para poder capturar sin conexión después de recargar la página.

**Reglas del almacén:**

| Regla | Cómo se cumple |
|---|---|
| Máximo 1,000 eventos (RN-MOV-03) | Se cuenta y se agrega en **una sola transacción de escritura**; si hay 1,000, la transacción se cancela con `BUFFER_FULL` y la interfaz alerta al operador. Una transacción de escritura sobre el mismo almacén se serializa entre pestañas, así que dos pestañas no pueden pasar del tope |
| El evento es "pendiente de validación" | La sola presencia en `pending_events` lo significa; no hay campo de estado |
| Un evento solo sale cuando el servidor confirma (SEG §7) | Se borra por `client_event_id` únicamente cuando aparece en `accepted` o `discarded` de la respuesta |
| Evolución del esquema | Las migraciones de IndexedDB (`onupgradeneeded`) **nunca borran** `pending_events`; solo agregan índices o almacenes |

#### Flujo de captura

1. **Lectura.** La cámara (o el lector HID) entrega un texto. Si **no tiene formato UUID**, se muestra "Código no reconocido" y **no se guarda ni se envía**. Es un filtro de formato para no ensuciar el buffer; el servidor sigue decidiendo si el token existe (RN-QR-02).
2. **Antirrebote técnico.** Ignorar el mismo texto leído de nuevo en menos de unos 1.5 s, para que un mismo fotograma no genere dos eventos **(Propuesta)**. No sustituye la ventana de rebote del negocio (RN-AST-02), que aplica el backend.
3. **Identidad del evento.** Se genera `client_event_id` y se toma `captured_at` del reloj del dispositivo **en ese instante**, antes de enviar nada.
4. **Camino en línea.** `POST /attendance/students/scan/` con `{ qr_token, client_event_id }`, con límite de **3 s** **(Propuesta)**. El cliente **no envía hora**: la hora efectiva es la del servidor (RN-TRX-04).
   - Cualquier respuesta HTTP con cuerpo de la API (200, 201, 4xx) se muestra al operador (§5.4.4).
   - `401 TOKEN_EXPIRED`: renueva una vez y repite.
   - Error de red, agotamiento del límite, `502`, `503` o `504` → **camino sin conexión**, con el mismo `client_event_id`.
5. **Camino sin conexión.**
   - Si no hay medición de reloj en `meta`, **no se captura** y se muestra "Conéctate al servidor una vez para calibrar el reloj"; sin desfase conocido no se puede cumplir RN-TRX-04.
   - Si hay desfase, se guarda el evento (regla del tope arriba) y se muestra "Capturado sin conexión, pendiente de validación", **sin nombre ni foto** (no se conocen).
   - Si `|clock_offset_ms|` supera 5 minutos, se avisa al operador "La hora de este dispositivo difiere del servidor". Es solo una advertencia: el backend marca esos eventos para revisión (SEG §7).
6. **Detección de modo.** Se considera sin conexión cuando el navegador lo reporta (`offline`) o fallan dos consultas seguidas a `GET /system/status/` (una cada 15 s con la app visible **(Propuesta)**). Se muestra un indicador persistente **"Sin conexión — N eventos pendientes"** (US-032). Al volver, se dispara la sincronización.

**Captura del QR:**

- **Cámara:** `getUserMedia({ video: { facingMode: 'environment' } })`. Estados propios: permiso denegado, sin cámara y contexto no seguro.
- **Decodificación:** `BarcodeDetector` si el navegador lo ofrece; si no, un decodificador en JavaScript o WebAssembly **(Propuesta; la librería se elige en el Hito 04 según la matriz de dispositivos, P-F7)**.
- **Lector USB (HID):** escucha de teclado en la pantalla de escaneo; acumula caracteres con intervalos muy cortos y cierra la lectura con `Enter` (RNF-COM-01).

#### Desfase de reloj

- Se mide con `GET /system/status/` (`server_time`): al iniciar sesión, al renovar el token y cada 5 minutos mientras haya conexión **(Propuesta)**.
- `offset = server_time − (inicio de la petición + duración/2)`, con los tiempos del dispositivo medidos con `performance.now()` para compensar la latencia. Se guarda redondeado en `ClockMeta`.
- **Convención de signo (P-F3):** `clock_offset_ms = hora_del_servidor − hora_del_dispositivo`, de modo que la hora efectiva es `captured_at + clock_offset_ms`. Los documentos no fijan el signo (el ejemplo de la API usa `1200` sin explicarlo); **debe confirmarse con el backend antes de implementar**.
- Cada evento guarda el desfase **conocido al capturarlo** (RN-TRX-04). No se recalcula al sincronizar.

### 5.3.5 Sincronización y validación contra RN-TRX-04

**Disparadores.** Como iOS/Safari no ofrece *Background Sync* y los tokens no pueden estar en el Service Worker, la sincronización se inicia **desde la página**: al abrir la app con pendientes, evento `online`, `visibilitychange` a visible, tras cada escaneo en línea exitoso si hay pendientes, cada 30 s con la app visible y en línea, y botón **Sincronizar ahora**.

**Algoritmo:**

1. Adquirir el candado `navigator.locks` `sige-sync` (una sola sincronización a la vez, entre pestañas).
2. Verificar sesión. Si el access venció, renovar (§5.2.5). Si la sesión no se puede recuperar, **conservar los eventos** y pedir iniciar sesión.
3. Medir y guardar el desfase actual (para futuros eventos; **no** se reescriben los ya guardados).
4. Leer los eventos por el índice `by_captured_at`, **de menor a mayor**: el rebote y el primer escaneo dependen del orden (RN-AST-02, RN-AST-03).
5. Enviar en lotes secuenciales de hasta 250 eventos **(Propuesta)** a `POST /attendance/students/sync/`, con `{ client_event_id, qr_token, event_type, captured_at, clock_offset_ms, captured_by }` por evento (el máximo de la API es 1,000).
6. Con cada respuesta, borrar de IndexedDB **solo** los `client_event_id` presentes en `accepted` o `discarded`, en una sola transacción. Los ausentes se reintentan después.
7. Mostrar el resultado al operador (§5.3.6) y actualizar el contador.

**Manejo de fallos:**

| Situación | Qué hace el cliente |
|---|---|
| Red caída, límite de tiempo o `5xx` | Detiene el lote, conserva todo y reintenta con retroceso creciente (5 s, 15 s, 45 s… hasta 5 min) mientras la app esté visible |
| `401` | Renueva una vez; si falla, conserva los eventos y pide iniciar sesión |
| `403` (el operador ya no tiene rol de escaneo) | Detiene, conserva y avisa; otro operador con permiso puede sincronizarlos |
| `400` o `422` del lote completo | Detiene, conserva, muestra `message` y `trace_id` (es un error de integración, no del evento) |
| Respuesta parcial | Borra lo confirmado y conserva el resto |

**Quién decide qué (RN-TRX-04, RN-TRX-05):**

| Aspecto | El cliente | El backend |
|---|---|---|
| **Hora efectiva** | Envía `captured_at` y `clock_offset_ms`; **no la calcula** ni altera `captured_at` | `captured_at` corregida con `clock_offset_ms` (RN-TRX-04, RNF-FIA-04) |
| Hora efectiva futura | Advierte al capturar si el desfase supera 5 min | Rechaza con `EVENT_IN_FUTURE` |
| Antigüedad del evento | Indica la antigüedad del más viejo; avisa si lleva más de 24 h sin sincronizar **(Propuesta)** | Descarta con `EVENT_TOO_OLD` si supera `OFFLINE_MAX_AGE_HOURS` (72 h) |
| Desfase mayor a 5 min | Solo advierte | Marca el evento para revisión |
| Existencia, vigencia y revocación del QR | **No valida** (no tiene datos) | `QR_NOT_RECOGNIZED`, `QR_REVOKED` |
| Estatus del estudiante | **No valida** | `STUDENT_NOT_ACTIVE` |
| Unicidad y rebote | **No valida** | `REGISTRADO`, `EVENTO_ADICIONAL`, `RECLASIFICADO`, `DUPLICADO_IGNORADO` |
| Rol y cuenta del operador | Envía `captured_by` | Verifica rol PRE o PAD y cuenta activa al sincronizar |
| Reintentos seguros | Reenvía el mismo `client_event_id` | Devuelve el resultado previo sin reprocesar |
| `event_type` | Lo guarda en el buffer (RN-MOV-02) y lo envía como campo opcional | Acepta `ESCANEO_ESTUDIANTE`, el único valor de esta versión (PF-05) |

### 5.3.6 Resultados y avisos al operador (US-033)

| Resultado de la API | Mensaje al operador |
|---|---|
| `accepted` · `REGISTRADO` | Registrado |
| `accepted` · `EVENTO_ADICIONAL` | Registrado como evento adicional |
| `accepted` · `RECLASIFICADO` | Corregido: ahora figura como ASISTIÓ o LLEGÓ TARDE |
| `accepted` · `DUPLICADO_IGNORADO` | Duplicado ignorado |
| `discarded` · `QR_REVOKED` | QR revocado: verifique la identidad de la persona manualmente |
| `discarded` · `STUDENT_NOT_ACTIVE` | El estudiante ya no está activo |
| `discarded` · `QR_NOT_RECOGNIZED` | QR no reconocido |
| `discarded` · `EVENT_TOO_OLD` | Evento demasiado antiguo: regístrelo manualmente |
| `discarded` · `EVENT_IN_FUTURE` | La hora del dispositivo estaba adelantada |

La pantalla de resumen muestra totales y, para cada descartado, la **hora local de captura**, el motivo y `rn_reference`. La API no devuelve el nombre del estudiante y el dispositivo no lo conoce, así que el operador identifica el caso por la hora y el motivo.

**Límite conocido (P-F2, decisión vigente de la v1):** el resumen vive en memoria. Si el operador cierra la app antes de leerlo, no queda en el dispositivo (guardarlo exigiría un tercer almacén). Si la institución necesita garantizar que los descartes se vean, hay dos opciones: guardar `client_event_id`, `captured_at` y `error_code` hasta que el operador los confirme, o exponer los acuses (`OFFLINE_EVENT_RECEIPT`) por un endpoint de consulta.

### 5.3.7 Persistencia del almacenamiento

- Al primer inicio de sesión se pide almacenamiento persistente con `navigator.storage.persist()` **(Propuesta)** para reducir el riesgo de purga.
- El contador de pendientes está siempre visible, con la antigüedad del evento más viejo.
- Se indica a los operadores **sincronizar al terminar la jornada** y no dejar la app cerrada con pendientes.
- En iOS, el comportamiento de purga de los sitios instalados frente a los abiertos en Safari **debe verificarse en la matriz de RNF-COM-02** antes de afirmarlo en la guía de operación.

### 5.3.8 Pruebas de aceptación offline

| # | Prueba | Resultado esperado |
|---|---|---|
| 1 | Con la PWA instalada y el dispositivo en modo avión, abrir la app | Llega a `/escaneo` |
| 2 | Escanear sin conexión | Mensaje de captura pendiente, contador +1, sin nombre ni foto |
| 3 | Revisar IndexedDB | El registro tiene **solo** los seis campos del §5.3.4 y `meta` solo el desfase |
| 4 | Capturar el evento 1,001 | Se rechaza con alerta y el buffer sigue en 1,000 (RN-MOV-03) |
| 5 | Recargar la página sin conexión | Los pendientes siguen ahí |
| 6 | Restablecer la conexión | Se sincroniza solo, en orden de `captured_at`, y se borran únicamente los confirmados |
| 7 | Sincronizar un QR revocado después de capturarlo | Descartado con `QR_REVOKED` y avisado con su hora de captura |
| 8 | Reenviar el mismo lote | Mismos resultados, sin duplicados (idempotencia) |
| 9 | Refresh vencido durante la desconexión | Pide iniciar sesión y conserva los eventos (SEG §7) |
| 10 | Dispositivo con reloj adelantado más de 5 min | Advertencia al capturar; el backend marca o rechaza según corresponda |
| 11 | Publicar una versión nueva con pendientes | Aparece el aviso de actualización; los pendientes se conservan; no se actualiza durante una sincronización |
| 12 | Cerrar sesión con pendientes | Advierte y **no borra** el buffer |

---

## 5.4 Sistema de diseño

### 5.4.1 Principios

| # | Principio | Origen |
|---|---|---|
| 1 | **Legible a pleno sol.** Contraste alto en toda la interfaz y contraste AAA en la pantalla de escaneo (zona de puerta) | RNF-USA-01, CT-11 |
| 2 | **Retroalimentación inmediata**, visual y sonora, ante un escaneo válido o inválido | RNF-USA-01, CT-10, CT-11 |
| 3 | **Nunca solo color.** Todo estado lleva icono y texto además de color | CT-14 |
| 4 | **Esquinas tipo squircle** de 12 a 16 px en todo componente interactivo | RNF-USA-01, CT-11 |
| 5 | **Móvil primero para PRE, DOC y escaneo; escritorio primero para administración.** Tabla en escritorio, tarjetas en móvil | HU (UX/UI), CT-14 |
| 6 | **Todo funciona sin recursos externos** (fuentes, iconos e imágenes locales) | RN-INF-01 |
| 7 | **Un solo lenguaje de estados**: cada pantalla con datos define los siete estados de CT-13 | CT-13 |

### 5.4.2 Tokens

Los tokens se definen como variables CSS en `shared/styles/tokens.css` y son la única fuente de valores: ningún componente usa colores, tamaños ni radios escritos a mano.

#### Color

Tema **claro** como único tema de la v1: la prioridad es la luz solar directa (modo oscuro queda fuera de alcance **(Propuesta)**). Los pares de la tabla se calcularon con la fórmula de contraste de WCAG 2.x.

| Uso | Token | Par (texto sobre fondo) | Contraste | Nivel |
|---|---|---|---|---|
| Texto principal | `--color-text` | `#0B1320` sobre `#FFFFFF` | 18.61:1 | AAA |
| Texto secundario | `--color-text-muted` | `#334155` sobre `#FFFFFF` | 10.35:1 | AAA |
| Texto secundario sobre superficie alterna | `--color-text-muted` | `#334155` sobre `#F1F5F9` | 9.45:1 | AAA |
| Enlace y acción primaria (texto) | `--color-primary` | `#0A3D91` sobre `#FFFFFF` | 10.05:1 | AAA |
| Botón primario | `--color-on-primary` | `#FFFFFF` sobre `#0A3D91` | 10.05:1 | AAA |
| Borde de control (campos, casillas) | `--color-border-strong` | `#64748B` sobre `#FFFFFF` | 4.76:1 | AA |
| Éxito, texto sobre fondo suave | `--color-success-text` | `#0B4A22` sobre `#DCF5E3` | 9.03:1 | AAA |
| Éxito, texto blanco sobre sólido | `--color-success-solid` | `#FFFFFF` sobre `#0A5A2A` | 8.37:1 | AAA |
| Advertencia, texto sobre fondo suave | `--color-warning-text` | `#5C3200` sobre `#FFEBC2` | 9.37:1 | AAA |
| Advertencia, texto blanco sobre sólido | `--color-warning-solid` | `#FFFFFF` sobre `#7C4400` | 7.82:1 | AAA |
| Peligro, texto sobre fondo suave | `--color-danger-text` | `#7A0F0F` sobre `#FDE4E4` | 9.14:1 | AAA |
| Peligro, texto blanco sobre sólido | `--color-danger-solid` | `#FFFFFF` sobre `#A31515` | 7.85:1 | AAA |
| Información, texto sobre fondo suave | `--color-info-text` | `#0A3D91` sobre `#DCEBFF` | 8.31:1 | AAA |
| Pendiente de validación, texto sobre fondo suave | `--color-pending-text` | `#3B2A7A` sobre `#E9E4FA` | 9.42:1 | AAA |
| Pendiente de validación, texto blanco sobre sólido | `--color-pending-solid` | `#FFFFFF` sobre `#4B35A0` | 9.07:1 | AAA |
| Neutro (duplicado ignorado), texto sobre fondo | `--color-neutral-text` | `#1F2937` sobre `#E5E9EE` | 12.04:1 | AAA |

Los colores institucionales (si la institución define una marca) sustituyen **solo** `--color-primary` y deben volver a pasar la tabla (P-F6). Un token nuevo no entra al sistema sin su contraste calculado.

```css
:root {
  /* Superficies y texto */
  --color-bg: #FFFFFF;            --color-surface: #FFFFFF;        --color-surface-alt: #F1F5F9;
  --color-border: #CBD5E1;        --color-border-strong: #64748B;
  --color-text: #0B1320;          --color-text-muted: #334155;
  /* Acción */
  --color-primary: #0A3D91;       --color-on-primary: #FFFFFF;     --color-focus: #0A3D91;
  /* Estados: texto/fondo suave y sólido (siempre acompañados de icono y texto) */
  --color-success-text: #0B4A22;  --color-success-bg: #DCF5E3;     --color-success-solid: #0A5A2A;
  --color-warning-text: #5C3200;  --color-warning-bg: #FFEBC2;     --color-warning-solid: #7C4400;
  --color-danger-text:  #7A0F0F;  --color-danger-bg:  #FDE4E4;     --color-danger-solid:  #A31515;
  --color-info-text:    #0A3D91;  --color-info-bg:    #DCEBFF;
  --color-pending-text: #3B2A7A;  --color-pending-bg: #E9E4FA;     --color-pending-solid: #4B35A0;
  --color-neutral-text: #1F2937;  --color-neutral-bg: #E5E9EE;
  /* Forma */
  --radius-control: 12px;         --radius-card: 16px;             --radius-sheet: 16px;
  /* Espacio (escala de 4 px) */
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-6: 24px; --space-8: 32px; --space-12: 48px; --space-16: 64px;
  /* Tamaño mínimo de objetivo táctil */
  --target-min: 44px;             --target-scan: 48px;
  /* Movimiento */
  --motion-fast: 120ms;           --motion-base: 200ms;
}
@media (prefers-reduced-motion: reduce) { :root { --motion-fast: 0ms; --motion-base: 0ms; } }
```

#### Tipografía

| Aspecto | Especificación |
|---|---|
| Familia | **Inter** variable, **alojada en el propio servidor** (`next/font/local`) **(Propuesta)**; respaldo `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`. Nunca una fuente remota |
| Escala | `--text-sm` 14 px · `--text-base` 16 px · `--text-lg` 18 px · `--text-xl` 20 px · `--text-2xl` 24 px · `--text-3xl` 32 px · `--text-display` 48 px (solo resultado de escaneo) |
| Cuerpo y campos | Mínimo 16 px (evita el acercamiento automático de iOS en los campos) |
| Pesos | 400 cuerpo, 500 etiquetas, 600 encabezados, 700 estados de escaneo |
| Cifras | `font-variant-numeric: tabular-nums` en matrículas, horas, conteos y tablas |
| Interlineado | 1.5 en cuerpo y 1.2 en encabezados y estados de escaneo |

#### Forma, espacio y elevación

- **Radio:** solo `--radius-control` (12 px: botones, campos, chips) y `--radius-card` / `--radius-sheet` (16 px: tarjetas, paneles, hojas inferiores). Sin pastillas ni radios fuera de 12 a 16 px en elementos interactivos.
- **Elevación:** se separa con bordes y fondos (`--color-border`, `--color-surface-alt`), **no con sombras**, que se pierden bajo el sol.
- **Objetivos táctiles:** mínimo 44 px; **48 px** en la pantalla de escaneo y en sus botones primarios **(Propuesta)**.
- **Foco visible:** `outline: 3px solid var(--color-focus); outline-offset: 2px` en todo elemento interactivo.

### 5.4.3 Especificación squircle (RNF-USA-01, CT-11)

RNF-USA-01 exige curvaturas tipo "squircle" con `border-radius` de 12 a 16 px. La especificación es en dos niveles, de modo que el requisito se cumple siempre y la forma mejora donde el navegador lo permite:

```css
/* Nivel 1: cumple RNF-USA-01 en cualquier navegador */
.squircle-control { border-radius: var(--radius-control); }   /* 12 px */
.squircle-card    { border-radius: var(--radius-card); }      /* 16 px */

/* Nivel 2: mejora progresiva con la curva superelíptica real */
@supports (corner-shape: squircle) {
  .squircle-control, .squircle-card { corner-shape: squircle; }
}
```

- El **nivel 1 es el que se acepta**: el valor numérico de `border-radius` es lo que dice el requisito.
- `corner-shape` es una propiedad CSS reciente: **su soporte debe comprobarse en los dispositivos de la matriz de RNF-COM-02** (P-F9). Si no existe en alguno, ese dispositivo queda con el nivel 1 sin otra consecuencia.
- **Prueba automática:** una prueba de componentes recorre los elementos interactivos y falla si el `border-radius` calculado queda fuera de 12 a 16 px.
- **Excepciones:** avatares e iconos circulares no interactivos.

### 5.4.4 Retroalimentación de escaneo

La confirmación de un QR debe resolverse en menos de 250 ms (RNF-DES-01, CT-10), así que el panel de resultado **aparece en cuanto llega la respuesta**, sin animaciones de entrada, y la cámara sigue activa para el siguiente escaneo.

| Resultado | Fondo | Icono y texto | Sonido | Vibración | Permanencia |
|---|---|---|---|---|---|
| `ASISTIO` (`REGISTRADO`) | `--color-success-solid` | Palomita · **ASISTIÓ** | Un tono agudo corto (880 Hz, 120 ms) | 60 ms | 2 s |
| `LLEGO_TARDE` (`REGISTRADO`) | `--color-warning-solid` | Reloj · **LLEGÓ TARDE** | Dos tonos medios (660 Hz, 100 ms cada uno) | 60 ms ×2 | 2 s |
| `RECLASIFICADO` | Según el nuevo estado | Mismo icono · **CORREGIDO: ASISTIÓ** o **CORREGIDO: LLEGÓ TARDE** | El del nuevo estado | 60 ms | 2 s |
| `EVENTO_ADICIONAL` o `DUPLICADO_IGNORADO` | `--color-neutral-bg` con texto `--color-neutral-text` | Dos palomitas · **YA REGISTRADO** | Un tono grave suave (440 Hz, 80 ms) | Ninguna | 1.5 s |
| Capturado sin conexión | `--color-pending-solid` | Reloj de arena · **PENDIENTE DE VALIDACIÓN** | Un tono medio (520 Hz, 150 ms) | 60 ms | 2 s |
| `QR_NOT_RECOGNIZED` | `--color-danger-solid` | X · **QR NO RECONOCIDO** | Dos tonos descendentes (300 y 200 Hz) | 200 ms | 3 s |
| `STUDENT_NOT_ACTIVE` | `--color-danger-solid` | X · **ESTUDIANTE NO ACTIVO** | Dos tonos descendentes | 200 ms | 3 s |
| `QR_REVOKED` | `--color-danger-solid` | Alerta · **QR REVOCADO: VERIFIQUE LA IDENTIDAD** | Tres tonos graves (250 Hz, 150 ms cada uno) | 300 ms | **Hasta que el operador lo confirme** |
| Buffer lleno (RN-MOV-03) | `--color-danger-solid` | Alerta · **BUFFER LLENO: ESPERE CONEXIÓN** | Tres tonos graves | 300 ms | **Hasta que el operador lo confirme** |

- **Contenido del panel (en línea):** `display_name`, grupo y fotografía que devuelve la API, para la verificación visual de quien escanea. Texto de estado en `--text-display`.
- **Sonido:** generado con la Web Audio API (sin archivos de audio). En iOS el contexto de audio solo se activa tras un gesto del usuario, así que se activa con el botón **Iniciar escaneo**. Un interruptor de silencio por dispositivo, activado por defecto.
- **Vibración:** donde el navegador la ofrezca; no se depende de ella.
- **Cada estado se distingue sin el color**: icono, texto y patrón de sonido diferentes (CT-14).
- **Valores de frecuencia, duración y permanencia: (Propuesta)**, a ajustar en la validación de usabilidad del Hito 06 (RNF-USA-01, KPI-37).

### 5.4.5 Componentes base

| Componente | Descripción | Estados que debe cubrir |
|---|---|---|
| `Boton` | Primario, secundario, peligro y texto; con icono opcional | Normal, foco, deshabilitado, cargando |
| `Campo`, `Selector`, `AreaTexto` | Etiqueta siempre visible, ayuda y error asociados con `aria-describedby` | Normal, foco, error, deshabilitado |
| `TablaResponsiva` | Tabla desde 768 px; **tarjetas** por debajo; paginación `page` y `page_size` | Los siete de §5.4.6 |
| `InsigniaEstado` | Estado de asistencia, de reporte o de envío con icono y texto | Ver catálogo abajo |
| `PanelResultadoEscaneo` | Resultado de §5.4.4 | Todos los de la tabla |
| `BannerSincronizacion` | "Sin conexión — N eventos pendientes" y progreso de sincronización | Sin conexión, sincronizando, error, al día |
| `BannerActualizacion` | Aviso de versión nueva del Service Worker | Visible, aplicando |
| `ConfirmarConMotivo` | Diálogo con motivo obligatorio (recortado y no vacío) para desactivar, reactivar, justificar, revocar QR y modificar asistencia | Abierto, validando, enviando, error |
| `ConfirmarAfectacion` | Diálogo "Este cambio afectará a N estudiantes" (`CONFIRMATION_REQUIRED`) | Abierto, enviando |
| `EstadoPantalla` | Contenedor que pinta cargando, vacío, error, permiso denegado o sin conexión según el estado de la consulta | Los siete |
| `Aviso` | Mensaje de éxito, información o error, no bloqueante | Éxito, error, información |
| `Dialogo` y `HojaInferior` | Modal centrado (escritorio) y hoja inferior (móvil), con foco atrapado | Abierto, cerrando |

**Catálogo de insignias** (siempre icono + texto + color):

| Estado | Texto | Familia | Icono |
|---|---|---|---|
| `ASISTIO` | ASISTIÓ | Éxito | Palomita |
| `LLEGO_TARDE` | LLEGÓ TARDE | Advertencia | Reloj |
| `FALTO` | FALTÓ | Peligro | X |
| `FALTA_JUSTIFICADA` | FALTA JUSTIFICADA | Información | Documento |
| Evento sin sincronizar | PENDIENTE DE VALIDACIÓN | Pendiente | Reloj de arena |
| Envío `PENDIENTE` | PENDIENTE | Pendiente | Reloj de arena |
| Envío `ENVIADO` | ENVIADO (nunca "leído", US-053) | Éxito | Sobre con palomita |
| Envío `FALLIDO` | FALLIDO | Peligro | Sobre con X |
| Reporte `REGISTRADO`, `REVISADO_PREFECTO`, `CANALIZADO`, `REVISADO_ADMINISTRATIVO` | Su etapa | Información | Flecha de etapa |
| Reporte `AUTORIZADO` | AUTORIZADO, PENDIENTE DE CONTACTO | Advertencia | Candado abierto |
| Reporte `COMUNICADO` o `RESUELTO` | Su etapa | Éxito | Palomita |
| Reporte `RECHAZADO` | RECHAZADO | Peligro | X |

### 5.4.6 Estados de interfaz (CT-13)

Toda pantalla con datos define **siete estados**: cargando, contenido, vacío, error con reintento, éxito, permiso denegado y, en móvil, sin conexión. `EstadoPantalla` los resuelve de forma uniforme.

| Estado | Cuándo aparece | Qué muestra | Acción | Accesibilidad |
|---|---|---|---|---|
| **Cargando** | La consulta está en curso (si tarda más de unos 150 ms **(Propuesta)**) | Esqueleto con la forma del contenido (filas o tarjetas); los botones muestran indicador de progreso y se deshabilitan | Ninguna | `aria-busy="true"` en la región |
| **Contenido** | Hay datos | La pantalla normal | Las de la pantalla | Tabla o lista con encabezados; orden por `sort_name` |
| **Vacío** | La consulta no devolvió resultados | Mensaje que explica **por qué**: "No hay resultados con estos filtros", "Aún no hay registros" o "Sin registros: día no lectivo" | Limpiar filtros o la acción principal de la pantalla | Mensaje en texto, no solo ilustración |
| **Error con reintento** | Error de red, `5xx` o `422` no asociable a un campo | `message` de la API, el `trace_id` copiable y botón **Reintentar** (CA-001-07) | Reintentar | `role="alert"` |
| **Éxito** | La operación terminó bien | Aviso breve (4 s) o confirmación persistente en operaciones largas (p. ej. importación) | Ver resultado, deshacer no aplica | `role="status"` |
| **Permiso denegado** | `403`, o ruta fuera del rol | "No tienes permiso para ver esta pantalla", sin detalles de lo que contiene | Volver al inicio | Foco al encabezado |
| **Sin conexión** (móvil) | Se perdió la conexión con el servidor local | Banner persistente "Sin conexión". Las acciones de escritura se deshabilitan con la explicación; **solo el escaneo sigue operando** en modo sin conexión (§5.3.4) | Reintentar al volver | `role="status"` |

Casos particulares:

- **Formularios.** Los errores `422` con `details` se pintan junto a cada campo; al enviar, un resumen enfoca el primer error. Un `422` sin campo va al estado **Error**.
- **404 de un recurso fuera de alcance** (p. ej. un reporte ajeno): se trata como "No encontrado", **sin** insinuar que exista (RN-REP-05).
- **`429`:** muestra la cuenta regresiva a partir de `Retry-After` y deshabilita el botón hasta que termine.
- **Inicio de sesión:** además, mensaje genérico que no revela qué dato falló, cuenta bloqueada con tiempo restante, cuenta desactivada y servidor no disponible (HU-001).

### 5.4.7 Responsive y accesibilidad (CT-14)

| Aspecto | Especificación |
|---|---|
| Puntos de corte | 360 px (base móvil), 768 px (tableta), 1024 px (escritorio). Tabla desde 768 px; tarjetas por debajo (HU) |
| Teclado | Todo es operable con teclado; orden de foco lógico; los diálogos atrapan el foco y lo devuelven al cerrar |
| Foco | Siempre visible (§5.4.2) |
| Etiquetas | Toda entrada tiene `label` visible; los iconos sin texto llevan `aria-label` |
| Errores | Mensajes comprensibles, asociados al campo y anunciados |
| Color | Nunca es el único portador de información (§5.4.1, principio 3) |
| Movimiento | Respeta `prefers-reduced-motion`; los estados de escaneo no usan animación |
| Idioma | `lang="es-MX"` en el documento; textos en español claro, sin tecnicismos para el personal operativo (RNF-USA-02) |
| Iconos | Conjunto empaquetado localmente (p. ej. `lucide-react`) **(Propuesta)**; sin CDN |

---

## 6. Decisiones propuestas y pendientes

Todo lo marcado **(Propuesta)** en el documento está aquí y quedó **aprobado**, junto con los huecos que aparecieron en los documentos fuente. Aprobar una propuesta no la cierra: la columna *Estado y parche* indica el parche que la implementa o la tarea que sigue pendiente. Los parches están en `SIGE_Parches3_Implementacion_Frontend_v1.md`.

| # | Tema y qué hace falta | Quién | Estado y parche |
|---|---|---|---|
| **P-F1** | **El refresh no devuelve el `user`** y no existe `GET /users/me/`. Tras recargar la página la app tiene un access token **sin rol ni nombre** (el JWT no lleva el rol, SEG §1) y no puede armar el menú. **Propuesta:** que `POST /auth/refresh/` devuelva el mismo objeto `user` que el login, leído de la base en ese momento. Parche en el §7 | Backend | Aprobada. Parche PF-01 |
| **P-F2** | El resumen de descartes de la sincronización vive solo en memoria (§5.3.6). Decidir si basta, si se guarda localmente hasta confirmarse o si se agrega un endpoint de acuses | Institución y desarrollo | Vigente en la v1: el resumen vive en memoria. Sin parche |
| **P-F3** | **Signo de `clock_offset_ms`.** Los documentos no lo fijan. Se propone `servidor − dispositivo` y hora efectiva `captured_at + clock_offset_ms`. Confirmar y documentar en la API (parche en el §7) | Backend | Aprobada. Parche PF-02 (falta confirmar el signo con backend al implementar) |
| **P-F4** | **Prueba técnica de navegación sin red** con el App Router (§5.2.2). Si falla, exportar el frontend como sitio estático | Desarrollo, antes del Hito 04 | Aprobada. Tarea previa al Hito 04; criterio en PF-07 (CA-032-08) |
| **P-F5** | `event_type` está en RN-MOV-02 y SEG §7 pero **no en el contrato de `sync`**. Hoy hay una sola clase de evento, así que no se envía. Confirmar si la API lo aceptará (opcional) y mantener el buffer en seis campos | Backend | Aprobada. Parches PF-05 y PF-06 |
| **P-F6** | Versiones de Next.js, React y librerías; color de marca institucional, si existe; fuente definitiva. Fijarlas al iniciar el Hito 04 | Desarrollo e institución | Aprobada. Tarea al iniciar el Hito 04. Sin parche |
| **P-F7** | **Matriz de dispositivos y navegadores soportados** (RNF-COM-02, "antes del Hito 04"): incluye instalación de la CA interna, soporte de Web Locks, cámara y comportamiento de purga en iOS | Equipo y institución | Aprobada. Parche PF-10; la matriz se completa antes del Hito 04 |
| **P-F8** | Valores de tiempo: límite de 3 s para el escaneo, ciclo de 15 s del estado del servidor, antirrebote técnico de 1.5 s, lote de 250. Ajustarlos en el piloto (Hito 06) | Desarrollo | Aprobada. Se ajustan en el piloto (Hito 06). Sin parche |
| **P-F9** | Soporte real de `corner-shape: squircle` en los dispositivos de la matriz | Desarrollo | Aprobada. Se verifica en la matriz de dispositivos. Sin parche |
| **P-F10** | Librería de decodificación de QR cuando no exista `BarcodeDetector` | Desarrollo | Aprobada. Se elige en el Hito 04. Sin parche |
| **P-F11** | Marcar ADR-01 como **Aceptada** en la Arquitectura C4 (parche en el §7) y retirar las referencias al Acta v9 en cualquier documento que aún las tenga | Documentación | Aprobada. Parches PF-04 y PF-12 |

---

## 7. Parches derivados a otros documentos

Los parches que implementan las propuestas aprobadas (PF-01 a PF-13) se consolidaron en `SIGE_Parches3_Implementacion_Frontend_v1.md`. Allí están, en un solo lugar, los de la API, Seguridad, Arquitectura C4, Reglas de Negocio, Requisitos, Criterios de Aceptación, Historias de Usuario, el Modelo de Datos y los Diagramas de Secuencia.

---

*Fin del documento.*
