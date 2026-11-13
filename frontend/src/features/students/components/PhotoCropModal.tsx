"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { uploadStudentPhoto } from "../services";
import { Button } from "@/shared/ui";
import {
  X,
  ZoomIn,
  ZoomOut,
  RotateCw,
  Crop,
  Check,
  Loader2,
  AlertTriangle,
  Move,
  RefreshCcw,
} from "lucide-react";

interface PhotoCropModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageSrc: string;
  studentId: string;
  studentName: string;
  rawFile?: File;
  onSuccess: (newPhotoUrl: string, timestamp: number) => void;
}

const VIEW_BOX_SIZE = 320; // Tamaño del visor cuadrado en px
const OUTPUT_SIZE = 800; // Resolución final cuadrada almacenada en px

export const PhotoCropModal: React.FC<PhotoCropModalProps> = ({
  isOpen,
  onClose,
  imageSrc,
  studentId,
  studentName,
  rawFile,
  onSuccess,
}) => {
  const [zoom, setZoom] = useState<number>(1.0);
  const [rotation, setRotation] = useState<number>(0); // 0, 90, 180, 270
  const [offset, setOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const imgRef = useRef<HTMLImageElement | null>(null);
  const [naturalSize, setNaturalSize] = useState<{ w: number; h: number }>({ w: 0, h: 0 });

  // Restablecer estados al abrir con una nueva imagen
  useEffect(() => {
    if (isOpen) {
      setZoom(1.0);
      setRotation(0);
      setOffset({ x: 0, y: 0 });
      setErrorMessage(null);
    }
  }, [isOpen, imageSrc]);

  // Al cargar la imagen en memoria
  const handleImageLoaded = (e: React.SyntheticEvent<HTMLImageElement>) => {
    const img = e.currentTarget;
    setNaturalSize({ w: img.naturalWidth, h: img.naturalHeight });
  };

  // Calcular la escala base para que la imagen cubra el visor (modo cover)
  const isRotated90or270 = rotation === 90 || rotation === 270;
  const effectiveW = isRotated90or270 ? naturalSize.h : naturalSize.w;
  const effectiveH = isRotated90or270 ? naturalSize.w : naturalSize.h;

  const baseScale =
    effectiveW > 0 && effectiveH > 0
      ? Math.max(VIEW_BOX_SIZE / effectiveW, VIEW_BOX_SIZE / effectiveH)
      : 1;

  const currentScale = baseScale * zoom;

  // Manejo de arrastre (Pan) con Mouse
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
    setDragStart({ x: e.clientX - offset.x, y: e.clientY - offset.y });
  };

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isDragging) return;
      setOffset({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    },
    [isDragging, dragStart]
  );

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Manejo de arrastre (Touch) para pantallas táctiles
  const handleTouchStart = (e: React.TouchEvent) => {
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      setIsDragging(true);
      setDragStart({ x: touch.clientX - offset.x, y: touch.clientY - offset.y });
    }
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging || e.touches.length !== 1) return;
    const touch = e.touches[0];
    setOffset({
      x: touch.clientX - dragStart.x,
      y: touch.clientY - dragStart.y,
    });
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
  };

  // Zoom con la rueda del ratón
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomDelta = e.deltaY < 0 ? 0.08 : -0.08;
    setZoom((prev) => Math.min(4.0, Math.max(0.5, prev + zoomDelta)));
  };

  // Rotar 90 grados a la derecha
  const handleRotate = () => {
    setRotation((prev) => (prev + 90) % 360);
    setOffset({ x: 0, y: 0 }); // recentrar al rotar
  };

  // Restablecer encuadre
  const handleReset = () => {
    setZoom(1.0);
    setRotation(0);
    setOffset({ x: 0, y: 0 });
  };

  // Guardar recorte exportando desde un canvas oculto a 800x800 px
  const handleSaveCrop = async () => {
    if (!imgRef.current || naturalSize.w === 0 || naturalSize.h === 0) return;

    try {
      setIsSaving(true);
      setErrorMessage(null);

      const canvas = document.createElement("canvas");
      canvas.width = OUTPUT_SIZE;
      canvas.height = OUTPUT_SIZE;
      const ctx = canvas.getContext("2d");

      if (!ctx) {
        throw new Error("No se pudo inicializar el lienzo de recorte gráfico.");
      }

      // Fondo blanco puro
      ctx.fillStyle = "#FFFFFF";
      ctx.fillRect(0, 0, OUTPUT_SIZE, OUTPUT_SIZE);

      // Factor de conversión entre el visor en pantalla y la resolución final
      const screenToCanvasFactor = OUTPUT_SIZE / VIEW_BOX_SIZE;

      // Trasladar al centro del lienzo + offset del usuario (en orden idéntico al CSS)
      const renderOffsetX = offset.x * screenToCanvasFactor;
      const renderOffsetY = offset.y * screenToCanvasFactor;
      ctx.translate(OUTPUT_SIZE / 2 + renderOffsetX, OUTPUT_SIZE / 2 + renderOffsetY);

      // Aplicar rotación
      ctx.rotate((rotation * Math.PI) / 180);

      // Dibujar la imagen centrada con su escala
      const renderScale = currentScale * screenToCanvasFactor;
      const drawW = naturalSize.w * renderScale;
      const drawH = naturalSize.h * renderScale;

      ctx.drawImage(imgRef.current, -drawW / 2, -drawH / 2, drawW, drawH);

      // Convertir a Blob JPEG de alta calidad
      const blob = await new Promise<Blob | null>((resolve) => {
        canvas.toBlob((b) => resolve(b), "image/jpeg", 0.93);
      });

      if (!blob) {
        throw new Error("Error al generar la imagen recortada.");
      }

      // Crear archivo para upload preservando también el original si se subió uno nuevo
      const file = new File([blob], `${studentId}.jpg`, { type: "image/jpeg" });
      const result = await uploadStudentPhoto(studentId, file, true, rawFile);

      // Notificar éxito al componente padre
      onSuccess(result.photo_url, Date.now());
      onClose();
    } catch (err: unknown) {
      console.error(err);
      setErrorMessage(
        err instanceof Error ? err.message : "Error al guardar el ajuste de fotografía."
      );
    } finally {
      setIsSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/70 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-lg flex flex-col overflow-hidden">
        {/* Cabecera */}
        <div className="px-5 py-3.5 bg-gradient-to-r from-blue-900 to-[#0A3D91] text-white flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center">
              <Crop className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-sm leading-tight">
                Ajustar Encuadre de Fotografía
              </h3>
              <p className="text-[11px] text-blue-200">
                {studentName} · Encuadre sobre toma original
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isSaving}
            className="w-7 h-7 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Mensaje de error si falla */}
        {errorMessage && (
          <div className="mx-5 mt-3 p-2.5 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2 text-xs text-red-800">
            <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Contenedor central de trabajo */}
        <div className="p-5 flex flex-col items-center gap-4">
          <p className="text-xs text-slate-500 text-center leading-relaxed max-w-sm">
            Arrastra la imagen para centrar los hombros y la cabeza. Usa el control
            inferior o la rueda del ratón para ajustar el zoom.
          </p>

          {/* Visor interactivo con máscara cuadrada 1:1 */}
          <div
            className="relative w-[320px] h-[320px] rounded-2xl overflow-hidden bg-slate-900 border-2 border-[#0A3D91] shadow-inner select-none cursor-grab active:cursor-grabbing"
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            onTouchStart={handleTouchStart}
            onTouchMove={handleTouchMove}
            onTouchEnd={handleTouchEnd}
            onWheel={handleWheel}
          >
            {/* Imagen manipulada */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              ref={imgRef}
              src={imageSrc}
              alt="Ajuste de fotografía"
              crossOrigin="anonymous"
              onLoad={handleImageLoaded}
              draggable={false}
              className="absolute pointer-events-none select-none max-w-none origin-center transition-transform duration-75 ease-out"
              style={{
                left: "50%",
                top: "50%",
                transform: `translate(-50%, -50%) translate(${offset.x}px, ${offset.y}px) rotate(${rotation}deg) scale(${currentScale})`,
              }}
            />

            {/* Guías de ayuda visual (regla de los tercios y marco del visor) */}
            <div className="absolute inset-0 pointer-events-none border border-white/30 rounded-2xl">
              {/* Líneas horizontales de tercio */}
              <div className="absolute left-0 right-0 top-1/3 border-b border-white/20 border-dashed" />
              <div className="absolute left-0 right-0 top-2/3 border-b border-white/20 border-dashed" />
              {/* Líneas verticales de tercio */}
              <div className="absolute top-0 bottom-0 left-1/3 border-r border-white/20 border-dashed" />
              <div className="absolute top-0 bottom-0 left-2/3 border-r border-white/20 border-dashed" />
            </div>

            {/* Badge flotante de ayuda */}
            <div className="absolute bottom-2 left-2 bg-black/60 backdrop-blur-xs text-white text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1 pointer-events-none">
              <Move className="w-3 h-3 text-blue-300" />
              <span>Arrastrar para mover</span>
            </div>
          </div>

          {/* Controles de Zoom y Rotación */}
          <div className="w-full max-w-xs space-y-3">
            {/* Barra de Zoom (rango extendido 0.5x - 4.0x para máximo control) */}
            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setZoom((z) => Math.max(0.5, z - 0.1))}
                className="p-1 rounded-md text-slate-600 hover:bg-slate-100 transition-colors"
                title="Reducir zoom"
              >
                <ZoomOut className="w-4 h-4" />
              </button>

              <input
                type="range"
                min="0.5"
                max="4.0"
                step="0.05"
                value={zoom}
                onChange={(e) => setZoom(parseFloat(e.target.value))}
                className="flex-1 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#0A3D91]"
              />

              <button
                type="button"
                onClick={() => setZoom((z) => Math.min(4.0, z + 0.1))}
                className="p-1 rounded-md text-slate-600 hover:bg-slate-100 transition-colors"
                title="Aumentar zoom"
              >
                <ZoomIn className="w-4 h-4" />
              </button>

              <span className="text-xs font-mono font-bold text-slate-700 w-10 text-right">
                {zoom.toFixed(1)}x
              </span>
            </div>

            {/* Botones de acción rápida: Rotar 90° y Restablecer */}
            <div className="flex items-center justify-between text-xs">
              <button
                type="button"
                onClick={handleRotate}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 text-slate-700 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors font-semibold"
                title="Girar 90 grados a la derecha"
              >
                <RotateCw className="w-3.5 h-3.5" />
                <span>Girar 90°</span>
              </button>

              <button
                type="button"
                onClick={handleReset}
                className="inline-flex items-center gap-1.5 px-2.5 py-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg transition-colors"
                title="Restablecer posición y zoom originales"
              >
                <RefreshCcw className="w-3.5 h-3.5" />
                <span>Restablecer</span>
              </button>
            </div>
          </div>
        </div>

        {/* Pie con botones de acción */}
        <div className="px-5 py-3.5 bg-slate-50 border-t border-slate-200 flex items-center justify-end gap-2.5">
          <Button
            type="button"
            variant="outline"
            size="sm"
            disabled={isSaving}
            onClick={onClose}
            className="text-xs"
          >
            Cancelar
          </Button>

          <Button
            type="button"
            size="sm"
            disabled={isSaving}
            onClick={handleSaveCrop}
            className="bg-[#0A3D91] hover:bg-[#072B68] text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm"
          >
            {isSaving ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Guardando recorte...</span>
              </>
            ) : (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>Aplicar y Guardar</span>
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
};

