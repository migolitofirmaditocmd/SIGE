# SIGE · Sistema Integral de Gestión Escolar
**Institución**: Escuela Secundaria Mixta 5  
**Proyecto**: Servicio Social (24 semanas / 480 horas totales)  
**Equipo de Desarrollo**: Ibrahim García ([@ultimaibrahim](https://github.com/ultimaibrahim)) & Miguel ([@migolitofirmaditocmd](https://github.com/migolitofirmaditocmd))  
**Arquitectura**: Frontend SPA / PWA (Next.js / TypeScript) + Backend REST API (Django / PostgreSQL) + Servidor Local LAN  
**Tablero de Gestión Oficial**: [GitHub Project v2 · SIGE](https://github.com/users/ultimaibrahim/projects/3)

---

## 🧭 Propósito del Proyecto
Establecer una infraestructura tecnológica centralizada, escalable y sostenible que reduzca la dependencia de procesos manuales, modernice el control de asistencia mediante identificadores QR, centralice el registro de incidencias y reportes escolares en 4 etapas, y opere en red local escolar de manera resiliente sin depender de conexión a Internet.

---

## 📋 Tablero de Control y Gestión (GitHub Projects)
El seguimiento de los **8 hitos oficiales**, la estructura de desglose de trabajo (EDT/WBS de 146 actividades) y la asignación de tareas se gestionan en:
👉 **[https://github.com/users/ultimaibrahim/projects/3](https://github.com/users/ultimaibrahim/projects/3)**

- **Vistas disponibles**:
  - **Tabla de Hitos (Table)**: Matriz con campos personalizados, estado e hitos asociados.
  - **Tablero Kanban de Flujo (Board)**: Flujo de trabajo (`Todo` ➔ `In Progress` ➔ `Done`).
  - **Cronograma de Hitos (Roadmap)**: Vista temporal alineada a las 24 semanas del cronograma maestro.

---

## 🛠️ Stack Tecnológico Base
- **Frontend & App Móvil**: [Next.js](https://nextjs.org/) (React, TypeScript, Tailwind CSS, Squircle UI, PWA con Service Worker para soporte offline)
- **Backend & API**: [Django REST Framework](https://www.django-rest-framework.org/) (Python 3.11+, Django 5.x)
- **Base de Datos**: PostgreSQL 15+
- **Infraestructura**: Servidor Local Físico en la Secundaria Mixta 5 (operación LAN sin Internet obligatoria)
- **Control de Versiones & Gestión**: Git, GitHub & GitHub Projects v2

---

## 📂 Estructura del Repositorio
```text
├── ACTA_CONSTITUTIVA_SIGE_v8.md             # Acta constitutiva oficial aprobada v8
├── docs/                                    # Documentación formal de ingeniería (SDLC)
│   ├── ACTA CONSTITUTIVA DE SOFTWARE PARA SECUNDARIA MIXTA 5.md
│   ├── ACTA_CONSTITUTIVA_SIGE_v2_corregida.md
│   ├── 01_ESPECIFICACION_DE_REQUISITOS_Y_FLUJOS.md # Flujos de proceso, RFs, RNFs
│   ├── 02_MODELO_DE_DATOS_Y_ARQUITECTURA_DB.md     # Diagrama ERD y constraints de BD
│   ├── PROPUESTA_TECNICA_APP_MOVIL_PWA.md  # Dictamen de arquitectura móvil PWA
│   ├── plantilla_estudiantes_secundaria5.csv # Plantilla canónica de importación
│   ├── gantt_cronograma/                   # Cronograma maestro y WBS Nivel 2 y 3
│   │   ├── SIGE_Diagrama_de_Gantt_WBS_Completo.xlsx (Hojas: Gantt, Lista Actividades, Cronología)
│   │   └── SIGE_Gantt_WBS_Nivel_2_y_3.csv
│   ├── Historias de Usuario/               # Historias de usuario, BDD y criterios v1/v2
│   ├── Flujo_registro_estudiante/          # Diagramas DrawIO de onboarding de alumnos
│   ├── Flujo_ciclo_qr/                     # Diagramas DrawIO de tokens y QR
│   ├── Flujo_asistencia_alumnos_docentes/  # Diagramas DrawIO de asistencia
│   ├── Flujo reportes de estudiantes/      # Diagramas DrawIO de incidencias
│   └── base de datos en excel/             # Listas reales de estudiantes para credenciales
├── backend/                                 # API Django REST Framework
│   ├── requirements.txt
│   └── .env.example
├── frontend/                                # Aplicación Next.js (próximamente)
├── .gitignore
└── README.md
```

---

## 🏛️ Hitos y Niveles de Madurez Tecnológica (24 Semanas / Acta v8)
1. **Hito 01 (Sem 1–8)**: Base funcional, base de datos y generación de códigos QR únicos para credenciales.
2. **Hito 02 (Sem 8–11)**: Sistema web integrado, gestión de estudiantes, usuarios y autenticación RBAC.
3. **Hito 03 (Sem 11–14)**: Backend, API y control de asistencia escolar centralizado.
4. **Hito 04 (Sem 14–17)**: Aplicación móvil operativa (PWA con escaneo QR y registro docente/prefectura).
5. **Hito 05 (Sem 17–19)**: Servidor local e infraestructura institucional LAN (operación offline sin Internet).
6. **Hito 06 (Sem 19–22)**: Validación con usuarios, pruebas de usabilidad y operación piloto real.
7. **Hito 07 (Sem 22–23)**: Plataforma integral validada multiplataforma (Web + Móvil + Servidor Local).
8. **Hito 08 (Sem 23–24)**: Preparación para operación, respaldos, manuales y entrega institucional final.
