"use client";

import React, { useState, useEffect, useRef } from "react";
import { Student } from "../types";
import { searchStudents } from "../services";
import { Search, Loader2, User, X } from "lucide-react";
import { Badge } from "@/shared/ui";

interface StudentSearchBarProps {
  onSelectStudent: (student: Student) => void;
  placeholder?: string;
}

export const StudentSearchBar: React.FC<StudentSearchBarProps> = ({
  onSelectStudent,
  placeholder = "Buscar alumno por nombre, matrícula o CURP (ej. García, 18016200)...",
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Cerrar desplegable si se hace click fuera
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Manejo de cambio de texto
  const handleQueryChange = (val: string) => {
    setQuery(val);
    if (!val.trim() || val.trim().length < 2) {
      setResults([]);
      setIsLoading(false);
      setHasSearched(false);
    }
  };

  // Búsqueda asíncrona con debounce
  useEffect(() => {
    if (!query.trim() || query.trim().length < 2) {
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      setHasSearched(true);
      try {
        const found = await searchStudents(query);
        setResults(found);
        setIsOpen(true);
      } catch (err) {
        console.error("Error al buscar:", err);
      } finally {
        setIsLoading(false);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (student: Student) => {
    onSelectStudent(student);
    setIsOpen(false);
  };

  const handleClear = () => {
    setQuery("");
    setResults([]);
    setIsOpen(false);
    setHasSearched(false);
  };

  return (
    <div ref={containerRef} className="relative w-full">
      <div className="relative flex items-center">
        <Search className="absolute left-3.5 w-5 h-5 text-slate-400 pointer-events-none" />
        <input
          type="text"
          value={query}
          onChange={(e) => handleQueryChange(e.target.value)}
          onFocus={() => {
            if (results.length > 0) setIsOpen(true);
          }}
          placeholder={placeholder}
          className="w-full h-12 pl-11 pr-10 text-sm bg-white text-slate-900 placeholder:text-slate-400 rounded-xl border border-slate-300 focus:border-[#0A3D91] focus:ring-2 focus:ring-[#0A3D91]/20 focus:outline-none shadow-sm transition-all"
        />

        {isLoading && (
          <Loader2 className="absolute right-3.5 w-4 h-4 text-[#0A3D91] animate-spin" />
        )}

        {!isLoading && query && (
          <button
            onClick={handleClear}
            className="absolute right-3 p-1 rounded-full text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Menú flotante de resultados de búsqueda */}
      {isOpen && (
        <div className="absolute left-0 right-0 mt-1.5 max-h-80 overflow-y-auto bg-white rounded-xl border border-slate-200 shadow-xl z-50 divide-y divide-slate-100">
          {results.length > 0 ? (
            results.map((student) => (
              <button
                key={student.id}
                onClick={() => handleSelect(student)}
                className="w-full text-left px-4 py-3 hover:bg-blue-50/70 transition-colors flex items-center justify-between gap-3 group"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <div className="w-9 h-9 rounded-full bg-slate-100 text-slate-600 group-hover:bg-[#0A3D91] group-hover:text-white flex items-center justify-center shrink-0 transition-colors">
                    <User className="w-4 h-4" />
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-bold text-slate-900 group-hover:text-[#0A3D91] truncate">
                      {student.display_name}
                    </p>
                    <p className="text-xs text-slate-500 font-mono">
                      Matrícula: {student.enrollment_id} · {student.academic_group}
                    </p>
                  </div>
                </div>

                <Badge
                  status={student.status === "ACTIVO" ? "ACTIVO" : "PENDIENTE"}
                  label={student.status_display}
                  size="sm"
                  className="shrink-0"
                />
              </button>
            ))
          ) : hasSearched && !isLoading ? (
            <div className="p-4 text-center text-xs text-slate-500">
              No se encontraron alumnos con el criterio &quot;{query}&quot;.
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
};
