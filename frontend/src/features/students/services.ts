/**
 * Servicios de comunicación HTTP con la API REST de SIGE Backend.
 */

import {
  AcademicGroup,
  BatchPhotoUploadResponse,
  GuardianContact,
  GuardianUpdatePayload,
  PaginatedResponse,
  Student,
  StudentCreatePayload,
  StudentDeleteResponse,
  StudentUpdatePayload,
} from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

/**
 * Obtiene la lista de grupos académicos con el conteo de estudiantes matriculados.
 */
export async function fetchGroups(): Promise<AcademicGroup[]> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/students/groups/`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`Error ${res.status} al cargar grupos académicos`);
    }
    return await res.json();
  } catch (error) {
    console.error("fetchGroups error:", error);
    throw error;
  }
}

/**
 * Realiza búsqueda de estudiantes por nombre, matrícula o CURP.
 */
export async function searchStudents(query: string): Promise<Student[]> {
  if (!query.trim()) return [];
  try {
    const res = await fetch(
      `${API_BASE}/api/v1/students/?search=${encodeURIComponent(query.trim())}&page_size=30`,
      { cache: "no-store" }
    );
    if (!res.ok) {
      throw new Error(`Error ${res.status} al buscar estudiantes`);
    }
    const data: PaginatedResponse<Student> = await res.json();
    return data.results;
  } catch (error) {
    console.error("searchStudents error:", error);
    throw error;
  }
}

/**
 * Obtiene los estudiantes correspondientes a un grupo académico (grado, letra y turno).
 */
export async function fetchStudentsByGroup(
  grade: number,
  groupLetter: string,
  shift: string
): Promise<Student[]> {
  try {
    const url = `${API_BASE}/api/v1/students/?grade=${grade}&group=${groupLetter}&shift=${shift}&page_size=100`;
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) {
      throw new Error(`Error ${res.status} al cargar alumnos del grupo`);
    }
    const data: PaginatedResponse<Student> = await res.json();
    return data.results;
  } catch (error) {
    console.error("fetchStudentsByGroup error:", error);
    throw error;
  }
}

/**
 * Obtiene el expediente completo de un estudiante por su UUID.
 */
export async function fetchStudentById(id: string): Promise<Student> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/students/${id}/`, {
      cache: "no-store",
    });
    if (!res.ok) {
      throw new Error(`Error ${res.status} al cargar expediente del estudiante`);
    }
    return await res.json();
  } catch (error) {
    console.error("fetchStudentById error:", error);
    throw error;
  }
}

/**
 * Genera la URL pública/interna para renderizar el código QR binario PNG.
 */
export function getQrImageUrl(token: string): string {
  return `${API_BASE}/api/v1/qr/${token}/image/`;
}

/**
 * Carga la fotografía de un estudiante a la API y base de datos (POST multipart).
 */
export async function uploadStudentPhoto(
  studentId: string,
  file: File,
  isManualCrop: boolean = false,
  originalFile?: File
): Promise<{
  photo_url: string;
  photo_sha256?: string;
  completeness: string;
  active_qr_token_id?: string | null;
}> {
  const formData = new FormData();
  formData.append("photo", file);
  if (isManualCrop) {
    formData.append("is_manual_crop", "true");
  }
  if (originalFile) {
    formData.append("original_photo", originalFile);
  }

  const res = await fetch(`${API_BASE}/api/v1/students/${studentId}/photo/`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(
      errorData?.message || `Error ${res.status} al subir fotografía`
    );
  }

  return await res.json();
}

/**
 * Retorna la URL directa para renderizar la fotografía del estudiante desde el backend.
 * Permite solicitar la toma original completa (sin recorte) para el editor manual de encuadre.
 */
export function getStudentPhotoUrl(
  studentId: string,
  timestamp?: string | number,
  original: boolean = false
): string {
  const params = new URLSearchParams();
  if (timestamp) params.append("t", String(timestamp));
  if (original) params.append("original", "true");
  const queryStr = params.toString() ? `?${params.toString()}` : "";
  return `${API_BASE}/api/v1/students/${studentId}/photo/${queryStr}`;
}

/**
 * Carga un lote de fotografías a la API para asociarlas automáticamente a los estudiantes (US-064).
 */
export async function uploadBatchPhotos(
  files: File[],
  options?: {
    grade?: number;
    group?: string;
    shift?: string;
    overwrite?: boolean;
  }
): Promise<BatchPhotoUploadResponse> {
  const formData = new FormData();
  for (const file of files) {
    if (file.name.toLowerCase().endsWith(".zip")) {
      formData.append("zip_file", file);
    } else {
      formData.append("photos", file);
    }
  }

  if (options?.grade) {
    formData.append("grade", options.grade.toString());
  }
  if (options?.group) {
    formData.append("group", options.group);
  }
  if (options?.shift) {
    formData.append("shift", options.shift);
  }
  if (options?.overwrite !== undefined) {
    formData.append("overwrite", options.overwrite.toString());
  }

  const res = await fetch(`${API_BASE}/api/v1/students/batch-photos/`, {
    method: "POST",
    body: formData,
  });

  return await res.json();
}

/**
 * Elimina la fotografía de un estudiante de la base de datos y del disco.
 * El endpoint limpia photo_url, photo_sha256 y photo_updated_at.
 */
export async function deleteStudentPhoto(studentId: string): Promise<{
  message: string;
  completeness: string;
  completeness_display: string;
}> {
  const res = await fetch(`${API_BASE}/api/v1/students/${studentId}/photo/`, {
    method: "DELETE",
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(
      errorData?.message || `Error ${res.status} al eliminar fotografía`
    );
  }

  return await res.json();
}

/**
 * Genera y descarga el PDF de credencial individual de un estudiante.
 * Llama a POST /api/v1/credentials/exports/ con mode=CREDENCIAL y entity_ids=[studentId].
 * Retorna el Blob binario del PDF listo para descarga.
 */
export async function downloadStudentCredentialPdf(
  studentId: string
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/v1/credentials/exports/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mode: "CREDENCIAL",
      entity_type: "STUDENT",
      entity_ids: [studentId],
      format: "PDF",
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(
      errorData?.detail ||
        errorData?.message ||
        `Error ${res.status} al generar credencial PDF`
    );
  }

  return await res.blob();
}

/**
 * Genera y descarga el PDF de credenciales de todos los alumnos elegibles de un grupo.
 * Llama a POST /api/v1/credentials/exports/ con mode=CREDENCIAL y group_id.
 * Retorna el Blob binario del PDF listo para descarga.
 */
export async function downloadGroupCredentialPdf(
  groupId: string
): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/v1/credentials/exports/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mode: "CREDENCIAL",
      entity_type: "STUDENT",
      group_id: groupId,
      format: "PDF",
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(
      errorData?.detail ||
        errorData?.message ||
        `Error ${res.status} al generar credenciales PDF del grupo`
    );
  }

  return await res.blob();
}

/**
 * Actualiza parcialmente los datos de un estudiante mediante PATCH (§3.4).
 * La matrícula es inmutable en el backend (RN-EST-02).
 */
export async function updateStudent(
  studentId: string,
  payload: StudentUpdatePayload
): Promise<Student> {
  const res = await fetch(`${API_BASE}/api/v1/students/${studentId}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    let errorMsg = `Error ${res.status} al actualizar estudiante`;
    if (errorData?.details) {
      const details = errorData.details;
      if (typeof details === "object") {
        const fieldErrors = Object.entries(details)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(", ") : val}`)
          .join(" | ");
        errorMsg = `${errorData.message || "Error de validación"}: ${fieldErrors}`;
      } else {
        errorMsg = String(details);
      }
    } else if (errorData?.message) {
      errorMsg = errorData.message;
    }
    throw new Error(errorMsg);
  }

  return await res.json();
}

/**
 * Actualiza los datos de un tutor asociado mediante PATCH (§3.4).
 * Si el tutor está vinculado a múltiples estudiantes, confirm=true aplica el cambio.
 */
export async function updateGuardian(
  guardianId: string,
  payload: GuardianUpdatePayload,
  confirm = true
): Promise<GuardianContact> {
  const res = await fetch(
    `${API_BASE}/api/v1/students/guardians/${guardianId}/?confirm=${confirm}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    }
  );

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    let errorMsg = `Error ${res.status} al actualizar tutor`;
    if (errorData?.details) {
      const details = errorData.details;
      if (typeof details === "object") {
        const fieldErrors = Object.entries(details)
          .map(([key, val]) => `${key}: ${Array.isArray(val) ? val.join(", ") : val}`)
          .join(" | ");
        errorMsg = `${errorData.message || "Error"}: ${fieldErrors}`;
      }
    } else if (errorData?.message) {
      errorMsg = errorData.message;
    }
    throw new Error(errorMsg);
  }

  return await res.json();
}

/**
 * Elimina permanentemente a un estudiante del sistema (hard delete).
 * Elimina el registro y sus fotografías. Esta operación es irreversible.
 */
export async function deleteStudent(
  studentId: string
): Promise<StudentDeleteResponse> {
  const res = await fetch(
    `${API_BASE}/api/v1/students/${studentId}/delete/`,
    { method: "DELETE" }
  );

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(
      errorData?.message || `Error ${res.status} al eliminar estudiante`
    );
  }

  return await res.json();
}

/**
 * Registra un nuevo estudiante individualmente (POST /api/v1/students/).
 * Incluye los datos académicos obligatorios y al menos un tutor.
 */
export async function createStudent(
  payload: StudentCreatePayload
): Promise<Student> {
  const res = await fetch(`${API_BASE}/api/v1/students/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    let errorMsg = `Error ${res.status} al registrar estudiante`;
    if (errorData?.details) {
      const details = errorData.details;
      if (typeof details === "object") {
        const fieldErrors = Object.entries(details)
          .map(
            ([key, val]) =>
              `${key}: ${Array.isArray(val) ? val.join(", ") : val}`
          )
          .join(" | ");
        errorMsg = `${errorData.message || "Error de validación"}: ${fieldErrors}`;
      } else {
        errorMsg = String(details);
      }
    } else if (errorData?.message) {
      errorMsg = errorData.message;
    }
    throw new Error(errorMsg);
  }

  return await res.json();
}
