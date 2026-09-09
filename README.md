# SIGE · Sistema Integral de Gestión Escolar
**Institución**: Escuela Secundaria Mixta 5  
**Proyecto**: Servicio Social (24 semanas / 480 horas totales)  
**Equipo de Desarrollo**: Ibrahim García ([@ultimaibrahim](https://github.com/ultimaibrahim)) & [@migolitofirmaditocmd](https://github.com/migolitofirmaditocmd)  
**Arquitectura**: Frontend SPA (Next.js / TypeScript) + Backend REST API (Django / PostgreSQL)  
**Tablero de Gestión Oficial**: [GitHub Project v2 · SIGE](https://github.com/users/ultimaibrahim/projects/3)

---

## 🧭 Propósito del Proyecto
Establecer una infraestructura tecnológica centralizada, escalable y sostenible que reduzca la dependencia de procesos manuales, modernice el control de asistencia mediante identificadores QR, centralice el registro de incidencias y reportes escolares, y facilite la comunicación oportuna con los familiares.

---

## 📋 Tablero de Control y Gestión (GitHub Projects)
El seguimiento de los 6 hitos, la estructura de desglose de trabajo (EDT/WBS) y la asignación de tareas se gestionan en:
👉 **[https://github.com/users/ultimaibrahim/projects/3](https://github.com/users/ultimaibrahim/projects/3)**

- **Vistas disponibles**:
  - **Tabla de Hitos (Table)**: Matriz con campos personalizados, estado e hitos asociados.
  - **Tablero Kanban de Flujo (Board)**: Flujo de trabajo (`Todo` ➔ `In Progress` ➔ `Done`).
  - **Cronograma de Hitos (Roadmap)**: Vista temporal alineada a las 24 semanas.

---

## 🛠️ Stack Tecnológico Base
- **Frontend**: [Next.js](https://nextjs.org/) (React, TypeScript, Tailwind CSS, Squircle UI)
- **Backend**: [Django REST Framework](https://www.django-rest-framework.org/) (Python 3.11+, Django 5.x)
- **Base de Datos**: PostgreSQL 15+
- **Control de Versiones & Gestión**: Git, GitHub & GitHub Projects v2

---

## 📂 Estructura del Repositorio
```text
├── docs/                    # Documentación formal de ingeniería (SDLC)
│   ├── ACTA CONSTITUTIVA DE SOFTWARE PARA SECUNDARIA MIXTA 5.md
│   ├── ACTA_CONSTITUTIVA_SIGE_v2_corregida.md (Charter con diagramas C4 y Gantt)
│   ├── 01_ESPECIFICACION_DE_REQUISITOS_Y_FLUJOS.md (Flujos, RFs, RNFs)
│   ├── 02_MODELO_DE_DATOS_Y_ARQUITECTURA_DB.md (Diagrama ERD y constraints)
│   └── plantilla_estudiantes_secundaria5.csv (Plantilla canónica oficial)
├── backend/                 # API Django REST Framework
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # Aplicación Next.js (próximamente)
├── .gitignore
└── README.md
```

---

## 🏛️ Hitos y Niveles de Madurez Tecnológica (24 Semanas)
1. **Hito 01 (Sem 1–8)**: Base funcional, base de datos y generación de códigos QR únicos para credenciales.
2. **Hito 02 (Sem 8–11)**: Sistema web integrado, autenticación JWT, RBAC y panel administrativo.
3. **Hito 03 (Sem 11–15)**: Control de asistencia mediante escaneo QR y reglas anti-duplicados.
4. **Hito 04 (Sem 16–19)**: Validación con usuarios, pruebas de usabilidad y operación piloto.
5. **Hito 05 (Sem 20–22)**: Plataforma integral validada (incidencias, reportes y mensajería con contingencia).
6. **Hito 06 (Sem 23–24)**: Preparación para operación, respaldos, manuales y entrega institucional.
