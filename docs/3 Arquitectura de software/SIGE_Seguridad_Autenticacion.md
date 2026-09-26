# SIGE — Documento de Seguridad y Autenticación
**Sistema Integral de Gestión Escolar**

Este documento detalla los mecanismos de seguridad, políticas de control de acceso y estrategias de autenticación implementadas en SIGE para garantizar la confidencialidad, integridad y disponibilidad de la información de la comunidad escolar.

---

## 1. Estrategia de Autenticación: JWT (JSON Web Tokens)
El sistema utiliza autenticación sin estado (stateless) mediante JWT para todas las comunicaciones entre el Frontend (PWA) y el Backend (Django API).

*   **Access Token (Vida Corta):** Tiene un tiempo de expiración de **15 minutos**. Se utiliza en el header `Authorization: Bearer <token>` de cada petición HTTP. Minimiza la ventana de exposición en caso de robo del token en dispositivos compartidos de la escuela.
*   **Refresh Token (Vida Media):** Tiene un tiempo de expiración de **24 horas** a nivel aplicación, y de **7 días** máximo con actividad constante. Se guarda bajo el mecanismo HTTP-Only Cookie (recomendado) o almacenamiento cifrado de la PWA. Solo se usa contra el endpoint `/api/v1/auth/refresh/` para obtener un nuevo Access Token.

---

## 2. Política de Bloqueo de Seguridad (RN-AUT-03)
Para prevenir ataques de fuerza bruta (brute-force) sobre las cuentas del personal, SIGE implementa una política estricta sobre la tabla `USER`:

1.  **Umbral de Bloqueo:** Tras un número de intentos fallidos consecutivos determinado por `OPERATIONAL_PARAMETER['ACCOUNT_LOCKOUT_MAX_ATTEMPTS']` (por defecto 5 intentos).
2.  **Mecanismo:** El campo `failed_login_attempts` se incrementa. Al llegar a 5, se estampa la fecha actual más el tiempo de castigo en el campo `locked_until`.
3.  **Tiempo de Bloqueo:** Controlado dinámicamente por `OPERATIONAL_PARAMETER['ACCOUNT_LOCKOUT_DURATION_MINUTES']` (por defecto 15 minutos).
4.  **Desbloqueo:** Se realiza automáticamente cuando expira la fecha de `locked_until` o de forma manual si un usuario `Administrador` limpia el campo.

---

## 3. Matriz RBAC Completa (RN-AUT-06)
El Control de Acceso Basado en Roles (RBAC) dicta qué operaciones pueden realizar los distintos tipos de `USER` sobre los módulos de SIGE.

| Módulo / Capacidad | Administrador | Prefecto | Docente | P. Administrativo | Solo Lectura |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **AUT:** Resetear claves / Desbloquear | ✅ | ❌ | ❌ | ❌ | ❌ |
| **ADM:** Cambiar Parámetros y Catálogos | ✅ | ❌ | ❌ | ❌ | ❌ |
| **ADM:** Consultar bitácora de auditoría / respaldos | ✅ | ❌ | ❌ | ❌ | ❌ |
| **EST:** Alta/Edición de Estudiantes | ✅ | ❌ | ❌ | ✅ | ❌ |
| **EST:** Consultar expediente (datos generales) | ✅ | ✅ | ❌ | ✅ | ❌ |
| **EST:** Ver datos de salud (tipo de sangre, alergias) | ✅ | ✅ | ❌ | ✅ | ❌ |
| **EST:** Ver adeudo de pago / materias pendientes | ✅ | ❌ | ❌ | ✅ | ❌ |
| **AST:** Escanear asistencia estudiantil | ❌ | ✅ | ❌ | ✅ | ❌ |
| **AST:** Justificar/modificar asistencia estudiantil | ✅ | ❌ | ❌ | ✅ | ❌ |
| **AST:** Alta y programación de docentes | ✅ | ❌ | ❌ | ✅ | ❌ |
| **AST:** Registrar entrada/salida de docente | ❌ | ❌ | ❌ | ✅ | ❌ |
| **AST:** Reactivar docente / vincular con cuenta | ✅ | ❌ | ❌ | ❌ | ❌ |
| **REP:** Registrar un reporte nuevo | ❌ | ❌ | ✅ (solo sus grupos asignados) | ❌ | ❌ |
| **REP:** Consultar reportes | ✅ (todos) | ✅ (sus grupos asignados) | ✅ (solo los que él registró) | ✅ (todos) | ❌ |
| **REP:** Revisar / canalizar (etapa Prefecto) | ❌ | ✅ | ❌ | ❌ | ❌ |
| **REP:** Revisar / autorizar comunicación a familia (etapa administrativa) | ❌ | ❌ | ❌ | ✅ | ❌ |
| **COM:** Reintentar envío de correo | ✅ | ❌ | ❌ | ✅ | ❌ |
| **IMP:** Carga Masiva de Alumnos | ✅ | ❌ | ❌ | ✅ | ❌ |
| **QR:** Emitir QR (alta inicial, estudiante o docente) | ✅ | ❌ | ❌ | ✅ | ❌ |
| **QR:** Revocar y regenerar QR | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Información consolidada / indicadores** | ✅ | ❌ | ❌ | ✅ | ✅ |
---

## 4. Checklist OWASP ASVS (Aplicado)
A continuación se detalla la aplicación de controles del Application Security Verification Standard (ASVS) Nivel 1 y 2 en los endpoints sensibles de SIGE.

### 4.1 Endpoints de Autenticación (`/auth/*`)
- [x] **V2.1.1 (Claves Seguras):** Verificación de que las contraseñas almacenadas usen algoritmos fuertes y *salt* (Django PBKDF2/Argon2).
- [x] **V2.2.1 (Anti-Enumeración):** Mensajes genéricos de fallo. ("Usuario o contraseña incorrectos", en lugar de "El usuario no existe").
- [x] **V2.3.1 (Bloqueo):** Implementación de limitación de tasa (Rate Limiting) y bloqueo temporal tras fallos reiterados (RN-AUT-03).

### 4.2 Endpoints de Asistencia Estudiantil (`/attendance/students/*`)
- [x] **V5.1.4 (Autorización a nivel de registro):** Validación (Insecure Direct Object Reference - IDOR). Un usuario no puede alterar asistencia si no tiene los roles RBAC requeridos.
- [x] **V11.1.5 (Lógica de Negocio):** Validación estricta en backend contra manipulaciones temporales desde el frontend offline (sincronización y validación del `effective_datetime` vs `scan_datetime`).

### 4.3 Endpoints de Reportes y Comunicaciones (`/reports/*` y `/communications/*`)
- [x] **V5.1.2 (Validación RBAC Explicita):** Un Docente solo puede levantar reportes para estudiantes en los grupos que tiene asignados explícitamente (`TEACHER_GROUP_ASSIGNMENT`).
- [x] **V5.3.3 (Principio de Menor Privilegio):** La consulta de reportes bloquea la visibilidad a actores externos no autorizados.

### 4.4 Endpoints de Estudiantes (`/students/*`)
- [x] **V4.1.3 (Fugas de Información):** Eliminación por diseño de has_payment_debt y pending_subjects cuando el solicitante es Prefecto; eliminación de blood_type, allergies, has_payment_debt y pending_subjects cuando el solicitante es Docente o cualquier otro rol sin acceso al expediente (RN-EST-12).

### 4.5 Endpoints de Credenciales QR (`/credentials/tokens/*`)
- [x] **V6.2.1 (Criptografía Básica):** Los tokens generados son UUIDv4 puros (aleatoriedad criptográficamente segura, no secuencial).
- [x] **V3.1.1 (Protección Replay):** El uso de validaciones de vigencia estricta, invalidando instantáneamente el código anterior al generarse un reemplazo para evitar tokens clonados (RN-QR-01).
