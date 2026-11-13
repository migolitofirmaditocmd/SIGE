"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Student,
  AcademicGroup,
  StudentSearchBar,
  StudentDetailCard,
  GroupSelector,
  GroupStudentTable,
  BatchPhotoUploadModal,
} from "@/features/students";
import { Badge, Button } from "@/shared/ui";
import {
  Search,
  ArrowLeft,
  GraduationCap,
  Sparkles,
  Upload,
} from "lucide-react";

export default function EstudiantesAdminPage() {
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [selectedGroup, setSelectedGroup] = useState<AcademicGroup | null>(null);
  const [isBatchModalOpen, setIsBatchModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSelectStudent = (student: Student) => {
    setSelectedStudent(student);
    // Desplazamiento suave al espacio de la ficha si está más abajo
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleBatchSuccess = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <main className="min-h-screen bg-[#F1F5F9] flex flex-col">
      {/* Modal de Carga Masiva de Fotografías */}
      <BatchPhotoUploadModal
        isOpen={isBatchModalOpen}
        onClose={() => setIsBatchModalOpen(false)}
        selectedGroup={selectedGroup}
        onSuccess={handleBatchSuccess}
      />

      {/* Barra Superior Institucional */}
      <header className="bg-[#0A3D91] text-white py-4 px-6 shadow-sm sticky top-0 z-40">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="p-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition-colors text-white"
              title="Volver al inicio"
            >
              <ArrowLeft className="w-5 h-5" />
            </Link>
            <div className="w-9 h-9 bg-white/10 rounded-xl flex items-center justify-center font-bold text-base border border-white/20">
              5
            </div>
            <div>
              <h1 className="text-base font-bold tracking-tight">
                Panel Administrativo · Consulta de Estudiantes
              </h1>
              <p className="text-xs text-blue-200">
                Escuela Secundaria Mixta 5 · Hito 2 (Puntos 4.7 y 4.8)
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button
              onClick={() => setIsBatchModalOpen(true)}
              variant="primary"
              size="sm"
              className="bg-white text-[#0A3D91] hover:bg-blue-50 border border-white/20 font-bold flex items-center gap-1.5 shadow-sm text-xs py-1.5 px-3"
            >
              <Upload className="w-3.5 h-3.5 text-[#0A3D91]" />
              <span>Subir Fotos por Lote</span>
            </Button>
            <Badge
              status="ACTIVO"
              label="Fase 1 · En Línea"
              size="sm"
              className="bg-white/15 text-white border-white/20"
            />
          </div>
        </div>
      </header>

      {/* Contenedor Principal */}
      <div className="max-w-6xl mx-auto w-full px-4 sm:px-6 py-6 flex-1 flex flex-col gap-6">
        {/* Sección 1: Buscador individual por nombre o matrícula */}
        <section className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm font-bold text-slate-900">
              <Search className="w-4 h-4 text-[#0A3D91]" />
              <span>Búsqueda Individual de Estudiante</span>
            </div>
            <span className="text-xs text-slate-500 hidden sm:inline">
              Escribe el nombre o matrícula para desplegar su ficha, foto y QR
            </span>
          </div>

          <StudentSearchBar onSelectStudent={handleSelectStudent} />
        </section>

        {/* Sección 2: Espacio de la Ficha Individual del Estudiante Seleccionado */}
        {selectedStudent && (
          <section className="animate-in fade-in slide-in-from-top-4 duration-300">
            <div className="mb-2 flex items-center justify-between">
              <span className="text-xs font-bold text-[#0A3D91] uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5" />
                Ficha del Estudiante Seleccionado
              </span>
            </div>
            <StudentDetailCard
              student={selectedStudent}
              onClose={() => setSelectedStudent(null)}
              onStudentUpdated={(updated) => {
                setSelectedStudent(updated);
                setRefreshKey((prev) => prev + 1);
              }}
              onStudentDeleted={() => {
                setSelectedStudent(null);
                setRefreshKey((prev) => prev + 1);
              }}
            />
          </section>
        )}

        {/* Sección 3: Consulta de Estudiantes por Grupo */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-base font-bold text-slate-900">
              <GraduationCap className="w-5 h-5 text-[#0A3D91]" />
              <span>Consulta por Grupo Escolar</span>
            </div>
            <span className="text-xs text-slate-500">
              Vista tabular por grupo (fotografía, matrícula, datos y acceso a ficha)
            </span>
          </div>

          {/* Selector de Grupo */}
          <GroupSelector
            selectedGroup={selectedGroup}
            onSelectGroup={setSelectedGroup}
          />

          {/* Tabla de Alumnos del Grupo */}
          {selectedGroup && (
            <GroupStudentTable
              group={selectedGroup}
              onSelectStudent={handleSelectStudent}
              refreshTrigger={refreshKey}
              onUploadPhotosClick={() => setIsBatchModalOpen(true)}
            />
          )}
        </section>
      </div>

      {/* Pie de Página */}
      <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-slate-500">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Escuela Secundaria Mixta 5 · Zapopan, Jalisco</span>
          <span>SIGE · Sistema Integral de Gestión Escolar</span>
        </div>
      </footer>
    </main>
  );
}
