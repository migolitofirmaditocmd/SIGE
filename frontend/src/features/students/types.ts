/**
 * Tipos e interfaces del módulo de Estudiantes y Catálogos Académicos.
 * Alineado con el Modelo de Datos SIGE v3.2 y Especificación API REST v2 §2.4.
 */

export interface GuardianContact {
  id: string;
  first_name: string;
  last_name_father: string;
  last_name_mother?: string | null;
  display_name: string;
  sort_name?: string;
  email?: string | null;
  phone_number?: string | null;
}

export interface StudentGuardianRelation {
  id: string;
  guardian: GuardianContact;
  relationship: string;
  relationship_display: string;
  is_primary_contact: boolean;
  is_valid_contact: boolean;
  consent_status?: string;
  consent_status_display?: string;
}

export interface Student {
  id: string;
  enrollment_id: string;
  curp?: string | null;
  first_name: string;
  last_name_father: string;
  last_name_mother?: string | null;
  display_name: string;
  sort_name?: string;
  grade: number;
  group_letter: string;
  shift: string;
  academic_group: string;
  status: "ACTIVO" | "BAJA" | "EGRESADO";
  status_display: string;
  completeness: "COMPLETO" | "INCOMPLETO";
  completeness_display?: string;
  missing_fields?: string[];
  birth_date?: string | null;
  sex?: string | null;
  photo_url?: string | null;
  address_street?: string | null;
  address_colonia?: string | null;
  address_municipio?: string | null;
  address_estado?: string | null;
  address_postal_code?: string | null;
  blood_type?: string | null;
  allergies?: string | null;
  has_payment_debt?: boolean | null;
  guardians: StudentGuardianRelation[];
  consent_warning?: boolean;
  institutional_email?: string | null;
  active_qr_token_id?: string | null;
  created_at?: string;
  updated_at?: string;
}

export interface AcademicGroup {
  id: string;
  grade: number;
  group_letter: string;
  shift: "MATUTINO" | "VESPERTINO";
  display_name: string;
  student_count: number;
  is_active: boolean;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface BatchPhotoResultItem {
  filename: string;
  status: "SUCCESS" | "SKIPPED" | "UNMATCHED" | "ERROR";
  message: string;
  student_id?: string | null;
  student_name?: string | null;
  enrollment_id?: string | null;
  group?: string | null;
  active_qr_token_id?: string | null;
}

export interface BatchPhotoUploadResponse {
  total_received: number;
  matched_count: number;
  updated_count: number;
  skipped_count: number;
  unmatched_count: number;
  results: BatchPhotoResultItem[];
}

export interface StudentUpdatePayload {
  first_name?: string;
  last_name_father?: string;
  last_name_mother?: string | null;
  curp?: string | null;
  institutional_email?: string | null;
  grade?: number;
  group_letter?: string;
  shift?: string;
  birth_date?: string | null;
  sex?: string | null;
  blood_type?: string | null;
  allergies?: string | null;
  address_street?: string | null;
  address_colonia?: string | null;
  address_municipio?: string | null;
  address_estado?: string | null;
  address_postal_code?: string | null;
}

export interface GuardianUpdatePayload {
  first_name?: string;
  last_name_father?: string;
  last_name_mother?: string | null;
  phone_number?: string | null;
  email?: string | null;
}


