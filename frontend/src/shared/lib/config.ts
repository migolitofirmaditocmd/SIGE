/**
 * Configuración global del cliente frontend (PWA / SIGE).
 */

export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000",
  offlineBufferMaxEvents: 1000, // Límite de eventos de asistencia offline (RN-MOV-03)
  attendanceGraceMinutes: 15,
};
