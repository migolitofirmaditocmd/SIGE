/* eslint-disable @next/next/no-img-element */
"use client";

import React from "react";
import { Student } from "../types";
import { getQrImageUrl } from "../services";
import { Badge, Card } from "@/shared/ui";
import {
  User,
  QrCode,
  Phone,
  MapPin,
  HeartPulse,
  CheckCircle2,
} from "lucide-react";

interface StudentDetailCardProps {
  student: Student;
  onClose?: () => void;
}

export const StudentDetailCard: React.FC<StudentDetailCardProps> = ({
  student,
  onClose,
}) => {
  const primaryGuardian =
    student.guardians.find((g) => g.is_primary_contact) ||
    student.guardians[0];

  return (
    <Card className="bg-white border-[#0A3D91]/20 shadow-md p-6 flex flex-col gap-6">
      {/* Encabezado: Foto / Placeholder, Nombre, Matrícula y Estatus */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-5 border-b border-slate-200">
        <div className="flex items-center gap-4">
          {/* Fotografía o Placeholder */}
          <div className="relative shrink-0">
            {student.photo_url ? (
              <img
                src={student.photo_url}
                alt={student.display_name}
                className="w-20 h-24 object-cover rounded-xl border-2 border-slate-300 shadow-sm"
              />
            ) : (
              <div className="w-20 h-24 rounded-xl border-2 border-dashed border-amber-300 bg-amber-50/70 flex flex-col items-center justify-center p-1 text-center">
                <User className="w-8 h-8 text-amber-600 mb-1" />
                <span className="text-[10px] font-bold text-amber-800 leading-tight">
                  Falta Foto
                </span>
                <span className="text-[8px] text-amber-600 leading-none mt-0.5">
                  Sin archivo
                </span>
              </div>
            )}
          </div>

          {/* Nombre y Matrícula */}
          <div className="space-y-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-xs font-bold text-[#0A3D91] bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-100">
                Matrícula: {student.enrollment_id}
              </span>
              <Badge
                status={student.status === "ACTIVO" ? "ACTIVO" : "PENDIENTE"}
                label={student.status_display}
                size="sm"
              />
              <span className="text-xs font-semibold text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full">
                {student.academic_group}
              </span>
            </div>

            <h3 className="text-xl font-bold text-[#0B1320] leading-snug">
              {student.display_name}
            </h3>

            {student.curp && (
              <p className="text-xs text-slate-500 font-mono">
                CURP: <span className="font-semibold">{student.curp}</span>
              </p>
            )}
          </div>
        </div>

        {onClose && (
          <button
            onClick={onClose}
            className="text-xs font-semibold text-slate-500 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors"
          >
            Cerrar ficha
          </button>
        )}
      </div>

      {/* Contenido en dos columnas: Datos generales / QR institucional */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Columna 1 y 2: Ficha técnica y de emergencia */}
        <div className="lg:col-span-2 space-y-4">
          {/* Tarjeta de Domicilio */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#0A3D91] uppercase tracking-wider">
              <MapPin className="w-4 h-4" />
              <span>Domicilio Registrado</span>
            </div>
            <div className="text-sm text-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div>
                <span className="text-xs text-slate-500 block">Calle y Número:</span>
                <span className="font-medium">
                  {student.address_street || "No registrado"}
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 block">Colonia:</span>
                <span className="font-medium">
                  {student.address_colonia || "No registrada"}
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 block">Municipio y Estado:</span>
                <span className="font-medium">
                  {student.address_municipio || "Zapopan"}
                  {student.address_estado ? `, ${student.address_estado}` : ""}
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 block">Código Postal:</span>
                <span className="font-medium font-mono">
                  {student.address_postal_code || "Sin C.P."}
                </span>
              </div>
            </div>
          </div>

          {/* Tarjeta de Salud y Alergias */}
          <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#0A3D91] uppercase tracking-wider">
              <HeartPulse className="w-4 h-4" />
              <span>Ficha Médica</span>
            </div>
            <div className="text-sm text-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div>
                <span className="text-xs text-slate-500 block">Tipo de Sangre:</span>
                <span className="font-bold text-red-700 bg-red-50 px-2 py-0.5 rounded border border-red-200 inline-block text-xs">
                  {student.blood_type || "No especificado"}
                </span>
              </div>
              <div>
                <span className="text-xs text-slate-500 block">Alergias Conocidas:</span>
                <span className="font-medium">
                  {student.allergies || "Ninguna"}
                </span>
              </div>
            </div>
          </div>

          {/* Tarjeta de Tutor / Contacto de Emergencia */}
          <div className="p-4 bg-blue-50/50 rounded-xl border border-blue-100 space-y-2">
            <div className="flex items-center gap-2 text-xs font-bold text-[#0A3D91] uppercase tracking-wider">
              <Phone className="w-4 h-4" />
              <span>Contacto de Emergencia / Tutor Legal</span>
            </div>
            {primaryGuardian ? (
              <div className="text-sm text-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-2">
                <div>
                  <span className="text-xs text-slate-500 block">Nombre del Tutor:</span>
                  <span className="font-semibold text-slate-900">
                    {primaryGuardian.guardian.display_name}
                  </span>
                  <span className="text-xs text-blue-700 font-medium block">
                    ({primaryGuardian.relationship_display})
                  </span>
                </div>
                <div>
                  <span className="text-xs text-slate-500 block">Teléfono de Contacto:</span>
                  <span className="font-bold text-emerald-800 font-mono text-base">
                    {primaryGuardian.guardian.phone_number || "Sin teléfono"}
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">
                Sin tutor legal registrado.
              </p>
            )}
          </div>
        </div>

        {/* Columna 3: Código QR de Asistencia Oficial */}
        <div className="flex flex-col items-center justify-between p-5 bg-gradient-to-b from-slate-50 to-white rounded-2xl border-2 border-slate-200 text-center">
          <div className="w-full space-y-1">
            <div className="flex items-center justify-center gap-1.5 text-xs font-bold text-[#0A3D91] uppercase tracking-wider">
              <QrCode className="w-4 h-4" />
              <span>Código QR de Asistencia</span>
            </div>
            <p className="text-[11px] text-slate-500">
              Escaneo óptico oficial con firma HMAC
            </p>
          </div>

          {/* Imagen del QR o Placeholder */}
          <div className="my-4">
            {student.active_qr_token_id ? (
              <div className="p-2.5 bg-white rounded-xl shadow-sm border border-slate-300 inline-block">
                <img
                  src={getQrImageUrl(student.active_qr_token_id)}
                  alt={`QR de ${student.display_name}`}
                  className="w-44 h-44 object-contain"
                />
                <span className="text-[9px] font-mono text-slate-400 block mt-1">
                  Token: {student.active_qr_token_id.slice(0, 18)}...
                </span>
              </div>
            ) : (
              <div className="w-44 h-44 rounded-xl border-2 border-dashed border-slate-300 bg-slate-100 flex flex-col items-center justify-center p-3 text-center">
                <QrCode className="w-10 h-10 text-slate-400 mb-2" />
                <span className="text-xs font-bold text-slate-700">
                  QR Pendiente
                </span>
                <span className="text-[10px] text-slate-500 mt-1">
                  Aún no se ha emitido el código QR para este estudiante.
                </span>
              </div>
            )}
          </div>

          <div className="w-full pt-3 border-t border-slate-100 flex items-center justify-center gap-1 text-[11px] text-slate-500">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Escuela Secundaria Mixta 5</span>
          </div>
        </div>
      </div>
    </Card>
  );
};
