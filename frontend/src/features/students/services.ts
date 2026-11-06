/**
 * Servicios de comunicación HTTP con la API REST de SIGE Backend.
 */

import { AcademicGroup, PaginatedResponse, Student } from "./types";

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
