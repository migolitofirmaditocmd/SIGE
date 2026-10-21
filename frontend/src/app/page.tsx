import React from "react";
import { Card, Button, Badge } from "@/shared/ui";
import { QrCode, Users, ShieldCheck, ClipboardList, CheckCircle2, Server, ArrowRight, Laptop } from "lucide-react";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-[#F1F5F9] flex flex-col">
      {/* Barra Superior Institucional */}
      <header className="bg-[#0A3D91] text-white py-4 px-6 shadow-sm">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-3 text-center sm:text-left">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center font-bold text-lg border border-white/20">
              5
            </div>
            <div>
              <h1 className="text-base font-bold tracking-tight">Escuela Secundaria Mixta 5</h1>
              <p className="text-xs text-blue-200">Sistema Integral de Gestión Escolar (SIGE)</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge status="ACTIVO" label="PWA v1.0 · En Línea" size="sm" className="bg-white/15 text-white border-white/20" />
          </div>
        </div>
      </header>

      {/* Contenido Principal */}
      <div className="max-w-6xl mx-auto w-full px-4 sm:px-6 py-8 flex-1 flex flex-col gap-8">
        {/* Banner de Estado de Hito 3.3 */}
        <Card className="bg-white border-l-4 border-l-[#0A3D91] flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold uppercase tracking-wider text-[#0A3D91] bg-blue-50 px-2.5 py-0.5 rounded-full">
                WBS 3.3 · Entregable Oficial
              </span>
              <Badge status="ASISTIO" label="Configuración Completada" size="sm" />
            </div>
            <h2 className="text-xl font-bold text-[#0B1320]">
              Proyecto Base Next.js & TypeScript Operativo
            </h2>
            <p className="text-sm text-[#334155]">
              Arquitectura modular PWA inicializada con App Router, Tailwind CSS, sistema de tokens Squircle UI y buffer IndexedDB listo para escaneo sin conexión.
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <Button variant="primary" size="md">
              <span>Ingresar al Sistema</span>
              <ArrowRight className="w-4 h-4 ml-1" />
            </Button>
          </div>
        </Card>

        {/* Módulos Principales de la Plataforma */}
        <section className="space-y-4">
          <h3 className="text-sm font-bold uppercase tracking-wider text-[#334155]">
            Módulos de la Plataforma (Roles SIGE)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card variant="elevated" className="flex flex-col justify-between hover:border-[#0A3D91]">
              <div className="space-y-3">
                <div className="w-10 h-10 rounded-xl bg-blue-50 text-[#0A3D91] flex items-center justify-center">
                  <QrCode className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-[#0B1320]">Control de Asistencia QR</h4>
                <p className="text-xs text-[#334155] leading-relaxed">
                  Escaneo de credenciales para prefectos con registro de entrada/salida y tolerancia horaria configurable.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-500">Prefectura / PAD</span>
                <span className="text-xs font-semibold text-[#0A3D91]">Operativo</span>
              </div>
            </Card>

            <Card variant="elevated" className="flex flex-col justify-between hover:border-[#0A3D91]">
              <div className="space-y-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 text-[#0A5A2A] flex items-center justify-center">
                  <Users className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-[#0B1320]">Expedientes e Importación</h4>
                <p className="text-xs text-[#334155] leading-relaxed">
                  Carga masiva por hoja de cálculo, validación de tutores legales y gestión de ficha médica/administrativa.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-500">Personal Administrativo</span>
                <span className="text-xs font-semibold text-[#0A5A2A]">Catálogos v3.2</span>
              </div>
            </Card>

            <Card variant="elevated" className="flex flex-col justify-between hover:border-[#0A3D91]">
              <div className="space-y-3">
                <div className="w-10 h-10 rounded-xl bg-amber-50 text-[#7C4400] flex items-center justify-center">
                  <ClipboardList className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-[#0B1320]">Reportes de Incidencias</h4>
                <p className="text-xs text-[#334155] leading-relaxed">
                  Flujo en 4 etapas: Registro docente, canalización por prefecto, revisión administrativa y notificación a tutores.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-500">Docentes / Prefectos</span>
                <span className="text-xs font-semibold text-[#7C4400]">4 Etapas</span>
              </div>
            </Card>

            <Card variant="elevated" className="flex flex-col justify-between hover:border-[#0A3D91]">
              <div className="space-y-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 text-[#4B35A0] flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-[#0B1320]">Seguridad y Auditoría</h4>
                <p className="text-xs text-[#334155] leading-relaxed">
                  Sesiones JWT trazables en memoria, roles estrictos (RBAC), bitácora inmutable y control de respaldos.
                </p>
              </div>
              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
                <span className="text-xs text-slate-500">Dirección / Admin</span>
                <span className="text-xs font-semibold text-[#4B35A0]">ASVS V4/V8</span>
              </div>
            </Card>
          </div>
        </section>

        {/* Verificación Técnica del Entregable 3.3 */}
        <Card className="bg-white">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
            <h3 className="font-bold text-base text-[#0B1320] flex items-center gap-2">
              <Server className="w-4 h-4 text-[#0A3D91]" />
              Verificación de Requisitos de Arquitectura (WBS 3.3)
            </h3>
            <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
              Validado 100%
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-[#0A5A2A] shrink-0 mt-0.5" />
              <div>
                <span className="font-medium text-[#0B1320]">Next.js App Router & TypeScript estricto</span>
                <p className="text-xs text-[#334155]">Estructura modular en src/features y src/shared desacoplada del backend.</p>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-[#0A5A2A] shrink-0 mt-0.5" />
              <div>
                <span className="font-medium text-[#0B1320]">Sistema de diseño Squircle UI & Tokens AAA</span>
                <p className="text-xs text-[#334155]">Paleta de alto contraste legible bajo luz solar directa (tokens.css).</p>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-[#0A5A2A] shrink-0 mt-0.5" />
              <div>
                <span className="font-medium text-[#0B1320]">PWA & Service Worker preparado</span>
                <p className="text-xs text-[#334155]">manifest.webmanifest y sw.js para precaché de shell sin vulnerar datos de menores.</p>
              </div>
            </div>

            <div className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-[#0A5A2A] shrink-0 mt-0.5" />
              <div>
                <span className="font-medium text-[#0B1320]">Buffer IndexedDB para captura sin conexión</span>
                <p className="text-xs text-[#334155]">Capa de persistencia idb con tope de 1,000 eventos (RN-MOV-02 / RN-MOV-03).</p>
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Pie de Página */}
      <footer className="border-t border-slate-200 bg-white py-4 px-6 text-center text-xs text-[#334155]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Escuela Secundaria Mixta 5 · Zapopan, Jalisco</span>
          <span>SIGE Frontend v1.0.0 · Next.js / TypeScript / PWA</span>
        </div>
      </footer>
    </main>
  );
}
