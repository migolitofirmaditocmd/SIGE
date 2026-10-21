import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { CheckCircle2, Clock, XCircle, FileText, Hourglass, MailCheck, AlertTriangle } from "lucide-react";

export type BadgeStatus =
  | "ASISTIO"
  | "LLEGO_TARDE"
  | "FALTO"
  | "FALTA_JUSTIFICADA"
  | "PENDIENTE"
  | "ENVIADO"
  | "FALLIDO"
  | "RECHAZADO"
  | "ACTIVO"
  | "INCOMPLETO";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  status: BadgeStatus;
  label?: string;
  size?: "sm" | "md";
}

const statusConfig: Record<
  BadgeStatus,
  { label: string; icon: React.ComponentType<{ className?: string }>; bg: string; text: string }
> = {
  ASISTIO: { label: "ASISTIÓ", icon: CheckCircle2, bg: "bg-[#DCF5E3]", text: "text-[#0B4A22]" },
  LLEGO_TARDE: { label: "LLEGÓ TARDE", icon: Clock, bg: "bg-[#FFEBC2]", text: "text-[#5C3200]" },
  FALTO: { label: "FALTÓ", icon: XCircle, bg: "bg-[#FDE4E4]", text: "text-[#7A0F0F]" },
  FALTA_JUSTIFICADA: { label: "FALTA JUSTIFICADA", icon: FileText, bg: "bg-[#DCEBFF]", text: "text-[#0A3D91]" },
  PENDIENTE: { label: "PENDIENTE", icon: Hourglass, bg: "bg-[#E9E4FA]", text: "text-[#3B2A7A]" },
  ENVIADO: { label: "ENVIADO", icon: MailCheck, bg: "bg-[#DCF5E3]", text: "text-[#0B4A22]" },
  FALLIDO: { label: "FALLIDO", icon: AlertTriangle, bg: "bg-[#FDE4E4]", text: "text-[#7A0F0F]" },
  RECHAZADO: { label: "RECHAZADO", icon: XCircle, bg: "bg-[#FDE4E4]", text: "text-[#7A0F0F]" },
  ACTIVO: { label: "ACTIVO", icon: CheckCircle2, bg: "bg-[#DCF5E3]", text: "text-[#0B4A22]" },
  INCOMPLETO: { label: "INCOMPLETO", icon: AlertTriangle, bg: "bg-[#FFEBC2]", text: "text-[#5C3200]" },
};

export const Badge: React.FC<BadgeProps> = ({ status, label, size = "md", className, ...props }) => {
  const config = statusConfig[status] || {
    label: status,
    icon: CheckCircle2,
    bg: "bg-[#E5E9EE]",
    text: "text-[#1F2937]",
  };

  const Icon = config.icon;
  const displayLabel = label || config.label;

  const sizeClasses = size === "sm" ? "text-xs px-2 py-0.5 gap-1" : "text-xs px-2.5 py-1 gap-1.5 font-medium";

  return (
    <span
      className={twMerge(
        clsx(
          "inline-flex items-center squircle-pill font-semibold tracking-wide border border-black/5 select-none",
          config.bg,
          config.text,
          sizeClasses,
          className
        )
      )}
      {...props}
    >
      <Icon className={size === "sm" ? "w-3.5 h-3.5" : "w-4 h-4"} />
      <span>{displayLabel}</span>
    </span>
  );
};
