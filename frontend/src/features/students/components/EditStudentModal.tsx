"use client";

import React, { useState } from "react";
import { Student } from "../types";
import { updateStudent, updateGuardian } from "../services";
import { Button } from "@/shared/ui";
import {
  X,
  Save,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  User,
  GraduationCap,
  MapPin,
  HeartPulse,
  Phone,
  Lock,
} from "lucide-react";

interface EditStudentModalProps {
  isOpen: boolean;
  onClose: () => void;
  student: Student;
  onStudentUpdated: (updatedStudent: Student) => void;
}

type TabType = "personal" | "academic" | "address" | "health" | "guardian";

export const EditStudentModal: React.FC<EditStudentModalProps> = ({
  isOpen,
  onClose,
  student,
  onStudentUpdated,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>("personal");

  // Datos del estudiante
  const [firstName, setFirstName] = useState(student.first_name || "");
  const [lastNameFather, setLastNameFather] = useState(student.last_name_father || "");
  const [lastNameMother, setLastNameMother] = useState(student.last_name_mother || "");
  const [curp, setCurp] = useState(student.curp || "");
  const [institutionalEmail, setInstitutionalEmail] = useState(student.institutional_email || "");
  const [birthDate, setBirthDate] = useState(student.birth_date || "");
  const [sex, setSex] = useState(student.sex || "");

  // Datos escolares
  const [grade, setGrade] = useState<number>(student.grade || 1);
  const [groupLetter, setGroupLetter] = useState(student.group_letter || "A");
  const [shift, setShift] = useState(student.shift || "MATUTINO");

  // Domicilio
  const [addressStreet, setAddressStreet] = useState(student.address_street || "");
  const [addressColonia, setAddressColonia] = useState(student.address_colonia || "");
  const [addressMunicipio, setAddressMunicipio] = useState(student.address_municipio || "Zapopan");
  const [addressEstado, setAddressEstado] = useState(student.address_estado || "Jalisco");
  const [addressPostalCode, setAddressPostalCode] = useState(student.address_postal_code || "");

  // Ficha médica
  const [bloodType, setBloodType] = useState(student.blood_type || "");
  const [allergies, setAllergies] = useState(student.allergies || "");

  // Tutor principal
  const primaryGuardianRelation =
    student.guardians.find((g) => g.is_primary_contact) || student.guardians[0];
  const primaryGuardian = primaryGuardianRelation?.guardian;

  const [guardianFirstName, setGuardianFirstName] = useState(
    primaryGuardian?.first_name || ""
  );
  const [guardianLastNameFather, setGuardianLastNameFather] = useState(
    primaryGuardian?.last_name_father || ""
  );
  const [guardianLastNameMother, setGuardianLastNameMother] = useState(
    primaryGuardian?.last_name_mother || ""
  );
  const [guardianPhone, setGuardianPhone] = useState(
    primaryGuardian?.phone_number || ""
  );
  const [guardianEmail, setGuardianEmail] = useState(
    primaryGuardian?.email || ""
  );

  // Estados de proceso
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);

    // Validaciones básicas de cliente
    if (!firstName.trim()) {
      setErrorMessage("El nombre de pila es obligatorio.");
      setActiveTab("personal");
      return;
    }
    if (!lastNameFather.trim()) {
      setErrorMessage("El apellido paterno es obligatorio.");
      setActiveTab("personal");
      return;
    }

    try {
      setIsSubmitting(true);

      // 1. Actualizar estudiante
      const studentPayload = {
        first_name: firstName.trim(),
        last_name_father: lastNameFather.trim(),
        last_name_mother: lastNameMother.trim() || null,
        curp: curp.trim().toUpperCase() || null,
        institutional_email: institutionalEmail.trim().toLowerCase() || null,
        birth_date: birthDate || null,
        sex: sex || null,
        grade: Number(grade),
        group_letter: groupLetter.trim().toUpperCase(),
        shift: shift.trim().toUpperCase(),
        address_street: addressStreet.trim() || null,
        address_colonia: addressColonia.trim() || null,
        address_municipio: addressMunicipio.trim() || null,
        address_estado: addressEstado.trim() || null,
        address_postal_code: addressPostalCode.trim() || null,
        blood_type: bloodType || null,
        allergies: allergies.trim() || null,
      };

      let updatedStudent = await updateStudent(student.id, studentPayload);

      // 2. Si hay tutor y se modificaron sus datos, actualizar tutor
      if (primaryGuardian) {
        const guardianPayload = {
          first_name: guardianFirstName.trim() || undefined,
          last_name_father: guardianLastNameFather.trim() || undefined,
          last_name_mother: guardianLastNameMother.trim() || null,
          phone_number: guardianPhone.trim() || null,
          email: guardianEmail.trim().toLowerCase() || null,
        };

        const updatedGuardian = await updateGuardian(
          primaryGuardian.id,
          guardianPayload,
          true
        );

        // Reintegrar datos del tutor en el student actualizado para la UI
        updatedStudent = {
          ...updatedStudent,
          guardians: updatedStudent.guardians.map((rel) =>
            rel.guardian.id === primaryGuardian.id
              ? {
                  ...rel,
                  guardian: {
                    ...rel.guardian,
                    first_name: updatedGuardian.first_name,
                    last_name_father: updatedGuardian.last_name_father,
                    last_name_mother: updatedGuardian.last_name_mother,
                    display_name: updatedGuardian.display_name,
                    phone_number: updatedGuardian.phone_number,
                    email: updatedGuardian.email,
                  },
                }
              : rel
          ),
        };
      }

      setSuccessMessage("Información actualizada correctamente.");
      onStudentUpdated(updatedStudent);

      // Cerrar modal automáticamente tras un breve instante
      setTimeout(() => {
        onClose();
      }, 700);
    } catch (err: unknown) {
      console.error(err);
      setErrorMessage(
        err instanceof Error ? err.message : "Error al guardar los cambios."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-xs animate-in fade-in duration-150">
      <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden">
        {/* Cabecera */}
        <div className="px-6 py-4 bg-gradient-to-r from-blue-900 to-[#0A3D91] text-white flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center backdrop-blur-xs">
              <User className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="font-bold text-base leading-tight">
                Editar Información del Estudiante
              </h3>
              <p className="text-xs text-blue-200 flex items-center gap-2 mt-0.5">
                <span>{student.display_name}</span>
                <span className="font-mono bg-white/20 px-1.5 py-0.2 rounded text-[11px]">
                  {student.enrollment_id}
                </span>
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="w-8 h-8 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors text-white"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Mensajes de alerta globales */}
        {errorMessage && (
          <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-200 rounded-xl flex items-start gap-2.5 text-xs text-red-800">
            <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
            <span className="font-medium leading-relaxed">{errorMessage}</span>
          </div>
        )}

        {successMessage && (
          <div className="mx-6 mt-4 p-3 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center gap-2.5 text-xs text-emerald-800">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span className="font-bold">{successMessage}</span>
          </div>
        )}

        {/* Barra de pestañas */}
        <div className="flex border-b border-slate-200 bg-slate-50 px-6 overflow-x-auto text-xs font-semibold">
          <button
            type="button"
            onClick={() => setActiveTab("personal")}
            className={`py-3 px-3.5 border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
              activeTab === "personal"
                ? "border-[#0A3D91] text-[#0A3D91] bg-white font-bold"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <User className="w-3.5 h-3.5" />
            <span>Datos Personales</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("academic")}
            className={`py-3 px-3.5 border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
              activeTab === "academic"
                ? "border-[#0A3D91] text-[#0A3D91] bg-white font-bold"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <GraduationCap className="w-3.5 h-3.5" />
            <span>Escolar</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("address")}
            className={`py-3 px-3.5 border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
              activeTab === "address"
                ? "border-[#0A3D91] text-[#0A3D91] bg-white font-bold"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <MapPin className="w-3.5 h-3.5" />
            <span>Domicilio</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("health")}
            className={`py-3 px-3.5 border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
              activeTab === "health"
                ? "border-[#0A3D91] text-[#0A3D91] bg-white font-bold"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <HeartPulse className="w-3.5 h-3.5" />
            <span>Salud</span>
          </button>

          <button
            type="button"
            onClick={() => setActiveTab("guardian")}
            className={`py-3 px-3.5 border-b-2 flex items-center gap-1.5 transition-colors whitespace-nowrap ${
              activeTab === "guardian"
                ? "border-[#0A3D91] text-[#0A3D91] bg-white font-bold"
                : "border-transparent text-slate-500 hover:text-slate-800"
            }`}
          >
            <Phone className="w-3.5 h-3.5" />
            <span>Tutor Legal</span>
          </button>
        </div>

        {/* Formulario con scroll */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-4">
          {/* PESTAÑA 1: DATOS PERSONALES */}
          {activeTab === "personal" && (
            <div className="space-y-4">
              <div className="p-3 bg-blue-50/70 border border-blue-100 rounded-xl flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <Lock className="w-3.5 h-3.5 text-[#0A3D91]" />
                  <span className="font-semibold text-slate-700">Matrícula escolar:</span>
                  <span className="font-mono font-bold text-[#0A3D91]">
                    {student.enrollment_id}
                  </span>
                </div>
                <span className="text-[10px] text-slate-500 italic">
                  Identificador inmutable oficial
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Nombre(s) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Apellido Paterno <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={lastNameFather}
                    onChange={(e) => setLastNameFather(e.target.value)}
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Apellido Materno
                  </label>
                  <input
                    type="text"
                    value={lastNameMother}
                    onChange={(e) => setLastNameMother(e.target.value)}
                    placeholder="(Opcional)"
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    CURP (18 caracteres)
                  </label>
                  <input
                    type="text"
                    maxLength={18}
                    value={curp}
                    onChange={(e) => setCurp(e.target.value.toUpperCase())}
                    placeholder="ABCD123456HDFRRN01"
                    className="w-full h-9 px-3 text-xs font-mono rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Correo Institucional
                  </label>
                  <input
                    type="email"
                    value={institutionalEmail}
                    onChange={(e) => setInstitutionalEmail(e.target.value)}
                    placeholder="alumno@secundariamixta5.edu.mx"
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Fecha de Nacimiento
                  </label>
                  <input
                    type="date"
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Sexo
                  </label>
                  <select
                    value={sex}
                    onChange={(e) => setSex(e.target.value)}
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  >
                    <option value="">No especificado</option>
                    <option value="M">Masculino (M)</option>
                    <option value="F">Femenino (F)</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* PESTAÑA 2: UBICACIÓN ESCOLAR */}
          {activeTab === "academic" && (
            <div className="space-y-4">
              <p className="text-xs text-slate-500">
                Ajusta el grado, grupo y turno asignados al alumno dentro de la institución.
              </p>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Grado
                  </label>
                  <select
                    value={grade}
                    onChange={(e) => setGrade(Number(e.target.value))}
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  >
                    <option value={1}>1° de Secundaria</option>
                    <option value={2}>2° de Secundaria</option>
                    <option value={3}>3° de Secundaria</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Grupo
                  </label>
                  <select
                    value={groupLetter}
                    onChange={(e) => setGroupLetter(e.target.value)}
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  >
                    {["A", "B", "C", "D", "E", "F"].map((g) => (
                      <option key={g} value={g}>
                        Grupo {g}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Turno
                  </label>
                  <select
                    value={shift}
                    onChange={(e) => setShift(e.target.value)}
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  >
                    <option value="MATUTINO">Matutino</option>
                    <option value="VESPERTINO">Vespertino</option>
                  </select>
                </div>
              </div>

              <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-600">
                Grupo resultante:{" "}
                <span className="font-bold text-[#0A3D91]">
                  {grade}° {groupLetter} {shift === "MATUTINO" ? "Matutino" : "Vespertino"}
                </span>
              </div>
            </div>
          )}

          {/* PESTAÑA 3: DOMICILIO */}
          {activeTab === "address" && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Calle y Número
                </label>
                <input
                  type="text"
                  value={addressStreet}
                  onChange={(e) => setAddressStreet(e.target.value)}
                  placeholder="Ej. Av. Hidalgo 123 Int. 4"
                  className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Colonia
                  </label>
                  <input
                    type="text"
                    value={addressColonia}
                    onChange={(e) => setAddressColonia(e.target.value)}
                    placeholder="Ej. Centro"
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Código Postal
                  </label>
                  <input
                    type="text"
                    maxLength={10}
                    value={addressPostalCode}
                    onChange={(e) => setAddressPostalCode(e.target.value)}
                    placeholder="Ej. 45100"
                    className="w-full h-9 px-3 text-xs font-mono rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Municipio
                  </label>
                  <input
                    type="text"
                    value={addressMunicipio}
                    onChange={(e) => setAddressMunicipio(e.target.value)}
                    placeholder="Zapopan"
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Estado
                  </label>
                  <input
                    type="text"
                    value={addressEstado}
                    onChange={(e) => setAddressEstado(e.target.value)}
                    placeholder="Jalisco"
                    className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                  />
                </div>
              </div>
            </div>
          )}

          {/* PESTAÑA 4: SALUD */}
          {activeTab === "health" && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Tipo de Sangre
                </label>
                <select
                  value={bloodType}
                  onChange={(e) => setBloodType(e.target.value)}
                  className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 bg-white focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                >
                  <option value="">No especificado</option>
                  <option value="O+">O Positivo (O+)</option>
                  <option value="O-">O Negativo (O-)</option>
                  <option value="A+">A Positivo (A+)</option>
                  <option value="A-">A Negativo (A-)</option>
                  <option value="B+">B Positivo (B+)</option>
                  <option value="B-">B Negativo (B-)</option>
                  <option value="AB+">AB Positivo (AB+)</option>
                  <option value="AB-">AB Negativo (AB-)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Alergias o Condiciones Médicas de Urgencia
                </label>
                <textarea
                  rows={3}
                  value={allergies}
                  onChange={(e) => setAllergies(e.target.value)}
                  placeholder="Ej. Alergia a la penicilina, asma leve, intolerancia..."
                  className="w-full p-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                />
              </div>
            </div>
          )}

          {/* PESTAÑA 5: TUTOR LEGAL */}
          {activeTab === "guardian" && (
            <div className="space-y-4">
              {primaryGuardian ? (
                <>
                  <div className="p-3 bg-blue-50/70 border border-blue-100 rounded-xl text-xs text-slate-700 flex items-center justify-between">
                    <div>
                      <span className="font-bold text-[#0A3D91]">Tutor asignado:</span>{" "}
                      <span>{primaryGuardian.display_name}</span>
                    </div>
                    <span className="text-[11px] font-semibold text-blue-700 bg-blue-100 px-2 py-0.5 rounded-full">
                      {primaryGuardianRelation.relationship_display}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Nombre(s)
                      </label>
                      <input
                        type="text"
                        value={guardianFirstName}
                        onChange={(e) => setGuardianFirstName(e.target.value)}
                        className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Apellido Paterno
                      </label>
                      <input
                        type="text"
                        value={guardianLastNameFather}
                        onChange={(e) => setGuardianLastNameFather(e.target.value)}
                        className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Apellido Materno
                      </label>
                      <input
                        type="text"
                        value={guardianLastNameMother}
                        onChange={(e) => setGuardianLastNameMother(e.target.value)}
                        className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Teléfono de Contacto
                      </label>
                      <input
                        type="tel"
                        value={guardianPhone}
                        onChange={(e) => setGuardianPhone(e.target.value)}
                        placeholder="Ej. 3312345678"
                        className="w-full h-9 px-3 text-xs font-mono rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-bold text-slate-700 mb-1">
                        Correo Electrónico
                      </label>
                      <input
                        type="email"
                        value={guardianEmail}
                        onChange={(e) => setGuardianEmail(e.target.value)}
                        placeholder="tutor@ejemplo.com"
                        className="w-full h-9 px-3 text-xs rounded-lg border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/20 focus:border-[#0A3D91]"
                      />
                    </div>
                  </div>
                </>
              ) : (
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-center text-xs text-amber-800">
                  Este alumno no tiene un tutor legal registrado actualmente.
                </div>
              )}
            </div>
          )}

          {/* Pie de acción */}
          <div className="pt-4 border-t border-slate-200 flex items-center justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={isSubmitting}
              onClick={onClose}
              className="text-xs"
            >
              Cancelar
            </Button>

            <Button
              type="submit"
              size="sm"
              disabled={isSubmitting}
              className="bg-[#0A3D91] hover:bg-[#072B68] text-white text-xs font-semibold flex items-center gap-1.5 shadow-sm"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Guardando...</span>
                </>
              ) : (
                <>
                  <Save className="w-3.5 h-3.5" />
                  <span>Guardar Cambios</span>
                </>
              )}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

