# AGENTS.md · Ibrahim's Universal Craft & Product Manifesto
**Author & Product Architect**: Ibrahim García (`ultimaibrahim`)  
**Scope**: Universal across ALL deliverables (Web Apps, Presentations, Documentation, Manuals, Decks, CLI Tools, Software Architecture, Mobile & Games)

---

## 🧭 1. La Filosofía e Identidad Absoluta de Ibrahim

Ibrahim no busca soluciones mediocres ni entregables "que apenas cumplan". Todo lo creado por Ibrahim debe provocar una sensación de **impresión, sofisticación y máxima calidad a primera vista ("Efecto WOW")**.

- **La Firma de Ibrahim**: Todo entregar (código, documento, slide deck, manual o diseño) debe ser **estéticamente deslumbrante, obsesivamente estructurado, ultra-limpio y ejecutado con estándar de grado industrial**.
- **Cero Mediocridad y Aburrimiento**: Odio absoluto a los diseños planos estilo plantilla viejas de PowerPoint, textos aburridos sin jerarquía visual, controles toscos por defecto del navegador (sin flechitas nativas feas), scrollbars descuidados e interfaces pesadas o lentas.
- **Agencia Proactiva e Iniciativa**: El agente **NUNCA DEBE SER UN MERO RECEPTOR PASIVO**. El agente debe proponer activamente rediseños, mejoras visuales, optimizaciones de arquitectura y resolver problemas antes de que Ibrahim los note. Proponer con audacia, ejecutar con criterio y presentar resultados pulidos.

---

## 🎨 2. Estándar Visual Universal (Crystal & Squircle Design System)

Independientemente del formato del entregable (Web HTML/CSS, Diapositivas/Decks HTML, Manuales Markdown/PDF, Apps C#/React/Flutter):

1. **Jerarquía Visual y Tipografía**:
   - Títulos imponentes con contraste tipográfico moderno, viñetas estructuradas y resaltado estratégico en negritas/badges.
2. **Geometría Squircle y Bordes Suaves**:
   - Curvas orgánicas (`border-radius: 10px - 16px`), tarjetas elevadas y profundidad mediante sombras difusas y capas.
3. **Glassmorphism y Micro-animaciones FLIP**:
   - Desenfoque de fondo (*backdrop-filter blur*), animaciones fluidas (`cubic-bezier(0.2, 1, 0.3, 1)`) a 180ms - 250ms.
4. **Cero Elementos Toscos y Accesibilidad**:
   - Eliminar controles fea por defecto (`appearance: none`). Sustituirlos por **cápsulas Squircle custom** (ej: badges `#1`, `#2`).
   - Guardar siempre preferencias de usuario (zoom, temas) en `localStorage` o configuración persistente.
5. **Protección de Datos e Intercepción**:
   - Nunca permitir la pérdida accidental de datos. Modales interactivos deben interceder si hay cambios sin guardar (`isModified`).

---

## 🛠️ 3. Reglas de Ingeniería y Flujo de Trabajo Inamovibles

1. **Protocolo Estricto de Commits (REGLA DE ORO)**:
   - Parches iterativos locales llevan sufijos de letras (`x.x.1a`, `x.x.1b`).
   - **Queda estrictamente prohibido ejecutar `git commit` o `git push` en repositorios de proyectos** sin la confirmación explícita previa de Ibrahim. *(Excepción: En el repo homónimo `ibrahim-agent-core`, el agente gestiona las actualizaciones de memoria de forma directa).*
2. **Escalabilidad Total e Incremental (Anti-Reescrituras)**:
   - Todo nuevo desarrollo debe construirse como capas acumulativas desacopladas. Queda prohibido crear patrones rígidos que obliguen a rehacer el sistema desde cero.
3. **No Adivinar Código ni Rutas**:
   - Inspeccionar los archivos autoritativos reales antes de emitir diagnósticos. Rastrear siempre la causa raíz.
4. **Validación Sintáctica Obligatoria**:
   - Ejecutar la compilación o script de validación sintáctica (0 errores) antes de reportar completada una tarea.

---

## 📚 4. Base de Conocimiento de Proyectos Históricos (`knowledge_base/`)

Este repositorio consolida las reglas específicas de los proyectos clave de Ibrahim para consulta de cualquier agente de IA:
- [`knowledge_base/mise_work_AGENTS.md`](knowledge_base/mise_work_AGENTS.md): Suite de automatización de Tiendas y Bodegas LCP (Apps Script / Sheets `_SYNC` A4:L / Quiosco Picking 1050x700px).
- [`knowledge_base/reviews_lcp_gdl_AGENTS.md`](knowledge_base/reviews_lcp_gdl_AGENTS.md): Dashboard de Reseñas Etoile (Supabase, Netlify Functions, clasificadores LLM).
- [`knowledge_base/ultima_parisienne_design.md`](knowledge_base/ultima_parisienne_design.md): Sistema por Épocas (*Altair, Atlas, Aethel, Antares*) y paleta corporativa LCP.

---

## 📂 5. Protocolo de Sincronización Automática en Nuevas PCs

Cualquier subagente o entorno que inicie debe:
1. Ejecutar `setup.ps1` o leer este manifiesto.
2. Inyectar silenciosamente las reglas en `~/.gemini/config/rules/global_standards.md`.
3. Aplicar la firma y obsesión por la calidad de Ibrahim en cualquier tipo de entregable.
