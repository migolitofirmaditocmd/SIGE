/* eslint-disable @next/next/no-img-element */
"use client";

import React, { useEffect, useState } from "react";
import { AcademicGroup, Student } from "../types";
import { fetchStudentsByGroup, getStudentPhotoUrl } from "../services";
import { Badge, Button } from "@/shared/ui";
import { User, Loader2, Eye, Phone, Upload } from "lucide-react";

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

  useEffect(() => {
    async function loadStudents() {
      try {
        setIsLoading(true);
        setError(null);
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

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden flex flex-col">
      {/* Barra superior de la tabla */}
      <div className="px-5 py-3.5 bg-slate-50 border-b border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h4 className="font-bold text-sm text-slate-800">
            Listado Oficial: {group.display_name}
          </h4>
          <p className="text-xs text-slate-500">
            {students.length} estudiantes registrados en este grupo
          </p>
        </div>

        {onUploadPhotosClick && (
          <Button
            onClick={onUploadPhotosClick}
            variant="outline"
            size="sm"
            className="bg-white hover:bg-blue-50 text-[#0A3D91] border-blue-200 flex items-center gap-1.5 text-xs font-semibold shadow-xs"
          >
            <Upload className="w-3.5 h-3.5 text-[#0A3D91]" />
            <span>Subir Fotos de este Grupo</span>
          </Button>
        )}
      </div>

      {/* Tabla responsiva */}
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
              <th className="py-3 px-4 text-right w-28">Acción</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-sm">
            {students.map((student, idx) => {
              const primaryGuardian =
                student.guardians.find((g) => g.is_primary_contact) ||
                student.guardians[0];

              return (
                <tr
                  key={student.id}
                  className="hover:bg-blue-50/40 transition-colors"
                >
                  {/* Número de fila */}
                  <td className="py-2.5 px-3 text-center text-xs font-mono font-bold text-slate-400">
                    {idx + 1}
                  </td>

                  {/* Foto o Placeholder */}
                  <td className="py-2.5 px-3 text-center">
                    <div className="inline-flex items-center justify-center">
                      {student.photo_url ? (
                        <img
                          src={getStudentPhotoUrl(student.id, student.updated_at)}
                          alt={student.display_name}
                          className="w-9 h-11 object-cover rounded-md border border-slate-300"
                        />
                      ) : (
                        <div
                          title="Falta foto"
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
