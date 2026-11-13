/* eslint-disable @next/next/no-img-element */
"use client";

import React, { useEffect, useState } from "react";
import { AcademicGroup, Student } from "../types";
import {
  downloadGroupCredentialPdf,
  fetchStudentsByGroup,
  getStudentPhotoUrl,
} from "../services";
import { Badge, Button } from "@/shared/ui";
import {
  User,
  Loader2,
  Eye,
  Phone,
  Upload,
  FileDown,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Camera,
  CheckCircle2,
} from "lucide-react";

interface GroupStudentTableProps {
  group: AcademicGroup;
  onSelectStudent: (student: Student) => void;
  refreshTrigger?: number;
  onUploadPhotosClick?: () => void;
}

export const GroupStudentTable: React.FC<GroupStudentTableProps> = ({
  group,
  onSelectStudent,
  refreshTrigger = 0,
  onUploadPhotosClick,
}) => {
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState(false);
  const [pdfMessage, setPdfMessage] = useState<{
    type: "success" | "error" | "warning";
    text: string;
  } | null>(null);
  /** Controla si el tablón de pendientes está expandido o colapsado. */
  const [pendingExpanded, setPendingExpanded] = useState<boolean>(true);

  useEffect(() => {
    async function loadStudents() {
      try {
        setIsLoading(true);
        setError(null);
        setPdfMessage(null);
        const data = await fetchStudentsByGroup(
          group.grade,
          group.group_letter,
          group.shift
        );
        setStudents(data);
      } catch (err) {
        console.error(err);
        setError("Error al cargar la lista de estudiantes.");
      } finally {
        setIsLoading(false);
      }
    }

    loadStudents();
  }, [group.id, group.grade, group.group_letter, group.shift, refreshTrigger]);

  /** Genera y descarga el PDF con todas las credenciales elegibles del grupo. */
  const handleDownloadGroupPdf = async () => {
    const withPhoto = students.filter((s) => Boolean(s.photo_url));
    const withoutPhoto = students.filter((s) => !s.photo_url);

    if (withPhoto.length === 0) {
      setPdfMessage({
        type: "error",
        text: `Ningún alumno del grupo tiene foto cargada. Sube las fotografías primero para poder generar credenciales.`,
      });
      return;
    }

    try {
      setIsDownloadingPdf(true);
      setPdfMessage(null);
      const blob = await downloadGroupCredentialPdf(group.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `credenciales_${group.display_name.replace(/\s+/g, "_")}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      if (withoutPhoto.length > 0) {
        setPdfMessage({
          type: "warning",
          text: `PDF descargado con ${withPhoto.length} credencial(es). ${withoutPhoto.length} alumno(s) sin foto fueron excluidos del PDF.`,
        });
      } else {
        setPdfMessage({
          type: "success",
          text: `PDF descargado con las ${withPhoto.length} credenciales del grupo.`,
        });
      }
    } catch (err: unknown) {
      setPdfMessage({
        type: "error",
        text:
          err instanceof Error
            ? err.message
            : "Error al generar credenciales del grupo.",
      });
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-white rounded-xl border border-slate-200">
        <Loader2 className="w-8 h-8 animate-spin text-[#0A3D91] mb-2" />
        <p className="text-sm text-slate-600 font-medium">
          Cargando alumnos de {group.display_name}...
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-50 text-red-700 rounded-xl border border-red-200 text-sm">
        {error}
      </div>
    );
  }

  /* ── Cálculos de cobertura de credenciales ───────────────────────── */
  const studentsWithPhoto = students.filter((s) => Boolean(s.photo_url));
  const studentsWithoutPhoto = students.filter((s) => !s.photo_url);
  const coveragePct =
    students.length > 0
      ? Math.round((studentsWithPhoto.length / students.length) * 100)
      : 0;
  const allHavePhoto = studentsWithoutPhoto.length === 0;

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col gap-0">

      {/* ── TABLÓN DE PENDIENTES (arriba de todo, siempre visible si hay faltantes) ── */}
      {studentsWithoutPhoto.length > 0 && (
        <div className="border-b border-amber-200 bg-amber-50/80">
          {/* Cabecera del tablón */}
          <button
            type="button"
            onClick={() => setPendingExpanded((v) => !v)}
            className="w-full flex items-center justify-between px-5 py-3 text-left hover:bg-amber-100/60 transition-colors"
          >
            <div className="flex items-center gap-2.5">
              <div className="flex items-center justify-center w-7 h-7 rounded-full bg-amber-200 text-amber-800 shrink-0">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-bold text-amber-900">
                  Tablón de Pendientes — Credenciales sin generar
                </p>
                <p className="text-xs text-amber-700 leading-snug">
                  <span className="font-bold">{studentsWithoutPhoto.length} alumno(s)</span> de{" "}
                  {students.length} no tienen fotografía y{" "}
                  <span className="font-bold">quedarán excluidos</span> del PDF de credenciales.
                  Sube sus fotos para incluirlos.
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-xs font-bold text-amber-800 bg-amber-200 px-2 py-0.5 rounded-full">
                {studentsWithoutPhoto.length} pendiente(s)
              </span>
              {pendingExpanded ? (
                <ChevronUp className="w-4 h-4 text-amber-700" />
              ) : (
                <ChevronDown className="w-4 h-4 text-amber-700" />
              )}
            </div>
          </button>

          {/* Lista de alumnos pendientes (colapsable) */}
          {pendingExpanded && (
            <div className="px-5 pb-3">
              <div className="bg-white rounded-xl border border-amber-200 overflow-hidden">
                <table className="w-full text-left border-collapse text-xs">
                  <thead>
                    <tr className="bg-amber-100/70 border-b border-amber-200 text-amber-800 font-bold uppercase tracking-wider">
                      <th className="py-2 px-3 text-center w-8">#</th>
                      <th className="py-2 px-3 w-32">Matrícula</th>
                      <th className="py-2 px-3">Nombre del Alumno</th>
                      <th className="py-2 px-3 text-center hidden sm:table-cell">Estatus</th>
                      <th className="py-2 px-3 text-right">Acción</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-amber-100">
                    {studentsWithoutPhoto.map((student, idx) => (
                      <tr key={student.id} className="hover:bg-amber-50/60 transition-colors">
                        <td className="py-2 px-3 text-center font-mono text-amber-600 font-bold">
                          {idx + 1}
                        </td>
                        <td className="py-2 px-3 font-mono font-bold text-[#0A3D91]">
                          {student.enrollment_id}
                        </td>
                        <td className="py-2 px-3">
                          <div className="flex items-center gap-2">
                            <div className="w-5 h-6 rounded border border-dashed border-amber-300 bg-amber-100 flex items-center justify-center shrink-0">
                              <User className="w-3 h-3 text-amber-500" />
                            </div>
                            <span className="font-semibold text-slate-800">
                              {student.display_name}
                            </span>
                          </div>
                        </td>
                        <td className="py-2 px-3 text-center hidden sm:table-cell">
                          <span className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-800 bg-amber-100 border border-amber-200 px-2 py-0.5 rounded-full">
                            <Camera className="w-3 h-3" />
                            Falta foto
                          </span>
                        </td>
                        <td className="py-2 px-3 text-right">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onSelectStudent(student)}
                            className="h-7 px-2.5 text-[10px] text-[#0A3D91] hover:bg-blue-50 border-[#0A3D91]/30"
                          >
                            <Eye className="w-3 h-3 mr-1" />
                            Ver ficha
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Acción sugerida */}
              {onUploadPhotosClick && (
                <div className="mt-2.5 flex items-center justify-between">
                  <p className="text-[11px] text-amber-700 italic">
                    💡 Usa <span className="font-bold">Subir Fotos por Lote</span> para cargar todas las fotografías pendientes a la vez.
                  </p>
                  <Button
                    onClick={onUploadPhotosClick}
                    size="sm"
                    className="h-7 px-3 text-[11px] font-bold bg-amber-600 hover:bg-amber-700 text-white border-0 shadow-xs flex items-center gap-1.5"
                  >
                    <Upload className="w-3 h-3" />
                    Subir fotos ahora
                  </Button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ── Todos con foto: banner de éxito ── */}
      {!isLoading && allHavePhoto && students.length > 0 && (
        <div className="px-5 py-2.5 bg-emerald-50 border-b border-emerald-200 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <p className="text-xs font-semibold text-emerald-800">
            ¡Todos los alumnos del grupo tienen fotografía!
            El PDF de credenciales incluirá a los {students.length} estudiantes.
          </p>
        </div>
      )}

      {/* ── Barra superior de la tabla ── */}
      <div className="px-5 py-3.5 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h4 className="font-bold text-sm text-slate-800">
            Listado Oficial: {group.display_name}
          </h4>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 mt-0.5">
            <p className="text-xs text-slate-500">
              {students.length} estudiantes registrados
            </p>
            {/* Cobertura de fotos / credenciales */}
            <span
              className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${
                allHavePhoto
                  ? "bg-emerald-100 text-emerald-800 border-emerald-200"
                  : studentsWithPhoto.length === 0
                  ? "bg-red-100 text-red-700 border-red-200"
                  : "bg-amber-100 text-amber-800 border-amber-200"
              }`}
            >
              {studentsWithPhoto.length}/{students.length} con foto ({coveragePct}%)
            </span>
          </div>
        </div>

        {/* Botones de acción */}
        <div className="flex items-center gap-2 flex-wrap justify-end">
          {onUploadPhotosClick && (
            <Button
              onClick={onUploadPhotosClick}
              variant="outline"
              size="sm"
              className="bg-white hover:bg-blue-50 text-[#0A3D91] border-blue-200 flex items-center gap-1.5 text-xs font-semibold shadow-xs"
            >
              <Upload className="w-3.5 h-3.5 text-[#0A3D91]" />
              <span>Subir Fotos</span>
            </Button>
          )}

          {/* Botón credenciales PDF del grupo */}
          <div className="flex flex-col items-end gap-1">
            <Button
              onClick={handleDownloadGroupPdf}
              disabled={isDownloadingPdf || studentsWithPhoto.length === 0}
              variant="outline"
              size="sm"
              className={`flex items-center gap-1.5 text-xs font-semibold shadow-xs ${
                studentsWithPhoto.length === 0
                  ? "opacity-50 cursor-not-allowed bg-slate-50 text-slate-400 border-slate-200"
                  : "bg-white hover:bg-emerald-50 text-emerald-700 border-emerald-200"
              }`}
              title={
                studentsWithPhoto.length === 0
                  ? "Ningún alumno tiene foto — sube fotografías primero"
                  : studentsWithoutPhoto.length > 0
                  ? `Generará ${studentsWithPhoto.length} credencial(es). ${studentsWithoutPhoto.length} alumno(s) sin foto serán excluidos.`
                  : `Descargar PDF con las ${studentsWithPhoto.length} credenciales del grupo`
              }
            >
              {isDownloadingPdf ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Generando...</span>
                </>
              ) : (
                <>
                  <FileDown className="w-3.5 h-3.5" />
                  <span>
                    Credenciales PDF
                    {studentsWithoutPhoto.length > 0 && studentsWithPhoto.length > 0 && (
                      <span className="ml-1 text-[10px] font-bold bg-amber-100 text-amber-800 px-1.5 py-0.5 rounded-full border border-amber-200">
                        {studentsWithPhoto.length}/{students.length}
                      </span>
                    )}
                  </span>
                </>
              )}
            </Button>

            {/* Mensaje de resultado del PDF */}
            {pdfMessage && (
              <span
                className={`text-[10px] font-semibold flex items-center gap-1 ${
                  pdfMessage.type === "success"
                    ? "text-emerald-700"
                    : pdfMessage.type === "warning"
                    ? "text-amber-700"
                    : "text-red-600"
                }`}
              >
                {pdfMessage.type === "success" && <CheckCircle2 className="w-3 h-3" />}
                {pdfMessage.type === "warning" && <AlertTriangle className="w-3 h-3" />}
                {pdfMessage.type === "error" && <AlertTriangle className="w-3 h-3" />}
                {pdfMessage.text}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ── Tabla responsiva ── */}
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-100/70 text-xs font-bold text-slate-600 uppercase tracking-wider">
              <th className="py-3 px-3 text-center w-12">#</th>
              <th className="py-3 px-3 text-center w-16">Foto</th>
              <th className="py-3 px-4 w-32">Matrícula</th>
              <th className="py-3 px-4">Nombre Completo</th>
              <th className="py-3 px-4">Tutor / Teléfono</th>
              <th className="py-3 px-3 text-center w-28">Estatus</th>
              <th className="py-3 px-3 text-center w-32">Credencial</th>
              <th className="py-3 px-4 text-right w-28">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm">
            {students.map((student, idx) => {
              const primaryGuardian =
                student.guardians.find((g) => g.is_primary_contact) ||
                student.guardians[0];
              const hasPhoto = Boolean(student.photo_url);

              return (
                <tr
                  key={student.id}
                  className={`transition-colors ${
                    hasPhoto
                      ? "hover:bg-blue-50/40"
                      : "bg-amber-50/30 hover:bg-amber-50/60"
                  }`}
                >
                  {/* Número de fila */}
                  <td className="py-2.5 px-3 text-center text-xs font-mono font-bold text-slate-400">
                    {idx + 1}
                  </td>

                  {/* Foto o Placeholder */}
                  <td className="py-2.5 px-3 text-center">
                    <div className="inline-flex items-center justify-center">
                      {hasPhoto ? (
                        <img
                          src={getStudentPhotoUrl(student.id, student.updated_at)}
                          alt={student.display_name}
                          className="w-9 h-11 object-cover rounded-md border border-slate-300"
                        />
                      ) : (
                        <div
                          title="Sin fotografía — no se generará credencial"
                          className="w-9 h-11 rounded-md border border-dashed border-amber-300 bg-amber-50 flex flex-col items-center justify-center p-0.5 text-center"
                        >
                          <User className="w-4 h-4 text-amber-600" />
                          <span className="text-[7px] font-bold text-amber-800 leading-none">
                            Falta
                          </span>
                        </div>
                      )}
                    </div>
                  </td>

                  {/* Matrícula */}
                  <td className="py-2.5 px-4 font-mono font-bold text-xs text-[#0A3D91]">
                    {student.enrollment_id}
                  </td>

                  {/* Nombre completo */}
                  <td className="py-2.5 px-4">
                    <div className="font-semibold text-slate-900">
                      {student.display_name}
                    </div>
                    {student.curp && (
                      <div className="text-[11px] text-slate-400 font-mono">
                        {student.curp}
                      </div>
                    )}
                  </td>

                  {/* Tutor y Teléfono */}
                  <td className="py-2.5 px-4 text-xs">
                    {primaryGuardian ? (
                      <div>
                        <span className="font-medium text-slate-800 block">
                          {primaryGuardian.guardian.display_name}
                        </span>
                        {primaryGuardian.guardian.phone_number && (
                          <span className="text-slate-500 font-mono flex items-center gap-1 mt-0.5">
                            <Phone className="w-3 h-3 text-slate-400" />
                            {primaryGuardian.guardian.phone_number}
                          </span>
                        )}
                      </div>
                    ) : (
                      <span className="text-slate-400 italic">
                        Sin tutor registrado
                      </span>
                    )}
                  </td>

                  {/* Estatus */}
                  <td className="py-2.5 px-3 text-center">
                    <Badge
                      status={student.status === "ACTIVO" ? "ACTIVO" : "PENDIENTE"}
                      label={student.status_display}
                      size="sm"
                    />
                  </td>

                  {/* Columna Credencial — nueva */}
                  <td className="py-2.5 px-3 text-center">
                    {hasPhoto ? (
                      <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        Lista
                      </span>
                    ) : (
                      <span
                        title="Falta fotografía para generar credencial"
                        className="inline-flex items-center gap-1 text-[10px] font-bold text-amber-800 bg-amber-50 border border-amber-200 px-2 py-0.5 rounded-full"
                      >
                        <Camera className="w-3 h-3 text-amber-600" />
                        Sin foto
                      </span>
                    )}
                  </td>

                  {/* Acción Ver Ficha */}
                  <td className="py-2.5 px-4 text-right">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onSelectStudent(student)}
                      className="h-8 px-2.5 text-xs text-[#0A3D91] hover:bg-blue-50 border-[#0A3D91]/30"
                    >
                      <Eye className="w-3.5 h-3.5 mr-1" />
                      <span>Ficha</span>
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
};
