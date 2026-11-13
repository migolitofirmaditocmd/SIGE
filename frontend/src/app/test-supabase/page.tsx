import { createClient } from "@/utils/supabase/server";
import { cookies } from "next/headers";

export default async function TestSupabasePage() {
  const cookieStore = await cookies();
  const supabase = createClient(cookieStore);

  const { data: todos, error } = await supabase.from("todos").select();

  return (
    <div className="p-8 max-w-lg mx-auto font-sans">
      <h1 className="text-xl font-bold mb-4 text-slate-800">
        Prueba de Conexión a Supabase
      </h1>
      {error && (
        <div className="p-3 bg-amber-50 text-amber-800 rounded-lg text-sm mb-4 border border-amber-200">
          Nota: {error.message} (Crea la tabla &apos;todos&apos; en el Dashboard de Supabase si deseas probar esta consulta).
        </div>
      )}
      <ul className="list-disc pl-5 space-y-1 text-sm text-slate-700">
        {todos && todos.length > 0 ? (
          todos.map((todo: { id: string | number; name: string }) => (
            <li key={todo.id}>{todo.name}</li>
          ))
        ) : (
          <li className="text-slate-500 italic">No hay registros aún en &apos;todos&apos;</li>
        )}
      </ul>
    </div>
  );
}
