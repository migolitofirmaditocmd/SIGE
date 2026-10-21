/**
 * Feature: Students (Estudiantes, Expedientes e Importación Masiva)
 * Responsabilidad: Gestión de expediente, validación de tutores e importación de lotes.
 */

export interface StudentSummary {
  id: string;
  enrollment_id: string;
  display_name: string;
  curp?: string;
  grade: number;
  group: string;
  shift: string;
  status: "ACTIVE" | "INACTIVE" | "GRADUATED" | "EXPELLED";
  completeness: "COMPLETO" | "INCOMPLETO";
}
