/**
 * Feature: QR Codes (Identificación Criptográfica y Credenciales)
 * Responsabilidad: Emisión, revocación y exportación para impresión de credenciales y stickers.
 */

export interface QRCodeTokenInfo {
  token: string;
  entityType: "STUDENT" | "TEACHER";
  status: "ACTIVE" | "REVOKED" | "EXPIRED";
  issuedAt: string;
}
