---
name: ibrahim-agent-core
description: Sistema maestro de experiencia, reglas de arquitectura, estilo gráfico Crystal & Squircle y protocolo de commits para Ibrahim García.
---

# Ibrahim Agent Core · Sistema de Onboarding y Reglas Universales

Este skill define la **memoria colectiva y estándares universales de trabajo** para Ibrahim García en cualquier computadora, entorno o proyecto de La Crêpe Parisienne / Grupo MYT.

## 📌 Principios de Trabajo Inamovibles

1. **Protocolo Estricto de Commits y Git**:
   - Parches iterativos locales llevan sufijos de letras (`x.x.1a`, `x.x.1b`).
   - **Queda estrictamente prohibido hacer `git commit` o `git push` a GitHub** sin confirmación explícita previa de Ibrahim.

2. **Diseño Visual y Separación Estricta de Paletas**:
   - **Proyectos de Cliente / La Crêpe Parisienne (LCP) / Grupo MYT**: Paleta corporativa verde (`#3D5A47`), acento sage (`#7A9E8A`) y superficies limpias (`#F5EFE6`).
   - **Marca Personal de Ibrahim (Atelier / Personal)**: Morado profundo/fondo (`#1F0D3D`, `#090314`), superficie (`#2F2B3F`), acentos lavanda (`#C084FC`, `#D8B4FE`), texto claro (`#F2F0F8`). Tipografías: Geist / Geist Mono. **Jamás mezclar ambas identidades**.
   - **Entregas Académicas e Institucionales (UdeG / CUGDL / LIACD)**: Identidad formal institucional. Estudiante: `Saul Ibrahim Garcia Ochoa`, Código: `224164463`, Carrera: `LIACD`, Sede: `CUGDL`. Estructura sobria con escudo UdeG y formato editorial de alta jerarquía técnica.
   - **Regla General UI**: Curvas squircle (`border-radius: 10px-14px`), eliminar controles toscos nativos (`appearance: none`).

3. **Compatibilidad Apps Script & Google Sheets**:
   - Fórmulas inyectadas en celdas mediante `.setFormula()` siempre escritas en **Inglés** y con parámetros separados por **comas (`,`)**.
   - Ejecución obligatoria de script de validación sintáctica (0 errores) antes de dar por terminado cualquier cambio `.gs`.

4. **Preservación de Hojas y Columna `_SYNC`**:
   - El rango de importación `IMPORTRANGE` debe usar estrictamente **`A4:L`** (12 columnas) para evitar romper o recortar la columna L de picking.

5. **Experiencia de Usuario en Modales**:
   - Diálogos HTML desacoplados con dimensiones amplias (`1050x700px`).
   - Salto directo tipeando el número de posición.
   - Guardado automático de preferencias de densidad/zoom en `localStorage`.
   - Intercepción de cierre por `X` con diálogo de confirmación si hay modificaciones sin guardar.

6. **Preservación Inamovible de Changelogs Históricos**

7. **Filosofía Mobile-First y Restricciones de la App Móvil Nativa**:
   - Las herramientas operativas de punto de venta/tienda son 90%+ móviles.
   - La app nativa de Google Sheets en iOS/Android **ignora menus personalizados (`createMenu`), toasts (`toast()`) y modales (`showModalDialog`)**.
   - Toda interacción debe dispararse mediante checkboxes en celdas físicas de la hoja de cálculo o ejecutarse de forma silenciosa y autoreparable en segundo plano.

8. **Doble Versionado Obligatorio (Técnico vs. Público/User-Friendly)**:
   - Al registrar cualquier incremento de versión o cambio, es **OBLIGATORIO actualizar siempre dos changelogs paralelos**:
     - **Changelog Técnico Tradicional** (`CHANGELOG.md` / `about.js` / `historial_versiones.md`): Con jerga técnica completa, arquitectura y funciones.
     - **Changelog Público / Operativo** (`CHANGELOG_PUBLIC.md` / Trello Cards): En formato **Beneficio Operativo (User-Friendly)** sin jerga de desarrollo, enfocado en el impacto directo a tiendas, experiencia del usuario y gerencias regionales.

9. **Consulta Obligatoria de Especificación Técnica & Arquitectura Viva (Living Architecture)**:
   - Toda suite con documentación profunda (como `documentacion/especificacion_sistema_completo.md` en MISE) **DEBE ser consultada al menos una vez al iniciar la sesión o antes de tocar código**.
   - **Mantenimiento Mandatorio Bidireccional:** Conforme el código evoluciona, se agregan funciones o se aprueban cambios, es mandatorio actualizar la especificación técnica en el mismo ciclo. Código y especificación nunca deben desfasarse.

## 🔄 Sincronización Automática de Reglas Globales

Si este entorno no cuenta con la carpeta `C:\Users\ibrag\.gemini\config\rules\`, el agente ejecutará silenciosamente la restauración de reglas desde la memoria del skill.
