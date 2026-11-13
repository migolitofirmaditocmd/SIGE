"use client";

import React, { useState } from "react";
import { Student, StudentCreatePayload } from "../types";
import { createStudent } from "../services";
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
  UserPlus,
} from "lucide-react";

interface AddStudentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onStudentCreated: (newStudent: Student) => void;
}

type TabType = "personal" | "academic" | "address" | "health" | "guardian";

const TABS: { key: TabType; label: string; icon: React.ReactNode }[] = [
  { key: "personal", label: "Personal", icon: <User className="w-3.5 h-3.5" /> },
  { key: "academic", label: "Escolar", icon: <GraduationCap className="w-3.5 h-3.5" /> },
  { key: "address", label: "Domicilio", icon: <MapPin className="w-3.5 h-3.5" /> },
  { key: "health", label: "Salud", icon: <HeartPulse className="w-3.5 h-3.5" /> },
  { key: "guardian", label: "Tutor", icon: <Phone className="w-3.5 h-3.5" /> },
];

export const AddStudentModal: React.FC<AddStudentModalProps> = ({
  isOpen,
  onClose,
  onStudentCreated,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>("personal");

  // Datos personales
  const [firstName, setFirstName] = useState("");
  const [lastNameFather, setLastNameFather] = useState("");
  const [lastNameMother, setLastNameMother] = useState("");
  const [curp, setCurp] = useState("");
  const [institutionalEmail, setInstitutionalEmail] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [sex, setSex] = useState("");
  const [enrollmentId, setEnrollmentId] = useState("");

  // Datos escolares
  const [grade, setGrade] = useState<number>(1);
  const [groupLetter, setGroupLetter] = useState("A");
  const [shift, setShift] = useState("MATUTINO");

  // Domicilio
  const [addressStreet, setAddressStreet] = useState("");
  const [addressColonia, setAddressColonia] = useState("");
  const [addressMunicipio, setAddressMunicipio] = useState("Zapopan");
  const [addressEstado, setAddressEstado] = useState("Jalisco");
  const [addressPostalCode, setAddressPostalCode] = useState("");

  // Ficha médica
  const [bloodType, setBloodType] = useState("");
  const [allergies, setAllergies] = useState("");

  // Tutor
  const [guardianFirstName, setGuardianFirstName] = useState("");
  const [guardianLastNameFather, setGuardianLastNameFather] = useState("");
  const [guardianLastNameMother, setGuardianLastNameMother] = useState("");
  const [guardianPhone, setGuardianPhone] = useState("");
  const [guardianEmail, setGuardianEmail] = useState("");
  const [guardianRelationship, setGuardianRelationship] = useState("PADRE");

  // Estados de proceso
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  if (!isOpen) return null;

  const resetForm = () => {
    setFirstName("");
    setLastNameFather("");
    setLastNameMother("");
    setCurp("");
    setInstitutionalEmail("");
    setBirthDate("");
    setSex("");
    setEnrollmentId("");
    setGrade(1);
    setGroupLetter("A");
    setShift("MATUTINO");
    setAddressStreet("");
    setAddressColonia("");
    setAddressMunicipio("Zapopan");
    setAddressEstado("Jalisco");
    setAddressPostalCode("");
    setBloodType("");
    setAllergies("");
    setGuardianFirstName("");
    setGuardianLastNameFather("");
    setGuardianLastNameMother("");
    setGuardianPhone("");
    setGuardianEmail("");
    setGuardianRelationship("PADRE");
    setActiveTab("personal");
    setErrorMessage(null);
    setSuccessMessage(null);
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

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
    if (!enrollmentId.trim()) {
      setErrorMessage("La matrícula es obligatoria.");
      setActiveTab("personal");
      return;
    }
    if (!guardianFirstName.trim() || !guardianLastNameFather.trim()) {
      setErrorMessage("El nombre y apellido paterno del tutor son obligatorios.");
      setActiveTab("guardian");
      return;
    }
    if (!guardianPhone.trim() && !guardianEmail.trim()) {
      setErrorMessage("El tutor debe tener al menos un teléfono o correo de contacto.");
      setActiveTab("guardian");
      return;
    }

    const payload: StudentCreatePayload = {
      enrollment_id: enrollmentId.trim(),
      first_name: firstName.trim(),
      last_name_father: lastNameFather.trim(),
      last_name_mother: lastNameMother.trim() || null,
      curp: curp.trim() || null,
      institutional_email: institutionalEmail.trim() || null,
      birth_date: birthDate || null,
      sex: sex || null,
      grade,
      group_letter: groupLetter,
      shift,
      blood_type: bloodType || null,
      allergies: allergies.trim() || null,
      address_street: addressStreet.trim() || null,
      address_colonia: addressColonia.trim() || null,
      address_municipio: addressMunicipio.trim() || null,
      address_estado: addressEstado.trim() || null,
      address_postal_code: addressPostalCode.trim() || null,
      guardians: [
        {
          first_name: guardianFirstName.trim(),
          last_name_father: guardianLastNameFather.trim(),
          last_name_mother: guardianLastNameMother.trim() || null,
          phone_number: guardianPhone.trim() || null,
          email: guardianEmail.trim() || null,
          relationship: guardianRelationship,
          is_primary_contact: true,
        },
      ],
    };

    try {
      setIsSubmitting(true);
      const newStudent = await createStudent(payload);
      setSuccessMessage(
        `Alumno ${newStudent.display_name} registrado exitosamente.`
      );
      onStudentCreated(newStudent);
      setTimeout(() => {
        handleClose();
      }, 1500);
    } catch (err: unknown) {
      setErrorMessage(
        err instanceof Error ? err.message : "Error al registrar el alumno."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const inputClass =
    "w-full px-3 py-2 text-sm border border-slate-200 rounded-lg bg-white focus:outline-none focus:ring-2 focus:ring-[#0A3D91]/30 focus:border-[#0A3D91] transition-all disabled:bg-slate-50 disabled:text-slate-400";
  const labelClass = "block text-xs font-semibold text-slate-600 mb-1";
  const fieldClass = "flex flex-col gap-0.5";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] flex flex-col border border-slate-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100 shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#0A3D91]/10 flex items-center justify-center">
              <UserPlus className="w-4 h-4 text-[#0A3D91]" />
            </div>
            <div>
              <h2 className="text-base font-bold text-[#0B1320]">
                Registrar nuevo alumno
              </h2>
              <p className="text-xs text-slate-500">
                Completa los datos del expediente escolar
              </p>
            </div>
          </div>
          <button
            onClick={handleClose}
            disabled={isSubmitting}
            className="text-slate-400 hover:text-slate-700 transition-colors disabled:opacity-50"
            aria-label="Cerrar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-100 shrink-0 overflow-x-auto">
          {TABS.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-1.5 px-4 py-2.5 text-xs font-semibold transition-colors whitespace-nowrap border-b-2 ${
                activeTab === tab.key
                  ? "border-[#0A3D91] text-[#0A3D91] bg-blue-50/60"
                  : "border-transparent text-slate-500 hover:text-slate-700 hover:bg-slate-50"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Body */}
        <form
          id="add-student-form"
          onSubmit={handleSubmit}
          className="flex-1 overflow-y-auto"
        >
          <div className="p-6 space-y-4">
            {/* ── Personal ── */}
            {activeTab === "personal" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className={`${fieldClass} sm:col-span-2`}>
                  <label className={labelClass}>
                    Matrícula <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={enrollmentId}
                    onChange={(e) => setEnrollmentId(e.target.value)}
                    placeholder="Ej. 17906679"
                    maxLength={20}
                    className={inputClass}
                    required
                    disabled={isSubmitting}
                  />
                  <span className="text-[10px] text-slate-400">
                    Identificador único e inmutable del alumno.
                  </span>
                </div>

                <div className={`${fieldClass} sm:col-span-2`}>
                  <label className={labelClass}>
                    Nombre(s) <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="Ej. Ana Sofía"
                    maxLength={80}
                    className={inputClass}
                    required
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>
                    Apellido Paterno <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={lastNameFather}
                    onChange={(e) => setLastNameFather(e.target.value)}
                    placeholder="Ej. García"
                    maxLength={60}
                    className={inputClass}
                    required
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Apellido Materno</label>
                  <input
                    type="text"
                    value={lastNameMother}
                    onChange={(e) => setLastNameMother(e.target.value)}
                    placeholder="Ej. López"
                    maxLength={60}
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>CURP</label>
                  <input
                    type="text"
                    value={curp}
                    onChange={(e) => setCurp(e.target.value.toUpperCase())}
                    placeholder="Ej. GALA050312HJCRNNA0"
                    maxLength={18}
                    className={`${inputClass} font-mono uppercase`}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Fecha de Nacimiento</label>
                  <input
                    type="date"
                    value={birthDate}
                    onChange={(e) => setBirthDate(e.target.value)}
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Sexo</label>
                  <select
                    value={sex}
                    onChange={(e) => setSex(e.target.value)}
                    className={inputClass}
                    disabled={isSubmitting}
                  >
                    <option value="">Sin especificar</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Correo Institucional</label>
                  <input
                    type="email"
                    value={institutionalEmail}
                    onChange={(e) => setInstitutionalEmail(e.target.value)}
                    placeholder="alumno@escuela.edu.mx"
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>
              </div>
            )}

            {/* ── Escolar ── */}
            {activeTab === "academic" && (
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className={fieldClass}>
                  <label className={labelClass}>
                    Grado <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={grade}
                    onChange={(e) => setGrade(Number(e.target.value))}
                    className={inputClass}
                    disabled={isSubmitting}
                  >
                    <option value={1}>1°</option>
                    <option value={2}>2°</option>
                    <option value={3}>3°</option>
                  </select>
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>
                    Grupo <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={groupLetter}
                    onChange={(e) => setGroupLetter(e.target.value)}
                    className={inputClass}
                    disabled={isSubmitting}
                  >
                    {["A", "B", "C", "D", "E", "F"].map((l) => (
                      <option key={l} value={l}>
                        {l}
                      </option>
                    ))}
                  </select>
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>
                    Turno <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={shift}
                    onChange={(e) => setShift(e.target.value)}
                    className={inputClass}
                    disabled={isSubmitting}
                  >
                    <option value="MATUTINO">Matutino</option>
                    <option value="VESPERTINO">Vespertino</option>
                  </select>
                </div>
              </div>
            )}

            {/* ── Domicilio ── */}
            {activeTab === "address" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className={`${fieldClass} sm:col-span-2`}>
                  <label className={labelClass}>Calle y número</label>
                  <input
                    type="text"
                    value={addressStreet}
                    onChange={(e) => setAddressStreet(e.target.value)}
                    placeholder="Ej. Av. Vallarta 1234"
                    maxLength={200}
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Colonia</label>
                  <input
                    type="text"
                    value={addressColonia}
                    onChange={(e) => setAddressColonia(e.target.value)}
                    placeholder="Ej. Jardines del Bosque"
                    maxLength={100}
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Municipio</label>
                  <input
                    type="text"
                    value={addressMunicipio}
                    onChange={(e) => setAddressMunicipio(e.target.value)}
                    maxLength={100}
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Estado</label>
                  <input
                    type="text"
                    value={addressEstado}
                    onChange={(e) => setAddressEstado(e.target.value)}
                    maxLength={60}
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Código Postal</label>
                  <input
                    type="text"
                    value={addressPostalCode}
                    onChange={(e) => setAddressPostalCode(e.target.value)}
                    placeholder="Ej. 44520"
                    maxLength={5}
                    pattern="\d{5}"
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>
              </div>
            )}

            {/* ── Salud ── */}
            {activeTab === "health" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className={fieldClass}>
                  <label className={labelClass}>Tipo de Sangre</label>
                  <select
                    value={bloodType}
                    onChange={(e) => setBloodType(e.target.value)}
                    className={inputClass}
                    disabled={isSubmitting}
                  >
                    <option value="">Sin especificar</option>
                    {["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"].map(
                      (bt) => (
                        <option key={bt} value={bt}>
                          {bt}
                        </option>
                      )
                    )}
                  </select>
                </div>

                <div className={`${fieldClass} sm:col-span-2`}>
                  <label className={labelClass}>Alergias conocidas</label>
                  <textarea
                    value={allergies}
                    onChange={(e) => setAllergies(e.target.value)}
                    placeholder="Describe cualquier alergia o condición médica relevante..."
                    rows={3}
                    maxLength={500}
                    className={`${inputClass} resize-none`}
                    disabled={isSubmitting}
                  />
                </div>
              </div>
            )}

            {/* ── Tutor ── */}
            {activeTab === "guardian" && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className={`${fieldClass} sm:col-span-2`}>
                  <label className={labelClass}>
                    Parentesco <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={guardianRelationship}
                    onChange={(e) => setGuardianRelationship(e.target.value)}
                    className={inputClass}
                    disabled={isSubmitting}
                  >
                    <option value="PADRE">Padre</option>
                    <option value="MADRE">Madre</option>
                    <option value="TUTOR">Tutor Legal</option>
                    <option value="ABUELO">Abuelo/a</option>
                    <option value="HERMANO">Hermano/a</option>
                    <option value="OTRO">Otro</option>
                  </select>
                </div>

                <div className={`${fieldClass} sm:col-span-2`}>
                  <label className={labelClass}>
                    Nombre(s) del tutor <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={guardianFirstName}
                    onChange={(e) => setGuardianFirstName(e.target.value)}
                    placeholder="Ej. María Elena"
                    maxLength={80}
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>
                    Apellido Paterno <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={guardianLastNameFather}
                    onChange={(e) => setGuardianLastNameFather(e.target.value)}
                    maxLength={60}
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Apellido Materno</label>
                  <input
                    type="text"
                    value={guardianLastNameMother}
                    onChange={(e) => setGuardianLastNameMother(e.target.value)}
                    maxLength={60}
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>
                    Teléfono{" "}
                    <span className="text-slate-400 font-normal">
                      (10 dígitos)
                    </span>
                  </label>
                  <input
                    type="tel"
                    value={guardianPhone}
                    onChange={(e) => setGuardianPhone(e.target.value)}
                    placeholder="Ej. 3312345678"
                    maxLength={10}
                    pattern="\d{10}"
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <div className={fieldClass}>
                  <label className={labelClass}>Correo Electrónico</label>
                  <input
                    type="email"
                    value={guardianEmail}
                    onChange={(e) => setGuardianEmail(e.target.value)}
                    placeholder="tutor@correo.com"
                    className={inputClass}
                    disabled={isSubmitting}
                  />
                </div>

                <p className="sm:col-span-2 text-xs text-slate-400">
                  <span className="text-red-500">*</span> Se requiere al menos
                  un teléfono o correo de contacto del tutor.
                </p>
              </div>
            )}
          </div>
        </form>

        {/* Footer */}
        <div className="shrink-0 px-6 py-4 border-t border-slate-100 flex flex-col gap-3">
          {/* Mensajes de éxito / error */}
          {errorMessage && (
            <div className="flex items-start gap-2 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              <AlertTriangle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
              <p className="text-xs text-red-800 font-medium leading-snug">
                {errorMessage}
              </p>
            </div>
          )}

          {successMessage && (
            <div className="flex items-start gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
              <p className="text-xs text-emerald-800 font-medium leading-snug">
                {successMessage}
              </p>
            </div>
          )}

          <div className="flex items-center justify-between gap-3">
            {/* Navegación entre tabs */}
            <div className="flex gap-1.5">
              {activeTab !== "personal" && (
                <button
                  type="button"
                  onClick={() => {
                    const idx = TABS.findIndex((t) => t.key === activeTab);
                    if (idx > 0) setActiveTab(TABS[idx - 1].key);
                  }}
                  disabled={isSubmitting}
                  className="px-3 py-1.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors disabled:opacity-50"
                >
                  ← Anterior
                </button>
              )}
              {activeTab !== "guardian" && (
                <button
                  type="button"
                  onClick={() => {
                    const idx = TABS.findIndex((t) => t.key === activeTab);
                    if (idx < TABS.length - 1) setActiveTab(TABS[idx + 1].key);
                  }}
                  disabled={isSubmitting}
                  className="px-3 py-1.5 text-xs font-semibold text-[#0A3D91] bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors disabled:opacity-50"
                >
                  Siguiente →
                </button>
              )}
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleClose}
                disabled={isSubmitting}
                className="h-8 px-4 text-xs font-semibold text-slate-600 border-slate-200 hover:bg-slate-50"
              >
                Cancelar
              </Button>

              <Button
                variant="primary"
                size="sm"
                type="submit"
                form="add-student-form"
                disabled={isSubmitting || !!successMessage}
                className="h-8 px-4 text-xs font-bold bg-[#0A3D91] hover:bg-[#072B68] text-white flex items-center gap-1.5"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Registrando...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-3.5 h-3.5" />
                    <span>Registrar alumno</span>
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

