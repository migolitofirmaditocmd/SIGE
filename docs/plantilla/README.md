# Plantilla Oficial de Registro Masivo de Estudiantes
**Escuela Secundaria Mixta 5 — Sistema Integral de Gestión Escolar (SIGE)**  
**Ubicación:** `docs/plantilla/`  
**Archivos disponibles:**
- [`plantilla_registro_estudiantes_sige.xlsx`](file:///c:/Users/pc/Documents/SIGE/docs/plantilla/plantilla_registro_estudiantes_sige.xlsx) (Libro Excel con formato visual, listas desplegables y guía integrada).
- [`plantilla_registro_estudiantes_sige.csv`](file:///c:/Users/pc/Documents/SIGE/docs/plantilla/plantilla_registro_estudiantes_sige.csv) (Archivo plano delimitado por comas con codificación UTF-8 con BOM).

---

## 🎯 1. Propósito

Esta plantilla permite al **Personal Administrativo y Secretarias** capturar la información de los estudiantes de forma estandarizada y ordenada en una hoja de cálculo, garantizando que el archivo pueda ser cargado sin errores en el módulo de importaciones masivas de la plataforma SIGE (`POST /api/v1/imports/upload/`).

Cumple estrictamente con el **Diccionario de Datos Institucional**, los requisitos **RF-IMP-01**, **RF-IMP-02** y las **Reglas de Negocio RN-IMP-01 a RN-IMP-10**.

---

## 📑 2. Estructura de la Hoja de Cálculo (`.xlsx`)

El libro contiene dos pestañas especialmente preparadas:

### Pestaña 1: `Estudiantes`
Contiene la tabla de captura de datos con las **33 columnas oficiales**. Cuenta con:
- **Encabezados agrupados por categoría:** Azul para datos del alumno, verde para familiares/tutores y morado para aspectos médicos y administrativos.
- **Formato de texto forzado (`@`):** En matrículas, CURP, códigos postales y teléfonos para evitar que Excel elimine ceros a la izquierda o convierta números a notación científica (`3.32E+09`).
- **Validación de datos (listas desplegables):**
  - `SEXO`: `H`, `M`.
  - `PARENTESCO TUTOR`: `TUTOR_LEGAL`, `MADRE`, `PADRE`, `ABUELO_A`, `OTRO`.
  - `TIPO DE SANGRE`: `O+`, `O-`, `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`.
  - `DEBE PAGO`: `NO`, `SI`.
- **4 filas de ejemplos reales y válidos** que demuestran casos cotidianos y situaciones especiales (nombres compuestos, falta de segundo apellido, tutores legales y registros incompletos).
- **Inmovilización de paneles:** Las filas de encabezado permanecen fijas al desplazarse verticalmente.

### Pestaña 2: `Instrucciones y Reglas`
Guía rápida de referencia pensada para el usuario final (secretarias), explicando el significado de los colores, los formatos permitidos y las preguntas frecuentes.

---

## 🎨 3. Código de Colores de los Encabezados

| Color | Nivel de Obligatoriedad | Descripción y Regla Asociada |
|---|---|---|
| 🔴 **Rojo Salmón** (`#FCE4D6`) | **Mínimo Obligatorio** | Campos indispensables para registrar al estudiante: `MATRICULA`, `NOMBRE(S)`, `APELLIDO PATERNO` y al menos un Tutor con contacto válido (`TELEFONO` o `CORREO`). Sin estos datos la fila es descartada automáticamente (RN-EST-10, RN-IMP-06). |
| 🟡 **Amarillo Suave** (`#FFF2CC`) | **Obligatorio Diferido** | `FECHA DE NACIMIENTO`: si no se cuenta con ella al momento de la captura, puede dejarse vacía. La plataforma guardará al estudiante con estatus **ACTIVO** bajo la marca **INCOMPLETO**, permitiéndole recibir asistencia y credencial provisional mientras entrega su acta (RN-EST-10). |
| ⚪ **Gris Claro** (`#F2F2F2`) | **Opcional Recomendado** | `CURP`, `DOMICILIO`, `COLONIA`, `MUNICIPIO`, `ESTADO`, `CODIGO POSTAL`, datos médicos, segundo tutor y adeudos. Pueden llenarse en la plantilla o completarse después en la plataforma. |

---

## 📋 4. Diccionario de Columnas

| N° | Nombre de Columna | Obligatorio | Formato / Ejemplo | Descripción y Regla |
|:---:|---|:---:|---|---|
| **1** | `MATRICULA` | **Sí** | `2026-1A-001` | Código o matrícula institucional única (RN-EST-02). |
| **2** | `CURP` | No | `GARA090314HJCXRA01` | 18 caracteres alfanuméricos oficiales de RENAPO. |
| **3** | `NOMBRE(S)` | **Sí** | `Juan Carlos` / `María José` | Nombre(s) de pila. **No poner apellidos aquí** (RN-TRX-08, RN-IMP-09). |
| **4** | `APELLIDO PATERNO` | **Sí** | `García` / `De la Cruz` | Primer apellido del estudiante (RN-TRX-08). Admite partículas ("De la"). |
| **5** | `APELLIDO MATERNO` | No | `López` / *(vacío)* | Segundo apellido. Si legalmente no tiene, **déjelo en blanco**. |
| **6** | `FECHA DE NACIMIENTO` | Diferido | `2011-03-14` | Formato `AAAA-MM-DD`. Si falta, crea registro `INCOMPLETO` (RN-EST-10). |
| **7** | `SEXO` | No | `H` o `M` | `H` = Hombre, `M` = Mujer. |
| **8** | `DOMICILIO` | No | `Av. Hidalgo 123` | Calle y número exterior / interior. |
| **9** | `COLONIA` | No | `Centro` / `Maestros` | Colonia o fraccionamiento. |
| **10** | `MUNICIPIO` | No | `Zapopan` / `Guadalajara` | Municipio de residencia. |
| **11** | `ESTADO` | No | `Jalisco` | Entidad federativa. |
| **12** | `CODIGO POSTAL` | No | `45150` | Código postal a 5 dígitos numéricos. |
| **13** | `TELEFONO ESTUDIANTE` | No | `3344556677` | Celular del alumno (10 dígitos). |
| **14** | `NOMBRE(S) MAMA` | Condicional* | `María Elena` | Nombre(s) de la madre. |
| **15** | `APELLIDO PATERNO MAMA` | Condicional* | `López` | Primer apellido de la madre. |
| **16** | `APELLIDO MATERNO MAMA` | No | `Pérez` | Segundo apellido de la madre. |
| **17** | `TELEFONO MAMA` | Condicional* | `3312345678` | Celular a 10 dígitos numéricos exactos de la madre. |
| **18** | `CORREO MAMA` | Condicional* | `maria.lopez@example.com` | Correo electrónico para notificaciones de asistencia y reportes. |
| **19** | `NOMBRE(S) PAPA` | Condicional* | `Carlos` | Nombre(s) del padre. |
| **20** | `APELLIDO PATERNO PAPA` | Condicional* | `García` | Primer apellido del padre. |
| **21** | `APELLIDO MATERNO PAPA` | No | `Torres` | Segundo apellido del padre. |
| **22** | `TELEFONO PAPA` | Condicional* | `3398765432` | Celular a 10 dígitos numéricos del padre. |
| **23** | `CORREO PAPA` | Condicional* | `carlos.garcia@example.com` | Correo electrónico válido del padre. |
| **24** | `PARENTESCO TUTOR` | No | `ABUELO_A` / `TUTOR_LEGAL` | Seleccionar vínculo si no es mamá ni papá. |
| **25** | `NOMBRE(S) TUTOR` | Condicional* | `Guadalupe` | Nombre(s) del tutor legal o representante alterno. |
| **26** | `APELLIDO PATERNO TUTOR` | Condicional* | `Soto` | Primer apellido del tutor legal. |
| **27** | `APELLIDO MATERNO TUTOR` | No | `Gómez` | Segundo apellido del tutor legal. |
| **28** | `TELEFONO TUTOR` | Condicional* | `3336388869` | Celular a 10 dígitos numéricos del tutor legal. |
| **29** | `CORREO TUTOR` | Condicional* | `guadalupe.soto@example.com` | Correo electrónico del tutor legal. |
| **30** | `TIPO DE SANGRE` | No | `O+`, `A+`, etc. | Grupo y factor Rh. |
| **31** | `ALERGIAS` | No | `Alergia a penicilina` | Notas médicas relevantes o `Ninguna`. |
| **32** | `DEBE PAGO` | No | `NO` o `SI` | Indicador de adeudo de aportación escolar (sin montos). |
| **33** | `MATERIAS PENDIENTES` | No | `Matemáticas 1` / `Ninguna` | Asignaturas no acreditadas de grados anteriores. |

*\* Nota sobre tutores (RN-EST-03 / RN-EST-11):* Es obligatorio registrar al menos a un tutor (ya sea Mamá, Papá o Tutor Legal) con su nombre, primer apellido y al menos un medio de contacto válido (teléfono celular a 10 dígitos o correo electrónico).

---

## ⚠️ 5. Reglas de Negocio Fundamentales para la Captura

1. **Nombres en tres columnas separadas (RN-TRX-08, RN-IMP-09):**  
   Nunca capture nombres completos en una sola casilla. La plataforma rechazará el archivo completo si los nombres no vienen en sus columnas individuales correspondientes.
2. **Prohibido el uso de valores sustitutos de relleno (RN-TRX-09):**  
   No escriba `"N/A"`, `"NA"`, `"NO TIENE"`, `"SIN APELLIDO"`, `"NINGUNO"`, `"XX"` ni guiones. Si el alumno o tutor no tiene segundo apellido o no cuenta con teléfono secundario, **deje la celda totalmente vacía**.
3. **Teléfonos de exactamente 10 dígitos (RN-EST-11):**  
   Escriba únicamente los 10 dígitos seguidos (ej. `3312345678`). No agregue espacios, paréntesis, guiones ni prefijos (`+52`, `044`).
4. **Una plantilla por grupo escolar (RN-IMP-08):**  
   Cada archivo o lote corresponde a los estudiantes de **un solo grupo** (ej. 1°A Matutino). En la pantalla de importación de la plataforma se seleccionará el grado, grupo, ciclo y turno de una sola vez, por lo que no es necesario repetir grado o grupo fila por fila.
5. **Protección contra duplicados (RN-IMP-03, RN-IMP-07):**  
   Si una matrícula ya fue registrada previamente en la escuela, la plataforma la reportará como duplicada y conservará el registro existente sin dañarlo ni sobrescribirlo, continuando con el resto de los alumnos del archivo.
6. **Reutilización automática de tutores entre hermanos (RN-EST-13, RN-IMP-10):**  
   Si dos o más alumnos comparten al mismo tutor (coincidencia de nombre completo y teléfono o correo), el sistema los vinculará al mismo registro de tutor familiar para no duplicar datos ni teléfonos.

---

## 🚀 6. Flujo de Uso en la Plataforma

```
1. Abrir plantilla oficial en Excel (.xlsx)
                    ↓
2. Llenar los datos de los estudiantes del grupo (eliminar las 4 filas de ejemplo)
                    ↓
3. Guardar el archivo (.xlsx o .csv)
                    ↓
4. Ingresar a SIGE con rol Administrador o Personal Administrativo
                    ↓
5. Ir a "Estudiantes" → "Importación Masiva"
                    ↓
6. Seleccionar Ciclo Escolar, Grado, Grupo y Turno
                    ↓
7. Subir el archivo → Revisar Vista Previa (Dry-Run)
                    ↓
8. Confirmar importación → Descargar reporte de registros creados
```
