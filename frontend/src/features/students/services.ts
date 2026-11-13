/**
 * Servicios de comunicación HTTP con la API REST de SIGE Backend.
 */

import {
  AcademicGroup,
  BatchPhotoUploadResponse,
  PaginatedResponse,
  Student,
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
  file: File
): Promise<{
  photo_url: string;
  photo_sha256?: string;
  completeness: string;
  active_qr_token_id?: string | null;
}> {
  const formData = new FormData();
  formData.append("photo", file);

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
 */
export function getStudentPhotoUrl(
  studentId: string,
  timestamp?: string | number
): string {
  const t = timestamp ? `?t=${timestamp}` : "";
  return `${API_BASE}/api/v1/students/${studentId}/photo/${t}`;
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

  if (!res.ok) {
    const errorData = await res.json().catch(() => null);
    throw new Error(
      errorData?.message || `Error ${res.status} al procesar lote de fotografías`
    );
  }

  return await res.json();
}


