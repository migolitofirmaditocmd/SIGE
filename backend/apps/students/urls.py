"""URLs del módulo de estudiantes y tutores.

Mapea todos los endpoints del módulo EST definidos en:
    - §2.4: endpoints de estudiantes y foto.
    - §3.4: endpoints de tutores y vínculos.

Todas las rutas se montan bajo /api/v1/students/ en core/urls.py.
"""

from django.urls import path

from .views import (
    ConsentUpdateView,
    GuardianDetailView,
    InvalidateContactView,
    StudentDetailView,
    StudentGuardianAddView,
    StudentListCreateView,
    StudentPhotoView,
    StudentReinstateView,
    StudentStatusView,
)

app_name = "students"

urlpatterns = [
    # ---------------------------------------------------------------
    # Estudiantes (§2.4)
    # ---------------------------------------------------------------
    # GET  /api/v1/students/        — listado paginado
    # POST /api/v1/students/        — crear estudiante
    path(
        "",
        StudentListCreateView.as_view(),
        name="student-list-create",
    ),
    # GET   /api/v1/students/{id}/   — expediente completo
    # PATCH /api/v1/students/{id}/   — actualización parcial
    path(
        "<uuid:pk>/",
        StudentDetailView.as_view(),
        name="student-detail",
    ),
    # POST /api/v1/students/{id}/photo/  — carga de fotografía
    # GET  /api/v1/students/{id}/photo/  — descarga autenticada
    path(
        "<uuid:pk>/photo/",
        StudentPhotoView.as_view(),
        name="student-photo",
    ),

    # ---------------------------------------------------------------
    # Transiciones de estado (§3.4)
    # ---------------------------------------------------------------
    # POST /api/v1/students/{id}/status/     — BAJA / EGRESADO
    path(
        "<uuid:pk>/status/",
        StudentStatusView.as_view(),
        name="student-status",
    ),
    # POST /api/v1/students/{id}/reinstate/  — BAJA → ACTIVO
    path(
        "<uuid:pk>/reinstate/",
        StudentReinstateView.as_view(),
        name="student-reinstate",
    ),

    # ---------------------------------------------------------------
    # Tutores y vínculos (§3.4)
    # ---------------------------------------------------------------
    # POST /api/v1/students/{id}/guardians/  — agregar tutor al alumno
    path(
        "<uuid:pk>/guardians/",
        StudentGuardianAddView.as_view(),
        name="student-guardian-add",
    ),
    # PATCH /api/v1/guardians/{id}/          — editar tutor (shared warning)
    path(
        "guardians/<uuid:pk>/",
        GuardianDetailView.as_view(),
        name="guardian-detail",
    ),
    # POST /api/v1/student-guardians/{id}/invalidate-contact/
    path(
        "student-guardians/<uuid:pk>/invalidate-contact/",
        InvalidateContactView.as_view(),
        name="studentguardian-invalidate-contact",
    ),
    # PATCH /api/v1/student-guardians/{id}/consent/
    path(
        "student-guardians/<uuid:pk>/consent/",
        ConsentUpdateView.as_view(),
        name="studentguardian-consent",
    ),
]
