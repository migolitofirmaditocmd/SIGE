/* eslint-disable @next/next/no-img-element */
"use client";

import React, { useState, useRef } from "react";
import { Student } from "../types";
import {
  deleteStudentPhoto,
  downloadStudentCredentialPdf,
  getQrImageUrl,
  getStudentPhotoUrl,
  uploadStudentPhoto,
} from "../services";
import { Badge, Card, Button } from "@/shared/ui";
import {
  User,
  QrCode,
  Phone,
  MapPin,
  HeartPulse,
  CheckCircle2,
  Camera,
  Upload,
  Loader2,
  AlertTriangle,
  Trash2,
  FileDown,
  Mail,
  IdCard,
  Pencil,
  Crop,
} from "lucide-react";
import { EditStudentModal } from "./EditStudentModal";
import { PhotoCropModal } from "./PhotoCropModal";

interface StudentDetailCardProps {
  student: Student;
  onClose?: () => void;
  onStudentUpdated?: (updated: Student) => void;
}

export const StudentDetailCard: React.FC<StudentDetailCardProps> = ({
  student,
  onClose,
  onStudentUpdated,
}) => {
  const [photoTimestamp, setPhotoTimestamp] = useState<number>(0);
  const [hasPhoto, setHasPhoto] = useState<boolean>(Boolean(student.photo_url));
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);
  const [isDownloadingPdf, setIsDownloadingPdf] = useState<boolean>(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState<boolean>(false);
  const [isCropModalOpen, setIsCropModalOpen] = useState<boolean>(false);
  const [cropImageSrc, setCropImageSrc] = useState<string>("");
  const [selectedRawFile, setSelectedRawFile] = useState<File | undefined>(undefined);
  const [uploadMessage, setUploadMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const primaryGuardian =
    student.guardians.find((g) => g.is_primary_contact) ||
    student.guardians[0];

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  /** Elimina la fotografía del estudiante previa confirmación del usuario. */
  const handleDeletePhoto = async () => {
    if (
      !window.confirm(
        `¿Eliminar la fotografía de ${student.display_name}?\n\nEsta acción no se puede deshacer.`
      )
    ) {
      return;
    }
    try {
      setIsDeleting(true);
      setUploadMessage(null);
      await deleteStudentPhoto(student.id);
      setHasPhoto(false);
      setPhotoTimestamp(0);
      setUploadMessage({ type: "success", text: "Fotografía eliminada correctamente." });
      if (onStudentUpdated) {
        onStudentUpdated({
          ...student,
          photo_url: null,
          completeness: "INCOMPLETO",
          updated_at: new Date().toISOString(),
        });
      }
    } catch (err: unknown) {
      setUploadMessage({
        type: "error",
        text: err instanceof Error ? err.message : "Error al eliminar la fotografía.",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  /** Descarga la credencial PDF individual del estudiante. */
  const handleDownloadCredentialPdf = async () => {
    try {
      setIsDownloadingPdf(true);
      setUploadMessage(null);
      const blob = await downloadStudentCredentialPdf(student.id);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `credencial_${student.enrollment_id}_${student.last_name_father}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err: unknown) {
      setUploadMessage({
        type: "error",
        text: err instanceof Error ? err.message : "Error al generar la credencial PDF.",
      });
    } finally {
      setIsDownloadingPdf(false);
    }
  };

  /** Abre el modal de recorte con un archivo nuevo seleccionado por el usuario. */
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validar tipo en el cliente
    if (!["image/jpeg", "image/png"].includes(file.type)) {
      setUploadMessage({
        type: "error",
        text: "Solo se permiten imágenes en formato JPEG o PNG.",
      });
      return;
    }

    // Guardar referencia al archivo original para persistirlo en el backend
    setSelectedRawFile(file);

    const reader = new FileReader();
    reader.onload = (event) => {
      const src = event.target?.result as string;
      if (src) {
        setCropImageSrc(src);
        setIsCropModalOpen(true);
      }
    };
    reader.readAsDataURL(file);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  /** Abre el modal de recorte manual usando la fotografía original (sin recortar) del alumno. */
  const handleOpenCropCurrentPhoto = () => {
    // Pedir la foto original con original=true para que el encuadre se realice sobre la toma completa
    const src = getStudentPhotoUrl(student.id, photoTimestamp || Date.now(), true);
    setSelectedRawFile(undefined);
    setCropImageSrc(src);
    setIsCropModalOpen(true);
  };

  /** Callback ejecutado cuando el usuario guarda su recorte manual. */
  const handleCropSuccess = (newPhotoUrl: string, newTimestamp: number) => {
    setPhotoTimestamp(newTimestamp);
    setHasPhoto(true);
    setUploadMessage({
      type: "success",
      text: "Fotografía y encuadre guardados exitosamente.",
    });

    if (onStudentUpdated) {
      onStudentUpdated({
        ...student,
        photo_url: newPhotoUrl,
        completeness: "COMPLETO",
        updated_at: new Date(newTimestamp).toISOString(),
      });
    }
  };

  const photoSrc = hasPhoto
    ? getStudentPhotoUrl(student.id, photoTimestamp)
    : null;

  return (
    <Card className="bg-white border-[#0A3D91]/20 shadow-md p-6 flex flex-col gap-6">
      {/* Input oculto para carga de fotografía */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Encabezado: Foto / Placeholder con botón de carga, Nombre, Matrícula y Estatus */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-5 border-b border-slate-200">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
          {/* Fotografía o Placeholder + Botón de Carga */}
          <div className="flex flex-col items-center gap-2 shrink-0">
            <div className="relative">
              {photoSrc ? (
                <img
                  src={photoSrc}
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

              {/* Botón flotante rápido sobre la imagen */}
              <button
                onClick={handleUploadClick}
                disabled={isUploading || isDeleting}
                title={hasPhoto ? "Cambiar fotografía" : "Cargar fotografía oficial"}
                className="absolute -bottom-1.5 -right-1.5 w-7 h-7 bg-[#0A3D91] hover:bg-[#072B68] text-white rounded-full flex items-center justify-center shadow-md border-2 border-white transition-all disabled:opacity-50"
              >
                {isUploading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Camera className="w-3.5 h-3.5" />
                )}
              </button>
            </div>

            {/* Botones de foto: Cargar/Cambiar, Ajustar Encuadre y Eliminar */}
            <div className="flex items-center gap-1.5 flex-wrap justify-center">
              <Button
                variant="outline"
                size="sm"
                onClick={handleUploadClick}
                disabled={isUploading || isDeleting}
                className="h-7 px-2 text-[11px] font-semibold text-[#0A3D91] border-[#0A3D91]/30 hover:bg-blue-50"
              >
                {isUploading ? (
                  <>
                    <Loader2 className="w-3 h-3 animate-spin mr-1" />
                    <span>Guardando...</span>
                  </>
                ) : hasPhoto ? (
                  <>
                    <Camera className="w-3 h-3 mr-1" />
                    <span>Cambiar</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-3 h-3 mr-1" />
                    <span>Cargar</span>
                  </>
                )}
              </Button>

              {/* Botón de ajuste manual de recorte y encuadre */}
              {hasPhoto && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleOpenCropCurrentPhoto}
                  disabled={isUploading || isDeleting}
                  title="Ajustar manualmente el encuadre, zoom y rotación de la fotografía"
                  className="h-7 px-2 text-[11px] font-semibold text-slate-700 border-slate-300 hover:bg-slate-100 flex items-center gap-1"
                >
                  <Crop className="w-3 h-3 text-[#0A3D91]" />
                  <span>Ajustar</span>
                </Button>
              )}

              {/* Botón eliminar foto (solo visible si hay foto) */}
              {hasPhoto && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDeletePhoto}
                  disabled={isDeleting || isUploading}
                  title="Eliminar fotografía del estudiante"
                  className="h-7 px-2 text-[11px] font-semibold text-red-600 border-red-200 hover:bg-red-50"
                >
                  {isDeleting ? (
                    <Loader2 className="w-3 h-3 animate-spin" />
                  ) : (
                    <Trash2 className="w-3 h-3" />
                  )}
                </Button>
              )}
            </div>
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

            {/* CURP prominente */}
            {student.curp && (
              <div className="flex items-center gap-1.5 mt-1">
                <IdCard className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <p className="text-xs text-slate-500">
                  CURP:{" "}
                  <span className="font-mono font-semibold text-slate-700 tracking-wide">
                    {student.curp}
                  </span>
                </p>
              </div>
            )}

            {/* Correo institucional */}
            {student.institutional_email && (
              <div className="flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                <p className="text-xs text-slate-500">
                  Correo:{" "}
                  <a
                    href={`mailto:${student.institutional_email}`}
                    className="font-medium text-[#0A3D91] hover:underline"
                  >
                    {student.institutional_email}
                  </a>
                </p>
              </div>
            )}

            {/* Mensaje de estado de subida / eliminación */}
            {uploadMessage && (
              <div
                className={`mt-2 text-xs font-semibold px-2.5 py-1 rounded-lg flex items-center gap-1.5 ${
                  uploadMessage.type === "success"
                    ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                    : "bg-red-50 text-red-800 border border-red-200"
                }`}
              >
                {uploadMessage.type === "success" ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                ) : (
                  <AlertTriangle className="w-3.5 h-3.5 text-red-600 shrink-0" />
                )}
                <span>{uploadMessage.text}</span>
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2 self-start sm:self-auto flex-wrap">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsEditModalOpen(true)}
            className="h-8 px-3 text-xs font-semibold text-[#0A3D91] border-[#0A3D91]/30 hover:bg-blue-50 flex items-center gap-1.5 shadow-2xs"
            title="Editar datos personales, escolares, médicos o tutor del alumno"
          >
            <Pencil className="w-3.5 h-3.5" />
            <span>Editar información</span>
          </Button>

          {onClose && (
            <button
              onClick={onClose}
              className="text-xs font-semibold text-slate-500 hover:text-slate-800 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors"
            >
              Cerrar ficha
            </button>
          )}
        </div>
      </div>

      {/* Modal para editar información del estudiante */}
      <EditStudentModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        student={student}
        onStudentUpdated={(updated) => {
          if (onStudentUpdated) {
            onStudentUpdated(updated);
          }
        }}
      />

      {/* Modal para ajuste manual de encuadre, zoom y recorte de fotografía sobre toma original */}
      <PhotoCropModal
        isOpen={isCropModalOpen}
        onClose={() => setIsCropModalOpen(false)}
        imageSrc={cropImageSrc}
        studentId={student.id}
        studentName={student.display_name}
        rawFile={selectedRawFile}
        onSuccess={handleCropSuccess}
      />

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
              <div className="w-48 p-4 rounded-xl border-2 border-dashed border-amber-300 bg-amber-50/70 flex flex-col items-center justify-center text-center space-y-2.5">
                <div className="p-2.5 bg-amber-100 rounded-full text-amber-700">
                  <QrCode className="w-8 h-8" />
                </div>
                <div>
                  <span className="text-xs font-bold text-amber-900 block">
                    QR Pendiente
                  </span>
                  <p className="text-[11px] text-amber-800 leading-snug mt-1 font-medium">
                    Si quieres tener el código QR, debes subir la fotografía del alumno.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleUploadClick}
                  disabled={isUploading}
                  className="mt-1 inline-flex items-center gap-1.5 px-3 py-1.5 bg-[#0A3D91] hover:bg-[#072B68] text-white rounded-lg text-xs font-semibold shadow-xs transition-colors disabled:opacity-50"
                  title="Cargar fotografía para generar el código QR"
                >
                  <Camera className="w-3.5 h-3.5" />
                  <span>Subir fotografía</span>
                </button>
              </div>
            )}
          </div>

          <div className="w-full pt-3 border-t border-slate-100 flex flex-col items-center gap-2">
            {/* Botón credencial PDF individual — solo si tiene foto */}
            {hasPhoto ? (
              student.active_qr_token_id ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleDownloadCredentialPdf}
                  disabled={isDownloadingPdf}
                  className="w-full h-8 text-[11px] font-semibold text-[#0A3D91] border-[#0A3D91]/30 hover:bg-blue-50 flex items-center justify-center gap-1.5"
                  title="Generar y descargar la credencial escolar en PDF"
                >
                  {isDownloadingPdf ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      <span>Generando PDF...</span>
                    </>
                  ) : (
                    <>
                      <FileDown className="w-3.5 h-3.5" />
                      <span>Descargar Credencial PDF</span>
                    </>
                  )}
                </Button>
              ) : (
                /* Tiene foto pero QR aún no se generó (caso edge) */
                <div className="w-full flex items-start gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 text-left">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-600 shrink-0 mt-0.5" />
                  <p className="text-[10px] text-amber-800 font-medium leading-snug">
                    El código QR aún no se ha generado. Recarga la ficha e inténtalo de nuevo.
                  </p>
                </div>
              )
            ) : (
              /* Sin foto — bloquear generación de credencial con aviso claro */
              <div className="w-full flex flex-col items-center gap-2">
                <div className="w-full flex items-start gap-2 bg-orange-50 border border-orange-200 rounded-lg px-3 py-2 text-left">
                  <AlertTriangle className="w-3.5 h-3.5 text-orange-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="text-[10px] text-orange-900 font-bold leading-snug">
                      Falta la fotografía
                    </p>
                    <p className="text-[10px] text-orange-800 leading-snug mt-0.5">
                      Para generar la credencial es obligatorio subir primero la fotografía del alumno.
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={handleUploadClick}
                  disabled={isUploading}
                  className="w-full inline-flex items-center justify-center gap-1.5 h-8 px-3 bg-[#0A3D91] hover:bg-[#072B68] text-white rounded-lg text-[11px] font-semibold shadow-xs transition-colors disabled:opacity-50"
                >
                  <Camera className="w-3.5 h-3.5" />
                  <span>Subir foto para generar credencial</span>
                </button>
              </div>
            )}

            <div className="flex items-center gap-1 text-[11px] text-slate-500">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>Escuela Secundaria Mixta 5</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
