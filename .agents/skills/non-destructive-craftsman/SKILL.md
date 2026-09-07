---
name: non-destructive-craftsman
description: Strict non-destructive modification protocol, blast radius analysis, zero accidental code deletion, regression prevention, and surgical additive changes.
---

# Non-Destructive Craftsman (Preservación Absoluta de Código)
**Master Standards**: Ibrahim García / Suite Atelier & Enterprise Projects  
**Rule of Law**: "Pedir X NUNCA debe destruir silenciosamente Y ni Z"

---

## 🛡️ 1. El Síndrome de la Destrucción Silenciosa (AI Amnesia)

Uno de los mayores defectos de los modelos de IA es la **amnesia destructiva**: cuando se les pide implementar o ajustar la función X, deciden que la función Y o Z "ya no es necesaria", "es redundante", o simplemente la omiten del archivo de reemplazo para ahorrar tokens, entregando un código roto sin avisar.

### ⚖️ Ley Inquebrantable de Preservación:
> **Queda terminantemente prohibido podar, omitir, renombrar o simplificar código, funciones, comentarios, validaciones o dependencias existentes a menos que el usuario lo haya pedido de forma explícita y literal.**

---

## 🔍 2. Protocolo de Modificación Quirúrgica (3 Pasos Obligatorios)

Cualquier agente que modifique código existente DEBE seguir este protocolo:

### Paso 1: Análisis de Radio de Impacto (Blast Radius Analysis)
Antes de escribir una sola línea de código, el agente debe responderse a sí mismo:
- ¿Qué funciones llaman a la sección que voy a tocar?
- ¿Qué hojas, celdas, endpoints o variables globales consume?
- Si modifico la firma o retorno de esta función, ¿a quién más rompo en cascada?

### Paso 2: Modificación Aditiva o Quirúrgica
- **Preferir adición sobre modificación**: Si una lógica es nueva, crea una función o submódulo nuevo y llámalo desde el flujo principal.
- **Edición Quirúrgica en Bloque Contiguo**: Utilizar herramientas de reemplazo por bloque exacto (`replace_file_content`) limitadas estrictamente a las líneas necesarias.
- **PROHIBIDO sobreescribir archivos completos** (`write_to_file` con `Overwrite: true`) en archivos de código maduros de más de 100 líneas, a menos que sea un archivo nuevo o una reestructuración explícitamente solicitada.

### Paso 3: Declaración Explícita de Intención y Diferencias
Al entregar el trabajo, el agente DEBE listar con transparencia:
1. **Qué se agregó exactamente.**
2. **Qué líneas precisas cambiaron y por qué.**
3. **Garantía explícita de no-regresión**: Confirmar que todas las demás funciones y módulos adyacentes permanecen intactos y operativos.

---

## 🧪 3. Verificación Pre-Entrega Obligatoria

Ninguna tarea se considera completa ni se presenta al usuario sin haber ejecutado:
1. **Prueba de Compilación/Sintaxis**: Ejecutar el script de sintaxis (Node VM, linter o compilador) para verificar 0 errores sintácticos.
2. **Prueba de Invariantes**: Verificar que las funciones, rangos y objetos clave que existían antes sigan presentes en el código.
3. Si algo falla, el agente debe corregirlo internamente antes de responder.
