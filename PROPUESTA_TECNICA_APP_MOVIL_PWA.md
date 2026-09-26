# Dictamen Técnico y Propuesta de Arquitectura: Implementación de la Aplicación Móvil (SIGE)

**Para**: Miguel (@migolitofirmaditocmd) & Equipo de Desarrollo SIGE  
**De**: Ibrahim García (@ultimaibrahim)  
**Proyecto**: Sistema Integral de Gestión Escolar (Secundaria Mixta 5)  
**Referencia Normativa**: Acta Constitutiva v8 (OE-11, Sección 6.10, Hito 04, Sección 8 y Sección 13.7)  
**Fecha**: Septiembre 2026 | **Estado**: Para Revisión y Aprobación Técnica Conjunta

---

## 📌 1. Situación Actual: ¿Qué dice exactamente el Acta v8?

Al auditar la **Versión 8 del Acta Constitutiva**, encontramos un punto clave de arquitectura:

1. **Ambigüedad en el Stack Móvil**:
   - En la tabla de **Restricción Tecnológica (Sección 8)**, el acta únicamente aprueba:
     - **Lenguajes**: TypeScript, Python.
     - **Frameworks**: Next.js (Frontend) y Django (Backend/API).
     - **Base de Datos**: PostgreSQL.
   - En ninguna parte del documento se menciona **Android Studio, Kotlin, Java, Flutter ni SDKs nativos**.
2. **Definición Funcional, no Tecnológica**:
   - El objetivo **OE-11**, la **Sección 6.10** y el **Hito 04** definen lo que la aplicación debe **hacer** (autenticar docentes/prefectos, escanear QR con la cámara, registrar asistencia, canalizar reportes y comunicarse con el servidor local vía Wi-Fi escolar), pero **no imponen con qué herramienta móvil compilarla**.
   - En la **Sección 15** se establece que las decisiones técnicas de implementación deben definirse formalmente en la etapa de arquitectura.

---

## ⚖️ 2. Análisis Comparativo: Android Studio vs. PWA con Service Worker

Considerando que el proyecto está limitado a **480 horas totales (2 personas × 10 h/semana × 24 semanas)** y que el servidor correrá físicamente en una **computadora dentro de la secundaria (red local LAN sin Internet obligatorio)**:

| Criterio de Evaluación | Enfoque A: Android Studio Nativo (Kotlin) | Enfoque B: PWA con Service Worker (Next.js) ⭐ |
| :--- | :--- | :--- |
| **Bases de Código (Codebases)** | **2 proyectos separados**: Uno en Next.js (web) y otro en Android Studio (móvil). | **1 solo proyecto unificado**: El mismo frontend Next.js en TypeScript adapta su interfaz a móvil. |
| **Tiempo Estimado de Desarrollo** | **~180 a 220 horas** (Configuración de Gradle, layouts XML/Compose, librerías de cámara nativa, networking Retrofit). | **~50 a 70 horas** (Reutiliza el 100% de la lógica de API, componentes visuales y tipados). |
| **Compatibilidad de Dispositivos** | **Solo Android**. Si un maestro o prefecto usa iPhone (iOS), queda 100% excluido del sistema. | **Universal (Android + iOS)**. Cualquier dispositivo con navegador moderno accede al instante. |
| **Distribución e Instalación** | **Muy compleja**: Al no haber Google Play Store escolar, habría que pasar APKs por USB/WhatsApp y activar "orígenes desconocidos" en cada celular. | **Cero fricción**: El docente se conecta al Wi-Fi de la escuela, abre la IP local y pulsa *"Instalar en pantalla de inicio"*. |
| **Operación Offline / Wi-Fi Inestable** | Requiere SQLite local y lógica manual de sincronización en Kotlin. | El **Service Worker** cachea la interfaz y usa **IndexedDB** para guardar registros si la red parpadea. |
| **Acceso a la Cámara (Escaneo QR)** | API nativa `CameraX` (alta complejidad de ciclo de vida). | API nativa web `BarcodeDetector` / `html5-qrcode` con aceleración de hardware en <100 ms. |
| **Riesgo de Capacidad (R-16 del Acta)** | **CRÍTICO**. Alto riesgo de exceder las 480 horas del servicio social. | **CONTROLADO**. Garantiza cumplir el Hito 04 sin comprometer la entrega final. |

---

## 🚀 3. Propuesta Técnica Recomendada

Se propone formalizar la adopción de una **Progressive Web App (PWA) de Alto Rendimiento**:

1. **Stack Móvil Unificado**:
   - Desarrollada dentro del mismo frontend Next.js (TypeScript) aprovechando el diseño móvil ergonómico (Thumb Zone).
   - Manifiesto web (`manifest.json`) que permite instalarse con ícono propio, pantalla completa y sin barra de direcciones del navegador.
2. **Capacidades Operativas**:
   - **Escaneo QR**: Acceso directo a la cámara trasera mediante APIs web modernas con detección en tiempo real.
   - **Service Worker**: Caché de la aplicación para que cargue al instante y almacene temporalmente asistencias si el Wi-Fi escolar tiene micro-cortes.
   - **Cero Costos**: No requiere cuentas de desarrollador de Google ($25 USD) ni Apple ($99 USD/año).
3. **Mecanismo de Respaldo (Capacitor / APK)**:
   - Si la dirección de la Secundaria Mixta 5 solicita obligatoriamente *"un archivo .apk entregable"*, la PWA puede empaquetarse con **Capacitor** (`@capacitor/android`) en un solo paso para generar el archivo `.apk` instalable sin necesidad de reescribir una sola línea de código.

---

## ✅ 4. Acuerdo y Próximos Pasos

Para dejar este acuerdo formalmente asentado en la documentación del proyecto:

- [ ] **Aprobación de Miguel**: Confirmar conformidad con el enfoque PWA (Next.js + Service Worker).
- [ ] **Actualización de Documentación**: Incorporar esta definición en `docs/01_ESPECIFICACION_DE_REQUISITOS_Y_FLUJOS.md` y en la arquitectura técnica.
- [ ] **Alineación del Hito 04 en GitHub Projects**: Registrar que el Hito 04 validará la PWA instalable en dispositivos de prueba.

---
*Este documento queda registrado en el repositorio del proyecto como evidencia de decisión arquitectónica fundamentada.*
