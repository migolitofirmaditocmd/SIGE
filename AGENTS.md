# SIGE · Sistema Integral de Gestión Escolar
**Escuela Secundaria Mixta 5**

---

## 🚨 REGLA FUNDAMENTAL DE DESARROLLO (MANDATORIA)

Antes de crear, modificar, refactorizar o eliminar cualquier archivo o código en este repositorio:
1. **Revisa obligatoriamente la carpeta [`docs/`](file:///c:/Users/pc/Documents/SIGE/docs) y todas sus subcarpetas** (especificaciones Markdown, diagramas XML/draw.io, historias de usuario, modelos relacionales y flujos de negocio).
2. Toda decisión técnica, de arquitectura, base de datos y seguridad debe basarse en la documentación oficial allí descrita (ver regla detallada en [`.agents/rules/obligatoriedad_documentacion_docs.md`](file:///c:/Users/pc/Documents/SIGE/.agents/rules/obligatoriedad_documentacion_docs.md)).
3. Todo código Python debe cumplir con **PEP 8**, tipado estricto y **Docstrings en Google Style** (ver regla en [`.agents/rules/docstrings_pep8.md`](file:///c:/Users/pc/Documents/SIGE/.agents/rules/docstrings_pep8.md)).

---

## 🏗️ Stack Tecnológico
* **Backend**: Python 3.13 + Django 5.1 + Django REST Framework + PostgreSQL (con fallback SQLite local) + Pytest.
* **Frontend**: Next.js (React, TypeScript, Tailwind CSS, Squircle UI, PWA con Service Worker para soporte offline).
* **Criptografía**: Tokens opacos UUIDv4 con firma HMAC-SHA256 y renderizado PNG (qrcode + Pillow).

## 🛠️ Comandos Principales
* Entorno virtual: `.\backend\.venv\Scripts\Activate.ps1`
* Migraciones: `python backend/manage.py migrate`
* Ejecutar pruebas: `pytest`
* Sembrar datos piloto: `python backend/manage.py seed_pilot_data`
