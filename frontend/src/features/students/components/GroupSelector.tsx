"use client";

import React, { useEffect, useState } from "react";
import { AcademicGroup } from "../types";
import { fetchGroups } from "../services";
import { Users, Loader2 } from "lucide-react";

interface GroupSelectorProps {
  selectedGroup: AcademicGroup | null;
  onSelectGroup: (group: AcademicGroup) => void;
}

export const GroupSelector: React.FC<GroupSelectorProps> = ({
  selectedGroup,
  onSelectGroup,
}) => {
  const [groups, setGroups] = useState<AcademicGroup[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadGroups() {
      try {
        setIsLoading(true);
        const data = await fetchGroups();
        setGroups(data);
        if (data.length > 0 && !selectedGroup) {
          onSelectGroup(data[0]);
        }
      } catch (err) {
        console.error(err);
        setError("No se pudieron cargar los grupos académicos.");
      } finally {
        setIsLoading(false);
      }
    }
    loadGroups();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 p-3 text-xs text-slate-500 bg-white rounded-xl border border-slate-200">
        <Loader2 className="w-4 h-4 animate-spin text-[#0A3D91]" />
        <span>Cargando catálogo de grupos...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-3 text-xs text-red-700 bg-red-50 rounded-xl border border-red-200">
        {error}
      </div>
    );
  }

  // Separar grupos por turno para renderizar con <optgroup>
  const matutinos = groups.filter((g) => g.shift === "MATUTINO");
  const vespertinos = groups.filter((g) => g.shift === "VESPERTINO");

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
      <div className="flex items-center gap-2 text-sm font-bold text-slate-800">
        <Users className="w-4 h-4 text-[#0A3D91]" />
        <span>Seleccionar Grupo Académico:</span>
      </div>

      <div className="flex items-center gap-3 w-full sm:w-auto">
        <select
          value={selectedGroup?.id || ""}
          onChange={(e) => {
            const found = groups.find((g) => g.id === e.target.value);
            if (found) onSelectGroup(found);
          }}
          className="h-10 px-3 bg-white text-sm font-semibold text-slate-900 rounded-lg border border-slate-300 focus:border-[#0A3D91] focus:ring-2 focus:ring-[#0A3D91]/20 focus:outline-none transition-all cursor-pointer w-full sm:w-72"
        >
          {matutinos.length > 0 && (
            <optgroup label="☀️  Turno Matutino">
              {matutinos.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.grade}°{group.group_letter} — {group.student_count} alumnos
                </option>
              ))}
            </optgroup>
          )}

          {vespertinos.length > 0 && (
            <optgroup label="🌙  Turno Vespertino">
              {vespertinos.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.grade}°{group.group_letter} — {group.student_count} alumnos
                </option>
              ))}
            </optgroup>
          )}
        </select>

        {selectedGroup && (
          <span
            className={`text-xs font-bold px-3 py-2 rounded-lg shrink-0 hidden md:inline-flex items-center gap-1.5 border ${
              selectedGroup.shift === "MATUTINO"
                ? "text-amber-700 bg-amber-50 border-amber-200"
                : "text-indigo-700 bg-indigo-50 border-indigo-200"
            }`}
          >
            <span>{selectedGroup.shift === "MATUTINO" ? "☀️" : "🌙"}</span>
            <span>
              {selectedGroup.student_count} alumnos ·{" "}
              {selectedGroup.shift === "MATUTINO" ? "Matutino" : "Vespertino"}
            </span>
          </span>
        )}
      </div>
    </div>
  );
};
