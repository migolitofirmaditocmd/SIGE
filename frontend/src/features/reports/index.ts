/**
 * Feature: Reports (Incidencias y Reportes Escolares)
 * Responsabilidad: Registro por docentes, canalización por prefectura y revisión directiva.
 */

export type ReportSeverity = "LEVE" | "MODERADA" | "GRAVE";

export type ReportStatus =
  | "REGISTRADO"
  | "REVISADO_PREFECTO"
  | "CANALIZADO"
  | "REVISADO_ADMINISTRATIVO"
  | "RECHAZADO"
  | "AUTORIZADO"
  | "COMUNICADO"
  | "RESUELTO";
