import { openDB, DBSchema, IDBPDatabase } from "idb";
import { config } from "../../lib/config";

/**
 * Esquema del buffer offline en IndexedDB (RN-MOV-02, RN-MOV-03).
 * Almacena únicamente metadatos opacos de escaneo sin datos personales de menores.
 */
export interface OfflineAttendanceEvent {
  client_event_id: string;   // UUIDv4 generado en el dispositivo
  qr_token: string;          // Token opaco escaneado de la credencial
  captured_at: string;       // Marca de tiempo ISO del dispositivo
  clock_offset_ms: number;   // Desfase entre reloj del servidor y cliente
  captured_by: string;       // ID del usuario prefecto autenticado
  sync_status: "PENDIENTE" | "ENVIANDO";
}

interface SigeOfflineDB extends DBSchema {
  offline_events: {
    key: string;
    value: OfflineAttendanceEvent;
    indexes: { "by-status": string; "by-captured-at": string };
  };
  metadata: {
    key: string;
    value: { key: string; value: unknown };
  };
}

const DB_NAME = "sige-offline";
const DB_VERSION = 1;

let dbPromise: Promise<IDBPDatabase<SigeOfflineDB>> | null = null;

export function getOfflineDB(): Promise<IDBPDatabase<SigeOfflineDB>> {
  if (!dbPromise) {
    dbPromise = openDB<SigeOfflineDB>(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains("offline_events")) {
          const store = db.createObjectStore("offline_events", { keyPath: "client_event_id" });
          store.createIndex("by-status", "sync_status");
          store.createIndex("by-captured-at", "captured_at");
        }
        if (!db.objectStoreNames.contains("metadata")) {
          db.createObjectStore("metadata", { keyPath: "key" });
        }
      },
    });
  }
  return dbPromise;
}

/**
 * Guarda un evento en el buffer offline con tope de 1,000 eventos (RN-MOV-03).
 */
export async function saveOfflineEvent(event: OfflineAttendanceEvent): Promise<void> {
  const db = await getOfflineDB();
  const count = await db.count("offline_events");
  
  if (count >= config.offlineBufferMaxEvents) {
    throw new Error(`Buffer offline lleno (límite de ${config.offlineBufferMaxEvents} eventos). Sincronice con la red escolar.`);
  }

  await db.put("offline_events", event);
}

/**
 * Obtiene el total de eventos pendientes de sincronizar.
 */
export async function getPendingEventsCount(): Promise<number> {
  const db = await getOfflineDB();
  return db.countFromIndex("offline_events", "by-status", "PENDIENTE");
}

/**
 * Recupera todos los eventos pendientes en orden de captura.
 */
export async function getPendingEvents(): Promise<OfflineAttendanceEvent[]> {
  const db = await getOfflineDB();
  return db.getAllFromIndex("offline_events", "by-status", "PENDIENTE");
}

/**
 * Elimina eventos confirmados por el backend tras sincronización exitosa.
 */
export async function removeSyncedEvents(clientEventIds: string[]): Promise<void> {
  const db = await getOfflineDB();
  const tx = db.transaction("offline_events", "readwrite");
  await Promise.all(clientEventIds.map((id) => tx.store.delete(id)));
  await tx.done;
}
