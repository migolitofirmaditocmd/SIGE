"use client";

import React, { useState, useRef } from "react";
import { AcademicGroup, BatchPhotoUploadResponse, BatchPhotoResultItem } from "../types";
import { uploadBatchPhotos } from "../services";
import { Button, Badge } from "@/shared/ui";
import {
  Upload,
  X,
  FileImage,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  RefreshCw,
  FolderUp,
  Sparkles,
  Users,
  Check,
} from "lucide-react";

interface BatchPhotoUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedGroup?: AcademicGroup | null;
  onSuccess?: () => void;
}

export const BatchPhotoUploadModal: React.FC<BatchPhotoUploadModalProps> = ({
  isOpen,
  onClose,
  selectedGroup,
  onSuccess,
}) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [scope, setScope] = useState<"group" | "all">(selectedGroup ? "group" : "all");
  const [overwrite, setOverwrite] = useState<boolean>(true);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadResult, setUploadResult] = useState<BatchPhotoUploadResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  if (!isOpen) return null;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const filesArray = Array.from(e.target.files);
      setSelectedFiles(filesArray);
      setErrorMessage(null);
      setUploadResult(null);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArray = Array.from(e.dataTransfer.files);
      setSelectedFiles(filesArray);
      setErrorMessage(null);
      setUploadResult(null);
    }
  };

  const handleReset = () => {
    setSelectedFiles([]);
    setUploadResult(null);
    setErrorMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleStartUpload = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setErrorMessage(null);

    try {
      const options = {
        grade: scope === "group" && selectedGroup ? selectedGroup.grade : undefined,
        group: scope === "group" && selectedGroup ? selectedGroup.group_letter : undefined,
        shift: scope === "group" && selectedGroup ? selectedGroup.shift : undefined,
        overwrite,
      };

      const response = await uploadBatchPhotos(selectedFiles, options);
      setUploadResult(response);
      if (onSuccess) {
        onSuccess();
      }
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : "Error inesperado al procesar las fotografías"
      );
    } finally {
      setIsUploading(false);
    }
  };

  const handleFinish = () => {
    handleReset();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Cabecera del Modal */}
        <div className="bg-[#0A3D91] text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-white/10 rounded-xl">
              <FolderUp className="w-5 h-5 text-blue-200" />
            </div>
            <div>
              <h2 className="text-base font-bold tracking-tight">
                Carga Masiva de Fotografías por Lote
              </h2>
              <p className="text-xs text-blue-200">
                Alineado con especificación institucional (US-064 · RN-EST-15/16)
              </p>
            </div>
          </div>
          <button
            onClick={uploadResult ? handleFinish : onClose}
            disabled={isUploading}
            className="p-1 rounded-lg text-white/80 hover:text-white hover:bg-white/10 transition-colors disabled:opacity-50"
            title="Cerrar ventana"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Contenido Dinámico */}
        <div className="p-6 overflow-y-auto flex-1 space-y-5">
          {!uploadResult ? (
            <>
              {/* Instrucción clara */}
              <div className="bg-blue-50/80 border border-blue-200 rounded-xl p-3.5 text-xs text-blue-900 flex items-start gap-2.5">
                <Sparkles className="w-4 h-4 text-[#0A3D91] shrink-0 mt-0.5" />
                <div>
                  <p className="font-semibold">Vinculación Automática por Nombre de Archivo</p>
                  <p className="text-blue-800/90 mt-0.5">
                    Puedes seleccionar todas las fotos juntas o un archivo ZIP. El sistema identificará 
                    automáticamente a qué alumno corresponde cada fotografía según el nombre del archivo, 
                    eliminará metadatos EXIF por privacidad de menores y guardará la imagen en la base de datos.
                  </p>
                </div>
              </div>

              {/* Zona de Selección / Drag and Drop */}
              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={() => !isUploading && fileInputRef.current?.click()}
                className={`border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
                  dragActive
                    ? "border-[#0A3D91] bg-blue-50/60 scale-[0.99]"
                    : selectedFiles.length > 0
                    ? "border-emerald-400 bg-emerald-50/30"
                    : "border-slate-300 hover:border-[#0A3D91] hover:bg-slate-50/80"
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/jpeg,image/png,image/webp,.zip"
                  onChange={handleFileChange}
                  className="hidden"
                  disabled={isUploading}
                />

                <div className="flex flex-col items-center gap-2">
                  <div
                    className={`p-3 rounded-full ${
                      selectedFiles.length > 0
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-blue-100 text-[#0A3D91]"
                    }`}
                  >
                    {selectedFiles.length > 0 ? (
                      <Check className="w-6 h-6" />
                    ) : (
                      <Upload className="w-6 h-6" />
                    )}
                  </div>

                  {selectedFiles.length > 0 ? (
                    <div>
                      <p className="text-sm font-bold text-slate-800">
                        {selectedFiles.length} {selectedFiles.length === 1 ? "archivo seleccionado" : "archivos seleccionados"}
                      </p>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Haz clic aquí si deseas elegir otros archivos
                      </p>
                    </div>
                  ) : (
                    <div>
                      <p className="text-sm font-bold text-slate-800">
                        Haz clic para seleccionar las fotos o arrástralas aquí
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        Formatos soportados: JPG, PNG, WEBP o archivo .ZIP comprimido
                      </p>
                    </div>
                  )}
                </div>
              </div>

              {/* Vista previa de archivos seleccionados */}
              {selectedFiles.length > 0 && (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 max-h-36 overflow-y-auto text-xs space-y-1">
                  <div className="flex items-center justify-between font-semibold text-slate-700 pb-1 border-b border-slate-200">
                    <span>Lista de archivos a procesar ({selectedFiles.length}):</span>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleReset();
                      }}
                      className="text-red-600 hover:underline text-[11px]"
                    >
                      Limpiar selección
                    </button>
                  </div>
                  {selectedFiles.slice(0, 10).map((file, idx) => (
                    <div key={idx} className="flex items-center gap-1.5 text-slate-600 truncate">
                      <FileImage className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate">{file.name}</span>
                      <span className="text-slate-400 text-[10px] shrink-0">
                        ({(file.size / 1024).toFixed(0)} KB)
                      </span>
                    </div>
                  ))}
                  {selectedFiles.length > 10 && (
                    <p className="text-slate-400 italic text-center pt-1 text-[11px]">
                      ... y {selectedFiles.length - 10} archivos más
                    </p>
                  )}
                </div>
              )}

              {/* Configuración de alcance */}
              <div className="space-y-3 pt-2 border-t border-slate-200">
                <label className="text-xs font-bold text-slate-700 block">
                  Alcance de coincidencia para la búsqueda de alumnos:
                </label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  {selectedGroup && (
                    <label
                      className={`flex items-center gap-2 p-2.5 rounded-xl border cursor-pointer transition-all ${
                        scope === "group"
                          ? "border-[#0A3D91] bg-blue-50/50 text-[#0A3D91] font-semibold"
                          : "border-slate-200 hover:bg-slate-50 text-slate-700"
                      }`}
                    >
                      <input
                        type="radio"
                        name="scope"
                        checked={scope === "group"}
                        onChange={() => setScope("group")}
                        className="text-[#0A3D91] focus:ring-[#0A3D91]"
                      />
                      <span>Priorizar grupo actual: {selectedGroup.display_name}</span>
                    </label>
                  )}
                  <label
                    className={`flex items-center gap-2 p-2.5 rounded-xl border cursor-pointer transition-all ${
                      scope === "all"
                        ? "border-[#0A3D91] bg-blue-50/50 text-[#0A3D91] font-semibold"
                        : "border-slate-200 hover:bg-slate-50 text-slate-700"
                    }`}
                  >
                    <input
                      type="radio"
                      name="scope"
                      checked={scope === "all"}
                      onChange={() => setScope("all")}
                      className="text-[#0A3D91] focus:ring-[#0A3D91]"
                    />
                    <span>Buscar en todo el plantel (todos los grupos)</span>
                  </label>
                </div>

                {/* Opción de sobreescritura */}
                <label className="flex items-center gap-2 text-xs text-slate-700 cursor-pointer pt-1">
                  <input
                    type="checkbox"
                    checked={overwrite}
                    onChange={(e) => setOverwrite(e.target.checked)}
                    className="rounded border-slate-300 text-[#0A3D91] focus:ring-[#0A3D91]"
                  />
                  <span>Actualizar fotografía incluso si el alumno ya tiene una guardada previamente</span>
                </label>
              </div>

              {/* Mensaje de error general si ocurre */}
              {errorMessage && (
                <div className="bg-red-50 border border-red-200 text-red-800 text-xs p-3 rounded-xl flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
                  <span>{errorMessage}</span>
                </div>
              )}
            </>
          ) : (
            /* Vista de Resultados post-procesamiento */
            <div className="space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                <div className="bg-slate-100 p-2.5 rounded-xl border border-slate-200">
                  <p className="text-xl font-bold text-slate-800">{uploadResult.total_received}</p>
                  <p className="text-[11px] text-slate-500 font-medium">Recibidas</p>
                </div>
                <div className="bg-emerald-50 p-2.5 rounded-xl border border-emerald-200">
                  <p className="text-xl font-bold text-emerald-700">{uploadResult.updated_count}</p>
                  <p className="text-[11px] text-emerald-600 font-medium">Vinculadas</p>
                </div>
                <div className="bg-blue-50 p-2.5 rounded-xl border border-blue-200">
                  <p className="text-xl font-bold text-blue-700">{uploadResult.skipped_count}</p>
                  <p className="text-[11px] text-blue-600 font-medium">Conservadas</p>
                </div>
                <div className="bg-amber-50 p-2.5 rounded-xl border border-amber-200">
                  <p className="text-xl font-bold text-amber-700">{uploadResult.unmatched_count}</p>
                  <p className="text-[11px] text-amber-600 font-medium">Sin coincidencia</p>
                </div>
              </div>

              {/* Detalle fila por fila */}
              <div className="border border-slate-200 rounded-xl overflow-hidden">
                <div className="bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 flex justify-between">
                  <span>Detalle de vinculación por archivo</span>
                  <span className="text-slate-500 font-normal">
                    {uploadResult.matched_count} de {uploadResult.total_received} identificados
                  </span>
                </div>
                <div className="max-h-60 overflow-y-auto divide-y divide-slate-100 text-xs">
                  {uploadResult.results.map((item: BatchPhotoResultItem, idx: number) => (
                    <div
                      key={idx}
                      className={`p-2.5 flex items-center justify-between gap-3 ${
                        item.status === "SUCCESS"
                          ? "bg-white hover:bg-slate-50"
                          : item.status === "SKIPPED"
                          ? "bg-blue-50/20 hover:bg-blue-50/40"
                          : "bg-amber-50/30 hover:bg-amber-50/50"
                      }`}
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        {item.status === "SUCCESS" ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
                        ) : item.status === "SKIPPED" ? (
                          <Check className="w-4 h-4 text-blue-600 shrink-0" />
                        ) : (
                          <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
                        )}
                        <div className="truncate">
                          <p className="font-semibold text-slate-800 truncate">
                            {item.filename}
                          </p>
                          <p className="text-[11px] text-slate-500 truncate">
                            {item.student_name ? (
                              <span>
                                {item.student_name} · <span className="font-medium text-slate-700">{item.group}</span>
                              </span>
                            ) : (
                              <span className="text-amber-700">{item.message}</span>
                            )}
                          </p>
                        </div>
                      </div>

                      <div className="shrink-0">
                        {item.status === "SUCCESS" && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-100 text-emerald-800">
                            Guardada
                          </span>
                        )}
                        {item.status === "SKIPPED" && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-blue-100 text-blue-800">
                            Conservada
                          </span>
                        )}
                        {item.status === "UNMATCHED" && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-amber-100 text-amber-800">
                            No coincide
                          </span>
                        )}
                        {item.status === "ERROR" && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-semibold bg-red-100 text-red-800">
                            Error
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Barra de Acciones Inferior */}
        <div className="bg-slate-50 px-6 py-3 border-t border-slate-200 flex items-center justify-between">
          {!uploadResult ? (
            <>
              <button
                type="button"
                onClick={onClose}
                disabled={isUploading}
                className="text-xs text-slate-600 hover:text-slate-900 font-medium disabled:opacity-50"
              >
                Cancelar
              </button>
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleStartUpload}
                  disabled={selectedFiles.length === 0 || isUploading}
                  variant="primary"
                  size="sm"
                  className="bg-[#0A3D91] hover:bg-[#082E6E] text-white flex items-center gap-1.5"
                >
                  {isUploading ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Procesando fotos ({selectedFiles.length})...</span>
                    </>
                  ) : (
                    <>
                      <Upload className="w-3.5 h-3.5" />
                      <span>Subir y Vincular ({selectedFiles.length})</span>
                    </>
                  )}
                </Button>
              </div>
            </>
          ) : (
            <div className="w-full flex justify-end">
              <Button
                onClick={handleFinish}
                variant="primary"
                size="sm"
                className="bg-[#0A3D91] hover:bg-[#082E6E] text-white"
              >
                Finalizar y Actualizar Vista
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
